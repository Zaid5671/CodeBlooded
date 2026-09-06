import time
import pandas as pd

from .data_loader import load_sanctioned_works, load_expenditure_works
from .preprocessing import preprocess_sanctioned_works
from .category_classifier import apply_category_classification
from .expenditure_matching import match_expenditure_data
from .compliance_rules import evaluate_compliance_rules
from .overrun_rules import evaluate_cost_overrun
from .peer_analysis import evaluate_peer_iqr
from .isolation_forest import train_and_score_isolation_forest
from .vendor_analytics import evaluate_vendor_analytics
from .duplicate_detector import evaluate_duplicate_works
from .consensus import evaluate_consensus
from .evidence import apply_evidence_generation

def run_detection_pipeline(sanc_filepath=None, exp_filepath=None):
    """
    Executes the complete end-to-end Anomalous Cost Estimate & Cost Overrun Detection pipeline.
    Implements all 21-phase requirements for Lok Sabha 18th datasets.
    """
    t0 = time.time()
    print("================================================================================")
    print("  ANOMALOUS COST ESTIMATE & COST OVERRUN DETECTION ENGINE (LOK SABHA 18TH)")
    print("================================================================================")

    # 1. Ingestion
    print("\n[Step 1/10] Loading Lok Sabha 18th datasets...")
    df_sanc_raw = load_sanctioned_works(sanc_filepath)
    df_exp_raw = load_expenditure_works(exp_filepath)
    print(f"  Loaded {len(df_sanc_raw):,} sanctioned works and {len(df_exp_raw):,} expenditure records.")

    # 2. Preprocessing & Work Category Classification
    print("\n[Step 2/10] Cleaning, deriving clean_work_id, checking floor, and categorizing works...")
    df_prep = preprocess_sanctioned_works(df_sanc_raw)
    df_cat = apply_category_classification(df_prep)
    dq_count = df_cat['is_below_floor'].sum()
    cat_counts = df_cat['standardized_category'].value_counts().to_dict()
    print(f"  Validated {len(df_cat):,} records. Identified {dq_count} records below ₹1,000 floor.")
    print(f"  Categorized works into {len(cat_counts)} taxonomy groups (Top: {list(cat_counts.items())[:3]}).")

    # 3. Expenditure Aggregation & Matching
    print("\n[Step 3/10] Aggregating expenditure records by clean_work_id and matching...")
    df_matched = match_expenditure_data(df_cat, df_exp_raw)
    matched_count = df_matched['actual_expenditure'].notnull().sum()
    print(f"  Successfully matched aggregated expenditure for {matched_count:,} works.")

    # 4. SLA & Compliance Engine
    print("\n[Step 4/10] Evaluating SLA & Compliance Rules...")
    df_comp = evaluate_compliance_rules(df_matched)
    breach_count = df_comp['compliance_flag'].sum()
    print(f"  SLA Compliance Engine Flagged: {breach_count:,} sanction/rejection SLA breaches.")

    # 5. Vendor Analytics (HHI & Payment Fragmentation)
    print("\n[Step 5/10] Evaluating Vendor Concentration (HHI) & Payment Fragmentation...")
    hhi_stats, frag_work_ids = evaluate_vendor_analytics(df_exp_raw)
    df_comp['vendor_fragmentation_flag'] = df_comp['clean_work_id'].isin(frag_work_ids)
    print(f"  Vendor Analytics Flagged: {len(frag_work_ids):,} works with payment fragmentation within 7 days.")

    # 6. Duplicate Work Detector
    print("\n[Step 6/10] Evaluating Duplicate Work Detector...")
    df_dup = evaluate_duplicate_works(df_comp)
    dup_count = df_dup['potential_duplicate_flag'].sum()
    print(f"  Duplicate Detector Flagged: {dup_count:,} potential duplicate work descriptions within constituency.")

    # 7. Signal 1: Cost Overrun Rule
    print("\n[Step 7/10] Evaluating Signal 1 (Deterministic Cost Overrun Checker)...")
    df_s1 = evaluate_cost_overrun(df_dup)
    overrun_count = df_s1['cost_overrun_flag'].sum()
    print(f"  Signal 1 Flagged: {overrun_count} works with > 10% cost overrun.")

    # 8. Signal 2: Hierarchical Peer IQR/MAD Detector
    print("\n[Step 8/10] Evaluating Signal 2 (Hierarchical Peer IQR & MAD Detector)...")
    df_s2 = evaluate_peer_iqr(df_s1)
    iqr_count = df_s2['peer_iqr_flag'].sum()
    state_cat_count = (df_s2['peer_level'] == 'STATE_CATEGORY').sum()
    nat_cat_count = (df_s2['peer_level'] == 'NATIONAL_CATEGORY').sum()
    print(f"  Signal 2 Flagged: {iqr_count:,} high-side peer IQR/MAD anomalies.")
    print(f"  Peer Groups: State-Category used for {state_cat_count:,} works; National-Category for {nat_cat_count:,} works.")

    # 9. Signal 3: Isolation Forest ML Detector
    print("\n[Step 9/10] Training & Scoring Signal 3 (Isolation Forest ML Detector)...")
    df_s3, imputer, iso_model = train_and_score_isolation_forest(df_s2)
    iso_count = df_s3['isolation_forest_flag'].sum()
    print(f"  Signal 3 Flagged: {iso_count:,} multivariate ML cost/timing anomalies.")

    # 10. Consensus & Evidence Generation
    print("\n[Step 10/10] Computing Consensus Risk Classification & Generating Evidence...")
    df_consensus = evaluate_consensus(df_s3)
    df_final = apply_evidence_generation(df_consensus)

    elapsed = time.time() - t0
    print(f"\nPipeline execution completed in {elapsed:.2f} seconds.")
    print("================================================================================\n")

    return df_final, iso_model
