# 3-MODEL RIGOROUS 80/20 TRAIN/TEST EVALUATION REPORT
**Generated At**: 2026-09-07T15:19:32.032639 | **Methodology Freeze**: SIH26102 Production Integrity

## 1. Executive Summary: Leak-Free 80/20 Train/Test Splits

| Model | Split Type | Train Set | Test Set | Train Temporal Range | Test Temporal Range | Primary Evaluation Metrics |
|---|---|---:|---:|---|---|---|
| **Model 1: Record Linkage** | Random 80/20 hold-out split with fixed random seed (42) | 63,376 works | 15,844 works | Full LS18 Active Term | Full LS18 Active Term | Vocab: 10,000 | Delta P99 Sim: 0.006 |
| **Model 2: Cost Anomaly** | Chronological 80/20 Split | 63,372 works | 15,844 works | 2024-07-09 to 2026-04-13 | 2026-04-13 to 2026-09-05 | Train Rate: 5.0% | Test Rate: 4.46% | Concordance: 0.3862 |
| **Model 3: Forecasting** | Chronological 80/20 Time-Series | 21 months | 6 months | 2024-07 to 2026-03 | 2026-04 to 2026-09 | MAE: ₹552,133,404.50 | RMSE: ₹721,252,976.15 | MAPE: 79.18% |

---

## 2. Data Leakage Audit

A comprehensive source-code audit across the repository confirms strict isolation between training and testing data:
- **Model 1 (TF-IDF Vectorizer)**: `TfidfVectorizer` is fitted strictly on the 80% training slice (`train_df`). The held-out test partition (`test_df`) is transformed using the fitted vocabulary without updating or refitting the vocabulary.
- **Model 2 (Imputation, Peer Statistics, Isolation Forest)**: `SimpleImputer`, hierarchical State-Category Tukey IQR/MAD baselines, and `IsolationForest(n_estimators=300, random_state=42)` are fitted solely on the chronological 80% train split (`train_raw`). The out-of-sample 20% test split (`test_raw`) is evaluated against these frozen baselines without incorporating any test distributions.
- **Model 3 (Time-Series Baseline)**: The 3-month rolling baseline is calibrated strictly on historical training months (`2024-07` to `2026-03`). Predictions for held-out test months (`2026-04` to `2026-09`) are generated sequentially forward without exposing future actuals to the estimator prior to evaluation.
- **Production Pipeline Execution**: Full-data production fits occur independently after evaluation reporting is complete to maximize operational coverage.


---

## 3. Model 1: Record Linkage / Potential Duplicate Work Detection

- **Split Methodology**: Random 80/20 hold-out split with fixed random seed (42).
- **Training Partition**: 63,376 sanctioned works.
- **Held-Out Test Partition**: 15,844 sanctioned works.
- **Learned Vocabulary Size**: 10,000 n-gram features fitted strictly on training text.
- **In-Sample Train Similarity Distribution**: Mean = `0.0393` (P90), `0.1896` (P99).
- **Held-Out Test Similarity Distribution**: Mean = `0.0387` (P90), `0.1837` (P99).
- **Distribution Stability Variance ($\Delta$ P99)**: `0.0060`.
- **Evaluation Interpretation**: The held-out TF-IDF similarity distribution is broadly consistent with the training distribution. This supports representation stability under the hold-out split, but does not establish duplicate-detection accuracy because verified duplicate/non-duplicate labels are unavailable.


---

## 4. Model 2: Unsupervised Cost Anomaly Detection

- **Evaluation Nature**: Chronological out-of-sample stability evaluation of an audit-time unsupervised anomaly detector.
- **Chronological Training Partition**: 63,372 works (`2024-07-09` to `2026-04-13`).
- **Chronological Test Partition**: 15,844 works (`2026-04-13` to `2026-09-05`).
- **Model Parameters**: Isolation Forest (`n_estimators=300`, `contamination=0.05`, `random_state=42`).
- **In-Sample Train Anomaly Rate**: `5.0%`.
- **Out-of-Sample Test Anomaly Rate**: `4.46%`.
- **Anomaly Rate Stability Delta**: `0.54%`.
- **Out-of-Sample Cross-Detector Concordance (Jaccard)**: `0.3862`.
- **Methodological Note**: Because verified audit outcome labels are unavailable, these metrics evaluate out-of-sample stability and agreement between independent unsupervised detectors rather than classification accuracy.


---

## 5. Model 2 Temporal Feature Availability Audit

The 8 non-redundant numerical features utilized by Model 2 are explicitly categorized by their point of availability in the administrative lifecycle:


| # | Feature Name | Administrative Availability Point | Functional Description |
|---|---|---|---|
| 1 | `log_sanction_amount` | **Sanction-Time** | Log-scale monetary sanction magnitude |
| 2 | `peer_dev_ratio_filled` | **Peer-Distribution (Train Baselines)** | Deviation ratio relative to category-state peer median |
| 3 | `robust_dev_filled` | **Peer-Distribution (Train Baselines)** | Tukey IQR / MAD robust normalized cost deviation |
| 4 | `days_filled` | **Lifecycle (Recommendation to Sanction)** | Duration in calendar days between recommendation and sanction |
| 5 | `num_payments_filled` | **Expenditure / Audit-Time** | Number of disbursement voucher installments recorded |
| 6 | `max_payment_ratio_filled` | **Expenditure / Audit-Time** | Fraction of total expenditure disbursed in single largest voucher |
| 7 | `payment_var_filled` | **Expenditure / Audit-Time** | Variance across installment payment voucher amounts |
| 8 | `median_time_between_payments_filled` | **Expenditure / Audit-Time** | Median calendar days between successive payment disbursements |

*Audit Finding*: Model 2 is an **audit-time anomaly detector** evaluated on historical records post-expenditure, rather than a pre-sanction forecasting model.


---

## 6. Model 3: Expenditure Forecasting Evaluation

- **Methodology**: 3-month rolling-average expenditure forecasting baseline.
- **Evaluation Dataset**: `data/original/LokSabha18/Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv (27 monthly aggregated observations)`.
- **Historical Context Dataset**: `data/original/LokSabha17/Expenditure on Completed and On-going Works as on Date_LokSabha17.csv (historical term reference)`.
- **Training Partition**: 21 monthly observations (`2024-07` to `2026-03`).
- **Testing Partition**: 6 monthly observations (`2026-04` to `2026-09`).


---

## 7. Baseline Comparison & Metric Evaluation

| Forecasting Method | Out-of-Sample MAE | Out-of-Sample RMSE | Out-of-Sample MAPE | Comparison to Naïve Baseline |
|---|---:|---:|---:|---|
| **3-Month Rolling Average (Proposed)** | **₹552,133,404.50** | ₹721,252,976.15 | 79.18% | **Marginally Lower MAE** ($-₹1,515,851.17$) |
| **Naïve Previous-Month Baseline** | ₹553,649,255.67 | **₹713,013,097.88** | **78.14%** | Baseline Reference |

**Performance Conclusion**: The 3-month rolling-average method marginally improves MAE relative to the naïve previous-month baseline, while RMSE and MAPE remain higher. It is therefore retained as an empirical forecasting aid and is not claimed to outperform the naïve baseline across all evaluation metrics.


---

## 8. Six-Month Production Forecast (Full Historical Baseline)

Empirical six-month projection generated from full 27-month historical baseline with recent trend momentum:


| Target Month | Forecasted Expenditure | Lower Bound | Upper Bound | Interval Terminology |
|---|---:|---:|---:|---|
| `2026-10` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2026-11` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2026-12` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-01` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-02` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-03` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |

---

## 9. Genuine Methodological & Administrative Limitations

1. **Absence of Ground-Truth Administrative Adjudication Labels**: Public government datasets do not contain validated fraud or duplicate outcome labels; metrics reflect statistical stability and multi-detector concordance rather than supervised classification accuracy.
2. **Cross-House Entity Linkage**: Rajya Sabha sitting member records lack direct Lok Sabha constituency keys; cross-house analysis requires text/location record linkage and remains under `CROSS_HOUSE_ENABLED = False` pending verified house mapping.
3. **Short Monthly Time Series**: 27 monthly observations limit high-order econometric models; empirical rolling baseline provides operational bounding without over-parameterization.
4. **Administrative Payment Grouping**: When voucher transactions lack unique voucher numbers, clustering relies on `(Work ID, Vendor, Amount, Date)` composites.


---

## 10. Reproducibility & Execution Command

To reproduce this exact 80/20 train/test evaluation run:
```bash
PYTHONPATH=. python3 scripts/train_test_3_models.py
```
