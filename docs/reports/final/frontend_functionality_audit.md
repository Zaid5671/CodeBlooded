# Frontend Functionality Audit Report (`SIH26102`)

## 1. System Architecture & Component Mapping

```
frontend/
├── index.html       # Single Page Application HTML5 structure (12 Views, Modals & Drawers)
├── style.css        # Neubrutalist Lime Green CSS System (Dual Light/Dark Mode)
└── app.js           # Production JavaScript Engine (API Fetcher, Real-Time Dynamic Sorting, Dynamic Dataset Switcher, Plotly Visualizations)
```

## 2. Pages & Views Implemented

| # | View Name | Route / Hash | Dynamic Data | Status |
|---|---|---|---|---|
| 1 | Overview / Command Center | `#overview` | Live Backend KPI API | PASS |
| 2 | Works Inventory Explorer | `#works` | Dynamic Search & Pagination (79,220 works) | PASS |
| 3 | Audit Priority Queue | `#priority` | Multi-Dimensional Risk Triage | PASS |
| 4 | Alert Center | `#alerts` | Category Filters & Review Persistence | PASS |
| 5 | Expenditure Intelligence | `#expenditure` | Disbursement Velocity Timeline | PASS |
| 6 | Statutory SLA Review | `#compliance` | 45-Day SLA Benchmark Breakdown | PASS |
| 7 | Duplicate Works (Record Linkage) | `#duplicates` | Text Cosine & Parity Comparison | PASS |
| 8 | Expenditure Outlook & Forecast | `#forecast` | 6-Month Rolling Outlay Projection | PASS |
| 9 | Agency & Vendor Risk | `#agencies` | HHI Concentration Metrics | PASS |
| 10 | Consolidated Risk Analytics | `#analytics` | Outlay vs Risk Scatter Engine | PASS |
| 11 | AI & Methodology Governance | `#methodology` | Models M1–M5 Specifications | PASS |
| 12 | Audit Reports & Verification Documents | `#reports` | Interactive Markdown Viewer API | PASS |

## 3. Dynamic Interactive Features Verified

1. **Header Dataset Selector**:
   - Dynamic dataset switching (`Lok Sabha 18`, `Lok Sabha 17`, `Rajya Sabha`, `Combined`).
   - Refetches all API endpoints with `?dataset=...` and updates KPIs, tables, and Plotly charts in real time.
2. **Table Header Column Sorting**:
   - `data-sort-col` bound to all `<th>` headers in `tbl-works`, `tbl-priority`, and `tbl-duplicates`.
   - Supports ascending/descending dynamic sorting with visual caret indicators (`▲`/`▼`).
3. **Global Filter System**:
   - Filters State, District, Category, and Priority Tiers across all 12 views in real time.
4. **Modals & Drawers**:
   - Spotlight Search (`Cmd+K` / `Ctrl+K`).
   - Work Investigation Drawer with live signal analysis.
   - Side-by-Side Duplicate Comparison Modal.
   - WhatsApp Notification Dispatcher (`POST /api/notifications/dispatch`).
   - Report Viewer (`GET /api/export-reports?file=...`).

## 4. Test Suite & Verification Results

- **Python Syntax & Bytecode**: 0 compilation errors (`python3 -m compileall backend/ audit_rules/`).
- **Pytest Automated Tests**: 136/136 unit tests passing (`python3 -m pytest tests/`).
- **Backend HTTP Server**: 200 OK on `http://127.0.0.1:5052/`.

```
======================== 136 passed in 75.37s (0:01:15) ========================
```
