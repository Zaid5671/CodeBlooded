import os
import sys
import time
import json

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def profile_backend():
    print("\n--- PROFILING BACKEND STARTUP & API LATENCY ---")
    t0 = time.time()
    import backend.app as app
    t1 = time.time()
    startup_time = t1 - t0
    print(f"Backend Startup Time: {startup_time:.4f}s")

    routes = [
        "/api/corpora",
        "/api/summary",
        "/api/validation",
        "/api/signals",
        "/api/works?limit=50",
        "/api/top-anomalies",
        "/api/double-dipping",
        "/api/delayed-projects",
        "/api/compliance",
        "/api/audit-priority",
        "/api/forecast",
        "/api/vendor-risk",
        "/api/inadmissible-works",
        "/api/private-beneficiaries",
        "/api/duplicate-expenditure",
        "/api/fund-utilization",
        "/api/deep-evaluation",
        "/api/canonical-registry",
        "/api/query?q=road",
        "/api/agents/triage?work_id=WS/MP18010/2025-2026/182165"
    ]

    api_times = {}
    with app.app.test_client() as client:
        for r in routes:
            t0 = time.time()
            res = client.get(r)
            t1 = time.time()
            duration = t1 - t0
            api_times[r] = duration
            print(f"GET {r:<50} -> {res.status_code} ({duration:.4f}s)")

    return startup_time, api_times

def profile_pipeline():
    print("\n--- PROFILING ML PIPELINE COMPONENTS ---")
    
    # 1. Reconciliation & Data Loading
    t0 = time.time()
    from data_pipeline.reconciliation_engine import run_master_reconciliation
    df_master, _ = run_master_reconciliation()
    t_reco = time.time() - t0
    print(f"Step 1: Master Reconciliation & Ingestion: {t_reco:.4f}s")

    # 2. M1 + Feature Engineering Detection Pipeline
    t0 = time.time()
    from ml.pipeline import run_detection_pipeline
    df_scored, iso_model = run_detection_pipeline()
    t_m1 = time.time() - t0
    print(f"Step 2: M1 Cost Anomaly & Feature Engine:  {t_m1:.4f}s")

    # 3. M2 Double Dipping
    t0 = time.time()
    from ml.model_2_duplicate_work.double_dipping import run_double_dipping_detection
    dd_summary = run_double_dipping_detection()
    t_m2 = time.time() - t0
    print(f"Step 3: M2 Double-Dipping Candidate Engine: {t_m2:.4f}s")

    # 4. M3 Delay Detection
    t0 = time.time()
    from audit_rules.delay.delayed_projects import run_delay_detection
    df_delay, _ = run_delay_detection(df_master)
    t_m3 = time.time() - t0
    print(f"Step 4: M3 Delayed Projects Engine:         {t_m3:.4f}s")

    # 5. M4 Compliance & Forecasting
    t0 = time.time()
    from audit_rules.statutory_compliance.approval_compliance import run_compliance_detection
    from ml.model_4_forecasting.expenditure_forecaster import run_expenditure_forecasting
    df_compliance, _ = run_compliance_detection(df_master)
    df_forecast, _ = run_expenditure_forecasting(df_master)
    t_m4 = time.time() - t0
    print(f"Step 5: M4 Compliance & Forecast Engine:    {t_m4:.4f}s")

    # 6. M5 Audit Priority Aggregator
    t0 = time.time()
    from audit_rules.vendor_risk.vendor_agency_network import run_vendor_agency_network_analysis
    from audit_rules.eligibility.inadmissible_works import run_inadmissible_work_detection
    from audit_rules.eligibility.private_beneficiaries import run_private_beneficiary_detection
    from ml.model_3_expenditure_anomaly.duplicate_expenditure import run_duplicate_expenditure_detection
    from audit_rules.fund_utilization.fund_utilization import run_fund_utilization_analysis
    from ml.model_5_audit_priority.misuse_priority import run_audit_priority_aggregation

    df_vendor_risk, _ = run_vendor_agency_network_analysis(df_master)
    df_inadmissible, _ = run_inadmissible_work_detection(df_master)
    df_private, _ = run_private_beneficiary_detection(df_master)
    df_dup_exp, _ = run_duplicate_expenditure_detection(None, df_master)
    df_fund, _ = run_fund_utilization_analysis(df_master, None)

    df_priority, _ = run_audit_priority_aggregation(
        df_scored, df_delay, df_compliance, dd_summary,
        df_vendor_risk, df_forecast, df_inadmissible,
        df_private, df_dup_exp, df_fund
    )
    t_m5 = time.time() - t0
    print(f"Step 6: M5 Audit Priority Aggregator:       {t_m5:.4f}s")

    return {
        "reconciliation": t_reco,
        "m1_cost_anomaly": t_m1,
        "m2_double_dipping": t_m2,
        "m3_delay_detection": t_m3,
        "m4_forecast_compliance": t_m4,
        "m5_audit_priority": t_m5
    }

if __name__ == "__main__":
    startup_time, api_times = profile_backend()
    ml_times = profile_pipeline()
    
    results = {
        "startup_time": startup_time,
        "api_times": api_times,
        "ml_times": ml_times
    }
    
    out_path = os.path.join(PROJECT_ROOT, "output", "profiling_baseline.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nProfiling baseline saved to {out_path}")
