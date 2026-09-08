import pandas as pd
import numpy as np
from feature_engineering.preprocessing import derive_clean_work_id, clean_monetary_field

def process_and_aggregate_expenditure(df_exp):
    """
    Groups raw expenditure dataset by clean_work_id BEFORE joining to sanctioned works.
    Calculates total actual_expenditure = SUM(Fund Disbursed Amount), voucher count,
    first and last expenditure dates using high-throughput vectorized aggregations.
    """
    df_e = df_exp.copy()

    # 1. Clean monetary field
    amt_col = None
    for col in ['Fund Disbursed Amount ( ₹ )', 'Fund Disbursed Amount', 'amount']:
        if col in df_e.columns:
            amt_col = col
            break
            
    if amt_col is None:
        raise KeyError("Fund Disbursed Amount column not found in expenditure dataset.")
        
    df_e['expenditure_amount'] = clean_monetary_field(df_e[amt_col])

    # 2. Derive canonical clean_work_id
    id_col = 'Work ID' if 'Work ID' in df_e.columns else ('Work' if 'Work' in df_e.columns else None)
    if id_col:
        df_e['clean_work_id'] = df_e[id_col].apply(derive_clean_work_id)
    else:
        df_e['clean_work_id'] = None

    # Parse expenditure dates
    df_e['exp_dt'] = pd.to_datetime(df_e.get('Expenditure Date'), errors='coerce')

    # Filter out missing Work IDs
    valid_exp = df_e[df_e['clean_work_id'].notnull()].copy()

    # 3. High-performance vectorized aggregation
    agg_df = valid_exp.groupby('clean_work_id').agg(
        actual_expenditure=('expenditure_amount', 'sum'),
        num_payments=('expenditure_amount', 'count'),
        max_payment_amount=('expenditure_amount', 'max'),
        first_expenditure_date=('exp_dt', 'min'),
        last_expenditure_date=('exp_dt', 'max')
    ).reset_index()

    agg_df['expenditure_record_count'] = agg_df['num_payments']
    agg_df['mean_payment_amount'] = (agg_df['actual_expenditure'] / agg_df['num_payments']).round(2)
    agg_df['max_payment_amount'] = agg_df['max_payment_amount'].round(2)
    agg_df['max_payment_ratio'] = np.where(
        agg_df['actual_expenditure'] > 0,
        (agg_df['max_payment_amount'] / agg_df['actual_expenditure']).round(4),
        1.0
    )
    agg_df['HAS_MULTIPLE_PAYMENTS'] = agg_df['num_payments'] > 1
    agg_df['PAYMENT_FEATURES_AVAILABLE'] = agg_df['num_payments'] > 0

    # Calculate payment variance and median time between payments for multi-payment works
    multi_mask = agg_df['num_payments'] > 1
    multi_work_ids = set(agg_df.loc[multi_mask, 'clean_work_id'])

    if multi_work_ids:
        multi_exp = valid_exp[valid_exp['clean_work_id'].isin(multi_work_ids)]
        var_series = multi_exp.groupby('clean_work_id')['expenditure_amount'].var(ddof=1).round(2)
        
        # Median diffs
        multi_exp_dates = multi_exp[multi_exp['exp_dt'].notnull()].sort_values(['clean_work_id', 'exp_dt'])
        multi_exp_dates['prev_dt'] = multi_exp_dates.groupby('clean_work_id')['exp_dt'].shift(1)
        multi_exp_dates['dt_diff'] = (multi_exp_dates['exp_dt'] - multi_exp_dates['prev_dt']).dt.days
        med_diff_series = multi_exp_dates.groupby('clean_work_id')['dt_diff'].median().round(2)

        agg_df['payment_variance'] = agg_df['clean_work_id'].map(var_series)
        agg_df['median_time_between_payments'] = agg_df['clean_work_id'].map(med_diff_series)
    else:
        agg_df['payment_variance'] = np.nan
        agg_df['median_time_between_payments'] = np.nan

    # Vendor names mapping
    vendor_col = 'Vendor Name' if 'Vendor Name' in valid_exp.columns else ('vendor' if 'vendor' in valid_exp.columns else None)
    if vendor_col:
        valid_v = valid_exp[valid_exp[vendor_col].notnull()]
        valid_v_clean = valid_v[valid_v[vendor_col].astype(str).str.strip() != '']
        vendor_map = valid_v_clean.groupby('clean_work_id')[vendor_col].apply(lambda s: [str(v).strip() for v in s if str(v).strip()]).to_dict()
        agg_df['vendor_names'] = agg_df['clean_work_id'].map(lambda wid: vendor_map.get(wid, []))
    else:
        agg_df['vendor_names'] = [[] for _ in range(len(agg_df))]

    # Print Validation Statistics
    total_rows = len(df_exp)
    unique_works = len(agg_df)
    multi_row_works = int((agg_df['num_payments'] > 1).sum())
    single_row_works = int((agg_df['num_payments'] == 1).sum())
    max_rows = int(agg_df['num_payments'].max()) if len(agg_df) > 0 else 0
    total_agg_amount = agg_df['actual_expenditure'].sum()
    pct_multi = (multi_row_works / unique_works * 100.0) if unique_works > 0 else 0.0
    pct_single = (single_row_works / unique_works * 100.0) if unique_works > 0 else 0.0

    print(f"  [Expenditure Aggregation Validation]")
    print(f"    • Total Raw Expenditure Rows:      {total_rows:,}")
    print(f"    • Unique Expenditure Work IDs:     {unique_works:,}")
    print(f"    • Single-Payment Works (1):        {single_row_works:,} ({pct_single:.1f}%)")
    print(f"    • Multi-Payment Works (>1):        {multi_row_works:,} ({pct_multi:.1f}%)")
    print(f"    • Max Vouchers for Single Work:    {max_rows}")
    print(f"    • Total Aggregated Disbursed Amt:  ₹{total_agg_amount:,.2f}")

    return agg_df

def match_expenditure_data(df_sanctioned, df_expenditure):
    """
    Joins aggregated expenditure data to sanctioned master works DataFrame on clean_work_id.
    """
    if df_expenditure is None or len(df_expenditure) == 0:
        df_s = df_sanctioned.copy()
        df_s['actual_expenditure'] = np.nan
        df_s['expenditure_record_count'] = 0
        df_s['num_payments'] = 0
        df_s['mean_payment_amount'] = np.nan
        df_s['max_payment_amount'] = np.nan
        df_s['max_payment_ratio'] = np.nan
        df_s['payment_variance'] = np.nan
        df_s['median_time_between_payments'] = np.nan
        df_s['HAS_MULTIPLE_PAYMENTS'] = False
        df_s['PAYMENT_FEATURES_AVAILABLE'] = False
        df_s['first_expenditure_date'] = pd.NaT
        df_s['last_expenditure_date'] = pd.NaT
        df_s['vendor_names'] = [[] for _ in range(len(df_s))]
        return df_s

    df_agg = process_and_aggregate_expenditure(df_expenditure)

    cols_to_merge = [
        'clean_work_id', 'actual_expenditure', 'expenditure_record_count', 'num_payments',
        'mean_payment_amount', 'max_payment_amount', 'max_payment_ratio', 'payment_variance',
        'median_time_between_payments', 'HAS_MULTIPLE_PAYMENTS', 'PAYMENT_FEATURES_AVAILABLE',
        'first_expenditure_date', 'last_expenditure_date', 'vendor_names'
    ]
    cols_present = [c for c in cols_to_merge if c in df_agg.columns]

    df_merged = pd.merge(df_sanctioned, df_agg[cols_present], on='clean_work_id', how='left')

    df_merged['expenditure_record_count'] = df_merged['expenditure_record_count'].fillna(0).astype(int)
    df_merged['num_payments'] = df_merged['num_payments'].fillna(0).astype(int)
    df_merged['HAS_MULTIPLE_PAYMENTS'] = df_merged['HAS_MULTIPLE_PAYMENTS'].fillna(False).astype(bool)
    df_merged['PAYMENT_FEATURES_AVAILABLE'] = df_merged['PAYMENT_FEATURES_AVAILABLE'].fillna(False).astype(bool)
    if 'vendor_names' in df_merged.columns:
        df_merged['vendor_names'] = df_merged['vendor_names'].apply(lambda v: v if isinstance(v, list) else [])

    return df_merged
