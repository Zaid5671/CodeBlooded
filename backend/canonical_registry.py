"""
Canonical Model & Module Registry for SIH26102 MPLADS Audit Intelligence System.
Defines authoritative business IDs, display titles, analytical scope, and non-incriminating governance metadata.
"""

CANONICAL_MODELS = {
    "M1_COST_ANOMALY": {
        "id": "M1_COST_ANOMALY",
        "title": "Anomalous Cost Estimate Detection",
        "type": "AI_ML_MODEL",
        "algorithm": "Robust Peer-Group IQR/MAD + Isolation Forest (8 Non-Redundant Features)",
        "operating_point": "Configured anomaly operating point: 5%",
        "grain": "Work Level (Sanctioned Works)",
        "scope": "AUDIT-TIME ANOMALY DETECTION (Sanction-time features support pre-sanction screening where available; payment-derived features available post-expenditure)",
        "governance_label": "POTENTIAL COST ANOMALY",
        "features": [
            "log_sanction_amount",
            "peer_dev_ratio_filled",
            "robust_dev_filled",
            "days_filled",
            "num_payments_filled",
            "max_payment_ratio_filled",
            "payment_var_filled",
            "median_time_between_payments_filled"
        ]
    },
    "M2_DUPLICATE_WORK": {
        "id": "M2_DUPLICATE_WORK",
        "title": "Double-Dipping / Duplicate Work Detection",
        "type": "AI_ML_MODEL",
        "algorithm": "Geographic Candidate Blocking (State + District + Work Category) + TF-IDF Vectorizer + Cosine Similarity",
        "grain": "Candidate Pair Level (Blocked Pairs)",
        "scope": "INTRA-HOUSE & CROSS-HOUSE WORK DEDUPLICATION (Top candidate-pair ranking; hold-out representation stability diagnostic reported separately)",
        "governance_label": "POTENTIAL DUPLICATE WORK"
    },
    "M3_EXPENDITURE_ANOMALY": {
        "id": "M3_EXPENDITURE_ANOMALY",
        "title": "Expenditure & Fund Utilization Anomaly Detection",
        "type": "AI_ML_MODEL",
        "algorithm": "Transaction-Grain Lifecycle Analysis (Payment Structuring Heuristic, Velocity, First-Payment Delay)",
        "grain": "Transaction & Work Level (One Work -> Many Expenditure Transactions)",
        "scope": "POST-SANCTION DISBURSEMENT & EXPENDITURE AUDIT (Analytical screening heuristic: num_payments >= 5, total_spent > 500k, max_payment < 200k — not statutory limits)",
        "governance_label": "PAYMENT PATTERN REQUIRING REVIEW"
    },
    "M4_FORECAST": {
        "id": "M4_FORECAST",
        "title": "MPLADS Expenditure Forecasting",
        "type": "AI_ML_MODEL",
        "algorithm": "Recursive 3-Month Rolling Average Baseline (Multi-Step 6-Month Horizon)",
        "grain": "National Monthly Aggregate (State-Month Prepared)",
        "scope": "EMPIRICAL DECISION-SUPPORT EXPENDITURE PROJECTION (Empirical 95% Expected Range; evaluated against naïve previous-month baseline)",
        "governance_label": "EMPIRICAL 95% EXPECTED RANGE"
    },
    "M5_AUDIT_PRIORITY": {
        "id": "M5_AUDIT_PRIORITY",
        "title": "Unified Audit Priority Aggregator",
        "type": "AI_ML_MODEL",
        "algorithm": "Multi-Dimensional Weighted Priority Aggregation (Sum = 1.0000; Deterministic Real Signals Only)",
        "weights": {
            "Cost": 0.30,
            "Delay": 0.25,
            "Compliance": 0.25,
            "Vendor": 0.10,
            "Eligibility": 0.10
        },
        "grain": "Work Level",
        "scope": "MULTI-CRITERIA RISK TRIAGE & AUDIT ALLOCATION (Internal Score [0.00, 0.90] in [0.00, 1.00]; UI Display 0-100; Supporting-only signals never Critical)",
        "governance_label": "AUDIT PRIORITY SCORE"
    }
}

SUPPORTING_LOGIC = {
    "RULE_DELAY_SLA": {
        "id": "RULE_DELAY_SLA",
        "title": "Execution Delay & SLA Benchmark",
        "type": "DETERMINISTIC_RULE",
        "algorithm": "Peer Group Duration Tukey IQR Upper Fence (Lifecycle-aware: completed vs ongoing)",
        "governance_label": "PEER-RELATIVE DELAY ANOMALY"
    },
    "RULE_STATUTORY_COMPLIANCE": {
        "id": "RULE_STATUTORY_COMPLIANCE",
        "title": "Recommendation-to-Sanction 45-Day Statutory Benchmark",
        "type": "DETERMINISTIC_RULE",
        "algorithm": "Configured 45-day statutory approval review benchmark (Excludes negative gaps; requires administrative review)",
        "governance_label": "STATUTORY BENCHMARK DEVIATION — REQUIRES AUDIT REVIEW"
    },
    "VENDOR_RISK": {
        "id": "VENDOR_RISK",
        "title": "Vendor & Implementing Agency Concentration Analyzer",
        "type": "GRAPH_ANALYTICS",
        "algorithm": "Herfindahl-Hirschman Index (HHI) + Bipartite Network Graph Metrics with Government Entity Safeguards",
        "governance_label": "VENDOR CONCENTRATION RISK"
    },
    "MODULE_DUPLICATE_EXPENDITURE": {
        "id": "MODULE_DUPLICATE_EXPENDITURE",
        "title": "Duplicate / Repeat Transaction Detector",
        "type": "DETERMINISTIC_MODULE",
        "algorithm": "Exact & Near-Repeat Amount / Date Transaction Matching",
        "governance_label": "POTENTIAL DUPLICATE EXPENDITURE"
    },
    "MODULE_FUND_UTILIZATION": {
        "id": "MODULE_FUND_UTILIZATION",
        "title": "Fund Utilization & Idle Balances Engine",
        "type": "ANALYTICS_MODULE",
        "algorithm": "Disbursement-to-Sanction Ratio & Inactivity Thresholds",
        "governance_label": "UTILIZATION IMBALANCE"
    },
    "MODULE_ELIGIBILITY": {
        "id": "MODULE_ELIGIBILITY",
        "title": "Inadmissible Work / Eligibility Filter",
        "type": "RULE_ENGINE",
        "algorithm": "Negative List Syntactic & Landmark Context Filter (Distinguishes funded object vs location reference)",
        "governance_label": "POTENTIALLY INADMISSIBLE — REQUIRES AUDIT REVIEW"
    },
    "MODULE_PRIVATE_BENEFICIARY": {
        "id": "MODULE_PRIVATE_BENEFICIARY",
        "title": "Private & Commercial Beneficiary Detector",
        "type": "RULE_ENGINE",
        "algorithm": "Entity Ownership Classifier with Public Institution Safeguards (Schools/Hospitals protected)",
        "governance_label": "POTENTIAL PRIVATE/COMMERCIAL BENEFICIARY — REQUIRES REVIEW"
    }
}

def get_canonical_registry():
    return {
        "models": CANONICAL_MODELS,
        "supporting_logic": SUPPORTING_LOGIC
    }
