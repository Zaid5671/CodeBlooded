import re
import pandas as pd
from feature_engineering.nlp_text_processor import clean_nlp_text

def normalize_text_for_dup(text):
    """Normalize text for duplicate detection using NLP text processing rules."""
    return clean_nlp_text(text)

def evaluate_duplicate_works(df):
    """
    Phase 14: Duplicate Work Detector.
    Identifies works with identical normalized description within the same Constituency.
    Flags records as POTENTIAL_DUPLICATE_WORK.
    """
    df_out = df.copy()
    df_out['potential_duplicate_flag'] = False
    df_out['duplicate_status'] = 'UNIQUE'

    work_col = 'Work description' if 'Work description' in df_out.columns else ('Work' if 'Work' in df_out.columns else None)
    if not work_col or 'Constituency' not in df_out.columns:
        return df_out

    df_out['norm_desc'] = df_out[work_col].apply(normalize_text_for_dup)
    
    # Filter non-empty descriptions
    valid_mask = (df_out['norm_desc'] != "") & df_out['Constituency'].notnull()
    
    # Find duplicates grouped by (Constituency, norm_desc)
    dup_groups = df_out[valid_mask].groupby(['Constituency', 'norm_desc']).size()
    dup_keys = set(dup_groups[dup_groups > 1].index)

    for idx, row in df_out.iterrows():
        key = (row.get('Constituency'), row.get('norm_desc'))
        if key in dup_keys:
            df_out.at[idx, 'potential_duplicate_flag'] = True
            df_out.at[idx, 'duplicate_status'] = 'POTENTIAL_DUPLICATE_WORK'

    df_out.drop(columns=['norm_desc'], inplace=True, errors='ignore')
    return df_out
