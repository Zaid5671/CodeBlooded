import os

# Model Metadata
MODEL_NAME = "Anomalous Cost Estimate & Cost Overrun Detection Engine"
MODEL_VERSION = "1.0.0"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "original", "LokSabha18")

SANCTIONED_WORKS_FILE = os.path.join(DATA_DIR, "Works Sanctioned_LokSabha_18.csv")
EXPENDITURE_WORKS_FILE = os.path.join(DATA_DIR, "Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv")
RECOMMENDED_WORKS_FILE = os.path.join(DATA_DIR, "Works Recommended_LokSabha_18.csv")
COMPLETED_WORKS_FILE = os.path.join(DATA_DIR, "Works Completed_LokSabha_18.csv")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Analytical Parameters
SANCTION_AMOUNT_FLOOR = 1000.0  # ₹1,000 minimum analytical floor
PEER_MIN_SIZE = 20              # Minimum state peer group size before national fallback
IQR_MULTIPLIER = 3.0            # Robust IQR deviation threshold (high-side only)
COST_OVERRUN_THRESHOLD = 0.10   # 10% threshold for actual expenditure > sanctioned

# Isolation Forest ML Parameters
IF_N_ESTIMATORS = 300
IF_CONTAMINATION = 0.05
RANDOM_STATE = 42

# Risk Classification Terminology
RISK_LEVEL_HIGH = "HIGH"
RISK_LEVEL_MEDIUM = "MEDIUM"
RISK_LEVEL_LOW = "LOW"
RISK_LEVEL_DATA_QUALITY = "DATA_QUALITY_REVIEW"

DISCLAIMER_TEXT = (
    "Statistical/financial anomaly requiring human investigation. "
    "Not proof of fraud or wrongdoing."
)

# Centralized Double-Dipping V2 Configuration
DOUBLE_DIPPING_V2_CONFIG = {
    "model_version": "double_dipping_v2",
    "semantic_weight": 0.35,
    "amount_weight": 0.20,
    "location_weight": 0.20,
    "vendor_weight": 0.15,
    "date_weight": 0.10,

    "high_risk_threshold": 85,
    "medium_risk_threshold": 70,

    "minimum_semantic_for_high": 0.75,
    "min_contextual_anchors_for_high": 2,
    "generic_description_dampening": 0.6,
    "convergence_bonus_multiplier": 1.10,

    "max_candidates": 5000,
    "embedding_model": "all-MiniLM-L6-v2",
    "image_similarity_available": False
}

# Alias for backwards compatibility
DOUBLE_DIPPING_CONFIG = DOUBLE_DIPPING_V2_CONFIG

# Model 3 — Delay Detection Parameters
DELAY_MIN_PEER_GROUP_SIZE = 10
DELAY_IQR_MULTIPLIER = 1.5
DEFAULT_REFERENCE_DATE = "2026-03-31"

# Model 4 — Compliance Parameters
COMPLIANCE_APPROVAL_DAYS = 45
COMPLIANCE_MINOR_MAX = 90
COMPLIANCE_MODERATE_MAX = 180
IA_WATCHLIST_MIN_WORKS = 20

# Model 5 — Audit Priority Aggregator Parameters (Weights sum exactly to 1.00)
AUDIT_COST_HIGH_WEIGHT = 0.30
AUDIT_COST_MEDIUM_WEIGHT = 0.10
AUDIT_DELAY_WEIGHT = 0.25
AUDIT_COMPLIANCE_WEIGHT = 0.25
AUDIT_VENDOR_RISK_WEIGHT = 0.10
MODEL_5_WEIGHT_SUM = 1.00

# Vendor-Agency Network Risk Parameters
VENDOR_HHI_HIGH_THRESHOLD = 0.25
VENDOR_TOP_SHARE_THRESHOLD = 0.60
VENDOR_FRAGMENTATION_WINDOW_DAYS = 7

# Expenditure Forecasting Parameters
LS17_DATA_DIR = os.path.join(BASE_DIR, "data", "original", "LokSabha17")
FORECAST_CONFIDENCE_INTERVAL = 0.95
FORECASTING_ENABLED = True
FORECAST_HORIZON_MONTHS = 6
MIN_FORECAST_OBSERVATIONS = 6

# Cross-House LS <-> RS Double-Dipping Parameters
CROSS_HOUSE_ENABLED = False
CROSS_HOUSE_STATUS_PENDING = "PENDING_RAJYA_SABHA_DATA"
CROSS_HOUSE_STATUS_READY = "READY"



