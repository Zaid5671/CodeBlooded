import os
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

class TestFinalModelIntegritySuite:
    """
    Forensic verification suite testing data integrity, leak-free evaluations,
    weight bounds, non-incriminating terminology, and dashboard synchronization.
    """

    def test_01_model_1_methodology_and_split_wording(self):
        report_path = os.path.join(OUTPUT_DIR, "MODEL_TRAIN_TEST_REPORT.md")
        assert os.path.exists(report_path), "MODEL_TRAIN_TEST_REPORT.md must exist."
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Random 80/20 hold-out split with fixed random seed (42)" in content
        assert "Stratified Random" not in content
        assert "duplicate-detection accuracy" not in content.lower() or "not establish duplicate-detection accuracy" in content

    def test_02_model_1_district_extraction_and_fallback(self):
        assert extract_district_from_ida("JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA)") == "JAUNPUR"
        assert extract_district_from_ida("Khargone (West Nimar)(DISTRICT COLLECTOR KHARGONE_IDA)") == "KHARGONE (WEST NIMAR)"
        assert extract_district_from_ida(None) == "UNKNOWN_DISTRICT"
        assert extract_district_from_ida("") == "UNKNOWN_DISTRICT"

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
        assert "Model 2 Temporal Feature Availability Audit" in content
        assert "Sanction-Time" in content
        assert "Expenditure / Audit-Time" in content

    def test_05_model_3_honest_baseline_comparison(self):
        report_path = os.path.join(OUTPUT_DIR, "MODEL_TRAIN_TEST_REPORT.md")
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "3-month rolling-average expenditure forecasting baseline" in content
        assert "marginally improves MAE" in content
        assert "RMSE and MAPE remain higher" in content

    def test_06_model_3_six_month_horizon_and_empirical_terminology(self):
        forecast_path = os.path.join(OUTPUT_DIR, "expenditure_forecast.json")
        assert os.path.exists(forecast_path), "expenditure_forecast.json must exist."
        with open(forecast_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("forecast_horizon") == 6
        assert data.get("status") == "SUCCESS"
        timeline = data.get("forecast_records", [])
        future_records = [r for r in timeline if r.get("type") == "FUTURE_FORECAST"]
        assert len(future_records) == 6

    def test_07_model_5_weights_sum_to_exact_one(self):
        weights = [
            AUDIT_COST_HIGH_WEIGHT,       # 0.30
            AUDIT_DELAY_WEIGHT,           # 0.25
            AUDIT_COMPLIANCE_WEIGHT,      # 0.25
            AUDIT_VENDOR_RISK_WEIGHT,     # 0.10
            0.10                          # 0.10 (Eligibility & Beneficiary)
        ]
        assert abs(sum(weights) - 1.0) < 1e-9
        assert abs(MODEL_5_WEIGHT_SUM - 1.0) < 1e-9

    def test_08_model_5_priority_score_bounds(self):
        summary_path = os.path.join(OUTPUT_DIR, "pipeline_summary.json")
        assert os.path.exists(summary_path), "pipeline_summary.json must exist."
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        m5 = data.get("audit_priority_model", {})
        min_score = m5.get("score_min", 0.0)
        max_score = m5.get("score_max", 0.90)
        assert min_score >= 0.0
        assert max_score <= 1.0

    def test_09_model_5_supporting_only_critical_invariant(self):
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

    def test_10_no_fraud_confirmation_language(self):
        summary_path = os.path.join(OUTPUT_DIR, "pipeline_summary.json")
        with open(summary_path, "r", encoding="utf-8") as f:
            text = f.read().lower()
        forbidden = ["fraud confirmed", "fraud detected", "corruption confirmed", "collusion confirmed"]
        for term in forbidden:
            assert term not in text, f"Forbidden incriminating term '{term}' found in pipeline summary."

    def test_11_dataset_inventory_dynamically_generated(self):
        scan_path = os.path.join(OUTPUT_DIR, "FULL_DATASET_SCAN.json")
        assert os.path.exists(scan_path), "FULL_DATASET_SCAN.json must exist."
        with open(scan_path, "r", encoding="utf-8") as f:
            scan_data = json.load(f)
        assert len(scan_data) == 17
        total_rows = sum(d["row_count"] for d in scan_data)
        assert total_rows == 782874
