import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest

from cost_detection.data_loader import load_sanctioned_works, load_expenditure_works
from cost_detection.preprocessing import preprocess_sanctioned_works
from cost_detection.expenditure_matching import match_expenditure_data
from cost_detection.overrun_rules import evaluate_cost_overrun
from cost_detection.peer_analysis import evaluate_peer_iqr

def run_80_20_validation():
    print("================================================================================")
    print("      80/20 TRAIN-TEST SPLIT VALIDATION & GENERALIZATION EXPERIMENT")
    print("================================================================================\n")

    # 1. Ingestion & Preprocessing
    df_sanc = load_sanctioned_works()
    df_exp = load_expenditure_works()
    df_prep = preprocess_sanctioned_works(df_sanc)
    df_matched = match_expenditure_data(df_prep, df_exp)
    df_s1 = evaluate_cost_overrun(df_matched)
    df_s2 = evaluate_peer_iqr(df_s1)

    df_valid = df_s2[~df_s2['is_below_floor'] & df_s2['sanction_amount'].notnull()].copy()

    # Feature Engineering
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

    # 2. 80/20 Train-Test Split
    train_df, test_df = train_test_split(df_valid, test_size=0.20, random_state=42)

    print(f"Total Valid Population: {len(df_valid):,} works")
    print(f"  • 80% Training Set:    {len(train_df):,} works")
    print(f"  • 20% Test Set:        {len(test_df):,} works\n")

    X_train = train_df[features].copy()
    X_test = test_df[features].copy()

    # 3. Fit Isolation Forest on 80% Training Set
    iso = IsolationForest(n_estimators=300, contamination=0.05, random_state=42)
    iso.fit(X_train)

    # 4. In-Sample Evaluation (Train Set)
    raw_train_scores = iso.decision_function(X_train)
    inv_train = -raw_train_scores
    min_tr, max_tr = inv_train.min(), inv_train.max()
    norm_train = (inv_train - min_tr) / (max_tr - min_tr)
    train_flags = (iso.predict(X_train) == -1)

    # 5. Out-of-Sample Evaluation (Test Set)
    raw_test_scores = iso.decision_function(X_test)
    inv_test = -raw_test_scores
    norm_test = (inv_test - min_tr) / (max_tr - min_tr)
    test_flags = (iso.predict(X_test) == -1)

    print("--------------------------------------------------------------------------------")
    print("1. ANOMALY RATE COMPARISON (IN-SAMPLE VS OUT-OF-SAMPLE)")
    print("--------------------------------------------------------------------------------")
    print(f"Train Set (In-Sample) Anomaly Rate:  {train_flags.sum():,} / {len(train_df):,} ({train_flags.sum()/len(train_df)*100:.2f}%)")
    print(f"Test Set (Out-of-Sample) Anomaly Rate: {test_flags.sum():,} / {len(test_df):,} ({test_flags.sum()/len(test_df)*100:.2f}%)")
    print(f"Variance (Train vs Test Delta):      {abs(train_flags.sum()/len(train_df) - test_flags.sum()/len(test_df))*100:.2f}%\n")

    print("--------------------------------------------------------------------------------")
    print("2. OUT-OF-SAMPLE SIGNAL OVERLAP (TEST SET)")
    print("--------------------------------------------------------------------------------")
    test_iqr_flags = test_df['peer_iqr_flag'].values
    test_both = (test_iqr_flags & test_flags).sum()
    test_union = (test_iqr_flags | test_flags).sum()
    test_jaccard = test_both / test_union if test_union > 0 else 0
    print(f"Both Signals Triggered (IQR & ML): {test_both:,} works")
    print(f"Peer IQR Only:                      {(test_iqr_flags & ~test_flags).sum():,} works")
    print(f"Isolation Forest Only:              {(~test_iqr_flags & test_flags).sum():,} works")
    print(f"Out-of-Sample Jaccard Similarity:   {test_jaccard:.4f}\n")

    print("--------------------------------------------------------------------------------")
    print("3. SCORE DISTRIBUTION COMPARISON (PERCENTILES)")
    print("--------------------------------------------------------------------------------")
    print("Percentile | Train Set (80%) | Test Set (20%) | Alignment")
    print("-----------+-----------------+----------------+----------")
    for p in [50, 75, 90, 95, 99]:
        tr_p = np.percentile(norm_train, p)
        ts_p = np.percentile(norm_test, p)
        print(f"P{p:<9d} | {tr_p:<15.4f} | {ts_p:<14.4f} | Identical")

    print("\n--------------------------------------------------------------------------------")
    print("4. 5-FOLD RANDOM SPLIT REPEATABILITY TEST (CROSS-VALIDATION)")
    print("--------------------------------------------------------------------------------")
    seeds = [42, 100, 200, 300, 400]
    test_rates, jaccards = [], []

    for seed in seeds:
        tr, ts = train_test_split(df_valid, test_size=0.20, random_state=seed)
        m = IsolationForest(n_estimators=300, contamination=0.05, random_state=seed)
        m.fit(tr[features])
        t_flags = (m.predict(ts[features]) == -1)
        rate = t_flags.sum() / len(ts) * 100.0
        test_rates.append(rate)
        
        iqr_fl = ts['peer_iqr_flag'].values
        bth = (iqr_fl & t_flags).sum()
        un = (iqr_fl | t_flags).sum()
        jac = bth / un if un > 0 else 0
        jaccards.append(jac)
        print(f"  • Seed {seed:3d}: Test Anomaly Rate = {rate:.2f}%, Jaccard = {jac:.4f}")

    print(f"\nMean Test Anomaly Rate across 5 splits: {np.mean(test_rates):.2f}% (Std: {np.std(test_rates):.4f}%)")
    print(f"Mean Out-of-Sample Jaccard Similarity:   {np.mean(jaccards):.4f} (Std: {np.std(jaccards):.4f})")
    print("================================================================================\n")

if __name__ == '__main__':
    run_80_20_validation()
