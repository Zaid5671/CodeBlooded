import numpy as np
import pandas as pd
from .config import PEER_MIN_SIZE, IQR_MULTIPLIER
from .category_classifier import apply_category_classification

def compute_peer_statistics(df_valid):
    """
    Computes hierarchical peer statistics (Category + State -> Category + National -> Insufficient)
    with IQR and Median Absolute Deviation (MAD) for robust variance handling.
    """
    if 'standardized_category' not in df_valid.columns:
        df_valid = apply_category_classification(df_valid)

    # 1. National-Category Peer Statistics (Group size >= 5)
    cat_national_stats = {}
    for cat, group in df_valid.groupby('standardized_category'):
        sanc_vals = group['sanction_amount'].dropna()
        g_size = len(sanc_vals)
        if g_size >= 5:
            med = float(sanc_vals.median())
            q1 = float(sanc_vals.quantile(0.25))
            q3 = float(sanc_vals.quantile(0.75))
            iqr = float(q3 - q1)
            mad = float((sanc_vals - med).abs().median())
            cat_national_stats[cat] = {
                'peer_level': 'NATIONAL_CATEGORY',
                'peer_count': g_size,
                'median': med,
                'q1': q1,
                'q3': q3,
                'iqr': iqr,
                'mad': mad,
                'confidence': 'LOW',
                'peer_confidence_flag': 'NATIONAL_CATEGORY_FALLBACK'
            }

    # 2. State-Category Peer Statistics (Group size >= 20)
    cat_state_stats = {}
    for (cat, state), group in df_valid.groupby(['standardized_category', 'State']):
        sanc_vals = group['sanction_amount'].dropna()
        g_size = len(sanc_vals)
        if g_size >= PEER_MIN_SIZE:
            med = float(sanc_vals.median())
            q1 = float(sanc_vals.quantile(0.25))
            q3 = float(sanc_vals.quantile(0.75))
            iqr = float(q3 - q1)
            mad = float((sanc_vals - med).abs().median())
            cat_state_stats[(cat, state)] = {
                'peer_level': 'STATE_CATEGORY',
                'peer_count': g_size,
                'median': med,
                'q1': q1,
                'q3': q3,
                'iqr': iqr,
                'mad': mad,
                'confidence': 'NORMAL',
                'peer_confidence_flag': 'STATE_CATEGORY_PEER_GROUP_VALID'
            }

    return cat_national_stats, cat_state_stats

def evaluate_peer_iqr(df, learned_stats=None):
    """
    Signal 2: Deterministic Peer IQR & MAD Anomaly Detector.
    Uses hierarchical peer grouping: (Category, State) -> (Category, National) -> Insufficient Data.
    Handles zero-IQR cases using Median Absolute Deviation (MAD) fallback.
    Accepts pre-computed `learned_stats` to prevent data leakage in train/test splits.
    """
    df_out = df.copy()

    if 'standardized_category' not in df_out.columns:
        df_out = apply_category_classification(df_out)

    valid_mask = ~df_out['is_below_floor'] & df_out['sanction_amount'].notnull()

    if learned_stats is None:
        df_valid = df_out[valid_mask]
        cat_national_stats, cat_state_stats = compute_peer_statistics(df_valid)
    else:
        cat_national_stats, cat_state_stats = learned_stats

    # Initialize output columns
    df_out['peer_level'] = 'NATIONAL_CATEGORY'
    df_out['peer_count'] = 0
    df_out['peer_size'] = 0  # alias
    df_out['peer_median'] = np.nan
    df_out['peer_q1'] = np.nan
    df_out['peer_q3'] = np.nan
    df_out['peer_iqr'] = np.nan
    df_out['peer_mad'] = np.nan
    df_out['peer_confidence'] = 'LOW'
    df_out['peer_confidence_flag'] = 'NATIONAL_CATEGORY_FALLBACK'
    
    df_out['peer_deviation_ratio'] = np.nan
    df_out['robust_deviation'] = np.nan
    df_out['peer_iqr_flag'] = False
    df_out['peer_iqr_status'] = 'NORMAL'

    peer_levels, peer_counts, medians, q1s, q3s, iqrs, mads, confs, conf_flags = [], [], [], [], [], [], [], [], []
    rob_devs, dev_ratios, iqr_flags, iqr_statuses = [], [], [], []

    for _, row in df_out.iterrows():
        is_below = row.get('is_below_floor', False)
        sanc = row.get('sanction_amount')

        if is_below or pd.isna(sanc):
            peer_levels.append('INSUFFICIENT_PEER_DATA')
            peer_counts.append(0)
            medians.append(np.nan)
            q1s.append(np.nan)
            q3s.append(np.nan)
            iqrs.append(np.nan)
            mads.append(np.nan)
            confs.append('INSUFFICIENT')
            conf_flags.append('DATA_QUALITY_FLOOR')
            rob_devs.append(0.0)
            dev_ratios.append(0.0)
            iqr_flags.append(False)
            iqr_statuses.append('SKIPPED_FLOOR')
            continue

        cat = row.get('standardized_category', 'OTHER')
        st = row.get('State')

        # Hierarchical Lookup
        if (cat, st) in cat_state_stats:
            p = cat_state_stats[(cat, st)]
        elif cat in cat_national_stats:
            p = cat_national_stats[cat]
        else:
            p = None

        if p is None:
            peer_levels.append('INSUFFICIENT_PEER_DATA')
            peer_counts.append(0)
            medians.append(np.nan)
            q1s.append(np.nan)
            q3s.append(np.nan)
            iqrs.append(np.nan)
            mads.append(np.nan)
            confs.append('INSUFFICIENT')
            conf_flags.append('INSUFFICIENT_PEER_DATA')
            rob_devs.append(0.0)
            dev_ratios.append(0.0)
            iqr_flags.append(False)
            iqr_statuses.append('INSUFFICIENT_PEER_DATA')
            continue

        peer_levels.append(p['peer_level'])
        peer_counts.append(p['peer_count'])
        med = p['median']
        iqr = p['iqr']
        mad = p['mad']
        medians.append(med)
        q1s.append(p['q1'])
        q3s.append(p['q3'])
        iqrs.append(iqr)
        mads.append(mad)
        confs.append(p['confidence'])
        conf_flags.append(p['peer_confidence_flag'])

        # Deviation calculations
        ratio = (sanc - med) / med if med > 0 else 0.0
        dev_ratios.append(ratio)

        # Zero-IQR & MAD Fallback Logic
        if iqr > 0:
            r_dev = (sanc - med) / iqr
            status = 'NORMAL'
        elif mad > 0:
            robust_scale = 1.4826 * mad
            r_dev = (sanc - med) / robust_scale
            status = 'MAD_FALLBACK'
        else:
            if sanc == med:
                r_dev = 0.0
                status = 'NORMAL'
            else:
                r_dev = 0.0
                status = 'ZERO_VARIANCE_UNRESOLVED'

        flag = bool(r_dev > IQR_MULTIPLIER)
        if flag:
            status = 'HIGH_PEER_DEVIATION'

        rob_devs.append(r_dev)
        iqr_flags.append(flag)
        iqr_statuses.append(status)

    df_out['peer_level'] = peer_levels
    df_out['peer_count'] = peer_counts
    df_out['peer_size'] = peer_counts
    df_out['peer_median'] = medians
    df_out['peer_q1'] = q1s
    df_out['peer_q3'] = q3s
    df_out['peer_iqr'] = iqrs
    df_out['peer_mad'] = mads
    df_out['peer_confidence'] = confs
    df_out['peer_confidence_flag'] = conf_flags

    df_out['peer_deviation_ratio'] = dev_ratios
    df_out['robust_deviation'] = rob_devs
    df_out['peer_iqr_flag'] = iqr_flags
    df_out['peer_iqr_status'] = iqr_statuses

    return df_out
