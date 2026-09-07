# PHASE 6 — AUDIT PRIORITY & DETERMINISTIC RULE ENGINE REPORT
**SIH 2026 | SIH26102 MPLADS Audit Intelligence Platform**

---

## 1. UNIFIED AUDIT PRIORITY MODEL (M5)
- **Signal Aggregation Weights**:
  - Cost Risk: `0.30`
  - Speed & Delay: `0.25`
  - Statutory Compliance: `0.25`
  - Vendor & Payment Risk: `0.10`
  - Eligibility & Beneficiary: `0.10`
  - **Total Sum**: `1.00`
- **Internal Normalized Score**: `0.0` to `1.0` (Mapped to `0 - 100` in UI).
- **Audit Priority Tiers**:
  - `CRITICAL AUDIT PRIORITY`: Multiple independent signals fired.
  - `STANDARD REVIEW`: Single signal or moderate deviation fired.
  - `LOW PRIORITY`: Zero independent signals fired.
  - *Invariant*: Supporting-only signals cannot independently trigger `CRITICAL AUDIT PRIORITY`.

## 2. DETERMINISTIC STATUTORY RULES
- **Recommendation -> Sanction SLA**: 75 Days (MPLADS Guidelines 2023).
- **Rejection Notification SLA**: 45 Days (`NOT CURRENTLY EVALUABLE` due to data boundary constraints).
- **Completion Baseline**: 365 Days.
- **Vendor Concentration**: HHI Threshold `0.40` (`PROCUREMENT CONCENTRATION INDICATOR`).

---
**Status**: `PHASE 6 AUDIT PRIORITY COMPLETE`
