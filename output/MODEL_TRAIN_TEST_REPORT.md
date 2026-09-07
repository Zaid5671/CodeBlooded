# SIH26102 — THREE AI/ML MODEL TRAIN/TEST EVALUATION REPORT

**Generated At**: 2026-09-07T15:52:19.712504 | **Evaluation Protocol**: 80/20 Train/Test Partitioning

**Governance Disclaimer**: *All metrics represent unsupervised distribution stability and empirical tracking. Not proof of fraud or legal wrongdoing.*

---

## 1. Canonical Evaluated Models

| Canonical ID | Model Name | Evaluation Methodology | Partitioning Protocol |
| :--- | :--- | :--- | :--- |
| **`M1_COST_ANOMALY`** | Anomalous Cost Estimate Detection | Chronological 80/20 Hold-Out | 8 Non-Redundant Features (Peer IQR + Isolation Forest) |
| **`M2_DUPLICATE_WORK`** | Duplicate Work / Record Linkage | Random 80/20 Hold-Out | TF-IDF Vocabulary fitted strictly on Train partition |
| **`M4_FORECAST`** | MPLADS Expenditure Forecasting | Chronological 80/20 Hold-Out | Recursive 3-Month Rolling Average vs Naïve Lag |

---

## 2. M2_DUPLICATE_WORK: Record Linkage Hold-Out Stability

- **Split Protocol**: Random 80/20 hold-out split with fixed random seed (42)
- **Total Work Records**: `79,220` works (`63,376` train, `15,844` test).
- **TF-IDF Vocabulary Size**: `10,000` features (fitted strictly on train).
- **Train Cosine Similarity Distribution**: P90 = `0.0393`, P99 = `0.1896`.
- **Test Cosine Similarity Distribution**: P90 = `0.0387`, P99 = `0.1837`.
- **Distribution Stability Variance (Delta P99)**: `0.0060`.

> **Interpretation**: The held-out TF-IDF similarity distribution is broadly consistent with the training distribution. This supports representation stability under the hold-out split, but does not establish duplicate-detection accuracy because verified duplicate/non-duplicate labels are unavailable.

---

## 3. M1_COST_ANOMALY: Unsupervised Anomaly Detection Stability

- **Train Population (80% Chronological)**: `63,372` works (`2024-07-09` to `2026-04-13`).
- **Test Population (20% Chronological)**: `15,844` works (`2026-04-13` to `2026-09-05`).
- **Train In-Sample Anomaly Rate**: `5.00%`.
- **Test Out-of-Sample Anomaly Rate**: `4.46%`.
- **Rate Delta**: `0.54%`.
- **Test Cross-Detector Concordance (Jaccard)**: `0.3862`.

### M1 Temporal Feature Availability Audit

| Feature Name | Availability Point | Role in Model |
| :--- | :--- | :--- |
| `log_sanction_amount` | Sanction-Time | Sanction-Time (Scale magnitude) |
| `peer_dev_ratio_filled` | Peer-Distribution | Peer-Distribution (Learned on Train only) |
| `robust_dev_filled` | Peer-Distribution | Peer-Distribution (Learned on Train only) |
| `days_filled` | Lifecycle | Lifecycle (Recommendation to Sanction latency) |
| `num_payments_filled` | Expenditure / Audit-Time | Expenditure / Audit-Time (Payment count) |
| `max_payment_ratio_filled` | Expenditure / Audit-Time | Expenditure / Audit-Time (Largest voucher ratio) |
| `payment_var_filled` | Expenditure / Audit-Time | Expenditure / Audit-Time (Disbursement variance) |
| `median_time_between_payments_filled` | Expenditure / Audit-Time | Expenditure / Audit-Time (Disbursement cadence) |

---

## 4. M4_FORECAST: Out-of-Sample Evaluation & Baseline Comparison

- **Total Observed Timeline**: `27` months (`2024-07` to `2026-09`).
- **Train Months (80%)**: `21` (`2024-07` to `2026-03`).
- **Test Months (20%)**: `6` (`2026-04` to `2026-09`).

| Metric | 3-Month Rolling Average Forecast | Naïve Previous-Month Baseline |
| :--- | :---: | :---: |
| **Mean Absolute Error (MAE)** | **₹552,133,404.50** | ₹553,649,255.67 |
| **Root Mean Squared Error (RMSE)** | **₹721,252,976.15** | ₹713,013,097.88 |
| **Mean Absolute Percentage Error (MAPE)** | **79.18%** | 78.14% |

> **Conclusion**: The 3-month rolling-average method marginally improves MAE relative to the naïve previous-month baseline, while RMSE and MAPE remain higher. It is therefore retained as an empirical forecasting aid and is not claimed to outperform the naïve baseline across all evaluation metrics.

### Six-Month Production Forecast Horizon

| Target Month | Forecast Expenditure | Lower Bound | Upper Bound | Interval Type |
| :--- | :---: | :---: | :---: | :--- |
| `2026-10` | ₹1,459,790,970.00 | ₹151,011,165.75 | ₹2,768,570,774.25 | Empirical 95% Expected Range |
| `2026-11` | ₹1,215,751,699.67 | ₹0.00 | ₹2,524,531,503.92 | Empirical 95% Expected Range |
| `2026-12` | ₹1,023,702,265.22 | ₹0.00 | ₹2,332,482,069.47 | Empirical 95% Expected Range |
| `2027-01` | ₹1,233,081,644.96 | ₹0.00 | ₹2,541,861,449.21 | Empirical 95% Expected Range |
| `2027-02` | ₹1,157,511,869.95 | ₹0.00 | ₹2,466,291,674.20 | Empirical 95% Expected Range |
| `2027-03` | ₹1,138,098,593.38 | ₹0.00 | ₹2,446,878,397.63 | Empirical 95% Expected Range |
