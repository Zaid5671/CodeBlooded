# MPLADS Anomaly Detection & Audit Decision-Support System (Lok Sabha 18th)

## Overview
This system is an **Audit Decision-Support & Statistical Anomaly Triage Engine** for the **Lok Sabha 18th Members of Parliament Local Area Development Scheme (MPLADS)** datasets.

> [!IMPORTANT]
> **Audit Decision-Support Disclaimer**:
> This system performs statistical, financial, and timing anomaly detection to prioritize administrative audit reviews. It is **NOT** a fraud classifier. A `HIGH RISK — REQUIRES AUDIT REVIEW` score does **NOT** constitute proof of fraud, corruption, favoritism, or criminal wrongdoing.

---

## Technical Architecture & Methodology

### 1. Data Quality Floor & Work ID Normalization
- **Data Quality Floor**: Works with `Sanction Amount < ₹1,000` are categorized as `DATA_QUALITY_REVIEW` and excluded from influencing peer statistical grouping or ML model training.
- **Canonical Work ID Normalization**: Normalizes free-text `Work` identifiers (e.g. `WS/\t MP620/2024-2025/133166-Construction...`) into canonical `clean_work_id` (`WS/MP620/2024-2025/133166`).

### 2. Mandatory Expenditure Aggregation
- Multiple raw expenditure vouchers/installments for a single project are aggregated prior to joining:
  $$\text{actual\_expenditure} = \sum \text{Fund Disbursed Amount}$$
- Out of 84,172 raw expenditure voucher records, 56,604 unique work projects were matched (14,628 works had multi-installment vouchers, up to 49 vouchers for a single work).

### 3. Work Category Taxonomy
- Works are categorized using deterministic keyword precedence into 11 taxonomy groups:
  `ROAD`, `EDUCATION`, `HEALTH`, `COMMUNITY_BUILDING`, `LIGHTING`, `WATER_SUPPLY`, `SANITATION`, `ELECTRIFICATION`, `EQUIPMENT`, `SPORTS`, `OTHER`.

### 4. Hierarchical Peer Grouping & Zero-IQR MAD Fallback
- **Hierarchy**:
  1. `(Category, State)` if group size $N \ge 20$.
  2. `(Category, National)` if state $N < 20$ but national $N \ge 5$.
  3. `INSUFFICIENT_PEER_DATA` if national $N < 5$.
- **Robust Deviation**:
  - Primary: $\text{robust\_deviation} = (\text{sanction\_amount} - \text{peer\_median}) / \text{IQR}$
  - Zero-IQR Fallback: When $\text{IQR} == 0$, uses Median Absolute Deviation ($\text{MAD} = \text{median}(|x - \text{median}|)$) scaled by $1.4826 \times \text{MAD}$.

### 5. Isolation Forest ML Detector
- Unsupervised `IsolationForest` (`n_estimators=300`, `contamination=0.05`, `random_state=42`).
- Trained on non-redundant features: `log_sanction_amount`, `peer_dev_ratio_filled`, `robust_dev_filled`, `days_filled`.

### 6. SLA Compliance Engine
- **Sanction SLA Breach**: Recommendation status pending/approved $> 75$ days.
- **Rejection SLA Breach**: Rejection notification $> 45$ days.

### 7. Leak-Free 80/20 Train-Test Validation
- 80% Training set (63,372 works) and 20% Test set (15,844 works).
- Peer statistics and ML estimators fit strictly on train splits before evaluating test splits across 5 distinct random seeds (42, 100, 200, 300, 400).
- **Out-of-Sample Anomaly Rate**: Mean **5.07%** ($\pm 0.23\%$).
- **Out-of-Sample Cross-Detector Concordance (Jaccard)**: Mean **0.4571** ($\pm 0.0274$).

---

---

## Repository Structure

```
├── frontend/                     # Apple-inspired Web Interface (index.html, style.css, app.js)
├── backend/                      # Flask REST API & Canonical Model Registry (app.py, canonical_registry.py)
├── ml/                           # Production Machine Learning Models
│   ├── model_1_cost_anomaly/     # M1: Peer IQR/MAD & Isolation Forest Cost Anomaly Detection
│   ├── model_2_duplicate_work/    # M2: Record Linkage & Multi-Signal Double-Dipping Detector
│   ├── model_3_expenditure_anomaly/ # M3: Expenditure Aggregation & Duplicate Voucher Engine
│   ├── model_4_forecasting/      # M4: Recursive Rolling Mean Time-Series Forecaster
│   └── model_5_audit_priority/   # M5: Audit Misuse Priority Aggregator & Consensus Engine
├── feature_engineering/          # Data Preprocessing, Normalization & Taxonomy Classifier
├── data_pipeline/                # Data Loaders & Master Lifecycle Reconciliation Engine
├── audit_rules/                  # Deterministic Statutory Audit Rules
│   ├── delay/                    # Delayed Projects Detection
│   ├── statutory_compliance/     # SLA & Approval Compliance Rules
│   ├── eligibility/              # Inadmissible Works & Private Beneficiaries Engine
│   ├── vendor_risk/              # Vendor Concentration HHI & Agency Network Analytics
│   ├── fund_utilization/         # Fund Utilization Engine
│   └── evidence.py               # Human-Readable Audit Evidence Generator
├── scripts/                      # Data, Training, Evaluation, Validation & Dashboard Scripts
├── tests/                        # Comprehensive Production Unit Test Suite (134 tests)
├── docs/                         # System Documentation & Model Cards
├── reports/                      # Validation, Audit & Phase Reports
├── data/                         # Original Raw Government Datasets (Read-Only)
└── output/                       # Generated Output Artifacts & JSON Reports
```

---

## Execution Instructions

```bash
# Run full audit & ML pipeline
python3 run_pipeline.py

# Run complete 134-test production unit test suite
python3 -m pytest tests/ -v

# Run leak-free 80/20 train-test split validation experiment
python3 scripts/validation/test_80_20_split.py

# Launch Flask API Backend server (Port 5051)
python3 backend/app.py
```

All generated output artifacts are saved in `output/`:
- `scored_sanctioned_works.json` & `scored_sanctioned_works.json.gz`
- `scored_sanctioned_works.csv`
- `pipeline_summary.json`
- `validation_results.json`
- `model_config.json`
- `dashboard.html`