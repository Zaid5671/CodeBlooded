import os
import json
import time
import pandas as pd
import numpy as np

from .config import OUTPUT_DIR, DOUBLE_DIPPING_V2_CONFIG
from .double_dipping_reconciliation import load_and_reconcile_lifecycle_data
from .double_dipping_candidates import generate_candidate_pairs
from .double_dipping_similarity import get_or_create_embeddings_cache, compute_pairwise_features
from .double_dipping_scoring import compute_double_dipping_risk

def calculate_score_distribution_diagnostics(risk_scores):
    """Computes statistical summary diagnostics for risk score distribution."""
    if not risk_scores:
        return {}
    scores_arr = np.array(risk_scores)
    n = len(scores_arr)
    return {
        "count": n,
        "min": float(np.min(scores_arr)),
        "p25": float(np.percentile(scores_arr, 25)),
        "median": float(np.median(scores_arr)),
        "p75": float(np.percentile(scores_arr, 75)),
        "mean": round(float(np.mean(scores_arr)), 2),
        "p90": float(np.percentile(scores_arr, 90)),
        "p95": float(np.percentile(scores_arr, 95)),
        "p99": float(np.percentile(scores_arr, 99)),
        "max": float(np.max(scores_arr)),
        "pct_gte_85": round(float(np.sum(scores_arr >= 85) / n * 100.0), 2),
        "pct_gte_90": round(float(np.sum(scores_arr >= 90) / n * 100.0), 2),
        "pct_gte_95": round(float(np.sum(scores_arr >= 95) / n * 100.0), 2),
        "pct_eq_100": round(float(np.sum(scores_arr == 100) / n * 100.0), 2)
    }

def compare_works(df_a, df_b=None, chamber_pair="LS-LS", max_candidates=5000, tfidf_model=None):
    """
    Generalized chamber-agnostic duplicate detection interface.
    
    Arguments:
        df_a: DataFrame or list of dicts for primary works (e.g. Lok Sabha master works)
        df_b: DataFrame or list of dicts for secondary works (e.g. Rajya Sabha works).
              If None, performs intra-dataset matching within df_a.
        chamber_pair: String denoting chamber comparison ("LS-LS" or "LS-RS")
        max_candidates: Int max candidate pairs to examine
        tfidf_model: Pre-fitted TFIDF model or None
        
    Returns:
        analyzed_pairs: List of dicts representing analyzed candidate pairs with full risk & evidence metrics
        blocking_metrics: dict of blocking statistics
    """
    if isinstance(df_a, list):
        df_a = pd.DataFrame(df_a)
    if df_b is not None and isinstance(df_b, list):
        df_b = pd.DataFrame(df_b)
        
    candidate_pairs, blocking_metrics = generate_candidate_pairs(
        df_a, df_b=df_b, chamber_pair=chamber_pair, max_pairs_per_group=30, overall_max_pairs=max_candidates
    )
    
    ch_parts = chamber_pair.split('-') if '-' in chamber_pair else [chamber_pair, chamber_pair]
    ch_a_default, ch_b_default = ch_parts[0], ch_parts[1]
    
    analyzed_pairs = []
    
    for idx, c in enumerate(candidate_pairs, start=1):
        r_a = c['entity_a']
        r_b = c['entity_b']
        
        feats = compute_pairwise_features(r_a, r_b, tfidf_model=tfidf_model)
        risk_res = compute_double_dipping_risk(r_a, r_b, feats)
        
        score_val = risk_res['risk_score']
        evidence_list = list(risk_res['triggered_evidence'])
        risk_tier_val = risk_res['risk_tier']
        if chamber_pair == "LS-RS" and "HIGH" in risk_tier_val:
            evidence_list.insert(0, "POTENTIAL CROSS-HOUSE DUPLICATE")
            
        pair_record = {
            'pair_id': f"PAIR_{idx:05d}",
            'chamber_a': r_a.get('chamber', ch_a_default),
            'chamber_b': r_b.get('chamber', ch_b_default),
            'chamber_pair': chamber_pair,
            'source_work_id': str(r_a.get('clean_work_id', r_a.get('work_id', r_a.get('entity_id', '')))),
            'matched_work_id': str(r_b.get('clean_work_id', r_b.get('work_id', r_b.get('entity_id', '')))),
            'work_a': {
                'entity_id': r_a.get('master_work_id', r_a.get('entity_id', '')),
                'work_id': r_a.get('clean_work_id', r_a.get('work_id', '')),
                'state': r_a.get('state', ''),
                'constituency': r_a.get('constituency', ''),
                'mp': r_a.get('mp', ''),
                'category': r_a.get('category', ''),
                'description': r_a.get('description', r_a.get('work_name', '')),
                'sanction_amount': r_a.get('sanction_amount', 0.0),
                'expenditure_amount': r_a.get('expenditure_amount', 0.0),
                'vendors': r_a.get('all_vendors', r_a.get('vendors', [])),
                'sanction_date': r_a.get('sanction_date', ''),
                'status': r_a.get('work_status', '')
            },
            'work_b': {
                'entity_id': r_b.get('master_work_id', r_b.get('entity_id', '')),
                'work_id': r_b.get('clean_work_id', r_b.get('work_id', '')),
                'state': r_b.get('state', ''),
                'constituency': r_b.get('constituency', ''),
                'mp': r_b.get('mp', ''),
                'category': r_b.get('category', ''),
                'description': r_b.get('description', r_b.get('work_name', '')),
                'sanction_amount': r_b.get('sanction_amount', 0.0),
                'expenditure_amount': r_b.get('expenditure_amount', 0.0),
                'vendors': r_b.get('all_vendors', r_b.get('vendors', [])),
                'sanction_date': r_b.get('sanction_date', ''),
                'status': r_b.get('work_status', '')
            },
            'risk_score': score_val,
            'risk_score_display': risk_res['risk_score_display'],
            'risk_tier': risk_tier_val,
            'similarity_score': score_val,
            'amount_similarity': round(feats['amount_similarity'] * 100, 1),
            'location_similarity': round(feats['location_similarity'] * 100, 1),
            'date_similarity': round(feats.get('date_similarity', 0.0) * 100, 1),
            'vendor_similarity': round(feats['vendor_similarity'] * 100, 1),
            'has_contextual_anchor': risk_res['has_contextual_anchor'],
            'convergence_count': risk_res['convergence_count'],
            'similarity_breakdown': {
                'semantic_similarity_pct': round(feats['semantic_similarity'] * 100, 1),
                'amount_similarity_pct': round(feats['amount_similarity'] * 100, 1),
                'location_similarity_pct': round(feats['location_similarity'] * 100, 1),
                'vendor_similarity_pct': round(feats['vendor_similarity'] * 100, 1)
            },
            'features': feats,
            'triggered_evidence': evidence_list,
            'evidence': evidence_list,
            'missing_evidence': risk_res['missing_evidence'],
            'dampeners_applied': risk_res['dampeners_applied'],
            'review_status': 'UNREVIEWED'
        }
        analyzed_pairs.append(pair_record)
        
    analyzed_pairs.sort(key=lambda x: (x['risk_score'], x['has_contextual_anchor'], x['similarity_breakdown']['semantic_similarity_pct']), reverse=True)
    return analyzed_pairs, blocking_metrics

def run_double_dipping_detection(data_dir="data/original/LokSabha18", output_dir=OUTPUT_DIR, max_candidates=None):
    """
    Main orchestrator for the Double-Dipping / Potential Duplicate Work Detection Engine V2.
    
    Returns:
        results_summary: dict with analytics summary and top suspicious candidate pairs
    """
    t0 = time.time()
    os.makedirs(output_dir, exist_ok=True)
    
    if max_candidates is None:
        max_candidates = DOUBLE_DIPPING_V2_CONFIG.get("max_candidates", 5000)
    
    # 1. Ingestion & Reconciliation Phase
    t_ingest_start = time.time()
    df_master, reco_summary = load_and_reconcile_lifecycle_data(data_dir)
    t_ingest = time.time() - t_ingest_start
    
    # 2. Embedding Generation & Cache Phase
    t_emb_start = time.time()
    model_obj, embeddings, backend_name, is_cached = get_or_create_embeddings_cache(df_master)
    t_emb = time.time() - t_emb_start
    
    # 3. LS-LS Candidate Blocking & Scoring Phase via generalized compare_works interface
    t_score_start = time.time()
    tfidf_model = model_obj if "TF-IDF" in backend_name else None
    
    analyzed_pairs, blocking_metrics = compare_works(
        df_master, df_b=None, chamber_pair="LS-LS", max_candidates=max_candidates, tfidf_model=tfidf_model
    )
    
    risk_scores = [p['risk_score'] for p in analyzed_pairs]
    tier_counts = {
        "HIGH RISK — REQUIRES AUDIT REVIEW": sum(1 for p in analyzed_pairs if p['risk_tier'] == "HIGH RISK — REQUIRES AUDIT REVIEW"),
        "MEDIUM RISK": sum(1 for p in analyzed_pairs if p['risk_tier'] == "MEDIUM RISK"),
        "LOW RISK": sum(1 for p in analyzed_pairs if p['risk_tier'] == "LOW RISK")
    }
    
    # 4. Check for Rajya Sabha Data Availability (LS-RS Cross-House Matching)
    rs_data_dir = os.path.join(os.path.dirname(data_dir), "RajyaSabha")
    cross_house_pairs = []
    if os.path.exists(rs_data_dir) and any(f.endswith('.csv') for f in os.listdir(rs_data_dir)):
        df_rs, _ = load_and_reconcile_lifecycle_data(rs_data_dir)
        cross_house_pairs, _ = compare_works(
            df_master, df_b=df_rs, chamber_pair="LS-RS", max_candidates=max_candidates, tfidf_model=tfidf_model
        )
        cross_house_status = "READY"
        cross_house_enabled = True
    else:
        cross_house_status = "PENDING_RAJYA_SABHA_DATA"
        cross_house_enabled = False
        
    cross_house_high_risk_count = sum(1 for p in cross_house_pairs if "HIGH" in p['risk_tier'])
    
    t_score = time.time() - t_score_start
    t_total = time.time() - t0
    
    score_dist = calculate_score_distribution_diagnostics(risk_scores)
    
    # 5. Export JSON & CSV Outputs
    json_export = {
        'module_name': 'Double-Dipping / Potential Duplicate Work Detection Engine V2',
        'model_version': 'double_dipping_v2',
        'embedding_backend': backend_name,
        'embedding_cached': is_cached,
        'image_similarity_available': False,
        'cross_house_enabled': cross_house_enabled,
        'cross_house_status': cross_house_status,
        'cross_house_candidate_count': len(cross_house_pairs),
        'cross_house_high_risk_count': cross_house_high_risk_count,
        'cross_house_display_message': "Cross-House LS↔RS Detection: Ready — Rajya Sabha data not currently available" if not cross_house_enabled else f"Cross-House LS↔RS Executed: {len(cross_house_pairs):,} pairs analyzed.",
        'reconciliation_summary': reco_summary,
        'blocking_metrics': blocking_metrics,
        'candidates_generated': len(analyzed_pairs),
        'risk_tier_counts': tier_counts,
        'score_distribution': score_dist,
        'weights_configuration': DOUBLE_DIPPING_V2_CONFIG,
        'performance_metrics_seconds': {
            'ingestion_reconciliation': round(t_ingest, 3),
            'embedding_generation': round(t_emb, 3),
            'candidate_blocking_scoring': round(t_score, 3),
            'total_runtime': round(t_total, 3)
        },
        'top_suspicious_pairs': analyzed_pairs,
        'cross_house_pairs': cross_house_pairs
    }
    
    json_path = os.path.join(output_dir, "double_dipping_results.json")
    with open(json_path, "w") as f:
        json.dump(json_export, f, indent=2)
        
    csv_rows = []
    for p in analyzed_pairs + cross_house_pairs:
        csv_rows.append({
            'pair_id': p['pair_id'],
            'chamber_pair': p.get('chamber_pair', 'LS-LS'),
            'risk_score': p['risk_score'],
            'risk_tier': p['risk_tier'],
            'review_status': p['review_status'],
            'work_a_id': p['work_a']['work_id'],
            'work_a_desc': p['work_a']['description'],
            'work_a_amt': p['work_a']['sanction_amount'],
            'work_b_id': p['work_b']['work_id'],
            'work_b_desc': p['work_b']['description'],
            'work_b_amt': p['work_b']['sanction_amount'],
            'constituency': p['work_a']['constituency'],
            'semantic_sim_pct': p['similarity_breakdown']['semantic_similarity_pct'],
            'amount_sim_pct': p['similarity_breakdown']['amount_similarity_pct'],
            'triggered_evidence_count': len(p['triggered_evidence']),
            'triggered_evidence_summary': " | ".join(p['triggered_evidence'])
        })
    df_csv = pd.DataFrame(csv_rows)
    csv_path = os.path.join(output_dir, "double_dipping_pairs.csv")
    df_csv.to_csv(csv_path, index=False)
    
    print(f"[Double-Dipping V2 Pipeline] Processed {len(df_master):,} master entities into {len(analyzed_pairs):,} candidate pairs in {t_total:.2f}s.")
    print(f"  • Model Version: double_dipping_v2 | Embedding Backend: {backend_name} (Cached: {is_cached})")
    print(f"  • Score Distribution: Min={score_dist.get('min')}, P25={score_dist.get('p25')}, Median={score_dist.get('median')}, P75={score_dist.get('p75')}, Max={score_dist.get('max')}")
    print(f"  • Score Saturation: % >= 85: {score_dist.get('pct_gte_85')}%, % == 100: {score_dist.get('pct_eq_100')}%")
    print(f"  • HIGH RISK Pairs:   {tier_counts['HIGH RISK — REQUIRES AUDIT REVIEW']:,}")
    print(f"  • MEDIUM RISK Pairs: {tier_counts['MEDIUM RISK']:,}")
    print(f"  • LOW RISK Pairs:    {tier_counts['LOW RISK']:,}")
    print(f"  • Cross-House Status: {cross_house_status} (Pairs: {len(cross_house_pairs)})")
    print(f"Results exported to {json_path} and {csv_path}")
    
    return json_export

