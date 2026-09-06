import pandas as pd
import numpy as np
from .preprocessing import derive_clean_work_id, clean_monetary_field

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

    # 3. Group by clean_work_id
    agg_dict = {
        'expenditure_amount': ['sum', 'count'],
        'exp_dt': ['min', 'max']
    }
    
    # Store vendor list if present
    if 'Vendor Name' in df_e.columns:
        agg_df = valid_exp.groupby('clean_work_id').agg(
            actual_expenditure=('expenditure_amount', 'sum'),
            expenditure_record_count=('expenditure_amount', 'count'),
            first_expenditure_date=('exp_dt', 'min'),
            last_expenditure_date=('exp_dt', 'max'),
            vendor_names=('Vendor Name', lambda s: [v for v in s.dropna().tolist() if str(v).strip()])
        ).reset_index()
    else:
        agg_df = valid_exp.groupby('clean_work_id').agg(
            actual_expenditure=('expenditure_amount', 'sum'),
            expenditure_record_count=('expenditure_amount', 'count'),
            first_expenditure_date=('exp_dt', 'min'),
            last_expenditure_date=('exp_dt', 'max')
        ).reset_index()

    # Print Validation Statistics
    total_rows = len(df_exp)
    unique_works = len(agg_df)
    multi_row_works = (agg_df['expenditure_record_count'] > 1).sum()
    max_rows = agg_df['expenditure_record_count'].max() if len(agg_df) > 0 else 0
    total_agg_amount = agg_df['actual_expenditure'].sum()

    print(f"  [Expenditure Aggregation Validation]")
    print(f"    • Total Raw Expenditure Rows:      {total_rows:,}")
    print(f"    • Unique Expenditure Work IDs:     {unique_works:,}")
    print(f"    • Works with Multi-Vouchers (>1):   {multi_row_works:,}")
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
