# AI-Powered MPLADS Audit Intelligence Platform (SIH26102)
## Team CodeBlooded — Lok Sabha 18th Audit Decision-Support & Anomaly Triage Engine

![SIH26102](https://img.shields.io/badge/SIH-26102-blue.svg)
![Lok Sabha 18th](https://img.shields.io/badge/Dataset-Lok%20Sabha%2018th-orange.svg)
![Architecture](https://img.shields.io/badge/Architecture-Verified%20%26%20Frozen-green.svg)
![Test Pass Rate](https://img.shields.io/badge/Test%20Pass%20Rate-100%25%20(149%2F149)-brightgreen.svg)
![Backend](https://img.shields.io/badge/Backend-Python%203.13%20%7C%20Flask-blue.svg)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla%20JS%20%7C%20Tailwind%20CSS%20%7C%20Chart.js-teal.svg)

---

## Executive Summary

The **AI-Powered MPLADS Audit Intelligence Platform** (Problem Statement **SIH26102**, Team **CodeBlooded**) is an enterprise-grade audit decision-support and statistical anomaly triage engine built for the **Lok Sabha 18th Members of Parliament Local Area Development Scheme (MPLADS)** datasets.

The platform assists government auditors, administrative officers, and policy analysts by systematically scrutinizing **79,220 master work projects** and **84,172 raw expenditure vouchers**. It automates the detection of cost anomalies, potential duplicate works, payment structuring patterns, statutory compliance SLA breaches, and vendor concentration risks—aggregating multi-dimensional signals into an actionable, audit-priority queue.

> [!IMPORTANT]
> **Governance & Non-Incriminating Terminology Disclaimer**:
> This platform performs statistical, financial, and timing anomaly triage to prioritize administrative audit reviews. It is **NOT** a criminal or fraud classifier. A `CRITICAL AUDIT PRIORITY` score or `M2 Candidate-Pair Risk Tier` does **NOT** constitute proof of illegal activity, corruption, or favoritism. All flags indicate works requiring administrative audit review under objective governance standards.

---

## Canonical M1–M5 ML Architecture (Verified & Frozen)

The analytical core consists of five verified, non-overlapping production machine learning and audit modules (M1–M5). The canonical architecture is locked and verified against empirical benchmark data:

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

### 1. Model M1 — Cost / Expenditure Anomaly Engine
- **Algorithm**: Unsupervised `IsolationForest` (`n_estimators=300`, `contamination=0.05`, `random_state=42`) combined with hierarchical peer-group robust deviation scaling (IQR and Median Absolute Deviation fallback).
- **8 Production Features**:
  1. `log_sanction`: Log-transformed sanction amount.
  2. `peer_dev`: Ratio deviation from peer group median.
  3. `robust_dev`: Robust z-score normalized by peer IQR / MAD.
  4. `days`: Project sanction-to-completion duration in days.
  5. `num_paym`: Total number of payment vouchers disbursed.
  6. `split_ind`: Payment voucher split ratio indicator.
  7. `zero_days`: Zero-day sanction-to-payment flag.
  8. `last_frac`: Fiscal year-end disbursement fraction.
- **Output**: Flagged **3,961 works** requiring cost audit review out of 79,220 master works.

### 2. Model M2 — Double-Dipping & Duplicate Work Intelligence
- **Algorithm**: Multi-stage candidate blocking followed by TF-IDF Vectorization and Cosine Similarity scoring across Work Title, Description, Executing Vendor, and Location Entities.
- **Output**: Exactly **5,000 candidate pairs** categorized into M2 candidate-pair risk tiers:
  - **High Risk**: 1,997 pairs
  - **Medium Risk**: 2,499 pairs
  - **Low Risk**: 504 pairs
- *Note*: These candidate pairs are flagged for audit review to prevent double-funding and are separate from M5 audit-priority tiers.

### 3. Model M3 — Expenditure / Payment Anomaly Detection
- **Algorithm**: Vectorized payment structuring analysis detecting voucher splitting, sudden payment velocity bursts, fiscal year-end rushes, and vendor clustering across 56,604 unique payment-linked projects.
- **Separate Audit Modules**:
  - **Delay Detection Rules**: Measures sanction SLA breaches (>75 days) and completion delay anomalies.
  - **Statutory Compliance Rules**: Measures regulatory approval compliance, work eligibility, and inadmissible work rules.

### 4. Model M4 — Rolling Expenditure Forecasting
- **Algorithm**: Recursive rolling-mean time-series forecast model predicting 6-month future expenditure trajectories with 95% confidence intervals across categories, states, and parliamentary constituencies.

### 5. Model M5 — Deterministic Audit Priority Aggregator
- **Algorithm**: Multi-dimensional risk matrix aggregating indicators from M1 (Cost Anomaly), M2 (Duplicate Candidate Risk), M3 (Expenditure Structuring), M4 (Forecast Trend), statutory SLA breaches, vendor concentration HHI, inadmissible beneficiary rules, and fund utilization metrics into action-oriented priority tiers.
- **Output**:
  - **CRITICAL Audit Priority**: 1,635 works requiring urgent scrutiny.
  - **HIGH / MEDIUM / LOW Audit Priorities**: Hierarchical queue for administrative audit workflows.

---

## Full-Stack Tech Stack

| Layer | Technologies & Frameworks | Key Architectural Highlights |
|---|---|---|
| **Frontend UI** | Vanilla JavaScript (ES6+), Tailwind CSS, Chart.js, HTML5 | Client-side response caching (`apiCache`), lazy-loaded views, 300ms search input debouncing, zero external build dependencies |
| **Backend REST API** | Python 3.13, Flask, CORS | 25 registered API endpoints, server-side startup in-memory pre-warming cache (`CACHE` dict), sub-5ms response latencies |
| **Machine Learning & Analytics** | Vectorized Pandas, Scikit-Learn, SciPy, NumPy | Isolation Forest, TF-IDF + Cosine Similarity, Vectorized `.groupby().agg()` payment aggregations, Dictionary iteration |
| **Testing & Quality Assurance** | Pytest, Git Diff Check | 149 automated unit and integration tests (**100% pass rate**), zero trailing whitespace violations |

---

## Full-Stack Performance Benchmarks

The entire stack is optimized for execution speed and real-time dashboard responsiveness:

| Component / Endpoint | Baseline | Optimized | Speedup Factor | Performance Status |
|---|---|---|---|---|
| **Backend Startup** | 1.05s | **1.09s** | ~1.0x | Pre-warms in-memory cache at startup |
| **GET /api/summary** | 0.0248s | **0.0131s** | **1.89x** | Cached response |
| **GET /api/works?limit=50** | 0.0573s | **0.0482s** | **1.18x** | Cached response |
| **GET /api/double-dipping** | 0.1082s (uncached) | **0.0014s** (cached) | **77.2x** | Measured sub-5-ms range |
| **GET /api/delayed-projects** | 0.4127s (cold cache) | **0.0019s–0.1988s** (warm cache) | **2.07x–217.2x** | Measured sub-5-ms to warm range |
| **GET /api/compliance** | 0.2776s (uncached) | **0.0021s** (cached) | **132.1x** | Measured sub-5-ms range |
| **GET /api/audit-priority** | 0.0017s (uncached) | **0.0004s** (cached) | **4.25x** | Measured sub-5-ms range |
| **Model 3 Expenditure Aggregation** | 15.38s | **0.84s** | **18.3x** | Vectorized Pandas `.agg()` |
| **Model 5 Audit Priority Aggregator** | 30.55s | **0.42s** | **72.7x** | Fast dictionary iteration |
| **Unified Pipeline Handoff** | ~100.8s | **~47.2s** | **2.13x** | In-memory DataFrame handoffs |
| **Software Test Pass Rate** | 149/149 tests | **149/149 passed** | **100% Pass** | Automated test suite verified |

---

## Frontend Dashboard Views & Navigation

The frontend interface (`frontend/index.html`) is clean, judge-friendly, and focused on key audit insights:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🏛️ MPLADS AUDIT INTELLIGENCE PLATFORM — LOK SABHA 18TH                 │
├─────────────────────────────────────────────────────────────────────────┤
│ [📊 Overview] [🔍 Works] [🚨 Priority Queue] [👯 Duplicates] [📈 Analytics] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │ Total Expenditure│ │ Audit Review Req│ │ Critical Priority│           │
│  │    ₹8,417.2 Cr   │ │   14,210 Works  │ │   1,635 Works   │           │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘           │
│                                                                         │
│  ┌─────────────────────────────────┐ ┌───────────────────────────────┐ │
│  │ Category Expenditure Breakdown  │ │ M5 Audit Priority Distribution│ │
│  │ (Chart.js Bar Visualization)    │ │ (Chart.js Doughnut Chart)     │ │
│  └─────────────────────────────────┘ └───────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Dashboard Sections:

1. **📊 Overview Executive Dashboard**:
   - Displays core KPIs: Total Works (79,220), Total Expenditure, Works Requiring Audit Review, Critical Audit Priority (1,635), Potential Duplicate Candidate Pairs (5,000), Delayed Works, and Fund Utilization.
   - Interactive high-level charts providing instant financial and risk visibility.

2. **🔍 Works Explorer**:
   - Searchable, paginated table of master works with 300ms input debouncing.
   - Category and state filters with instant work detail modal view.

3. **🚨 Priority Audit Queue**:
   - Actionable list of projects categorized by M5 audit priority tiers (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
   - Detailed justification metrics showing exact statutory SLA breaches, cost anomaly scores, and risk factors.

4. **👯 Duplicate Work Intelligence**:
   - Candidate double-dipping pair inspection displaying semantic similarity scores (Cosine Similarity), location overlaps, and vendor comparisons for the 5,000 candidate pairs.

5. **📈 Expenditure & Anomaly Analytics**:
   - Deep statistical analysis of M1 Isolation Forest cost anomalies and M3 payment structuring (voucher splitting and payment velocity bursts).

6. **🔮 Expenditure Forecasting**:
   - Interactive time-series forecast charts predicting 6-month future expenditure trends with 95% confidence bands.

---

## 25 Registered Backend REST API Endpoint Directory

The Flask server (`backend/app.py`) exposes 25 REST API routes:

| Route Path | Method | Purpose | Response Time (Cached) |
|---|---|---|---|
| `/` | GET | System Health Check & Version Info | < 2 ms |
| `/api/summary` | GET | Executive KPIs & Dashboard Statistics | < 5 ms |
| `/api/works` | GET | Paginated Master Sanctioned Works | < 45 ms |
| `/api/work/<work_id>` | GET | Detailed Single Work Audit Record | < 5 ms |
| `/api/double-dipping` | GET | M2 Duplicate Candidate Pairs (5,000 pairs) | < 2 ms |
| `/api/delayed-projects` | GET | SLA Delay Breaches & Project Duration Anomalies | < 2 ms |
| `/api/compliance` | GET | Statutory SLA & Regulatory Compliance Rules | < 3 ms |
| `/api/audit-priority` | GET | M5 Deterministic Audit Priority Rankings | < 1 ms |
| `/api/forecast` | GET | M4 6-Month Expenditure Trajectory Predictions | < 1 ms |
| `/api/vendor-risk` | GET | Vendor Concentration HHI & Agency Network Risk | < 4 ms |
| `/api/inadmissible-works` | GET | Inadmissible Category & Statutory Guideline Rules | < 1 ms |
| `/api/private-beneficiaries` | GET | Private Beneficiary & Non-Public Asset Flags | < 1 ms |
| `/api/duplicate-expenditure` | GET | Duplicate Payment Voucher & Disbursement Flags | < 1 ms |
| `/api/fund-utilization` | GET | State/Constituency Fund Utilization Ratios | < 1 ms |
| `/api/deep-evaluation` | GET | Unified Comprehensive Deep Audit Report | < 5 ms |
| `/api/export/csv` | GET | CSV Export of Scored Audit Records | Download Stream |
| `/api/export/json` | GET | JSON Export of Full Scored Audit Dataset | Download Stream |
| `/api/stats/categories` | GET | Category Breakdown Distribution | < 2 ms |
| `/api/stats/states` | GET | State-level Expenditure & Work Counts | < 2 ms |
| `/api/stats/mps` | GET | Member of Parliament Work Summary Stats | < 3 ms |
| `/api/search` | GET | Fast Keyword Search across Master Works | < 15 ms |
| `/api/audit-rules` | GET | Audit Rule Definitions & Threshold Specs | < 1 ms |
| `/api/model-metadata` | GET | Model M1–M5 Configuration Parameters | < 1 ms |
| `/api/health` | GET | API Backend Health & Cache Status | < 1 ms |
| `/api/version` | GET | API Build Version & Verification Status | < 1 ms |

---

## Repository Directory Structure

```
.
├── backend/                             # Flask REST API Server & Data Handlers
│   ├── app.py                           # 25 REST API Routes with Startup In-Memory Cache
│   ├── canonical_registry.py           # Canonical Model Parameter Registry
│   └── audit_engine/                    # Backend Audit Aggregation Handlers
├── frontend/                            # Apple-Inspired Clean Web Interface
│   ├── index.html                       # Single Page Application Dashboard Layout
│   ├── app.js                           # Client-side Router, apiCache & Debounced Search
│   └── style.css                        # Modern Responsive Stylesheet
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
├── feature_engineering/                 # Data Normalization & 11-Group Taxonomy Classifier
├── data_pipeline/                       # Data Loaders & Master Lifecycle Reconciliation
├── scripts/                             # Verification & Profiling Scripts
│   └── profile_system.py                # System Latency & Performance Benchmark Runner
├── tests/                               # Comprehensive Automated Test Suite (149 tests)
├── docs/                                # Forensic Audit Reports & Documentation
│   ├── SIH26102_SOURCE_OF_TRUTH.md      # Reconciled System Source of Truth
│   ├── SIH26102_PERFORMANCE_AUDIT.md    # Detailed Forensic Performance Audit
│   └── SIH26102_PERFORMANCE_REPORT.md   # Final Performance Benchmarks & Verification
├── data/                                # Original Raw Datasets (Read-Only)
├── output/                              # Generated Scored JSON/CSV Output Artifacts
├── run_pipeline.py                      # Unified ML Audit Pipeline Execution Script
└── README.md                            # Comprehensive System README
```

---

## Installation, Setup & Execution Guide

### Prerequisites
- **Python**: Version 3.10 or higher (Python 3.13 recommended)
- **Pip**: Python package manager
- **Web Browser**: Modern browser (Chrome, Safari, Firefox, Edge)

### 1. Clone the Repository
```bash
git clone https://github.com/Zaid5671/CodeBlooded.git
cd CodeBlooded
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Execute the Full ML & Audit Pipeline
Run the unified 13-step pipeline to load raw datasets, engineer features, run models M1–M5, and generate output JSON files:
```bash
python3 run_pipeline.py
```

### 4. Launch the Backend API Server
Start the Flask backend server on port 5051 with pre-warmed in-memory caching:
```bash
python3 backend/app.py
```

### 5. Access the Frontend Dashboard
Open `frontend/index.html` directly in your web browser, or serve it via local web server:
```bash
# Example using Python HTTP server
python3 -m http.server 8000 --directory frontend
```
Then navigate to `http://localhost:8000` in your web browser.

### 6. Run the Automated Test Suite
Run all 149 automated unit and integration tests:
```bash
python3 -m pytest tests/ -v
```

---

## Verification & Architecture Freeze Statement

- **M1–M5 ML Architecture**: Fully verified against canonical baseline outputs and frozen.
- **Data Integrity**: Tested on 79,220 master sanctioned works and 84,172 payment vouchers. Zero synthetic data in production data paths.
- **Test Pass Rate**: **149/149 automated tests passed (100% pass rate)**.
- **Git Code Cleanliness**: Passed `git diff --check` with 0 trailing whitespace violations.

---

## Team & Project Information

- **Problem Statement**: SIH26102 — AI-Powered MPLADS Audit Intelligence Platform
- **Team Name**: CodeBlooded
- **Repository**: [https://github.com/Zaid5671/CodeBlooded](https://github.com/Zaid5671/CodeBlooded)