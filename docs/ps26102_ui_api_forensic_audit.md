# SIH26102 UI / API Forensic Audit Report

**Project**: AI-Powered MPLADS Audit Intelligence Platform  
**Team**: CodeBlooded  
**Problem Statement ID**: SIH26102  

---

## A. Verdict

> [!CAUTION]
> **UI / API FORENSIC VERDICT**: The UI/API feature claims in Section E of previous reports contained multiple unsupported assertions. Server-enforced RBAC, Leaflet GIS choropleth maps, Natural Language SQL translation in M5, dynamic PDF/CSV dossier generators, and `tests/test_backend.py` **DO NOT EXIST** in the production codebase.
>
> All UI and API claims are hereby reconciled to reflect exact source code implementations.

---

## B. Four-Role Access Verification

- **Implementation**: `frontend/app.js` (`state.currentRole`), `frontend/index.html` (login modal `#login-role` & header dropdown `#header-role-selector`).
- **Server-Side Enforcement**: `backend/app.py` has **NO authentication, sessions, or authorization checks**, and **NO `/api/user/role` endpoint**.
- **Classification**: **DEMO/CONTEXT SWITCH ONLY**.

---

## C. GIS / Geo-Spatial Verification

- **Code Inspection**: No Leaflet, Mapbox, GeoJSON, or SVG map libraries are imported in `frontend/` or `backend/`.
- **Backend Endpoint**: `/api/geo-spatial` **DOES NOT EXIST** in `backend/app.py`.
- **UI State**: Geographic filters exist as HTML `<select>` dropdowns for State and District.
- **Classification**: **NOT FOUND / DOCUMENTATION ONLY**.

---

## D. Natural Language Query Verification

- **Implementation**: Endpoint `/api/query` in `backend/app.py`.
- **Engine Logic**: Performs simple word-level substring matching across concatenated work fields (`f"{work_id} {work_name} {State} {District} {Constituency} {standardized_category} {audit_priority_tier}".lower()`).
- **SQL / M5 Integration**: Does NOT generate SQL and is NOT part of Model 5 (M5 is Audit Priority Aggregator).
- **Classification**: **IMPLEMENTED (SIMPLE KEYWORD MATCHING) + UNTESTED**.

---

## E. PDF / CSV Export Verification

- **Endpoints**: `/api/reports/pdf` and `/api/reports/csv` **DO NOT EXIST**.
- **Existing Endpoint**: `/api/export-reports` in `backend/app.py` serves static markdown files (e.g. `reports/final/final_system_verification.md`), NOT dynamic PDF or CSV files.
- **Test File**: `tests/test_backend.py` **DOES NOT EXIST**.
- **Classification**: **NOT FOUND / STUB (MARKDOWN FILE SERVER ONLY)**.

---

## F. Frontend UI Verification

- **Visual Styling**: `frontend/style.css` implements modern glassmorphism UI tokens (`backdrop-filter: blur(12px)`, translucent card backgrounds, dark mode toggle).
- **Dashboard Structure**: Navigation tabs for Overview, Works, Priority, Duplicates, Analytics, Forecast.
- **Classification**: **IMPLEMENTED + VISUALLY VERIFIED**.

---

## G. Complete API Route Inventory

| Endpoint Route | Method | Exists in `backend/app.py` | Actual Functionality |
|---|---|---|---|
| `/api/corpora` | GET | **YES** | Returns available corpus metadata. |
| `/api/summary` | GET | **YES** | Returns aggregate dataset summary statistics. |
| `/api/validation` | GET | **YES** | Returns system data quality validation checks. |
| `/api/signals` | GET | **YES** | Returns audit signal statistics. |
| `/api/works` | GET | **YES** | Returns paginated master work records with search/filter. |
| `/api/works/<work_id>` | GET | **YES** | Returns deep-dive details for a single work entity. |
| `/api/top-anomalies` | GET | **YES** | Returns top M1 cost anomaly records. |
| `/api/double-dipping` | GET | **YES** | Returns M2 duplicate work candidate pairs. |
| `/api/delayed-projects` | GET | **YES** | Returns delayed project records and SLA breach checks. |
| `/api/compliance` | GET | **YES** | Returns statutory compliance adherence metrics. |
| `/api/ia-watchlist` | GET | **YES** | Returns implementing agency risk metrics. |
| `/api/audit-priority` | GET | **YES** | Returns M5 audit priority score aggregation. |
| `/api/forecast` | GET | **YES** | Returns M4 rolling average expenditure projections. |
| `/api/vendor-risk` | GET | **YES** | Returns vendor risk network analytics. |
| `/api/inadmissible-works` | GET | **YES** | Returns inadmissible work rule evaluation. |
| `/api/private-beneficiaries` | GET | **YES** | Returns private beneficiary rule evaluation. |
| `/api/duplicate-expenditure` | GET | **YES** | Returns transaction-level payment anomaly analysis. |
| `/api/fund-utilization` | GET | **YES** | Returns idle fund utilization metrics. |
| `/api/deep-evaluation` | GET | **YES** | Returns deep evaluation model diagnostics. |
| `/api/canonical-registry` | GET | **YES** | Returns canonical model registry definitions. |
| `/api/query` | GET, POST | **YES** | Basic substring keyword query parser. |
| `/api/agents/triage` | GET, POST | **YES** | Multi-agent consensus triage simulation. |
| `/api/notifications/dispatch` | POST | **YES** | Dispatches alert notifications. |
| `/api/export-reports` | GET | **YES** | Serves static markdown audit reports. |
| `/` | GET | **YES** | Serves frontend static application index. |
| `/api/models/m1/evaluate` | POST | **NO** | Endpoint does not exist in `backend/app.py`. |
| `/api/models/m2/evaluate` | POST | **NO** | Endpoint does not exist in `backend/app.py`. |
| `/api/models/m3/evaluate` | POST | **NO** | Endpoint does not exist in `backend/app.py`. |
| `/api/models/m4/evaluate` | POST | **NO** | Endpoint does not exist in `backend/app.py`. |
| `/api/non-compliance` | GET | **NO** | Endpoint route is `/api/compliance`. |
| `/api/cost-anomalies` | GET | **NO** | Endpoint route is `/api/top-anomalies`. |
| `/api/delay-bottlenecks` | GET | **NO** | Endpoint route is `/api/delayed-projects`. |
| `/api/geo-spatial` | GET | **NO** | Endpoint does not exist in `backend/app.py`. |
| `/api/reports/pdf` | GET | **NO** | Endpoint does not exist in `backend/app.py`. |
| `/api/reports/csv` | GET | **NO** | Endpoint does not exist in `backend/app.py`. |
| `/api/user/role` | GET | **NO** | Endpoint does not exist in `backend/app.py`. |

---

## H. Test Coverage Matrix

| Feature Area | Production Code File | Test Suite Coverage | Classification |
|---|---|---|---|
| **M1 Cost Anomaly** | `ml/model_1_cost_anomaly/isolation_forest.py` | `tests/test_final_integrity.py` | IMPLEMENTED + TESTED |
| **M2 Duplicate Work** | `ml/model_2_duplicate_work/double_dipping.py` | `tests/test_double_dipping.py` | IMPLEMENTED + TESTED |
| **M3 Payment Anomaly** | `ml/model_3_expenditure_anomaly/duplicate_expenditure.py` | `tests/test_new_modules.py` | IMPLEMENTED + TESTED |
| **M4 Expenditure Forecast** | `ml/model_4_forecasting/expenditure_forecast.py` | `tests/test_cross_house_and_forecast.py` | IMPLEMENTED + TESTED |
| **M5 Audit Priority** | `ml/model_5_audit_priority/misuse_priority.py` | `tests/test_models_3_4_5.py` | IMPLEMENTED + TESTED |
| **4-Role Access Switcher** | `frontend/app.js` | None in `tests/` | DEMO/CONTEXT SWITCH ONLY |
| **GIS Geo Map View** | None | None | NOT FOUND |
| **Natural Language Query** | `backend/app.py` (`/api/query`) | None | IMPLEMENTED + NOT TESTED |
| **PDF / CSV Export** | None (`/api/export-reports` serves MD) | None (`test_backend.py` does not exist) | NOT FOUND |

---

## I. M2 Candidate Count Reconciliation

- **Canonical File**: `output/double_dipping_results.json`
- **Total Candidates**: **5,000 candidate pairs**
- **Risk Tier Breakdown**:
  - **HIGH RISK — REQUIRES AUDIT REVIEW**: **1,997 pairs**
  - **MEDIUM RISK**: **2,499 pairs**
  - **LOW RISK**: **504 pairs**

---

## J. Unsupported Claims & Corrections

1. **Server-Enforced 4-Role RBAC**: Corrected to **Demo Context Switcher**.
2. **GIS Leaflet Choropleth Map**: Corrected to **Not Found / State & District Dropdown Filters Only**.
3. **Natural Language SQL Translation**: Corrected to **Basic Substring Keyword Matcher (`/api/query`)**.
4. **Dynamic PDF & CSV Generators**: Corrected to **Static Markdown File Server (`/api/export-reports`)**.
5. **`tests/test_backend.py`**: Corrected to **Does Not Exist**.
6. **M2 3,090 Pairs Claim**: Corrected to **5,000 Candidate Pairs (1,997 High / 2,499 Medium / 504 Low)**.
