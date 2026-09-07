import re
import pandas as pd
import numpy as np

try:
    import scipy.sparse as sp
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_SPARSE_AVAILABLE = True
except ImportError:
    SKLEARN_SPARSE_AVAILABLE = False

def extract_district_from_ida(ida):
    """
    Extracts a normalized district name from IDA field strings.
    Example: 'JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA)' -> 'JAUNPUR'
             'Khargone (West Nimar)(DISTRICT COLLECTOR...)' -> 'KHARGONE (WEST NIMAR)'
    Fallback: 'UNKNOWN_DISTRICT' when unparseable or null.
    """
    if pd.isna(ida) or not str(ida).strip():
        return 'UNKNOWN_DISTRICT'
    s = str(ida).strip()
    m = re.search(r'^(.*?)(?=\((?:DISTRICT|DEPUTY|COLLECTOR|MAGISTRATE|PLANNING|OFFICER|District|Deputy|Collector|Magistrate)\b)', s, re.I)
    if m:
        dist = m.group(1).strip()
        if dist:
            return dist.upper()
    if '(' in s:
        parts = s.split('(')
        first = parts[0].strip()
        if len(first) > 1 and not re.search(r'\b(DISTRICT|DEPUTY|COLLECTOR|MAGISTRATE|PLANNING|OFFICER)\b', first, re.I):
            return first.upper()
        for p in parts:
            p_clean = p.rstrip(')').strip()
            if p_clean and not re.search(r'\b(DISTRICT|DEPUTY|COLLECTOR|MAGISTRATE|PLANNING|OFFICER)\b', p_clean, re.I):
                return p_clean.upper()
    clean = re.sub(r'[\._\-]+', ' ', s).strip()
    return clean.upper() if clean else 'UNKNOWN_DISTRICT'

def extract_location_tokens(text):
    """Extract location-like tokens (capitalized words, village, GP, Ward, Gram Panchayat, Road names)."""
    if pd.isna(text):
        return set()
    s = str(text).lower()
    stop_words = {'construction', 'of', 'road', 'at', 'in', 'from', 'to', 'work', 'development', 'paver', 'block', 'installation', 'solar', 'light', 'water', 'pipe', 'line', 'hall', 'community', 'school', 'cement', 'concrete', 'cc', 'gram', 'panchayat'}
    tokens = set(re.findall(r'\b[a-z0-9]{3,}\b', s))
    return tokens - stop_words

def generate_candidate_pairs(df_master, df_b=None, chamber_pair="LS-LS", max_pairs_per_group=30, overall_max_pairs=5000):
    """
    Generates candidate pairs of Master Work Entities for double-dipping V2 analysis.
    Supports both intra-dataset (df_master vs df_master, e.g. LS-LS) and
    cross-dataset (df_master vs df_b, e.g. LS-RS) candidate generation.
    
    Returns:
        candidate_pairs: List of dicts containing (entity_a, entity_b, blocking_key)
        blocking_metrics: dict of blocking statistics
    """
    if df_b is None or df_b is df_master:
        return _generate_intra_candidate_pairs(df_master, max_pairs_per_group, overall_max_pairs)
    else:
        return _generate_cross_candidate_pairs(df_master, df_b, chamber_pair, max_pairs_per_group, overall_max_pairs)

def _generate_intra_candidate_pairs(df_master, max_pairs_per_group=30, overall_max_pairs=5000):
    candidate_pairs = []
    seen_pair_keys = set()
    raw_pairs_examined = 0
    pairs_removed_lifecycle = 0
    pairs_removed_duplicate = 0
    
    df = df_master.copy()
    state_col = 'state' if 'state' in df.columns else ('State' if 'State' in df.columns else df.columns[0])
    const_col = 'constituency' if 'constituency' in df.columns else ('Constituency' if 'Constituency' in df.columns else df.columns[0])
    ida_col = 'IDA' if 'IDA' in df.columns else ('ida' if 'ida' in df.columns else None)
    
    if 'district_normalized' not in df.columns:
        if ida_col and ida_col in df.columns:
            df['district_normalized'] = df[ida_col].apply(extract_district_from_ida)
        elif 'district' in df.columns:
            df['district_normalized'] = df['district'].fillna('UNKNOWN_DISTRICT').astype(str).str.strip().str.upper()
        else:
            df['district_normalized'] = 'UNKNOWN_DISTRICT'
            
    df['state_clean'] = df[state_col].fillna('UNKNOWN_STATE').astype(str).str.strip().str.upper()
    df['const_clean'] = df[const_col].fillna('UNKNOWN_CONSTITUENCY').astype(str).str.strip().str.upper()
    
    df['blocking_key'] = np.where(
        df['district_normalized'] != 'UNKNOWN_DISTRICT',
        df['state_clean'] + '|' + df['district_normalized'] + '|' + df['const_clean'],
        df['state_clean'] + '|' + df['const_clean']
    )
    
    groups = df.groupby('blocking_key')
    blocked_groups_count = len(groups)
    
    for block_key, group_df in groups:
        if len(group_df) < 2:
            continue
            
        records = group_df.to_dict('records')
        descriptions = [r.get('description', r.get('work_name', '')) for r in records]
        n = len(records)
        
        sim_matrix = None
        if SKLEARN_SPARSE_AVAILABLE:
            try:
                vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words='english').fit_transform(descriptions)
                sim_matrix = (vec * vec.T).tocsr()
            except Exception:
                sim_matrix = None
            
        group_pairs = []
        
        if sim_matrix is not None and SKLEARN_SPARSE_AVAILABLE:
            coo = sp.triu(sim_matrix, k=1).tocoo()
            for i, j, tfidf_sim in zip(coo.row, coo.col, coo.data):
                raw_pairs_examined += 1
                if tfidf_sim < 0.35:
                    continue
                    
                r_a = records[i]
                r_b = records[j]
                
                mid_a = r_a.get('master_work_id', r_a.get('entity_id', r_a.get('clean_work_id', str(i))))
                mid_b = r_b.get('master_work_id', r_b.get('entity_id', r_b.get('clean_work_id', str(j))))
                
                if mid_a == mid_b:
                    pairs_removed_lifecycle += 1
                    continue
                cid_a = r_a.get('clean_work_id', r_a.get('canonical_work_id'))
                cid_b = r_b.get('clean_work_id', r_b.get('canonical_work_id'))
                if cid_a and cid_b and cid_a == cid_b:
                    pairs_removed_lifecycle += 1
                    continue
                    
                pair_key = tuple(sorted([str(mid_a), str(mid_b)]))
                if pair_key in seen_pair_keys:
                    pairs_removed_duplicate += 1
                    continue
                    
                group_pairs.append((tfidf_sim, r_a, r_b, pair_key, f"BLOCK:{block_key}"))
        else:
            for i in range(min(n, 100)):
                words_i = set(re.findall(r'\b[a-z0-9]{3,}\b', str(descriptions[i]).lower()))
                if not words_i: continue
                for j in range(i+1, min(n, 100)):
                    raw_pairs_examined += 1
                    words_j = set(re.findall(r'\b[a-z0-9]{3,}\b', str(descriptions[j]).lower()))
                    if not words_j: continue
                    overlap = len(words_i.intersection(words_j)) / len(words_i.union(words_j))
                    if overlap < 0.30: continue
                    
                    r_a = records[i]
                    r_b = records[j]
                    mid_a = r_a.get('master_work_id', r_a.get('entity_id', r_a.get('clean_work_id', str(i))))
                    mid_b = r_b.get('master_work_id', r_b.get('entity_id', r_b.get('clean_work_id', str(j))))
                    
                    if mid_a == mid_b:
                        pairs_removed_lifecycle += 1
                        continue
                    cid_a = r_a.get('clean_work_id', r_a.get('canonical_work_id'))
                    cid_b = r_b.get('clean_work_id', r_b.get('canonical_work_id'))
                    if cid_a and cid_b and cid_a == cid_b:
                        pairs_removed_lifecycle += 1
                        continue
                    pair_key = tuple(sorted([str(mid_a), str(mid_b)]))
                    if pair_key in seen_pair_keys:
                        pairs_removed_duplicate += 1
                        continue
                    group_pairs.append((overlap, r_a, r_b, pair_key, f"BLOCK:{block_key}"))
                
        group_pairs.sort(key=lambda x: x[0], reverse=True)
        for _, r_a, r_b, pair_key, block_path in group_pairs[:max_pairs_per_group]:
            seen_pair_keys.add(pair_key)
            candidate_pairs.append({
                'entity_a': r_a,
                'entity_b': r_b,
                'blocking_path': block_path
            })
            if len(candidate_pairs) >= overall_max_pairs:
                break
                
        if len(candidate_pairs) >= overall_max_pairs:
            break

    metrics = {
        'blocked_groups': blocked_groups_count,
        'raw_pairs_examined': raw_pairs_examined,
        'pairs_removed_lifecycle': pairs_removed_lifecycle,
        'lifecycle_reconciled_excluded_pairs': pairs_removed_lifecycle,
        'duplicate_candidate_pairs_removed': pairs_removed_duplicate,
        'retained_candidate_pairs': len(candidate_pairs)
    }
    
    return candidate_pairs, metrics

def _generate_cross_candidate_pairs(df_a, df_b, chamber_pair, max_pairs_per_group=30, overall_max_pairs=5000):
    candidate_pairs = []
    seen_pair_keys = set()
    raw_pairs_examined = 0
    pairs_removed_duplicate = 0
    
    state_col_a = 'state' if 'state' in df_a.columns else df_a.columns[0]
    state_col_b = 'state' if 'state' in df_b.columns else df_b.columns[0]
    
    groups_a = dict(list(df_a.groupby(state_col_a)))
    groups_b = dict(list(df_b.groupby(state_col_b)))
    
    common_states = set(groups_a.keys()).intersection(set(groups_b.keys()))
    if not common_states:
        # Fallback to single group comparison if state columns differ
        common_states = {'ALL'}
        groups_a = {'ALL': df_a}
        groups_b = {'ALL': df_b}
        
    for state in common_states:
        group_a = groups_a[state]
        group_b = groups_b[state]
        
        recs_a = group_a.to_dict('records')
        recs_b = group_b.to_dict('records')
        
        descs_a = [r.get('description', r.get('work_name', '')) for r in recs_a]
        descs_b = [r.get('description', r.get('work_name', '')) for r in recs_b]
        
        sim_matrix = None
        if SKLEARN_SPARSE_AVAILABLE and descs_a and descs_b:
            try:
                vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words='english')
                vec_a = vec.fit_transform(descs_a)
                vec_b = vec.transform(descs_b)
                sim_matrix = (vec_a * vec_b.T).tocsr()
            except Exception:
                sim_matrix = None
                
        group_pairs = []
        if sim_matrix is not None:
            coo = sim_matrix.tocoo()
            for i, j, tfidf_sim in zip(coo.row, coo.col, coo.data):
                raw_pairs_examined += 1
                if tfidf_sim < 0.35:
                    continue
                r_a = recs_a[i]
                r_b = recs_b[j]
                
                mid_a = r_a.get('master_work_id', r_a.get('entity_id', r_a.get('clean_work_id', str(i))))
                mid_b = r_b.get('master_work_id', r_b.get('entity_id', r_b.get('clean_work_id', str(j))))
                
                pair_key = (str(mid_a), str(mid_b))
                reverse_key = (str(mid_b), str(mid_a))
                if pair_key in seen_pair_keys or reverse_key in seen_pair_keys:
                    pairs_removed_duplicate += 1
                    continue
                    
                group_pairs.append((tfidf_sim, r_a, r_b, pair_key, f"CROSS_HOUSE:{chamber_pair}|{state}"))
        else:
            for i, r_a in enumerate(recs_a[:100]):
                words_i = set(re.findall(r'\b[a-z0-9]{3,}\b', str(descs_a[i]).lower()))
                if not words_i: continue
                for j, r_b in enumerate(recs_b[:100]):
                    raw_pairs_examined += 1
                    words_j = set(re.findall(r'\b[a-z0-9]{3,}\b', str(descs_b[j]).lower()))
                    if not words_j: continue
                    overlap = len(words_i.intersection(words_j)) / len(words_i.union(words_j))
                    if overlap < 0.30: continue
                    
                    mid_a = r_a.get('master_work_id', r_a.get('entity_id', r_a.get('clean_work_id', str(i))))
                    mid_b = r_b.get('master_work_id', r_b.get('entity_id', r_b.get('clean_work_id', str(j))))
                    
                    pair_key = (str(mid_a), str(mid_b))
                    reverse_key = (str(mid_b), str(mid_a))
                    if pair_key in seen_pair_keys or reverse_key in seen_pair_keys:
                        pairs_removed_duplicate += 1
                        continue
                    group_pairs.append((overlap, r_a, r_b, pair_key, f"CROSS_HOUSE:{chamber_pair}|{state}"))
                    
        group_pairs.sort(key=lambda x: x[0], reverse=True)
        for _, r_a, r_b, pair_key, block_path in group_pairs[:max_pairs_per_group]:
            seen_pair_keys.add(pair_key)
            candidate_pairs.append({
                'entity_a': r_a,
                'entity_b': r_b,
                'blocking_path': block_path
            })
            if len(candidate_pairs) >= overall_max_pairs:
                break
        if len(candidate_pairs) >= overall_max_pairs:
            break
            
    metrics = {
        'blocked_groups': len(common_states),
        'raw_pairs_examined': raw_pairs_examined,
        'duplicate_candidate_pairs_removed': pairs_removed_duplicate,
        'retained_candidate_pairs': len(candidate_pairs)
    }
    return candidate_pairs, metrics

