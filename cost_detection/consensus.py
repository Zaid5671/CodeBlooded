import numpy as np
import pandas as pd
from .config import (
    RISK_LEVEL_HIGH,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_LOW,
    RISK_LEVEL_DATA_QUALITY,
)

def evaluate_consensus(df):
    """
    Combines Signal 1 (Cost Overrun), Signal 2 (Peer IQR), and Signal 3 (Isolation Forest)
    into an explainable consensus risk classification.
    """
    df_out = df.copy()

    # Count positive signals
    sig1 = df_out['cost_overrun_flag'].astype(int)
    sig2 = df_out['peer_iqr_flag'].astype(int)
    sig3 = df_out['isolation_forest_flag'].astype(int)

    df_out['positive_signal_count'] = sig1 + sig2 + sig3

    # Default classification based on signal counts
    signal_count = df_out['positive_signal_count']
    
    conditions = [
        (signal_count >= 2),
        (signal_count == 1),
        (signal_count == 0)
    ]
    
    choices = [
        RISK_LEVEL_HIGH,
        RISK_LEVEL_MEDIUM,
        RISK_LEVEL_LOW
    ]
    
    consensus_risk = np.select(conditions, choices, default=RISK_LEVEL_LOW)

    # Priority Override: Data Quality Review for implausible sanction amounts (< ₹1,000)
    dq_mask = df_out['is_below_floor']
    final_risk = np.where(dq_mask, RISK_LEVEL_DATA_QUALITY, consensus_risk)

    df_out['risk_level'] = final_risk

    return df_out
