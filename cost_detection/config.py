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
