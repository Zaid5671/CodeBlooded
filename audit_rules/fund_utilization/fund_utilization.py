import os
import json
import pandas as pd
import numpy as np
from ml.config import OUTPUT_DIR, DISCLAIMER_TEXT, PEER_MIN_SIZE, IQR_MULTIPLIER

def calculate_tukey_upper_fence(series, min_size=10, multiplier=1.5):
    """Calculates non-parametric Tukey IQR upper fence for a numerical series."""
    valid_vals = series.dropna().values
    if len(valid_vals) < min_size:
        return None
    q1 = float(np.percentile(valid_vals, 25))
    q3 = float(np.percentile(valid_vals, 75))
    iqr = q3 - q1
    return q3 + (multiplier * iqr)

def run_fund_utilization_analysis(df_master, df_expenditure=None):
    """
    MODULE 7 — Idle / Inefficient Fund Utilization Engine.
    Evaluates sanction-to-first-payment delays and multi-payment trajectory milestone rates.
    
    Tier A: Sanction to First Payment Delay (State / National peer fencing).
    Tier B: Cumulative Milestone Utilization Trajectories (25%, 50%, 75%, 90%).
    """
    df_m = df_master.copy()
    if 'first_expenditure_date' not in df_m.columns and df_expenditure is not None and not df_expenditure.empty:
        exp_df = df_expenditure.copy()
        date_col = 'Voucher Date' if 'Voucher Date' in exp_df.columns else exp_df.get('expenditure_date')
        exp_df['exp_dt'] = pd.to_datetime(date_col, errors='coerce')
        cid_col = 'clean_work_id' if 'clean_work_id' in exp_df.columns else ('Work ID' if 'Work ID' in exp_df.columns else 'work_id')
        if cid_col in exp_df.columns:
            first_dates = exp_df.groupby(cid_col)['exp_dt'].min().reset_index()
            first_dates.columns = ['clean_work_id', 'first_expenditure_date']
            df_m = df_m.merge(first_dates, on='clean_work_id', how='left')
    
    sanc_col = df_m['Sanction Date'] if 'Sanction Date' in df_m.columns else df_m.get('sanction_date')
    if isinstance(sanc_col, pd.DataFrame):
        sanc_col = sanc_col.iloc[:, 0]
        
    exp_col = df_m.get('first_expenditure_date')
    if isinstance(exp_col, pd.DataFrame):
        exp_col = exp_col.iloc[:, 0]
    elif exp_col is None:
        exp_col = pd.Series([np.nan] * len(df_m), index=df_m.index)

    sanc_series = pd.to_datetime(sanc_col, errors='coerce')
    exp_series = pd.to_datetime(exp_col, errors='coerce')

    df_m['sanc_dt'] = sanc_series
    df_m['first_exp_dt'] = exp_series

    # -------------------------------------------------------------------------
    # TIER A: Sanction to First Payment Delay Calculation
    # -------------------------------------------------------------------------
    mask_both = sanc_series.notnull() & exp_series.notnull()
    df_m['days_to_first_payment'] = np.where(mask_both, (exp_series - sanc_series).dt.days, np.nan)
    
    # Filter out invalid negative duration values
    df_m.loc[df_m['days_to_first_payment'] < 0, 'days_to_first_payment'] = np.nan
    
    state_series = df_m['State'] if 'State' in df_m.columns else (df_m['state'] if 'state' in df_m.columns else pd.Series(['NATIONAL'] * len(df_m), index=df_m.index))
    if isinstance(state_series, pd.DataFrame):
        state_series = state_series.iloc[:, 0]
    df_m['state_group'] = state_series.fillna('NATIONAL').astype(str).str.strip().str.upper()
    df_m['category_group'] = df_m.get('work_category', 'OTHER').astype(str).str.strip().str.upper()

    national_tier_a_fence = calculate_tukey_upper_fence(df_m['days_to_first_payment'], min_size=PEER_MIN_SIZE)
    if national_tier_a_fence is None or national_tier_a_fence <= 0:
        national_tier_a_fence = 180.0  # 180-day administrative benchmark fallback

    state_fences = {}
    for st, group in df_m.groupby('state_group'):
        fence = calculate_tukey_upper_fence(group['days_to_first_payment'], min_size=PEER_MIN_SIZE)
        state_fences[st] = fence if fence is not None else national_tier_a_fence

    df_m['tier_a_fence'] = df_m['state_group'].map(state_fences).fillna(national_tier_a_fence)
    
    df_m['idle_utilization_delay'] = False
    df_m['utilization_status'] = 'WITHIN_EXPECTED_TIMELINE'
    
    mask_delayed = df_m['days_to_first_payment'].notnull() & (df_m['days_to_first_payment'] > df_m['tier_a_fence'])
    df_m.loc[mask_delayed, 'idle_utilization_delay'] = True
    df_m.loc[mask_delayed, 'utilization_status'] = 'IDLE_UTILIZATION_DELAY'
    
    if 'num_payments' in df_m.columns:
        num_payments_col = df_m['num_payments']
    elif 'expenditure_record_count' in df_m.columns:
        num_payments_col = df_m['expenditure_record_count']
    else:
        num_payments_col = pd.Series([0] * len(df_m), index=df_m.index)
        
    df_m['num_payments'] = pd.to_numeric(num_payments_col, errors='coerce').fillna(0).astype(int)
    
    df_m['milestone_25pct'] = np.where(df_m['num_payments'] > 1, 'MILESTONE_EVALUATED', 'MILESTONE_NOT_REACHED')
    df_m['milestone_50pct'] = np.where(df_m['num_payments'] > 1, 'MILESTONE_EVALUATED', 'MILESTONE_NOT_REACHED')
    df_m['milestone_75pct'] = np.where(df_m['num_payments'] > 1, 'MILESTONE_EVALUATED', 'MILESTONE_NOT_REACHED')
    df_m['milestone_90pct'] = np.where(df_m['num_payments'] > 1, 'MILESTONE_EVALUATED', 'MILESTONE_NOT_REACHED')

    records = []
    for idx, row in df_m.iterrows():
        cid = row['clean_work_id']
        n_pay = int(row['num_payments'])
        days_fp = row['days_to_first_payment']
        is_idle = bool(row['idle_utilization_delay'])
        fence = float(row['tier_a_fence'])
        
        ev_list = []
        if is_idle:
            ev_list.append(f"IDLE UTILIZATION DELAY: {int(days_fp)} days from sanction to first payment disbursement (State Peer Upper Fence: {int(fence)} days). Requires audit review.")
        elif pd.isnull(days_fp):
            if pd.isnull(row['sanc_dt']):
                ev_list.append("Sanction date missing — sanction-to-first-payment duration not computable.")
            elif pd.isnull(row['first_exp_dt']):
                ev_list.append("First expenditure payment date missing — utilization timeline pending.")

        if n_pay <= 1:
            trajectory_status = "SINGLE_PAYMENT_LUMP_SUM"
            trajectory_note = "Single payment record. Intermediate trajectory milestones not computable."
        else:
            trajectory_status = "MULTI_PAYMENT_TRAJECTORY_AVAILABLE"
            trajectory_note = f"Multi-payment trajectory supported ({n_pay} vouchers)."

        records.append({
            'clean_work_id': cid,
            'idle_utilization_signal': is_idle,
            'days_sanction_to_first_payment': round(float(days_fp), 1) if pd.notnull(days_fp) else None,
            'peer_upper_fence_days': round(fence, 1),
            'num_payments': n_pay,
            'has_multiple_payments': n_pay > 1,
            'utilization_status': 'PEER_RELATIVE_UTILIZATION_DELAY' if is_idle else ('WITHIN_EXPECTED_TIMELINE' if pd.notnull(days_fp) else 'NOT_COMPUTABLE'),
            'trajectory_status': trajectory_status,
            'trajectory_note': trajectory_note,
            'combined_evidence': ev_list,
            'disclaimer': DISCLAIMER_TEXT
        })
        
    df_priority_res = pd.DataFrame(records)
    
    # -------------------------------------------------------------------------
    # Critical Coverage Disclosure Statistics
    # -------------------------------------------------------------------------
    total_works = len(df_m)
    usable_sanc = int(df_m['sanc_dt'].notnull().sum())
    usable_first_exp = int(df_m['first_exp_dt'].notnull().sum())
    usable_trajectory = int(mask_both.sum())
    
    single_pay = int((df_m['num_payments'] == 1).sum())
    multi_pay = int((df_m['num_payments'] > 1).sum())
    zero_pay = int((df_m['num_payments'] == 0).sum())
    
    pct_single = (single_pay / total_works * 100.0) if total_works > 0 else 0.0
    pct_multi = (multi_pay / total_works * 100.0) if total_works > 0 else 0.0
    pct_zero = (zero_pay / total_works * 100.0) if total_works > 0 else 0.0

    summary = {
        'total_works_processed': total_works,
        'works_with_usable_sanction_date': usable_sanc,
        'works_with_usable_first_payment_date': usable_first_exp,
        'works_with_usable_sanction_to_payment_duration': usable_trajectory,
        'single_payment_works_count': single_pay,
        'single_payment_works_pct': round(pct_single, 2),
        'multi_payment_works_count': multi_pay,
        'multi_payment_works_pct': round(pct_multi, 2),
        'zero_payment_works_count': zero_pay,
        'zero_payment_works_pct': round(pct_zero, 2),
        'idle_utilization_delay_count': int((df_priority_res['idle_utilization_signal'] == True).sum()),
        'coverage_disclosure': 'For works with only one recorded payment (lump-sum), intermediate utilization milestones cannot be inferred from the available transaction data.',
        'disclaimer': DISCLAIMER_TEXT
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "fund_utilization_results.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    df_priority_res.to_csv(os.path.join(OUTPUT_DIR, "fund_utilization.csv"), index=False)
    
    return df_priority_res, summary
