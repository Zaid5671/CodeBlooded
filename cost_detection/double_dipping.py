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
    
    # 3. Candidate Blocking Phase
    t_block_start = time.time()
    candidate_pairs, blocking_metrics = generate_candidate_pairs(df_master, max_pairs_per_group=30, overall_max_pairs=max_candidates)
    t_block = time.time() - t_block_start
    
    # 4. Pairwise Scoring & Evidence Generation Phase
    t_score_start = time.time()
    tfidf_model = model_obj if "TF-IDF" in backend_name else None
    
    analyzed_pairs = []
    risk_scores = []
    
    tier_counts = {
        "HIGH RISK — REQUIRES AUDIT REVIEW": 0,
        "MEDIUM RISK": 0,
        "LOW RISK": 0
    }
    
    for idx, c in enumerate(candidate_pairs, start=1):
        r_a = c['entity_a']
        r_b = c['entity_b']
        
        feats = compute_pairwise_features(r_a, r_b, tfidf_model=tfidf_model)
        risk_res = compute_double_dipping_risk(r_a, r_b, feats)
        
        score_val = risk_res['risk_score']
        risk_scores.append(score_val)
        
        tier = risk_res['risk_tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        pair_record = {
            'pair_id': f"PAIR_{idx:05d}",
            'work_a': {
                'entity_id': r_a.get('master_work_id', r_a['entity_id']),
                'work_id': r_a['clean_work_id'],
                'state': r_a['state'],
                'constituency': r_a['constituency'],
                'mp': r_a['mp'],
                'category': r_a['category'],
                'description': r_a['description'],
                'sanction_amount': r_a['sanction_amount'],
                'expenditure_amount': r_a['expenditure_amount'],
                'vendors': r_a.get('all_vendors', r_a.get('vendors', [])),
                'sanction_date': r_a['sanction_date'],
                'status': r_a['work_status']
            },
            'work_b': {
                'entity_id': r_b.get('master_work_id', r_b['entity_id']),
                'work_id': r_b['clean_work_id'],
                'state': r_b['state'],
                'constituency': r_b['constituency'],
                'mp': r_b['mp'],
                'category': r_b['category'],
                'description': r_b['description'],
                'sanction_amount': r_b['sanction_amount'],
                'expenditure_amount': r_b['expenditure_amount'],
                'vendors': r_b.get('all_vendors', r_b.get('vendors', [])),
                'sanction_date': r_b['sanction_date'],
                'status': r_b['work_status']
            },
            'risk_score': score_val,
            'risk_score_display': risk_res['risk_score_display'],
            'risk_tier': risk_res['risk_tier'],
            'has_contextual_anchor': risk_res['has_contextual_anchor'],
            'convergence_count': risk_res['convergence_count'],
            'similarity_breakdown': {
                'semantic_similarity_pct': round(feats['semantic_similarity'] * 100, 1),
                'amount_similarity_pct': round(feats['amount_similarity'] * 100, 1),
                'location_similarity_pct': round(feats['location_similarity'] * 100, 1),
                'vendor_similarity_pct': round(feats['vendor_similarity'] * 100, 1)
            },
            'features': feats,
            'triggered_evidence': risk_res['triggered_evidence'],
            'missing_evidence': risk_res['missing_evidence'],
            'dampeners_applied': risk_res['dampeners_applied'],
            'review_status': 'UNREVIEWED'
        }
        analyzed_pairs.append(pair_record)
        
    analyzed_pairs.sort(key=lambda x: (x['risk_score'], x['has_contextual_anchor'], x['similarity_breakdown']['semantic_similarity_pct']), reverse=True)
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
        'reconciliation_summary': reco_summary,
        'blocking_metrics': blocking_metrics,
        'candidates_generated': len(candidate_pairs),
        'risk_tier_counts': tier_counts,
        'score_distribution': score_dist,
        'weights_configuration': DOUBLE_DIPPING_V2_CONFIG,
        'performance_metrics_seconds': {
            'ingestion_reconciliation': round(t_ingest, 3),
            'embedding_generation': round(t_emb, 3),
            'candidate_blocking': round(t_block, 3),
            'scoring_evidence': round(t_score, 3),
            'total_runtime': round(t_total, 3)
        },
        'top_suspicious_pairs': analyzed_pairs
    }
    
    json_path = os.path.join(output_dir, "double_dipping_results.json")
    with open(json_path, "w") as f:
        json.dump(json_export, f, indent=2)
        
    csv_rows = []
    for p in analyzed_pairs:
        csv_rows.append({
            'pair_id': p['pair_id'],
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
    
    print(f"[Double-Dipping V2 Pipeline] Processed {len(df_master):,} master entities into {len(candidate_pairs):,} candidate pairs in {t_total:.2f}s.")
    print(f"  • Model Version: double_dipping_v2 | Embedding Backend: {backend_name} (Cached: {is_cached})")
    print(f"  • Score Distribution: Min={score_dist.get('min')}, P25={score_dist.get('p25')}, Median={score_dist.get('median')}, P75={score_dist.get('p75')}, Max={score_dist.get('max')}")
    print(f"  • Score Saturation: % >= 85: {score_dist.get('pct_gte_85')}%, % == 100: {score_dist.get('pct_eq_100')}%")
    print(f"  • HIGH RISK Pairs:   {tier_counts['HIGH RISK — REQUIRES AUDIT REVIEW']:,}")
    print(f"  • MEDIUM RISK Pairs: {tier_counts['MEDIUM RISK']:,}")
    print(f"  • LOW RISK Pairs:    {tier_counts['LOW RISK']:,}")
    print(f"Results exported to {json_path} and {csv_path}")
    
    return json_export
