import time
import pandas as pd

from .data_loader import load_sanctioned_works, load_expenditure_works
from .preprocessing import preprocess_sanctioned_works
from .expenditure_matching import match_expenditure_data
from .overrun_rules import evaluate_cost_overrun
from .peer_analysis import evaluate_peer_iqr
from .isolation_forest import train_and_score_isolation_forest
from .consensus import evaluate_consensus
from .evidence import apply_evidence_generation

def run_detection_pipeline(sanc_filepath=None, exp_filepath=None):
    """
    Executes the complete end-to-end Anomalous Cost Estimate & Cost Overrun Detection pipeline.
    """
    t0 = time.time()
    print("================================================================================")
    print("  ANOMALOUS COST ESTIMATE & COST OVERRUN DETECTION ENGINE (LOK SABHA 18TH)")
    print("================================================================================")

    # 1. Ingestion
    print("\n[Step 1/7] Loading Lok Sabha 18th datasets...")
    df_sanc_raw = load_sanctioned_works(sanc_filepath)
    df_exp_raw = load_expenditure_works(exp_filepath)
    print(f"  Loaded {len(df_sanc_raw):,} sanctioned works and {len(df_exp_raw):,} expenditure records.")

    # 2. Preprocessing & Data Quality Layer
    print("\n[Step 2/7] Cleaning, parsing dates, and checking data quality floor...")
    df_prep = preprocess_sanctioned_works(df_sanc_raw)
    dq_count = df_prep['is_below_floor'].sum()
    print(f"  Validated {len(df_prep):,} records. Identified {dq_count} records below ₹1,000 floor.")

    # 3. Expenditure Matching
    print("\n[Step 3/7] Matching expenditure records by canonical Work ID...")
    df_matched = match_expenditure_data(df_prep, df_exp_raw)
    matched_count = df_matched['actual_expenditure'].notnull().sum()
    print(f"  Successfully matched expenditure for {matched_count:,} works ({len(df_matched) - matched_count:,} missing expenditure).")

    # 4. Signal 1: Cost Overrun Rule
    print("\n[Step 4/7] Evaluating Signal 1 (Deterministic Cost Overrun Checker)...")
    df_s1 = evaluate_cost_overrun(df_matched)
    overrun_count = df_s1['cost_overrun_flag'].sum()
    print(f"  Signal 1 Flagged: {overrun_count} works with > 10% cost overrun.")

    # 5. Signal 2: Peer IQR Detector
    print("\n[Step 5/7] Evaluating Signal 2 (Deterministic Peer IQR Detector)...")
    df_s2 = evaluate_peer_iqr(df_s1)
    iqr_count = df_s2['peer_iqr_flag'].sum()
    fallback_count = (df_s2['peer_level'] == 'NATIONAL').sum()
    print(f"  Signal 2 Flagged: {iqr_count:,} high-side peer IQR anomalies.")
    print(f"  Peer Groups: State-level used for {len(df_s2) - fallback_count:,} works; National fallback for {fallback_count} works.")

    # 6. Signal 3: Isolation Forest ML Detector
    print("\n[Step 6/7] Training & Scoring Signal 3 (Isolation Forest ML Detector)...")
    df_s3, iso_model = train_and_score_isolation_forest(df_s2)
    iso_count = df_s3['isolation_forest_flag'].sum()
    print(f"  Signal 3 Flagged: {iso_count:,} multivariate ML cost/timing anomalies.")

    # 7. Consensus & Evidence Generation
    print("\n[Step 7/7] Computing Consensus Risk Classification & Generating Evidence...")
    df_consensus = evaluate_consensus(df_s3)
    df_final = apply_evidence_generation(df_consensus)

    elapsed = time.time() - t0
    print(f"\nPipeline execution completed in {elapsed:.2f} seconds.")
    print("================================================================================\n")

    return df_final, iso_model
