# SIH26102 Architecture Reconciliation Report

**Project**: AI-Powered MPLADS Audit Intelligence Platform  
**Team**: CodeBlooded  
**Problem Statement ID**: SIH26102  
**Organization**: Ministry of Statistics and Programme Implementation (MoSPI)  
**Department**: Data Informatics & Innovation Division (DIID)  

---

## 1. Executive Finding

> [!CAUTION]
> **RECONCILIATION FINDING**: The earlier generated file `docs/ps26102_complete_implementation_audit.md` had contained inconsistencies with the canonical source code of the repository. It has now been completely reconciled against the verified production codebase.

### Summary of Architectural Truth vs. Historical Misconceptions
- **M1 (Cost Anomaly)**: Actual source is `IsolationForest(n_estimators=300, contamination=0.05)` on 8 non-redundant features with peer-relative robust deviation logic.
- **M2 (Duplicate Work Detection)**: Actual source is Geographic Candidate Blocking + TF-IDF Vectorizer + Cosine Similarity yielding 5,000 candidates (1,997 High Risk, 2,499 Medium Risk, 504 Low Risk).
- **M3 (Expenditure / Payment Anomaly)**: Actual source is transaction-grain voucher aggregation & payment structuring/fragmentation detector.
- **M4 (Expenditure Forecasting)**: Actual source is Recursive 3-Month Rolling Average Baseline (multi-step 6-month horizon). Zero XGBoost dependencies.
- **M5 (Audit Priority Aggregator)**: Actual source is Deterministic Weighted Multi-Signal Aggregator (Cost 0.30, Delay 0.25, Compliance 0.25, Vendor 0.10, Eligibility 0.10).

---

## 2. Canonical M1–M5 Verification Matrix

| Model ID | Expected Canonical Identity | Actual Source Implementation File | Status | Verification Evidence |
|---|---|---|---|---|
| **M1** | Cost / Expenditure Anomaly (Isolation Forest, $n\_estimators=300, contamination=0.05$) | `ml/model_1_cost_anomaly/isolation_forest.py`, `ml/config.py` | **VERIFIED** | `IF_N_ESTIMATORS = 300`, `IF_CONTAMINATION = 0.05`. 8 features used. Unsupervised. |
| **M2** | Duplicate Work Detection (Geographic Blocking + TF-IDF + Cosine Similarity) | `ml/model_2_duplicate_work/double_dipping.py` | **VERIFIED** | `TF-IDF Cosine Vectorizer` with candidate blocking generating 5,000 candidate pairs. |
| **M3** | Payment / Expenditure Anomaly (Transaction grain structuring & fragmentation) | `ml/model_3_expenditure_anomaly/duplicate_expenditure.py` | **VERIFIED** | Transaction-level voucher analysis for small-value payment fragmentation patterns. |
| **M4** | Expenditure Forecasting (Recursive 3-Month Rolling Average, 6-Month Horizon) | `ml/model_4_forecasting/expenditure_forecast.py` | **VERIFIED** | `recursive_rolling_mean_forecast` (window=3, horizon=6). Zero XGBoost dependencies. |
| **M5** | Multi-Signal Audit Priority Aggregator (Deterministic Weights: Cost 0.30, Delay 0.25, Compliance 0.25, Vendor 0.10, Eligibility 0.10) | `ml/model_5_audit_priority/misuse_priority.py` | **VERIFIED** | Multi-factor weighted evidence aggregator summing to 1.00 max weight. Assigns Critical / Standard / Low priority tiers. |

---

## 3. Supervised Learning Audit

A comprehensive scan across the entire production codebase (`ml/`, `backend/`, `frontend/`, `tests/`) for supervised estimators (`RandomForest`, `DecisionTree`, `GradientBoosting`, `XGBoost`, `CatBoost`, `LogisticRegression`, `SVC`, `KNeighbors`) yielded the following empirical findings:

| File Search Path | Estimator | Target | Label Source | Production Impact | Status |
|---|---|---|---|---|---|
| Production `ml/` (excluding `vendor/`) | **None** | N/A | N/A | None | **Zero Supervised Models in Production** |
| Production `backend/` | **None** | N/A | N/A | None | **Zero Supervised Models in Production** |
| Research / Diagnostics (`ml/scratch_ml_components.py`) | `ScratchIsolationForest` | Unsupervised | N/A | Research/Benchmark Only | Does not affect production output. |
| Vendor Libs (`ml/vendor/`) | Vendored scikit-learn | N/A | N/A | Vendor dependency | Utility library only. |

> [!IMPORTANT]
> **SUPERVISED LEARNING FINDING**: There are **ZERO supervised classifiers or regressors** in production. The repository relies strictly on unsupervised anomaly detection (M1), text representation matching (M2), transaction heuristic rules (M3), time-series rolling average baseline (M4), and deterministic weighted multi-signal aggregation (M5).

---

## 4. M4 Expenditure Forecasting Verification

- **Actual Algorithm**: Recursive 3-Month Rolling Average (`recursive_rolling_mean_forecast`).
- **Implementation File**: `ml/model_4_forecasting/expenditure_forecast.py`
- **Operational Horizon**: 6 months.
- **Baseline**: Naive Previous-Month Baseline.
- **Empirical LS18 Evaluation**:
  - **6-Month Clean Evaluation**:
    - M4 MAE = ₹310,403,934.10 vs Naive MAE = ₹321,020,787.50 (**3.31% lower MAE**)
    - M4 RMSE = ₹350,568,052.97 vs Naive RMSE = ₹428,285,828.31 (**18.15% lower RMSE**)
  - **8-Month Holdout Evaluation**:
    - M4 MAE = ₹420,589,864.65 vs Naive MAE = ₹442,636,073.00 (**4.98% lower MAE**)
- **XGBoost Status**: Not imported or called in production M4.
- **Qlib Status**: `ml/model_4_forecasting/qlib_series_forecaster.py` exists strictly for auxiliary research benchmark factor generation and does not touch production API outputs.

---

## 5. M1 Cost / Expenditure Anomaly Verification

- **Algorithm**: `sklearn.ensemble.IsolationForest`
- **Hyperparameters**: `n_estimators=300`, `contamination=0.05`, `random_state=42` (defined in `ml/config.py`).
- **Production Features (8 non-redundant)**:
  1. `log_sanction`
  2. `peer_dev`
  3. `robust_dev`
  4. `days`
  5. `num_payments`
  6. `max_payment_ratio`
  7. `payment_var`
  8. `time_between_payments`
- **Handling**: Peer-relative robust MAD / IQR deviation logic; missing values imputed or preserved as explicit NULLs.

---

## 6. M2 Duplicate Work Detection Verification

- **Algorithm**: Geographic Candidate Blocking (State + District + Work Category) + TF-IDF Vectorizer + Cosine Similarity.
- **Implementation File**: `ml/model_2_duplicate_work/double_dipping.py`
- **Empirical Results (`output/double_dipping_results.json`)**:
  - **Candidate Pairs Generated**: **5,000 pairs**
  - **High Risk — Requires Audit Review**: **1,997 pairs**
  - **Medium Risk**: **2,499 pairs**
  - **Low Risk**: **504 pairs**
- **Terminology**: `POTENTIAL DUPLICATE WORK`, `POTENTIAL CROSS-HOUSE DUPLICATE — REQUIRES REVIEW`.

---

## 7. M3 Expenditure / Payment Anomaly Verification

- **Grain**: Transaction / Voucher grain.
- **Logic**: Payment structuring & small-value payment fragmentation pattern detection across vouchers.
- **Terminology**: `SMALL-VALUE PAYMENT FRAGMENTATION PATTERN — REQUIRES REVIEW`.
- **Statutory Limits**: No arbitrary statutory limits claimed.

---

## 8. M5 Multi-Signal Audit Priority Verification

- **Weights (Max Sum = 1.00)**:
  - Cost Risk: `0.30`
  - Speed & Delay: `0.25`
  - Statutory Compliance: `0.25`
  - Vendor & Payment Risk: `0.10`
  - Eligibility & Beneficiary: `0.10`
- **Tier Assignment Logic**:
  - `CRITICAL AUDIT PRIORITY` (Score $\ge 0.50$ or $\ge 2$ major dimensions fired)
  - `STANDARD AUDIT PRIORITY` ($0.25 \le \text{Score} < 0.50$ or 1 major dimension fired)
  - `LOW AUDIT PRIORITY` ($\text{Score} < 0.25$)

---

## 9. UI / API Feature Verification Matrix

| Feature | Source Implementation File | Automated Test File | Status |
|---|---|---|---|
| **4-Role Demo Context Switcher** | `frontend/app.js` | `tests/test_final_integrity.py` | **DEMO CONTEXT SWITCH** |
| **State & District Filters** | `frontend/app.js`, `backend/app.py` | `tests/test_full_system.py` | **IMPLEMENTED + TESTED** |
| **Basic Keyword Work Search** | `backend/app.py` (`/api/query`) | `tests/test_full_system.py` | **IMPLEMENTED + TESTED** |
| **Markdown Audit Report Viewer** | `backend/app.py` (`/api/export-reports`) | `tests/test_final_integrity.py` | **IMPLEMENTED + TESTED** |
| **Apple Liquid-Glass UI Tokens** | `frontend/style.css`, `frontend/index.html` | `tests/test_final_integrity.py` | **IMPLEMENTED + TESTED** |
| **Asset Verification Disclosure** | `frontend/index.html`, `backend/app.py` | `tests/test_final_integrity.py` | **IMPLEMENTED + TESTED** |

---

## 10. Dataset Verification

- **LS18 Dataset**: 79,220 works
- **LS17 Dataset**: 92,117 works
- **RS Sitting Dataset**: 19,607 works
- **RS Retired Dataset**: 19,607 works
- **Total Corpus Records**: **210,551 records**
- **Unique Source Work Entities**: **190,944 unique work entities**
- **Synthetic Government Data**: **NONE in production**. Zero synthetic or fake government records exist in production.

---

## 11. External Repository Verification

- **`vendor/funNLP`**: Production text preprocessing support for Indian administrative terms.
- **`vendor/ML-From-Scratch`**: Diagnostic and benchmark comparison tool (`scratch_ml_components.py`). Does NOT alter production outputs.
- **`vendor/qlib`**: Auxiliary research factor generation (`qlib_series_forecaster.py`). Does NOT alter production M4 outputs.
- **`vendor/netron`**: Architecture visualizer tool.

---

## 12. Terminology Audit & Remediation

The repository has been audited for non-incriminating language. All aggressive or premature phrasing ("fraud detected", "guilty", "collusion confirmed") has been replaced with objective governance terminology:
- `POTENTIAL ANOMALY`
- `POTENTIAL DUPLICATE`
- `CRITICAL AUDIT PRIORITY`
- `SMALL-VALUE PAYMENT FRAGMENTATION PATTERN — REQUIRES REVIEW`
- `INDEPENDENT ASSET VERIFICATION EVIDENCE UNAVAILABLE IN CURRENT SOURCE DATA`

---

## 13. Suspect Audit Report Corrections Table

| Historical Incorrect Claim | Actual Verified Code Evidence | Corrected Claim |
|---|---|---|
| M1 $n\_estimators=200$ | `ml/config.py` sets `IF_N_ESTIMATORS = 300` | M1 Isolation Forest uses $n\_estimators=300$. |
| M2 is Random Forest Classifier | `ml/model_2_duplicate_work/double_dipping.py` uses TF-IDF + Cosine Similarity | M2 is Duplicate Work Detection via Geographic Blocking & TF-IDF Cosine Similarity. |
| M2 Candidate Count: 3,090 pairs | `output/double_dipping_results.json` | Actual candidate count is 5,000 pairs (1,997 High Risk, 2,499 Medium Risk, 504 Low Risk). |
| M4 is XGBoost | `ml/model_4_forecasting/expenditure_forecast.py` uses `recursive_rolling_mean_forecast` | M4 is Recursive 3-Month Rolling Average Baseline (Multi-step 6-Month Horizon). |
| M5 is NL Query Engine | `ml/model_5_audit_priority/misuse_priority.py` | M5 is Deterministic Weighted Multi-Signal Audit Priority Aggregator. |
| "100% ML Model Accuracy" | `tests/` suite execution | 149/149 represents software unit test pass count, not ML classification accuracy. |

---

## 14. Required Remediation Priorities

### P0 — Immediate Action (Completed)
1. **Source of Truth Document Created**: `docs/SIH26102_SOURCE_OF_TRUTH.md` published as authoritative reference.
2. **Reconciliation Documents Synchronized**: All docs updated to eliminate stale claims.

### P1 — Prior to Final Submission
1. **Freeze Architecture**: Freeze M1–M5 canonical identities, backend routes, and frontend UI tokens.

### P2 — Ongoing Maintainability
1. **Automated Consistency Assertions**: Maintain `tests/test_final_integrity.py` assertions ensuring model descriptions match `backend/canonical_registry.py`.
