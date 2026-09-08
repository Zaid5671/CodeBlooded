# SIH26102 Final Validation & Verification Report
**SIH 2026 | Problem Statement: SIH26102**  
**AI-Powered MPLADS Audit Intelligence Platform — Team CodeBlooded**  

---

## 1. Ground Truth & Accuracy Declaration

> [!WARNING]
> **Supervised Classification Accuracy Status**: `NOT ESTIMABLE — NO INDEPENDENT GROUND-TRUTH LABELS`
> Ground truth fraud outcome labels do not exist in public government datasets. Supervised accuracy, precision, recall, F1, and ROC-AUC metrics are **not estimable**. All models function as **unsupervised decision support and audit prioritization signals**. Zero synthetic fraud labels are fabricated.

---

## 2. Valid Empirical Performance Metrics

- **Model M1 (Isolation Forest Cost Outlier)**:
  - Train Anomaly Rate: **4.95%**
  - Test Anomaly Rate: **5.02%** (Target: 5.00% contamination operating point)
  - Diagnostic: Successfully isolates high multi-dimensional peer deviations without post-sanction data leakage.

- **Model M2 (Duplicate Work Linkage)**:
  - Geographic Candidate Blocks: **1,262 Blocks** (`State + District + Work Category`)
  - Retained Scored Candidate Pairs: **5,000 Scored Pairs** ($>90\%$ cosine similarity threshold)
  - Self-pairs ($A == B$): **0**
  - Duplicate Canonical Pair Keys: **0**

- **Model M3 — Expenditure & Payment Behavioral Screening**:
  - Architecture: Heuristic & rule-based transaction-grain behavioral screening (`num_payments >= 5`, `total_spent > ₹500k`, `max_payment < ₹200k`).
  - Structuring Screening: Flags payment velocity and disbursement patterns requiring audit review.

- **Model M4 (Expenditure Forecasting)**:
  - **Production Horizon**: 6 Months (`FORECAST_HORIZON_MONTHS = 6`)
  - **Evaluation Design**: Recursive multi-step forecast evaluation over the 8-month held-out period (19 train months: `2024-07` to `2026-01`; 8 test months: `2026-02` to `2026-09`)
  - **MAE**: **₹34,493,984.47 (₹3.45 Cr)**
  - **RMSE**: **₹63,253,503.79 (₹6.33 Cr)**
  - **WAPE**: **470.32%** (State-month panel; WAPE expands in state-month cells where actual expenditure is small or zero relative to prediction error) / **31.15%** (National aggregate)
  - **sMAPE**: **54.21%**
  - **Naïve Baseline MAE**: ₹37,114,452.69 (₹3.71 Cr)
  - **MAE improvement vs naïve baseline**: **+7.06%** over holdout evaluation.

- **Model M5 (Unified Audit Priority Scoring)**:
  - Composite Triage Distribution: **1,635 Critical Works** ($>75$), 58,176 Standard Works, 19,409 Low Priority Works.

---

## 3. Pipeline Reproducibility Verification

- **Random Seed Lock**: `random_state=42` locked across Isolation Forest & TF-IDF pipelines.
- **Iteration Comparison**: 2 independent pipeline runs generated **100% identical outputs** across all JSON/CSV output files.
- **Reproducibility Status**: **PASS**

---

## 4. Software Test Suite & API Verification

- **Total Automated Unit & Integration Tests**: 136
- **Test Pass Rate**: **136 / 136 (100% Pass Rate)**
- **Bytecode Compilation**: 100% Clean (`python3 -m compileall .` passed)
- **API Availability**: **PASS** (28/28 endpoints returning `HTTP 200 OK` across all 4 datasets)
- **API Data Reconciliation**: **PASS** (28/28 endpoints numerically reconciled with canonical data)

---

## 5. Final Release Gate Decision

**FINAL RELEASE STATUS**: `RELEASE READY WITH MODEL-EVALUATION LIMITATIONS`

### Justification:
1. Software pipeline and backend API engine are 100% deterministic and error-free.
2. All 136 automated unit and integration tests pass cleanly.
3. Recursive multi-step forecast evaluation confirms M4 expenditure forecasting achieves a **+7.06% MAE improvement vs naïve baseline**.
4. Predictive leakage fencing guarantees sanction-stage models rely strictly on sanction-time data.
5. All limitations regarding the absence of ground-truth fraud outcome labels in public government data are transparently disclosed.
