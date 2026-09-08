import os
import re
import pandas as pd
import numpy as np
from feature_engineering.preprocessing import derive_clean_work_id, clean_monetary_field

def _find_corpus_file(data_dir, pattern_key):
    if not os.path.exists(data_dir):
        return ""
    files = os.listdir(data_dir)
    for f in files:
        if f.lower().endswith(".csv") and pattern_key.lower() in f.lower():
            return os.path.join(data_dir, f)
    return ""

def _get_series(df, col_name, fallback_val=""):
    if col_name in df.columns:
        return df[col_name].fillna('').astype(str).str.strip()
    matches = [c for c in df.columns if col_name.lower() in str(c).lower()]
    if matches:
        return df[matches[0]].fillna('').astype(str).str.strip()
    return pd.Series([fallback_val] * len(df))

def _get_amt_series(df, keywords):
    for kw in keywords:
        matches = [c for c in df.columns if kw.lower() in str(c).lower()]
        if matches:
            return df[matches[0]]
    return df.iloc[:, 0] if not df.empty else pd.Series(dtype=float)

def load_and_reconcile_lifecycle_data(data_dir="data/original/LokSabha18"):
    """
    Loads MPLADS datasets across lifecycle stages (Recommended, Sanctioned, Expenditure, Completed)
    and reconciles them into unified MasterWorkEntity records using fast vectorized operations.
    """
    sanctioned_path = _find_corpus_file(data_dir, "Sanctioned")
    expenditure_path = _find_corpus_file(data_dir, "Expenditure")
    recommended_path = _find_corpus_file(data_dir, "Recommended")
    completed_path = _find_corpus_file(data_dir, "Completed")
    
    # Load raw dataframes safely
    df_sanc = pd.read_csv(sanctioned_path, low_memory=False) if (sanctioned_path and os.path.exists(sanctioned_path)) else pd.DataFrame()
    df_exp = pd.read_csv(expenditure_path, low_memory=False) if (expenditure_path and os.path.exists(expenditure_path)) else pd.DataFrame()
    df_reco = pd.read_csv(recommended_path, low_memory=False) if (recommended_path and os.path.exists(recommended_path)) else pd.DataFrame()
    df_comp = pd.read_csv(completed_path, low_memory=False) if (completed_path and os.path.exists(completed_path)) else pd.DataFrame()

    entity_dict = {}
    exact_id_matches = 0
    fallback_matches = 0
    unmatched_records = 0

    # 1. Process Sanctioned Works (Primary backbone)
    sanc_count = len(df_sanc)
    if not df_sanc.empty:
        work_col = 'Work' if 'Work' in df_sanc.columns else ('Work description' if 'Work description' in df_sanc.columns else df_sanc.columns[0])
        desc_col = 'Work description' if 'Work description' in df_sanc.columns else work_col
        
        sanc_amt_raw = _get_amt_series(df_sanc, ['sanction', 'amount'])
        df_sanc['clean_sanc_amt'] = clean_monetary_field(sanc_amt_raw).fillna(0.0)
        cids = [derive_clean_work_id(w) for w in df_sanc[work_col]]
        
        st_series = _get_series(df_sanc, 'state')
        cn_series = _get_series(df_sanc, 'constituency')
        if cn_series.str.len().sum() == 0:
            cn_series = _get_series(df_sanc, 'district')
        mp_series = _get_series(df_sanc, 'member')
        ida_series = _get_series(df_sanc, 'ida')
        cat_series = _get_series(df_sanc, 'category', fallback_val='OTHER')
        desc_series = _get_series(df_sanc, desc_col)
        work_name_series = _get_series(df_sanc, work_col)
        dt_series = _get_series(df_sanc, 'sanction date')
        rec_dt_series = _get_series(df_sanc, 'recommended date')
        status_series = _get_series(df_sanc, 'status', fallback_val='SANCTIONED')

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
                    'work_category': cat_series.iloc[idx],
                    'state': st_series.iloc[idx],
                    'constituency': cn_series.iloc[idx],
                    'mp': mp_series.iloc[idx],
                    'ida': ida_series.iloc[idx],
                    'sanction_amount': sanc_amt,
                    'recommended_amount': sanc_amt,
                    'expenditure_amount': 0.0,
                    'completed_amount': 0.0,
                    'vendors': set(),
                    'payment_status': 'SANCTIONED',
                    'sanction_date': dt_series.iloc[idx],
                    'recommended_date': rec_dt_series.iloc[idx],
                    'completion_date': '',
                    'expenditure_dates': set(),
                    'lifecycle_status': status_series.iloc[idx],
                    'stages_present': {'sanctioned'},
                    'source_datasets': ['Works Sanctioned']
                }
            else:
                entity_dict[key]['stages_present'].add('sanctioned')
                entity_dict[key]['source_datasets'].append('Works Sanctioned')
                if sanc_amt > entity_dict[key]['sanction_amount']:
                    entity_dict[key]['sanction_amount'] = sanc_amt

    # 2. Reconcile Expenditure Works
    exp_count = len(df_exp)
    if not df_exp.empty:
        exp_w_col = 'Work ID' if 'Work ID' in df_exp.columns else ('Work' if 'Work' in df_exp.columns else df_exp.columns[0])
        exp_amt_raw = _get_amt_series(df_exp, ['disbursed', 'expenditure', 'amount'])
        df_exp['clean_exp_amt'] = clean_monetary_field(exp_amt_raw).fillna(0.0)
        cids_exp = [derive_clean_work_id(w) for w in df_exp[exp_w_col]]
        
        st_exp = _get_series(df_exp, 'state')
        cn_exp = _get_series(df_exp, 'constituency')
        if cn_exp.str.len().sum() == 0:
            cn_exp = _get_series(df_exp, 'district')
        mp_exp = _get_series(df_exp, 'member')
        ida_exp = _get_series(df_exp, 'ida')
        desc_exp = _get_series(df_exp, 'work')
        vendor_exp = _get_series(df_exp, 'vendor')
        pay_status_exp = _get_series(df_exp, 'payment status')
        dt_exp = _get_series(df_exp, 'expenditure date')

        desc_prefix_exp = desc_exp.str.lower().str.replace(r'[^a-z0-9]', '', regex=True).str[:40]
        amt_rounded_exp = df_exp['clean_exp_amt'].round(-3).astype(int).astype(str)
        comp_keys_exp = "COMP_" + st_exp.str.upper() + "_" + cn_exp.str.upper() + "_" + desc_prefix_exp + "_" + amt_rounded_exp

        for idx in range(exp_count):
            cid = cids_exp[idx]
            key = cid if cid else comp_keys_exp.iloc[idx]
            exp_amt = float(df_exp['clean_exp_amt'].iloc[idx])
            v_name = vendor_exp.iloc[idx]
            e_date = dt_exp.iloc[idx]
            p_stat = pay_status_exp.iloc[idx]

            if key in entity_dict:
                entity_dict[key]['stages_present'].add('expenditure')
                entity_dict[key]['source_datasets'].append('Expenditure')
                entity_dict[key]['expenditure_amount'] += exp_amt
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
                    'mp': mp_exp.iloc[idx],
                    'ida': ida_exp.iloc[idx],
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
    if not df_comp.empty:
        comp_w_col = [c for c in df_comp.columns if 'work' in c.lower()][0] if any('work' in c.lower() for c in df_comp.columns) else df_comp.columns[0]
        comp_amt_raw = _get_amt_series(df_comp, ['disbursed', 'completed', 'amount'])
        df_comp['clean_comp_amt'] = clean_monetary_field(comp_amt_raw).fillna(0.0)
        cids_comp = [derive_clean_work_id(w) for w in df_comp[comp_w_col]]
        st_comp = _get_series(df_comp, 'state')
        cn_comp = _get_series(df_comp, 'constituency')
        if cn_comp.str.len().sum() == 0:
            cn_comp = _get_series(df_comp, 'district')
        desc_comp = _get_series(df_comp, comp_w_col)
        dt_comp = _get_series(df_comp, 'completion date')

        desc_prefix_comp = desc_comp.str.lower().str.replace(r'[^a-z0-9]', '', regex=True).str[:40]
        amt_rounded_comp = df_comp['clean_comp_amt'].round(-3).astype(int).astype(str)
        comp_keys_comp = "COMP_" + st_comp.str.upper() + "_" + cn_comp.str.upper() + "_" + desc_prefix_comp + "_" + amt_rounded_comp

        for idx in range(comp_count):
            cid = cids_comp[idx]
            key = cid if cid else comp_keys_comp.iloc[idx]
            c_date = dt_comp.iloc[idx]
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
        reco_w_col = [c for c in df_reco.columns if 'work' in c.lower()][0] if any('work' in c.lower() for c in df_reco.columns) else df_reco.columns[0]
        reco_amt_raw = _get_amt_series(df_reco, ['recommended', 'amount'])
        df_reco['clean_reco_amt'] = clean_monetary_field(reco_amt_raw).fillna(0.0)
        cids_reco = [derive_clean_work_id(w) for w in df_reco[reco_w_col]]
        st_reco = _get_series(df_reco, 'state')
        cn_reco = _get_series(df_reco, 'constituency')
        if cn_reco.str.len().sum() == 0:
            cn_reco = _get_series(df_reco, 'district')
        desc_reco = _get_series(df_reco, reco_w_col)

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
            'state': ent['state'],
            'constituency': ent['constituency'],
            'mp': ent['mp'],
            'ida': ent['ida'],
            'sanction_amount': ent['sanction_amount'],
            'recommended_amount': ent['recommended_amount'],
            'expenditure_amount': ent['expenditure_amount'],
            'completed_amount': ent['completed_amount'],
            'vendor_count': len(ent['vendors']),
            'vendors_str': ", ".join(list(ent['vendors'])[:5]),
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
        'lifecycle_reconciled_entities': int((df_master['stage_count'] > 1).sum()) if ('stage_count' in df_master.columns and not df_master.empty) else 0,
        'exact_id_matches': exact_id_matches,
        'fallback_matches': fallback_matches,
        'unmatched_records': unmatched_records
    }
    
    return df_master, reco_summary
