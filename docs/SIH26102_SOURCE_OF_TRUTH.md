# SIH26102 Source of Truth — Canonical Reference Document

> **Authoritative Policy**: Executable source code and reproducible outputs are authoritative over earlier documentation, design briefs, or prior reports.

**Project**: AI-Powered MPLADS Audit Intelligence Platform  
**Team**: CodeBlooded  
**Problem Statement ID**: SIH26102  
**Organization**: Ministry of Statistics and Programme Implementation (MoSPI)  
**Department**: Data Informatics & Innovation Division (DIID)  
**Headline Alignment**: *"Near-Complete Functional & Technical Match to SIH26102"*  

---

## 1. Project Overview

The **AI-Powered MPLADS Audit Intelligence Platform** is a decision-support system designed to assist MoSPI administrative authorities in auditing work recommendations, fund utilization, transaction patterns, work execution timelines, and candidate duplicate recommendations under the Members of Parliament Local Area Development Scheme (MPLADS).

---

## 2. Dataset Scope & Keying Architecture

- **Total Corpus Records**: **210,551 records** across 4 official government datasets:
  - `LS18` (18th Lok Sabha): 79,220 sanctioned, 84,172 expenditure, 34,440 completed, 107,024 recommended works
  - `LS17` (17th Lok Sabha): 92,117 sanctioned, 138,575 expenditure, 71,256 completed, 94,749 recommended works
  - `RS_Sitting` (Rajya Sabha Sitting): 19,607 sanctioned, 25,141 expenditure, 9,979 completed, 25,240 recommended works
  - `RS_Retired` (Rajya Sabha Retired): 19,607 sanctioned, 25,130 expenditure, 9,964 completed, 25,204 recommended works
- **Unique Source Work Entities**: **190,944 unique work entities**.
- **Total Payment Transactions**: **272,978 payment vouchers**.
- **Canonical Key Architecture**: `canonical_work_key = CORPUS|source_work_id` (0 collisions across all 210,551 records).
- **Rajya Sabha Snapshot Identity**: `RS_Sitting` and `RS_Retired` represent historical snapshot views of the same source work population (19,607 overlapping RS Work IDs; 19,606 identical rows; 1 row differs only in Work Status; union = 19,607 unique source works). Entity deduplication prevents double-counting.
- **Synthetic Government Data**: **No synthetic or fake government records were identified in the audited production data paths.**

---

## 3. Model M1 — Cost / Expenditure Anomaly

- **Implementation**: `ml/model_1_cost_anomaly/isolation_forest.py`
- **Algorithm**: Unsupervised `sklearn.ensemble.IsolationForest` (`n_estimators=300`, `contamination=0.05`, `random_state=42`).
- **Features (8 non-redundant)**:
  1. `log_sanction`
  2. `peer_dev`
  3. `robust_dev`
  4. `days`
  5. `num_payments`
  6. `max_payment_ratio`
  7. `payment_var`
  8. `time_between_payments`
- **Deviation Logic**: Uses peer-relative Median Absolute Deviation (MAD) / Interquartile Range (IQR) Tukey fences.
- **Supervised Classifier / Fraud Labels**: **NONE**. No supervised fraud prediction exists.

---

## 4. Model M2 — Duplicate Work Detection

- **Implementation**: `ml/model_2_duplicate_work/double_dipping.py`
- **Algorithm**: Geographic Candidate Blocking (State + District + Work Category) + TF-IDF Vectorizer + Cosine Similarity.
- **Candidate Pair Output (`output/double_dipping_results.json`)**:
  - Total Candidates Generated: **5,000 candidate pairs**
  - **M2 Candidate-Pair Risk Tiers**:
    - High Risk (Candidate Pair Risk Tier): **1,997 pairs**
    - Medium Risk (Candidate Pair Risk Tier): **2,499 pairs**
    - Low Risk (Candidate Pair Risk Tier): **504 pairs**
  - *Distinction*: These are M2 candidate-pair risk tiers and are NOT M5 audit-priority tiers (`CRITICAL AUDIT PRIORITY`, `STANDARD AUDIT PRIORITY`, `LOW AUDIT PRIORITY`).
- **Terminology**: `POTENTIAL DUPLICATE — REQUIRES REVIEW`, `POTENTIAL CROSS-HOUSE DUPLICATE — REQUIRES REVIEW`.

---

## 5. Model M3 — Expenditure / Payment Anomaly

- **Implementation**: `ml/model_3_expenditure_anomaly/duplicate_expenditure.py`
- **Method**: Transaction-grain voucher and payment analysis.
- **Indicators**: Identifies small-value payment fragmentation patterns (`num_payments >= 5`, `total_spent > 500000`, `max_payment < 200000`).
- **Terminology**: `SMALL-VALUE PAYMENT FRAGMENTATION PATTERN — REQUIRES REVIEW`. (Heuristic review-oriented indicators; not universal statutory limits).

---

## 6. Model M4 — Expenditure Forecasting

- **Implementation**: `ml/model_4_forecasting/expenditure_forecast.py`
- **Algorithm**: Recursive 3-Month Rolling Average Baseline (`recursive_rolling_mean_forecast`).
- **Operational Forecast Horizon**: Multi-step 6-Month Horizon.
- **Baseline**: Naive Previous-Month Baseline.
- **Empirical Range**: `EMPIRICAL 95% EXPECTED RANGE`.
- **Evaluated LS18 National Outlay Improvement**:
  - **6-Month Clean Evaluation (2026-03 to 2026-08)**: M4 MAE ₹310.40M vs Naive ₹321.02M (**3.31% lower MAE**); M4 RMSE ₹350.57M vs Naive ₹428.28M (**18.15% lower RMSE**).
  - **8-Month Holdout Evaluation (2026-02 to 2026-09)**: M4 MAE ₹420.59M vs Naive ₹442.64M (**4.98% lower MAE**).
- **Wording Policy**: *"On the evaluated LS18 national expenditure series, the recursive 3-month rolling-average M4 forecast reduced MAE by 3.31% on the 6-month evaluation window and 4.98% on the 8-month holdout compared with the naive previous-month baseline."*
- **XGBoost / Prophet Status**: **NONE in production**.

---

## 7. Model M5 — Multi-Signal Audit Priority Aggregator

- **Implementation**: `ml/model_5_audit_priority/misuse_priority.py`
- **Algorithm**: Deterministic Weighted Multi-Signal Evidence Aggregator.
- **Weights (Max Sum = 1.00)**:
  - Cost Risk: `0.30`
  - Speed & Delay: `0.25`
  - Statutory Compliance: `0.25`
  - Vendor & Payment Risk: `0.10`
  - Eligibility & Beneficiary: `0.10`
- **Canonical M5 Audit Priority Tiers**:
  - `CRITICAL AUDIT PRIORITY` (Score $\ge 0.50$ or $\ge 2$ major independent signals)
  - `STANDARD AUDIT PRIORITY` ($0.20 \le \text{Score} < 0.50$ or 1 major signal)
  - `LOW AUDIT PRIORITY` ($\text{Score} < 0.20$ and 0 major signals)

---

## 8. Unified Engine Architecture

- **Implementation**: `ml/unified_model_engine.py`
- **Role**: Orchestrates canonical modules M1–M5 without redefining algorithms or introducing alternate implementations.

---

## 9. External Repositories & Vendor Tooling

- **`vendor/funNLP`**: Production text preprocessing support for administrative terms (`GLOBAL_STOPWORDS`). Preserves domain-important terms (`road`, `school`, `hospital`, `hall`, `construction`).
- **`vendor/ML-From-Scratch`**: Research, diagnostic, and benchmark comparison tool (`scratch_ml_components.py`). Does NOT alter production outputs.
- **`vendor/qlib`**: Research factor generation (`qlib_series_forecaster.py`). Does NOT alter production M4 outputs.
- **`vendor/netron`**: Architecture visualization tool.

---

## 10. Backend APIs & Endpoint Inventory

The **25 registered backend API routes** in `backend/app.py`:
1. `GET /api/corpora` — Returns available corpus metadata
2. `GET /api/summary` — Returns aggregate dataset summary statistics
3. `GET /api/validation` — Returns data quality validation checks
4. `GET /api/signals` — Returns audit signal statistics
5. `GET /api/works` — Returns paginated master work records with search/filter
6. `GET /api/works/<work_id>` — Returns details for a single work entity
7. `GET /api/top-anomalies` — Returns top M1 cost anomaly records
8. `GET /api/double-dipping` — Returns M2 duplicate work candidate pairs
9. `GET /api/delayed-projects` — Returns delayed project records & SLA checks
10. `GET /api/compliance` — Returns statutory compliance metrics
11. `GET /api/ia-watchlist` — Returns implementing agency risk metrics
12. `GET /api/audit-priority` — Returns M5 audit priority score aggregation
13. `GET /api/forecast` — Returns M4 rolling average expenditure projections
14. `GET /api/vendor-risk` — Returns vendor risk network analytics
15. `GET /api/inadmissible-works` — Returns inadmissible work rule evaluation
16. `GET /api/private-beneficiaries` — Returns private beneficiary rule evaluation
17. `GET /api/duplicate-expenditure` — Returns transaction-level payment anomaly analysis
18. `GET /api/fund-utilization` — Returns idle fund utilization metrics
19. `GET /api/deep-evaluation` — Returns deep evaluation model diagnostics
20. `GET /api/canonical-registry` — Returns canonical model registry definitions
21. `GET, POST /api/query` — Basic substring keyword search
22. `GET, POST /api/agents/triage` — Multi-agent consensus triage simulation
23. `POST /api/notifications/dispatch` — Dispatches alert notifications
24. `GET /api/export-reports` — Serves static markdown audit reports
25. `GET /` — Serves frontend static application index

---

## 11. Frontend Capabilities & UI Tokens

- **Visual Styling**: `frontend/style.css` implements modern glassmorphism UI tokens (`backdrop-filter: blur(12px)`, translucent card backgrounds, dark mode toggle).
- **Navigation Views**: Responsive view sections for Overview, Works, Priority, Duplicates, Analytics, Forecast.
- **Demo Role Switcher**: `frontend/app.js` allows demo context switching across MP, District Authority, State Nodal Authority, Ministry Authority, and Evaluator roles. Backend authentication and authorization are not implemented.

---

## 12. PS Requirement Coverage Matrix

| # | Requirement Category | Actual Implementation | Status |
|---|---|---|---|
| 1 | Large-Scale Fund Monitoring | Unified corpus loading (210,551 records across LS18, LS17, RS) | **FULLY IMPLEMENTED** |
| 2 | Expenditure Analysis | M1 Isolation Forest ($n\_estimators=300$) + peer MAD analysis | **FULLY IMPLEMENTED** |
| 3 | Cost Estimate Analysis | Peer-relative cost ratio z-score & Tukey fence overrun detection | **FULLY IMPLEMENTED** |
| 4 | Work Execution / Delay | Delay tracking engine evaluating 45-day response & 75-day sanction timelines | **FULLY IMPLEMENTED** |
| 5 | Payment Pattern Analysis | M3 transaction-level voucher structuring & fragmentation detector | **FULLY IMPLEMENTED** |
| 6 | Asset Verification Boundary | Explicit disclosure: *"Independent asset verification evidence unavailable in current source data"* | **DATA-LIMITED / DISCLOSED** |
| 7 | Duplicate Works Detection | M2 Geographic Blocking + TF-IDF Vectorizer + Cosine Similarity | **FULLY IMPLEMENTED** |
| 8 | Dynamic Risk Prioritization | M5 Weighted Multi-Signal Audit Priority Aggregator | **FULLY IMPLEMENTED** |
| 9 | Expenditure Forecasting | M4 Recursive 3-Month Rolling Average Forecast (6-month horizon) | **FULLY IMPLEMENTED** |
| 10 | Decision-Support Dashboard | Apple-style glassmorphism responsive web UI | **FULLY IMPLEMENTED** |
| 11 | Role Audiences | 4-role demo context switcher (MP, District, State, Central) | **DEMO CONTEXT SWITCH ONLY** |

---

## 13. Known Limitations & Asset Verification Disclosure

> [!IMPORTANT]
> **Data Scope Boundary**: Independent physical asset verification evidence (such as geotagged site inspection photos or third-party completion certificates) is not present in official source MPLADS datasets. The system explicitly discloses this boundary across UI footers, API metadata, and report headers (*"Independent asset verification evidence unavailable in current source data"*).

---

## 14. Current Empirical Metrics & Holdout Results

- **M1 Isolation Forest**: `n_estimators=300`, `contamination=0.05`.
- **M2 Candidate Pairs**: 5,000 candidate pairs (M2 candidate-pair risk tiers: 1,997 High Risk, 2,499 Medium Risk, 504 Low Risk).
- **M4 Forecasting Evaluation**:
  - **6-Month Clean Evaluation**: M4 MAE ₹310.40M vs Naive ₹321.02M (**3.31% lower MAE**); M4 RMSE ₹350.57M vs Naive ₹428.28M (**18.15% lower RMSE**).
  - **8-Month Holdout Evaluation**: M4 MAE ₹420.59M vs Naive ₹442.64M (**4.98% lower MAE**).

---

## 15. Automated Test Suite Status

- **Software Test Suite Pass Rate**: **149 passed / 149 total** in ~76s (100% software test pass rate).
- **Scope**: Covers data loading, feature engineering, M1–M5 model execution, holdout forecasting, and UI integrity assertions.

---

## 16. Git Working Directory State

- **Branch**: `main`
- **Clean Diff Check**: `git diff --check` passed with 0 whitespace issues.
- **Uncommitted Modifications**: Kept locally uncommitted and unstaged as required (`git commit` and `git push` forbidden).

---

## 17. Prohibited & Unsupported Claims

Unsupported aggressive or premature terminology identified during the audit was replaced with objective governance terminology.

The following claims are **STRICTLY PROHIBITED**:
1. Supervised fraud prediction accuracy, ROC-AUC, or precision/recall.
2. Server-enforced role-based access control (RBAC).
3. Interactive Leaflet/GeoJSON GIS choropleth maps.
4. Natural Language SQL query translation in M5.
5. Dynamic PDF or CSV dossier generation.
6. XGBoost / Prophet forecasting models in M4.
7. Random Forest delay or completion classifiers in M2.
8. Claims of 100% ML accuracy based on 149 software unit tests.
