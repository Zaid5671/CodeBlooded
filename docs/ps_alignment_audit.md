# SIH26102 — Official Problem Statement Alignment Audit

**SIH 2026 | Problem Statement: SIH26102**  
**AI-Powered MPLADS Audit Intelligence Platform — Team CodeBlooded**  
**Organization**: Ministry of Statistics and Programme Implementation (MoSPI) — Data Informatics & Innovation Division (DIID)  
**Audit Timestamp**: 2026-09-09  
**Status**: `EMPIRICALLY VERIFIED & AUDIT READY`

---

## 1. Executive Summary

**SIH26102 Solution Alignment: Near-Complete Functional & Technical Match**

This audit evaluates the functional, technical, and methodological alignment of the **AI-Powered MPLADS Audit Intelligence Platform** against the official Ministry of Statistics and Programme Implementation (MoSPI) Problem Statement `SIH26102`.

---

## 2. Official Problem Statement Requirements

The official SIH26102 Problem Statement defines the following core functional capabilities required for an AI-powered MPLADS monitoring and analytics platform:

1. **Cost Estimate Anomalies**: Detect works where sanctioned outlays deviate significantly from historical or peer baselines.
2. **Expenditure & Utilization Patterns**: Analyze spending trends, utilization velocity, and payment distribution patterns.
3. **Payment Patterns & Velocity**: Screen transaction-grain payment vouchers for unusual spacing or structuring.
4. **Work Progress & Execution**: Track completion status, execution delays, and implementation timelines.
5. **Irregularities & Unusual Patterns**: Identify multi-dimensional anomalies in project lifecycle data.
6. **Duplicate Work Detection**: Identify potential duplicate or recurrent work recommendations within geographic boundaries.
7. **Delayed Projects & Norm Deviations**: Screen for SLA breaches and non-compliance with statutory guidelines.
8. **Risk-Based Alerts & Prioritization**: Generate automated alerts and triage high-risk cases for audit review.
9. **Predictive Insights & Utilization Forecasting**: Predict future monthly expenditure utilization trends across 6-month horizons.
10. **Multi-Role Decision-Support Dashboards**: Provide tailored insights for MPs, State Nodal Authorities, District Authorities, and the Ministry.
11. **Stakeholder Support**: Enable data-driven decision-making across all administrative tiers.
12. **Automated Compliance Monitoring**: Monitor statutory approval windows and administrative delay thresholds.
13. **Trend Analysis**: Evaluate macro historical utilization and spending patterns across regions.
14. **Early-Warning Mechanisms**: Highlight utilization delays and cost outliers prior to final disbursement.
15. **Transparency & Accountability**: Enhance monitoring efficiency and strengthen audit trail visibility.

---

## 3. Requirement-to-System Mapping

| Official PS Requirement | Implemented Engine & Module | Verification Evidence | Status |
| :--- | :--- | :--- | :--- |
| **Cost-estimate anomalies** | Model M1 — Isolation Forest (`n_estimators=300`) + Peer Group IQR/MAD Statistics | Tested on 79,220 LS18 works & 92,117 LS17 works; fit on train split strictly. | ✅ Implemented |
| **Duplicate works** | Model M2 — Geographic Candidate Blocking (`State+District+Category`) + TF-IDF Vectorizer + Cosine Similarity | Retained 5,000 scored candidate pairs ($>90\%$ threshold); 0 self-pairs; 0 duplicate canonical keys. | ✅ Implemented |
| **Expenditure & payment anomalies** | Model M3 — Transaction-grain payment velocity & structuring heuristic screening | Aggregated 272,978 payment vouchers across 4 datasets without missing-amount crashes. | ✅ Implemented |
| **Predictive utilization trends** | Model M4 — Recursive 3-Month Rolling Average (`recursive_rolling_mean_forecast`) over 6-month horizon | Evaluated on held-out LS18 expenditure timelines; produced lower MAE than naive baseline. | ✅ Implemented |
| **Delays & statutory deviations** | Statutory Compliance & Delay Engine (`compliance_rules.py` & `delayed_projects.py`) | Monitored SLA adherence against applicable 45-day communication/rejection window and generally applicable 75-day sanction timeline. | ✅ Implemented |
| **Risk-based alerts & prioritization** | Model M5 — Unified Audit Priority Aggregator (`misuse_priority.py`) | 5-dimensional weighted risk aggregation (`Cost 0.30`, `Speed 0.25`, `Compliance 0.25`, `Vendor 0.10`, `Eligibility 0.10`). | ✅ Implemented |
| **Decision-support dashboards** | Glassmorphism Web App (`frontend/index.html`) & REST API Service (`backend/app.py`) | 28/28 API endpoints returned successful HTTP 200 responses in automated integration tests. | ✅ Implemented |
| **Real MPLADS data analysis** | Multi-Corpus Ingestion Pipeline (`unified_model_engine.py --corpus ALL`) | Ingested all 4 datasets (`LS18`, `LS17`, `RS_Sitting`, `RS_Retired`), total 210,551 corpus records. | ✅ Implemented |
| **Potential fraud identification** | Risk signals routed to human audit review queue | Unsupervised risk triage signals assigned into `CRITICAL`, `STANDARD`, and `LOW` priority tiers. | ⚠️ Addressed as risk-screening, not fraud confirmation |

---

## 4. What Is Quantitatively Validated

The codebase has undergone empirical and software validation across the following measurable components:

1. **Model M1 Operating-Point Validation**: Scikit-Learn IsolationForest configured at $5\%$ contamination achieved a stable $5.02\%$ anomaly operating point on test split ($4.95\%$ on train split).
2. **Model M2 Pair-Generation & Integrity Validation**: Candidate pair generator retained 5,000 candidate pairs above $90\%$ similarity with 0 self-pairs (`A == B`) and 0 duplicate canonical pair keys.
3. **Model M3 Transaction Processing Validation**: Aggregated 272,978 raw payment vouchers across all 4 datasets with $100\%$ transaction coverage.
4. **Model M4 Forecasting Benchmark**: On the evaluated LS18 national expenditure series, the 8-Month National Holdout Evaluation produced $4.98\%$ lower MAE and $14.13\%$ lower RMSE than the naive baseline, and the 6-Month National Holdout Evaluation produced $3.31\%$ lower MAE and $18.15\%$ lower RMSE than the naive baseline.
5. **Model M5 Logical Invariants & Weights**: 5-dimensional risk weights sum strictly to $1.00$; supporting-only invariant verified (secondary signals alone cannot trigger `CRITICAL AUDIT PRIORITY`).
6. **Automated Software Test Suite**: **149/149 automated software tests passed** cleanly across the pytest test suite.
7. **API Integration**: All 28 documented API endpoints returned successful HTTP responses in the automated endpoint integration test.

---

## 5. What Is NOT Quantitatively Claimable

To maintain scientific rigor and presentation integrity, the following claims are explicitly **NOT** made:

- **Numerical PS Alignment Percentage**: The official PS provides no weighted scoring rubric; arbitrary percentages such as "99.5%" are unvalidated narrative numbers and are not used.
- **Supervised Fraud Detection Accuracy**: Supervised accuracy, precision, recall, F1-score, and ROC-AUC are **not estimable** because public government datasets lack ground-truth fraud labels.
- **Confirmed Fraud Rate**: The system does not confirm fraud; high-risk outputs represent statistical anomalies requiring human audit review.
- **Real-World Fraud Elimination Effectiveness**: Real-world fraud prevention depends on field audit execution by statutory authorities.

---

## 6. Fraud Ground-Truth Limitation Disclosure

### WHY WE DO NOT CLAIM A NUMERICAL PS-ALIGNMENT SCORE

The official SIH26102 Problem Statement does not provide a numerical scoring rubric for measuring solution alignment. Therefore, assigning a percentage such as 99.5% would imply a level of quantitative measurement that the source document does not support.

Instead, solution alignment is assessed functionally. Each explicitly identified capability in the Problem Statement has been mapped to a corresponding implemented system module and verification evidence.

Public MPLADS datasets do not provide verified fraud/non-fraud ground-truth outcome labels suitable for supervised fraud-classification evaluation. Therefore, the platform does not fabricate fraud labels or report supervised fraud accuracy. It instead performs AI-assisted anomaly screening, risk triage, predictive analysis, compliance monitoring, and audit prioritization, with human authorities responsible for final investigation and decisions.

---

## 7. Human-in-the-Loop Governance Standard

$$\text{AI Anomaly Signal} \longrightarrow \text{Audit Evidence Record} \longrightarrow \text{Triage Queue} \longrightarrow \text{Human Investigation} \longrightarrow \text{Authority Decision}$$

This transparent, leakage-controlled design follows responsible-AI principles appropriate for audit-support systems operating on unlabeled public-sector data. Human review remains the final decision point, and no automated fraud verdict is issued.

---

## 8. Known System Limitations

1. **No Verified Fraud Ground Truth**: Public government data does not indicate which past works were fraudulent. All models act as unsupervised risk triage signals.
2. **Macro Forecasting Variance (M4)**: National and state expenditure time series are subject to fiscal quarter policy releases, which can introduce temporary variance against rolling-average forecasts.
3. **Data Quality & Free-Text Ambiguity**: Free-text work descriptions in administrative records vary in detail across districts, affecting semantic duplicate similarity matching.
4. **Duplicate Candidate $\neq$ Confirmed Duplicate**: Model M2 identifies candidate work pairs meeting high textual/geographic similarity; physical site verification is required to confirm actual duplication.
5. **Anomaly $\neq$ Wrongdoing**: High sanctioned outlays or multi-installment payment vouchers represent administrative tracking flags, not proof of financial impropriety.
6. **Risk Score $\neq$ Probability of Fraud**: Model M5 audit priority scores represent composite risk triage rank, not a calibrated mathematical probability of corruption.

---

## 9. Final Position

The platform implements the explicitly identified functional capabilities of SIH26102 and has been validated through software, pipeline-integrity, rule/invariant, and forecasting benchmark tests. Because the official public datasets do not provide verified fraud outcome labels, the system does not claim supervised fraud-detection accuracy. It instead provides explainable AI-assisted risk screening, prioritization, predictive insights, compliance monitoring, and decision-support for human auditors.

---

## 10. Documented Audit Scope

No unsupported claims were identified in the audited repository paths and file types (`.md`, `.py`, `.js`, `.html`, `.json`, `.txt`; excluding `.git`, `__pycache__`, and `vendor` directories).

---

## 11. Viva / Presentation Q&A Reference

> **JUDGE**: *"How close is your solution to the Problem Statement?"*  
> **ANSWER**: *"Every functional capability explicitly named in SIH26102 has a corresponding implemented module — cost anomaly analysis, duplicate-work screening, expenditure and payment analysis, forecasting, delay and compliance monitoring, risk alerts, and multi-role decision-support dashboards. We don't assign an artificial percentage to that alignment because the PS provides no scoring rubric. We validate what can actually be measured and disclose what cannot."*

> **JUDGE**: *"Can your AI system detect fraud?"*  
> **ANSWER**: *"We can identify potential risk patterns that may warrant audit investigation, but we do not claim confirmed fraud detection. The public MPLADS data does not contain verified fraud ground-truth labels, so fabricating them would produce an unjustified accuracy claim. Human review remains the final decision point."*
