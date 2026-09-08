# 02. Technical Requirements Document (TRD)
> **MPLADS Audit Intelligence Platform — SIH 2026 (Problem Statement SIH26102)**  
> *The Blueprint: Architecture, tech stack, API specifications, and technical constraints.*

---

## 1. System Architecture & Tech Stack

| Layer | Technology Choice | Rationale |
|---|---|---|
| **Frontend UI** | HTML5, Vanilla JS (ES6+), CSS3 (Custom Variables) | Zero external bundler overhead, high performance, instant cold start. |
| **Design System** | Positivus Neubrutalist Lime Green System (`#b9fd50`) | High-contrast government intelligence aesthetic inspired by macOS Tahoe. |
| **Data Visualization** | Plotly.js (`v2.24.1`) | High-performance interactive charts (Bar, Donut, Timeline, Scatter, Forecast). |
| **Backend Runtime** | Python 3.13 / Flask REST Server (`backend/app.py`) | Lightweight, native ML model integration, zero-dependency REST endpoints. |
| **ML & Data Engine** | `scikit-learn` (IsolationForest), `numpy`, `pandas` | Unsupervised anomaly detection, IQR baselines, TF-IDF cosine linkage. |
| **Data Storage** | Gzip JSON (`scored_sanctioned_works.json.gz`), Pre-computed Cache | Ultra-fast memory caching (<10ms lookup) for 79,220 master work entities. |

---

## 2. API Endpoint Specifications

### Core Data Endpoints
- `GET /api/summary?dataset={corpus}`: Returns top-level KPI metrics (Total Outlay, Critical Count, Cost Overruns, Duplicates).
- `GET /api/works?limit=500&dataset={corpus}&state={state}&search={query}`: Returns paginated, searchable master work records.
- `GET /api/works/<work_id>`: Returns full single project audit details.
- `GET /api/audit-priority?dataset={corpus}`: Returns Model M5 unified priority queue items.
- `GET /api/double-dipping?dataset={corpus}`: Returns Model M2 record linkage duplicate work pairs.
- `GET /api/compliance?dataset={corpus}`: Returns Model M3 45-day statutory SLA review metrics.
- `GET /api/forecast?dataset={corpus}`: Returns Model M4 6-month rolling expenditure forecast records.
- `GET /api/vendor-risk?dataset={corpus}`: Returns implementing agency HHI concentration risk scores.
- `POST /api/notifications/dispatch`: Generates WhatsApp Business and Webhook alert payloads.
- `GET /api/export-reports?file={filepath}`: Serves system verification markdown reports.

---

## 3. Environment Variables & Configuration

```ini
PORT=5052
FLASK_ENV=production
DATASET_DIR=output/
WHATSAPP_WEBHOOK_URL=https://api.whatsapp.com/v1/messages
ENABLE_OFFLINE_DEMO_MODE=true
```

---

## 4. Key Libraries & Dependencies

- **Python**: `flask`, `scikit-learn`, `numpy`, `pandas`, `pytest`, `compileall`
- **Frontend CDN**: `plotly.js-dist@2.24.1`, `font-awesome@6.4.2`, Google Fonts (`Space Grotesk`, `Plus Jakarta Sans`, `Fira Code`)

---

## 5. Technical Constraints

- **Zero Cloud Runtime Lock-In**: Must execute 100% offline without mandatory external cloud API calls for SIH live judging.
- **Strict Null Safety**: Missing values must render as `"Data unavailable in source record"` instead of fabricating `0` or fake fraud labels.
- **Memory Footprint**: Total backend RAM consumption must remain <500MB.
