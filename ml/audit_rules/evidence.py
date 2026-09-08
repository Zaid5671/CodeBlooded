import json
import pandas as pd
from ml.config import DISCLAIMER_TEXT, RISK_LEVEL_DATA_QUALITY

def generate_work_evidence(row):
    """Generates a list of human-readable evidence strings for a single work record."""
    evidence = []

    # Data Quality Check
    if row.get('is_below_floor', False):
        amt = row.get('sanction_amount')
        amt_str = f"₹{amt:,.2f}" if pd.notnull(amt) else "N/A"
        evidence.append(
            f"Sanction amount ({amt_str}) is below the configured ₹1,000 minimum analytical floor "
            f"and requires source verification."
        )

    # Work Category Context
    cat = row.get('standardized_category', 'OTHER')
    if cat != 'OTHER':
        evidence.append(f"Work Category Taxonomy: {cat}")

    # SLA Compliance Check
    if row.get('compliance_flag', False):
        status = row.get('compliance_status', '')
        if status == 'SANCTION_SLA_BREACH':
            days = row.get('rec_to_sanc_days', 'N/A')
            evidence.append(f"SLA Compliance Breach: Sanction pending/approved took {days} days from recommendation (exceeded 75-day SLA).")
        elif status == 'REJECTION_NOTIFICATION_SLA_BREACH':
            evidence.append("SLA Compliance Breach: Work rejection notification exceeded applicable 45-day communication/rejection window.")

    # Vendor Fragmentation Check
    if row.get('vendor_fragmentation_flag', False):
        evidence.append("Payment Fragmentation Detector: Multiple payments to the same vendor occurred within a 7-day window and may warrant procurement review.")

    # Duplicate Work Check
    if row.get('potential_duplicate_flag', False):
        evidence.append("Duplicate Work Detector: Potential duplicate work description detected within same constituency — Requires human verification.")

    # Signal 1: Cost Overrun
    if row.get('cost_overrun_flag', False):
        act = row.get('actual_expenditure', 0)
        sanc = row.get('sanction_amount', 1)
        var_pct = row.get('cost_variance_pct', 0)
        evidence.append(
            f"Cost Overrun Detected: Actual expenditure (₹{act:,.2f}) exceeded sanctioned amount "
            f"(₹{sanc:,.2f}) by {var_pct:.1f}% (threshold: 10%)."
        )
    elif pd.isna(row.get('actual_expenditure')):
        evidence.append("MISSING EVIDENCE: No expenditure record found yet for this work.")

    # Signal 2: Peer IQR / MAD
    if row.get('peer_iqr_flag', False):
        sanc = row.get('sanction_amount', 0)
        med = row.get('peer_median', 0)
        ratio = row.get('peer_deviation_ratio', 0) * 100.0 if pd.notnull(row.get('peer_deviation_ratio')) else 0.0
        rob_dev = row.get('robust_deviation', 0)
        plevel = row.get('peer_level', 'STATE_CATEGORY').replace('_', ' ').lower()
        stat_type = "MAD fallback" if row.get('peer_iqr_status') == 'MAD_FALLBACK' else "IQR"
        evidence.append(
            f"Peer Anomaly: Sanction amount (₹{sanc:,.2f}) is {ratio:.1f}% above {plevel} median "
            f"(₹{med:,.2f}) with {stat_type} robust deviation of {rob_dev:.2f} (threshold: 3.0)."
        )

    if row.get('peer_confidence') == 'LOW':
        evidence.append("Peer Statistics Warning: National category fallback used due to small state-category sample size (< 20 works).")

    # Signal 3: Isolation Forest
    if row.get('isolation_forest_flag', False):
        score = row.get('isolation_forest_score', 0)
        evidence.append(
            f"ML Anomaly Detected: Isolation Forest identified anomalous cost/timing pattern "
            f"(anomaly score: {score:.4f})."
        )

    if not evidence and row.get('risk_level') == 'LOW':
        evidence.append("No statistical or financial anomaly signals triggered.")

    return evidence

def build_output_json_structure(row):
    """Constructs the canonical JSON schema representation for a single record."""
    evidence = generate_work_evidence(row)
    
    return {
        "work_id": str(row.get('clean_work_id', row.get('work_id', ''))),
        "clean_work_id": str(row.get('clean_work_id', '')),
        "mp_name": str(row.get("Hon'ble Members of Parliament", '')),
        "state": str(row.get('State', '')),
        "constituency": str(row.get('Constituency', '')),
        "work_description": str(row.get('Work description', row.get('Work', ''))),
        "standardized_category": str(row.get('standardized_category', 'OTHER')),
        "sanctioned_amount": float(row['sanction_amount']) if pd.notnull(row.get('sanction_amount')) else None,
        "actual_expenditure": float(row['actual_expenditure']) if pd.notnull(row.get('actual_expenditure')) else None,
        "expenditure_record_count": int(row['expenditure_record_count']) if pd.notnull(row.get('expenditure_record_count')) else 0,
        "recommendation_to_sanction_days": int(row['rec_to_sanc_days']) if pd.notnull(row.get('rec_to_sanc_days')) else None,
        
        "compliance": {
            "status": str(row.get('compliance_status', 'COMPLIANT')),
            "flag": bool(row.get('compliance_flag', False))
        },
        
        "peer_statistics": {
            "peer_level": str(row.get('peer_level', 'NATIONAL_CATEGORY')),
            "peer_size": int(row['peer_size']) if pd.notnull(row.get('peer_size')) else 0,
            "median": float(row['peer_median']) if pd.notnull(row.get('peer_median')) else None,
            "q1": float(row['peer_q1']) if pd.notnull(row.get('peer_q1')) else None,
            "q3": float(row['peer_q3']) if pd.notnull(row.get('peer_q3')) else None,
            "iqr": float(row['peer_iqr']) if pd.notnull(row.get('peer_iqr')) else None,
            "mad": float(row['peer_mad']) if pd.notnull(row.get('peer_mad')) else None,
            "confidence": str(row.get('peer_confidence', 'NORMAL'))
        },
        
        "signals": {
            "cost_overrun": {
                "flag": bool(row.get('cost_overrun_flag', False)),
                "variance_pct": float(row['cost_variance_pct']) if pd.notnull(row.get('cost_variance_pct')) else None,
                "status": str(row.get('cost_variance_status', 'NO_EXPENDITURE_RECORD_YET'))
            },
            "peer_iqr": {
                "flag": bool(row.get('peer_iqr_flag', False)),
                "robust_deviation": float(row['robust_deviation']) if pd.notnull(row.get('robust_deviation')) else None,
                "status": str(row.get('peer_iqr_status', 'NORMAL'))
            },
            "isolation_forest": {
                "flag": bool(row.get('isolation_forest_flag', False)),
                "anomaly_score": float(row['isolation_forest_score']) if pd.notnull(row.get('isolation_forest_score')) else None
            }
        },
        
        "consensus": {
            "positive_signal_count": int(row.get('positive_signal_count', 0)),
            "risk_level": str(row.get('risk_level', 'LOW'))
        },
        
        "evidence": evidence,
        "disclaimer": DISCLAIMER_TEXT
    }

def apply_evidence_generation(df):
    """Applies evidence generation across the dataframe."""
    df_out = df.copy()
    df_out['evidence_list'] = df_out.apply(generate_work_evidence, axis=1)
    df_out['evidence_text'] = df_out['evidence_list'].apply(lambda x: " | ".join(x))
    return df_out
