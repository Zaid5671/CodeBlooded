# SIH26102 — Problem-to-Solution Traceability Matrix

This matrix maps every core requirement of the **SIH26102 Problem Statement** directly to available data sources, system capabilities, ML models/rules, outputs, empirical evidence, and operational limitations.

---

| SIH26102 Requirement | Data Available | System Capability | Model / Rule | Output | Empirical Evidence | Operational Limitation |
|---|---|---|---|---|---|---|
| **MPLADS Work Monitoring** | 863,032 raw records across 23 CSV files (LS18, LS17, RS Sitting, RS Retired) | Works Explorer & Master Registry Search | Data Ingestion Pipeline | Interactive search table of 79,220 master works | 28/28 API tests passing `200 OK` | Public data lacks individual citizen PII. |
| **Sanction Cost Anomaly Detection** | Sanctioned amount, work category, state, constituency | Outlay Anomaly Screening | **Model M1**: Isolation Forest (`contamination=0.05`, `n_estimators=300`) | Binary Anomaly Flag & Risk Score | Test Anomaly Rate: **5.02%** (Train: **4.95%**) | Unsupervised model; requires ground physical audit verification. |
| **Duplicate Work Identification** | Work description, location, state, district, constituency | Geographic Candidate Pair Linkage | **Model M2**: Candidate Blocking + TF-IDF Cosine Similarity ($>90\%$) | Candidate Duplicate Work Pairs | **5,000 Scored Pairs** (Self-pairs: 0, Collisions: 0) | Requires ground audit seal verification to confirm double dipping. |
| **Unusual Expenditure & Payment Velocity** | Fund disbursed amount, payment date, payment count | Structuring & Velocity Screening | **Model M3**: Payment Structuring Rule Screening | Unusual Payment Signal Flag | Filtered structured payment records | Analytical screening parameter; not a legal finding. |
| **Expenditure Trend Forecasting** | Monthly state expenditure time-series (39 months historical) | 6-Month Expenditure Outlook | **Model M4**: 3-Month Rolling Time-Series Projection | Projected Monthly Outlay with 95% CI | **MAE: ₹3.45 Cr** (+7.06% gain vs Naïve Baseline) | Evaluated at State × Month aggregation grain. |
| **Risk-Based Audit Prioritization** | Composite features (Cost, Speed, Compliance, Vendor, Eligibility) | Multi-Signal Triage Queue | **Model M5**: Composite Weighted Priority Scoring | Triage Tiers: `CRITICAL`, `STANDARD`, `LOW` | **1,635 Critical Works** (Score $>75$) | Priority score optimizes audit sequence, not legal guilt. |
| **Statutory Delay Monitoring** | Recommendation date, sanction date, completion date | SLA Bottleneck Tracking | **Rule Engine**: Sanction Delay ($>45$d), Completion Delay ($>180$d) | Days Overdue & Escalation Status | Delayed projects pipeline output | Depends on reporting date entry accuracy in source CSVs. |
| **Vendor Concentration Risk** | Implementing agency name, district contract outlay | Agency Risk Matrix | **Rule Engine**: Herfindahl-Hirschman Index (HHI) | HHI Concentration Index ($0.0 \text{--} 1.0$) | District agency HHI charts | Agency name spelling variation across districts. |
| **Inadmissible Asset Screening** | Work description text | Negative List Screening | **Rule Engine**: Keyword Matching against MoSPI Guidelines | Inadmissible Work Flag | List of flagged commercial/private works | Keyword matching requires context verification. |
