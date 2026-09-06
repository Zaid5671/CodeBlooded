import re
import pandas as pd
from .preprocessing import clean_monetary_field, derive_work_id

def match_expenditure_data(df_sanctioned, df_expenditure):
    """
    Match sanctioned works against expenditure records using canonical Work ID.
    """
    df_sanc = df_sanctioned.copy()
    
    if df_expenditure is None or df_expenditure.empty:
        df_sanc['actual_expenditure'] = None
        df_sanc['cost_variance_ratio'] = None
        df_sanc['cost_variance_pct'] = None
        df_sanc['cost_variance_status'] = "NO_EXPENDITURE_RECORD_YET"
        return df_sanc

    df_exp = df_expenditure.copy()
    
    # 1. Clean Work ID in Expenditure
    if 'Work ID' in df_exp.columns:
        df_exp['exp_work_id'] = df_exp['Work ID'].apply(lambda x: re.sub(r'\s+', '', str(x)).upper() if pd.notna(x) else None)
    elif 'Work' in df_exp.columns:
        df_exp['exp_work_id'] = df_exp['Work'].apply(derive_work_id)
    else:
        df_exp['exp_work_id'] = None

    # 2. Parse Fund Disbursed Amount
    if 'Fund Disbursed Amount ( ₹ )' in df_exp.columns:
        df_exp['disbursed_numeric'] = clean_monetary_field(df_exp['Fund Disbursed Amount ( ₹ )'])
    else:
        df_exp['disbursed_numeric'] = 0.0

    # 3. Aggregate total expenditure per Work ID
    exp_aggregated = (
        df_exp.dropna(subset=['exp_work_id'])
        .groupby('exp_work_id')['disbursed_numeric']
        .sum()
        .reset_index()
        .rename(columns={'disbursed_numeric': 'actual_expenditure'})
    )

    # 4. Left join to preserve ALL sanctioned works
    df_matched = pd.merge(
        df_sanc,
        exp_aggregated,
        left_on='work_id',
        right_on='exp_work_id',
        how='left'
    )
    
    if 'exp_work_id' in df_matched.columns:
        df_matched.drop(columns=['exp_work_id'], inplace=True)
        
    return df_matched
