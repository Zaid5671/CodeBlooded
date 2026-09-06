import numpy as np
import pandas as pd
from .config import COST_OVERRUN_THRESHOLD

def evaluate_cost_overrun(df, threshold=COST_OVERRUN_THRESHOLD):
    """
    Signal 1: Deterministic Cost Overrun Checker.
    Evaluates whether actual expenditure exceeds sanctioned amount beyond configured threshold.
    """
    df_out = df.copy()
    
    # Initialize output columns
    df_out['cost_variance_ratio'] = np.nan
    df_out['cost_variance_pct'] = np.nan
    df_out['cost_overrun_flag'] = False
    df_out['cost_variance_status'] = "NO_EXPENDITURE_RECORD_YET"

    has_exp = df_out['actual_expenditure'].notnull()
    valid_sanc = (df_out['sanction_amount'].notnull()) & (df_out['sanction_amount'] > 0)
    eval_mask = has_exp & valid_sanc

    # Calculate variance for works with expenditure
    sanc = df_out.loc[eval_mask, 'sanction_amount']
    act = df_out.loc[eval_mask, 'actual_expenditure']
    
    ratio = (act - sanc) / sanc
    pct = ratio * 100.0
    
    df_out.loc[eval_mask, 'cost_variance_ratio'] = ratio
    df_out.loc[eval_mask, 'cost_variance_pct'] = pct
    
    flag = act > (sanc * (1.0 + threshold))
    df_out.loc[eval_mask, 'cost_overrun_flag'] = flag
    
    status = np.where(
        flag,
        "COST_OVERRUN_DETECTED",
        "WITHIN_SANCTIONED_BUDGET"
    )
    df_out.loc[eval_mask, 'cost_variance_status'] = status
    
    return df_out
