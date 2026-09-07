"""
Backwards Compatibility Alias Layer for cost_detection
Maps legacy cost_detection imports to reorganized production packages:
- ml
- feature_engineering
- data_pipeline
- audit_rules
"""

import sys
from ml import config, validation, pipeline
from ml.model_1_cost_anomaly import isolation_forest, peer_analysis, overrun_rules
from ml.model_2_duplicate_work import (
    double_dipping,
    double_dipping_candidates,
    double_dipping_similarity,
    double_dipping_scoring,
    double_dipping_reconciliation,
    duplicate_detector,
)
from ml.model_3_expenditure_anomaly import expenditure_matching
from ml.model_5_audit_priority import consensus
from feature_engineering import preprocessing, category_classifier
from data_pipeline import data_loader
from audit_rules.statutory_compliance import compliance_rules
from audit_rules.vendor_risk import vendor_analytics
from audit_rules import evidence

sys.modules["cost_detection.config"] = config
sys.modules["cost_detection.validation"] = validation
sys.modules["cost_detection.pipeline"] = pipeline
sys.modules["cost_detection.isolation_forest"] = isolation_forest
sys.modules["cost_detection.peer_analysis"] = peer_analysis
sys.modules["cost_detection.overrun_rules"] = overrun_rules
sys.modules["cost_detection.double_dipping"] = double_dipping
sys.modules["cost_detection.double_dipping_candidates"] = double_dipping_candidates
sys.modules["cost_detection.double_dipping_similarity"] = double_dipping_similarity
sys.modules["cost_detection.double_dipping_scoring"] = double_dipping_scoring
sys.modules["cost_detection.double_dipping_reconciliation"] = double_dipping_reconciliation
sys.modules["cost_detection.duplicate_detector"] = duplicate_detector
sys.modules["cost_detection.expenditure_matching"] = expenditure_matching
sys.modules["cost_detection.consensus"] = consensus
sys.modules["cost_detection.preprocessing"] = preprocessing
sys.modules["cost_detection.category_classifier"] = category_classifier
sys.modules["cost_detection.data_loader"] = data_loader
sys.modules["cost_detection.compliance_rules"] = compliance_rules
sys.modules["cost_detection.vendor_analytics"] = vendor_analytics
sys.modules["cost_detection.evidence"] = evidence
