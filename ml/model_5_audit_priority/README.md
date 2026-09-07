# Model 5 — Multi-Signal Risk Aggregator & Audit Priority Triage Engine

- **Purpose**: Aggregates independent risk signals into a unified audit priority score (0–100) and priority tier.
- **Input**: Fired signal flags from M1, M2, M3, M4, delay SLA, statutory compliance, and vendor risk engines.
- **Features**: Normalized weighted signal vector.
- **Algorithm**: Linear weighted aggregation: Cost Anomaly (0.30) + Delay SLA (0.25) + Compliance (0.25) + Vendor Risk (0.10) + Eligibility (0.10) = 1.00.
- **Output**: Audit priority score (0–100), audit_tier (CRITICAL AUDIT PRIORITY, STANDARD REVIEW, LOW PRIORITY), and supporting evidence logs.
- **Called From**: ml.model_5_audit_priority.misuse_priority.run_audit_priority_aggregation()
- **Evaluation Method**: Multimodal signal concordance audit; supporting-only signals cannot elevate risk to Critical without primary signals.
- **Known Limitations**: Audit triage allocation tool; requires human auditor verification.
