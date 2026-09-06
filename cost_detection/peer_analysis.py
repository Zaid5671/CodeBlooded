import numpy as np
import pandas as pd
from .config import PEER_MIN_SIZE, IQR_MULTIPLIER

def compute_peer_statistics(df_valid):
    """
    Computes national and state-level median, Q1, Q3, and IQR statistics
    for valid works (sanction_amount >= ₹1,000).
    """
    # 1. National Peer Statistics
    nat_sanc = df_valid['sanction_amount'].dropna()
    nat_median = nat_sanc.median()
    nat_q1 = nat_sanc.quantile(0.25)
    nat_q3 = nat_sanc.quantile(0.75)
    nat_iqr = nat_q3 - nat_q1
    nat_size = len(nat_sanc)

    national_stats = {
        'peer_level': 'NATIONAL',
        'size': nat_size,
        'median': nat_median,
        'q1': nat_q1,
        'q3': nat_q3,
        'iqr': nat_iqr,
        'confidence': 'LOW',
        'peer_confidence_flag': 'NATIONAL_FALLBACK_LOW_CONFIDENCE'
    }

    # 2. State Peer Statistics (Group size >= 20)
    state_stats = {}
    for state, group in df_valid.groupby('State'):
        sanc_vals = group['sanction_amount'].dropna()
        g_size = len(sanc_vals)
        if g_size >= PEER_MIN_SIZE:
            med = sanc_vals.median()
            q1 = sanc_vals.quantile(0.25)
            q3 = sanc_vals.quantile(0.75)
            iqr = q3 - q1
            state_stats[state] = {
                'peer_level': 'STATE',
                'size': g_size,
                'median': med,
                'q1': q1,
                'q3': q3,
                'iqr': iqr,
                'confidence': 'NORMAL',
                'peer_confidence_flag': 'STATE_PEER_GROUP_VALID'
            }

    return national_stats, state_stats

def evaluate_peer_iqr(df):
    """
    Signal 2: Deterministic Peer IQR Anomaly Detector.
    Flags works where sanction_amount exceeds state (or national fallback) peer median by > 3.0 IQRs.
    """
    df_out = df.copy()
    
    # Filter valid works for statistics calculation
    valid_mask = ~df_out['is_below_floor'] & df_out['sanction_amount'].notnull()
    df_valid = df_out[valid_mask]

    national_stats, state_stats = compute_peer_statistics(df_valid)

    # Initialize output columns
    df_out['peer_level'] = 'NATIONAL'
    df_out['peer_size'] = national_stats['size']
    df_out['peer_median'] = national_stats['median']
    df_out['peer_q1'] = national_stats['q1']
    df_out['peer_q3'] = national_stats['q3']
    df_out['peer_iqr'] = national_stats['iqr']
    df_out['peer_confidence'] = 'LOW'
    df_out['peer_confidence_flag'] = 'NATIONAL_FALLBACK_LOW_CONFIDENCE'
    
    df_out['peer_deviation_ratio'] = np.nan
    df_out['robust_deviation'] = np.nan
    df_out['peer_iqr_flag'] = False
    df_out['peer_iqr_status'] = 'NORMAL'

    # Apply peer statistics per row
    peer_levels, peer_sizes, medians, q1s, q3s, iqrs, confs, conf_flags = [], [], [], [], [], [], [], []

    for _, row in df_out.iterrows():
        st = row.get('State')
        if st in state_stats:
            p = state_stats[st]
        else:
            p = national_stats
            
        peer_levels.append(p['peer_level'])
        peer_sizes.append(p['size'])
        medians.append(p['median'])
        q1s.append(p['q1'])
        q3s.append(p['q3'])
        iqrs.append(p['iqr'])
        confs.append(p['confidence'])
        conf_flags.append(p['peer_confidence_flag'])

    df_out['peer_level'] = peer_levels
    df_out['peer_size'] = peer_sizes
    df_out['peer_median'] = medians
    df_out['peer_q1'] = q1s
    df_out['peer_q3'] = q3s
    df_out['peer_iqr'] = iqrs
    df_out['peer_confidence'] = confs
    df_out['peer_confidence_flag'] = conf_flags

    # Calculate ratios for valid works
    eval_mask = valid_mask & df_out['peer_median'].notnull() & (df_out['peer_median'] > 0)
    
    sanc = df_out.loc[eval_mask, 'sanction_amount']
    med = df_out.loc[eval_mask, 'peer_median']
    iqr = df_out.loc[eval_mask, 'peer_iqr']

    df_out.loc[eval_mask, 'peer_deviation_ratio'] = (sanc - med) / med

    # IQR zero / null protection
    valid_iqr_mask = eval_mask & (iqr > 0)
    invalid_iqr_mask = eval_mask & (iqr <= 0)

    df_out.loc[valid_iqr_mask, 'robust_deviation'] = (sanc.loc[valid_iqr_mask] - med.loc[valid_iqr_mask]) / iqr.loc[valid_iqr_mask]
    df_out.loc[invalid_iqr_mask, 'peer_iqr_status'] = 'INSUFFICIENT_PEER_VARIANCE'

    # High-side flag only
    high_side_flag = (df_out['robust_deviation'] > IQR_MULTIPLIER)
    df_out.loc[valid_iqr_mask & high_side_flag, 'peer_iqr_flag'] = True
    df_out.loc[valid_iqr_mask & high_side_flag, 'peer_iqr_status'] = 'HIGH_PEER_IQR_DEVIATION'

    return df_out
