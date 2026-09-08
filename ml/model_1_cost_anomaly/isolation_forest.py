import numpy as np
import pandas as pd
from ml.config import IF_N_ESTIMATORS, IF_CONTAMINATION, RANDOM_STATE

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.impute import SimpleImputer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    
    class FallbackSimpleImputer:
        def __init__(self, strategy="constant", fill_value=0.0):
            self.fill_value = fill_value
        def fit_transform(self, X):
            return np.nan_to_num(np.array(X, dtype=float), nan=self.fill_value)
        def transform(self, X):
            return np.nan_to_num(np.array(X, dtype=float), nan=self.fill_value)

    class FallbackIsolationForest:
        def __init__(self, n_estimators=300, contamination=0.05, random_state=42):
            self.contamination = contamination
            self.random_state = random_state
            self.means_ = None
            self.stds_ = None
            self.threshold_ = None
            
        def fit(self, X):
            X_arr = np.array(X, dtype=float)
            self.means_ = np.mean(X_arr, axis=0)
            self.stds_ = np.std(X_arr, axis=0)
            self.stds_[self.stds_ == 0] = 1.0
            
            z_scores = np.abs((X_arr - self.means_) / self.stds_)
            composite_dist = np.mean(z_scores, axis=1)
            
            cutoff_pct = (1.0 - self.contamination) * 100
            self.threshold_ = np.percentile(composite_dist, cutoff_pct)
            return self
            
        def decision_function(self, X):
            X_arr = np.array(X, dtype=float)
            z_scores = np.abs((X_arr - self.means_) / self.stds_)
            composite_dist = np.mean(z_scores, axis=1)
            # Higher distance = lower decision score (more anomalous)
            return -composite_dist
            
        def predict(self, X):
            X_arr = np.array(X, dtype=float)
            z_scores = np.abs((X_arr - self.means_) / self.stds_)
            composite_dist = np.mean(z_scores, axis=1)
            return np.where(composite_dist >= self.threshold_, -1, 1)

NUMERIC_FEATURES = [
    'log_sanction_amount',
    'peer_dev_ratio_filled',
    'robust_dev_filled',
    'days_filled',
    'num_payments_filled',
    'max_payment_ratio_filled',
    'payment_var_filled',
    'median_time_between_payments_filled'
]

def train_and_score_isolation_forest(df, fitted_imputer=None, fitted_model=None):
    """
    Signal 3: Isolation Forest ML Anomaly Detector.
    Multivariate unsupervised cost/timing anomaly detection using non-redundant engineered features:
    - log_sanction_amount (log scale monetary magnitude)
    - peer_dev_ratio_filled (peer deviation ratio filled with 0.0 safe baseline)
    - robust_dev_filled (IQR/MAD robust deviation filled with 0.0 safe baseline)
    - days_filled (recommendation to sanction duration in days filled with median baseline)
    - num_payments_filled (payment installments volume)
    - max_payment_ratio_filled (largest voucher ratio)
    - payment_var_filled (payment amount variance)
    - median_time_between_payments_filled (median days between payments)
    """
    df_out = df.copy()

    df_out['isolation_forest_score'] = np.nan
    df_out['isolation_forest_flag'] = False
    df_out['isolation_forest_status'] = 'NORMAL'

    valid_mask = ~df_out['is_below_floor'] & df_out['sanction_amount'].notnull()
    df_valid = df_out[valid_mask].copy()

    if len(df_valid) == 0:
        return df_out, fitted_imputer, fitted_model

    # 1. Feature Engineering
    df_valid['log_sanction_amount'] = np.log1p(df_valid['sanction_amount'])
    
    rec_days_median = df_valid['rec_to_sanc_days'].median() if pd.notnull(df_valid['rec_to_sanc_days'].median()) else 0.0
    df_valid['days_filled'] = df_valid['rec_to_sanc_days'].fillna(rec_days_median)
    df_valid['robust_dev_filled'] = df_valid['robust_deviation'].fillna(0.0)
    df_valid['peer_dev_ratio_filled'] = df_valid['peer_deviation_ratio'].fillna(0.0)

    # Payment behavior features safely filled for ML imputer
    df_valid['num_payments_filled'] = df_valid['num_payments'].fillna(0.0) if 'num_payments' in df_valid.columns else 0.0
    df_valid['max_payment_ratio_filled'] = df_valid['max_payment_ratio'].fillna(1.0) if 'max_payment_ratio' in df_valid.columns else 1.0
    df_valid['payment_var_filled'] = df_valid['payment_variance'].fillna(0.0) if 'payment_variance' in df_valid.columns else 0.0
    
    med_time = df_valid['median_time_between_payments'].median() if 'median_time_between_payments' in df_valid.columns and pd.notnull(df_valid['median_time_between_payments'].median()) else 0.0
    df_valid['median_time_between_payments_filled'] = df_valid['median_time_between_payments'].fillna(med_time) if 'median_time_between_payments' in df_valid.columns else 0.0

    features = NUMERIC_FEATURES

    X_raw = df_valid[features]
    X_raw = X_raw.replace([np.inf, -np.inf], np.nan)

    # 2. Imputation
    if fitted_imputer is None:
        if SKLEARN_AVAILABLE:
            imputer = SimpleImputer(strategy="constant", fill_value=0.0)
        else:
            imputer = FallbackSimpleImputer(strategy="constant", fill_value=0.0)
        X_imputed = imputer.fit_transform(X_raw)
    else:
        imputer = fitted_imputer
        X_imputed = imputer.transform(X_raw)

    # 3. Model Training / Evaluation
    if fitted_model is None:
        if SKLEARN_AVAILABLE:
            iso_model = IsolationForest(
                n_estimators=IF_N_ESTIMATORS,
                contamination=IF_CONTAMINATION,
                random_state=RANDOM_STATE
            )
        else:
            iso_model = FallbackIsolationForest(
                n_estimators=IF_N_ESTIMATORS,
                contamination=IF_CONTAMINATION,
                random_state=RANDOM_STATE
            )
        iso_model.fit(X_imputed)
    else:
        iso_model = fitted_model

    # 4. Compute Anomaly Score
    raw_scores = iso_model.decision_function(X_imputed)
    
    inverted_scores = -raw_scores
    min_s, max_s = inverted_scores.min(), inverted_scores.max()
    
    if max_s > min_s:
        normalized_scores = (inverted_scores - min_s) / (max_s - min_s)
    else:
        normalized_scores = np.zeros_like(inverted_scores)

    predictions = iso_model.predict(X_imputed)  # -1 for anomaly, 1 for normal
    flags = (predictions == -1)

    df_out.loc[valid_mask, 'isolation_forest_score'] = normalized_scores
    df_out.loc[valid_mask, 'isolation_forest_flag'] = flags
    df_out.loc[valid_mask, 'isolation_forest_status'] = np.where(flags, 'ANOMALOUS_PATTERN_DETECTED', 'NORMAL')

    if 'risk_level' not in df_out.columns:
        df_out['risk_level'] = np.where(df_out['isolation_forest_flag'], 'HIGH', 'LOW')

    return df_out, imputer, iso_model
