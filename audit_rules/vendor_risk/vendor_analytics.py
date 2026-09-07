import pandas as pd
import numpy as np

def evaluate_vendor_analytics(df_exp_raw):
    """
    Phase 12 & 13: Vendor Concentration (HHI) & Payment Fragmentation Analytics.
    Analyzes raw expenditure records for vendor concentration per IDA/State
    and flags payment fragmentation (multiple payments to same vendor within 7 days).
    """
    if 'Vendor Name' not in df_exp_raw.columns:
        return {}, set()

    df_e = df_exp_raw.dropna(subset=['Vendor Name']).copy()
    if len(df_e) == 0:
        return {}, set()

    # 1. HHI Concentration per IDA
    hhi_by_ida = {}
    if 'IDA' in df_e.columns:
        for ida, group in df_e.groupby('IDA'):
            vendor_counts = group['Vendor Name'].value_counts()
            total = len(group)
            if total >= 5:
                shares = vendor_counts / total
                hhi = float((shares ** 2).sum())
                hhi_by_ida[ida] = {
                    'hhi': hhi,
                    'total_payments': total,
                    'top_vendor': vendor_counts.index[0],
                    'top_vendor_share': float(shares.iloc[0])
                }

    # 2. Payment Fragmentation (multiple payments to same vendor within 7 days)
    fragmented_work_ids = set()
    if 'Expenditure Date' in df_e.columns and 'Work ID' in df_e.columns:
        df_e['exp_dt'] = pd.to_datetime(df_e['Expenditure Date'], errors='coerce')
        df_sorted = df_e.dropna(subset=['exp_dt', 'Work ID']).sort_values(by=['Work ID', 'Vendor Name', 'exp_dt'])
        
        for (work_id, vendor), group in df_sorted.groupby(['Work ID', 'Vendor Name']):
            if len(group) > 1:
                diffs = group['exp_dt'].diff().dt.days
                if (diffs <= 7).any():
                    from feature_engineering.preprocessing import derive_clean_work_id
                    clean_id = derive_clean_work_id(work_id)
                    if clean_id:
                        fragmented_work_ids.add(clean_id)

    return hhi_by_ida, fragmented_work_ids
