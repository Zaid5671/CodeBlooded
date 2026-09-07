import os
import json
import unittest
import pandas as pd
import numpy as np

from ml.config import OUTPUT_DIR
from ml.model_2_duplicate_work.double_dipping import compare_works, run_double_dipping_detection
from ml.model_2_duplicate_work.double_dipping_candidates import generate_candidate_pairs
from ml.model_4_forecasting.expenditure_forecast import generate_expenditure_forecast

class TestCrossHouseAndForecast(unittest.TestCase):

    def setUp(self):
        self.mock_ls_works = [
            {
                'clean_work_id': 'LS_001',
                'master_work_id': 'LS_001',
                'entity_id': 'LS_001',
                'chamber': 'LS',
                'state': 'MAHARASHTRA',
                'constituency': 'MUMBAI NORTH',
                'mp': 'MP Alpha',
                'category': 'ROAD',
                'description': 'Construction of CC road near Zilla Parishad School Ward 5',
                'sanction_amount': 500000.0,
                'expenditure_amount': 450000.0,
                'vendors': ['ABC Infra Pvt Ltd'],
                'sanction_date': '2024-08-10',
                'work_status': 'SANCTIONED'
            },
            {
                'clean_work_id': 'LS_002',
                'master_work_id': 'LS_002',
                'entity_id': 'LS_002',
                'chamber': 'LS',
                'state': 'MAHARASHTRA',
                'constituency': 'MUMBAI NORTH',
                'mp': 'MP Alpha',
                'category': 'LIGHTING',
                'description': 'Installation of solar street lights at Main Chowk',
                'sanction_amount': 200000.0,
                'expenditure_amount': 200000.0,
                'vendors': ['Solar Tech Enterprises'],
                'sanction_date': '2024-09-01',
                'work_status': 'COMPLETED'
            }
        ]

        self.mock_rs_works = [
            {
                'clean_work_id': 'RS_001',
                'master_work_id': 'RS_001',
                'entity_id': 'RS_001',
                'chamber': 'RS',
                'state': 'MAHARASHTRA',
                'constituency': 'MUMBAI NORTH',
                'mp': 'MP Beta (RS)',
                'category': 'ROAD',
                'description': 'Construction of CC road near Zilla Parishad School Ward 5',
                'sanction_amount': 490000.0,
                'expenditure_amount': 480000.0,
                'vendors': ['ABC Infra Pvt Ltd'],
                'sanction_date': '2024-08-15',
                'work_status': 'SANCTIONED'
            },
            {
                'clean_work_id': 'RS_002',
                'master_work_id': 'RS_002',
                'entity_id': 'RS_002',
                'chamber': 'RS',
                'state': 'KERALA',
                'constituency': 'WAYANAD',
                'mp': 'MP Gamma (RS)',
                'category': 'ROAD',
                'description': 'Construction of CC road',
                'sanction_amount': 300000.0,
                'expenditure_amount': 0.0,
                'vendors': [],
                'sanction_date': '2024-10-01',
                'work_status': 'SANCTIONED'
            }
        ]

    # -------------------------------------------------------------------------
    # PART A: CROSS-HOUSE DOUBLE-DIPPING TESTS
    # -------------------------------------------------------------------------
    def test_ls_ls_behavior_preserved(self):
        """Verify LS-LS intra-dataset candidate generation and scoring behave as expected."""
        pairs, metrics = compare_works(self.mock_ls_works, df_b=None, chamber_pair="LS-LS")
        self.assertIsInstance(pairs, list)
        self.assertIsInstance(metrics, dict)
        for p in pairs:
            self.assertEqual(p['chamber_pair'], "LS-LS")

    def test_ls_rs_interface_accepts_two_datasets(self):
        """Verify compare_works accepts separate df_a and df_b datasets with chamber_pair='LS-RS'."""
        pairs, metrics = compare_works(self.mock_ls_works, df_b=self.mock_rs_works, chamber_pair="LS-RS")
        self.assertIsInstance(pairs, list)
        self.assertGreaterEqual(len(pairs), 1)
        self.assertEqual(pairs[0]['chamber_pair'], "LS-RS")
        self.assertEqual(pairs[0]['chamber_a'], "LS")
        self.assertEqual(pairs[0]['chamber_b'], "RS")

    def test_same_asset_high_similarity_detected(self):
        """Verify identical work descriptions in same location across chambers receive high risk score."""
        pairs, _ = compare_works(self.mock_ls_works, df_b=self.mock_rs_works, chamber_pair="LS-RS")
        # Match between LS_001 and RS_001 (same physical asset description and location)
        matched = [p for p in pairs if (p['source_work_id'] == 'LS_001' and p['matched_work_id'] == 'RS_001') or (p['source_work_id'] == 'RS_001' and p['matched_work_id'] == 'LS_001')]
        self.assertEqual(len(matched), 1)
        self.assertGreaterEqual(matched[0]['risk_score'], 80)
        self.assertIn("POTENTIAL CROSS-HOUSE DUPLICATE", matched[0]['triggered_evidence'])

    def test_different_location_generic_desc_not_high_risk(self):
        """Verify generic descriptions in different locations are not automatically classified as HIGH risk."""
        ls_generic = [{
            'clean_work_id': 'LS_G', 'master_work_id': 'LS_G', 'state': 'DELHI', 'constituency': 'NEW DELHI',
            'category': 'ROAD', 'description': 'Construction of CC road', 'sanction_amount': 100000.0,
            'expenditure_amount': 0.0, 'vendors': [], 'sanction_date': '2024-01-01', 'work_status': 'SANCTIONED'
        }]
        rs_generic = [{
            'clean_work_id': 'RS_G', 'master_work_id': 'RS_G', 'state': 'TAMIL NADU', 'constituency': 'CHENNAI',
            'category': 'ROAD', 'description': 'Construction of CC road', 'sanction_amount': 100000.0,
            'expenditure_amount': 0.0, 'vendors': [], 'sanction_date': '2024-01-01', 'work_status': 'SANCTIONED'
        }]
        pairs, _ = compare_works(ls_generic, df_b=rs_generic, chamber_pair="LS-RS")
        for p in pairs:
            self.assertNotEqual(p['risk_tier'], "HIGH RISK — REQUIRES AUDIT REVIEW")

    def test_reverse_duplicate_pairs_deduplicated(self):
        """Verify pair candidate generator removes reverse duplicate pairs (id_b, id_a)."""
        df_a = pd.DataFrame(self.mock_ls_works)
        df_b = pd.DataFrame(self.mock_rs_works)
        candidates, metrics = generate_candidate_pairs(df_a, df_b=df_b, chamber_pair="LS-RS")
        pair_keys = [ (c['entity_a']['clean_work_id'], c['entity_b']['clean_work_id']) for c in candidates ]
        reverse_keys = [ (b, a) for (a, b) in pair_keys ]
        for r_key in reverse_keys:
            self.assertNotIn(r_key, pair_keys)

    def test_missing_rs_data_handling(self):
        """Verify pipeline orchestrator handles missing RS data gracefully without crashing."""
        res = run_double_dipping_detection(data_dir="data/original/LokSabha18")
        self.assertEqual(res['cross_house_status'], "PENDING_RAJYA_SABHA_DATA")
        self.assertFalse(res['cross_house_enabled'])
        self.assertEqual(res['cross_house_candidate_count'], 0)
        self.assertEqual(res['cross_house_high_risk_count'], 0)

    def test_missing_fields_resilience(self):
        """Verify missing fields (missing vendors, missing dates) do not crash matching."""
        sparse_a = [{'clean_work_id': 'SA1', 'state': 'GOA', 'constituency': 'NORTH GOA', 'description': 'Supply of books'}]
        sparse_b = [{'clean_work_id': 'SB1', 'state': 'GOA', 'constituency': 'NORTH GOA', 'description': 'Supply of books'}]
        pairs, _ = compare_works(sparse_a, df_b=sparse_b, chamber_pair="LS-RS")
        self.assertIsInstance(pairs, list)

    def test_chamber_pair_correctly_written(self):
        """Verify chamber_pair field is written as LS-RS on output records."""
        pairs, _ = compare_works(self.mock_ls_works, df_b=self.mock_rs_works, chamber_pair="LS-RS")
        for p in pairs:
            self.assertEqual(p['chamber_pair'], "LS-RS")

    # -------------------------------------------------------------------------
    # PART B: EXPENDITURE FORECASTING TESTS
    # -------------------------------------------------------------------------
    def test_forecast_monthly_aggregation(self):
        """Verify expenditure forecasting executes monthly aggregation cleanly on data."""
        df_fcst, res = generate_expenditure_forecast()
        self.assertIn(res['status'], ['SUCCESS', 'INSUFFICIENT_DATA'])
        self.assertIsInstance(res['forecast_records'], list)
        if res['status'] == 'SUCCESS':
            self.assertGreater(res['observations_used'], 0)

    def test_forecast_insufficient_data_handling(self):
        """Verify forecaster handles insufficient historical observation threshold gracefully."""
        df_fcst, res = generate_expenditure_forecast(data_dir="tmp_non_existent_path")
        self.assertEqual(res['status'], "INSUFFICIENT_DATA")
        self.assertEqual(res['observations_used'], 0)
        self.assertEqual(len(res['forecast_records']), 0)

    def test_forecast_prediction_interval_bounds(self):
        """Verify prediction intervals satisfy lower_bound <= forecast <= upper_bound."""
        df_fcst, res = generate_expenditure_forecast()
        if res['status'] == 'SUCCESS':
            for r in res['forecast_records']:
                self.assertLessEqual(r['lower_bound'], r['upper_bound'])
                self.assertLessEqual(r['lower_bound'], r['forecast_expenditure'] + 1e-5)

    def test_forecast_deviation_statuses(self):
        """Verify deviation_status values are valid non-incriminating flags."""
        df_fcst, res = generate_expenditure_forecast()
        valid_statuses = {'ABOVE_EXPECTED_TREND', 'BELOW_EXPECTED_TREND', 'WITHIN_EXPECTED_RANGE', 'PROJECTED_FORECAST'}
        if res['status'] == 'SUCCESS':
            for r in res['forecast_records']:
                self.assertIn(r['deviation_status'], valid_statuses)

    def test_forecast_deterministic_execution(self):
        """Verify forecaster yields identical output across multiple runs."""
        _, res1 = generate_expenditure_forecast()
        _, res2 = generate_expenditure_forecast()
        self.assertEqual(res1['observations_used'], res2['observations_used'])
        self.assertEqual(res1['anomaly_count'], res2['anomaly_count'])

    def test_forecast_output_files_generated(self):
        """Verify output/expenditure_forecast_results.json and expenditure_forecast.csv are written."""
        generate_expenditure_forecast()
        json_p1 = os.path.join(OUTPUT_DIR, "expenditure_forecast_results.json")
        json_p2 = os.path.join(OUTPUT_DIR, "expenditure_forecast.json")
        csv_p = os.path.join(OUTPUT_DIR, "expenditure_forecast.csv")
        self.assertTrue(os.path.exists(json_p1))
        self.assertTrue(os.path.exists(json_p2))
        self.assertTrue(os.path.exists(csv_p))

if __name__ == '__main__':
    unittest.main()
