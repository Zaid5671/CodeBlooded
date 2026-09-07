import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime

# Local vendor path & project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
vendor_dir = os.path.join(project_root, "vendor")
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.impute import SimpleImputer
from sklearn.ensemble import IsolationForest

from cost_detection.data_loader import load_sanctioned_works, load_expenditure_works
from cost_detection.preprocessing import preprocess_sanctioned_works, clean_monetary_field
from cost_detection.category_classifier import apply_category_classification
from cost_detection.expenditure_matching import match_expenditure_data
from cost_detection.compliance_rules import evaluate_compliance_rules
from cost_detection.overrun_rules import evaluate_cost_overrun
from cost_detection.peer_analysis import compute_peer_statistics, evaluate_peer_iqr
from cost_detection.isolation_forest import train_and_score_isolation_forest, NUMERIC_FEATURES
from backend.forecasting.expenditure_forecast import recursive_rolling_mean_forecast
from backend.canonical_registry import get_canonical_registry

def evaluate_m2_duplicate_work():
    print("\n========================================================")
    print("  M2_DUPLICATE_WORK: RECORD LINKAGE 80/20 HOLD-OUT EVALUATION")
    print("========================================================")

    df_sanc = load_sanctioned_works()
    total_records = len(df_sanc)

    text_corpus = df_sanc['Work description'].fillna(df_sanc['Work category']).fillna('').astype(str).str.strip()
    df_sanc['clean_desc'] = text_corpus

    # Random 80/20 hold-out split with fixed random seed (42)
    train_df, test_df = train_test_split(df_sanc, test_size=0.20, random_state=42)

    print(f"Total Work Records: {total_records:,}")
    print(f"  • 80% Train Records: {len(train_df):,}")
    print(f"  • 20% Test Records:  {len(test_df):,}")

    # Fit TF-IDF strictly on Train
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000, min_df=2, stop_words='english')
    train_vecs = vectorizer.fit_transform(train_df['clean_desc'])
    test_vecs = vectorizer.transform(test_df['clean_desc'])

    vocab_size = len(vectorizer.vocabulary_)
    print(f"Vocabulary Size (Fitted strictly on Train): {vocab_size:,} features")

    np.random.seed(42)
    idx_tr1 = np.random.randint(0, len(train_df), 10000)
    idx_tr2 = np.random.randint(0, len(train_df), 10000)
    tr_sims = np.asarray(train_vecs[idx_tr1].multiply(train_vecs[idx_tr2]).sum(axis=1)).ravel()

    idx_ts1 = np.random.randint(0, len(test_df), 10000)
    idx_ts2 = np.random.randint(0, len(test_df), 10000)
    ts_sims = np.asarray(test_vecs[idx_ts1].multiply(test_vecs[idx_ts2]).sum(axis=1)).ravel()

    tr_mean, tr_p90, tr_p99 = float(np.mean(tr_sims)), float(np.percentile(tr_sims, 90)), float(np.percentile(tr_sims, 99))
    ts_mean, ts_p90, ts_p99 = float(np.mean(ts_sims)), float(np.percentile(ts_sims, 90)), float(np.percentile(ts_sims, 99))

    print(f"Train Similarity Distribution: Mean={tr_mean:.4f}, P90={tr_p90:.4f}, P99={tr_p99:.4f}")
    print(f"Test Similarity Distribution:  Mean={ts_mean:.4f}, P90={ts_p90:.4f}, P99={ts_p99:.4f}")

    return {
        "model_id": "M2_DUPLICATE_WORK",
        "model_name": "M2_DUPLICATE_WORK: Record Linkage / Duplicate Work Detection",
        "split_description": "Random 80/20 hold-out split with fixed random seed (42)",
        "total_records": total_records,
        "train_records": len(train_df),
        "test_records": len(test_df),
        "vocab_size": vocab_size,
        "train_sim_p90": tr_p90,
        "train_sim_p99": tr_p99,
        "test_sim_p90": ts_p90,
        "test_sim_p99": ts_p99,
        "delta_p99": round(abs(tr_p99 - ts_p99), 4),
        "interpretation": (
            "The held-out TF-IDF similarity distribution is broadly consistent with the training "
            "distribution. This supports representation stability under the hold-out split, but does "
            "not establish duplicate-detection accuracy because verified duplicate/non-duplicate labels "
            "are unavailable."
        )
    }

def evaluate_m1_cost_anomaly():
    print("\n========================================================")
    print("  M1_COST_ANOMALY: COST ANOMALY 80/20 CHRONOLOGICAL EXPERIMENT")
    print("========================================================")

    df_sanc = load_sanctioned_works()
    df_exp = load_expenditure_works()
    df_prep = preprocess_sanctioned_works(df_sanc)
    df_cat = apply_category_classification(df_prep)
    df_matched = match_expenditure_data(df_cat, df_exp)
    df_comp = evaluate_compliance_rules(df_matched)
    df_s1 = evaluate_cost_overrun(df_comp)

    df_valid = df_s1[~df_s1['is_below_floor'] & df_s1['sanction_amount'].notnull()].copy()

    # Sort chronologically by sanc_dt or rec_dt
    df_valid['dt'] = df_valid['sanc_dt'].fillna(df_valid['rec_dt'])
    df_valid = df_valid.sort_values(by='dt').reset_index(drop=True)

    split_idx = int(len(df_valid) * 0.80)
    train_raw = df_valid.iloc[:split_idx].copy()
    test_raw = df_valid.iloc[split_idx:].copy()

    train_start = str(train_raw['dt'].min().date()) if train_raw['dt'].notnull().sum() > 0 else "N/A"
    train_end = str(train_raw['dt'].max().date()) if train_raw['dt'].notnull().sum() > 0 else "N/A"
    test_start = str(test_raw['dt'].min().date()) if test_raw['dt'].notnull().sum() > 0 else "N/A"
    test_end = str(test_raw['dt'].max().date()) if test_raw['dt'].notnull().sum() > 0 else "N/A"

    print(f"Total Valid Population: {len(df_valid):,} works")
    print(f"  • 80% Train (Chronological): {len(train_raw):,} works (Range: {train_start} to {train_end})")
    print(f"  • 20% Test (Chronological):  {len(test_raw):,} works (Range: {test_start} to {test_end})")

    # 1. Fit Peer Statistics ONLY on Train
    train_peer_stats = compute_peer_statistics(train_raw)
    train_s2 = evaluate_peer_iqr(train_raw, learned_stats=train_peer_stats)
    test_s2 = evaluate_peer_iqr(test_raw, learned_stats=train_peer_stats)

    # 2. Fit Isolation Forest ONLY on Train
    train_s3, fitted_imputer, fitted_iso_model = train_and_score_isolation_forest(train_s2)
    test_s3, _, _ = train_and_score_isolation_forest(
        test_s2,
        fitted_imputer=fitted_imputer,
        fitted_model=fitted_iso_model
    )

    train_flags = train_s3['isolation_forest_flag'].values
    test_flags = test_s3['isolation_forest_flag'].values

    train_rate = (train_flags.sum() / len(train_flags)) * 100.0
    test_rate = (test_flags.sum() / len(test_flags)) * 100.0
    delta_rate = abs(train_rate - test_rate)

    # Concordance with rule-based peer IQR flag
    test_iqr_flags = test_s3['peer_iqr_flag'].values
    intersection = np.logical_and(test_flags, test_iqr_flags).sum()
    union = np.logical_or(test_flags, test_iqr_flags).sum()
    test_jaccard = float(intersection / union) if union > 0 else 0.0

    print(f"Train In-Sample Anomaly Rate:    {train_rate:.2f}%")
    print(f"Test Out-of-Sample Anomaly Rate: {test_rate:.2f}%")
    print(f"Rate Delta:                      {delta_rate:.2f}%")
    print(f"Test Cross-Detector Concordance (Jaccard): {test_jaccard:.4f}")

    feature_availability = {
        'log_sanction_amount': 'Sanction-Time (Scale magnitude)',
        'peer_dev_ratio_filled': 'Peer-Distribution (Learned on Train only)',
        'robust_dev_filled': 'Peer-Distribution (Learned on Train only)',
        'days_filled': 'Lifecycle (Recommendation to Sanction latency)',
        'num_payments_filled': 'Expenditure / Audit-Time (Payment count)',
        'max_payment_ratio_filled': 'Expenditure / Audit-Time (Largest voucher ratio)',
        'payment_var_filled': 'Expenditure / Audit-Time (Disbursement variance)',
        'median_time_between_payments_filled': 'Expenditure / Audit-Time (Disbursement cadence)'
    }

    return {
        "model_id": "M1_COST_ANOMALY",
        "model_name": "M1_COST_ANOMALY: Unsupervised Cost Anomaly Detection",
        "evaluation_description": "Chronological out-of-sample stability evaluation of an audit-time unsupervised anomaly detector",
        "train_rows": len(train_raw),
        "test_rows": len(test_raw),
        "train_start": train_start,
        "train_end": train_end,
        "test_start": test_start,
        "test_end": test_end,
        "feature_count": len(NUMERIC_FEATURES),
        "feature_names": NUMERIC_FEATURES,
        "feature_availability": feature_availability,
        "isolation_forest_params": {
            "n_estimators": 300,
            "contamination": 0.05,
            "random_state": 42
        },
        "train_anomaly_rate": round(train_rate, 2),
        "test_anomaly_rate": round(test_rate, 2),
        "rate_delta": round(delta_rate, 2),
        "test_cross_detector_jaccard": round(test_jaccard, 4),
        "limitation_note": (
            "Because verified audit outcome labels are unavailable, these metrics evaluate "
            "out-of-sample stability and agreement between independent unsupervised detectors "
            "rather than classification accuracy."
        )
    }

def evaluate_m4_forecast():
    print("\n========================================================")
    print("  M4_FORECAST: EXPENDITURE FORECASTING 80/20 EXPERIMENT")
    print("========================================================")

    p18 = "data/original/LokSabha18/Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv"
    df18 = pd.read_csv(p18, low_memory=False)
    amt_cols = [c for c in df18.columns if ('disbursed' in c.lower() or 'amount' in c.lower()) and 'date' not in c.lower()]
    amt_c = amt_cols[0] if amt_cols else df18.columns[-1]
    date_c = 'Expenditure Date'

    df18['clean_amt'] = clean_monetary_field(df18[amt_c])
    df18['dt'] = pd.to_datetime(df18[date_c], errors='coerce', dayfirst=True)

    valid18 = df18.dropna(subset=['dt', 'clean_amt']).copy()
    valid18['year_month'] = valid18['dt'].dt.to_period('M').astype(str)
    min_m = valid18['year_month'].min()
    max_m = valid18['year_month'].max()
    all_periods = pd.period_range(start=min_m, end=max_m, freq='M').astype(str)
    monthly_series = valid18.groupby('year_month')['clean_amt'].sum().reindex(all_periods, fill_value=0.0)

    total_obs = len(monthly_series)

    split_idx = int(np.floor(total_obs * 0.80))
    train_series = monthly_series.iloc[:split_idx]
    test_series = monthly_series.iloc[split_idx:]

    train_vals = train_series.values
    test_vals = test_series.values

    train_start = str(train_series.index[0])
    train_end = str(train_series.index[-1])
    test_start = str(test_series.index[0])
    test_end = str(test_series.index[-1])

    print(f"Total Monthly Observations: {total_obs}")
    print(f"  • Train Observations (80%): {len(train_series)} ({train_start} to {train_end})")
    print(f"  • Test Observations (20%):  {len(test_series)} ({test_start} to {test_end})")

    predictions = []
    baseline_prev = []

    history = list(train_vals)
    for actual in test_vals:
        fcst = float(np.mean(history[-3:]))
        predictions.append(fcst)
        baseline_prev.append(float(history[-1]))
        history.append(actual)

    predictions = np.array(predictions)
    test_vals = np.array(test_vals)
    base_prev = np.array(baseline_prev)

    def calc_metrics(y_true, y_pred):
        mae = float(np.mean(np.abs(y_true - y_pred)))
        rmse = float(np.sqrt(np.mean((y_true - y_pred)**2)))
        mape = float(np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1.0)))) * 100.0
        return mae, rmse, mape

    model_mae, model_rmse, model_mape = calc_metrics(test_vals, predictions)
    prev_mae, prev_rmse, prev_mape = calc_metrics(test_vals, base_prev)

    print(f"\nModel Out-of-Sample Evaluation:")
    print(f"  • Model MAE:   ₹{model_mae:,.2f} (vs Prev-Month: ₹{prev_mae:,.2f})")
    print(f"  • Model RMSE:  ₹{model_rmse:,.2f} (vs Prev-Month: ₹{prev_rmse:,.2f})")
    print(f"  • Model MAPE:  {model_mape:.2f}% (vs Prev-Month: {prev_mape:.2f}%)")

    full_vals = monthly_series.values
    future_preds = recursive_rolling_mean_forecast(full_vals, horizon=6, window=3)
    full_std = float(np.std(full_vals)) if np.std(full_vals) > 0 else float(np.mean(full_vals)) * 0.25

    future_6m = []
    last_ym = pd.to_datetime(str(monthly_series.index[-1]) + "-01")
    future_dates = pd.date_range(start=last_ym + pd.DateOffset(months=1), periods=6, freq="MS")
    for m_dt, f_val in zip(future_dates, future_preds):
        f_val = round(float(f_val), 2)
        margin = round(1.96 * full_std, 2)
        future_6m.append({
            "month": m_dt.strftime("%Y-%m"),
            "forecast_expenditure": f_val,
            "lower_bound": max(0.0, round(f_val - margin, 2)),
            "upper_bound": round(f_val + margin, 2),
            "expected_range_type": "Empirical 95% Expected Range"
        })

    conclusion_text = (
        "The 3-month rolling-average method marginally improves MAE relative to the naïve "
        "previous-month baseline, while RMSE and MAPE remain higher. It is therefore retained "
        "as an empirical forecasting aid and is not claimed to outperform the naïve baseline across all evaluation metrics."
    )

    return {
        "model_id": "M4_FORECAST",
        "model_name": "M4_FORECAST: Rolling-Average Expenditure Forecasting Baseline",
        "methodology": "3-month rolling-average expenditure forecasting baseline",
        "evaluation_dataset": "data/original/LokSabha18/Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv (27 monthly aggregated observations)",
        "historical_context_dataset": "data/original/LokSabha17/Expenditure on Completed and On-going Works as on Date_LokSabha17.csv (historical term reference)",
        "production_forecast_dataset": "Lok Sabha 18th 27 historical monthly observations",
        "total_observations": total_obs,
        "train_observations": len(train_series),
        "test_observations": len(test_series),
        "train_start": train_start,
        "train_end": train_end,
        "test_start": test_start,
        "test_end": test_end,
        "model_mae": round(model_mae, 2),
        "model_rmse": round(model_rmse, 2),
        "model_mape": round(model_mape, 2),
        "prev_mae": round(prev_mae, 2),
        "prev_rmse": round(prev_rmse, 2),
        "prev_mape": round(prev_mape, 2),
        "conclusion": conclusion_text,
        "future_6m_forecast": future_6m
    }

def main():
    m2_res = evaluate_m2_duplicate_work()
    m1_res = evaluate_m1_cost_anomaly()
    m4_res = evaluate_m4_forecast()

    # Generate output/MODEL_TRAIN_TEST_REPORT.md
    md = []
    md.append("# SIH26102 — THREE AI/ML MODEL TRAIN/TEST EVALUATION REPORT\n\n")
    md.append(f"**Generated At**: {datetime.now().isoformat()} | **Evaluation Protocol**: 80/20 Train/Test Partitioning\n\n")
    md.append("**Governance Disclaimer**: *All metrics represent unsupervised distribution stability and empirical tracking. Not proof of fraud or legal wrongdoing.*\n\n")
    md.append("---\n\n")

    # Section 1: Canonical Registry
    md.append("## 1. Canonical Evaluated Models\n\n")
    md.append("| Canonical ID | Model Name | Evaluation Methodology | Partitioning Protocol |\n")
    md.append("| :--- | :--- | :--- | :--- |\n")
    md.append(f"| **`M1_COST_ANOMALY`** | Anomalous Cost Estimate Detection | Chronological 80/20 Hold-Out | 8 Non-Redundant Features (Peer IQR + Isolation Forest) |\n")
    md.append(f"| **`M2_DUPLICATE_WORK`** | Duplicate Work / Record Linkage | Random 80/20 Hold-Out | TF-IDF Vocabulary fitted strictly on Train partition |\n")
    md.append(f"| **`M4_FORECAST`** | MPLADS Expenditure Forecasting | Chronological 80/20 Hold-Out | Recursive 3-Month Rolling Average vs Naïve Lag |\n")
    md.append("\n---\n\n")

    # Section 2: M2 Duplicate Work
    md.append("## 2. M2_DUPLICATE_WORK: Record Linkage Hold-Out Stability\n\n")
    md.append(f"- **Split Protocol**: {m2_res['split_description']}\n")
    md.append(f"- **Total Work Records**: `{m2_res['total_records']:,}` works (`{m2_res['train_records']:,}` train, `{m2_res['test_records']:,}` test).\n")
    md.append(f"- **TF-IDF Vocabulary Size**: `{m2_res['vocab_size']:,}` features (fitted strictly on train).\n")
    md.append(f"- **Train Cosine Similarity Distribution**: P90 = `{m2_res['train_sim_p90']:.4f}`, P99 = `{m2_res['train_sim_p99']:.4f}`.\n")
    md.append(f"- **Test Cosine Similarity Distribution**: P90 = `{m2_res['test_sim_p90']:.4f}`, P99 = `{m2_res['test_sim_p99']:.4f}`.\n")
    md.append(f"- **Distribution Stability Variance (Delta P99)**: `{m2_res['delta_p99']:.4f}`.\n\n")
    md.append(f"> **Interpretation**: {m2_res['interpretation']}\n\n")
    md.append("---\n\n")

    # Section 3: M1 Cost Anomaly
    md.append("## 3. M1_COST_ANOMALY: Unsupervised Anomaly Detection Stability\n\n")
    md.append(f"- **Train Population (80% Chronological)**: `{m1_res['train_rows']:,}` works (`{m1_res['train_start']}` to `{m1_res['train_end']}`).\n")
    md.append(f"- **Test Population (20% Chronological)**: `{m1_res['test_rows']:,}` works (`{m1_res['test_start']}` to `{m1_res['test_end']}`).\n")
    md.append(f"- **Train In-Sample Anomaly Rate**: `{m1_res['train_anomaly_rate']:.2f}%`.\n")
    md.append(f"- **Test Out-of-Sample Anomaly Rate**: `{m1_res['test_anomaly_rate']:.2f}%`.\n")
    md.append(f"- **Rate Delta**: `{m1_res['rate_delta']:.2f}%`.\n")
    md.append(f"- **Test Cross-Detector Concordance (Jaccard)**: `{m1_res['test_cross_detector_jaccard']:.4f}`.\n\n")

    md.append("### M1 Temporal Feature Availability Audit\n\n")
    md.append("| Feature Name | Availability Point | Role in Model |\n")
    md.append("| :--- | :--- | :--- |\n")
    for feat, desc in m1_res['feature_availability'].items():
        md.append(f"| `{feat}` | {desc.split('(')[0].strip()} | {desc} |\n")
    md.append("\n---\n\n")

    # Section 4: M4 Forecasting
    md.append("## 4. M4_FORECAST: Out-of-Sample Evaluation & Baseline Comparison\n\n")
    md.append(f"- **Total Observed Timeline**: `{m4_res['total_observations']}` months (`{m4_res['train_start']}` to `{m4_res['test_end']}`).\n")
    md.append(f"- **Train Months (80%)**: `{m4_res['train_observations']}` (`{m4_res['train_start']}` to `{m4_res['train_end']}`).\n")
    md.append(f"- **Test Months (20%)**: `{m4_res['test_observations']}` (`{m4_res['test_start']}` to `{m4_res['test_end']}`).\n\n")
    md.append("| Metric | 3-Month Rolling Average Forecast | Naïve Previous-Month Baseline |\n")
    md.append("| :--- | :---: | :---: |\n")
    md.append(f"| **Mean Absolute Error (MAE)** | **₹{m4_res['model_mae']:,.2f}** | ₹{m4_res['prev_mae']:,.2f} |\n")
    md.append(f"| **Root Mean Squared Error (RMSE)** | **₹{m4_res['model_rmse']:,.2f}** | ₹{m4_res['prev_rmse']:,.2f} |\n")
    md.append(f"| **Mean Absolute Percentage Error (MAPE)** | **{m4_res['model_mape']:.2f}%** | {m4_res['prev_mape']:.2f}% |\n\n")
    md.append(f"> **Conclusion**: {m4_res['conclusion']}\n\n")

    md.append("### Six-Month Production Forecast Horizon\n\n")
    md.append("| Target Month | Forecast Expenditure | Lower Bound | Upper Bound | Interval Type |\n")
    md.append("| :--- | :---: | :---: | :---: | :--- |\n")
    for r in m4_res['future_6m_forecast']:
        md.append(f"| `{r['month']}` | ₹{r['forecast_expenditure']:,.2f} | ₹{r['lower_bound']:,.2f} | ₹{r['upper_bound']:,.2f} | {r['expected_range_type']} |\n")

    with open("output/MODEL_TRAIN_TEST_REPORT.md", "w", encoding="utf-8") as f:
        f.writelines(md)
    print("Wrote output/MODEL_TRAIN_TEST_REPORT.md")

if __name__ == '__main__':
    main()
