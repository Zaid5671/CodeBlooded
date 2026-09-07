import pandas as pd
import numpy as np
from ml.config import (
    COMPLIANCE_APPROVAL_DAYS,
    COMPLIANCE_MINOR_MAX,
    COMPLIANCE_MODERATE_MAX,
    IA_WATCHLIST_MIN_WORKS,
)

def run_compliance_detection(df_master, statutory_days=COMPLIANCE_APPROVAL_DAYS, minor_max=COMPLIANCE_MINOR_MAX, moderate_max=COMPLIANCE_MODERATE_MAX):
    """
    MODEL 4 — Compliance Deviation Detector
    Fully deterministic statutory/procedural rule engine (45-day statutory approval window).
    
    Args:
        df_master: pd.DataFrame containing master work entities.
        statutory_days: int, statutory approval limit (default 45 days).
        minor_max: int, max days for MINOR_DEVIATION (default 90 days).
        moderate_max: int, max days for MODERATE_DEVIATION (default 180 days).
        
    Returns:
        df_compliance: pd.DataFrame with per-work statutory compliance evaluation.
        summary: dict with summary metrics.
    """
    df = df_master.copy()
    
    if 'clean_work_id' not in df.columns:
        if 'canonical_work_id' in df.columns:
            df['clean_work_id'] = df['canonical_work_id']
        elif 'work_id' in df.columns:
            df['clean_work_id'] = df['work_id']
        else:
            df['clean_work_id'] = [f"WORK_{i:06d}" for i in range(len(df))]
            
    df['sanc_dt'] = pd.to_datetime(df.get('sanction_date'), errors='coerce')
    df['rec_dt'] = pd.to_datetime(df.get('recommended_date'), errors='coerce')
    
    df['approval_gap_days'] = np.where(
        df['sanc_dt'].notnull() & df['rec_dt'].notnull(),
        (df['sanc_dt'] - df['rec_dt']).dt.days,
        np.nan
    )
    
    records = []
    for idx, row in df.iterrows():
        cid = row['clean_work_id']
        st = str(row.get('state', '')).strip()
        ida = str(row.get('ida', '')).strip()
        gap = row['approval_gap_days']
        
        if pd.isna(gap):
            severity = "UNKNOWN_MISSING_DATES"
            sig_comp = False
            ev = "Compliance status cannot be determined because one or more required dates are missing."
        else:
            gap = float(gap)
            if gap <= statutory_days:
                severity = "COMPLIANT"
                sig_comp = False
                ev = f"Sanctioned within the {statutory_days}-day statutory approval window."
            elif gap <= minor_max:
                severity = "MINOR_DEVIATION"
                sig_comp = True
                excess = int(gap - statutory_days)
                ev = f"Sanctioned {int(gap)} days after recommendation, exceeding the {statutory_days}-day statutory window by {excess} days (MINOR_DEVIATION)."
            elif gap <= moderate_max:
                severity = "MODERATE_DEVIATION"
                sig_comp = True
                excess = int(gap - statutory_days)
                ev = f"Sanctioned {int(gap)} days after recommendation, exceeding the {statutory_days}-day statutory window by {excess} days (MODERATE_DEVIATION)."
            else:
                severity = "SEVERE_DEVIATION"
                sig_comp = True
                excess = int(gap - statutory_days)
                ev = f"Sanctioned {int(gap)} days after recommendation, exceeding the {statutory_days}-day statutory window by {excess} days (SEVERE_DEVIATION)."
                
        records.append({
            'clean_work_id': cid,
            'state': st,
            'ida': ida,
            'approval_gap_days': gap if pd.notnull(gap) else None,
            'compliance_severity': severity,
            'signal_compliance': sig_comp,
            'evidence': ev
        })
        
    df_compliance = pd.DataFrame(records)
    
    summary = {
        'total_works': len(df_compliance),
        'compliant_works': int((df_compliance['compliance_severity'] == 'COMPLIANT').sum()),
        'minor_deviation_works': int((df_compliance['compliance_severity'] == 'MINOR_DEVIATION').sum()),
        'moderate_deviation_works': int((df_compliance['compliance_severity'] == 'MODERATE_DEVIATION').sum()),
        'severe_deviation_works': int((df_compliance['compliance_severity'] == 'SEVERE_DEVIATION').sum()),
        'total_deviations': int(df_compliance['signal_compliance'].sum()),
        'missing_dates_works': int((df_compliance['compliance_severity'] == 'UNKNOWN_MISSING_DATES').sum()),
        'statutory_window_days': statutory_days
    }
    
    return df_compliance, summary

def build_ia_watchlist(df_master, min_works=IA_WATCHLIST_MIN_WORKS):
    """
    Builds the IA Accountability Watchlist aggregating approval gap metrics by Implementing Agency.
    
    Args:
        df_master: pd.DataFrame containing master work entities.
        min_works: int, minimum works threshold for inclusion (default 20).
        
    Returns:
        df_ia_watchlist: pd.DataFrame ranked by median approval gap days descending.
    """
    df = df_master.copy()
    df['sanc_dt'] = pd.to_datetime(df.get('sanction_date'), errors='coerce')
    df['rec_dt'] = pd.to_datetime(df.get('recommended_date'), errors='coerce')
    df['approval_gap_days'] = np.where(
        df['sanc_dt'].notnull() & df['rec_dt'].notnull(),
        (df['sanc_dt'] - df['rec_dt']).dt.days,
        np.nan
    )
    
    df['ida_clean'] = df.get('ida', '').fillna('').astype(str).str.strip()
    df_valid = df[df['ida_clean'].str.len() > 0].copy()
    
    if df_valid.empty:
        return pd.DataFrame(columns=['rank', 'implementing_agency', 'work_count', 'median_approval_gap_days'])
        
    stats = []
    grouped = df_valid.groupby('ida_clean')
    for ida_name, group in grouped:
        w_count = len(group)
        if w_count >= min_works:
            gaps = group['approval_gap_days'].dropna()
            med_gap = float(np.median(gaps)) if len(gaps) > 0 else np.nan
            stats.append({
                'implementing_agency': ida_name,
                'work_count': w_count,
                'median_approval_gap_days': round(med_gap, 1) if pd.notnull(med_gap) else None
            })
            
    df_watchlist = pd.DataFrame(stats)
    if not df_watchlist.empty:
        df_watchlist = df_watchlist.sort_values(by=['median_approval_gap_days', 'work_count'], ascending=[False, False]).reset_index(drop=True)
        df_watchlist.insert(0, 'rank', range(1, len(df_watchlist) + 1))
    else:
        df_watchlist = pd.DataFrame(columns=['rank', 'implementing_agency', 'work_count', 'median_approval_gap_days'])
        
    return df_watchlist
