# SIH 2026 — SIH26102 — Demonstration Guide

This directory contains demonstration guidelines and presentation references for the **AI-Powered MPLADS Audit Intelligence Platform** (SIH 2026 Problem Statement SIH26102).

---

## 🚀 How to Run the Demonstration

### 1. Launch Backend API Server
From the root repository directory:
```bash
PORT=5051 PYTHONPATH=. python3 backend/app.py
```
Backend API will run at: `http://localhost:5051`

### 2. Launch Static Dashboard Server (Optional)
```bash
python3 -m http.server 8000 --directory output
```
Frontend standalone HTML dashboard will run at: `http://localhost:8000/dashboard.html`

---

## 📋 Judge / Reviewer Demonstration Flow

1. **Overview / Command Center**:
   - Open `http://localhost:8000/dashboard.html`
   - Review top-level KPI cards (Total Works, Critical Audit Priority, Potential Anomalies, Potential Duplicates)
   - Toggle dataset selector (`LokSabha18`, `LokSabha17`, `RajyaSabha_Sitting`, `RajyaSabha_Retired`) to demonstrate multi-corpus dynamic switching.

2. **Works Inventory Explorer**:
   - Filter by State / Risk Level or Search by MP name / Work ID.
   - Click any work row to slide open the **Work Detail Drawer** displaying raw metadata, financial breakdown, and model explanation evidence.

3. **Audit Priority Queue (Model 5)**:
   - Inspect multi-signal audit triage score (0–100) and priority tiers (`CRITICAL AUDIT PRIORITY`, `STANDARD REVIEW`, `LOW PRIORITY`).

4. **Multi-Dimensional Anomaly Explorer (Model 1)**:
   - View M1 Isolation Forest multivariate ML anomaly score distribution and peer-relative cost deviation.

5. **Potential Duplicate Works (Model 2)**:
   - View candidate duplicate work pairs generated via Geographic Candidate Blocking + Cosine Text Similarity.
   - Click any pair to view side-by-side work comparison.

6. **Expenditure Intelligence & Forecasting (Models 3 & 4)**:
   - View voucher disbursement velocity, tranche structure, and 6-month empirical rolling average forecast with confidence bounds.

7. **Vendor Risk & Compliance**:
   - View Herfindahl-Hirschman Index (HHI) concentration analytics, government entity safeguards, and statutory recommendation-to-sanction approval timeline gaps.

8. **Model Integrity & Methodology Audit**:
   - Inspect 80/20 train/test split stability metrics, Jaccard overlap, and methodology governance standards.

---

## 🛡️ Governance & Terminology Safeguards

- **Unsupervised Anomaly Triage**: Operates without ground-truth fraud labels.
- **Approved Terminology**: Uses *"Potential Anomaly"*, *"Potential Duplicate"*, *"Requires Audit Review"* — strictly avoids "fraud confirmed" or "corruption detected".
