import os
import json
import pandas as pd
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

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Run Pipeline
    df_scored, iso_model = run_detection_pipeline()

    # 2. Run Validation & Sanity Checks
    validation_results = run_validation_and_sanity_checks(df_scored)

    # 3. Save Model Configuration
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
    config_path = os.path.join(OUTPUT_DIR, "model_config.json")
    with open(config_path, "w") as f:
        json.dump(config_export, f, indent=2)

    # 4. Save Validation Results
    val_path = os.path.join(OUTPUT_DIR, "validation_results.json")
    with open(val_path, "w") as f:
        json.dump(validation_results, f, indent=2)

    # 5. Build and Save Output JSON Structure
    json_records = [build_output_json_structure(row) for _, row in df_scored.iterrows()]
    json_path = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json")
    with open(json_path, "w") as f:
        json.dump(json_records, f, indent=2)

    # 6. Save Scored Dataframe as CSV
    csv_path = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.csv")
    df_scored.to_csv(csv_path, index=False)

    # 7. Save Pipeline Summary JSON
    summary_export = {
        "model_name": MODEL_NAME,
        "total_sanctioned_works": len(df_scored),
        "risk_breakdown": validation_results['risk_classification_counts'],
        "signals": {
            "cost_overrun_flags": validation_results['signal_1_cost_overrun_flags'],
            "peer_iqr_flags": validation_results['signal_2_peer_iqr_flags'],
            "isolation_forest_flags": validation_results['signal_3_isolation_forest_flags']
        },
        "expenditure_matching": {
            "matched_works": validation_results['records_with_expenditure'],
            "missing_expenditure_works": validation_results['records_missing_expenditure']
        },
        "peer_group_levels": {
            "state_peer_group_works": validation_results['records_using_state_peer'],
            "national_fallback_works": validation_results['records_using_national_fallback']
        },
        "jaccard_overlap_iqr_vs_if": validation_results['jaccard_overlap_iqr_vs_isolation_forest'],
        "all_sanity_checks_passed": validation_results['all_sanity_checks_passed']
    }
    summary_path = os.path.join(OUTPUT_DIR, "pipeline_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary_export, f, indent=2)

    # Print Summary & Top 20 High Risk Works
    print("================================================================================")
    print("                        PIPELINE VALIDATION & SUMMARY")
    print("================================================================================")
    print(f"Total Sanctioned Population Analyzed: {validation_results['total_sanctioned_works']:,}")
    print(f"  • HIGH Risk Works:               {validation_results['risk_classification_counts']['HIGH']:,}")
    print(f"  • MEDIUM Risk Works:             {validation_results['risk_classification_counts']['MEDIUM']:,}")
    print(f"  • LOW Risk Works:                {validation_results['risk_classification_counts']['LOW']:,}")
    print(f"  • DATA_QUALITY_REVIEW (< ₹1,000): {validation_results['risk_classification_counts']['DATA_QUALITY_REVIEW']:,}")
    print("--------------------------------------------------------------------------------")
    print(f"Signal Flags Breakdown:")
    print(f"  • Signal 1 (Cost Overrun > 10%): {validation_results['signal_1_cost_overrun_flags']:,}")
    print(f"  • Signal 2 (Peer IQR Dev > 3.0): {validation_results['signal_2_peer_iqr_flags']:,}")
    print(f"  • Signal 3 (Isolation Forest):   {validation_results['signal_3_isolation_forest_flags']:,}")
    print(f"Jaccard Overlap (Peer IQR vs Isolation Forest): {validation_results['jaccard_overlap_iqr_vs_isolation_forest']:.4f}")
    print(f"All Sanity Checks Passed: {validation_results['all_sanity_checks_passed']}")
    print("================================================================================\n")

    print("================================================================================")
    print("                   TOP 20 HIGH-RISK ANOMALOUS WORKS DISPLAY")
    print("================================================================================")
    
    mp_col_name = "Hon'ble Members of Parliament"
    high_works = df_scored[df_scored['risk_level'] == 'HIGH'].sort_values(
        by=['positive_signal_count', 'isolation_forest_score'], ascending=[False, False]
    ).head(20)

    for idx, (_, row) in enumerate(high_works.iterrows(), start=1):
        mp_val = row.get(mp_col_name, 'N/A')
        state_val = row.get('State', 'N/A')
        const_val = row.get('Constituency', 'N/A')
        work_desc = str(row.get('Work description', row.get('Work', 'N/A')))[:70]
        act_exp_str = f"₹{row['actual_expenditure']:,.2f}" if pd.notnull(row['actual_expenditure']) else "NO_EXPENDITURE_RECORD_YET"
        
        print(f"\n--- [{idx}/20] WORK ID: {row['work_id']} ---")
        print(f"  MP:            {mp_val}")
        print(f"  State / Const: {state_val} | {const_val}")
        print(f"  Work:          {work_desc}")
        print(f"  Sanction Amt:  ₹{row['sanction_amount']:,.2f}")
        print(f"  Peer Median:   ₹{row['peer_median']:,.2f} ({row['peer_level']} level, Size: {row['peer_size']})")
        print(f"  Robust Dev:    {row['robust_deviation']:.2f} IQRs | Dev Ratio: {row['peer_deviation_ratio']*100:.1f}%")
        print(f"  Rec->Sanc Days: {row['rec_to_sanc_days']} days")
        print(f"  Actual Exp:    {act_exp_str}")
        print(f"  ML Anomaly:    Score={row['isolation_forest_score']:.4f} | Flag={row['isolation_forest_flag']}")
        print(f"  Risk Level:    {row['risk_level']} (Positive Signals: {row['positive_signal_count']})")
        print("  Evidence:")
        for ev in row['evidence_list']:
            print(f"    - {ev}")

    print("\n================================================================================")
    print(f"All outputs successfully exported to: {OUTPUT_DIR}")
    print("================================================================================\n")

if __name__ == '__main__':
    main()
