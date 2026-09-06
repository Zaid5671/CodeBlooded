import os
import unittest
import pandas as pd
import numpy as np

from cost_detection.double_dipping_similarity import (
    normalize_text_for_matching,
    normalize_vendor_name,
    is_generic_description,
    extract_location_entities,
    compute_pairwise_features,
    get_or_create_embeddings_cache
)
from cost_detection.double_dipping_scoring import compute_double_dipping_risk
from cost_detection.double_dipping_candidates import generate_candidate_pairs
from cost_detection.double_dipping import calculate_score_distribution_diagnostics

class TestDoubleDipping25V2Suite(unittest.TestCase):

    def test_01_lifecycle_records_not_flagged(self):
        """TEST 1: Same lifecycle work across datasets is NOT flagged."""
        df_master = pd.DataFrame([
            {
                'entity_id': 'ENT_000001',
                'clean_work_id': 'WS/MP100/2024-2025/111111',
                'state': 'UTTAR PRADESH',
                'constituency': 'VARANASI',
                'mp': 'MP A',
                'category': 'ROAD',
                'description': 'Construction of cc road at rampur village',
                'sanction_amount': 500000.0,
                'expenditure_amount': 500000.0,
                'all_vendors': ['XYZ Construction'],
                'sanction_date': '2024-05-10',
                'work_status': 'COMPLETED'
            },
            {
                'entity_id': 'ENT_000002',
                'clean_work_id': 'WS/MP100/2024-2025/111111', # Same clean_work_id
                'state': 'UTTAR PRADESH',
                'constituency': 'VARANASI',
                'mp': 'MP A',
                'category': 'ROAD',
                'description': 'Construction of cc road at rampur village',
                'sanction_amount': 500000.0,
                'expenditure_amount': 500000.0,
                'all_vendors': ['XYZ Construction'],
                'sanction_date': '2024-05-10',
                'work_status': 'SANCTIONED'
            }
        ])
        candidates, metrics = generate_candidate_pairs(df_master)
        self.assertEqual(len(candidates), 0, "Same clean_work_id must NOT produce double-dipping pairs")
        self.assertEqual(metrics['pairs_removed_lifecycle'], 1)

    def test_02_distinct_similar_works_flagged(self):
        """TEST 2: Two distinct identical/similar works are flagged."""
        r_a = {
            'entity_id': 'ENT_000001',
            'clean_work_id': 'WS/MP100/2024-2025/111111',
            'state': 'UTTAR PRADESH',
            'constituency': 'VARANASI',
            'mp': 'MP A',
            'category': 'ROAD',
            'description': 'Construction of cement concrete road at rampur village ward 5',
            'sanction_amount': 500000.0,
            'all_vendors': ['XYZ Infra'],
            'sanction_date': '2024-05-10',
            'work_status': 'SANCTIONED'
        }
        r_b = {
            'entity_id': 'ENT_000002',
            'clean_work_id': 'WS/MP100/2024-2025/222222', # Distinct work_id
            'state': 'UTTAR PRADESH',
            'constituency': 'VARANASI',
            'mp': 'MP A',
            'category': 'ROAD',
            'description': 'Construction of cement concrete road at rampur village ward 5',
            'sanction_amount': 500000.0,
            'all_vendors': ['XYZ Infra'],
            'sanction_date': '2024-05-12',
            'work_status': 'SANCTIONED'
        }
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertGreaterEqual(risk['risk_score'], 85)
        self.assertEqual(risk['risk_tier'], "HIGH RISK — REQUIRES AUDIT REVIEW")

    def test_03_generic_description_dampened(self):
        """TEST 3: Generic boilerplate descriptions receive dampening."""
        r_a = {
            'entity_id': 'ENT_000001',
            'clean_work_id': 'WS/MP100/2024-2025/111111',
            'state': 'UTTAR PRADESH',
            'constituency': 'VARANASI',
            'mp': 'MP A',
            'category': 'ROAD',
            'description': 'Construction of road',
            'sanction_amount': 500000.0,
            'all_vendors': [],
            'sanction_date': '2024-05-10',
            'work_status': 'SANCTIONED'
        }
        r_b = {
            'entity_id': 'ENT_000002',
            'clean_work_id': 'WS/MP100/2024-2025/222222',
            'state': 'UTTAR PRADESH',
            'constituency': 'VARANASI',
            'mp': 'MP A',
            'category': 'ROAD',
            'description': 'Construction of road',
            'sanction_amount': 500000.0,
            'all_vendors': [],
            'sanction_date': '2024-05-10',
            'work_status': 'SANCTIONED'
        }
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertTrue(feats['is_generic_description'])
        self.assertLess(risk['risk_score'], 85)

    def test_04_same_vendor_alone_not_high_risk(self):
        """TEST 4: Same vendor alone does NOT produce HIGH RISK."""
        r_a = {
            'entity_id': 'ENT_000001',
            'clean_work_id': 'WS/MP100/2024-2025/111111',
            'state': 'BIHAR',
            'constituency': 'PATNA',
            'mp': 'MP B',
            'category': 'HEALTH',
            'description': 'Supply of CT scan machine for hospital',
            'sanction_amount': 4500000.0,
            'all_vendors': ['Surya Infra Pvt Ltd'],
            'sanction_date': '2024-01-01',
            'work_status': 'SANCTIONED'
        }
        r_b = {
            'entity_id': 'ENT_000002',
            'clean_work_id': 'WS/MP100/2024-2025/222222',
            'state': 'BIHAR',
            'constituency': 'PATNA',
            'mp': 'MP B',
            'category': 'ROAD',
            'description': 'Construction of 2km rural road at gola block',
            'sanction_amount': 200000.0,
            'all_vendors': ['Surya Infra Pvt Ltd'],
            'sanction_date': '2024-06-01',
            'work_status': 'SANCTIONED'
        }
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertNotEqual(risk['risk_tier'], "HIGH RISK — REQUIRES AUDIT REVIEW")

    def test_05_same_constituency_alone_not_high_risk(self):
        """TEST 5: Same constituency alone does NOT produce HIGH RISK."""
        r_a = {
            'entity_id': 'ENT_000001',
            'clean_work_id': 'WS/MP100/2024-2025/111111',
            'state': 'BIHAR',
            'constituency': 'PATNA',
            'mp': 'MP B',
            'category': 'HEALTH',
            'description': 'Installation of water purifier in school',
            'sanction_amount': 50000.0,
            'all_vendors': ['Vendor A'],
            'sanction_date': '2024-01-01',
            'work_status': 'SANCTIONED'
        }
        r_b = {
            'entity_id': 'ENT_000002',
            'clean_work_id': 'WS/MP100/2024-2025/222222',
            'state': 'BIHAR',
            'constituency': 'PATNA',
            'mp': 'MP B',
            'category': 'LIGHTING',
            'description': 'Highmast solar light at bus stand',
            'sanction_amount': 800000.0,
            'all_vendors': ['Vendor B'],
            'sanction_date': '2024-08-01',
            'work_status': 'SANCTIONED'
        }
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertNotEqual(risk['risk_tier'], "HIGH RISK — REQUIRES AUDIT REVIEW")

    def test_06_missing_fields_no_crash(self):
        """TEST 6: Missing amount/date/vendor/location does not crash."""
        r_a = {
            'entity_id': 'ENT_000001',
            'clean_work_id': 'UNPARSED_1',
            'state': '',
            'constituency': '',
            'mp': '',
            'category': 'OTHER',
            'description': '',
            'sanction_amount': 0.0,
            'all_vendors': [],
            'sanction_date': '',
            'work_status': ''
        }
        r_b = {
            'entity_id': 'ENT_000002',
            'clean_work_id': 'UNPARSED_2',
            'state': '',
            'constituency': '',
            'mp': '',
            'category': 'OTHER',
            'description': '',
            'sanction_amount': 0.0,
            'all_vendors': [],
            'sanction_date': '',
            'work_status': ''
        }
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertIsInstance(risk['risk_score'], int)

    def test_07_zero_amounts_no_nan_inf(self):
        """TEST 7: Zero amounts do not cause NaN/Inf."""
        r_a = {'sanction_amount': 0.0, 'description': 'road'}
        r_b = {'sanction_amount': 0.0, 'description': 'road'}
        feats = compute_pairwise_features(r_a, r_b)
        self.assertFalse(np.isnan(feats['amount_similarity']))
        self.assertFalse(np.isinf(feats['amount_similarity']))

    def test_08_embedding_cache(self):
        """TEST 8: Embedding / vector cache works."""
        df_dummy = pd.DataFrame([{'description': 'test work'}])
        model_obj, emb, backend, is_cached = get_or_create_embeddings_cache(df_dummy)
        self.assertIsNotNone(emb)

    def test_09_no_self_pairs(self):
        """TEST 9: Candidate blocking does not generate self-pairs."""
        df_master = pd.DataFrame([
            {
                'entity_id': 'ENT_000001',
                'clean_work_id': 'WS/MP100/2024-2025/111111',
                'state': 'UTTAR PRADESH',
                'constituency': 'VARANASI',
                'mp': 'MP A',
                'category': 'ROAD',
                'description': 'Construction of cc road',
                'sanction_amount': 500000.0,
                'expenditure_amount': 0.0,
                'all_vendors': [],
                'sanction_date': '',
                'work_status': 'SANCTIONED'
            }
        ])
        candidates, metrics = generate_candidate_pairs(df_master)
        self.assertEqual(len(candidates), 0)

    def test_10_canonical_ids_excluded(self):
        """TEST 10: Canonical lifecycle IDs are excluded."""
        df_master = pd.DataFrame([
            {'entity_id': 'E1', 'clean_work_id': 'WS/MP1/2024/10', 'state': 'UP', 'constituency': 'VARANASI', 'description': 'Road A', 'sanction_amount': 100},
            {'entity_id': 'E2', 'clean_work_id': 'WS/MP1/2024/10', 'state': 'UP', 'constituency': 'VARANASI', 'description': 'Road A', 'sanction_amount': 100}
        ])
        candidates, metrics = generate_candidate_pairs(df_master)
        self.assertEqual(len(candidates), 0)

    def test_11_evidence_corresponds_to_features(self):
        """TEST 11: Evidence values correspond to actual features."""
        r_a = {'sanction_amount': 500000.0, 'description': 'cc road at rampur village', 'constituency': 'VARANASI'}
        r_b = {'sanction_amount': 500000.0, 'description': 'cc road at rampur village', 'constituency': 'VARANASI'}
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertTrue(any("Identical" in ev or "High" in ev for ev in risk['triggered_evidence']))

    def test_12_risk_score_in_bounds(self):
        """TEST 12: Risk score remains in [0, 100]."""
        r_a = {'sanction_amount': 100, 'description': 'a'}
        r_b = {'sanction_amount': 200, 'description': 'b'}
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertGreaterEqual(risk['risk_score'], 0)
        self.assertLessEqual(risk['risk_score'], 100)

    def test_13_high_risk_requires_contextual_proof(self):
        """TEST 13: HIGH RISK requires contextual proof."""
        r_a = {'sanction_amount': 100, 'description': 'generic road', 'constituency': 'CONST A'}
        r_b = {'sanction_amount': 100, 'description': 'generic road', 'constituency': 'CONST B'}
        feats = compute_pairwise_features(r_a, r_b)
        feats['location_similarity'] = 0.0
        feats['vendor_similarity'] = 0.0
        feats['constituency_match'] = 0.0
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertNotEqual(risk['risk_tier'], "HIGH RISK — REQUIRES AUDIT REVIEW")

    def test_14_deterministic_output(self):
        """TEST 14: Deterministic output."""
        r_a = {'sanction_amount': 500000.0, 'description': 'construction of road at rampur', 'constituency': 'VARANASI'}
        r_b = {'sanction_amount': 500000.0, 'description': 'construction of road at rampur', 'constituency': 'VARANASI'}
        feats1 = compute_pairwise_features(r_a, r_b)
        risk1 = compute_double_dipping_risk(r_a, r_b, feats1)
        feats2 = compute_pairwise_features(r_a, r_b)
        risk2 = compute_double_dipping_risk(r_a, r_b, feats2)
        self.assertEqual(risk1['risk_score'], risk2['risk_score'])

    def test_15_no_duplicate_reverse_pairs(self):
        """TEST 15: Duplicate pair A-B and B-A are NOT both returned."""
        df_master = pd.DataFrame([
            {'entity_id': 'E1', 'clean_work_id': 'W1', 'state': 'UP', 'constituency': 'VNS', 'description': 'Road Rampur 1', 'sanction_amount': 100},
            {'entity_id': 'E2', 'clean_work_id': 'W2', 'state': 'UP', 'constituency': 'VNS', 'description': 'Road Rampur 2', 'sanction_amount': 100}
        ])
        candidates, _ = generate_candidate_pairs(df_master)
        pair_keys = [tuple(sorted([c['entity_a']['entity_id'], c['entity_b']['entity_id']])) for c in candidates]
        self.assertEqual(len(pair_keys), len(set(pair_keys)))

    def test_16_missing_location_not_fake_match(self):
        """TEST 16: Missing location does NOT become fake location match."""
        r_a = {'description': 'construction of road'}
        r_b = {'description': 'construction of road'}
        feats = compute_pairwise_features(r_a, r_b)
        self.assertEqual(feats['location_similarity'], 0.0)

    def test_17_identical_generic_not_auto_high(self):
        """TEST 17: Identical generic descriptions do NOT automatically become high risk."""
        r_a = {'sanction_amount': 50000.0, 'description': 'repair work', 'constituency': 'CONST A'}
        r_b = {'sanction_amount': 50000.0, 'description': 'repair work', 'constituency': 'CONST B'}
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertLess(risk['risk_score'], 85)

    def test_18_image_placeholder_safe(self):
        """TEST 18: Image placeholder values do NOT trigger image processing."""
        r_a = {'description': 'work a', 'image': 'Images'}
        r_b = {'description': 'work b', 'image': 'Images'}
        feats = compute_pairwise_features(r_a, r_b)
        self.assertFalse(feats['image_similarity_available'])

    def test_19_missing_vendor_not_fake_match(self):
        """TEST 19: Missing vendor does NOT become vendor match."""
        r_a = {'all_vendors': []}
        r_b = {'all_vendors': []}
        feats = compute_pairwise_features(r_a, r_b)
        self.assertEqual(feats['vendor_status'], 'NO_VENDOR_DATA')
        self.assertEqual(feats['vendor_similarity'], 0.5)

    def test_20_missing_amount_not_fake_match(self):
        """TEST 20: Missing amount handled safely without crash."""
        r_a = {'sanction_amount': 0.0, 'description': 'work a'}
        r_b = {'sanction_amount': 100000.0, 'description': 'work b'}
        feats = compute_pairwise_features(r_a, r_b)
        self.assertLess(feats['amount_similarity'], 1.0)

    def test_21_v2_model_version_exposed(self):
        """TEST 21: Model version is V2."""
        from cost_detection.config import DOUBLE_DIPPING_V2_CONFIG
        self.assertEqual(DOUBLE_DIPPING_V2_CONFIG['model_version'], 'double_dipping_v2')

    def test_22_convergence_bonus_applied(self):
        """TEST 22: Multi-signal convergence bonus triggers when >= 3 anchors match."""
        r_a = {'sanction_amount': 500000.0, 'description': 'cc road at rampur village', 'all_vendors': ['XYZ Infra'], 'constituency': 'VNS'}
        r_b = {'sanction_amount': 500000.0, 'description': 'cc road at rampur village', 'all_vendors': ['XYZ Infra'], 'constituency': 'VNS'}
        feats = compute_pairwise_features(r_a, r_b)
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertGreaterEqual(risk['convergence_count'], 3)

    def test_23_score_distribution_diagnostics(self):
        """TEST 23: Score distribution diagnostics calculated correctly."""
        scores = [10, 20, 50, 75, 85, 90, 100]
        diag = calculate_score_distribution_diagnostics(scores)
        self.assertEqual(diag['min'], 10.0)
        self.assertEqual(diag['max'], 100.0)
        self.assertIn('p25', diag)
        self.assertIn('p75', diag)
        self.assertIn('pct_gte_85', diag)

    def test_24_master_feature_vector_keys(self):
        """TEST 24: Master 25-feature vector populated."""
        r_a = {'sanction_amount': 100, 'description': 'test work a'}
        r_b = {'sanction_amount': 100, 'description': 'test work b'}
        feats = compute_pairwise_features(r_a, r_b)
        self.assertIn('semantic_similarity', feats)
        self.assertIn('title_similarity', feats)
        self.assertIn('amount_difference', feats)
        self.assertIn('location_method', feats)

    def test_25_score_saturation_control(self):
        """TEST 25: Generic works without contextual anchors do NOT saturate at 100."""
        r_a = {'sanction_amount': 50000.0, 'description': 'construction of road', 'constituency': 'VARANASI'}
        r_b = {'sanction_amount': 50000.0, 'description': 'construction of road', 'constituency': 'VARANASI'}
        feats = compute_pairwise_features(r_a, r_b)
        feats['location_similarity'] = 0.0
        risk = compute_double_dipping_risk(r_a, r_b, feats)
        self.assertLess(risk['risk_score'], 95)

if __name__ == '__main__':
    unittest.main()
