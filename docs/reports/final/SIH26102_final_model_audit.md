# SIH26102 Final Model Audit Report
**SIH 2026 | Problem Statement: SIH26102**  
**AI-Powered MPLADS Audit Intelligence Platform — Team CodeBlooded**  

---

## 1. Production Model Inventory & Audit Matrix

| Model | Actual Problem Solved | Input Features | Output Signal | Architecture | Ground Truth Status | Valid Metric | Model Status |
|---|---|---|---|---|---|---|---|
| **M1** | Sanction Cost Outlier Detection | `sanctioned_amount`, `state`, `category` | Anomaly Flag & Score | Isolation Forest (`n_estimators=300`, `contamination=0.05`) | `NO GROUND TRUTH` | Test Anomaly Rate: **5.02%** | `PASS WITH LIMITATIONS` |
| **M2** | Duplicate Work Linkage | `work_description`, `state`, `district` | Candidate Pairs & Similarity | Candidate Blocking (`State + District + Category`) + TF-IDF Cosine Match ($>90\%$) | `NO GROUND TRUTH` | **5,000 Scored Pairs** (0 duplicate canonical pair keys) | `PASS WITH LIMITATIONS` |
| **M3** | Expenditure & Payment Behavioral Screening | `num_payments`, `total_spent`, `max_payment` | Structuring Signal | Transaction-grain Behavioral Threshold Screening | `NO GROUND TRUTH` | Structuring Screening Rate | `PASS WITH LIMITATIONS` |
| **M4** | Expenditure Forecasting | Historical Monthly Outlay (`STATE × MONTH`) | Projected Monthly Outlay (₹ Cr) | Recursive 3-Month Rolling Average | Historical Holdout | **MAE: ₹34,493,984.47** (+7.06% MAE improvement vs naïve) | `PASS` |
| **M5** | Multi-Signal Audit Prioritization | Risk Vector (Cost, Delay, Compliance, Vendor, Eligibility) | Priority Score $[0, 100]$ & Tier | Composite Weight Matrix ($\sum w_i = 1.00$) | `NO GROUND TRUTH` | **1,635 Critical Works** | `PASS WITH LIMITATIONS` |

---

## 2. Model Leakage Fencing Audit

- **Model M1**: Fenced to sanction-stage features only (`sanctioned_amount`, state/category peer medians). Post-sanction expenditure and disbursement dates are strictly excluded. Peer medians are fit **strictly on the chronological training partition**.
- **Model M2**: Candidate blocking is restricted within geographic `State + District` partitions. Canonical pair key sorting (`tuple(sorted([id1, id2]))`) guarantees zero duplicate pair key reporting.
- **Model M3**: Handles missing disbursement amounts distinctly from `0.0` spending.
- **Model M4**: Evaluated strictly on an 8-month chronological holdout set (2026-02 to 2026-09). Rolling averages contain zero future values.
- **Model M5**: Weights sum to `1.00`. Supporting-only invariant verified (secondary signals alone cannot trigger `CRITICAL`).

---

## 3. Production Code vs Validation Code Consistency

- **Validation Alignment**: Production model logic (`ml/models/`, `cost_detection/`, `data_pipeline/`) is invoked directly during pipeline execution.
- **Validation Script**: `tests/` execute actual production pipeline methods. Zero simplified dummy models are substituted during validation.
