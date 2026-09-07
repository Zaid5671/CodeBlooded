# Temporary Demo Backend (Flask REST API)

This is a temporary demonstration backend serving REST API endpoints for the **Anomalous Cost Estimate & Cost Overrun Detection Engine**.

## 📌 Data Source
It reads pre-computed ML outputs dynamically from `../../output/`:
- `pipeline_summary.json`
- `validation_results.json`
- `model_config.json`
- `scored_sanctioned_works.json` (or `.json.gz`)

It does NOT retrain the model or modify raw CSV files.

## 🚀 Running the Backend
From the project root:
```bash
python3 temp_demo/backend/app.py
```
Or with venv:
```bash
python3 -m venv temp_demo/.venv
source temp_demo/.venv/bin/activate
pip install -r temp_demo/requirements.txt
python3 temp_demo/backend/app.py
```

## 📡 API Endpoints
- `GET /api/summary`: Top-level summary KPIs (79,220 works, 2,849 HIGH, 1,924 MEDIUM, 74,443 LOW).
- `GET /api/works`: Paginated & filterable list of projects (`?page=1&limit=50&risk=HIGH&state=...&search=...`).
- `GET /api/works/<work_id>`: Detailed record and evidence list for a specific project ID.
- `GET /api/top-anomalies`: Top 20 highest risk/anomaly score projects.
- `GET /api/signals`: Signal statistics and overlap metrics.
- `GET /api/validation`: 80/20 train/test split stability and 5-seed cross-validation metrics.
