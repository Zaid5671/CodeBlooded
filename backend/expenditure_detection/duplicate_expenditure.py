import os
import json
import pandas as pd
import numpy as np
from cost_detection.config import OUTPUT_DIR, DISCLAIMER_TEXT
from cost_detection.preprocessing import derive_clean_work_id, clean_monetary_field

def run_duplicate_expenditure_detection(df_exp, df_master=None):
    """
    MODULE 6 — Duplicate / Repeated Expenditure Detector.
    Scans raw expenditure vouchers for exact duplicate payments and near-repeated payment patterns.
    
    Tier 1: Exact duplicate transaction records (same work_id, vendor, amount, expenditure_date).
    Tier 2: Near-repeated payment pattern (same vendor, same agency/constituency, amount diff <= 5%, date diff <= 30 days).
    """
    if df_exp is None or df_exp.empty:
        summary_empty = {
            'total_vouchers_analyzed': 0,
            'exact_duplicate_payment_count': 0,
            'near_repeat_pattern_count': 0,
            'flagged_works_count': 0,
            'status': 'INSUFFICIENT_DATA',
            'disclaimer': DISCLAIMER_TEXT
        }
        return pd.DataFrame(), summary_empty

    df_e = df_exp.copy()
    
    amt_col = 'Fund Disbursed Amount ( ₹ )' if 'Fund Disbursed Amount ( ₹ )' in df_e.columns else ('amount' if 'amount' in df_e.columns else df_e.columns[-1])
    id_col = 'Work ID' if 'Work ID' in df_e.columns else ('clean_work_id' if 'clean_work_id' in df_e.columns else None)
    v_col = 'Vendor Name' if 'Vendor Name' in df_e.columns else 'vendor'
    dt_col = 'Expenditure Date' if 'Expenditure Date' in df_e.columns else 'date'
    
    df_e['clean_amt'] = clean_monetary_field(df_e[amt_col]).fillna(0.0)
    df_e['clean_work_id'] = [derive_clean_work_id(v) or str(v).strip() for v in df_e[id_col]] if id_col else None
    df_e['clean_vendor'] = df_e[v_col].astype(str).str.strip().str.upper() if v_col in df_e.columns else "UNKNOWN_VENDOR"
    df_e['exp_dt'] = pd.to_datetime(df_e.get(dt_col), errors='coerce')
    
    valid_vouchers = df_e.dropna(subset=['clean_work_id', 'clean_amt']).copy()
    
    # -------------------------------------------------------------------------
    # TIER 1: Exact Duplicate Payment Check
    # -------------------------------------------------------------------------
    exact_dup_mask = valid_vouchers.duplicated(subset=['clean_work_id', 'clean_vendor', 'clean_amt', 'exp_dt'], keep=False)
    exact_dup_vouchers = valid_vouchers[exact_dup_mask].copy()
    
    exact_dup_works = set(exact_dup_vouchers['clean_work_id'].unique())
    
    # -------------------------------------------------------------------------
    # TIER 2: Near-Repeated Payment Pattern (Within 30 days & Amount diff <= 5%)
    # -------------------------------------------------------------------------
    near_repeat_works = set()
    near_repeat_records = []
    
    grouped = valid_vouchers.groupby('clean_work_id')
    for work_id, group in grouped:
        if len(group) < 2:
            continue
            
        group_sorted = group.sort_values('exp_dt').reset_index(drop=True)
        for i in range(len(group_sorted) - 1):
            row_a = group_sorted.iloc[i]
            row_b = group_sorted.iloc[i + 1]
            
            amt_a, amt_b = row_a['clean_amt'], row_b['clean_amt']
            dt_a, dt_b = row_a['exp_dt'], row_b['exp_dt']
            
            if pd.notnull(dt_a) and pd.notnull(dt_b):
                date_diff_days = abs((dt_b - dt_a).days)
                max_amt = max(amt_a, amt_b)
                amt_diff_pct = (abs(amt_a - amt_b) / max_amt * 100.0) if max_amt > 0 else 0.0
                
                if date_diff_days <= 30 and amt_diff_pct <= 5.0 and row_a['clean_vendor'] == row_b['clean_vendor'] and row_a['clean_vendor'] != "UNKNOWN_VENDOR":
                    near_repeat_works.add(work_id)
                    near_repeat_records.append({
                        'clean_work_id': work_id,
                        'vendor': row_a['clean_vendor'],
                        'amount_1': round(float(amt_a), 2),
                        'amount_2': round(float(amt_b), 2),
                        'date_1': str(dt_a.strftime("%Y-%m-%d")),
                        'date_2': str(dt_b.strftime("%Y-%m-%d")),
                        'days_between': date_diff_days,
                        'amount_diff_pct': round(amt_diff_pct, 2)
                    })

    # Combine into work-level duplicate expenditure flags
    all_work_ids = []
    if df_master is not None and 'clean_work_id' in df_master.columns:
        all_work_ids = list(df_master['clean_work_id'].dropna().unique())
    elif len(valid_vouchers) > 0:
        all_work_ids = list(valid_vouchers['clean_work_id'].dropna().unique())
        
    if not all_work_ids:
        all_work_ids = list(set(list(exact_dup_works) + list(near_repeat_works)))

    records = []
    for wid in all_work_ids:
        has_exact = wid in exact_dup_works
        has_near = wid in near_repeat_works
        
        is_flagged = has_exact or has_near
        ev_list = []
        if has_exact:
            ev_list.append("POTENTIAL DUPLICATE PAYMENT: Multiple expenditure vouchers with identical work ID, vendor, amount, and date. Requires audit review.")
        if has_near:
            ev_list.append("REPEATED PAYMENT PATTERN REQUIRING REVIEW: Near-identical payment amounts to same vendor within 30-day window.")
            
        status = "POTENTIAL DUPLICATE PAYMENT — REQUIRES AUDIT REVIEW" if is_flagged else "NORMAL_PAYMENT_PATTERN"
        
        records.append({
            'clean_work_id': wid,
            'duplicate_expenditure_signal': is_flagged,
            'exact_duplicate_payment': has_exact,
            'near_repeated_payment_pattern': has_near,
            'duplicate_expenditure_status': status,
            'duplicate_expenditure_evidence': ev_list,
            'disclaimer': DISCLAIMER_TEXT
        })
        
    if not records:
        records.append({
            'clean_work_id': 'NONE',
            'duplicate_expenditure_signal': False,
            'exact_duplicate_payment': False,
            'near_repeated_payment_pattern': False,
            'duplicate_expenditure_status': 'NORMAL_PAYMENT_PATTERN',
            'duplicate_expenditure_evidence': [],
            'disclaimer': DISCLAIMER_TEXT
        })

    df_priority_res = pd.DataFrame(records)
    
    summary = {
        'total_vouchers_analyzed': len(valid_vouchers),
        'unique_works_analyzed': len(all_work_ids),
        'exact_duplicate_payment_works': len(exact_dup_works),
        'near_repeat_pattern_works': len(near_repeat_works),
        'total_flagged_duplicate_expenditure_works': int(df_priority_res['duplicate_expenditure_signal'].sum()),
        'limitations': 'Expenditure dataset lacks unique transaction GUIDs. Duplicate payments represent statistical pattern alerts requiring statutory voucher verification.',
        'disclaimer': DISCLAIMER_TEXT
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "duplicate_expenditure_results.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    df_priority_res.to_csv(os.path.join(OUTPUT_DIR, "duplicate_expenditure.csv"), index=False)
    
    return df_priority_res, summary
