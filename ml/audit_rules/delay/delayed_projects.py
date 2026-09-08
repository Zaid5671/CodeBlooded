import pandas as pd
import numpy as np
from datetime import datetime
from ml.config import (
    DELAY_MIN_PEER_GROUP_SIZE,
    DELAY_IQR_MULTIPLIER,
    DEFAULT_REFERENCE_DATE,
)

def run_delay_detection(df_master, reference_date=DEFAULT_REFERENCE_DATE, min_peer_size=DELAY_MIN_PEER_GROUP_SIZE, iqr_multiplier=DELAY_IQR_MULTIPLIER):
    """
    MODEL 3 — Delayed Projects Detector
    Deterministic peer-relative statistical detector using Tukey IQR upper fences.
    
    Args:
        df_master: pd.DataFrame containing reconciled master work entities or sanctioned works.
        reference_date: str or datetime for ongoing duration evaluation (makes calculations reproducible).
        min_peer_size: int, minimum state peer group size before national fallback.
        iqr_multiplier: float, Tukey fence multiplier (default 1.5).
        
    Returns:
        df_delay: pd.DataFrame with delay evaluation per work entity.
        summary: dict with summary metrics.
    """
    df = df_master.copy()
    
    # Ensure clean_work_id exists
    if 'clean_work_id' not in df.columns:
        if 'canonical_work_id' in df.columns:
            df['clean_work_id'] = df['canonical_work_id']
        elif 'work_id' in df.columns:
            df['clean_work_id'] = df['work_id']
        else:
            df['clean_work_id'] = [f"WORK_{i:06d}" for i in range(len(df))]
            
    # Reference Date parsing
    if isinstance(reference_date, str):
        ref_dt = pd.to_datetime(reference_date, errors='coerce')
    elif isinstance(reference_date, (datetime, np.datetime64, pd.Timestamp)):
        ref_dt = pd.to_datetime(reference_date)
    else:
        ref_dt = pd.to_datetime(DEFAULT_REFERENCE_DATE)
        
    if pd.isna(ref_dt):
        ref_dt = pd.to_datetime(DEFAULT_REFERENCE_DATE)
        
    # Date conversions
    df['sanc_dt'] = pd.to_datetime(df.get('sanction_date'), errors='coerce')
    df['comp_dt'] = pd.to_datetime(df.get('completion_date'), errors='coerce')
    
    # Lifecycle status / Completed flag
    status_col = 'work_status' if 'work_status' in df.columns else ('lifecycle_status' if 'lifecycle_status' in df.columns else None)
    if status_col and status_col in df.columns:
        df['is_completed'] = df[status_col].astype(str).str.upper().str.contains('COMPLET') | df['comp_dt'].notnull()
    else:
        df['is_completed'] = df['comp_dt'].notnull()
        
    # Calculate completion duration for completed works with valid sanction date
    df['completion_days'] = np.where(
        df['is_completed'] & df['sanc_dt'].notnull() & df['comp_dt'].notnull(),
        (df['comp_dt'] - df['sanc_dt']).dt.days,
        np.nan
    )
    # Ensure non-negative duration
    df['completion_days'] = np.where(df['completion_days'] < 0, np.nan, df['completion_days'])
    
    # -------------------------------------------------------------------------
    # 1. PEER BASELINE CALCULATION (Genuinely completed works ONLY)
    # -------------------------------------------------------------------------
    completed_df = df[df['is_completed'] & df['completion_days'].notnull()].copy()
    national_completed_days = completed_df['completion_days'].dropna()
    
    if len(national_completed_days) > 0:
        nat_q1 = float(np.percentile(national_completed_days, 25))
        nat_q3 = float(np.percentile(national_completed_days, 75))
        nat_iqr = nat_q3 - nat_q1
        if nat_iqr == 0:
            nat_upper_fence = nat_q3 if nat_q3 > 0 else 365.0
        else:
            nat_upper_fence = nat_q3 + (iqr_multiplier * nat_iqr)
    else:
        nat_q1, nat_q3, nat_iqr = 0.0, 365.0, 365.0
        nat_upper_fence = 365.0
        
    national_completed_count = len(completed_df)
    
    # State-level completed fences
    state_fences = {}
    state_counts = {}
    
    if 'state' in df.columns:
        grouped = completed_df.groupby('state')
        for state_name, group in grouped:
            c_days = group['completion_days'].dropna()
            g_count = len(c_days)
            state_counts[state_name] = g_count
            
            if g_count >= min_peer_size:
                q1 = float(np.percentile(c_days, 25))
                q3 = float(np.percentile(c_days, 75))
                iqr = q3 - q1
                if iqr == 0:
                    fence = q3 if q3 > 0 else nat_upper_fence
                else:
                    fence = q3 + (iqr_multiplier * iqr)
                state_fences[state_name] = fence
                
    # -------------------------------------------------------------------------
    # 2. EVALUATE DELAY FOR ALL WORKS
    # -------------------------------------------------------------------------
    records = []
    state_eval_count = 0
    nat_eval_count = 0
    
    for idx, row in df.iterrows():
        cid = row['clean_work_id']
        st = str(row.get('state', '')).strip()
        is_comp = bool(row['is_completed'])
        sanc_dt = row['sanc_dt']
        comp_dt = row['comp_dt']
        
        # Determine peer baseline
        if st in state_fences:
            upper_fence_days = float(state_fences[st])
            peer_group = st
            peer_group_size = int(state_counts[st])
            delay_basis = "STATE_PEER"
            state_eval_count += 1
        else:
            upper_fence_days = float(nat_upper_fence)
            peer_group = "NATIONAL"
            peer_group_size = int(national_completed_count)
            delay_basis = "NATIONAL_FALLBACK_LOW_CONFIDENCE"
            nat_eval_count += 1
            
        # Check missing sanction date
        if pd.isna(sanc_dt):
            records.append({
                'clean_work_id': cid,
                'state': st,
                'is_completed': is_comp,
                'duration_for_delay_check': None,
                'upper_fence_days': round(upper_fence_days, 1),
                'peer_group': peer_group,
                'peer_group_size': peer_group_size,
                'delay_basis': delay_basis,
                'delay_status': "UNKNOWN_MISSING_SANCTION_DATE",
                'signal_delay': False,
                'evidence': "Delay status cannot be determined because sanction date is missing."
            })
            continue
            
        if is_comp:
            comp_days = row['completion_days']
            if pd.isna(comp_days):
                # Completed flag set but completion date missing/invalid
                duration = (ref_dt - sanc_dt).days if pd.notnull(sanc_dt) else None
                records.append({
                    'clean_work_id': cid,
                    'state': st,
                    'is_completed': True,
                    'duration_for_delay_check': duration,
                    'upper_fence_days': round(upper_fence_days, 1),
                    'peer_group': peer_group,
                    'peer_group_size': peer_group_size,
                    'delay_basis': delay_basis,
                    'delay_status': "UNKNOWN_MISSING_DATES",
                    'signal_delay': False,
                    'evidence': "Completed status indicated but valid completion date is missing."
                })
            else:
                comp_days = float(comp_days)
                sig_delay = bool(comp_days > upper_fence_days)
                if sig_delay:
                    d_status = "COMPLETED_DELAYED"
                    basis_label = "STATE" if delay_basis == "STATE_PEER" else "national"
                    ev = f"Work took {int(comp_days)} days to complete, exceeding the {basis_label} peer upper fence of {int(upper_fence_days)} days for similar completed works."
                    if delay_basis == "NATIONAL_FALLBACK_LOW_CONFIDENCE":
                        ev += " The state peer group contained fewer than 10 completed works; LOW_CONFIDENCE."
                else:
                    d_status = "COMPLETED_ON_TIME"
                    ev = f"Work completed in {int(comp_days)} days (within peer upper fence of {int(upper_fence_days)} days)."
                    
                records.append({
                    'clean_work_id': cid,
                    'state': st,
                    'is_completed': True,
                    'duration_for_delay_check': comp_days,
                    'upper_fence_days': round(upper_fence_days, 1),
                    'peer_group': peer_group,
                    'peer_group_size': peer_group_size,
                    'delay_basis': delay_basis,
                    'delay_status': d_status,
                    'signal_delay': sig_delay,
                    'evidence': ev
                })
        else:
            days_ongoing = float((ref_dt - sanc_dt).days)
            days_ongoing = max(0.0, days_ongoing)
            sig_delay = bool(days_ongoing > upper_fence_days)
            if sig_delay:
                d_status = "ONGOING_DELAYED"
                basis_label = "STATE" if delay_basis == "STATE_PEER" else "national"
                ev = f"Work has been ongoing for {int(days_ongoing)} days, exceeding the {basis_label} peer upper fence of {int(upper_fence_days)} days for similar completed works."
                if delay_basis == "NATIONAL_FALLBACK_LOW_CONFIDENCE":
                    ev += " The state peer group contained fewer than 10 completed works; LOW_CONFIDENCE."
            else:
                d_status = "ONGOING_ON_SCHEDULE"
                ev = f"Work has been ongoing for {int(days_ongoing)} days (within peer upper fence of {int(upper_fence_days)} days)."
                
            records.append({
                'clean_work_id': cid,
                'state': st,
                'is_completed': False,
                'duration_for_delay_check': days_ongoing,
                'upper_fence_days': round(upper_fence_days, 1),
                'peer_group': peer_group,
                'peer_group_size': peer_group_size,
                'delay_basis': delay_basis,
                'delay_status': d_status,
                'signal_delay': sig_delay,
                'evidence': ev
            })
            
    df_delay = pd.DataFrame(records)
    
    summary = {
        'total_works': len(df_delay),
        'completed_works': int(df_delay['is_completed'].sum()),
        'ongoing_works': int((~df_delay['is_completed']).sum()),
        'delayed_completed_works': int((df_delay['delay_status'] == 'COMPLETED_DELAYED').sum()),
        'delayed_ongoing_works': int((df_delay['delay_status'] == 'ONGOING_DELAYED').sum()),
        'total_delayed_works': int(df_delay['signal_delay'].sum()),
        'state_peer_evaluations': int((df_delay['delay_basis'] == 'STATE_PEER').sum()),
        'national_fallback_evaluations': int((df_delay['delay_basis'] == 'NATIONAL_FALLBACK_LOW_CONFIDENCE').sum()),
        'missing_sanction_date_works': int((df_delay['delay_status'] == 'UNKNOWN_MISSING_SANCTION_DATE').sum()),
        'national_upper_fence_days': round(float(nat_upper_fence), 1),
        'state_peer_groups_formed': len(state_fences)
    }
    
    return df_delay, summary
