import re
import os
import json
import pandas as pd
import numpy as np
from ml.config import OUTPUT_DIR, DISCLAIMER_TEXT

# Landmark / Location Prepositions
LOCATION_PREPOSITIONS = [
    r'\bnear\b', r'\bat\b', r'\bopp\b', r'\bopposite\b', r'\bpass\b', r'\bpas\b',
    r'\bbeside\b', r'\badjacent\b', r'\bnear to\b', r'\bnearby\b', r'\bon the way to\b',
    r'\bbehind\b', r'\bfront of\b', r'\bin front of\b', r'\btowards\b', r'\bvia\b'
]

# Civic / Eligible Work Types
CIVIC_WORK_TYPES = [
    'ROAD', 'CC ROAD', 'DRAIN', 'COMMUNITY HALL', 'HALL', 'SOLAR', 'LIGHT',
    'PAVER BLOCK', 'BOUNDARY WALL', 'WATER', 'SCHOOL', 'SHED', 'STAGE',
    'TOILET', 'WELL', 'PATHWAY', 'CULVERT', 'BRIDGE', 'BUILDING', 'ROOM',
    'ROOF', 'PLAYGROUND', 'PARK', 'LIBRARY', 'BOREWELL', 'PIPE', 'PIPELINE'
]

# Religious Keywords
RELIGIOUS_KEYWORDS = [
    'TEMPLE', 'MANDIR', 'MOSQUE', 'MASJID', 'CHURCH', 'GURUDWARA', 'ASHRAM',
    'DHARAMSHALA', 'SHIVALAYA', 'MATHA', 'MATH', 'KABRISTAN', 'GRAVEYARD',
    'IDGAH', 'MADRASA', 'PANDAL', 'SAMADHI', 'STUPA', 'MONASTERY'
]

def classify_inadmissible_work_description(description):
    """
    3-Stage Syntactic & Semantic Eligibility Classifier for Work Descriptions.
    
    Stage 1: Landmark Syntactic Role Filter
             Identifies religious terms used as geographical landmarks (e.g. 'near Mandir').
    Stage 2: Direct Inadmissible Object Detection
             Identifies works where the primary funded asset is religious.
    Stage 3: Ambiguous Candidate Classification
             Tags unclear descriptions requiring manual administrative review.
    """
    if not isinstance(description, str) or not description.strip():
        return {
            'status': 'UNKNOWN_MISSING_DESCRIPTION',
            'inadmissible_signal': False,
            'evidence': 'Missing or invalid work description text.',
            'category': 'VALID_CIVIC_WORK'
        }

    text_upper = description.upper()
    
    # Scan for raw religious keyword presence
    found_keywords = [kw for kw in RELIGIOUS_KEYWORDS if kw in text_upper]
    if not found_keywords:
        return {
            'status': 'VALID_CIVIC_WORK',
            'inadmissible_signal': False,
            'evidence': 'No inadmissible asset keywords detected.',
            'category': 'VALID_CIVIC_WORK'
        }

    # Check Stage 1: Location Landmark Preposition Check
    prep_regex = r'(' + '|'.join(LOCATION_PREPOSITIONS) + r')\s+.*(' + '|'.join([re.escape(kw) for kw in found_keywords]) + r')'
    is_location_landmark = bool(re.search(prep_regex, text_upper, re.IGNORECASE))

    # Check if primary work type is civic
    is_civic_work = any(cw in text_upper for cw in CIVIC_WORK_TYPES)

    if is_location_landmark and is_civic_work:
        return {
            'status': 'RELIGIOUS_TERM_AS_LOCATION_REFERENCE',
            'inadmissible_signal': False,
            'evidence': f"Religious term(s) [{', '.join(found_keywords)}] used as location landmark for civic work. Not flagged as inadmissible.",
            'category': 'LOCATION_LANDMARK_REFERENCE'
        }

    # Stage 2: Direct Religious Object Construction / Renovation
    direct_patterns = [
        r'CONSTRUCTION OF (TEMPLE|MANDIR|MOSQUE|MASJID|CHURCH|GURUDWARA|DHARAMSHALA|SHIVALAYA|MATHA|KABRISTAN)',
        r'RENOVATION OF (TEMPLE|MANDIR|MOSQUE|MASJID|CHURCH|GURUDWARA|DHARAMSHALA|SHIVALAYA|MATHA|KABRISTAN)',
        r'BEAUTIFICATION OF (TEMPLE|MANDIR|MOSQUE|MASJID|CHURCH|GURUDWARA|DHARAMSHALA|SHIVALAYA|MATHA|KABRISTAN)',
        r'REPAIR OF (TEMPLE|MANDIR|MOSQUE|MASJID|CHURCH|GURUDWARA|DHARAMSHALA|SHIVALAYA|MATHA|KABRISTAN)',
        r'BUILDING OF (TEMPLE|MANDIR|MOSQUE|MASJID|CHURCH|GURUDWARA|DHARAMSHALA|SHIVALAYA|MATHA|KABRISTAN)'
    ]
    
    is_direct_object = any(bool(re.search(pat, text_upper)) for pat in direct_patterns)
    
    if is_direct_object or (not is_civic_work and not is_location_landmark):
        return {
            'status': 'POTENTIALLY_INADMISSIBLE',
            'inadmissible_signal': True,
            'evidence': f"Primary funded asset appears to be religious structure [{', '.join(found_keywords)}]. Requires statutory audit review.",
            'category': 'DIRECT_RELIGIOUS_OBJECT'
        }

    # Stage 3: Ambiguous Candidate
    return {
        'status': 'AMBIGUOUS_REQUIRES_REVIEW',
        'inadmissible_signal': True,
        'evidence': f"Contains religious keyword(s) [{', '.join(found_keywords)}] with ambiguous syntactic context. Requires manual audit review.",
        'category': 'AMBIGUOUS_CANDIDATE'
    }

def run_inadmissible_work_detection(df_master):
    """
    MODULE 2 — Inadmissible Work / Eligibility Anomaly Engine.
    Evaluates master work entities for potentially inadmissible statutory expenditures.
    """
    df_m = df_master.copy()
    
    desc_col = 'description' if 'description' in df_m.columns else ('Work' if 'Work' in df_m.columns else 'work_name')
    
    records = []
    raw_mentions = 0
    landmark_mentions = 0
    direct_candidates = 0
    ambiguous_candidates = 0

    for idx, row in df_m.iterrows():
        cid = row.get('clean_work_id', row.get('master_work_id', row.get('work_id')))
        desc = str(row.get(desc_col, '')).strip()
        
        res = classify_inadmissible_work_description(desc)
        
        if any(kw in desc.upper() for kw in RELIGIOUS_KEYWORDS):
            raw_mentions += 1
            
        if res['status'] == 'RELIGIOUS_TERM_AS_LOCATION_REFERENCE':
            landmark_mentions += 1
        elif res['status'] == 'POTENTIALLY_INADMISSIBLE':
            direct_candidates += 1
        elif res['status'] == 'AMBIGUOUS_REQUIRES_REVIEW':
            ambiguous_candidates += 1
            
        records.append({
            'clean_work_id': cid,
            'inadmissible_signal': res['inadmissible_signal'],
            'eligibility_status': res['status'],
            'eligibility_category': res['category'],
            'eligibility_evidence': res['evidence'],
            'disclaimer': DISCLAIMER_TEXT
        })
        
    df_res = pd.DataFrame(records)
    
    final_potentially_inadmissible = direct_candidates + ambiguous_candidates
    
    summary = {
        'total_works_analyzed': len(df_m),
        'raw_religious_keyword_mentions': raw_mentions,
        'location_reference_mentions': landmark_mentions,
        'direct_religious_object_candidates': direct_candidates,
        'ambiguous_candidates': ambiguous_candidates,
        'final_potentially_inadmissible_count': final_potentially_inadmissible,
        'disclaimer': DISCLAIMER_TEXT
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "inadmissible_works_results.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    df_res.to_csv(os.path.join(OUTPUT_DIR, "inadmissible_works.csv"), index=False)
    
    return df_res, summary
