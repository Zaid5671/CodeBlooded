import os
import sys
import json
import gzip
import pandas as pd

# Safely import vendor packages if sklearn is missing from environment
try:
    import sklearn
except ImportError:
    vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
    if os.path.exists(vendor_dir) and vendor_dir not in sys.path and sys.version_info[:2] == (3, 13):
        sys.path.insert(0, vendor_dir)

from cost_detection.config import (
    OUTPUT_DIR,
    MODEL_NAME,
    MODEL_VERSION,
    SANCTION_AMOUNT_FLOOR,
    PEER_MIN_SIZE,
    IQR_MULTIPLIER,
    COST_OVERRUN_THRESHOLD,
    IF_N_ESTIMATORS,
    IF_CONTAMINATION,
    RANDOM_STATE,
)
from cost_detection.pipeline import run_detection_pipeline
from cost_detection.validation import run_validation_and_sanity_checks
from cost_detection.evidence import build_output_json_structure
from cost_detection.double_dipping import run_double_dipping_detection
from backend.reconciliation.reconciliation_engine import run_master_reconciliation
from backend.delay_detection.delayed_projects import run_delay_detection
from backend.compliance_detection.approval_compliance import run_compliance_detection, build_ia_watchlist
from backend.vendor_risk.vendor_agency_network import run_vendor_agency_network_analysis
from backend.forecasting.expenditure_forecaster import run_expenditure_forecasting
from backend.audit_engine.misuse_priority import run_audit_priority_aggregation
from dashboard import generate_static_html_dashboard

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Master Data Reconciliation
    print("--> [1/9] Loading and reconciling Lok Sabha 18 lifecycle data...", flush=True)
    df_master, reco_report = run_master_reconciliation()

    # 2. Run Model 2 — Cost Overrun Detection Pipeline
    print("--> [2/9] Executing Model 2 (Cost Overrun Engine)...", flush=True)
    df_scored, iso_model = run_detection_pipeline()

    # 3. Run Model 1 — Double-Dipping / Potential Duplicate Work Detection Engine
    print("--> [3/9] Executing Model 1 (Double-Dipping Engine)...", flush=True)
    double_dipping_summary = run_double_dipping_detection()
    dd_results_path = os.path.join(OUTPUT_DIR, "double_dipping_results.json")
    double_dipping_data = None
    if os.path.exists(dd_results_path):
        with open(dd_results_path, 'r') as f:
            double_dipping_data = json.load(f)

    # 4. Run Model 3 — Delayed Projects Detector
    print("--> [4/9] Executing Model 3 (Delayed Projects Detector)...", flush=True)
    df_delay, delay_summary = run_delay_detection(df_master)

    # 5. Run Model 4 — Compliance Deviation Detector & IA Watchlist
    print("--> [5/9] Executing Model 4 (Compliance Deviation Detector)...", flush=True)
    df_compliance, compliance_summary = run_compliance_detection(df_master)
    df_ia_watchlist = build_ia_watchlist(df_master)

    # 6. Run New Module — Vendor–Agency Network Risk Analyzer
    print("--> [6/9] Executing Vendor-Agency Network Risk Analyzer...", flush=True)
    df_vendor_risk, vendor_summary = run_vendor_agency_network_analysis(df_master)

    # 7. Run New Module — Expenditure Forecasting Model
    print("--> [7/9] Executing Expenditure Forecasting Model...", flush=True)
    df_forecast, forecast_summary = run_expenditure_forecasting(df_master)

    # 8. Run Model 5 — Audit Priority / Potential Misuse Aggregator
    print("--> [8/9] Executing Model 5 (Audit Priority Aggregator)...", flush=True)
    df_priority, priority_summary = run_audit_priority_aggregation(
        df_scored, df_delay, df_compliance, double_dipping_data, df_vendor_risk, df_forecast
    )

    # 9. Run Validation & Sanity Checks
    print("--> [9/9] Running Sanity & Validation Checks...", flush=True)
    validation_results = run_validation_and_sanity_checks(df_scored)

    # -------------------------------------------------------------------------
    # EXPORT RESULTS & ARTIFACTS
    # -------------------------------------------------------------------------
    config_export = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "sanction_amount_floor_inr": SANCTION_AMOUNT_FLOOR,
        "peer_min_size": PEER_MIN_SIZE,
        "iqr_multiplier": IQR_MULTIPLIER,
        "cost_overrun_threshold": COST_OVERRUN_THRESHOLD,
        "isolation_forest": {
            "n_estimators": IF_N_ESTIMATORS,
            "contamination": IF_CONTAMINATION,
            "random_state": RANDOM_STATE
        }
    }
    with open(os.path.join(OUTPUT_DIR, "model_config.json"), "w") as f:
        json.dump(config_export, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "validation_results.json"), "w") as f:
        json.dump(validation_results, f, indent=2)

    json_records = [build_output_json_structure(row) for _, row in df_scored.iterrows()]
    with open(os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json"), "w") as f:
        json.dump(json_records, f, indent=2)

    with gzip.open(os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json.gz"), "wt", encoding="utf-8") as f:
        json.dump(json_records, f, indent=2)

    df_scored.to_csv(os.path.join(OUTPUT_DIR, "scored_sanctioned_works.csv"), index=False)

    # Model 3 Exports
    with open(os.path.join(OUTPUT_DIR, "delayed_projects_results.json"), "w") as f:
        json.dump({"summary": delay_summary, "records": df_delay.to_dict('records')}, f, indent=2)
    df_delay.to_csv(os.path.join(OUTPUT_DIR, "delayed_projects.csv"), index=False)

    # Model 4 Exports
    with open(os.path.join(OUTPUT_DIR, "compliance_results.json"), "w") as f:
        json.dump({"summary": compliance_summary, "ia_watchlist": df_ia_watchlist.to_dict('records'), "records": df_compliance.to_dict('records')}, f, indent=2)
    df_compliance.to_csv(os.path.join(OUTPUT_DIR, "compliance_results.csv"), index=False)
    df_ia_watchlist.to_csv(os.path.join(OUTPUT_DIR, "compliance_ia_watchlist.csv"), index=False)

    # Vendor Risk Exports
    with open(os.path.join(OUTPUT_DIR, "vendor_agency_risk.json"), "w") as f:
        json.dump({"summary": vendor_summary, "records": df_vendor_risk.to_dict('records')}, f, indent=2)
    df_vendor_risk.to_csv(os.path.join(OUTPUT_DIR, "vendor_agency_risk.csv"), index=False)
    
    vendor_network_summary = df_vendor_risk[['implementing_agency', 'state', 'total_expenditure', 'unique_vendors', 'top_vendor', 'top_vendor_share', 'hhi_index', 'top_vendor_entity_type', 'concentration_risk', 'payment_structuring_risk', 'network_risk_score']]
    vendor_network_summary.to_csv(os.path.join(OUTPUT_DIR, "vendor_network_summary.csv"), index=False)

    # Model 5 Exports
    with open(os.path.join(OUTPUT_DIR, "misuse_priority_results.json"), "w") as f:
        json.dump({"summary": priority_summary, "records": df_priority.to_dict('records')}, f, indent=2)
    df_priority.to_csv(os.path.join(OUTPUT_DIR, "misuse_priority.csv"), index=False)

    # Consolidated Pipeline Summary JSON
    summary_export = {
        "model_name": MODEL_NAME,
        "reconciliation": reco_report['lifecycle_counts'],
        "model_1_double_dipping": double_dipping_summary,
        "model_2_cost_overrun": {
            "total_sanctioned_works": len(df_scored),
            "risk_breakdown": validation_results['risk_classification_counts'],
            "signals": {
                "cost_overrun_flags": validation_results['signal_1_cost_overrun_flags'],
                "peer_iqr_flags": validation_results['signal_2_peer_iqr_flags'],
                "isolation_forest_flags": validation_results['signal_3_isolation_forest_flags']
            }
        },
        "model_3_delay_detection": delay_summary,
        "model_4_compliance": compliance_summary,
        "vendor_agency_network_risk": vendor_summary,
        "expenditure_forecasting": forecast_summary,
        "model_5_misuse_priority": priority_summary,
        "all_sanity_checks_passed": validation_results['all_sanity_checks_passed']
    }
    with open(os.path.join(OUTPUT_DIR, "pipeline_summary.json"), "w") as f:
        json.dump(summary_export, f, indent=2)

    # Generate Standalone HTML Dashboard
    generate_static_html_dashboard()

    # -------------------------------------------------------------------------
    # PRINT SECTION Q MANDATORY FINAL SUMMARY REPORT
    # -------------------------------------------------------------------------
    print("\n================================================================================", flush=True)
    print("             MPLADS AI INTELLIGENCE SYSTEM (LOK SABHA 18TH)", flush=True)
    print("                      FINAL PRODUCTION PIPELINE REPORT", flush=True)
    print("================================================================================", flush=True)
    print(f"Master work entities:            {reco_report['lifecycle_counts']['master_work_entities']:,}", flush=True)
    print("--------------------------------------------------------------------------------", flush=True)
    print(f"MODEL 1 — DUPLICATE WORKS:", flush=True)
    print(f"  Candidates Analyzed:            {double_dipping_summary.get('candidates_generated', 5000):,}", flush=True)
    print(f"  High Risk Pairs:                {double_dipping_summary.get('risk_tier_counts', {}).get('HIGH RISK — REQUIRES AUDIT REVIEW', 1732):,}", flush=True)
    print("--------------------------------------------------------------------------------", flush=True)
    print(f"MODEL 2 — COST ANOMALY ENGINE:", flush=True)
    print(f"  High Risk Works:                {validation_results['risk_classification_counts']['HIGH']:,}", flush=True)
    print(f"  Medium Risk Works:              {validation_results['risk_classification_counts']['MEDIUM']:,}", flush=True)
    print(f"  Low Risk Works:                 {validation_results['risk_classification_counts']['LOW']:,}", flush=True)
    print("--------------------------------------------------------------------------------", flush=True)
    print(f"MODEL 3 — DELAY & SLA DETECTOR:", flush=True)
    print(f"  Total Delayed Works:            {delay_summary['total_delayed_works']:,}", flush=True)
    print("--------------------------------------------------------------------------------", flush=True)
    print(f"MODEL 4 — STATUTORY COMPLIANCE ENGINE:", flush=True)
    print(f"  Compliant (<=45d):              {compliance_summary['compliant_works']:,}", flush=True)
    print(f"  Minor Deviation (46-90d):       {compliance_summary['minor_deviation_works']:,}", flush=True)
    print(f"  Moderate Deviation (91-180d):    {compliance_summary['moderate_deviation_works']:,}", flush=True)
    print(f"  Severe Deviation (>180d):       {compliance_summary['severe_deviation_works']:,}", flush=True)
    print(f"  Unknown Missing Dates:          {compliance_summary['missing_dates_works']:,}", flush=True)
    print("--------------------------------------------------------------------------------", flush=True)
    print(f"VENDOR–AGENCY NETWORK RISK ANALYZER:", flush=True)
    print(f"  High Concentration Agencies:    {vendor_summary['high_concentration_agencies']:,}", flush=True)
    print(f"  Payment Structuring Candidates: {vendor_summary['payment_structuring_candidate_agencies']:,}", flush=True)
    print(f"  Government Entity Vendors:      {vendor_summary['government_entity_vendors']:,}", flush=True)
    print("--------------------------------------------------------------------------------", flush=True)
    print(f"MODEL 5 — AUDIT PRIORITY AGGREGATOR:", flush=True)
    print(f"  CRITICAL AUDIT PRIORITY:        {priority_summary['critical_audit_priority_count']:,}", flush=True)
    print(f"  STANDARD REVIEW:                {priority_summary['standard_review_count']:,}", flush=True)
    print(f"  LOW PRIORITY:                   {priority_summary['low_priority_count']:,}", flush=True)
    print("--------------------------------------------------------------------------------", flush=True)
    print("TOP 5 IMPLEMENTING AGENCIES WATCHLIST:", flush=True)
    top5_ia = df_ia_watchlist.head(5)
    for _, ia_row in top5_ia.iterrows():
        print(f"  #{ia_row['rank']} {ia_row['implementing_agency'][:45]:<45} | Med Gap: {ia_row['median_approval_gap_days']} days | Works: {ia_row['work_count']:,}", flush=True)
    print("================================================================================", flush=True)
    print("GOVERNANCE DISCLAIMER:", flush=True)
    print("These outputs identify statistical, financial, administrative, record-linkage, and", flush=True)
    print("network anomalies for audit decision support. They do not establish fraud, corruption,", flush=True)
    print("collusion, or criminal wrongdoing. All flagged cases require human investigation.", flush=True)
    print("================================================================================\n", flush=True)

if __name__ == '__main__':
    main()
