import os
import glob
import pandas as pd
from ml.config import (
    SANCTIONED_WORKS_FILE,
    EXPENDITURE_WORKS_FILE,
    RECOMMENDED_WORKS_FILE,
    COMPLETED_WORKS_FILE,
)

def _find_csv(primary_path, file_patterns, folder_hints):
    """Smart helper to find CSV files across primary path, manual upload folders, and /content."""
    if primary_path and os.path.exists(primary_path):
        return primary_path

    # Search in folder hints
    for folder in folder_hints:
        if os.path.exists(folder):
            for pattern in file_patterns:
                matches = glob.glob(os.path.join(folder, pattern))
                if matches:
                    return matches[0]
                matches_rec = glob.glob(os.path.join(folder, "**", pattern), recursive=True)
                if matches_rec:
                    return matches_rec[0]

    # Search current directory and /content recursively
    for pattern in file_patterns:
        matches = glob.glob(pattern) + glob.glob(os.path.join("/content", pattern))
        if matches:
            return matches[0]
        matches_rec = glob.glob(os.path.join("/content", "**", pattern), recursive=True)
        if matches_rec:
            return matches_rec[0]

    return primary_path

def load_sanctioned_works(filepath=None):
    """Load the primary analytical dataset (Works Sanctioned CSV)."""
    folder_hints = ["data/original/LokSabha18", "LokSabha18", "/content/LokSabha18", "/content"]
    file_patterns = ["*Works*Sanctioned*.csv", "*Works_Sanctioned*.csv", "*Sanctioned*.csv"]

    target_path = _find_csv(filepath or SANCTIONED_WORKS_FILE, file_patterns, folder_hints)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Sanctioned works file not found at: {target_path}")
    df = pd.read_csv(target_path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df

def load_expenditure_works(filepath=None):
    """Load the expenditure matching dataset."""
    folder_hints = ["data/original/LokSabha18", "LokSabha18", "/content/LokSabha18", "/content"]
    file_patterns = ["*Expenditure*.csv", "*Expenditure_on_Completed*.csv"]

    target_path = _find_csv(filepath or EXPENDITURE_WORKS_FILE, file_patterns, folder_hints)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Expenditure works file not found at: {target_path}")
    df = pd.read_csv(target_path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df

def load_recommended_works(filepath=None):
    """Load recommended works dataset if available for cross-referencing."""
    folder_hints = ["data/original/LokSabha18", "LokSabha18", "/content/LokSabha18", "/content"]
    file_patterns = ["*Works*Recommended*.csv", "*Recommended*.csv"]

    target_path = _find_csv(filepath or RECOMMENDED_WORKS_FILE, file_patterns, folder_hints)
    if not os.path.exists(target_path):
        return None
    df = pd.read_csv(target_path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df

def load_completed_works(filepath=None):
    """Load completed works dataset for validation/cross-referencing."""
    folder_hints = ["data/original/LokSabha18", "LokSabha18", "/content/LokSabha18", "/content"]
    file_patterns = ["*Works*Completed*.csv", "*Completed*.csv"]

    target_path = _find_csv(filepath or COMPLETED_WORKS_FILE, file_patterns, folder_hints)
    if not os.path.exists(target_path):
        return None
    df = pd.read_csv(target_path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df
