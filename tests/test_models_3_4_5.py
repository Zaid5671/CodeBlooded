import os
import unittest
import pandas as pd
import numpy as np
from datetime import datetime

from backend.delay_detection.delayed_projects import run_delay_detection
from backend.compliance_detection.approval_compliance import run_compliance_detection, build_ia_watchlist
from backend.audit_engine.misuse_priority import run_audit_priority_aggregation

class TestModels345(unittest.TestCase):
    
    # -------------------------------------------------------------------------
    # MODEL 3 TESTS (1-12)
    # -------------------------------------------------------------------------
    def setUp(self):
        # Create synthetic master dataset for testing
        np.random.seed(42)
        
        # State A: 12 completed works (duration 10 to 50 days), 2 ongoing
        # State B: 3 completed works (duration 20 to 30 days), 2 ongoing (national fallback)
        records = []
        for i in range(12):
            records.append({
                'clean_work_id': f"WS/MP1/2024-2025/100{i}",
                'state': 'STATE_A',
                'sanction_date': '2024-01-01',
                'completion_date': f"2024-02-{10+i:02d}", # ~40 to 51 days
                'work_status': 'COMPLETED'
            })
            
        for i in range(3):
            records.append({
                'clean_work_id': f"WS/MP2/2024-2025/200{i}",
                'state': 'STATE_B',
                'sanction_date': '2024-01-01',
                'completion_date': '2024-01-20',
                'work_status': 'COMPLETED'
            })
            
        # Ongoing work in State A (long ongoing)
        records.append({
            'clean_work_id': 'WS/MP1/2024-2025/1099',
            'state': 'STATE_A',
            'sanction_date': '2024-01-01',
            'completion_date': None,
            'work_status': 'SANCTIONED'
        })
        
        # Ongoing work in State B
        records.append({
            'clean_work_id': 'WS/MP2/2024-2025/2099',
            'state': 'STATE_B',
            'sanction_date': '2024-01-01',
            'completion_date': None,
            'work_status': 'SANCTIONED'
        })
        
        # Work missing sanction date
        records.append({
            'clean_work_id': 'WS/MP3/2024-2025/3001',
            'state': 'STATE_C',
            'sanction_date': None,
            'completion_date': None,
            'work_status': 'SANCTIONED'
        })
        
        self.df_test_master = pd.DataFrame(records)

    def test_01_correct_iqr_calculation(self):
        df_delay, summary = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        self.assertIn('state_peer_groups_formed', summary)
        self.assertGreaterEqual(summary['state_peer_groups_formed'], 1)

    def test_02_correct_tukey_upper_fence(self):
        df_delay, summary = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        state_a_fences = df_delay[df_delay['state'] == 'STATE_A']['upper_fence_days'].iloc[0]
        self.assertGreater(state_a_fences, 0)

    def test_03_iqr_zero_does_not_crash(self):
        # Create dataset where all completed works have exact same duration (IQR=0)
        df_zero_iqr = pd.DataFrame([
            {'clean_work_id': f"W{i}", 'state': 'STATE_ZERO', 'sanction_date': '2024-01-01', 'completion_date': '2024-02-01', 'work_status': 'COMPLETED'}
            for i in range(12)
        ])
        df_delay, summary = run_delay_detection(df_zero_iqr, reference_date='2025-01-01')
        self.assertEqual(len(df_delay), 12)

    def test_04_no_nan_inf_from_zero_iqr(self):
        df_zero_iqr = pd.DataFrame([
            {'clean_work_id': f"W{i}", 'state': 'STATE_ZERO', 'sanction_date': '2024-01-01', 'completion_date': '2024-02-01', 'work_status': 'COMPLETED'}
            for i in range(12)
        ])
        df_delay, _ = run_delay_detection(df_zero_iqr, reference_date='2025-01-01')
        self.assertFalse(df_delay['upper_fence_days'].isnull().any())
        self.assertFalse(np.isinf(df_delay['upper_fence_days']).any())

    def test_05_state_with_10_plus_uses_state_peer(self):
        df_delay, _ = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        row_state_a = df_delay[df_delay['state'] == 'STATE_A'].iloc[0]
        self.assertEqual(row_state_a['delay_basis'], 'STATE_PEER')

    def test_06_state_with_less_than_10_uses_national_fallback(self):
        df_delay, _ = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        row_state_b = df_delay[df_delay['state'] == 'STATE_B'].iloc[0]
        self.assertEqual(row_state_b['delay_basis'], 'NATIONAL_FALLBACK_LOW_CONFIDENCE')

    def test_07_completed_duration_is_correct(self):
        df_delay, _ = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        w0 = df_delay[df_delay['clean_work_id'] == 'WS/MP1/2024-2025/1000'].iloc[0]
        self.assertEqual(w0['duration_for_delay_check'], 40.0) # Jan 1 to Feb 10 = 40 days

    def test_08_ongoing_duration_is_correct(self):
        df_delay, _ = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        ong = df_delay[df_delay['clean_work_id'] == 'WS/MP1/2024-2025/1099'].iloc[0]
        self.assertEqual(ong['duration_for_delay_check'], 366.0) # 2024 is leap year, Jan 1 2024 to Jan 1 2025 = 366 days

    def test_09_missing_sanction_date_is_retained(self):
        df_delay, _ = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        missing_row = df_delay[df_delay['clean_work_id'] == 'WS/MP3/2024-2025/3001'].iloc[0]
        self.assertEqual(missing_row['delay_status'], 'UNKNOWN_MISSING_SANCTION_DATE')
        self.assertFalse(missing_row['signal_delay'])

    def test_10_missing_completion_record_is_retained(self):
        df_delay, _ = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        ong_row = df_delay[df_delay['clean_work_id'] == 'WS/MP1/2024-2025/1099'].iloc[0]
        self.assertFalse(ong_row['is_completed'])
        self.assertIn('ONGOING', ong_row['delay_status'])

    def test_11_delay_evidence_contains_threshold_values(self):
        df_delay, _ = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        ong_delayed = df_delay[df_delay['clean_work_id'] == 'WS/MP1/2024-2025/1099'].iloc[0]
        self.assertTrue(ong_delayed['signal_delay'])
        self.assertIn('peer upper fence', ong_delayed['evidence'])

    def test_12_repeated_execution_is_deterministic(self):
        d1, s1 = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        d2, s2 = run_delay_detection(self.df_test_master, reference_date='2025-01-01')
        pd.testing.assert_frame_equal(d1, d2)
        self.assertEqual(s1, s2)

    # -------------------------------------------------------------------------
    # MODEL 4 TESTS (13-21)
    # -------------------------------------------------------------------------
    def test_13_gap_le_45_is_compliant(self):
        df = pd.DataFrame([{'clean_work_id': 'W1', 'recommended_date': '2024-01-01', 'sanction_date': '2024-01-30'}]) # 29 days
        df_c, _ = run_compliance_detection(df)
        self.assertEqual(df_c.iloc[0]['compliance_severity'], 'COMPLIANT')
        self.assertFalse(df_c.iloc[0]['signal_compliance'])

    def test_14_gap_46_to_90_is_minor_deviation(self):
        df = pd.DataFrame([{'clean_work_id': 'W1', 'recommended_date': '2024-01-01', 'sanction_date': '2024-03-01'}]) # 60 days
        df_c, _ = run_compliance_detection(df)
        self.assertEqual(df_c.iloc[0]['compliance_severity'], 'MINOR_DEVIATION')
        self.assertTrue(df_c.iloc[0]['signal_compliance'])

    def test_15_gap_91_to_180_is_moderate_deviation(self):
        df = pd.DataFrame([{'clean_work_id': 'W1', 'recommended_date': '2024-01-01', 'sanction_date': '2024-05-01'}]) # 121 days
        df_c, _ = run_compliance_detection(df)
        self.assertEqual(df_c.iloc[0]['compliance_severity'], 'MODERATE_DEVIATION')
        self.assertTrue(df_c.iloc[0]['signal_compliance'])

    def test_16_gap_gt_180_is_severe_deviation(self):
        df = pd.DataFrame([{'clean_work_id': 'W1', 'recommended_date': '2024-01-01', 'sanction_date': '2024-08-01'}]) # 213 days
        df_c, _ = run_compliance_detection(df)
        self.assertEqual(df_c.iloc[0]['compliance_severity'], 'SEVERE_DEVIATION')
        self.assertTrue(df_c.iloc[0]['signal_compliance'])

    def test_17_missing_dates_gives_unknown_missing_dates(self):
        df = pd.DataFrame([{'clean_work_id': 'W1', 'recommended_date': '2024-01-01', 'sanction_date': None}])
        df_c, _ = run_compliance_detection(df)
        self.assertEqual(df_c.iloc[0]['compliance_severity'], 'UNKNOWN_MISSING_DATES')
        self.assertFalse(df_c.iloc[0]['signal_compliance'])

    def test_18_missing_dates_are_retained(self):
        df = pd.DataFrame([{'clean_work_id': 'W1', 'recommended_date': None, 'sanction_date': None}])
        df_c, _ = run_compliance_detection(df)
        self.assertEqual(len(df_c), 1)

    def test_19_signal_compliance_only_fires_for_deviations(self):
        df = pd.DataFrame([
            {'clean_work_id': 'W1', 'recommended_date': '2024-01-01', 'sanction_date': '2024-01-10'}, # Compliant
            {'clean_work_id': 'W2', 'recommended_date': '2024-01-01', 'sanction_date': '2024-03-10'}, # Minor
            {'clean_work_id': 'W3', 'recommended_date': '2024-01-01', 'sanction_date': None}          # Missing
        ])
        df_c, _ = run_compliance_detection(df)
        fired = df_c[df_c['signal_compliance']]['clean_work_id'].tolist()
        self.assertEqual(fired, ['W2'])

    def test_20_ia_watchlist_excludes_fewer_than_20_works(self):
        records = []
        for i in range(25):
            records.append({'clean_work_id': f"W_A_{i}", 'ida': 'AGENCY_A', 'recommended_date': '2024-01-01', 'sanction_date': '2024-03-01'})
        for i in range(5):
            records.append({'clean_work_id': f"W_B_{i}", 'ida': 'AGENCY_B', 'recommended_date': '2024-01-01', 'sanction_date': '2024-03-01'})
            
        df_master = pd.DataFrame(records)
        watchlist = build_ia_watchlist(df_master, min_works=20)
        self.assertEqual(len(watchlist), 1)
        self.assertEqual(watchlist.iloc[0]['implementing_agency'], 'AGENCY_A')

    def test_21_ia_watchlist_sorts_by_median_gap_descending(self):
        records = []
        for i in range(20):
            records.append({'clean_work_id': f"W_FAST_{i}", 'ida': 'FAST_AGENCY', 'recommended_date': '2024-01-01', 'sanction_date': '2024-01-10'}) # 9 days gap
            records.append({'clean_work_id': f"W_SLOW_{i}", 'ida': 'SLOW_AGENCY', 'recommended_date': '2024-01-01', 'sanction_date': '2024-06-01'}) # ~152 days gap
            
        df_master = pd.DataFrame(records)
        watchlist = build_ia_watchlist(df_master, min_works=20)
        self.assertEqual(watchlist.iloc[0]['implementing_agency'], 'SLOW_AGENCY')

    # -------------------------------------------------------------------------
    # MODEL 5 TESTS (22-34)
    # -------------------------------------------------------------------------
    def test_22_high_cost_contributes_0_30(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH', 'evidence_list': ['Cost high']}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': False, 'delay_status': 'ONGOING_ON_SCHEDULE'}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False, 'compliance_severity': 'COMPLIANT'}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.30)
        self.assertTrue(row['cost_signal'])

    def test_23_medium_cost_contributes_0_10(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'MEDIUM', 'evidence_list': ['Cost medium']}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': False, 'delay_status': 'ONGOING_ON_SCHEDULE'}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False, 'compliance_severity': 'COMPLIANT'}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.10)

    def test_24_medium_cost_does_not_count_as_fired_independent_signal(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'MEDIUM', 'evidence_list': ['Cost medium']}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': False, 'delay_status': 'ONGOING_ON_SCHEDULE'}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False, 'compliance_severity': 'COMPLIANT'}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertFalse(row['cost_signal'])
        self.assertEqual(row['fired_signal_count'], 0)
        self.assertEqual(row['audit_priority'], 'LOW_PRIORITY')

    def test_25_delay_contributes_0_25(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True, 'delay_status': 'ONGOING_DELAYED', 'evidence': 'Delayed 100 days'}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False, 'compliance_severity': 'COMPLIANT'}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.25)
        self.assertTrue(row['delay_signal'])

    def test_26_compliance_contributes_0_25(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': True, 'compliance_severity': 'SEVERE_DEVIATION', 'evidence': 'Gap 200 days'}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['misuse_priority_score'], 0.25)
        self.assertTrue(row['compliance_signal'])

    def test_27_two_signals_gives_critical_audit_priority(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH', 'evidence_list': ['Cost high']}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True, 'evidence': 'Delayed'}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['fired_signal_count'], 2)
        self.assertEqual(row['audit_priority'], 'CRITICAL_AUDIT_PRIORITY')

    def test_28_one_signal_gives_standard_review(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH', 'evidence_list': ['Cost high']}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['fired_signal_count'], 1)
        self.assertEqual(row['audit_priority'], 'STANDARD_REVIEW')

    def test_29_zero_signals_gives_low_priority(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'LOW'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': False}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['fired_signal_count'], 0)
        self.assertEqual(row['audit_priority'], 'LOW_PRIORITY')

    def test_30_fired_signal_count_is_correct(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': True, 'compliance_severity': 'SEVERE_DEVIATION'}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        self.assertEqual(row['fired_signal_count'], 3)
        self.assertEqual(row['misuse_priority_score'], 0.80)

    def test_31_combined_evidence_corresponds_to_fired_signals(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH', 'evidence_list': ['Cost overrun detected']}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True, 'evidence': 'Ongoing for 400 days'}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': False, 'evidence': 'Sanctioned in 20 days'}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        row = df_p.iloc[0]
        ev = " ".join(row['combined_evidence'])
        self.assertIn('Cost overrun', ev)
        self.assertIn('Ongoing for 400 days', ev)

    def test_32_no_duplicate_work_ids_in_final_aggregation(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH'}, {'clean_work_id': 'W1', 'risk_level': 'HIGH'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': True}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        self.assertEqual(len(df_p), 1)

    def test_33_no_nan_or_inf_in_outputs(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': True}])
        
        df_p, _ = run_audit_priority_aggregation(df_s, df_d, df_c)
        self.assertFalse(df_p['misuse_priority_score'].isnull().any())
        self.assertFalse(np.isinf(df_p['misuse_priority_score']).any())

    def test_34_deterministic_repeated_execution(self):
        df_s = pd.DataFrame([{'clean_work_id': 'W1', 'risk_level': 'HIGH'}])
        df_d = pd.DataFrame([{'clean_work_id': 'W1', 'signal_delay': True}])
        df_c = pd.DataFrame([{'clean_work_id': 'W1', 'signal_compliance': True}])
        
        p1, s1 = run_audit_priority_aggregation(df_s, df_d, df_c)
        p2, s2 = run_audit_priority_aggregation(df_s, df_d, df_c)
        pd.testing.assert_frame_equal(p1, p2)
        self.assertEqual(s1, s2)

if __name__ == '__main__':
    unittest.main()
