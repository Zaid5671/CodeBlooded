import re
import numpy as np
import pandas as pd
from ml.config import SANCTION_AMOUNT_FLOOR

def derive_clean_work_id(work_str):
    """
    Derives canonical clean_work_id string from raw Work or Work ID field.
    Normalizes tabs, spaces, and formatting around MP identifiers.
    Pattern: WS/MP<number>/<year-range>/<id_number>
    Example: 'WS/\t MP620/2024-2025/133166-Construction...' -> 'WS/MP620/2024-2025/133166'
    """
    if pd.isna(work_str) or not str(work_str).strip():
        return None
        
    s = str(work_str).strip()
    
    # Extract canonical WS/MP regex pattern with optional tabs/spaces
    match = re.search(r'WS/[^\d]*MP\s*(\d+)/(\d{4}-\d{4})/(\d+)', s, re.IGNORECASE)
    if match:
        mp_num, yr, item_id = match.group(1), match.group(2), match.group(3)
        return f"WS/MP{mp_num}/{yr}/{item_id}"
    
    # Generic regex fallback for WS/.../.../...
    match2 = re.search(r'WS/[^/]+/\d{4}-\d{4}/\d+', s, re.IGNORECASE)
    if match2:
        return re.sub(r'\s+', '', match2.group(0)).upper()
        
    parts = s.split('-')
    if len(parts) > 1 and 'WS/' in parts[0].upper():
        return re.sub(r'\s+', '', parts[0]).upper()
        
    return None

def derive_clean_work_id_details(work_str):
    """
    Returns tuple of (clean_work_id, work_id_parse_status, work_id_parse_reason).
    """
    cid = derive_clean_work_id(work_str)
    if cid is None:
        if pd.isna(work_str) or not str(work_str).strip():
            return None, "MISSING", "Work field is empty or null"
        else:
            return None, "INVALID_FORMAT", "No canonical WS/MP identifier found in string"
    return cid, "PARSED", "Canonical WS/MP pattern match"

def clean_monetary_field(series):
    """Parse numeric currency strings safely."""
    s = series.astype(str).str.replace(',', '', regex=False)
    s = s.str.replace('₹', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce')

def preprocess_sanctioned_works(df):
    """
    Clean and prepare sanctioned works dataframe for analytical processing.
    Extracts canonical clean_work_id, work_id_parse_status, work_id_parse_reason.
    Enforces Data Quality Floor (< ₹1,000).
    """
    df_clean = df.copy()
    
    # 1. Parse sanction amount
    if 'Sanction Amount ( ₹ )' in df_clean.columns:
        df_clean['sanction_amount'] = clean_monetary_field(df_clean['Sanction Amount ( ₹ )'])
    elif 'sanction_amount' in df_clean.columns:
        df_clean['sanction_amount'] = clean_monetary_field(df_clean['sanction_amount'])
    else:
        raise KeyError("Sanction Amount column not found in sanctioned works dataset.")
        
    # 2. Derive canonical clean_work_id (Check 'Work' column FIRST as it contains the WS/MP identifier)
    work_col = 'Work' if 'Work' in df_clean.columns else ('Work description' if 'Work description' in df_clean.columns else None)
    
    clean_ids, parse_statuses, parse_reasons = [], [], []
    
    for idx in range(len(df_clean)):
        val = df_clean[work_col].iloc[idx] if work_col else None
        cid, status, reason = derive_clean_work_id_details(val)
        
        if cid is None:
            cid = f"UNPARSED_SANC_{idx}"
            
        clean_ids.append(cid)
        parse_statuses.append(status)
        parse_reasons.append(reason)
        
    df_clean['clean_work_id'] = clean_ids
    df_clean['work_id'] = clean_ids
    df_clean['source_work_id'] = clean_ids
    df_clean['work_id_parse_status'] = parse_statuses
    df_clean['work_id_parse_reason'] = parse_reasons
        
    # 3. Parse Dates
    df_clean['rec_dt'] = pd.to_datetime(df_clean.get('Recommended date'), errors='coerce')
    df_clean['sanc_dt'] = pd.to_datetime(df_clean.get('Sanction Date'), errors='coerce')
    
    # Duration in days between recommendation and sanction
    df_clean['rec_to_sanc_days'] = (df_clean['sanc_dt'] - df_clean['rec_dt']).dt.days
    
    # Data Quality Floor Flag (< ₹1,000 floor or missing/negative)
    df_clean['is_below_floor'] = (
        df_clean['sanction_amount'].isnull() | 
        (df_clean['sanction_amount'] < SANCTION_AMOUNT_FLOOR) |
        (df_clean['sanction_amount'] < 0)
    )
    
    df_clean['data_quality_flag'] = np.where(
        df_clean['is_below_floor'],
        "IMPLAUSIBLE_SANCTION_AMOUNT",
        "VALID"
    )
    
    return df_clean
