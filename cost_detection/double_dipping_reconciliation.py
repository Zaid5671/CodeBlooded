import os
import re
import pandas as pd
import numpy as np
from .preprocessing import derive_clean_work_id, clean_monetary_field

def load_and_reconcile_lifecycle_data(data_dir="data/original/LokSabha18"):
    """
    Loads MPLADS datasets across lifecycle stages (Recommended, Sanctioned, Expenditure, Completed)
    and reconciles them into unified MasterWorkEntity records using fast vectorized operations.
    
    Returns:
        df_master: pd.DataFrame of master work entities
        reco_summary: dict of reconciliation statistics
    """
    sanctioned_path = os.path.join(data_dir, "Works Sanctioned_LokSabha_18.csv")
    expenditure_path = os.path.join(data_dir, "Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv")
    recommended_path = os.path.join(data_dir, "Works Recommended_LokSabha_18.csv")
    completed_path = os.path.join(data_dir, "Works Completed_LokSabha_18.csv")
    
    # Load raw dataframes safely
    df_sanc = pd.read_csv(sanctioned_path, low_memory=False) if os.path.exists(sanctioned_path) else pd.DataFrame()
    df_exp = pd.read_csv(expenditure_path, low_memory=False) if os.path.exists(expenditure_path) else pd.DataFrame()
    df_reco = pd.read_csv(recommended_path, low_memory=False) if os.path.exists(recommended_path) else pd.DataFrame()
    df_comp = pd.read_csv(completed_path, low_memory=False) if os.path.exists(completed_path) else pd.DataFrame()

    entity_dict = {}
    exact_id_matches = 0
    fallback_matches = 0
    unmatched_records = 0

    # 1. Process Sanctioned Works (Primary backbone)
    sanc_count = len(df_sanc)
    if not df_sanc.empty:
        work_col = 'Work' if 'Work' in df_sanc.columns else 'Work description'
        desc_col = 'Work description' if 'Work description' in df_sanc.columns else 'Work'
        
        df_sanc['clean_sanc_amt'] = clean_monetary_field(df_sanc['Sanction Amount ( ₹ )']).fillna(0.0)
        cids = [derive_clean_work_id(w) for w in df_sanc[work_col]]
        
        st_series = df_sanc['State'].fillna('').astype(str).str.strip()
        cn_series = df_sanc['Constituency'].fillna('').astype(str).str.strip()
        mp_series = df_sanc["Hon'ble Members of Parliament"].fillna('').astype(str).str.strip() if "Hon'ble Members of Parliament" in df_sanc.columns else ""
        ida_series = df_sanc['IDA'].fillna('').astype(str).str.strip() if 'IDA' in df_sanc.columns else ""
        cat_series = df_sanc['Work category'].fillna('OTHER').astype(str).str.strip() if 'Work category' in df_sanc.columns else 'OTHER'
        desc_series = df_sanc[desc_col].fillna('').astype(str).str.strip()
        work_name_series = df_sanc[work_col].fillna('').astype(str).str.strip()
        dt_series = df_sanc['Sanction Date'].fillna('').astype(str).str.strip() if 'Sanction Date' in df_sanc.columns else ""
        rec_dt_series = df_sanc['Recommended date'].fillna('').astype(str).str.strip() if 'Recommended date' in df_sanc.columns else ""
        status_series = df_sanc['Work Status'].fillna('SANCTIONED').astype(str).str.strip() if 'Work Status' in df_sanc.columns else "SANCTIONED"

        desc_prefix = desc_series.str.lower().str.replace(r'[^a-z0-9]', '', regex=True).str[:40]
        amt_rounded = df_sanc['clean_sanc_amt'].round(-3).astype(int).astype(str)
        comp_keys = "COMP_" + st_series.str.upper() + "_" + cn_series.str.upper() + "_" + desc_prefix + "_" + amt_rounded

        for idx in range(sanc_count):
            cid = cids[idx]
            key = cid if cid else comp_keys.iloc[idx]
            sanc_amt = float(df_sanc['clean_sanc_amt'].iloc[idx])
            
            if cid:
                exact_id_matches += 1
            else:
                fallback_matches += 1

            if key not in entity_dict:
                entity_dict[key] = {
                    'master_work_id': f"ENT_{len(entity_dict)+1:06d}",
                    'canonical_work_id': cid if cid else key,
                    'is_canonical_id': bool(cid),
                    'linkage_confidence': 'EXACT_ID' if cid else 'STRONG_COMPOSITE_MATCH',
                    'work_name': work_name_series.iloc[idx],
                    'description': desc_series.iloc[idx],
                    'work_category': cat_series.iloc[idx] if isinstance(cat_series, pd.Series) else cat_series,
                    'state': st_series.iloc[idx],
                    'constituency': cn_series.iloc[idx],
                    'mp': mp_series.iloc[idx] if isinstance(mp_series, pd.Series) else mp_series,
                    'ida': ida_series.iloc[idx] if isinstance(ida_series, pd.Series) else ida_series,
                    'sanction_amount': sanc_amt,
                    'recommended_amount': sanc_amt,
                    'expenditure_amount': 0.0,
                    'completed_amount': 0.0,
                    'vendors': set(),
                    'payment_status': 'SANCTIONED',
                    'sanction_date': dt_series.iloc[idx] if isinstance(dt_series, pd.Series) else dt_series,
                    'recommended_date': rec_dt_series.iloc[idx] if isinstance(rec_dt_series, pd.Series) else rec_dt_series,
                    'completion_date': '',
                    'expenditure_dates': set(),
                    'lifecycle_status': status_series.iloc[idx] if isinstance(status_series, pd.Series) else status_series,
                    'stages_present': {'sanctioned'},
                    'source_datasets': ['Works Sanctioned']
                }
            else:
                entity_dict[key]['stages_present'].add('sanctioned')
                entity_dict[key]['source_datasets'].append('Works Sanctioned')
                if sanc_amt > entity_dict[key]['sanction_amount']:
                    entity_dict[key]['sanction_amount'] = sanc_amt

    # 2. Reconcile Expenditure Works (AGGREGATE BEFORE JOINING)
    exp_count = len(df_exp)
    if not df_exp.empty:
        exp_w_col = 'Work ID' if 'Work ID' in df_exp.columns else 'Work'
        df_exp['clean_exp_amt'] = clean_monetary_field(df_exp['Fund Disbursed Amount ( ₹ )']).fillna(0.0)
        cids_exp = [derive_clean_work_id(w) for w in df_exp[exp_w_col]]
        
        st_exp = df_exp['State'].fillna('').astype(str).str.strip()
        cn_exp = df_exp['Constituency'].fillna('').astype(str).str.strip()
        mp_exp = df_exp["Hon'ble Members of Parliament"].fillna('').astype(str).str.strip() if "Hon'ble Members of Parliament" in df_exp.columns else ""
        ida_exp = df_exp['IDA'].fillna('').astype(str).str.strip() if 'IDA' in df_exp.columns else ""
        desc_exp = df_exp['Work'].fillna('').astype(str).str.strip()
        vendor_exp = df_exp['Vendor Name'].fillna('').astype(str).str.strip() if 'Vendor Name' in df_exp.columns else ""
        pay_status_exp = df_exp['Payment Status'].fillna('').astype(str).str.strip() if 'Payment Status' in df_exp.columns else ""
        dt_exp = df_exp['Expenditure Date'].fillna('').astype(str).str.strip() if 'Expenditure Date' in df_exp.columns else ""

        desc_prefix_exp = desc_exp.str.lower().str.replace(r'[^a-z0-9]', '', regex=True).str[:40]
        amt_rounded_exp = df_exp['clean_exp_amt'].round(-3).astype(int).astype(str)
        comp_keys_exp = "COMP_" + st_exp.str.upper() + "_" + cn_exp.str.upper() + "_" + desc_prefix_exp + "_" + amt_rounded_exp

        for idx in range(exp_count):
            cid = cids_exp[idx]
            key = cid if cid else comp_keys_exp.iloc[idx]
            exp_amt = float(df_exp['clean_exp_amt'].iloc[idx])
            v_name = vendor_exp.iloc[idx] if isinstance(vendor_exp, pd.Series) else vendor_exp
            e_date = dt_exp.iloc[idx] if isinstance(dt_exp, pd.Series) else dt_exp
            p_stat = pay_status_exp.iloc[idx] if isinstance(pay_status_exp, pd.Series) else pay_status_exp

            if key in entity_dict:
                entity_dict[key]['stages_present'].add('expenditure')
                entity_dict[key]['source_datasets'].append('Expenditure')
                entity_dict[key]['expenditure_amount'] += exp_amt
                if p_stat:
                    entity_dict[key]['payment_status'] = p_stat
                if v_name and v_name.upper() != 'NAN':
                    entity_dict[key]['vendors'].add(v_name)
                if e_date and e_date.upper() != 'NAN':
                    entity_dict[key]['expenditure_dates'].add(e_date)
            else:
                unmatched_records += 1
                entity_dict[key] = {
                    'master_work_id': f"ENT_{len(entity_dict)+1:06d}",
                    'canonical_work_id': cid if cid else key,
                    'is_canonical_id': bool(cid),
                    'linkage_confidence': 'EXACT_ID' if cid else 'UNLINKED',
                    'work_name': desc_exp.iloc[idx],
                    'description': desc_exp.iloc[idx],
                    'work_category': 'OTHER',
                    'state': st_exp.iloc[idx],
                    'constituency': cn_exp.iloc[idx],
                    'mp': mp_exp.iloc[idx] if isinstance(mp_exp, pd.Series) else mp_exp,
                    'ida': ida_exp.iloc[idx] if isinstance(ida_exp, pd.Series) else ida_exp,
                    'sanction_amount': 0.0,
                    'recommended_amount': 0.0,
                    'expenditure_amount': exp_amt,
                    'completed_amount': 0.0,
                    'vendors': {v_name} if (v_name and v_name.upper() != 'NAN') else set(),
                    'payment_status': p_stat if p_stat else 'EXPENDITURE_RECORDED',
                    'sanction_date': '',
                    'recommended_date': '',
                    'completion_date': '',
                    'expenditure_dates': {e_date} if (e_date and e_date.upper() != 'NAN') else set(),
                    'lifecycle_status': 'EXPENDITURE_RECORDED',
                    'stages_present': {'expenditure'},
                    'source_datasets': ['Expenditure']
                }

    # 3. Process Completed Works
    comp_count = len(df_comp)
    if not df_comp.empty and 'Work Description' in df_comp.columns:
        df_comp['clean_comp_amt'] = clean_monetary_field(df_comp['Amount Disbursed ( ₹ )']).fillna(0.0)
        cids_comp = [derive_clean_work_id(w) for w in df_comp['Work']]
        st_comp = df_comp['State'].fillna('').astype(str).str.strip()
        cn_comp = df_comp['Constituency'].fillna('').astype(str).str.strip()
        desc_comp = df_comp['Work Description'].fillna('').astype(str).str.strip()
        dt_comp = df_comp['Completion Date'].fillna('').astype(str).str.strip() if 'Completion Date' in df_comp.columns else ""

        desc_prefix_comp = desc_comp.str.lower().str.replace(r'[^a-z0-9]', '', regex=True).str[:40]
        amt_rounded_comp = df_comp['clean_comp_amt'].round(-3).astype(int).astype(str)
        comp_keys_comp = "COMP_" + st_comp.str.upper() + "_" + cn_comp.str.upper() + "_" + desc_prefix_comp + "_" + amt_rounded_comp

        for idx in range(comp_count):
            cid = cids_comp[idx]
            key = cid if cid else comp_keys_comp.iloc[idx]
            c_date = dt_comp.iloc[idx] if isinstance(dt_comp, pd.Series) else dt_comp
            c_amt = float(df_comp['clean_comp_amt'].iloc[idx])
            if key in entity_dict:
                entity_dict[key]['stages_present'].add('completed')
                entity_dict[key]['source_datasets'].append('Works Completed')
                entity_dict[key]['completed_amount'] = max(entity_dict[key]['completed_amount'], c_amt)
                if c_date and c_date.upper() != 'NAN':
                    entity_dict[key]['completion_date'] = c_date

    # 4. Process Recommended Works
    reco_count = len(df_reco)
    if not df_reco.empty:
        reco_w_col = 'WORK' if 'WORK' in df_reco.columns else 'Work description'
        df_reco['clean_reco_amt'] = clean_monetary_field(df_reco['RECOMMENDED AMOUNT   ( ₹ )']).fillna(0.0)
        cids_reco = [derive_clean_work_id(w) for w in df_reco[reco_w_col]]
        st_reco = df_reco['State'].fillna('').astype(str).str.strip()
        cn_reco = df_reco['Constituency'].fillna('').astype(str).str.strip()
        desc_reco = df_reco['Work description'].fillna('').astype(str).str.strip() if 'Work description' in df_reco.columns else ""

        desc_prefix_reco = desc_reco.str.lower().str.replace(r'[^a-z0-9]', '', regex=True).str[:40]
        amt_rounded_reco = df_reco['clean_reco_amt'].round(-3).astype(int).astype(str)
        comp_keys_reco = "COMP_" + st_reco.str.upper() + "_" + cn_reco.str.upper() + "_" + desc_prefix_reco + "_" + amt_rounded_reco

        for idx in range(reco_count):
            cid = cids_reco[idx]
            key = cid if cid else comp_keys_reco.iloc[idx]
            r_amt = float(df_reco['clean_reco_amt'].iloc[idx])
            if key in entity_dict:
                entity_dict[key]['stages_present'].add('recommended')
                entity_dict[key]['source_datasets'].append('Works Recommended')
                entity_dict[key]['recommended_amount'] = max(entity_dict[key]['recommended_amount'], r_amt)

    # 5. Build Master Dataframe
    master_records = []
    for key, ent in entity_dict.items():
        master_records.append({
            'master_work_id': ent['master_work_id'],
            'entity_id': ent['master_work_id'],
            'clean_work_id': ent['canonical_work_id'],
            'canonical_work_id': ent['canonical_work_id'],
            'is_canonical_id': ent['is_canonical_id'],
            'linkage_confidence': ent['linkage_confidence'],
            'work_name': ent['work_name'],
            'description': ent['description'],
            'work_category': ent['work_category'],
            'category': ent['work_category'],
            'state': ent['state'],
            'constituency': ent['constituency'],
            'mp': ent['mp'],
            'ida': ent['ida'],
            'sanction_amount': ent['sanction_amount'],
            'recommended_amount': ent['recommended_amount'],
            'expenditure_amount': ent['expenditure_amount'],
            'completed_amount': ent['completed_amount'],
            'primary_vendor': next(iter(ent['vendors']), '') if ent['vendors'] else '',
            'all_vendors': list(ent['vendors']),
            'vendors': list(ent['vendors']),
            'payment_status': ent['payment_status'],
            'sanction_date': ent['sanction_date'],
            'recommended_date': ent['recommended_date'],
            'completion_date': ent['completion_date'],
            'expenditure_date': next(iter(ent['expenditure_dates']), '') if ent['expenditure_dates'] else '',
            'expenditure_dates': list(ent['expenditure_dates']),
            'work_status': ent['lifecycle_status'],
            'lifecycle_status': ent['lifecycle_status'],
            'stages_present': list(ent['stages_present']),
            'stage_count': len(ent['stages_present']),
            'source_datasets': list(set(ent['source_datasets']))
        })
        
    df_master = pd.DataFrame(master_records)
    
    reco_summary = {
        'sanctioned_records': sanc_count,
        'expenditure_records': exp_count,
        'recommended_records': reco_count,
        'completed_records': comp_count,
        'master_entities': len(df_master),
        'unique_master_work_entities': len(df_master),
        'lifecycle_reconciled_entities': int((df_master['stage_count'] > 1).sum()),
        'exact_id_matches': exact_id_matches,
        'fallback_matches': fallback_matches,
        'unmatched_records': unmatched_records
    }
    
    return df_master, reco_summary
