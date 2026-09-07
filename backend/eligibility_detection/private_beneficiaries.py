import os
import json
import re
import pandas as pd
import numpy as np
from cost_detection.config import OUTPUT_DIR, DISCLAIMER_TEXT

# Entity Classification Keywords
PRIVATE_COMMERCIAL_MARKERS = [
    r'\bPRIVATE\b', r'\bPVT\b', r'\bPVT LTD\b', r'\bPRIVATE LIMITED\b',
    r'\bCOMPANY\b', r'\bCOMMERCIAL\b', r'\bFACTORY\b', r'\bMALL\b',
    r'\bHOTEL\b', r'\bPLAZA\b', r'\bSHOPPING\b', r'\bFLAT\b', r'\bAPARTMENT\b',
    r'\bBUILDER\b', r'\bDEVELOPER\b', r'\bCORPORATE\b'
]

PUBLIC_GOVT_MARKERS = [
    r'\bGOVT\b', r'\bGOVERNMENT\b', r'\bZILLA PARISHAD\b', r'\bGRAM PANCHAYAT\b',
    r'\bMUNICIPAL\b', r'\bNIGAM\b', r'\bPWD\b', r'\bPUBLIC\b', r'\bSTATE\b',
    r'\bCENTRAL\b', r'\bDISTRICT\b', r'\bPOLICE\b', r'\bPRIMARY SCHOOL\b',
    r'\bHIGHER SECONDARY\b', r'\bPHC\b', r'\bCHC\b', r'\bANG ANWADI\b'
]

TRUST_NONPROFIT_MARKERS = [
    r'\bTRUST\b', r'\bSOCIETY\b', r'\bCLUB\b', r'\bNGO\b', r'\bASSOCIATION\b',
    r'\bFOUNDATION\b', r'\bSAMITI\b', r'\bSANSTHAN\b'
]

AMBIGUOUS_MARKERS = [
    r'\bSCHOOL\b', r'\bCOLLEGE\b', r'\bHOSPITAL\b', r'\bDISPENSARY\b'
]

def classify_entity_beneficiary(description, vendor_list=None):
    """
    Classifies entity beneficiary ownership from work description and vendor records.
    
    Categories:
        - GOVERNMENT_ENTITY
        - PRIVATE_OR_COMMERCIAL_CANDIDATE
        - NONPROFIT_TRUST_CANDIDATE
        - AMBIGUOUS_ENTITY
        - UNKNOWN_OWNERSHIP
    """
    text_upper = str(description).upper()
    
    # 1. Check for explicit public / government markers
    if any(bool(re.search(pat, text_upper)) for pat in PUBLIC_GOVT_MARKERS):
        return {
            'entity_category': 'GOVERNMENT_ENTITY',
            'private_beneficiary_signal': False,
            'status': 'GOVERNMENT_ENTITY',
            'evidence': 'Work description references public sector / government entity or facility.'
        }
        
    # 2. Check for explicit private / commercial markers
    is_private = any(bool(re.search(pat, text_upper)) for pat in PRIVATE_COMMERCIAL_MARKERS)
    
    if is_private:
        return {
            'entity_category': 'PRIVATE_OR_COMMERCIAL_CANDIDATE',
            'private_beneficiary_signal': True,
            'status': 'POTENTIAL PRIVATE/COMMERCIAL BENEFICIARY — REQUIRES REVIEW',
            'evidence': 'Work description contains explicit private or commercial entity markers. Requires audit verification of statutory admissibility.'
        }

    # 3. Check for nonprofit / trust markers
    if any(bool(re.search(pat, text_upper)) for pat in TRUST_NONPROFIT_MARKERS):
        return {
            'entity_category': 'NONPROFIT_TRUST_CANDIDATE',
            'private_beneficiary_signal': False,
            'status': 'NONPROFIT_TRUST_CANDIDATE',
            'evidence': 'Work description references trust, society, or non-profit association.'
        }

    # 4. Check for ambiguous markers (e.g. school/hospital without explicit ownership tag)
    if any(bool(re.search(pat, text_upper)) for pat in AMBIGUOUS_MARKERS):
        return {
            'entity_category': 'AMBIGUOUS_ENTITY',
            'private_beneficiary_signal': False,
            'status': 'AMBIGUOUS_ENTITY',
            'evidence': 'References educational or healthcare facility without explicit government/private ownership tag.'
        }

    # 5. Default: Unknown Ownership
    return {
        'entity_category': 'UNKNOWN_OWNERSHIP',
        'private_beneficiary_signal': False,
        'status': 'UNKNOWN_OWNERSHIP',
        'evidence': 'Ownership type cannot be definitively established from available text fields.'
    }

def run_private_beneficiary_detection(df_master):
    """
    MODULE 3 — Private / Commercial Beneficiary Detector.
    Scans master work entities for potential private/commercial beneficiary anomalies.
    """
    df_m = df_master.copy()
    desc_col = 'description' if 'description' in df_m.columns else ('Work' if 'Work' in df_m.columns else 'work_name')
    
    records = []
    category_counts = {
        'GOVERNMENT_ENTITY': 0,
        'PRIVATE_OR_COMMERCIAL_CANDIDATE': 0,
        'NONPROFIT_TRUST_CANDIDATE': 0,
        'AMBIGUOUS_ENTITY': 0,
        'UNKNOWN_OWNERSHIP': 0
    }
    
    for idx, row in df_m.iterrows():
        cid = row.get('clean_work_id', row.get('master_work_id', row.get('work_id')))
        desc = str(row.get(desc_col, '')).strip()
        v_list = row.get('vendors', [])
        
        res = classify_entity_beneficiary(desc, v_list)
        cat = res['entity_category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
        records.append({
            'clean_work_id': cid,
            'private_beneficiary_signal': res['private_beneficiary_signal'],
            'entity_category': cat,
            'beneficiary_status': res['status'],
            'beneficiary_evidence': res['evidence'],
            'disclaimer': DISCLAIMER_TEXT
        })
        
    df_res = pd.DataFrame(records)
    
    summary = {
        'total_works_analyzed': len(df_m),
        'category_breakdown': category_counts,
        'private_commercial_candidate_count': category_counts['PRIVATE_OR_COMMERCIAL_CANDIDATE'],
        'limitations': 'Entity classification is derived from text heuristics. An authoritative government institutional registry is not currently available in MPLADS dataset.',
        'disclaimer': DISCLAIMER_TEXT
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "private_beneficiaries_results.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    df_res.to_csv(os.path.join(OUTPUT_DIR, "private_beneficiaries.csv"), index=False)
    
    return df_res, summary
