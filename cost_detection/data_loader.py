import os
import pandas as pd
from .config import (
    SANCTIONED_WORKS_FILE,
    EXPENDITURE_WORKS_FILE,
    RECOMMENDED_WORKS_FILE,
    COMPLETED_WORKS_FILE,
)

def load_sanctioned_works(filepath=None):
    """Load the primary analytical dataset (Works Sanctioned_LokSabha_18.csv)."""
    path = filepath or SANCTIONED_WORKS_FILE
    if not os.path.exists(path):
        raise FileNotFoundError(f"Sanctioned works file not found at: {path}")
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df

def load_expenditure_works(filepath=None):
    """Load the expenditure matching dataset (Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv)."""
    path = filepath or EXPENDITURE_WORKS_FILE
    if not os.path.exists(path):
        raise FileNotFoundError(f"Expenditure works file not found at: {path}")
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df

def load_recommended_works(filepath=None):
    """Load recommended works dataset if available for cross-referencing."""
    path = filepath or RECOMMENDED_WORKS_FILE
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df

def load_completed_works(filepath=None):
    """Load completed works dataset for validation/cross-referencing."""
    path = filepath or COMPLETED_WORKS_FILE
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df
