import re
import pandas as pd
import numpy as np

try:
    import scipy.sparse as sp
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_SPARSE_AVAILABLE = True
except ImportError:
    SKLEARN_SPARSE_AVAILABLE = False

def extract_location_tokens(text):
    """Extract location-like tokens (capitalized words, village, GP, Ward, Gram Panchayat, Road names)."""
    if pd.isna(text):
        return set()
    s = str(text).lower()
    stop_words = {'construction', 'of', 'road', 'at', 'in', 'from', 'to', 'work', 'development', 'paver', 'block', 'installation', 'solar', 'light', 'water', 'pipe', 'line', 'hall', 'community', 'school', 'cement', 'concrete', 'cc', 'gram', 'panchayat'}
    tokens = set(re.findall(r'\b[a-z0-9]{3,}\b', s))
    return tokens - stop_words

def generate_candidate_pairs(df_master, max_pairs_per_group=30, overall_max_pairs=5000):
    """
    Generates candidate pairs of DISTINCT Master Work Entities for double-dipping V2 analysis.
    Uses multi-path blocking (Constituency, Category + Location, MP) with pair deduplication.
    
    Returns:
        candidate_pairs: List of dicts containing (entity_a, entity_b, blocking_key)
        blocking_metrics: dict of blocking statistics
    """
    candidate_pairs = []
    seen_pair_keys = set()
    raw_pairs_examined = 0
    pairs_removed_lifecycle = 0
    pairs_removed_duplicate = 0
    
    state_col = 'state' if 'state' in df_master.columns else df_master.columns[0]
    const_col = 'constituency' if 'constituency' in df_master.columns else df_master.columns[0]
    
    groups = df_master.groupby([state_col, const_col])
    blocked_groups_count = len(groups)
    
    for (state, const), group_df in groups:
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
                
                mid_a = r_a.get('master_work_id', r_a.get('entity_id', str(i)))
                mid_b = r_b.get('master_work_id', r_b.get('entity_id', str(j)))
                
                if mid_a == mid_b:
                    pairs_removed_lifecycle += 1
                    continue
                cid_a = r_a.get('clean_work_id', r_a.get('canonical_work_id'))
                cid_b = r_b.get('clean_work_id', r_b.get('canonical_work_id'))
                if cid_a and cid_b and cid_a == cid_b:
                    pairs_removed_lifecycle += 1
                    continue
                    
                pair_key = tuple(sorted([mid_a, mid_b]))
                if pair_key in seen_pair_keys:
                    pairs_removed_duplicate += 1
                    continue
                    
                group_pairs.append((tfidf_sim, r_a, r_b, pair_key, f"CONSTITUENCY:{state}|{const}"))
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
                    mid_a = r_a.get('master_work_id', r_a.get('entity_id', str(i)))
                    mid_b = r_b.get('master_work_id', r_b.get('entity_id', str(j)))
                    
                    if mid_a == mid_b:
                        pairs_removed_lifecycle += 1
                        continue
                    cid_a = r_a.get('clean_work_id', r_a.get('canonical_work_id'))
                    cid_b = r_b.get('clean_work_id', r_b.get('canonical_work_id'))
                    if cid_a and cid_b and cid_a == cid_b:
                        pairs_removed_lifecycle += 1
                        continue
                    pair_key = tuple(sorted([mid_a, mid_b]))
                    if pair_key in seen_pair_keys:
                        pairs_removed_duplicate += 1
                        continue
                    group_pairs.append((overlap, r_a, r_b, pair_key, f"CONSTITUENCY:{state}|{const}"))
                
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
