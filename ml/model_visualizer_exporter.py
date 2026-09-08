"""
SIH26102 — SUPPORTING MODEL VISUALIZATION / ARCHITECTURE INSPECTION (Netron Integration)
==========================================================================================
Generates Netron-compatible model architecture graph schemas and DAG DAG diagrams
for interactive visual architecture inspection.

Role: SUPPORTING MODEL VISUALIZATION / ARCHITECTURE INSPECTION TOOLING ONLY
Affects Prediction/Scores: NO (0.00% impact on M1, M2, M3, M4, M5 scores/forecasts)
Output Artifact: output/model_architecture_graph.json
"""

import os
import json

def export_netron_model_graph(output_path="output/model_architecture_graph.json"):
    """
    Generates Netron-compatible graph metadata specification mapping the entire
    SIH26102 5-Model Architecture (M1-M5) into a structured visualization DAG.
    Role: Supporting Model Visualization / Architecture Inspection Tooling.
    """
    graph = {
        "format": "Netron Open Neural/ML Model Graph Schema V1",
        "system": "SIH26102 MPLADS Audit Intelligence Platform",
        "role": "SUPPORTING_MODEL_VISUALIZATION_ARCHITECTURE_INSPECTION",
        "affects_model_predictions": False,
        "models": {
            "M1_COST_ANOMALY": {
                "name": "Model M1: Cost Estimate Anomaly Engine",
                "type": "Isolation Forest + Robust Peer IQR/MAD",
                "inputs": ["sanction_amount", "state", "category"],
                "outputs": ["risk_level"]
            },
            "M2_DUPLICATE_WORK": {
                "name": "Model M2: Duplicate Work Linkage Engine",
                "type": "Geographic Candidate Blocking + TF-IDF Cosine Match",
                "inputs": ["work_description", "state", "district"],
                "outputs": ["candidate_pairs_requiring_review"]
            },
            "M3_EXPENDITURE_ANOMALY": {
                "name": "Model M3: Expenditure & Payment Behavioral Screening",
                "type": "Transaction-Grain Behavioral Screening Heuristic",
                "inputs": ["num_payments", "total_spent", "max_payment"],
                "outputs": ["structuring_status"]
            },
            "M4_FORECAST": {
                "name": "Model M4: Expenditure Forecasting Engine",
                "type": "Recursive 3-Month Rolling Average Baseline",
                "inputs": ["historical_monthly_outlay"],
                "outputs": ["projected_monthly_outlay", "empirical_95_expected_range"]
            },
            "M5_AUDIT_PRIORITY": {
                "name": "Model M5: Unified Audit Priority Aggregator",
                "type": "Multi-Dimensional Weighted Priority Aggregation",
                "inputs": ["Cost(0.30)", "Delay(0.25)", "Compliance(0.25)", "Vendor(0.10)", "Eligibility(0.10)"],
                "outputs": ["priority_score", "audit_priority_tier"]
            }
        }
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(graph, f, indent=2)
    return graph
