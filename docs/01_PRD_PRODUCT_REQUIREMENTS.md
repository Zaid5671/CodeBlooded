# 01. Product Requirements Document (PRD)
> **MPLADS Audit Intelligence Platform — SIH 2026 (Problem Statement SIH26102)**  
> *The North Star Document: Product vision, user personas, core requirements, and success metrics.*

---

## 1. Executive Summary & Product Vision

- **App Name**: MPLADS Audit Intelligence Platform
- **Tagline**: AI-Powered Decision Support & Multi-Agent Triage Engine for Public Infrastructure Expenditure Audit
- **Problem Statement**: SIH26102 — Monitoring 79,220+ Member of Parliament Local Area Development Scheme (MPLADS) work entities across 543+ Lok Sabha and Rajya Sabha constituencies manually leads to undetected cost inflation, duplicate funding across parliamentary terms ("double-dipping"), statutory SLA approval delays, and vendor concentration risks.
- **Solution**: An enterprise-grade government monitoring console powered by 5 machine learning models (M1–M5) that automatically triages, scores (0–100), and correlates sanction and expenditure data across parliamentary corpora.

---

## 2. Target User Personas

1. **Ministry Official (MoSPI)**: National-level auditors overseeing policy compliance, country-wide expenditure velocity, and high-risk audit selection.
2. **State Nodal Authority (SNA)**: State-level administrators monitoring district implementation agencies, SLA bottlenecks, and regional vendor concentration.
3. **District Authority / Magistrate (DA)**: On-ground execution authorities investigating specific work anomalies, cost outliers, and dispatching WhatsApp alerts to field officers.
4. **MP / Constituency Office**: Parliamentary representatives tracking sanction velocity and project completion SLA benchmarks.
5. **SIH Evaluator / Judge**: Technical judges verifying ML pipeline repeatability, test suite coverage (136/136 tests), and production UI/UX integration.

---

## 3. Core Features (Must-Have vs. Nice-to-Have)

### Must-Have (v1.0 Production Release)
- **M1 Cost Anomaly Engine**: Peer IQR / MAD baseline + 300-estimator Isolation Forest cost outlier screening.
- **M2 Double-Dipping Detector**: 384-dimensional Sentence-Transformers TF-IDF record linkage for cross-house duplicate work matching.
- **M3 Statutory SLA Compliance**: Automated tracking against the 45-day statutory sanction approval window.
- **M4 Expenditure Forecasting**: 6-month rolling outlay projection with empirical 95% confidence bounds.
- **M5 Unified Misuse Priority Aggregator**: Multi-dimensional risk score (0–100) combining Models M1–M4.
- **Dynamic Dataset Switcher**: Real-time dataset selector (`Lok Sabha 18`, `Lok Sabha 17`, `Rajya Sabha`, `Combined Dataset`) that refetches backend endpoints and updates all views.
- **Responsive Geographic Breakdown**: Dynamic State-wise vs. District-wise outlay distribution charts.
- **WhatsApp Notification Dispatcher**: Webhook payload generator (`POST /api/notifications/dispatch`) for automated alert delivery.
- **Production UX & Legal Suite**: DPDP Act 2023 Privacy Policy, Terms of Service, Security Disclosure, Cookie Preferences, Accessibility Statement, and 404/403/500 error fallbacks.

### Nice-to-Have (v2.0 Roadmap)
- GIS Interactive Satellite Map Overlay for physical site verification.
- Automated CAG Audit Docket PDF Generator.

---

## 4. User Stories

- *As a District Magistrate*, I want to filter works in my district to identify cost outliers exceeding peer medians by >1.5x so that I can audit suspect contractors before releasing final payment.
- *As a MoSPI Auditor*, I want to cross-match works across Lok Sabha 17 and 18 to catch duplicate road construction projects funded twice under different sanction IDs.
- *As a State Nodal Officer*, I want to identify implementing agencies with high HHI concentration scores (>0.30) to prevent vendor monopolization.

---

## 5. Out of Scope

- Direct financial disbursement execution (the system is a non-custodial audit decision support console).
- Unauthenticated public crowdsourcing.

---

## 6. Key Success Metrics

- **Data Integrity**: 100% coverage of 79,220 master work entities with 0 missing field crashes.
- **Model Repeatability**: 5-fold cross-validation Jaccard overlap = `0.5659 ± 0.0086`.
- **Automated Test Pass Rate**: 136/136 pytest unit test suites passing (`python3 -m pytest tests/`).
- **Response Latency**: <100ms API response time for paginated master works queries.
