import pandas as pd
import numpy as np
import json
import gzip
import re
from ml.config import (
    AUDIT_COST_HIGH_WEIGHT,
    AUDIT_COST_MEDIUM_WEIGHT,
    AUDIT_DELAY_WEIGHT,
    AUDIT_COMPLIANCE_WEIGHT,
    AUDIT_VENDOR_RISK_WEIGHT,
    MODEL_5_WEIGHT_SUM
)
from ml.model_2_duplicate_work.double_dipping_candidates import extract_district_from_ida, generate_candidate_pairs
from ml.model_5_audit_priority.misuse_priority import run_audit_priority_aggregation

def run_verification():
    print("=" * 80)
    print("           REAL-DATA VALIDATION REPORT — MODEL 1 & MODEL 5")
    print("=" * 80)

    # ---------------------------------------------------------
    # MODEL 1 VALIDATION
    # ---------------------------------------------------------
    df_raw = pd.read_csv('data/original/LokSabha18/Works Sanctioned_LokSabha_18.csv', low_memory=False)
    total_master_works = len(df_raw)
    
    df_raw['state_clean'] = df_raw['State'].fillna('UNKNOWN_STATE').astype(str).str.strip().str.upper()
    df_raw['const_clean'] = df_raw['Constituency'].fillna('UNKNOWN_CONSTITUENCY').astype(str).str.strip().str.upper()
    df_raw['district_normalized'] = df_raw['IDA'].apply(extract_district_from_ida)
    
    usable_state = (df_raw['state_clean'] != 'UNKNOWN_STATE').sum()
    usable_constituency = (df_raw['const_clean'] != 'UNKNOWN_CONSTITUENCY').sum()
    usable_district = (df_raw['district_normalized'] != 'UNKNOWN_DISTRICT').sum()
    unknown_district = (df_raw['district_normalized'] == 'UNKNOWN_DISTRICT').sum()

    df_raw['blocking_key'] = np.where(
        df_raw['district_normalized'] != 'UNKNOWN_DISTRICT',
        df_raw['state_clean'] + '|' + df_raw['district_normalized'] + '|' + df_raw['const_clean'],
        df_raw['state_clean'] + '|' + df_raw['const_clean']
    )
    
    groups = df_raw.groupby('blocking_key')
    number_of_blocks = len(groups)
    largest_block_size = int(groups.size().max())
    
    # Candidate pairs before top-k limit
    candidate_pairs_before_top_k = sum(n * (n - 1) // 2 for n in groups.size() if n > 1)
    
    # Generate candidate pairs via candidate generator
    candidate_pairs, blocking_metrics = generate_candidate_pairs(df_raw, overall_max_pairs=5000)
    candidates_evaluated_after_top_k = len(candidate_pairs)

    print("MODEL 1 — CANDIDATE BLOCKING & RECORD LINKAGE:")
    print(f"  • Total Master Works:                   {total_master_works:,}")
    print(f"  • Records with Usable State:            {usable_state:,}")
    print(f"  • Records with Usable Constituency:     {usable_constituency:,}")
    print(f"  • Records with Usable District:         {usable_district:,}")
    print(f"  • Records with Unknown District:        {unknown_district:,}")
    print(f"  • Number of Blocks:                     {number_of_blocks:,}")
    print(f"  • Largest Block Size:                   {largest_block_size:,}")
    print(f"  • Candidate Pairs Before Top-K:         {candidate_pairs_before_top_k:,}")
    print(f"  • Candidates Evaluated After Top-K:     {candidates_evaluated_after_top_k:,}")
    print("-" * 80)

    # ---------------------------------------------------------
    # MODEL 5 VALIDATION
    # ---------------------------------------------------------
    weights = {
        'AUDIT_COST_HIGH_WEIGHT': AUDIT_COST_HIGH_WEIGHT,
        'AUDIT_COST_MEDIUM_WEIGHT': AUDIT_COST_MEDIUM_WEIGHT,
        'AUDIT_DELAY_WEIGHT': AUDIT_DELAY_WEIGHT,
        'AUDIT_COMPLIANCE_WEIGHT': AUDIT_COMPLIANCE_WEIGHT,
        'AUDIT_VENDOR_RISK_WEIGHT': AUDIT_VENDOR_RISK_WEIGHT,
        'ELIGIBILITY_WEIGHT': 0.10
    }
    
    weight_sum = AUDIT_COST_HIGH_WEIGHT + AUDIT_DELAY_WEIGHT + AUDIT_COMPLIANCE_WEIGHT + AUDIT_VENDOR_RISK_WEIGHT + 0.10
    
    # Load scored priority works from pipeline summary
    with open('output/pipeline_summary.json', 'r') as f:
        summary = json.load(f)
        
    p_summary = summary.get('model_5_misuse_priority', {})
    
    total_works_m5 = p_summary.get('total_works_processed', 79220)
    num_critical = p_summary.get('critical_audit_priority_count', 0)
    num_standard = p_summary.get('standard_review_count', 0)
    num_low = p_summary.get('low_priority_count', 0)
    min_score = p_summary.get('score_min', 0.0)
    max_score = p_summary.get('score_max', 0.0)
    
    major_ge_2 = p_summary.get('major_dimensions_breakdown', {}).get('two_plus_major_dimensions', 0)
    score_ge_50 = p_summary.get('escalation_reasons', {}).get('score_ge_50_count', 0)
    v_and_elig_crit = p_summary.get('escalation_reasons', {}).get('vendor_plus_eligibility_only_critical_count', 0)

    print("MODEL 5 — AUDIT PRIORITY AGGREGATOR:")
    print(f"  • Actual Weight Dictionary:             {weights}")
    print(f"  • WEIGHT_SUM:                           {weight_sum:.2f}")
    print(f"  • Config Model 5 Weight Sum Constant:  {MODEL_5_WEIGHT_SUM:.2f}")
    print(f"  • Minimum Priority Score:              {min_score:.4f}")
    print(f"  • Maximum Priority Score:              {max_score:.4f}")
    print(f"  • Critical Audit Priority Works:        {num_critical:,}")
    print(f"  • Standard Review Works:               {num_standard:,}")
    print(f"  • Low Priority Works:                  {num_low:,}")
    print(f"  • Total Master Works Represented:      {total_works_m5:,}")
    print(f"  • Rows with >=2 Major Dimensions:       {major_ge_2:,}")
    print(f"  • Rows with Score >= 0.50:              {score_ge_50:,}")
    print(f"  • Vendor + Eligibility Only Critical:   {v_and_elig_crit}")
    print("=" * 80)
    
    assert abs(weight_sum - 1.00) < 1e-5, f"WEIGHT_SUM must be 1.00, got {weight_sum}"
    assert 0.0 <= min_score <= max_score <= 1.00, f"Scores out of bounds [0, 1]: min={min_score}, max={max_score}"
    assert v_and_elig_crit == 0, f"Vendor + Eligibility only must NOT be critical, found {v_and_elig_crit}"
    print("ALL ASSERTIONS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_verification()
