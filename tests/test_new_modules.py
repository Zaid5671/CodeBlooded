import unittest
import pandas as pd
import numpy as np

from backend.eligibility_detection.inadmissible_works import (
    classify_inadmissible_work_description,
    run_inadmissible_work_detection
)
from backend.eligibility_detection.private_beneficiaries import (
    classify_entity_beneficiary,
    run_private_beneficiary_detection
)
from backend.expenditure_detection.duplicate_expenditure import run_duplicate_expenditure_detection
from backend.fund_utilization.fund_utilization import run_fund_utilization_analysis
from backend.vendor_risk.vendor_agency_network import run_vendor_agency_network_analysis
from backend.audit_engine.misuse_priority import run_audit_priority_aggregation
from backend.forecasting.expenditure_forecast import generate_expenditure_forecast
from cost_detection.double_dipping import run_double_dipping_detection

class TestNewModulesSuite(unittest.TestCase):

    # 1. Payment Feature & Single/Multi Payment Tests
    def test_01_single_payment_handling(self):
        df_master = pd.DataFrame([{
            'clean_work_id': 'W_SINGLE',
            'State': 'MAHARASHTRA',
            'work_category': 'ROAD',
            'sanction_amount': 500000.0,
            'Sanction Date': '2024-01-01',
            'first_expenditure_date': '2024-03-01',
            'num_payments': 1
        }])
        df_res, summary = run_fund_utilization_analysis(df_master)
        row = df_res.iloc[0]
        self.assertEqual(row['num_payments'], 1)
        self.assertFalse(row['has_multiple_payments'])
        self.assertEqual(row['trajectory_status'], "SINGLE_PAYMENT_LUMP_SUM")

    def test_02_multi_payment_handling(self):
        df_master = pd.DataFrame([{
            'clean_work_id': 'W_MULTI',
            'State': 'MAHARASHTRA',
            'work_category': 'ROAD',
            'sanction_amount': 500000.0,
            'Sanction Date': '2024-01-01',
            'first_expenditure_date': '2024-02-01',
            'num_payments': 3
        }])
        df_res, summary = run_fund_utilization_analysis(df_master)
        row = df_res.iloc[0]
        self.assertEqual(row['num_payments'], 3)
        self.assertTrue(row['has_multiple_payments'])
        self.assertEqual(row['trajectory_status'], "MULTI_PAYMENT_TRAJECTORY_AVAILABLE")

    # 2. Missing Date & First-Payment Delay Tests
    def test_03_missing_sanction_date_handling(self):
        df_master = pd.DataFrame([{
            'clean_work_id': 'W_NODATE',
            'State': 'MAHARASHTRA',
            'work_category': 'ROAD',
            'sanction_amount': 500000.0,
            'Sanction Date': None,
            'first_expenditure_date': '2024-03-01',
            'num_payments': 1
        }])
        df_res, _ = run_fund_utilization_analysis(df_master)
        row = df_res.iloc[0]
        self.assertIsNone(row['days_sanction_to_first_payment'])
        self.assertEqual(row['utilization_status'], "NOT_COMPUTABLE")

    def test_04_first_payment_delay_fencing(self):
        # Create artificial peer group to test Tukey IQR fence
        records = []
        for i in range(15):
            records.append({
                'clean_work_id': f'W_{i}',
                'State': 'KERALA',
                'work_category': 'ROAD',
                'sanction_amount': 100000.0,
                'Sanction Date': '2024-01-01',
                'first_expenditure_date': f'2024-01-{10+i:02d}', # 9-23 days delay
                'num_payments': 1
            })
        # Add extreme delayed work
        records.append({
            'clean_work_id': 'W_EXTREME',
            'State': 'KERALA',
            'work_category': 'ROAD',
            'sanction_amount': 100000.0,
            'Sanction Date': '2024-01-01',
            'first_expenditure_date': '2025-06-01', # ~500 days delay
            'num_payments': 1
        })
        df_m = pd.DataFrame(records)
        df_res, summary = run_fund_utilization_analysis(df_m)
        extreme_row = df_res[df_res['clean_work_id'] == 'W_EXTREME'].iloc[0]
        self.assertTrue(extreme_row['idle_utilization_signal'])
        self.assertEqual(extreme_row['utilization_status'], "PEER_RELATIVE_UTILIZATION_DELAY")

    # 3. Religious Landmark vs Direct Object Tests
    def test_05_religious_landmark_syntactic_filter(self):
        desc = "Construction of CC Road near Mandir Ward 4"
        res = classify_inadmissible_work_description(desc)
        self.assertEqual(res['status'], "RELIGIOUS_TERM_AS_LOCATION_REFERENCE")
        self.assertFalse(res['inadmissible_signal'])

    def test_06_direct_religious_object_detection(self):
        desc = "Construction of Temple in Village Rampur"
        res = classify_inadmissible_work_description(desc)
        self.assertEqual(res['status'], "POTENTIALLY_INADMISSIBLE")
        self.assertTrue(res['inadmissible_signal'])

    def test_07_ambiguous_religious_description(self):
        desc = "Renovation work at Shivalaya complex"
        res = classify_inadmissible_work_description(desc)
        self.assertIn(res['status'], ["AMBIGUOUS_REQUIRES_REVIEW", "POTENTIALLY_INADMISSIBLE"])
        self.assertTrue(res['inadmissible_signal'])

    # 4. Private Beneficiary & Government Safeguard Tests
    def test_08_private_commercial_beneficiary_detection(self):
        desc = "Construction of boundary wall for ABC Private Limited premises"
        res = classify_entity_beneficiary(desc)
        self.assertEqual(res['entity_category'], "PRIVATE_OR_COMMERCIAL_CANDIDATE")
        self.assertTrue(res['private_beneficiary_signal'])

    def test_09_government_entity_safeguard(self):
        desc = "Construction of additional classroom for Government Higher Secondary School"
        res = classify_entity_beneficiary(desc)
        self.assertEqual(res['entity_category'], "GOVERNMENT_ENTITY")
        self.assertFalse(res['private_beneficiary_signal'])

    # 5. Duplicate Expenditure Tests
    def test_10_exact_duplicate_payment(self):
        df_exp = pd.DataFrame([
            {'Work ID': 'W_DUP', 'Vendor Name': 'VENDOR A', 'Fund Disbursed Amount ( ₹ )': 50000.0, 'Expenditure Date': '2024-05-01'},
            {'Work ID': 'W_DUP', 'Vendor Name': 'VENDOR A', 'Fund Disbursed Amount ( ₹ )': 50000.0, 'Expenditure Date': '2024-05-01'}
        ])
        df_res, summary = run_duplicate_expenditure_detection(df_exp)
        row = df_res.iloc[0]
        self.assertTrue(row['exact_duplicate_payment'])
        self.assertTrue(row['duplicate_expenditure_signal'])

    def test_11_near_repeat_payment_pattern(self):
        df_exp = pd.DataFrame([
            {'Work ID': 'W_NEAR', 'Vendor Name': 'VENDOR B', 'Fund Disbursed Amount ( ₹ )': 49000.0, 'Expenditure Date': '2024-05-01'},
            {'Work ID': 'W_NEAR', 'Vendor Name': 'VENDOR B', 'Fund Disbursed Amount ( ₹ )': 49500.0, 'Expenditure Date': '2024-05-15'}
        ])
        df_res, summary = run_duplicate_expenditure_detection(df_exp)
        row = df_res.iloc[0]
        self.assertTrue(row['near_repeated_payment_pattern'])
        self.assertTrue(row['duplicate_expenditure_signal'])

    # 6. Vendor Graph Metrics & Reach Tests
    def test_12_vendor_graph_metrics(self):
        df_master = pd.DataFrame([
            {'clean_work_id': 'W1', 'Constituency': 'C1', 'Hon\'ble Members of Parliament': 'MP1', 'vendors': ['SUPPLIER X']},
            {'clean_work_id': 'W2', 'Constituency': 'C2', 'Hon\'ble Members of Parliament': 'MP2', 'vendors': ['SUPPLIER X']},
            {'clean_work_id': 'W3', 'Constituency': 'C3', 'Hon\'ble Members of Parliament': 'MP3', 'vendors': ['SUPPLIER X']}
        ])
        df_ia, summary = run_vendor_agency_network_analysis(df_master)
        self.assertIn('cross_constituency_reach_agencies', summary)

    # 7. Model 5 Normalized Score & Tier Threshold Tests
    def test_13_model_5_normalized_score_bounded(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W_M5', 'risk_level': 'HIGH', 'IDA': 'AGENCY_1'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W_M5', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'W_M5', 'signal_compliance': True}])
        
        df_p, summary = run_audit_priority_aggregation(df_s, df_d, df_c)
        score = df_p.iloc[0]['misuse_priority_score']
        display_score = df_p.iloc[0]['display_score']
        self.assertLessEqual(score, 1.00)
        self.assertGreaterEqual(score, 0.00)
        self.assertLessEqual(display_score, 100.0)

    def test_14_model_5_tier_thresholds(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W_HIGH', 'risk_level': 'HIGH', 'IDA': 'AGENCY_1'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W_HIGH', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'W_HIGH', 'signal_compliance': True}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        self.assertEqual(df_p.iloc[0]['audit_priority'], 'CRITICAL_AUDIT_PRIORITY')

    # 8. Cross-House & Forecast Horizon Tests
    def test_15_cross_house_pending_state(self):
        res = run_double_dipping_detection()
        self.assertEqual(res['cross_house_status'], "PENDING_RAJYA_SABHA_DATA")
        self.assertFalse(res['cross_house_enabled'])

    def test_16_forecast_6_month_horizon(self):
        df_fc, res = generate_expenditure_forecast()
        self.assertEqual(res['forecast_horizon'], 6)

if __name__ == '__main__':
    unittest.main()
