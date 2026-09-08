# AI-Powered MPLADS Audit Intelligence Platform (SIH26102)
## Team CodeBlooded — Lok Sabha 18th Audit Decision-Support & Anomaly Triage Engine

![SIH26102](https://img.shields.io/badge/Problem%20Statement-SIH26102-blue.svg)
![Organization](https://img.shields.io/badge/Organization-MoSPI%20%7C%20DIID-navy.svg)
![Team](https://img.shields.io/badge/Team-CodeBlooded-red.svg)
![Dataset Scope](https://img.shields.io/badge/Corpus%20Records-210%2C551-orange.svg)
![Architecture](https://img.shields.io/badge/ML%20Architecture-Verified%20%26%20Frozen-green.svg)
![Test Pass Rate](https://img.shields.io/badge/Test%20Pass%20Rate-100%25%20(149%2F149)-brightgreen.svg)
![Backend](https://img.shields.io/badge/Backend-Python%203.13%20%7C%20Flask%20(25%20APIs)-blue.svg)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla%20JS%20%7C%20Tailwind%20CSS%20%7C%20Chart.js-teal.svg)

---

## 1. Problem Statement & Official Metadata

- **Problem Statement ID**: **SIH26102**
- **Problem Statement Title**: AI-Powered MPLADS Audit Intelligence Platform
- **Nodal Ministry / Organization**: Ministry of Statistics and Programme Implementation (MoSPI)
- **Department**: Data Informatics & Innovation Division (DIID)
- **Team Name**: **CodeBlooded**
- **Target Scheme**: Members of Parliament Local Area Development Scheme (MPLADS)
- **Primary Data Scope**: **Lok Sabha 18th** (with comparison datasets across Lok Sabha 17th, Rajya Sabha Sitting, and Rajya Sabha Retired MPs)
- **Headline Compliance Alignment**: *"Near-Complete Functional & Technical Match to SIH26102"*

---

## 2. Executive Summary & Audit Governance Disclaimer

The **AI-Powered MPLADS Audit Intelligence Platform** is an enterprise-grade administrative decision-support system designed to assist MoSPI administrative authorities, district nodal agencies, and financial auditors in scrutinizing work recommendations, fund utilization, transaction patterns, execution timelines, statutory SLA compliance, and candidate duplicate recommendations under MPLADS.

The platform processes **210,551 total corpus records** across **190,944 unique source work entities** and **272,978 payment vouchers**. It automates statistical anomaly triage through a 5-tier canonical machine learning pipeline (M1–M5), presenting prioritized administrative audit workflows on an Apple-inspired glassmorphism web interface.

> [!IMPORTANT]
> **Governance & Non-Incriminating Terminology Disclaimer**:
> This platform performs statistical, financial, and timing anomaly triage to prioritize administrative audit reviews. It is **NOT** a criminal or fraud classifier. A `CRITICAL AUDIT PRIORITY` score or `M2 Candidate-Pair Risk Tier` does **NOT** constitute proof of illegal activity, corruption, or favoritism. All flags indicate works requiring administrative audit review under objective governance standards.
>
> **Data Scope Boundary**: Independent physical asset verification evidence (such as geotagged site inspection photos or third-party completion certificates) is unavailable in current official source MPLADS datasets. The system explicitly discloses this boundary across UI footers, API metadata, and report headers (*"Independent asset verification evidence unavailable in current source data"*).

---

## 3. Dataset Scope, Resources & Keying Architecture

### 3.1 Corpus Breakdown (210,551 Total Records)
The platform integrates four official government datasets sourced from MoSPI e-SAKSHI MPLADS administrative portals:

| Corpus ID | Dataset Name | Sanctioned Works | Expenditure Vouchers | Completed Works | Recommended Works | Total Corpus Records |
|---|---|---|---|---|---|---|
| **`LS18`** | **18th Lok Sabha (Primary)** | **79,220** | **84,172** | **34,440** | **107,024** | **107,024** |
| **`LS17`** | **17th Lok Sabha (Historical)** | 92,117 | 138,575 | 71,256 | 94,749 | 94,749 |
| **`RS_Sitting`** | **Rajya Sabha Sitting MPs** | 19,607 | 25,141 | 9,979 | 25,240 | 25,240 |
| **`RS_Retired`** | **Rajya Sabha Retired MPs** | 19,607 | 25,130 | 9,964 | 25,204 | 25,204 |
| **TOTAL** | **All Corpora Combined** | **210,551** | **272,978** | **125,639** | **252,217** | **210,551** |

### 3.2 Canonical Work Key & Entity Deduplication
- **Unique Source Work Entities**: **190,944 unique work entities** across all datasets.
- **Canonical Key Format**: `canonical_work_key = CORPUS|source_work_id` (achieves zero collisions across all 210,551 records).
- **Rajya Sabha Snapshot Identity**: `RS_Sitting` and `RS_Retired` represent historical snapshot views of the same underlying Rajya Sabha source work population (19,607 overlapping RS Work IDs; 19,606 identical rows; 1 row differs only in Work Status; union = 19,607 unique source works). Entity deduplication prevents double-counting.
- **Zero Synthetic Government Records**: **No synthetic or fake government records exist in the audited production data paths.** 100% of analyzed data originates from actual government records.

---

## 4. Feature Engineering, Taxonomy Classifier & Peer Grouping

### 4.1 Data Quality Floor & Work ID Normalization
1. **Data Quality Floor**: Works with `Sanction Amount < ₹1,000` are categorized as `DATA_QUALITY_REVIEW` and excluded from peer statistical grouping and ML model training to prevent skewing variance calculations.
2. **Work ID Normalization**: Normalizes free-text `Work` strings (e.g. `WS/\t MP620/2024-2025/133166-Construction...`) into canonical `clean_work_id` (`WS/MP620/2024-2025/133166`).

### 4.2 Work Category Taxonomy Classifier (11 Groups)
Works are classified using deterministic keyword precedence rules into 11 domain categories:
- `ROAD` (Roads, CC Roads, Bituminous, Pathways)
- `EDUCATION` (School Classrooms, Libraries, Educational Supplies)
- `HEALTH` (Hospitals, Primary Health Centres, Medical Equipment)
- `COMMUNITY_BUILDING` (Community Halls, Panchayat Bhawans, Auditoriums)
- `LIGHTING` (High-Mast Lights, Solar Street Lights, LED Lighting)
- `WATER_SUPPLY` (Borewells, Tube Wells, Handpumps, Overhead Tanks)
- `SANITATION` (Public Toilets, Drainage Systems, Waste Management)
- `ELECTRIFICATION` (Transformers, Power Grid Extensions)
- `EQUIPMENT` (Ambulances, Generators, Public Machinery)
- `SPORTS` (Sports Complexes, Stadiums, Gym Equipment)
- `OTHER` (Unclassified infrastructure works)

### 4.3 Hierarchical Peer Grouping & Zero-IQR MAD Fallback Math
To detect cost anomalies fairly across states and work types, works are evaluated against statistical peer groups:
- **Grouping Hierarchy**:
  1. Primary Group: `(Category, State)` if group size $N \ge 20$.
  2. Secondary Fallback: `(Category, National)` if state $N < 20$ but national $N \ge 5$.
  3. Insufficient Data: `INSUFFICIENT_PEER_DATA` if national $N < 5$.
- **Robust Deviation Math**:
  $$\text{robust\_deviation} = \frac{\text{sanction\_amount} - \text{peer\_median}}{\text{IQR}}$$
- **Zero-IQR MAD Fallback**: When peer $\text{IQR} == 0$ (e.g., standardized solar light sanctions), the system falls back to Median Absolute Deviation ($\text{MAD}$):
  $$\text{MAD} = \text{median}(|x - \text{median}|)$$
  $$\text{scaled\_MAD} = 1.4826 \times \text{MAD}$$

---

## 5. Canonical M1–M5 ML Architecture (Verified & Frozen)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     RAW DATASET RECONCILIATION ENGINE                   │
│   79,220 Master Sanctioned Works  │  84,172 Raw Payment Vouchers     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│            FEATURE ENGINEERING & TAXONOMY CLASSIFIER (11 GROUPS)       │
│  (ROAD, EDUCATION, HEALTH, COMMUNITY_BUILDING, WATER_SUPPLY, etc.)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│ M1 COST ANOMALY   │       │ M2 DOUBLE-DIPPING │       │ M3 PAYMENT        │
│ Isolation Forest  │       │ Candidate Pair    │       │ Structuring &     │
│ (300 estimators,  │       │ Similarity Engine │       │ Velocity Analysis │
│  contam=0.05)     │       │ (5,000 Pairs)     │       │ (Aggregated Vouchers)│
└────────┬──────────┘       └────────┬──────────┘       └────────┬──────────┘
         │                           │                           │
         │         ┌─────────────────┴─────────────────┐         │
         │         │ M4 EXPENDITURE TIME-SERIES FORECAST│         │
         │         │ 6-Month Rolling Mean & 95% CI     │         │
         │         └─────────────────┬─────────────────┘         │
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│            M5 DETERMINISTIC AUDIT PRIORITY AGGREGATOR ENGINE            │
│  Combines M1–M4 Flags, Statutory SLA Breaches, Vendor HHI & Compliance   │
│  Outputs Tiers: CRITICAL (1,635 works), HIGH, MEDIUM, LOW Priorities    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Model M1 — Cost / Expenditure Anomaly Engine
- **Implementation**: `ml/model_1_cost_anomaly/isolation_forest.py`
- **Algorithm**: Unsupervised `sklearn.ensemble.IsolationForest` (`n_estimators=300`, `contamination=0.05`, `random_state=42`).
- **8 Production Features**:
  1. `log_sanction`: Log-transformed sanction amount.
  2. `peer_dev`: Ratio deviation from peer group median.
  3. `robust_dev`: Robust z-score normalized by peer IQR / MAD.
  4. `days`: Project sanction-to-completion duration in days.
  5. `num_payments`: Total number of payment vouchers disbursed.
  6. `max_payment_ratio`: Ratio of max single payment to total sanction.
  7. `payment_var`: Variance in inter-payment voucher amounts.
  8. `time_between_payments`: Average days between consecutive disbursements.
- **Output**: Flagged **3,961 works** requiring cost audit review out of 79,220 master works.
- **Supervised Fraud Classifier / Fake Labels**: **NONE**. No supervised fraud prediction model exists.

### 5.2 Model M2 — Double-Dipping & Duplicate Work Intelligence
- **Implementation**: `ml/model_2_duplicate_work/double_dipping.py`
- **Algorithm**: Geographic Candidate Blocking (State + District + Work Category) + TF-IDF Vectorization (`ngram_range=(1,2)`) + Cosine Similarity matching across Work Title, Description, Executing Vendor, and Location Entities.
- **Text Normalization**: Domain-aware stopword preservation using `vendor/funNLP` (`GLOBAL_STOPWORDS` preserving `road`, `school`, `hospital`, `hall`, `construction`).
- **Candidate Pair Output (`output/double_dipping_results.json`)**:
  - Total Candidates Generated: **5,000 candidate pairs**
  - **M2 Candidate-Pair Risk Tiers**:
    - High Risk: **1,997 pairs**
    - Medium Risk: **2,499 pairs**
    - Low Risk: **504 pairs**
  - *Clarification*: These are M2 candidate-pair risk tiers and are NOT M5 audit-priority tiers.

### 5.3 Model M3 — Expenditure / Payment Anomaly Detection
- **Implementation**: `ml/model_3_expenditure_anomaly/duplicate_expenditure.py` & `expenditure_matching.py`
- **Algorithm**: Vectorized payment structuring analysis detecting voucher splitting, sudden payment velocity bursts, fiscal year-end rushes, and vendor clustering across 56,604 unique payment-linked projects.
- **Optimized Execution**: Vectorized `.groupby().agg()` aggregations executing in **~0.84s** (**18.3x speedup**).
- **Separate Audit Rules**:
  - **Delay Detection Rules**: Measures sanction SLA breaches (>75 days) and rejection SLA breaches (>45 days).
  - **Statutory Compliance Rules**: Measures regulatory approval compliance, work eligibility, and inadmissible work rules.

### 5.4 Model M4 — Rolling Expenditure Forecasting
- **Implementation**: `ml/model_4_forecasting/expenditure_forecast.py`
- **Algorithm**: Recursive 3-Month Rolling Average Forecast (`recursive_rolling_mean_forecast`). Multi-step 6-month forecast horizon with empirical 95% confidence intervals.
- **Evaluated LS18 National Outlay Improvement**:
  - **6-Month Evaluation (2026-03 to 2026-08)**: M4 MAE ₹310.40M vs Naive ₹321.02M (**3.31% lower MAE**); M4 RMSE ₹350.57M vs Naive ₹428.28M (**18.15% lower RMSE**).
  - **8-Month Holdout Evaluation (2026-02 to 2026-09)**: M4 MAE ₹420.59M vs Naive ₹442.64M (**4.98% lower MAE**).
- **XGBoost / Prophet Status**: **NONE in production**.

### 5.5 Model M5 — Multi-Signal Audit Priority Aggregator
- **Implementation**: `ml/model_5_audit_priority/misuse_priority.py`
- **Algorithm**: Deterministic Weighted Multi-Signal Evidence Aggregator running via fast dictionary iteration (`df.to_dict('records')`) in **~0.42s** (**72.7x speedup**).
- **Signal Weights (Max Sum = 1.00)**:
  - Cost Risk Weight: `0.30`
  - Speed & Delay Weight: `0.25`
  - Statutory Compliance Weight: `0.25`
  - Vendor & Payment Risk Weight: `0.10`
  - Eligibility & Beneficiary Weight: `0.10`
- **Canonical M5 Audit Priority Tiers**:
  - **`CRITICAL AUDIT PRIORITY`**: **1,635 works** (Score $\ge 0.50$ or $\ge 2$ major independent signals).
  - **`STANDARD AUDIT PRIORITY`**: ($0.20 \le \text{Score} < 0.50$ or 1 major signal).
  - **`LOW AUDIT PRIORITY`**: ($\text{Score} < 0.20$ and 0 major signals).

---

## 6. Vendor Tooling & External Repositories

- **`vendor/funNLP`**: Production text preprocessing support for administrative terms (`GLOBAL_STOPWORDS`). Preserves domain-important terms (`road`, `school`, `hospital`, `hall`, `construction`).
- **`vendor/ML-From-Scratch`**: Research, diagnostic, and benchmark comparison tool (`scratch_ml_components.py`). Does NOT alter production outputs.
- **`vendor/qlib`**: Research factor generation (`qlib_series_forecaster.py`). Does NOT alter production M4 outputs.
- **`vendor/netron`**: Architecture visualization tool.

---

## 7. Full-Stack Performance Benchmarks

The entire stack has been forensically audited and optimized for speed, memory efficiency, and UI responsiveness:

| Component / Endpoint | Baseline | Optimized | Speedup Factor | Optimization Mechanism |
|---|---|---|---|---|
| **Backend Startup** | 1.05s | **1.09s** | ~1.0x | Server-side `CACHE` pre-warming at initialization |
| **GET /api/summary** | 0.0248s | **0.0131s** | **1.89x** | In-memory cached payload |
| **GET /api/works?limit=50** | 0.0573s | **0.0482s** | **1.18x** | Slice-based response rendering |
| **GET /api/double-dipping** | 0.1082s (uncached) | **0.0014s** (cached) | **77.2x** | Measured sub-5-ms range |
| **GET /api/delayed-projects** | 0.4127s (cold cache) | **0.0019s–0.1988s** (warm cache) | **2.07x–217.2x** | Cold cache file read vs warm cache read |
| **GET /api/compliance** | 0.2776s (uncached) | **0.0021s** (cached) | **132.1x** | Measured sub-5-ms range |
| **GET /api/audit-priority** | 0.0017s (uncached) | **0.0004s** (cached) | **4.25x** | Measured sub-5-ms range |
| **Model 3 Expenditure Aggregation** | 15.38s | **0.84s** | **18.3x** | Vectorized Pandas `.groupby().agg()` |
| **Model 5 Audit Priority Aggregator** | 30.55s | **0.42s** | **72.7x** | Fast Python `to_dict('records')` iteration |
| **Full Pipeline Data Handoff** | ~100.8s | **~47.2s** | **2.13x** | In-memory DataFrame handoffs |
| **Automated Software Test Suite** | 149 tests | **149 passed** | **100% Pass** | 149/149 passed in 73.54s |

---

## 8. Complete 25 Backend REST API Endpoint Directory

The Flask backend server (`backend/app.py`) registers **25 REST API endpoints**:

| # | Endpoint Route | HTTP Method | Response Data / Parameters | Sub-5ms Cached Response |
|---|---|---|---|---|
| 1 | `GET /` | GET | Serves Frontend Single Page App | Yes |
| 2 | `GET /api/corpora` | GET | Available corpus metadata (LS18, LS17, RS) | Yes |
| 3 | `GET /api/summary` | GET | Executive KPIs, Total Works & Financial Stats | Yes |
| 4 | `GET /api/validation` | GET | Data Quality Floor & Work ID Normalization Check | Yes |
| 5 | `GET /api/signals` | GET | Statistical Audit Signal Counts & Distribution | Yes |
| 6 | `GET /api/works` | GET | Paginated Master Works (`page`, `limit`, `category`, `search`) | Dynamic |
| 7 | `GET /api/works/<work_id>` | GET | Detailed Work Entity Profile & Audit History | Yes |
| 8 | `GET /api/top-anomalies` | GET | Top M1 Cost Anomaly Flagged Records | Yes |
| 9 | `GET /api/double-dipping` | GET | M2 Duplicate Candidate Pairs (5,000 pairs) | Yes |
| 10 | `GET /api/delayed-projects` | GET | SLA Delay Breaches & Project Duration Anomalies | Yes |
| 11 | `GET /api/compliance` | GET | Statutory SLA & Approval Compliance Metrics | Yes |
| 12 | `GET /api/ia-watchlist` | GET | Implementing Agency Watchlist & Risk Score | Yes |
| 13 | `GET /api/audit-priority` | GET | M5 Deterministic Audit Priority Rankings | Yes |
| 14 | `GET /api/forecast` | GET | M4 Rolling Average 6-Month Trajectory Predictions | Yes |
| 15 | `GET /api/vendor-risk` | GET | Vendor Concentration HHI & Agency Network Risk | Yes |
| 16 | `GET /api/inadmissible-works` | GET | Inadmissible Work Rule Evaluation | Yes |
| 17 | `GET /api/private-beneficiaries` | GET | Private Beneficiary & Non-Public Asset Flags | Yes |
| 18 | `GET /api/duplicate-expenditure` | GET | Transaction-Level Payment Voucher Anomaly Flags | Yes |
| 19 | `GET /api/fund-utilization` | GET | State & Constituency Fund Utilization Ratios | Yes |
| 20 | `GET /api/deep-evaluation` | GET | Comprehensive Multi-Model Deep Evaluation Diagnostics | Yes |
| 21 | `GET /api/canonical-registry` | GET | Canonical Model Parameter Registry Definitions | Yes |
| 22 | `GET, POST /api/query` | GET/POST | Fast Substring Keyword Search across Master Works | Dynamic |
| 23 | `GET, POST /api/agents/triage` | GET/POST | Multi-Agent Consensus Triage Simulation | Dynamic |
| 24 | `POST /api/notifications/dispatch` | POST | Alert Notification Dispatch Handler | Action |
| 25 | `GET /api/export-reports` | GET | Static Markdown Audit Report Exporter | Stream |

---

## 9. Frontend Capabilities & Demo User Roles

- **Visual Styling**: `frontend/style.css` implements modern Apple-inspired glassmorphism UI tokens (`backdrop-filter: blur(12px)`, translucent card backgrounds, dark mode toggle).
- **Client-Side Optimization**: `frontend/app.js` wraps backend fetches with an in-memory `apiCache` map with 60s TTL invalidation and 300ms input debouncing on search explorer.
- **Demo Role Switcher**: Interactive context switcher allowing users to test role-oriented perspectives:
  1. **Member of Parliament (MP)**: Constituency-focused project tracking and fund allocation views.
  2. **District Nodal Authority**: Project SLA monitoring, sanction tracking, and vendor risk analysis.
  3. **State Nodal Authority**: State-wide fund utilization ratios and inter-district performance comparisons.
  4. **Ministry Nodal Authority (MoSPI)**: Executive national KPIs, M5 Critical Audit Priority queue, and policy forecasting.
  5. **Independent Auditor / Evaluator**: Full forensic audit breakdown, M1 cost anomalies, M2 duplicate candidate pair inspection.
- *Clarification*: The role switcher represents frontend demo context switching. Server-enforced RBAC authentication is not implemented.

---

## 10. PS Requirement Coverage Matrix

| # | Requirement Category | Actual Technical Implementation | Verification Status |
|---|---|---|---|
| 1 | **Large-Scale Fund Monitoring** | Unified corpus loading (210,551 records across LS18, LS17, RS) | **FULLY IMPLEMENTED** |
| 2 | **Expenditure Analysis** | M1 Isolation Forest ($n\_estimators=300$) + peer MAD analysis | **FULLY IMPLEMENTED** |
| 3 | **Cost Estimate Analysis** | Peer-relative cost ratio z-score & Tukey fence overrun detection | **FULLY IMPLEMENTED** |
| 4 | **Work Execution / Delay** | Delay tracking engine evaluating 45-day response & 75-day sanction timelines | **FULLY IMPLEMENTED** |
| 5 | **Payment Pattern Analysis** | M3 transaction-level voucher structuring & fragmentation detector | **FULLY IMPLEMENTED** |
| 6 | **Asset Verification Boundary** | Explicit disclosure: *"Independent asset verification evidence unavailable in current source data"* | **DATA-LIMITED / DISCLOSED** |
| 7 | **Duplicate Works Detection** | M2 Geographic Blocking + TF-IDF Vectorizer + Cosine Similarity | **FULLY IMPLEMENTED** |
| 8 | **Dynamic Risk Prioritization** | M5 Weighted Multi-Signal Audit Priority Aggregator | **FULLY IMPLEMENTED** |
| 9 | **Expenditure Forecasting** | M4 Recursive 3-Month Rolling Average Forecast (6-month horizon) | **FULLY IMPLEMENTED** |
| 10 | **Decision-Support Dashboard** | Apple-style glassmorphism responsive web UI | **FULLY IMPLEMENTED** |
| 11 | **Role Audiences** | 4-role demo context switcher (MP, District, State, Central) | **DEMO CONTEXT SWITCH ONLY** |

---

## 11. Leak-Free 80/20 Train-Test Validation Experiment

To verify model stability and eliminate data leakage, an independent 80/20 train-test split experiment was conducted across 5 random seeds (42, 100, 200, 300, 400):

- **Data Split**: 80% Training set (63,372 works) and 20% Test set (15,844 works).
- **Strict Leak-Free Protocol**: Peer statistics (median, IQR, MAD) and ML estimators were fitted strictly on training splits before evaluating test splits.
- **Out-of-Sample Anomaly Rate**: Mean **5.07%** ($\pm 0.23\%$).
- **Out-of-Sample Cross-Detector Concordance (Jaccard Index)**: Mean **0.4571** ($\pm 0.0274$).

---

## 12. Complete Directory Structure

```
.
├── backend/                             # Flask REST API Server & Handlers
│   ├── app.py                           # 25 REST API Routes with Startup In-Memory Cache
│   ├── canonical_registry.py           # Canonical Model Parameter Registry
│   └── audit_engine/                    # Backend Audit Aggregation Handlers
├── frontend/                            # Apple-Inspired Web Interface
│   ├── index.html                       # Single Page Application Layout
│   ├── app.js                           # Client-side Router, apiCache & Debounced Search
│   └── style.css                        # Modern Responsive Glassmorphism Stylesheet
├── ml/                                  # Production ML Models (M1–M5)
│   ├── model_1_cost_anomaly/            # M1: Peer IQR/MAD & Isolation Forest Cost Anomaly
│   ├── model_2_duplicate_work/          # M2: Candidate Blocking & Record Linkage Engine
│   ├── model_3_expenditure_anomaly/     # M3: Vectorized Payment Aggregation & Structuring
│   ├── model_4_forecasting/             # M4: Rolling Mean Expenditure Forecaster
│   └── model_5_audit_priority/          # M5: Deterministic Audit Priority Aggregator
├── audit_rules/                         # Deterministic Statutory Audit Rules
│   ├── delay/                           # Delay Detection Rules
│   ├── statutory_compliance/            # Statutory Compliance Rules
│   ├── eligibility/                     # Inadmissible Works & Private Beneficiary Engine
│   ├── vendor_risk/                     # Vendor Concentration HHI & Agency Network Analytics
│   ├── fund_utilization/                # Fund Utilization Engine
│   └── evidence.py                      # Human-Readable Audit Evidence Generator
├── feature_engineering/                 # Data Preprocessing & 11-Group Taxonomy Classifier
├── data_pipeline/                       # Data Loaders & Master Lifecycle Reconciliation
├── vendor/                              # Text Preprocessing & Research Tools
│   ├── funNLP/                          # Administrative Text Tokenization & Stopwords
│   └── ML-From-Scratch/                 # Diagnostic Benchmark Components
├── scripts/                             # Verification & Profiling Scripts
│   ├── profile_system.py                # System Latency & Performance Benchmark Runner
│   └── validation/                      # 80/20 Validation Scripts
├── tests/                               # Comprehensive Automated Test Suite (149 tests)
├── docs/                                # Forensic Audit Reports & Documentation
│   ├── SIH26102_SOURCE_OF_TRUTH.md      # Reconciled System Source of Truth
│   ├── SIH26102_PERFORMANCE_AUDIT.md    # Detailed Forensic Performance Audit
│   └── SIH26102_PERFORMANCE_REPORT.md   # Final Performance Benchmarks & Verification
├── data/                                # Original Raw Datasets (Read-Only)
├── output/                              # Generated Scored JSON/CSV Output Artifacts
├── run_pipeline.py                      # Unified ML Audit Pipeline Execution Script
└── README.md                            # Comprehensive Production README
```

---

## 13. Installation, Environment Setup & Execution Guide

### 13.1 System Requirements
- **Operating System**: macOS, Linux, or Windows (WSL2 recommended)
- **Python**: Version 3.10+ (Python 3.13 recommended)
- **Dependencies**: `pandas`, `scikit-learn`, `flask`, `flask-cors`, `pytest`, `numpy`, `scipy`

### 13.2 Step-by-Step Setup
```bash
# 1. Clone the repository
git clone https://github.com/Zaid5671/CodeBlooded.git
cd CodeBlooded

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install required Python packages
pip install -r requirements.txt
```

### 13.3 Running the Full ML Audit Pipeline
Execute the complete 13-step data loader, feature engineering, and M1–M5 model pipeline:
```bash
python3 run_pipeline.py
```
*Output JSON and CSV files will be generated in `output/`.*

### 13.4 Launching the Backend REST API Server
Start the Flask server on port 5051 with pre-warmed in-memory caching:
```bash
python3 backend/app.py
```

### 13.5 Opening the Frontend Dashboard
Open `frontend/index.html` directly in your browser or serve via Python local server:
```bash
python3 -m http.server 8000 --directory frontend
```
Then navigate to `http://localhost:8000` in your web browser.

### 13.6 Running the Production Test Suite
Execute all 149 automated unit and integration tests:
```bash
python3 -m pytest tests/ -v
```

---

## 14. Prohibited & Non-Supported Claims Policy

To maintain complete empirical integrity, the following claims are **STRICTLY PROHIBITED**:
1. Supervised fraud prediction accuracy, ROC-AUC curves, or precision/recall metrics (since no ground-truth fraud labels exist).
2. Server-enforced role-based access control (RBAC).
3. Interactive Leaflet/GeoJSON GIS choropleth maps.
4. Natural Language SQL query translation in M5.
5. Dynamic PDF or CSV dossier generation on the fly.
6. XGBoost / Prophet forecasting models in M4.
7. Random Forest delay or completion classifiers in M2.
8. Claims of 100% ML accuracy based on 149 software unit tests.

---

## 15. Team & Repository Information

- **Problem Statement ID**: SIH26102
- **Problem Statement Title**: AI-Powered MPLADS Audit Intelligence Platform
- **Team Name**: CodeBlooded
- **Repository URL**: [https://github.com/Zaid5671/CodeBlooded](https://github.com/Zaid5671/CodeBlooded)
- **Status**: **Architecture Verified & Frozen** | **100% Test Pass Rate (149/149 passed)**