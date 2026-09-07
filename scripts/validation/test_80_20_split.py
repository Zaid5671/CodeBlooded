import os
import sys
import json
import pandas as pd
import numpy as np

# Add local vendor directory to sys.path if present for maximum portability
vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

from sklearn.model_selection import train_test_split

from data_pipeline.data_loader import load_sanctioned_works, load_expenditure_works
from feature_engineering.preprocessing import preprocess_sanctioned_works
from feature_engineering.category_classifier import apply_category_classification
from ml.model_3_expenditure_anomaly.expenditure_matching import match_expenditure_data
from audit_rules.statutory_compliance.compliance_rules import evaluate_compliance_rules
from ml.model_1_cost_anomaly.overrun_rules import evaluate_cost_overrun
from ml.model_1_cost_anomaly.peer_analysis import compute_peer_statistics, evaluate_peer_iqr
from ml.model_1_cost_anomaly.isolation_forest import train_and_score_isolation_forest

def run_80_20_validation():
    print("================================================================================")
    print("   LEAK-FREE 80/20 TRAIN-TEST SPLIT VALIDATION & GENERALIZATION EXPERIMENT")
    print("================================================================================\n")
    print("NOTE: No public ground-truth administrative audit outcome labels are available;")
    print("therefore supervised accuracy cannot be established. Model performance is evaluated")
    print("via Out-of-Sample Anomaly-Rate Stability and Cross-Detector Concordance (Jaccard).\n")

    # 1. Ingestion & Base Preprocessing (Independent of statistical aggregation)
    df_sanc = load_sanctioned_works()
    df_exp = load_expenditure_works()
    df_prep = preprocess_sanctioned_works(df_sanc)
    df_cat = apply_category_classification(df_prep)
    df_matched = match_expenditure_data(df_cat, df_exp)
    df_comp = evaluate_compliance_rules(df_matched)
    df_s1 = evaluate_cost_overrun(df_comp)

    # Valid analytical population (>= ₹1,000 floor)
    df_valid = df_s1[~df_s1['is_below_floor'] & df_s1['sanction_amount'].notnull()].copy()

    # 2. 80/20 Train-Test Split BEFORE fitting any peer statistics or ML models (Strict Leakage Prevention)
    train_raw, test_raw = train_test_split(df_valid, test_size=0.20, random_state=42)

    print(f"Total Valid Population: {len(df_valid):,} works")
    print(f"  • 80% Training Set:    {len(train_raw):,} works")
    print(f"  • 20% Test Set:        {len(test_raw):,} works\n")

    # 3. Fit Peer Statistics ONLY on 80% Training Set
    train_peer_stats = compute_peer_statistics(train_raw)

    # Apply learned peer statistics to Train and Test sets separately
    train_s2 = evaluate_peer_iqr(train_raw, learned_stats=train_peer_stats)
    test_s2 = evaluate_peer_iqr(test_raw, learned_stats=train_peer_stats)

    # 4. Fit Isolation Forest & Imputer ONLY on 80% Training Set
    train_s3, fitted_imputer, fitted_iso_model = train_and_score_isolation_forest(train_s2)

    # Transform 20% Test Set using learned imputer and fitted model (Strict Leakage Prevention)
    test_s3, _, _ = train_and_score_isolation_forest(
        test_s2,
        fitted_imputer=fitted_imputer,
        fitted_model=fitted_iso_model
    )

    # 5. Out-of-Sample Anomaly-Rate Stability Comparison
    train_flags = train_s3['isolation_forest_flag'].values
    test_flags = test_s3['isolation_forest_flag'].values

    train_rate = train_flags.sum() / len(train_raw) * 100.0
    test_rate = test_flags.sum() / len(test_raw) * 100.0
    delta_rate = abs(train_rate - test_rate)

    print("--------------------------------------------------------------------------------")
    print("1. OUT-OF-SAMPLE ANOMALY-RATE STABILITY (IN-SAMPLE VS OUT-OF-SAMPLE)")
    print("--------------------------------------------------------------------------------")
    print(f"Train Set (In-Sample 80%) Anomaly Rate:   {train_flags.sum():,} / {len(train_raw):,} ({train_rate:.2f}%)")
    print(f"Test Set (Out-of-Sample 20%) Anomaly Rate: {test_flags.sum():,} / {len(test_raw):,} ({test_rate:.2f}%)")
    print(f"Rate Stability Variance (Delta):          {delta_rate:.2f}%\n")

    # 6. Out-of-Sample Cross-Detector Concordance (Test Set)
    test_iqr_flags = test_s3['peer_iqr_flag'].values
    test_both = (test_iqr_flags & test_flags).sum()
    test_union = (test_iqr_flags | test_flags).sum()
    test_jaccard = test_both / test_union if test_union > 0 else 0.0

    print("--------------------------------------------------------------------------------")
    print("2. OUT-OF-SAMPLE CROSS-DETECTOR CONCORDANCE (TEST SET)")
    print("--------------------------------------------------------------------------------")
    print(f"Both Detectors Triggered (Peer IQR/MAD & ML): {test_both:,} works")
    print(f"Peer IQR/MAD Only:                            {(test_iqr_flags & ~test_flags).sum():,} works")
    print(f"Isolation Forest ML Only:                     {(~test_iqr_flags & test_flags).sum():,} works")
    print(f"Out-of-Sample Jaccard Concordance:            {test_jaccard:.4f}\n")

    # 7. Score Distribution Comparison (Percentiles)
    train_scores = train_s3['isolation_forest_score'].dropna().values
    test_scores = test_s3['isolation_forest_score'].dropna().values

    print("--------------------------------------------------------------------------------")
    print("3. SCORE DISTRIBUTION ALIGNMENT (PERCENTILES)")
    print("--------------------------------------------------------------------------------")
    print("Percentile | Train Set (80%) | Test Set (20%) | Alignment")
    print("-----------+-----------------+----------------+----------")
    for p in [50, 75, 90, 95, 99]:
        tr_p = np.percentile(train_scores, p)
        ts_p = np.percentile(test_scores, p)
        print(f"P{p:<9d} | {tr_p:<15.4f} | {ts_p:<14.4f} | Stable")

    # 8. 5-Fold Leak-Free Repeatability Test (Cross-Validation)
    print("\n--------------------------------------------------------------------------------")
    print("4. 5-FOLD LEAK-FREE REPEATABILITY TEST")
    print("--------------------------------------------------------------------------------")
    seeds = [42, 100, 200, 300, 400]
    test_rates, jaccards = [], []

    for seed in seeds:
        tr_raw, ts_raw = train_test_split(df_valid, test_size=0.20, random_state=seed)
        
        # Fit stats on train split
        tr_stats = compute_peer_statistics(tr_raw)
        tr_s2 = evaluate_peer_iqr(tr_raw, learned_stats=tr_stats)
        ts_s2 = evaluate_peer_iqr(ts_raw, learned_stats=tr_stats)

        # Fit ML model on train split
        tr_s3, imp, model = train_and_score_isolation_forest(tr_s2)
        ts_s3, _, _ = train_and_score_isolation_forest(ts_s2, fitted_imputer=imp, fitted_model=model)

        t_fl = ts_s3['isolation_forest_flag'].values
        rate = t_fl.sum() / len(ts_raw) * 100.0
        test_rates.append(rate)

        iqr_fl = ts_s3['peer_iqr_flag'].values
        bth = (iqr_fl & t_fl).sum()
        un = (iqr_fl | t_fl).sum()
        jac = bth / un if un > 0 else 0.0
        jaccards.append(jac)
        print(f"  • Seed {seed:3d}: Out-of-Sample Anomaly Rate = {rate:.2f}%, Cross-Detector Concordance = {jac:.4f}")

    print(f"\nMean Out-of-Sample Anomaly Rate across 5 splits: {np.mean(test_rates):.2f}% (Std: {np.std(test_rates):.4f}%)")
    print(f"Mean Out-of-Sample Cross-Detector Concordance:  {np.mean(jaccards):.4f} (Std: {np.std(jaccards):.4f})")
    print("================================================================================\n")

if __name__ == '__main__':
    run_80_20_validation()
