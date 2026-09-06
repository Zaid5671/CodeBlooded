import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from .config import IF_N_ESTIMATORS, IF_CONTAMINATION, RANDOM_STATE

def train_and_score_isolation_forest(df):
    """
    Signal 3: Isolation Forest ML Anomaly Detector.
    Multivariate unsupervised cost/timing anomaly detection.
    """
    df_out = df.copy()

    # Initialize output columns
    df_out['isolation_forest_score'] = np.nan
    df_out['isolation_forest_flag'] = False
    df_out['isolation_forest_status'] = 'NORMAL'

    # Filter valid analytical population (>= ₹1,000 floor)
    valid_mask = ~df_out['is_below_floor'] & df_out['sanction_amount'].notnull()
    df_valid = df_out[valid_mask].copy()

    if len(df_valid) == 0:
        return df_out

    # 1. Feature Engineering
    df_valid['log_sanction_amount'] = np.log1p(df_valid['sanction_amount'])
    df_valid['days_filled'] = df_valid['rec_to_sanc_days'].fillna(df_valid['rec_to_sanc_days'].median())
    df_valid['robust_dev_filled'] = df_valid['robust_deviation'].fillna(0.0)
    df_valid['peer_dev_ratio_filled'] = df_valid['peer_deviation_ratio'].fillna(0.0)

    features = [
        'sanction_amount',
        'peer_dev_ratio_filled',
        'robust_dev_filled',
        'days_filled',
        'log_sanction_amount'
    ]

    X = df_valid[features].copy()

    # 2. Fit Isolation Forest
    iso_model = IsolationForest(
        n_estimators=IF_N_ESTIMATORS,
        contamination=IF_CONTAMINATION,
        random_state=RANDOM_STATE
    )
    iso_model.fit(X)

    # 3. Compute Anomaly Score
    # sklearn decision_function: lower score = more anomalous
    raw_scores = iso_model.decision_function(X)
    
    # Invert score so higher = more anomalous
    inverted_scores = -raw_scores
    min_s, max_s = inverted_scores.min(), inverted_scores.max()
    
    if max_s > min_s:
        normalized_scores = (inverted_scores - min_s) / (max_s - min_s)
    else:
        normalized_scores = np.zeros_like(inverted_scores)

    predictions = iso_model.predict(X)  # -1 for anomaly, 1 for normal
    flags = (predictions == -1)

    # Assign scores and flags to valid records
    df_out.loc[valid_mask, 'isolation_forest_score'] = normalized_scores
    df_out.loc[valid_mask, 'isolation_forest_flag'] = flags
    df_out.loc[valid_mask, 'isolation_forest_status'] = np.where(flags, 'ANOMALOUS_PATTERN_DETECTED', 'NORMAL')

    return df_out, iso_model
