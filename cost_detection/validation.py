import numpy as np
import pandas as pd

def run_validation_and_sanity_checks(df_scored):
    """
    Executes automated validation and sanity checks on the pipeline results.
    """
    results = {}

    total_works = len(df_scored)
    results['total_sanctioned_works'] = total_works

    # 1. Floor checks
    below_floor_count = int(df_scored['is_below_floor'].sum())
    results['records_below_floor_1000'] = below_floor_count

    # 2. Missing expenditure checks
    missing_exp_count = int(df_scored['actual_expenditure'].isnull().sum())
    matched_exp_count = int(df_scored['actual_expenditure'].notnull().sum())
    results['records_with_expenditure'] = matched_exp_count
    results['records_missing_expenditure'] = missing_exp_count

    # 3. Peer group breakdown
    state_peer_count = int((df_scored['peer_level'] == 'STATE').sum())
    national_peer_count = int((df_scored['peer_level'] == 'NATIONAL').sum())
    results['records_using_state_peer'] = state_peer_count
    results['records_using_national_fallback'] = national_peer_count

    # 4. Signal flags
    overrun_flags = int(df_scored['cost_overrun_flag'].sum())
    iqr_flags = int(df_scored['peer_iqr_flag'].sum())
    iso_flags = int(df_scored['isolation_forest_flag'].sum())
    
    results['signal_1_cost_overrun_flags'] = overrun_flags
    results['signal_2_peer_iqr_flags'] = iqr_flags
    results['signal_3_isolation_forest_flags'] = iso_flags

    # 5. Risk classification breakdown
    risk_counts = df_scored['risk_level'].value_counts().to_dict()
    results['risk_classification_counts'] = {
        'HIGH': int(risk_counts.get('HIGH', 0)),
        'MEDIUM': int(risk_counts.get('MEDIUM', 0)),
        'LOW': int(risk_counts.get('LOW', 0)),
        'DATA_QUALITY_REVIEW': int(risk_counts.get('DATA_QUALITY_REVIEW', 0))
    }

    # 6. Jaccard Overlap between Peer IQR & Isolation Forest
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

    # 7. Sanity assertions
    sanity_checks = {
        'no_nan_scores_in_valid_records': bool(df_scored.loc[~df_scored['is_below_floor'], 'isolation_forest_score'].notnull().all()),
        'no_infinite_robust_deviations': bool(not np.isinf(df_scored['robust_deviation'].fillna(0)).any()),
        'no_negative_sanction_amounts': bool((df_scored['sanction_amount'].dropna() >= 0).all()),
        'all_records_accounted_for': bool(total_works == (results['risk_classification_counts']['HIGH'] + 
                                                          results['risk_classification_counts']['MEDIUM'] + 
                                                          results['risk_classification_counts']['LOW'] + 
                                                          results['risk_classification_counts']['DATA_QUALITY_REVIEW'])),
        'duplicate_work_ids_check': bool(df_scored['work_id'].duplicated().sum() == 0)
    }

    results['sanity_checks'] = sanity_checks
    results['all_sanity_checks_passed'] = all(sanity_checks.values())

    return results
