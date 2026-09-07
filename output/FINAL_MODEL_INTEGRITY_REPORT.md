# SIH26102 — FINAL MODEL INTEGRITY & RECONCILIATION REPORT
**Generated At**: 2026-09-07T15:21:22.964009 | **Status**: PRODUCTION INTEGRITY FROZEN

## A. Dataset Inventory

- **Total Files Scanned**: 23 CSV files under `data/original/`
- **Total Administrative Records**: 863,032 rows across 3 legislative partitions:
  - **17th Lok Sabha (2019–2024)**: 397,241 records (5 files)
  - **18th Lok Sabha (2024–Present)**: 305,413 records (6 files)
  - **Rajya Sabha Sitting Members**: 80,220 records (6 files)

## B. Join Integrity & Primary Key Isolation

- **Internal Lifecycle Joins (LS18)**: Primary key `Work` achieves 100.0% match with `Works Recommended`, 75.51% match with `Expenditure` (aggregated to 56,604 unique work entities), and 43.47% with `Works Completed`.
- **Cross-Term Isolation (LS18 ⟕ LS17)**: 0 primary key collisions across terms (disjoint identifier spaces).
- **Cross-House Isolation (LS18 ⟕ RS Sitting)**: 0 primary key collisions. Ingested RS Sitting data is isolated under `CROSS_HOUSE_ENABLED = False` pending verified MP cross-house linkage.

## C. Model 1: Record Linkage / Duplicate Work Detection Evaluation

- **Split**: Random 80/20 hold-out split with fixed random seed (42).
- **Train Records**: 63,376 works | **Test Records**: 15,844 works.
- **TF-IDF Vocabulary**: 10,000 features fitted strictly on training partition.
- **Train Cosine Similarity P99**: `0.1896` | **Test Cosine Similarity P99**: `0.1837` | **Delta**: `0.0059`.
- **Evaluation Interpretation**: The held-out TF-IDF similarity distribution is broadly consistent with the training distribution. This supports representation stability under the hold-out split, but does not establish duplicate-detection accuracy because verified duplicate/non-duplicate labels are unavailable.

## D. Model 2: Unsupervised Cost Anomaly Detection Evaluation

- **Split**: Chronological 80/20 split based on sanction/recommendation dates.
- **Train Partition**: 63,372 works (2024-07-09 to 2026-04-13).
- **Test Partition**: 15,844 works (2026-04-13 to 2026-09-05).
- **Features**: 8 non-redundant numerical features.
- **Train In-Sample Anomaly Rate**: `5.00%` | **Test Out-of-Sample Anomaly Rate**: `4.46%` | **Delta**: `0.54%`.
- **Out-of-Sample Cross-Detector Concordance (Jaccard)**: `0.3862`.

## E. Model 2 Temporal Feature Availability Audit

| Feature | Availability Point | Role in Audit Intelligence |
|---|---|---|
| `log_sanction_amount` | Sanction-Time | Scale baseline magnitude |
| `peer_dev_ratio_filled` | Peer-Distribution (Train Only) | State-Category peer ratio |
| `robust_dev_filled` | Peer-Distribution (Train Only) | Tukey IQR / MAD normalized deviation |
| `days_filled` | Lifecycle (Rec to Sanc) | Administrative sanction latency |
| `num_payments_filled` | Expenditure / Audit-Time | Payment installment volume |
| `max_payment_ratio_filled` | Expenditure / Audit-Time | Lump-sum concentration ratio |
| `payment_var_filled` | Expenditure / Audit-Time | Installment amount variance |
| `median_time_between_payments_filled` | Expenditure / Audit-Time | Disbursement interval cadence |

*Audit Classification*: Model 2 operates as an **audit-time unsupervised anomaly detector** over financial records post-expenditure.

## F & G. Model 3: Forecasting Evaluation & Baseline Comparison

- **Methodology**: 3-month rolling-average expenditure forecasting baseline.
- **Training Observations**: 21 months (2024-07 to 2026-03) | **Test Observations**: 6 months (2026-04 to 2026-09).
- **Out-of-Sample Error Metrics**:
  - **Model MAE**: ₹552,133,404.50 (vs Naïve Prev-Month: ₹553,649,255.67)
  - **Model RMSE**: ₹721,252,976.15 (vs Naïve Prev-Month: ₹713,013,097.88)
  - **Model MAPE**: 79.18% (vs Naïve Prev-Month: 78.14%)
- **Performance Conclusion**: The 3-month rolling-average method marginally improves MAE relative to the naïve previous-month baseline, while RMSE and MAPE remain higher. It is therefore retained as an empirical forecasting aid and is not claimed to outperform the naïve baseline across all evaluation metrics.

## H. Six-Month Production Forecast Horizon

| Target Month | Forecast Expenditure | Lower Bound | Upper Bound | Interval Type |
|---|---:|---:|---:|---|
| `2026-10` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2026-11` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2026-12` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-01` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-02` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |
| `2027-03` | ₹1,337,916,700.78 | ₹29,136,896.53 | ₹2,646,696,505.03 | Empirical 95% Expected Range |

## I. Model 4: Statutory 45-Day Compliance Results

- **Compliant ($\le$ 45 days)**: 23,337 works
- **Minor Deviation (46–90 days)**: 20,937 works
- **Moderate Deviation (91–180 days)**: 21,611 works
- **Severe Deviation (> 180 days)**: 13,334 works
- **Implementing Agency Watchlist**: 609 agencies

## J. Vendor & Agency Risk Analytics

- **High Concentration Agencies (HHI > 0.25)**: 67 agencies
- **Small-Value Payment Fragmentation Candidates**: 651 works
- **Whitelisted Government Entities**: 34 entities

## K. Module 6: Potential Duplicate Expenditure Results

- **Exact Duplicate Vouchers**: 435 vouchers
- **Near-Repeat Payment Patterns**: 700 patterns

## L. Module 7: Fund Utilization & Velocity Results

- **Status**: Implemented & active across 544 MP allocations and 79,220 sanctioned works.
- **Disbursement Velocity Tracking**: Active.

## M, N & O. Model 5: Audit Priority Aggregator Verification

- **Dimension Weights ($\sum = 1.00$)**:
  - Cost Risk = `0.30` (Major)
  - Speed & Delay = `0.25` (Major)
  - Statutory Compliance = `0.25` (Major)
  - Vendor & Payment = `0.10` (Supporting)
  - Eligibility & Beneficiary = `0.10` (Supporting)
- **Score Range**: [0.0000, 0.9000] $\subseteq [0.00, 1.00]$
- **Master Audit Priority Tier Distribution (79,220 Sanctioned Works)**:
  - **CRITICAL AUDIT PRIORITY**: **1,635 works**
  - **STANDARD REVIEW**: **58,182 works**
  - **LOW PRIORITY**: **19,403 works**
- **Supporting-Only Critical Escalations**: **0 works** (Invariant preserved).

## P. Test Suite Verification Result

- **Automated Test Results**: **112 / 112 PASSED (100%)** (`PYTHONPATH=. pytest tests/ -v`).

## Q. Leakage Audit Confirmation

- All vectorizers, imputers, peer distribution fences, and Isolation Forest models are calibrated solely on training splits before evaluating held-out sets.

## R. Genuine Remaining Limitations

1. Public administrative data does not contain verified ground-truth fraud adjudication labels; predictions represent anomaly indicators for human audit review.
2. Cross-house candidate evaluation between Lok Sabha and Rajya Sabha remains under `CROSS_HOUSE_ENABLED = False` until MP cross-house linkage is verified.
3. Monthly time series (27 observations) limits formal seasonal decomposition.

## S. Git Verification & Push Status

- **Remote**: `https://github.com/Zaid5671/CodeBlooded.git` on branch `main`.
