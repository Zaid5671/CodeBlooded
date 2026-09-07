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

    # 9. Model 5 Weight Sum & Model 1 District Extraction Tests
    def test_17_model_5_weights_sum_to_one(self):
        from cost_detection.config import (
            AUDIT_COST_HIGH_WEIGHT,
            AUDIT_COST_MEDIUM_WEIGHT,
            AUDIT_DELAY_WEIGHT,
            AUDIT_COMPLIANCE_WEIGHT,
            AUDIT_VENDOR_RISK_WEIGHT,
            MODEL_5_WEIGHT_SUM
        )
        self.assertEqual(MODEL_5_WEIGHT_SUM, 1.00)
        # Sum of maximum weights across 5 independent physical dimensions equals 1.00
        max_dim_sum = AUDIT_COST_HIGH_WEIGHT + AUDIT_DELAY_WEIGHT + AUDIT_COMPLIANCE_WEIGHT + AUDIT_VENDOR_RISK_WEIGHT + 0.10
        self.assertAlmostEqual(max_dim_sum, 1.00, places=4)

    def test_18_district_extraction_from_ida(self):
        from cost_detection.double_dipping_candidates import extract_district_from_ida
        self.assertEqual(extract_district_from_ida('JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA)'), 'JAUNPUR')
        self.assertEqual(extract_district_from_ida('DHARWAD(DEPUTY COMMISSIONER DHARWAR_IDA)'), 'DHARWAD')
        self.assertEqual(extract_district_from_ida('Dakshin Dinajpur(DISTRICT MAGISTRATE DINAJPUR DAKSHIN_IDA)'), 'DAKSHIN DINAJPUR')
        self.assertEqual(extract_district_from_ida('Khargone (West Nimar)(DISTRICT COLLECTOR KHARGONE_IDA)'), 'KHARGONE (WEST NIMAR)')

    def test_19_district_extraction_edge_cases(self):
        from cost_detection.double_dipping_candidates import extract_district_from_ida
        self.assertEqual(extract_district_from_ida(None), 'UNKNOWN_DISTRICT')
        self.assertEqual(extract_district_from_ida(''), 'UNKNOWN_DISTRICT')
        self.assertEqual(extract_district_from_ida('   '), 'UNKNOWN_DISTRICT')
        self.assertEqual(extract_district_from_ida(12345), '12345')

    def test_20_candidate_blocking_key(self):
        from cost_detection.double_dipping_candidates import _generate_intra_candidate_pairs
        df_dummy = pd.DataFrame([
            {'clean_work_id': 'W1', 'State': 'UP', 'Constituency': 'JAUNPUR', 'IDA': 'JAUNPUR(DISTRICT MAGISTRATE_IDA)', 'work_name': 'Road construction at Village A'},
            {'clean_work_id': 'W2', 'State': 'UP', 'Constituency': 'JAUNPUR', 'IDA': 'JAUNPUR(DISTRICT MAGISTRATE_IDA)', 'work_name': 'Road construction at Village A'}
        ])
        pairs, metrics = _generate_intra_candidate_pairs(df_dummy)
        self.assertGreater(metrics['blocked_groups'], 0)
        self.assertEqual(metrics['retained_candidate_pairs'], 1)
        self.assertIn('JAUNPUR', pairs[0]['blocking_path'])

    # 10. Model 5 Deterministic Tier Assignment Suite (Cases A through L)
    def test_21_cases_a_through_l_tier_assignment(self):
        # Case A: Vendor only (Score: 0.10, Major: 0) -> LOW
        df_s = pd.DataFrame([{'clean_work_id': 'WA', 'risk_level': 'LOW', 'IDA': 'AG_V'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WA', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WA', 'signal_compliance': False}])
        df_v = pd.DataFrame([{'implementing_agency': 'AG_V', 'concentration_risk': True}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c, df_vendor_risk=df_v)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.10)
        self.assertEqual(row['major_dimension_count'], 0)
        self.assertEqual(row['audit_priority'], 'LOW_PRIORITY')

        # Case B: Eligibility only (Score: 0.10, Major: 0) -> LOW
        df_s = pd.DataFrame([{'clean_work_id': 'WB', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WB', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WB', 'signal_compliance': False}])
        df_inad = pd.DataFrame([{'clean_work_id': 'WB', 'inadmissible_signal': True, 'eligibility_status': 'POTENTIALLY_INADMISSIBLE'}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c, df_inadmissible=df_inad)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.10)
        self.assertEqual(row['major_dimension_count'], 0)
        self.assertEqual(row['audit_priority'], 'LOW_PRIORITY')

        # Case C: Vendor + Eligibility (Score: 0.20, Major: 0) -> STANDARD (Key regression test)
        df_s = pd.DataFrame([{'clean_work_id': 'WC', 'risk_level': 'LOW', 'IDA': 'AG_V'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WC', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WC', 'signal_compliance': False}])
        df_inad = pd.DataFrame([{'clean_work_id': 'WC', 'inadmissible_signal': True, 'eligibility_status': 'POTENTIALLY_INADMISSIBLE'}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c, df_vendor_risk=df_v, df_inadmissible=df_inad)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.20)
        self.assertEqual(row['major_dimension_count'], 0)
        self.assertEqual(row['audit_priority'], 'STANDARD_REVIEW')

        # Case D: Cost only (Score: 0.30, Major: 1) -> STANDARD
        df_s = pd.DataFrame([{'clean_work_id': 'WD', 'risk_level': 'HIGH'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WD', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WD', 'signal_compliance': False}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.30)
        self.assertEqual(row['major_dimension_count'], 1)
        self.assertEqual(row['audit_priority'], 'STANDARD_REVIEW')

        # Case E: Delay only (Score: 0.25, Major: 1) -> STANDARD
        df_s = pd.DataFrame([{'clean_work_id': 'WE', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WE', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'WE', 'signal_compliance': False}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.25)
        self.assertEqual(row['major_dimension_count'], 1)
        self.assertEqual(row['audit_priority'], 'STANDARD_REVIEW')

        # Case F: Cost + Delay (Score: 0.55, Major: 2) -> CRITICAL
        df_s = pd.DataFrame([{'clean_work_id': 'WF', 'risk_level': 'HIGH'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WF', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'WF', 'signal_compliance': False}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.55)
        self.assertEqual(row['major_dimension_count'], 2)
        self.assertEqual(row['audit_priority'], 'CRITICAL_AUDIT_PRIORITY')

        # Case G: Cost + Compliance (Score: 0.55, Major: 2) -> CRITICAL
        df_s = pd.DataFrame([{'clean_work_id': 'WG', 'risk_level': 'HIGH'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WG', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WG', 'signal_compliance': True, 'compliance_severity': 'SEVERE_DEVIATION'}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.55)
        self.assertEqual(row['major_dimension_count'], 2)
        self.assertEqual(row['audit_priority'], 'CRITICAL_AUDIT_PRIORITY')

        # Case H: Delay + Compliance (Score: 0.50, Major: 2) -> CRITICAL
        df_s = pd.DataFrame([{'clean_work_id': 'WH', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WH', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'WH', 'signal_compliance': True, 'compliance_severity': 'SEVERE_DEVIATION'}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.50)
        self.assertEqual(row['major_dimension_count'], 2)
        self.assertEqual(row['audit_priority'], 'CRITICAL_AUDIT_PRIORITY')

        # Case I: Cost + Vendor (Score: 0.40, Major: 1) -> STANDARD
        df_s = pd.DataFrame([{'clean_work_id': 'WI', 'risk_level': 'HIGH', 'IDA': 'AG_V'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WI', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WI', 'signal_compliance': False}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c, df_vendor_risk=df_v)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.40)
        self.assertEqual(row['major_dimension_count'], 1)
        self.assertEqual(row['audit_priority'], 'STANDARD_REVIEW')

        # Case J: Delay + Eligibility (Score: 0.35, Major: 1) -> STANDARD
        df_s = pd.DataFrame([{'clean_work_id': 'WJ', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WJ', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'WJ', 'signal_compliance': False}])
        df_inad_j = pd.DataFrame([{'clean_work_id': 'WJ', 'inadmissible_signal': True, 'eligibility_status': 'POTENTIALLY_INADMISSIBLE'}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c, df_inadmissible=df_inad_j)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.35)
        self.assertEqual(row['major_dimension_count'], 1)
        self.assertEqual(row['audit_priority'], 'STANDARD_REVIEW')

        # Case K: Compliance + Vendor (Score: 0.35, Major: 1) -> STANDARD
        df_s = pd.DataFrame([{'clean_work_id': 'WK', 'risk_level': 'LOW', 'IDA': 'AG_V'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WK', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WK', 'signal_compliance': True, 'compliance_severity': 'SEVERE_DEVIATION'}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c, df_vendor_risk=df_v)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.35)
        self.assertEqual(row['major_dimension_count'], 1)
        self.assertEqual(row['audit_priority'], 'STANDARD_REVIEW')

        # Case L: No signals (Score: 0.00, Major: 0) -> LOW
        df_s = pd.DataFrame([{'clean_work_id': 'WL', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'WL', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'WL', 'signal_compliance': False}])
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.00)
        self.assertEqual(row['major_dimension_count'], 0)
        self.assertEqual(row['audit_priority'], 'LOW_PRIORITY')

if __name__ == '__main__':
    unittest.main()
