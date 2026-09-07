# PHASE 4 — MODEL EVALUATION REPORT
**SIH 2026 | SIH26102 MPLADS Audit Intelligence Platform**

---

## 1. M1 — ANOMALOUS COST ESTIMATE DETECTION MODEL
- **Objective**: Identify unusual sanctioned/estimated costs relative to comparable peer works using sanction-time data only.
- **Predictive Leakage Fencing**: Zero expenditure, zero payment, and zero post-sanction fields are used in M1 predictive inputs.
- **Model Architecture**: Peer-Group Robust Statistics (IQR / Tukey Upper Fence) + Isolation Forest Anomaly Screening.
- **Peer Hierarchy**: `[State + Category] -> [National + Category]`.
- **Evaluation Standard**: Unsupervised diagnostic scoring; no ground-truth fraud accuracy claims.

## 2. M2 — DUPLICATE WORK DETECTION MODEL
- **Pipeline Architecture**: `Sanctioned Works -> Candidate Blocking (State + District + Category) -> Pairwise TF-IDF + Cosine Similarity -> Potential Duplicate Candidate Pairs`.
- **Candidate Blocking Results**:
  - Total Pairs Analyzed: 5,000
  - Self-pairs: 0
  - Bidirectional duplicate pairs: 0
  - Canonical Pair Ordering Enforced: `pair_key = tuple(sorted([work_id_1, work_id_2]))`
- **Governance Classification**: Strictly classified as `POTENTIAL DUPLICATE`.

## 3. M3 — EXPENDITURE & FUND UTILIZATION ANOMALY MODEL
- **Input Grain**: Transaction-level expenditure aggregated to work-level behavioral features.
- **Key Behavioral Metrics**: Payment count, utilization ratio, payment timing velocity, vendor diversity.
- **Payment Structuring Heuristic**:
  - `num_payments >= 5`
  - `total_spent > ₹500,000`
  - `max_payment < ₹200,000`
  - *Analytical screening parameter, NOT statutory limit.*

## 4. M4 — EXPENDITURE FORECASTING MODEL
- **Primary Aggregation Grain**: `STATE × CALENDAR MONTH`.
- **Forecast Horizon**: 6 Months.
- **Metrics vs Naïve Baseline**:
  - MAE, RMSE, MAPE evaluated chronologically across monthly time-series projections.
  - Empirical 95% Expected Range computed as $[\mu - 2\sigma, \mu + 2\sigma]$.
- **Data Boundary Handling**: Genuine zero-spend months preserved; zero missing observations converted into fake zeroes.

---
**Status**: `PHASE 4 EVALUATION COMPLETE`
