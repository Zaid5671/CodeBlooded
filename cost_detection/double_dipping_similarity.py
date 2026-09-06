import os
import re
import math
import pickle
import numpy as np
import pandas as pd

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

CACHE_DIR = "output/cache"
EMBEDDINGS_CACHE_PATH = os.path.join(CACHE_DIR, "double_dipping_embeddings.pkl")

# Standard generic MPLADS template phrases
GENERIC_PATTERNS = [
    r'^construction of road$',
    r'^construction of c\.c\. road$',
    r'^construction of paver block road$',
    r'^paver block road construction$',
    r'^installation of solar light$',
    r'^installation of solar street light$',
    r'^construction of drain$',
    r'^construction of drainage$',
    r'^installation of tube well$',
    r'^construction of community hall$',
    r'^construction of boundary wall$',
    r'^development work$',
    r'^repair work$'
]

def normalize_text_for_matching(text):
    """Normalize text while retaining numbers, road codes, village and facility identifiers."""
    if pd.isna(text) or not text:
        return ""
    s = str(text).lower().strip()
    s = re.sub(r'[\t\r\n]+', ' ', s)
    s = re.sub(r'[^\w\s\-/]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def normalize_vendor_name(vendor):
    """Normalize vendor corporate names for fuzzy comparison."""
    if pd.isna(vendor) or not vendor:
        return ""
    v = str(vendor).upper().strip()
    v = re.sub(r'\b(PVT|PRIVATE|LTD|LIMITED|INC|CORP|CORPORATION|CONSTRUCTIONS?|ENTERPRISES?|INFRA|INFRATECH|WORKS)\b', '', v)
    v = re.sub(r'[^A-Z0-9]', '', v)
    return v

def is_generic_description(text, shared_location_tokens_count=0):
    """
    Returns True if description is a generic boilerplate phrase without specific location tokens.
    """
    s = normalize_text_for_matching(text)
    if shared_location_tokens_count > 0:
        return False
    for pat in GENERIC_PATTERNS:
        if re.search(pat, s):
            return True
    words = s.split()
    if len(words) <= 4 and not re.search(r'\d', s):
        return True
    return False

def extract_location_entities(text):
    """Extract location-specific keywords (villages, panchayats, wards, road names)."""
    s = normalize_text_for_matching(text)
    stop_words = {
        'construction', 'of', 'road', 'at', 'in', 'from', 'to', 'work', 'development',
        'paver', 'block', 'installation', 'solar', 'light', 'water', 'pipe', 'line',
        'hall', 'community', 'school', 'boundary', 'wall', 'interlocking', 'cement',
        'concrete', 'cc', 'gram', 'panchayat', 'gp', 'ward', 'no', 'near', 'house',
        'side', 'street', 'area', 'dist', 'district', 'village', 'nagar', 'colony',
        'repair', 'drain', 'drainage', 'supply', 'fitting'
    }
    tokens = set(re.findall(r'\b[a-z0-9]{3,}\b', s))
    return tokens - stop_words

def compute_fallback_text_similarity(str1, str2):
    s1, s2 = normalize_text_for_matching(str1), normalize_text_for_matching(str2)
    w1, w2 = set(s1.split()), set(s2.split())
    if not w1 or not w2:
        return 0.0
    intersection = len(w1.intersection(w2))
    union = len(w1.union(w2))
    return float(intersection / union) if union > 0 else 0.0

def get_or_create_embeddings_cache(df_master, cache_dir=CACHE_DIR):
    """
    Computes or retrieves cached text representations for all master descriptions.
    Uses SBERT if sentence-transformers is installed, otherwise falls back to TF-IDF.
    """
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "double_dipping_embeddings.pkl")
    
    data_hash = len(df_master)
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "rb") as f:
                cached_data = pickle.load(f)
                if cached_data.get("data_hash") == data_hash:
                    return cached_data["model"], cached_data["embeddings"], cached_data["backend"], True
        except Exception:
            pass
            
    descriptions = [normalize_text_for_matching(d) for d in df_master['description']]
    
    try:
        from sentence_transformers import SentenceTransformer
        sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = sbert_model.encode(descriptions, show_progress_bar=False)
        backend = "SBERT (all-MiniLM-L6-v2)"
        model_obj = sbert_model
    except Exception:
        if SKLEARN_AVAILABLE:
            tfidf_model = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words='english')
            embeddings = tfidf_model.fit_transform(descriptions)
            backend = "TF-IDF Cosine Vectorizer (Scikit-Learn Fallback)"
            model_obj = tfidf_model
        else:
            backend = "Jaccard Token Vectorizer (Pure Python Fallback)"
            model_obj = "JACCARD_FALLBACK"
            embeddings = np.zeros((len(descriptions), 1))
        
    cache_payload = {
        "data_hash": data_hash,
        "model": model_obj,
        "embeddings": embeddings,
        "backend": backend
    }
    with open(cache_file, "wb") as f:
        pickle.dump(cache_payload, f)
        
    return model_obj, embeddings, backend, False

def compute_pairwise_features(r_a, r_b, tfidf_model=None):
    """
    Computes master 25-dimensional feature vector between two master work entities.
    """
    title_a = normalize_text_for_matching(r_a.get('work_name', r_a.get('description', '')))
    title_b = normalize_text_for_matching(r_b.get('work_name', r_b.get('description', '')))
    desc_a = normalize_text_for_matching(r_a.get('description', ''))
    desc_b = normalize_text_for_matching(r_b.get('description', ''))
    
    # 1. Semantic Similarity
    if tfidf_model is not None and SKLEARN_AVAILABLE:
        try:
            vecs = tfidf_model.transform([desc_a, desc_b])
            semantic_sim = float(cosine_similarity(vecs[0], vecs[1])[0][0])
        except Exception:
            semantic_sim = compute_fallback_text_similarity(desc_a, desc_b)
    elif SKLEARN_AVAILABLE:
        try:
            v = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit_transform([desc_a, desc_b])
            semantic_sim = float(cosine_similarity(v[0], v[1])[0][0])
        except Exception:
            semantic_sim = compute_fallback_text_similarity(desc_a, desc_b)
    else:
        semantic_sim = compute_fallback_text_similarity(desc_a, desc_b)

    semantic_sim = min(1.0, max(0.0, semantic_sim))

    # 2. Title & Description Fuzzy Similarity
    words_t_a, words_t_b = set(title_a.split()), set(title_b.split())
    title_sim = len(words_t_a.intersection(words_t_b)) / len(words_t_a.union(words_t_b)) if words_t_a.union(words_t_b) else 0.0
    
    words_d_a, words_d_b = set(desc_a.split()), set(desc_b.split())
    desc_sim = len(words_d_a.intersection(words_d_b)) / len(words_d_a.union(words_d_b)) if words_d_a.union(words_d_b) else 0.0
    fuzzy_sim = (title_sim * 0.4) + (desc_sim * 0.6)

    # 3. Amount Features
    amt_a = float(r_a.get('sanction_amount', 0.0) or 0.0)
    amt_b = float(r_b.get('sanction_amount', 0.0) or 0.0)
    amt_diff = abs(amt_a - amt_b)
    max_amt = max(amt_a, amt_b)
    amt_ratio = min(amt_a, amt_b) / max_amt if max_amt > 0 else 1.0
    amount_sim = 1.0 - (amt_diff / max_amt) if max_amt > 0 else 1.0

    # 4. Vendor Features
    v_a = normalize_vendor_name(r_a.get('primary_vendor', ''))
    v_b = normalize_vendor_name(r_b.get('primary_vendor', ''))
    vendor_exact = bool(v_a and v_b and v_a == v_b)
    if vendor_exact:
        vendor_sim = 1.0
        vendor_status = 'MATCHING_VENDOR'
    elif v_a and v_b:
        words_v_a, words_v_b = set(v_a.split()), set(v_b.split())
        vendor_sim = len(words_v_a.intersection(words_v_b)) / len(words_v_a.union(words_v_b)) if words_v_a.union(words_v_b) else 0.0
        vendor_status = 'DIFFERENT_VENDORS'
    else:
        vendor_sim = 0.5
        vendor_status = 'NO_VENDOR_DATA'

    vendor_evidence_avail = bool(v_a or v_b)

    # 5. Date Features
    d_a_str = r_a.get('sanction_date', '')
    d_b_str = r_b.get('sanction_date', '')
    d_a = pd.to_datetime(d_a_str, errors='coerce')
    d_b = pd.to_datetime(d_b_str, errors='coerce')
    if pd.notnull(d_a) and pd.notnull(d_b):
        date_diff_days = abs((d_a - d_b).days)
        date_sim = math.exp(-date_diff_days / 90.0)
    else:
        date_diff_days = 999
        date_sim = 0.5

    # 6. Location Features
    loc_a = extract_location_entities(desc_a)
    loc_b = extract_location_entities(desc_b)
    overlap_tokens = loc_a.intersection(loc_b)
    shared_loc_list = sorted(list(overlap_tokens))
    loc_token_overlap = len(overlap_tokens)
    loc_evidence_avail = bool(loc_a or loc_b)
    
    st_match = bool(r_a.get('state') and r_a.get('state') == r_b.get('state'))
    cn_match = bool(r_a.get('constituency') and r_a.get('constituency') == r_b.get('constituency'))
    
    if cn_match and loc_token_overlap >= 2:
        loc_confidence = "HIGH"
        loc_method = "CONSTITUENCY_AND_LOCATION_TOKENS"
        loc_sim = 1.0
    elif cn_match and loc_token_overlap == 1:
        loc_confidence = "MEDIUM"
        loc_method = "CONSTITUENCY_AND_SINGLE_LOCATION_TOKEN"
        loc_sim = 0.8
    elif cn_match:
        loc_confidence = "MEDIUM"
        loc_method = "CONSTITUENCY_MATCH"
        loc_sim = 0.6
    elif st_match:
        loc_confidence = "LOW"
        loc_method = "STATE_MATCH_ONLY"
        loc_sim = 0.3
    else:
        loc_confidence = "LOW"
        loc_method = "DIFFERENT_STATES"
        loc_sim = 0.0

    # 7. Category & Lifecycle Linkage Safeguards
    cat_a = r_a.get('work_category', 'OTHER')
    cat_b = r_b.get('work_category', 'OTHER')
    category_sim = 1.0 if cat_a == cat_b else 0.5

    same_master = bool(r_a.get('master_work_id') and r_a.get('master_work_id') == r_b.get('master_work_id'))
    
    cid_a = r_a.get('clean_work_id', r_a.get('canonical_work_id', ''))
    cid_b = r_b.get('clean_work_id', r_b.get('canonical_work_id', ''))
    same_canonical_id = bool(cid_a and cid_b and cid_a == cid_b)

    is_generic = is_generic_description(desc_a, loc_token_overlap) or is_generic_description(desc_b, loc_token_overlap)

    contextual_anchors = 0
    if cn_match: contextual_anchors += 1
    if loc_token_overlap >= 1: contextual_anchors += 1
    if amount_sim >= 0.9: contextual_anchors += 1
    if vendor_exact or vendor_sim >= 0.7: contextual_anchors += 1
    if date_diff_days <= 30: contextual_anchors += 1
    
    has_anchor = bool(contextual_anchors >= 2)

    convergence_count = 0
    if semantic_sim >= 0.75: convergence_count += 1
    if loc_sim >= 0.6: convergence_count += 1
    if amount_sim >= 0.9: convergence_count += 1
    if vendor_sim >= 0.7: convergence_count += 1
    if date_sim >= 0.7: convergence_count += 1

    return {
        'semantic_similarity': semantic_sim,
        'title_similarity': title_sim,
        'description_similarity': desc_sim,
        'fuzzy_text_similarity': fuzzy_sim,

        'amount_similarity': amount_sim,
        'amount_difference': amt_diff,
        'amount_ratio': amt_ratio,

        'vendor_similarity': vendor_sim,
        'vendor_exact_match': vendor_exact,
        'vendor_status': vendor_status,
        'vendor_evidence_available': vendor_evidence_avail,

        'date_similarity': date_sim,
        'date_difference_days': date_diff_days,

        'category_similarity': category_sim,
        'state_match': st_match,
        'constituency_match': cn_match,
        'location_similarity': loc_sim,
        'location_token_overlap': loc_token_overlap,
        'shared_location_tokens': shared_loc_list,
        'location_evidence_available': loc_evidence_avail,
        'location_confidence': loc_confidence,
        'location_method': loc_method,

        'same_master_work': same_master,
        'same_canonical_work_id': same_canonical_id,

        'is_generic_description': is_generic,
        'generic_description_flag': is_generic,
        'image_similarity_available': False,
        'has_contextual_anchor': has_anchor,
        'convergence_count': convergence_count
    }
