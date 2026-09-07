import pandas as pd
import numpy as np
from feature_engineering.preprocessing import derive_clean_work_id, clean_monetary_field

def process_and_aggregate_expenditure(df_exp):
    """
    Groups raw expenditure dataset by clean_work_id BEFORE joining to sanctioned works.
    Calculates total actual_expenditure = SUM(Fund Disbursed Amount), voucher count,
    first and last expenditure dates.
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

    # Custom per-work payment behavior calculation
    def calc_payment_features(group):
        n = len(group)
        amts = group['expenditure_amount'].values
        tot = float(amts.sum())
        mean_amt = tot / n if n > 0 else 0.0
        max_amt = float(amts.max()) if n > 0 else 0.0
        max_ratio = max_amt / tot if tot > 0 else 1.0
        
        if n > 1:
            var_amt = float(np.var(amts, ddof=1)) if n > 1 else np.nan
            dts = sorted([d for d in group['exp_dt'] if pd.notnull(d)])
            if len(dts) > 1:
                diffs = [(dts[i] - dts[i-1]).days for i in range(1, len(dts))]
                med_diff = float(np.median(diffs))
            else:
                med_diff = np.nan
        else:
            var_amt = np.nan
            med_diff = np.nan
            
        vendors = [str(v).strip() for v in group.get('Vendor Name', pd.Series(dtype=object)).dropna() if str(v).strip()]
        first_dt = group['exp_dt'].min()
        last_dt = group['exp_dt'].max()
        
        return pd.Series({
            'actual_expenditure': tot,
            'expenditure_record_count': n,
            'num_payments': n,
            'mean_payment_amount': round(mean_amt, 2),
            'max_payment_amount': round(max_amt, 2),
            'max_payment_ratio': round(max_ratio, 4),
            'payment_variance': round(var_amt, 2) if pd.notnull(var_amt) else np.nan,
            'median_time_between_payments': round(med_diff, 2) if pd.notnull(med_diff) else np.nan,
            'HAS_MULTIPLE_PAYMENTS': n > 1,
            'PAYMENT_FEATURES_AVAILABLE': n > 0,
            'first_expenditure_date': first_dt,
            'last_expenditure_date': last_dt,
            'vendor_names': vendors
        })

    agg_df = valid_exp.groupby('clean_work_id').apply(calc_payment_features).reset_index()

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
    Joins aggregated expenditure data to sanctioned works by canonical clean_work_id.
    """
    df_sanc = df_sanctioned.copy()
    df_agg = process_and_aggregate_expenditure(df_expenditure)

    # Join aggregated expenditure
    df_merged = df_sanc.merge(df_agg, on='clean_work_id', how='left')

    return df_merged
