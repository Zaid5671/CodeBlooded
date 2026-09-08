# SIH26102 — Official Problem Analysis & Capabilities Specification

**Problem Statement ID**: SIH26102  
**Title**: AI-Powered MPLADS Audit Intelligence Platform  
**Team**: CodeBlooded (SIH 2026)  

---

## A1. Problem Statement Analysis

The **Member of Parliament Local Area Development Scheme (MPLADS)** enables Members of Parliament (MPs) to recommend developmental works in their constituencies, focusing on creating durable community assets (e.g., drinking water, primary education, public health, sanitation, and roads). Grounded in official MoSPI (Ministry of Statistics and Programme Implementation) operational guidelines, the audit intelligence platform processes records across four stages of the work lifecycle:

1. **Recommendation**: MP recommendation of project scope, location, and recommended outlay.
2. **Sanction**: District Authority (DA) technical and financial sanction, cost estimation, and implementing agency assignment.
3. **Execution & Progress**: Ongoing physical execution, milestone progress tracking, and payment disbursement.
4. **Completion & Asset Creation**: Final asset creation, completion certification, and ground audit verification.

### System Capabilities & Grounded Scope

- **MPLADS Works & Recommendations**: Ingest and audit raw works data across Lok Sabha (17th & 18th) and Rajya Sabha (Sitting & Retired).
- **Sanctions & Cost Estimates**: Identify cost anomalies where sanctioned outlay deviates significantly from peer state/category baselines.
- **Expenditure & Payment Monitoring**: Track payment velocity, transaction structuring patterns, and disbursement timelines.
- **Work Progress & Asset Creation**: Monitor SLA completion timelines, delay durations, and physical asset reporting.
- **Trends & Forecasts**: Provide 6-month state-level expenditure trend projections using time-series analysis.
- **Anomalies & Irregularities**: Detect unusual cost estimates (M1), potential duplicate work linkages across boundary partitions (M2), and payment structuring indicators (M3).
- **Delayed Projects**: Flag projects exceeding statutory sanction-to-completion SLA windows.
- **Risk-Based Alerts & Decision Support**: Score and prioritize work entities for human field audit review (M5).
- **Dashboards & Stakeholder Views**: Multi-role views tailored to Ministry, State Nodal Authority, District Authority, and MP Offices.

> [!IMPORTANT]
> **Boundary of Capabilities**: The platform functions as an **administrative audit decision support and triage system**. It does **NOT** auto-confirm criminal fraud or legal culpability without physical ground audit inspection by certified authorities.

---

## A2. Actual System Users & Intended Stakeholders

| Stakeholder Role | Intended Platform Capabilities | Scope of Access |
|---|---|---|
| **Ministry (MoSPI Nodal Desk)** | National overview, macro expenditure trends, state-level risk comparisons, 6-month outlay forecasts, high-level SLA bottleneck analysis. | All India / Multi-State |
| **State Nodal Authority (SNA)** | Inter-district priority tracking, implementing agency concentration (HHI), state SLA delay escalation monitoring. | State-Wide Jurisdiction |
| **District Authority (DA / DM)** | District-level triage queue, Work Investigation Drawer, WhatsApp field alert dispatch, duplicate work side-by-side verification. | District / Constituency |
| **MP / Constituency Office** | Track recommended vs sanctioned works status, constituency outlay summary, project completion progress. | Constituency Bound |

---

## A3. Core Problem Statement

> **"The system must help decision-makers monitor a large volume of MPLADS work and financial records, identify potentially unusual patterns and compliance concerns, prioritize records for review, and provide evidence-based decision support."**

---

## Part B — System Function Taxonomy: Prediction vs Detection vs Rules

### B1. What the System Predicts
- **Model M4 (Expenditure Forecasting)**: Predicts **future monthly expenditure/outlay** over a 6-month horizon at the `STATE × MONTH` level using chronological historical expenditure trends.
  - *Input*: Historical monthly outlay time-series.
  - *Output*: Projected monthly outlay (₹ Cr) with 95% confidence intervals.
  - *Horizon*: 6 Months.
  - *Metric*: MAE, RMSE, WAPE (+7.06% accuracy gain vs Naïve Baseline).

### B2. What the System Detects
- **Model M1 (Cost Outliers)**: Detects works with sanctioned outlays that deviate significantly from state and category peer-group distributions using Isolation Forest (`contamination=0.05`).
- **Model M2 (Duplicate Works)**: Detects potential duplicate/recurrent work candidate pairs within geographic boundaries using TF-IDF cosine text similarity ($> 90\%$).
- **Model M3 (Expenditure Anomalies)**: Detects structured or unusual payment disbursement velocity patterns.

### B3. What the System Ranks
- **Model M5 (Audit Priority Scoring)**: Integrates independent signals (Cost, Speed, Compliance, Vendor, Eligibility) into a composite priority score $[0, 100]$.
  - *Triage Categories*: `CRITICAL` ($>75$), `STANDARD` ($40\text{--}75$), `LOW` ($<40$).
  - *Purpose*: Ranks records to optimize human ground-audit allocation.

### B4. What the Rule Engine Checks
- **Deterministic SLA Rules**: Sanction delay $> 45$ days, completion delay $> 180$ days.
- **Inadmissible Works Screening**: Keyword matches against negative list guidelines (e.g., commercial/private assets).
- **Vendor Concentration (HHI)**: Herfindahl-Hirschman Index for agency contract allocation.
