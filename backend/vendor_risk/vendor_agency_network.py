import os
import re
import json
import math
import pandas as pd
import numpy as np
from cost_detection.config import (
    OUTPUT_DIR,
    VENDOR_HHI_HIGH_THRESHOLD,
    VENDOR_TOP_SHARE_THRESHOLD,
    VENDOR_FRAGMENTATION_WINDOW_DAYS,
)
from cost_detection.data_loader import load_expenditure_works
from cost_detection.preprocessing import derive_clean_work_id, clean_monetary_field

GOVT_VENDOR_PATTERNS = [
    r'DISTRICT ENGINEER', r'EXECUTIVE ENGINEER', r'NIRMITHI KENDRA', r'NIRMITI KENDRA',
    r'ZILLA PARISHAD', r'PUBLIC WORKS', r'PWD', r'DEPUTY COMMISSIONER', r'DISTRICT COLLECTOR',
    r'MUNICIPAL', r'CORPORATION', r'DEPARTMENT', r'DIVISION', r'PANCHAYAT SAMITI',
    r'BLOCK DEVELOPMENT', r'STATE ELECTRICITY', r'ASSAM ELECTRICITY', r'BOARD', r'AUTHORITY'
]

PRIVATE_VENDOR_PATTERNS = [
    r'\bPVT\b', r'\bPRIVATE\b', r'\bLTD\b', r'\bLIMITED\b', r'\bINFRA\b', r'\bINFRATECH\b',
    r'\bCONSTRUCTION\b', r'\bCONSTRUCTIONS\b', r'\bENTERPRISES\b', r'\bBUILDERS\b', r'\bASSOCIATES\b'
]

def normalize_vendor_name_advanced(vendor_str):
    if pd.isna(vendor_str) or not str(vendor_str).strip():
        return ""
    v = str(vendor_str).upper().strip()
    v = re.sub(r'[\t\r\n]+', ' ', v)
    v = re.sub(r'\s+', ' ', v)
    return v

def classify_vendor_entity_type(vendor_name):
    if not vendor_name or vendor_name.upper() == 'NAN':
        return "UNKNOWN"
        
    v_upper = vendor_name.upper()
    for pat in GOVT_VENDOR_PATTERNS:
        if re.search(pat, v_upper):
            return "GOVERNMENT_ENTITY"
            
    for pat in PRIVATE_VENDOR_PATTERNS:
        if re.search(pat, v_upper):
            return "PRIVATE_ENTITY"
            
    return "UNKNOWN"

def run_vendor_agency_network_analysis(df_master=None, data_dir="data/original/LokSabha18"):
    """
    Vendor–Agency Network Risk Analyzer
    Evaluates vendor concentration (HHI), government entity protection, payment structuring,
    and bipartite IA-Vendor network features.
    
    Returns:
        df_ia_risk: pd.DataFrame with IA-level concentration & network metrics.
        summary: dict with top-level network metrics.
    """
    # Load expenditure records
    df_exp = load_expenditure_works(os.path.join(data_dir, "Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv"))
    
    df_exp['clean_exp_amt'] = clean_monetary_field(df_exp['Fund Disbursed Amount ( ₹ )']).fillna(0.0)
    df_exp['clean_work_id'] = [derive_clean_work_id(w) for w in df_exp['Work ID' if 'Work ID' in df_exp.columns else 'Work']]
    df_exp['ida_clean'] = df_exp['IDA'].fillna('').astype(str).str.strip() if 'IDA' in df_exp.columns else ""
    df_exp['vendor_orig'] = df_exp['Vendor Name'].fillna('').astype(str).str.strip() if 'Vendor Name' in df_exp.columns else ""
    df_exp['vendor_norm'] = [normalize_vendor_name_advanced(v) for v in df_exp['vendor_orig']]
    df_exp['exp_dt'] = pd.to_datetime(df_exp.get('Expenditure Date'), errors='coerce')
    
    # Filter valid expenditure rows
    valid_exp = df_exp[df_exp['ida_clean'].str.len() > 0].copy()
    
    # -------------------------------------------------------------------------
    # 1. PAYMENT STRUCTURING / FRAGMENTATION (Same IA + Vendor + Short Window)
    # -------------------------------------------------------------------------
    frag_records = []
    grouped_ia_v = valid_exp.groupby(['ida_clean', 'vendor_norm'])
    
    for (ida_name, v_name), group in grouped_ia_v:
        if not v_name or len(group) < 2:
            continue
        g_sorted = group.sort_values('exp_dt').dropna(subset=['exp_dt'])
        if len(g_sorted) >= 2:
            d_diffs = g_sorted['exp_dt'].diff().dt.days
            short_gaps = d_diffs[d_diffs <= VENDOR_FRAGMENTATION_WINDOW_DAYS]
            if len(short_gaps) > 0:
                frag_records.append({
                    'ida': ida_name,
                    'vendor_norm': v_name,
                    'fragmented_transactions': len(short_gaps) + 1,
                    'total_amt': group['clean_exp_amt'].sum()
                })
                
    df_frag = pd.DataFrame(frag_records)
    frag_ia_set = set(df_frag['ida']) if not df_frag.empty else set()
    
    # -------------------------------------------------------------------------
    # 2. IA LEVEL VENDOR CONCENTRATION & HHI
    # -------------------------------------------------------------------------
    ia_stats = []
    grouped_ia = valid_exp.groupby('ida_clean')
    
    for ida_name, group in grouped_ia:
        tot_exp = float(group['clean_exp_amt'].sum())
        work_cnt = len(group['clean_work_id'].dropna().unique())
        tx_cnt = len(group)
        state_val = str(group['State'].iloc[0]).strip() if 'State' in group.columns else ""
        
        # Vendor breakdown
        v_group = group.groupby('vendor_norm')['clean_exp_amt'].sum()
        unique_vendors_count = len(v_group[v_group.index != ''])
        
        if unique_vendors_count > 0 and tot_exp > 0:
            top_vendor_name = v_group.idxmax()
            top_vendor_amt = float(v_group.max())
            top_vendor_share = float(top_vendor_amt / tot_exp)
            
            # HHI calculation
            shares = (v_group / tot_exp)
            hhi = float((shares ** 2).sum())
        else:
            top_vendor_name = "N/A"
            top_vendor_amt = 0.0
            top_vendor_share = 0.0
            hhi = 0.0
            
        entity_type = classify_vendor_entity_type(top_vendor_name)
        
        # Concentration Risk
        has_conc_risk = bool(top_vendor_share >= VENDOR_TOP_SHARE_THRESHOLD and work_cnt >= 5 and unique_vendors_count > 1)
        has_frag_risk = bool(ida_name in frag_ia_set)
        
        evidence = []
        if has_conc_risk:
            if entity_type == "GOVERNMENT_ENTITY":
                evidence.append(f"High expenditure concentration ({top_vendor_share*100:.1f}%) associated with a government/entity vendor ('{top_vendor_name}'); concentration alone does not establish irregularity.")
            else:
                evidence.append(f"High vendor concentration detected: Top vendor ('{top_vendor_name}') accounts for {top_vendor_share*100:.1f}% of total IA expenditure (HHI: {hhi:.3f}).")
                
        if has_frag_risk:
            evidence.append("Multiple transactions to the same vendor occurred within a 7-day window (potential payment structuring/fragmentation).")
            
        if not evidence:
            evidence.append("Vendor allocation across implementing agency shows normal distribution.")
            
        # Network Risk Score
        raw_net_score = (hhi * 0.5) + (top_vendor_share * 0.3) + (0.2 if has_frag_risk else 0.0)
        if entity_type == "GOVERNMENT_ENTITY":
            raw_net_score *= 0.5  # Dampen score for public/government bodies
            
        net_score = round(min(1.00, raw_net_score), 4)
        
        ia_stats.append({
            'implementing_agency': ida_name,
            'state': state_val,
            'total_expenditure': tot_exp,
            'work_count': work_cnt,
            'transaction_count': tx_cnt,
            'unique_vendors': unique_vendors_count,
            'top_vendor': top_vendor_name,
            'top_vendor_amount': top_vendor_amt,
            'top_vendor_share': round(top_vendor_share, 4),
            'hhi_index': round(hhi, 4),
            'top_vendor_entity_type': entity_type,
            'concentration_risk': has_conc_risk,
            'payment_structuring_risk': has_frag_risk,
            'network_risk_score': net_score,
            'evidence': evidence
        })
        
    df_ia_risk = pd.DataFrame(ia_stats)
    df_ia_risk = df_ia_risk.sort_values(by=['network_risk_score', 'total_expenditure'], ascending=[False, False]).reset_index(drop=True)
    
    summary = {
        'total_implementing_agencies_analyzed': len(df_ia_risk),
        'high_concentration_agencies': int(df_ia_risk['concentration_risk'].sum()),
        'payment_structuring_candidate_agencies': int(df_ia_risk['payment_structuring_risk'].sum()),
        'government_entity_vendors': int((df_ia_risk['top_vendor_entity_type'] == 'GOVERNMENT_ENTITY').sum()),
        'private_entity_vendors': int((df_ia_risk['top_vendor_entity_type'] == 'PRIVATE_ENTITY').sum()),
        'disclaimer': "Vendor concentration and network analysis identify structural patterns for administrative audit review. They do not prove collusion or fraud."
    }
    
    return df_ia_risk, summary
