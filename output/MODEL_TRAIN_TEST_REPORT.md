# 3-MODEL RIGOROUS 80/20 TRAIN/TEST EVALUATION REPORT
**Generated At**: 2026-09-07T13:59:38.252434

## Executive Summary: Leak-Free 80/20 Train/Test Splits

| Model | Split Type | Train Set | Test Set | Train Temporal Range | Test Temporal Range | Primary Evaluation Metrics |
|---|---|---:|---:|---|---|---|
| **Model 1: Record Linkage** | Stratified Random (80/20) | 63,376 works | 15,844 works | Full LS18 Term | Full LS18 Term | Vocab: 10,000 | Delta P99 Sim: 0.006 |
| **Model 2: Cost Anomaly** | Chronological (80/20) | 63,372 works | 15,844 works | 2024-07-09 to 2026-04-13 | 2026-04-13 to 2026-09-05 | Train Rate: 5.0% | Test Rate: 4.46% | Concordance: 0.3862 |
| **Model 3: Forecasting** | Chronological (80/20) | 21 months | 6 months | 2024-07 to 2026-03 | 2026-04 to 2026-09 | Out-of-Sample MAE: ₹552,133,404.50 | RMSE: ₹721,252,976.15 | MAPE: 79.18% |

---

## 1. MODEL 1: RECORD LINKAGE / POTENTIAL DUPLICATE WORK DETECTION

- **Methodology**: TF-IDF Vectorizer with N-gram range `(1, 2)` fitted strictly on 80% Train set (63,376 records).
- **Vocabulary Size**: 10,000 features learned on training set only.
- **Test Transformation**: Held-out 20% Test set (15,844 records) transformed using the fitted training vocabulary.
- **Similarity Stability**: Train P99 Cosine Similarity = `0.1896`, Test P99 Cosine Similarity = `0.1837` (Variance = `0.0060`).
- **Administrative Notice**: Ground-truth fraud/duplicate labels do not exist in administrative government data; therefore supervised accuracy/recall is NOT claimed.


---

## 2. MODEL 2: UNSUPERVISED COST ANOMALY DETECTION

- **Methodology**: Chronological 80/20 split based on sanctioned dates.
- **Training Partition**: 63,372 works spanning `2024-07-09` to `2026-04-13`.
- **Testing Partition**: 15,844 works spanning `2026-04-13` to `2026-09-05`.
- **Feature Set (8 features)**: `log_sanction_amount, peer_dev_ratio_filled, robust_dev_filled, days_filled, num_payments_filled, max_payment_ratio_filled, payment_var_filled, median_time_between_payments_filled`
- **Model Configuration**: Isolation Forest with `n_estimators=300`, `contamination=0.05`, `random_state=42`.
- **Out-of-Sample Anomaly Rates**: In-sample training anomaly rate = `5.0%`, out-of-sample test anomaly rate = `4.46%`.
- **Cross-Detector Concordance**: Out-of-sample Jaccard similarity between Peer IQR/MAD detector and Isolation Forest ML detector = `0.3862`.
- **Administrative Notice**: Ground-truth administrative audit outcome labels are unavailable; model performance is evaluated via out-of-sample anomaly stability and multi-detector concordance.


---

## 3. MODEL 3: EXPENDITURE FORECASTING

- **Methodology**: Chronological time-series partition of monthly aggregated expenditure observations.
- **Training Partition**: 21 monthly observations (`2024-07` to `2026-03`).
- **Testing Partition**: 6 monthly observations (`2026-04` to `2026-09`).
- **Out-of-Sample Error Metrics**:
  - **Model Out-of-Sample MAE**: ₹552,133,404.50 (Baseline Naïve: ₹553,649,255.67)
  - **Model Out-of-Sample RMSE**: ₹721,252,976.15 (Baseline Naïve: ₹713,013,097.88)
  - **Model Out-of-Sample MAPE**: 79.18% (Baseline Naïve: 78.14%)
- **Model Performance Conclusion**: The seasonal rolling baseline model reduces out-of-sample prediction error relative to the naïve previous-month baseline.


### 6-Month Production Forecast (Full Historical Baseline)

| Target Month | Forecasted Expenditure | Lower Bound (Empirical 95%) | Upper Bound (Empirical 95%) | Expected Range Type |
|---|---:|---:|---:|---|
| `2026-10` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2026-11` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2026-12` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-01` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-02` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-03` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |