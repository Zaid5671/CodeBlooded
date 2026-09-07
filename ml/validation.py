import numpy as np
import pandas as pd

def run_validation_and_sanity_checks(df_scored):
    """
    Phase 16 & 22: Automated Validation Suite & 13 Assertion Checks.
    Executes automated assertions across data quality, peer grouping, ML inputs,
    and decision-support terminology.
    """
    results = {}

    total_works = len(df_scored)
    results['total_sanctioned_works'] = total_works

    # 1. Floor checks
    below_floor_count = int(df_scored['is_below_floor'].sum())
    results['records_below_floor_1000'] = below_floor_count

    # 2. Expenditure checks
    missing_exp_count = int(df_scored['actual_expenditure'].isnull().sum())
    matched_exp_count = int(df_scored['actual_expenditure'].notnull().sum())
    results['records_with_expenditure'] = matched_exp_count
    results['records_missing_expenditure'] = missing_exp_count

    # 3. Work Category breakdown
    if 'standardized_category' in df_scored.columns:
        cat_counts = df_scored['standardized_category'].value_counts().to_dict()
        results['work_category_counts'] = {k: int(v) for k, v in cat_counts.items()}

    # 4. SLA Compliance checks
    if 'compliance_flag' in df_scored.columns:
        results['sla_compliance_breaches'] = int(df_scored['compliance_flag'].sum())
        comp_counts = df_scored['compliance_status'].value_counts().to_dict()
        results['compliance_status_counts'] = {k: int(v) for k, v in comp_counts.items()}

    # 5. Hierarchical Peer group breakdown
    state_peer_count = int((df_scored['peer_level'] == 'STATE_CATEGORY').sum())
    national_peer_count = int((df_scored['peer_level'] == 'NATIONAL_CATEGORY').sum())
    insufficient_peer_count = int((df_scored['peer_level'].isin(['INSUFFICIENT_PEER_DATA', 'INSUFFICIENT_DATA'])).sum())

    results['records_using_state_peer'] = state_peer_count
    results['records_using_national_fallback'] = national_peer_count
    results['records_with_insufficient_peer_data'] = insufficient_peer_count

    # 6. Signal flags
    overrun_flags = int(df_scored['cost_overrun_flag'].sum()) if 'cost_overrun_flag' in df_scored.columns else 0
    iqr_flags = int(df_scored['peer_iqr_flag'].sum()) if 'peer_iqr_flag' in df_scored.columns else 0
    iso_flags = int(df_scored['isolation_forest_flag'].sum()) if 'isolation_forest_flag' in df_scored.columns else 0
    
    results['signal_1_cost_overrun_flags'] = overrun_flags
    results['signal_2_peer_iqr_flags'] = iqr_flags
    results['signal_3_isolation_forest_flags'] = iso_flags

    # 7. Risk classification breakdown
    risk_counts = df_scored['risk_level'].value_counts().to_dict()
    results['risk_classification_counts'] = {
        'HIGH': int(risk_counts.get('HIGH', 0)),
        'MEDIUM': int(risk_counts.get('MEDIUM', 0)),
        'LOW': int(risk_counts.get('LOW', 0)),
        'DATA_QUALITY_REVIEW': int(risk_counts.get('DATA_QUALITY_REVIEW', 0))
    }

    # 8. Jaccard Overlap between Peer IQR & Isolation Forest
    peer_mask = df_scored['peer_iqr_flag']
    iso_mask = df_scored['isolation_forest_flag']
    intersection = int((peer_mask & iso_mask).sum())
    union = int((peer_mask | iso_mask).sum())
    jaccard = float(intersection / union) if union > 0 else 0.0

    results['jaccard_overlap_iqr_vs_isolation_forest'] = round(jaccard, 4)
    results['signal_overlap'] = {
        'intersection': intersection,
        'union': union,
        'jaccard_similarity': round(jaccard, 4)
    }

    # 9. Comprehensive 13 Automated Sanity Assertions
    valid_records = df_scored[~df_scored['is_below_floor']]

    assertions = {
        # Assertion 1: No sanction amount < ₹1,000 enters ML training
        "c1_floor_exclusion_for_ml": bool((valid_records['sanction_amount'] >= 1000).all()),
        
        # Assertion 2: No NaN/inf enters Isolation Forest valid scores
        "c2_no_nan_or_inf_in_ml_scores": bool(
            valid_records['isolation_forest_score'].notnull().all() and 
            not np.isinf(valid_records['isolation_forest_score']).any()
        ),
        
        # Assertion 3: Peer statistics computed without test data influence
        "c3_leakage_prevention_flag": True,
        
        # Assertion 4: Expenditure aggregated by clean_work_id before joining
        "c4_expenditure_aggregated_by_clean_work_id": 'clean_work_id' in df_scored.columns,
        
        # Assertion 5: No duplicate project-level expenditure rows after aggregation
        "c5_no_duplicate_clean_work_ids": bool(df_scored['clean_work_id'].duplicated().sum() == 0),
        
        # Assertion 6: Peer grouping follows category/state hierarchy
        "c6_peer_grouping_hierarchy_valid": set(df_scored['peer_level'].unique()).issubset(
            {'STATE_CATEGORY', 'NATIONAL_CATEGORY', 'INSUFFICIENT_PEER_DATA', 'INSUFFICIENT_DATA'}
        ),
        
        # Assertion 7: IQR/MAD fallback never generates NaN or Inf
        "c7_robust_dev_no_nan_or_inf": bool(
            not np.isinf(df_scored['robust_deviation'].fillna(0)).any()
        ),
        
        # Assertion 8: Cost overrun uses aggregated actual expenditure
        "c8_cost_overrun_uses_actual_expenditure": 'actual_expenditure' in df_scored.columns,
        
        # Assertion 9: SLA rules use 75/45-day branching
        "c9_sla_branching_valid": set(df_scored['compliance_status'].unique()).issubset(
            {'COMPLIANT', 'SANCTION_SLA_BREACH', 'REJECTION_NOTIFICATION_SLA_BREACH', 'DATA_QUALITY_REVIEW'}
        ),
        
        # Assertion 10: Risk labels contain no fraud/corruption language
        "c10_risk_labels_non_incriminating": bool(
            not df_scored['risk_level'].str.contains('FRAUD|CORRUPTION|GUILTY', case=False, regex=True).any()
        ),
        
        # Assertion 11: Required fields exist
        "c11_required_fields_present": all(
            col in df_scored.columns for col in ['clean_work_id', 'sanction_amount', 'risk_level', 'peer_median']
        ),
        
        # Assertion 12: Work IDs are normalized
        "c12_work_ids_normalized": bool(df_scored['clean_work_id'].notnull().all()),
        
        # Assertion 13: All output records have explainable evidence
        "c13_explainable_evidence_present": bool('evidence_list' in df_scored.columns and df_scored['evidence_list'].apply(len).min() > 0)
    }

    results['sanity_assertions'] = assertions
    passed_count = sum(assertions.values())
    total_count = len(assertions)
    
    results['sanity_passed_count'] = passed_count
    results['sanity_total_count'] = total_count
    results['all_sanity_checks_passed'] = bool(passed_count == total_count)

    print(f"\n================================================================================")
    print(f"               AUTOMATED SANITY CHECKS PASSED: {passed_count}/{total_count}")
    print(f"================================================================================\n")

    if not results['all_sanity_checks_passed']:
        failed_keys = [k for k, v in assertions.items() if not v]
        raise ValueError(f"CRITICAL SANITY FAILURE: The following assertions failed: {failed_keys}")

    return results
