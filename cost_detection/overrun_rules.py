import numpy as np
import pandas as pd
from .config import COST_OVERRUN_THRESHOLD

def evaluate_cost_overrun(df):
    """
    Phase 9: Signal 1 - Deterministic Cost Overrun Checker.
    Calculates cost_variance_ratio = (actual_expenditure - sanction_amount) / sanction_amount.
    Flags DETERMINISTIC_COST_OVERRUN when actual expenditure exceeds sanctioned amount by > 10%.
    Handles missing expenditure as MISSING_EXPENDITURE_EVIDENCE (does not treat missing expenditure as 0).
    """
    df_out = df.copy()

    # Initialize output columns
    df_out['cost_variance_ratio'] = np.nan
    df_out['cost_variance_pct'] = np.nan
    df_out['cost_overrun_flag'] = False
    df_out['cost_variance_status'] = 'MISSING_EXPENDITURE_EVIDENCE'

    for idx, row in df_out.iterrows():
        act = row.get('actual_expenditure')
        sanc = row.get('sanction_amount')
        is_below = row.get('is_below_floor', False)

        if is_below or pd.isna(sanc) or sanc <= 0:
            df_out.at[idx, 'cost_variance_status'] = 'SKIPPED_FLOOR'
            continue

        if pd.isna(act):
            df_out.at[idx, 'cost_variance_status'] = 'MISSING_EXPENDITURE_EVIDENCE'
            continue

        ratio = (act - sanc) / sanc
        pct = ratio * 100.0
        
        df_out.at[idx, 'cost_variance_ratio'] = ratio
        df_out.at[idx, 'cost_variance_pct'] = pct

        if ratio > COST_OVERRUN_THRESHOLD:
            df_out.at[idx, 'cost_overrun_flag'] = True
            df_out.at[idx, 'cost_variance_status'] = 'DETERMINISTIC_COST_OVERRUN'
        else:
            df_out.at[idx, 'cost_variance_status'] = 'WITHIN_SANCTIONED_BUDGET'

    return df_out
