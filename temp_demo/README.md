# Temporary Demonstration Dashboard (SIH 2026 PS 102)

This directory contains a **temporary, self-contained full-stack demonstration dashboard** for showcasing the **Anomalous Cost Estimate & Cost Overrun Detection Engine** (Lok Sabha 18th MPLADS) to judges and stakeholders.

---

## 📌 Architecture & Design Principles

* **Unsupervised Anomaly Detection**: Operates without ground-truth fraud labels. Uses terminology *"Anomalous / Requires Investigation"* instead of confirmed fraud.
* **Non-Invasive Prototype**: Completely isolated inside `temp_demo/`. Does **NOT** modify or retrain existing production code (`cost_detection/`, `run_pipeline.py`, `dashboard.py`, `output/`).
* **Real Dataset Integration**: Reads pre-computed ML outputs dynamically from `output/pipeline_summary.json`, `output/validation_results.json`, and `output/scored_sanctioned_works.json`.

---

## 🚀 How to Run the Temporary Application

### Step 1: Create virtual environment & install requirements
From the project root directory (`SIH PROJECT FILES`):
```bash
python3 -m venv temp_demo/.venv
source temp_demo/.venv/bin/activate
pip install -r temp_demo/requirements.txt
```

### Step 2: Launch the Flask Backend
```bash
python3 temp_demo/backend/app.py
```

### Step 3: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📡 REST API Endpoints

- `GET /api/summary`: Top-level summary KPIs (79,220 works, 2,849 HIGH, 1,924 MEDIUM, 74,443 LOW).
- `GET /api/works`: Paginated, searchable, filterable project records (`?page=1&limit=50&risk=HIGH&state=...&search=...`).
- `GET /api/works/<work_id>`: Complete details and evidence for a specific project ID.
- `GET /api/top-anomalies`: Returns top 20 highest risk/anomaly score projects.
- `GET /api/signals`: Signal statistics and overlap metrics.
- `GET /api/validation`: 80/20 out-of-sample train-test split stability and 5-seed cross-validation metrics.

---

## 💡 How the Model Detects Anomalies (3 Independent Signals)

1. **Signal 1 — Cost Overrun Rule**: Checks whether actual expenditure exceeds sanctioned budget by > 10%.
2. **Signal 2 — Deterministic Peer IQR**: Compares project sanction amount against State peer median. Flagged if robust deviation > 3.0 IQRs.
3. **Signal 3 — Isolation Forest ML**: Multivariate unsupervised anomaly detection (`n_estimators=300`, `contamination=0.05`, `random_state=42`) using sanction amount, peer ratios, IQR deviation, timeline, and log scale.

### Consensus Risk Classification
- **Signals ≥ 2** $\rightarrow$ 🚨 **HIGH Risk**
- **Signals == 1** $\rightarrow$ ⚠️ **MEDIUM Risk**
- **Signals == 0** $\rightarrow$ ✅ **LOW Risk / Normal**
- **Sanction < ₹1,000** $\rightarrow$ 🔍 **DATA_QUALITY_REVIEW**

---

## ⚠️ Why Supervised Accuracy is Not Reported
Supervised classification accuracy (e.g. 95% accuracy) is not reported because official government datasets do not contain verified historical fraud ground-truth labels. Inventing labels would introduce false confidence. The engine is evaluated using **out-of-sample stability (0.11% train/test delta), score percentile consistency, and signal Jaccard overlap (0.5969)**.

---

## 🗑️ How to Remove the Temporary Demo
To remove the temporary demo without affecting the production code:
```bash
rm -rf temp_demo
```
