# PHASE 4 — MODEL EVALUATION REPORT
**SIH 2026 | SIH26102 MPLADS Audit Intelligence Platform**
**Run Timestamp**: 2026-09-07 16:57:12

---

## 1. M1 — ANOMALOUS COST ESTIMATE DETECTION MODEL
- **Architecture**: Peer-Group Robust Statistics (IQR / MAD) + Isolation Forest Anomaly Screening.
- **Predictive Leakage Fencing**: Zero post-sanction expenditure or payment fields used in sanction-stage predictions.

## 2. M2 — DUPLICATE WORK DETECTION MODEL
- **Architecture**: State + District + Category Candidate Blocking -> TF-IDF Pairwise Cosine Similarity.
- **Candidate Pairs Scored**: 5,000 candidate pairs retained.
- **Classification**: `POTENTIAL DUPLICATE`.

## 3. M3 — EXPENDITURE & FUND UTILIZATION ANOMALY MODEL
- **Input Grain**: Transaction-level expenditure aggregated to work-level features.
- **Analytical Structuring Heuristic**: `num_payments >= 5`, `total_spent > 500,000`, `max_payment < 200,000` (Analytical screening parameter).

## 4. M4 — EXPENDITURE FORECASTING MODEL
- **Aggregation**: `STATE × CALENDAR MONTH`.
- **Horizon**: 6-Month Projection.
- **Interval Designation**: `Empirical 95% Expected Range` ($[\mu - 2\sigma, \mu + 2\sigma]$).

---
