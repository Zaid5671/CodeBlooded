# SIH26102 Final Problem Analysis Report
**SIH 2026 | Problem Statement: SIH26102**  
**AI-Powered MPLADS Audit Intelligence Platform — Team CodeBlooded**  

---

## 1. Executive Problem Summary

The **SIH26102 Problem Statement** addresses public financial monitoring, decision support, and audit triage for the Member of Parliament Local Area Development Scheme (MPLADS). Grounded strictly in official MoSPI operational guidelines, the core problem is defined as:

> *"The system must help decision-makers monitor a large volume of MPLADS work and financial records, identify potentially unusual patterns and compliance concerns, prioritize records for review, and provide evidence-based decision support."*

---

## 2. Platform Capability Scope & Boundaries

- **In-Scope Capabilities**:
  - Ingestion and auditing of MPLADS recommendations, sanctions, expenditures, and completion records.
  - Identification of cost estimate outliers relative to state/category peer baselines (Model M1).
  - Geographic candidate-pair record linkage for potential duplicate work recommendations (Model M2).
  - Detection of structured or unusual payment disbursement patterns (Model M3).
  - 6-month macro expenditure trend forecasting at `STATE × MONTH` level (Model M4).
  - Composite multi-signal audit priority scoring and triage tiering (`CRITICAL`, `STANDARD`, `LOW`) (Model M5).
  - Deterministic SLA delay tracking (sanction delay $>45$d, completion delay $>180$d) and inadmissible work screening.

- **Out-of-Scope / Non-Grounded Capabilities**:
  - The system does **NOT** compute "criminal fraud probability" or auto-convict individuals. High priority scores represent statistical risk indicators intended solely to optimize physical ground audit selection.

---

## 3. Stakeholder Capability Mapping

| Stakeholder | Jurisdiction | Primary Capabilities |
|---|---|---|
| **Ministry (MoSPI)** | All India | National Overview, 6-Month Expenditure Outlook (M4), State SLA Delay Escalation, Macro Risk Analytics. |
| **State Nodal Authority (SNA)** | State-Wide | Inter-district priority queues, Agency Concentration Index (HHI), State SLA Monitoring. |
| **District Authority (DA / DM)** | District / Constituency | Work Investigation Drawer, WhatsApp alert dispatch to field inspectors, Duplicate Work Comparison (M2). |
| **MP / Constituency Office** | Constituency | Constituency outlay summary, recommended vs sanctioned works status, completion tracking. |

---

## 4. System Function Taxonomy

- **PREDICTION**: Model M4 estimates future monthly outlay over 6 months (+7.06% MAE gain vs Naïve Baseline).
- **DETECTION**: Models M1, M2, and M3 detect statistical cost outliers, candidate duplicate pairs, and payment structuring signals.
- **PRIORITIZATION**: Model M5 ranks records into 3 audit triage tiers (`CRITICAL`, `STANDARD`, `LOW`).
- **DETERMINISTIC RULES**: Delay rules, negative keyword screening, and vendor HHI concentration metrics.
