import re
import numpy as np
import pandas as pd
from .config import SANCTION_AMOUNT_FLOOR

def derive_work_id(work_str):
    """
    Derives the canonical Work ID string from the raw Work description.
    Pattern: WS/MP<number>/<year-range>/<id_number>
    Example: 'WS/\t MP620/2024-2025/133166-Construction...' -> 'WS/MP620/2024-2025/133166'
    """
    if pd.isna(work_str):
        return None
    s = str(work_str).strip()
    match = re.search(r'WS/[^/]+/\d{4}-\d{4}/\d+', s, re.IGNORECASE)
    if match:
        return re.sub(r'\s+', '', match.group(0)).upper()
    parts = s.split('-')
    if len(parts) > 1:
        return re.sub(r'\s+', '', parts[0]).upper()
    return re.sub(r'\s+', '', s).upper()

def clean_monetary_field(series):
    """Parse numeric currency strings safely."""
    s = series.astype(str).str.replace(',', '', regex=False)
    s = s.str.replace('₹', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce')

def preprocess_sanctioned_works(df):
    """
    Clean and prepare sanctioned works dataframe for analytical processing.
    """
    df_clean = df.copy()
    
    # 1. Parse sanction amount
    if 'Sanction Amount ( ₹ )' in df_clean.columns:
        df_clean['sanction_amount'] = clean_monetary_field(df_clean['Sanction Amount ( ₹ )'])
    elif 'sanction_amount' not in df_clean.columns:
        raise KeyError("Sanction Amount column not found.")
        
    # 2. Derive canonical Work ID
    if 'Work' in df_clean.columns:
        df_clean['work_id'] = df_clean['Work'].apply(derive_work_id)
    else:
        df_clean['work_id'] = [f"WORK_SANC_{i}" for i in range(len(df_clean))]
        
    # 3. Parse Dates
    df_clean['rec_dt'] = pd.to_datetime(df_clean['Recommended date'], errors='coerce')
    df_clean['sanc_dt'] = pd.to_datetime(df_clean['Sanction Date'], errors='coerce')
    
    # Duration in days between recommendation and sanction
    df_clean['rec_to_sanc_days'] = (df_clean['sanc_dt'] - df_clean['rec_dt']).dt.days
    
    # Data Quality Floor Flag
    df_clean['is_below_floor'] = (
        df_clean['sanction_amount'].isnull() | 
        (df_clean['sanction_amount'] < SANCTION_AMOUNT_FLOOR)
    )
    
    df_clean['data_quality_flag'] = np.where(
        df_clean['is_below_floor'],
        "IMPLAUSIBLE_SANCTION_AMOUNT",
        "VALID"
    )
    
    return df_clean
