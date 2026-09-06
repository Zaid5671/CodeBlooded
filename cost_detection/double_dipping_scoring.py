from .config import DOUBLE_DIPPING_V2_CONFIG

def compute_double_dipping_risk(r_a, r_b, features, config=DOUBLE_DIPPING_V2_CONFIG):
    """
    Computes explainable weighted V2 risk score and structured evidence for potential double-dipping.
    
    Returns:
        result_dict: Structured dictionary with score, tier, triggered evidence, and missing evidence.
    """
    weights = {
        'semantic_similarity': config.get('semantic_weight', 0.35),
        'amount_similarity': config.get('amount_weight', 0.20),
        'location_similarity': config.get('location_weight', 0.20),
        'vendor_similarity': config.get('vendor_weight', 0.15),
        'date_similarity': config.get('date_weight', 0.10)
    }
    
    # Missing vendor data handling (re-weight remaining available features)
    if not features.get('vendor_evidence_available', False):
        weights['vendor_similarity'] = 0.0
        
    total_weight = sum(weights.values())
    if total_weight <= 0:
        total_weight = 1.0
        
    weighted_sum = (
        features['semantic_similarity'] * weights['semantic_similarity'] +
        features['amount_similarity'] * weights['amount_similarity'] +
        features['location_similarity'] * weights['location_similarity'] +
        features['vendor_similarity'] * weights['vendor_similarity'] +
        features['date_similarity'] * weights['date_similarity']
    )
    
    raw_score = (weighted_sum / total_weight) * 100.0
    
    # 2. Convergence Bonus calculation (reward multi-evidence convergence)
    min_sem = config.get('minimum_semantic_for_high', 0.75)
    convergence_anchors = []
    
    if features['semantic_similarity'] >= min_sem:
        convergence_anchors.append("High Semantic Text Match")
    if features['location_similarity'] >= 0.3 or features.get('location_token_overlap', 0) >= 1:
        convergence_anchors.append("Specific Location Token Match")
    if features.get('vendor_exact_match', False) or features['vendor_similarity'] == 1.0:
        convergence_anchors.append("Matching Contractor/Vendor")
    if features['amount_similarity'] >= 0.98 and r_a.get('sanction_amount', 0) > 0:
        convergence_anchors.append("Identical Sanction Amount")
    if features['date_similarity'] >= 0.85:
        convergence_anchors.append("Close Temporal Execution Window")
        
    convergence_count = len(convergence_anchors)
    
    final_score = raw_score
    dampeners = []
    
    # Multi-signal convergence bonus if >= 3 independent anchors
    if convergence_count >= 3:
        bonus_mult = config.get('convergence_bonus_multiplier', 1.10)
        final_score *= bonus_mult
    
    # Generic description dampening
    if features.get('is_generic_description', False) and features.get('location_similarity', 0.0) <= 0.6:
        damp_factor = config.get('generic_description_dampening', 0.6)
        final_score *= damp_factor
        dampeners.append("Generic description penalty applied (no unique location tokens)")
        
    final_score = min(100.0, max(0.0, final_score))
    int_score = int(round(final_score))
    
    # Contextual Proof Requirement for HIGH RISK (Requires min 2 independent anchors + min semantic)
    min_anchors = config.get('min_contextual_anchors_for_high', 2)
    has_contextual_proof = (convergence_count >= min_anchors) and (features['semantic_similarity'] >= min_sem)
    
    high_thresh = config.get('high_risk_threshold', 85)
    med_thresh = config.get('medium_risk_threshold', 70)
    
    if int_score >= high_thresh and has_contextual_proof:
        risk_tier = "HIGH RISK — REQUIRES AUDIT REVIEW"
    elif int_score >= med_thresh:
        risk_tier = "MEDIUM RISK"
    else:
        risk_tier = "LOW RISK"
        
    # Triggered & Missing Evidence
    triggered_evidence = []
    missing_evidence = []
    
    # Semantic text evidence
    sem_pct = features['semantic_similarity'] * 100.0
    if sem_pct >= (min_sem * 100.0):
        triggered_evidence.append(f"High semantic text similarity ({sem_pct:.1f}%)")
    elif sem_pct < 40.0:
        missing_evidence.append(f"Low semantic description overlap ({sem_pct:.1f}%)")
        
    # Location evidence
    if features.get('shared_location_tokens'):
        loc_str = ", ".join([f"'{t}'" for t in features['shared_location_tokens'][:3]])
        triggered_evidence.append(f"Matching location tokens found ({loc_str})")
    elif features.get('location_evidence_available', False):
        missing_evidence.append("Different location tokens found in descriptions")
    else:
        missing_evidence.append("No specific shared location/village tokens found")
        
    # Amount evidence
    amt_a = float(r_a.get('sanction_amount', 0.0))
    amt_b = float(r_b.get('sanction_amount', 0.0))
    if features['amount_similarity'] >= 0.98 and amt_a > 0:
        triggered_evidence.append(f"Identical or near-identical sanction amount (₹{amt_a:,.2f} vs ₹{amt_b:,.2f})")
    elif features['amount_similarity'] < 0.60:
        missing_evidence.append(f"Substantially different sanction amounts (₹{amt_a:,.2f} vs ₹{amt_b:,.2f})")
        
    # Vendor evidence
    if features['vendor_status'] == 'MATCHING_VENDOR':
        vendors_str = ", ".join(r_a.get('all_vendors', r_a.get('vendors', [])))
        triggered_evidence.append(f"Identical vendor involved ('{vendors_str}')")
    elif features['vendor_status'] == 'DIFFERENT_VENDORS':
        missing_evidence.append("Different vendors recorded across works")
    else:
        missing_evidence.append("Expenditure vendor records missing or partial")
        
    # Constituency evidence
    if features['constituency_match'] == 1.0:
        triggered_evidence.append(f"Sanctioned within same constituency ('{r_a.get('constituency')}')")
    else:
        missing_evidence.append("Sanctioned across different constituencies")
        
    # Image evidence
    if not features.get('image_similarity_available', False):
        missing_evidence.append("No image comparison available (Image field contains placeholder strings)")

    features['has_contextual_anchor'] = has_contextual_proof
    features['convergence_count'] = convergence_count

    return {
        'risk_score': int_score,
        'risk_score_display': f"{int_score}/100",
        'risk_tier': risk_tier,
        'has_contextual_anchor': has_contextual_proof,
        'convergence_count': convergence_count,
        'convergence_anchors': convergence_anchors,
        'dampeners_applied': dampeners,
        'triggered_evidence': triggered_evidence,
        'missing_evidence': missing_evidence,
        'features': features
    }
