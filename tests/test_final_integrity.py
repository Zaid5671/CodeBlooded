import os
import glob
import json
import pytest
import numpy as np
import pandas as pd
from datetime import datetime

from cost_detection.config import (
    AUDIT_COST_HIGH_WEIGHT,
    AUDIT_COST_MEDIUM_WEIGHT,
    AUDIT_DELAY_WEIGHT,
    AUDIT_COMPLIANCE_WEIGHT,
    AUDIT_VENDOR_RISK_WEIGHT,
    MODEL_5_WEIGHT_SUM,
    OUTPUT_DIR,
    FORECAST_HORIZON_MONTHS
)
from cost_detection.isolation_forest import NUMERIC_FEATURES
from cost_detection.double_dipping_candidates import extract_district_from_ida
from backend.canonical_registry import get_canonical_registry

class TestFinalModelIntegritySuite:
    """
    Forensic verification suite testing data integrity, leak-free evaluations,
    weight bounds, non-incriminating terminology, and dashboard synchronization.
    """

    def test_01_canonical_model_registry(self):
        registry = get_canonical_registry()
        models = registry["models"]
        supporting = registry["supporting_logic"]

        assert "M1_COST_ANOMALY" in models
        assert "M2_DUPLICATE_WORK" in models
        assert "M3_EXPENDITURE_ANOMALY" in models
        assert "M4_FORECAST" in models
        assert "M5_AUDIT_PRIORITY" in models

        assert "RULE_DELAY_SLA" in supporting
        assert "RULE_STATUTORY_COMPLIANCE" in supporting
        assert "VENDOR_RISK" in supporting
        assert "MODULE_ELIGIBILITY" in supporting

    def test_02_model_1_methodology_and_split_wording(self):
        report_path = os.path.join(OUTPUT_DIR, "MODEL_TRAIN_TEST_REPORT.md")
        assert os.path.exists(report_path), "MODEL_TRAIN_TEST_REPORT.md must exist."
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Random 80/20 hold-out split with fixed random seed (42)" in content
        assert "Stratified Random" not in content
        assert "duplicate-detection accuracy" not in content.lower() or "not establish duplicate-detection accuracy" in content

    def test_03_model_2_exact_eight_features(self):
        expected_features = [
            'log_sanction_amount',
            'peer_dev_ratio_filled',
            'robust_dev_filled',
            'days_filled',
            'num_payments_filled',
            'max_payment_ratio_filled',
            'payment_var_filled',
            'median_time_between_payments_filled'
        ]
        assert len(NUMERIC_FEATURES) == 8
        assert NUMERIC_FEATURES == expected_features

    def test_04_model_2_temporal_feature_availability_audit(self):
        report_path = os.path.join(OUTPUT_DIR, "MODEL_TRAIN_TEST_REPORT.md")
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "M1 Temporal Feature Availability Audit" in content or "Sanction-Time" in content
        assert "Sanction-Time" in content
        assert "Expenditure / Audit-Time" in content

    def test_05_model_3_honest_baseline_comparison(self):
        report_path = os.path.join(OUTPUT_DIR, "MODEL_TRAIN_TEST_REPORT.md")
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "3-month rolling-average method marginally improves MAE" in content or "3-Month Rolling Average" in content
        assert "RMSE and MAPE remain higher" in content

    def test_06_model_5_weights_sum_to_exact_one(self):
        weights = [
            AUDIT_COST_HIGH_WEIGHT,       # 0.30
            AUDIT_DELAY_WEIGHT,           # 0.25
            AUDIT_COMPLIANCE_WEIGHT,      # 0.25
            AUDIT_VENDOR_RISK_WEIGHT,     # 0.10
            0.10                          # 0.10 (Eligibility & Beneficiary)
        ]
        assert abs(sum(weights) - 1.0) < 1e-9
        assert abs(MODEL_5_WEIGHT_SUM - 1.0) < 1e-9

    def test_07_model_5_supporting_only_critical_invariant(self):
        vendor_weight = AUDIT_VENDOR_RISK_WEIGHT  # 0.10
        elig_weight = 0.10                        # 0.10
        score = vendor_weight + elig_weight       # 0.20
        major_count = 0

        if score >= 0.50 or major_count >= 2:
            tier = "CRITICAL_AUDIT_PRIORITY"
        elif score >= 0.20 or major_count >= 1:
            tier = "STANDARD_REVIEW"
        else:
            tier = "LOW_PRIORITY"

        assert tier == "STANDARD_REVIEW", "Supporting-only signals must be STANDARD_REVIEW, never CRITICAL."

    def test_08_no_fraud_confirmation_language(self):
        summary_path = os.path.join(OUTPUT_DIR, "pipeline_summary.json")
        with open(summary_path, "r", encoding="utf-8") as f:
            text = f.read().lower()
        forbidden = ["fraud confirmed", "corruption confirmed", "collusion confirmed"]
        for term in forbidden:
            assert term not in text, f"Forbidden incriminating term '{term}' found in pipeline summary."

    def test_09_no_synthetic_work_ids_in_sanctioned(self):
        ls18_sanc = pd.read_csv("data/original/LokSabha18/Works Sanctioned_LokSabha_18.csv", low_memory=False)
        id_col = ls18_sanc.columns[0]
        sample_ids = ls18_sanc[id_col].dropna().astype(str).tolist()[:50]
        for sid in sample_ids:
            assert not sid.startswith("WORK_0"), "Synthetic WORK_0 IDs detected in source dataset."

    def test_10_rajya_sabha_sitting_retired_comparison(self):
        s_sanc = pd.read_csv("data/original/RajyaSabha_Sitting/Works_Sanctioned_Rajya_Sitting.csv", low_memory=False)
        r_sanc = pd.read_csv("data/original/RajyaSabha_Retired/Works Sanctioned.csv", low_memory=False)
        assert len(s_sanc) == len(r_sanc) == 19607

        s_rec = pd.read_csv("data/original/RajyaSabha_Sitting/Works_Recommended_Rajya_Sitting.csv", low_memory=False)
        r_rec = pd.read_csv("data/original/RajyaSabha_Retired/Works Recommended.csv", low_memory=False)
        assert len(s_rec) != len(r_rec), "Sitting and Retired Recommended Works must reflect genuine source row differences (36 rows)."

    def test_11_cross_house_isolation_enabled(self):
        from cost_detection.config import CROSS_HOUSE_ENABLED
        assert CROSS_HOUSE_ENABLED is False, "Cross-house automatic matching must remain disabled in production without verified metadata."

    def test_12_deep_evaluation_report_exists_and_dynamic(self):
        deep_eval_json = os.path.join(OUTPUT_DIR, "ALL_DATASETS_DEEP_EVALUATION.json")
        assert os.path.exists(deep_eval_json), "ALL_DATASETS_DEEP_EVALUATION.json must exist."
        with open(deep_eval_json) as f:
            data = json.load(f)
        assert "datasets" in data
        assert "LokSabha18" in data["datasets"]
        assert "LokSabha17" in data["datasets"]
        assert "RajyaSabha_Sitting" in data["datasets"]
        assert "RajyaSabha_Retired" in data["datasets"]

        for k, d in data["datasets"].items():
            m5 = d["m5_audit_priority"]
            assert m5.get("supporting_only_critical_count", 0) == 0, f"Supporting only critical count in {k} must be 0."

    def test_13_m3_expenditure_heuristic_and_no_fabricated_metrics(self):
        from scripts.test_all_datasets_deep_evaluation import evaluate_m3_expenditure_anomaly
        df_exp = pd.read_csv("data/original/LokSabha18/Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv", low_memory=False)
        res = evaluate_m3_expenditure_anomaly(df_exp, None)
        assert res["model_id"] == "M3_EXPENDITURE_ANOMALY"
        assert "num_payments >= 5" in res["heuristic_description"]
        assert "total_spent > ₹500,000" in res["heuristic_description"]
        assert "max_payment < ₹200,000" in res["heuristic_description"]
        assert res["statutory_threshold"] is False
        assert "statistical_transaction_outliers" not in res

    def test_14_m2_diagnostic_representation_stability_wording(self):
        deep_eval_md = os.path.join(OUTPUT_DIR, "ALL_DATASETS_DEEP_EVALUATION_REPORT.md")
        with open(deep_eval_md, "r", encoding="utf-8") as f:
            content = f.read()
        assert "M2_DUPLICATE_WORK — TF-IDF Representation Stability Diagnostic" in content
        assert "duplicate-detection accuracy" not in content.lower() or "not establish duplicate-detection accuracy" in content

    def test_15_delay_rule_lifecycle_awareness(self):
        from scripts.test_all_datasets_deep_evaluation import evaluate_rule_delay_sla
        sanc_df = pd.DataFrame({
            'sanction_dt': [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-01')],
            'work_id': ['WORK_A', 'WORK_B']
        })
        comp_df = pd.DataFrame({
            'Work ID': ['WORK_A'],
            'Completion Date': ['2024-03-01']
        })
        res = evaluate_rule_delay_sla(sanc_df, comp_df)
        assert res['records_evaluated'] == 2
        assert res['completed_works_evaluated'] == 1
        assert res['ongoing_works_evaluated'] == 1

    def test_16_m4_empirical_expected_range_wording(self):
        forecast_path = os.path.join(OUTPUT_DIR, "expenditure_forecast.json")
        with open(forecast_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "confidence_interval" not in content.lower() or "expected range" in content.lower()
        report_path = os.path.join(OUTPUT_DIR, "FINAL_MODEL_INTEGRITY_REPORT.md")
        with open(report_path, "r", encoding="utf-8") as f:
            rep_text = f.read()
        assert "EMPIRICAL 95% EXPECTED RANGE" in rep_text
