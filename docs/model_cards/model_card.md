# Model Card: Anomalous Cost Estimate & Cost Overrun Detection Engine

## 📌 Model Overview
* **Model Name**: `Anomalous Cost Estimate & Cost Overrun Detection Engine`
* **Version**: `1.0.0`
* **Target Domain**: SIH 2026 Problem Statement 102 (MPLADS - Lok Sabha 18th)
* **Primary Task**: Multi-signal statistical and financial anomaly detection on sanctioned public works estimates.
* **Scope**: Lok Sabha 18th ONLY (`/data/original/LokSabha18`). Excludes Lok Sabha 17th and Rajya Sabha datasets.

---

## 🎯 Purpose & Design Principles
This engine detects **unusual cost estimates, high peer-group variance, and actual expenditure overruns** that require human administrative review and physical verification.

> [!IMPORTANT]
> **Not a Fraud Predictor**: This model does NOT predict or classify fraud. It detects statistical and financial anomalies for human investigation. HIGH risk means multiple statistical signals triggered, not proof of wrongdoing.

---

## 🏗️ Architecture & Signal Breakdown

The system integrates **three independent signals** combined through an explainable consensus engine:

```
                    Sanctioned Works (79,220 Records)
                                  │
                                  ▼
                    Data Quality Floor Check (₹1,000)
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
          Sanction < ₹1,000              Sanction >= ₹1,000
                   │                             │
                   ▼                             ▼
         DATA_QUALITY_REVIEW            Multi-Signal Detection
                                                 │
            ┌────────────────────────────────────┼────────────────────────────────────┐
            │                                    │                                    │
            ▼                                    ▼                                    ▼
    SIGNAL 1: COST OVERRUN             SIGNAL 2: PEER IQR                  SIGNAL 3: ISOLATION FOREST
    Deterministic Rule                 Robust Peer Statistics               Multivariate ML Anomaly
    Actual > Sanctioned + 10%          Robust Dev > 3.0 (High side)        n_estimators=300, contamination=0.05
            │                                    │                                    │
            └────────────────────────────────────┼────────────────────────────────────┘
                                                 │
                                                 ▼
                                          CONSENSUS ENGINE
                                  Signals >= 2  ──>  HIGH
                                  Signals == 1  ──>  MEDIUM
                                  Signals == 0  ──>  LOW
```

---

## 📊 Features & Model Specification

### Signal 1: Cost Overrun Rule Engine
* **Formula**: `cost_variance_ratio = (actual_expenditure - sanctioned_amount) / sanctioned_amount`
* **Threshold**: Default 10% (`actual_expenditure > sanctioned_amount * 1.10`).
* **Expenditure Matching**: Primary key `work_id` derived from raw work header string.

### Signal 2: Deterministic Peer IQR Detector
* **Grouping Variable**: `State` (Primary). Min size = 20 works.
* **Fallback**: National peer statistics when state count < 20 (`peer_level = "NATIONAL"`).
* **Formula**: `robust_deviation = (sanction_amount - peer_median) / IQR`
* **Flag**: `robust_deviation > 3.0` (High-side anomalies only).
* **Protection**: If `IQR == 0` or null, robust deviation is set to null to prevent division by zero.

### Signal 3: Isolation Forest ML Detector
* **Algorithm**: `sklearn.ensemble.IsolationForest`
* **Configuration**: `n_estimators=300`, `contamination=0.05`, `random_state=42`
* **Features Used**:
  1. `sanction_amount` (INR)
  2. `peer_deviation_ratio` = `(sanction_amount - peer_median) / peer_median`
  3. `robust_deviation` = `(sanction_amount - peer_median) / IQR`
  4. `rec_to_sanc_days` = `sanction_date - recommended_date`
  5. `log_sanction_amount` = `log1p(sanction_amount)`
* **Excluded Features**: Identifiers (MP name, Work ID, Constituency, Vendor Name, raw text).

---

## ⚠️ Data Quality Floor & Missing Expenditure Handling

1. **₹1,000 Minimum Floor**: Works with `sanction_amount < ₹1,000` (e.g. ₹2.46, ₹3.50) bypass normal ML scoring and are flagged as `DATA_QUALITY_REVIEW` with `data_quality_flag = "IMPLAUSIBLE_SANCTION_AMOUNT"`.
2. **Missing Expenditure**: Works without expenditure records are flagged as `cost_variance_status = "NO_EXPENDITURE_RECORD_YET"` with evidence `"MISSING EVIDENCE: no expenditure record found yet for this work."` Missing expenditure indicates ongoing work, not an anomaly.

---

## 📜 Disclaimer
> Statistical/financial anomaly requiring human investigation. Not proof of fraud or wrongdoing.
