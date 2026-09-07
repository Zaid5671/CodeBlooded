import os
import sys
import unittest
import pandas as pd
import numpy as np

vendor_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vendor")
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

from data_pipeline.reconciliation_engine import run_master_reconciliation
from audit_rules.vendor_risk.vendor_agency_network import run_vendor_agency_network_analysis, classify_vendor_entity_type
from ml.model_4_forecasting.expenditure_forecaster import run_expenditure_forecasting
from ml.model_5_audit_priority.misuse_priority import run_audit_priority_aggregation

class TestFullSystemProductionSuite(unittest.TestCase):

    # 1. GOVERNMENT ENTITY CLASSIFICATION TESTS
    def test_01_government_entity_classification(self):
        self.assertEqual(classify_vendor_entity_type("DISTRICT ENGINEER PWD"), "GOVERNMENT_ENTITY")
        self.assertEqual(classify_vendor_entity_type("DEPUTY COMMISSIONER CACHAR_IDA"), "GOVERNMENT_ENTITY")
        self.assertEqual(classify_vendor_entity_type("EXECUTIVE ENGINEER HARIDWAR"), "GOVERNMENT_ENTITY")
        self.assertEqual(classify_vendor_entity_type("ZILLA NIRMITI KENDRA"), "GOVERNMENT_ENTITY")

    def test_02_private_entity_classification(self):
        self.assertEqual(classify_vendor_entity_type("ABC INFRASTRUCTURE PVT LTD"), "PRIVATE_ENTITY")
        self.assertEqual(classify_vendor_entity_type("XYZ CONSTRUCTIONS PRIVATE LIMITED"), "PRIVATE_ENTITY")

    # 2. VENDOR CONCENTRATION & HHI TESTS
    def test_03_vendor_concentration_and_hhi(self):
        df_ia, summary = run_vendor_agency_network_analysis()
        self.assertGreater(len(df_ia), 0)
        self.assertIn('total_implementing_agencies_analyzed', summary)
        self.assertIn('high_concentration_agencies', summary)

    def test_04_payment_structuring_detection(self):
        df_ia, summary = run_vendor_agency_network_analysis()
        self.assertIn('payment_structuring_candidate_agencies', summary)

    # 3. EXPENDITURE FORECASTING TESTS
    def test_05_expenditure_forecasting_projections(self):
        df_fc, summary = run_expenditure_forecasting()
        self.assertEqual(len(df_fc), 6)
        self.assertIn('total_expected_expenditure', summary)
        self.assertTrue((df_fc['upper_bound'] >= df_fc['lower_bound']).all())

    # 4. MASTER RECONCILIATION TESTS
    def test_06_master_reconciliation_report(self):
        df_master, reco_report = run_master_reconciliation()
        self.assertGreater(len(df_master), 70000)
        self.assertIn('lifecycle_counts', reco_report)
        self.assertEqual(reco_report['lifecycle_counts']['master_work_entities'], len(df_master))

    # 5. MODEL 5 ADVANCED AGGREGATION TESTS
    def test_07_vendor_risk_integrated_in_model_5(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH', 'IDA': 'AGENCY_A'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True, 'delay_status': 'ONGOING_DELAYED', 'evidence': 'Delayed'}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False}])
        df_v = pd.DataFrame([{
            'implementing_agency': 'AGENCY_A',
            'concentration_risk': True,
            'evidence': ['High expenditure concentration detected']
        }])

        df_p, summary = run_audit_priority_aggregation(df_s, df_d, df_c, df_vendor_risk=df_v)
        row = df_p.iloc[0]
        self.assertEqual(row['fired_signal_count'], 2)
        self.assertEqual(row['audit_priority'], 'CRITICAL_AUDIT_PRIORITY')
        self.assertTrue(row['vendor_concentration_risk'])
        self.assertIn('Vendor Network:', ' '.join(row['combined_evidence']))

if __name__ == '__main__':
    unittest.main()
