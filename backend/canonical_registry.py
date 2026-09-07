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
        "scope": "AUDIT-TIME ANOMALY DETECTION / PRE-SANCTION COST SCREENING",
        "governance_label": "POTENTIAL COST ANOMALY"
    },
    "M2_DUPLICATE_WORK": {
        "id": "M2_DUPLICATE_WORK",
        "title": "Double-Dipping / Duplicate Work Detection",
        "type": "AI_ML_MODEL",
        "algorithm": "Geographic Candidate Blocking (State+District+Category) + TF-IDF Vectorizer + Token Cosine Similarity",
        "grain": "Candidate Pair Level (Blocked Pairs)",
        "scope": "INTRA-HOUSE & CROSS-HOUSE WORK DEDUPLICATION",
        "governance_label": "POTENTIAL DUPLICATE WORK"
    },
    "M3_EXPENDITURE_ANOMALY": {
        "id": "M3_EXPENDITURE_ANOMALY",
        "title": "Expenditure & Fund Utilization Anomaly Detection",
        "type": "AI_ML_MODEL",
        "algorithm": "Transaction-Grain Lifecycle Analysis (Payment Structuring, Velocity, First-Payment Delay)",
        "grain": "Transaction & Work Level",
        "scope": "POST-SANCTION DISBURSEMENT & EXPENDITURE AUDIT",
        "governance_label": "POTENTIAL EXPENDITURE / DISBURSEMENT ANOMALY"
    },
    "M4_FORECAST": {
        "id": "M4_FORECAST",
        "title": "MPLADS Expenditure Forecasting",
        "type": "AI_ML_MODEL",
        "algorithm": "Recursive 3-Month Rolling Average Baseline (Multi-Step 6-Month Horizon)",
        "grain": "National Monthly Aggregate (State-Month Prepared)",
        "scope": "EMPIRICAL DECISION-SUPPORT EXPENDITURE PROJECTION",
        "governance_label": "EMPIRICAL 95% EXPECTED RANGE"
    },
    "M5_AUDIT_PRIORITY": {
        "id": "M5_AUDIT_PRIORITY",
        "title": "Unified Audit Priority Aggregator",
        "type": "AI_ML_MODEL",
        "algorithm": "Multi-Dimensional Weighted Priority Aggregation (Sum = 1.00)",
        "weights": {
            "Cost": 0.30,
            "Delay": 0.25,
            "Compliance": 0.25,
            "Vendor": 0.10,
            "Eligibility": 0.10
        },
        "grain": "Work Level",
        "scope": "MULTI-CRITERIA RISK TRIAGE & AUDIT ALLOCATION",
        "governance_label": "AUDIT PRIORITY SCORE"
    }
}

SUPPORTING_LOGIC = {
    "RULE_DELAY_SLA": {
        "id": "RULE_DELAY_SLA",
        "title": "Execution Delay & SLA Benchmark",
        "type": "DETERMINISTIC_RULE",
        "algorithm": "Peer Group Duration Tukey IQR Upper Fence",
        "governance_label": "PEER-RELATIVE DELAY ANOMALY"
    },
    "RULE_STATUTORY_COMPLIANCE": {
        "id": "RULE_STATUTORY_COMPLIANCE",
        "title": "Recommendation-to-Sanction 45-Day Statutory Benchmark",
        "type": "DETERMINISTIC_RULE",
        "algorithm": "Configured 45-day statutory approval threshold review",
        "governance_label": "STATUTORY COMPLIANCE DEVIATION — REQUIRES AUDIT REVIEW"
    },
    "VENDOR_RISK": {
        "id": "VENDOR_RISK",
        "title": "Vendor & Implementing Agency Concentration Analyzer",
        "type": "GRAPH_ANALYTICS",
        "algorithm": "Herfindahl-Hirschman Index (HHI) + Bipartite Network Graph Metrics",
        "governance_label": "VENDOR CONCENTRATION RISK"
    },
    "MODULE_DUPLICATE_EXPENDITURE": {
        "id": "MODULE_DUPLICATE_EXPENDITURE",
        "title": "Duplicate / Repeat Transaction Detector",
        "type": "DETERMINISTIC_MODULE",
        "algorithm": "Exact & Near-Repeat Amount / Date Transaction Matching",
        "governance_label": "PAYMENT PATTERN REQUIRING REVIEW"
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
        "algorithm": "Negative List Syntactic & Keyword Parser with Context Filters",
        "governance_label": "POTENTIALLY INADMISSIBLE — REQUIRES AUDIT REVIEW"
    },
    "MODULE_PRIVATE_BENEFICIARY": {
        "id": "MODULE_PRIVATE_BENEFICIARY",
        "title": "Private & Commercial Beneficiary Detector",
        "type": "RULE_ENGINE",
        "algorithm": "Entity Ownership Classifier with Government Entity Safeguards",
        "governance_label": "POTENTIAL PRIVATE/COMMERCIAL BENEFICIARY — REQUIRES REVIEW"
    }
}

def get_canonical_registry():
    return {
        "models": CANONICAL_MODELS,
        "supporting_logic": SUPPORTING_LOGIC
    }
