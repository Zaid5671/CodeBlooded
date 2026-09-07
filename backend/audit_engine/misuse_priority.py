import pandas as pd
import numpy as np
from cost_detection.config import (
    AUDIT_COST_HIGH_WEIGHT,
    AUDIT_COST_MEDIUM_WEIGHT,
    AUDIT_DELAY_WEIGHT,
    AUDIT_COMPLIANCE_WEIGHT,
    AUDIT_VENDOR_RISK_WEIGHT,
    DISCLAIMER_TEXT,
)

def run_audit_priority_aggregation(
    df_scored, df_delay, df_compliance, double_dipping_results=None,
    df_vendor_risk=None, df_forecast=None, df_inadmissible=None,
    df_private_beneficiaries=None, df_duplicate_expenditure=None, df_fund_utilization=None
):
    """
    MODEL 5 — Audit Priority / Potential Misuse Aggregator
    Multi-dimensional evidence & risk aggregator combining Models 1-4, Vendor Risk, Forecasting,
    Inadmissible Works, Private Beneficiaries, Duplicate Expenditure, and Idle Fund Utilization.
    
    Score Normalization:
    Calculates weighted raw sum across independent signals and normalizes by max weight sum (2.15)
    to ensure Priority Score is strictly bounded in [0.00, 1.00] (Display Score: 0 to 100).
    """
    df_s = df_scored.copy()
    df_d = df_delay.copy()
    df_c = df_compliance.copy()
    
    for d_item in [df_s, df_d, df_c]:
        if 'clean_work_id' not in d_item.columns:
            if 'canonical_work_id' in d_item.columns:
                d_item['clean_work_id'] = d_item['canonical_work_id']
            elif 'work_id' in d_item.columns:
                d_item['clean_work_id'] = d_item['work_id']
                
    df_s = df_s.drop_duplicates(subset=['clean_work_id'])
    df_d = df_d.drop_duplicates(subset=['clean_work_id'])
    df_c = df_c.drop_duplicates(subset=['clean_work_id'])
    
    d_cols = [c for c in ['clean_work_id', 'signal_delay', 'delay_status', 'evidence', 'duration_for_delay_check', 'upper_fence_days', 'delay_basis'] if c in df_d.columns]
    c_cols = [c for c in ['clean_work_id', 'signal_compliance', 'compliance_severity', 'evidence', 'approval_gap_days'] if c in df_c.columns]

    merged = df_s.merge(df_d[d_cols], on='clean_work_id', how='left', suffixes=('', '_delay'))
    merged = merged.merge(df_c[c_cols], on='clean_work_id', how='left', suffixes=('', '_compliance'))
    
    # Merge new module dataframes if provided
    inadmissible_map = {}
    if df_inadmissible is not None and not df_inadmissible.empty:
        for _, row in df_inadmissible.iterrows():
            cid = row['clean_work_id']
            inadmissible_map[cid] = {
                'signal': bool(row.get('inadmissible_signal', False)),
                'status': row.get('eligibility_status', 'UNKNOWN'),
                'evidence': row.get('eligibility_evidence', '')
            }

    priv_map = {}
    if df_private_beneficiaries is not None and not df_private_beneficiaries.empty:
        for _, row in df_private_beneficiaries.iterrows():
            cid = row['clean_work_id']
            priv_map[cid] = {
                'signal': bool(row.get('private_beneficiary_signal', False)),
                'status': row.get('beneficiary_status', 'UNKNOWN'),
                'evidence': row.get('beneficiary_evidence', '')
            }

    dup_exp_map = {}
    if df_duplicate_expenditure is not None and not df_duplicate_expenditure.empty:
        for _, row in df_duplicate_expenditure.iterrows():
            cid = row['clean_work_id']
            dup_exp_map[cid] = {
                'signal': bool(row.get('duplicate_expenditure_signal', False)),
                'evidence': row.get('duplicate_expenditure_evidence', [])
            }

    idle_util_map = {}
    if df_fund_utilization is not None and not df_fund_utilization.empty:
        for _, row in df_fund_utilization.iterrows():
            cid = row['clean_work_id']
            idle_util_map[cid] = {
                'signal': bool(row.get('idle_utilization_signal', False)),
                'evidence': row.get('combined_evidence', [])
            }

    # Process Model 1 double dipping flags if present
    dd_work_map = {}
    if double_dipping_results is not None:
        pairs = []
        if isinstance(double_dipping_results, dict) and 'top_suspicious_pairs' in double_dipping_results:
            pairs = double_dipping_results['top_suspicious_pairs']
        elif isinstance(double_dipping_results, dict) and 'scored_pairs' in double_dipping_results:
            pairs = double_dipping_results['scored_pairs']
        elif isinstance(double_dipping_results, pd.DataFrame):
            pairs = double_dipping_results.to_dict('records')
            
        for p in pairs:
            tier = p.get('risk_tier', '')
            score = p.get('risk_score', p.get('composite_risk_score', 0))
            if 'HIGH' in str(tier).upper() or score >= 70:
                w1 = p.get('work_a', {}).get('clean_work_id') or p.get('clean_work_id_1') or p.get('work_id_1')
                w2 = p.get('work_b', {}).get('clean_work_id') or p.get('clean_work_id_2') or p.get('work_id_2')
                ev_dd = f"Potential double-dipping candidate pair (Risk Score: {score}/100, Tier: {tier})."
                if w1: dd_work_map[w1] = dd_work_map.get(w1, []) + [ev_dd]
                if w2: dd_work_map[w2] = dd_work_map.get(w2, []) + [ev_dd]

    # Process Vendor Agency Risk Map
    v_risk_map = {}
    if df_vendor_risk is not None and not df_vendor_risk.empty:
        for idx, v_row in df_vendor_risk.iterrows():
            ida_key = str(v_row.get('implementing_agency', '')).strip()
            if ida_key:
                v_risk_map[ida_key] = v_row.to_dict()

    records = []
    for idx, row in merged.iterrows():
        cid = row['clean_work_id']
        ida = str(row.get('IDA', row.get('ida', ''))).strip()
        
        # 1. Cost Risk Signals
        cost_level = str(row.get('risk_level', 'LOW')).upper()
        if cost_level == 'HIGH':
            cost_score = AUDIT_COST_HIGH_WEIGHT
            cost_signal = True
        elif cost_level == 'MEDIUM':
            cost_score = AUDIT_COST_MEDIUM_WEIGHT
            cost_signal = False
        else:
            cost_score = 0.0
            cost_signal = False
            
        # 2. Delay Signals
        sig_delay = bool(row.get('signal_delay', False))
        delay_score = AUDIT_DELAY_WEIGHT if sig_delay else 0.0
        
        # 3. Compliance Signals
        sig_comp = bool(row.get('signal_compliance', False))
        comp_score = AUDIT_COMPLIANCE_WEIGHT if sig_comp else 0.0
        
        # 4. Vendor Network Risk Score Component
        v_info = v_risk_map.get(ida, {})
        v_conc_risk = bool(v_info.get('concentration_risk', False))
        v_frag_risk = bool(v_info.get('payment_structuring_risk', False))
        v_score = AUDIT_VENDOR_RISK_WEIGHT if (v_conc_risk or v_frag_risk) else 0.0
        
        # 5. New Modules Signals
        inad_info = inadmissible_map.get(cid, {})
        inad_signal = inad_info.get('signal', False)
        inad_score = 0.25 if inad_signal else 0.0

        priv_info = priv_map.get(cid, {})
        priv_signal = priv_info.get('signal', False)
        priv_score = 0.25 if priv_signal else 0.0

        dup_exp_info = dup_exp_map.get(cid, {})
        dup_exp_signal = dup_exp_info.get('signal', False)
        dup_exp_score = 0.20 if dup_exp_signal else 0.0

        idle_util_info = idle_util_map.get(cid, {})
        idle_util_signal = idle_util_info.get('signal', False)
        idle_util_score = 0.20 if idle_util_signal else 0.0

        # Priority Score Calculation
        raw_score = cost_score + delay_score + comp_score + v_score + inad_score + priv_score + dup_exp_score + idle_util_score
        misuse_priority_score = min(1.00, round(raw_score, 4))
        display_score = round(misuse_priority_score * 100, 1)
        
        # Core Fired Independent Signal Count (Historical 3-Signal Standard preserved)
        fired_signal_count = int(cost_signal) + int(sig_delay) + int(sig_comp)
        all_signals_count = sum(int(s) for s in [cost_signal, sig_delay, sig_comp, v_conc_risk, inad_signal, priv_signal, dup_exp_signal, idle_util_signal])
        
        if display_score >= 45.0 or all_signals_count >= 2:
            audit_priority = "CRITICAL_AUDIT_PRIORITY"
        elif display_score >= 20.0 or all_signals_count == 1:
            audit_priority = "STANDARD_REVIEW"
        else:
            audit_priority = "LOW_PRIORITY"
            
        # Build Combined Evidence
        combined_evidence = []
        
        if cost_level in ['HIGH', 'MEDIUM']:
            cost_ev_list = row.get('evidence_list', [])
            if isinstance(cost_ev_list, list) and len(cost_ev_list) > 0:
                combined_evidence.extend(cost_ev_list)
            else:
                combined_evidence.append(f"Cost risk level evaluated as {cost_level}.")
                
        if sig_delay:
            delay_ev = str(row.get('evidence', '') or '')
            if delay_ev and "within peer" not in delay_ev.lower():
                combined_evidence.append(f"Delay Signal: {delay_ev}")
                
        if sig_comp:
            comp_ev = str(row.get('evidence_compliance', row.get('evidence', '')) or '')
            if comp_ev and "within the 45-day" not in comp_ev.lower():
                combined_evidence.append(f"Compliance Signal: {comp_ev}")
                
        if cid in dd_work_map:
            combined_evidence.extend(dd_work_map[cid])
            
        if v_info and v_info.get('evidence'):
            for v_ev in v_info['evidence']:
                if "normal distribution" not in v_ev.lower():
                    combined_evidence.append(f"Vendor Network: {v_ev}")
                    
        if inad_signal and inad_info.get('evidence'):
            combined_evidence.append(f"Eligibility Anomaly: {inad_info['evidence']}")
            
        if priv_signal and priv_info.get('evidence'):
            combined_evidence.append(f"Beneficiary Anomaly: {priv_info['evidence']}")

        if dup_exp_signal and dup_exp_info.get('evidence'):
            combined_evidence.extend(dup_exp_info['evidence'])

        if idle_util_signal and idle_util_info.get('evidence'):
            combined_evidence.extend(idle_util_info['evidence'])
            
        if audit_priority != "LOW_PRIORITY" and len(combined_evidence) == 0:
            combined_evidence.append(f"Audit priority flagged based on score {display_score}/100.")
            
        records.append({
            'clean_work_id': cid,
            'state': str(row.get('State', row.get('state', ''))).strip(),
            'constituency': str(row.get('Constituency', row.get('constituency', ''))).strip(),
            'mp': str(row.get("Hon'ble Members of Parliament", row.get('mp', ''))).strip(),
            'ida': ida,
            'work_name': str(row.get('Work', row.get('work_name', ''))).strip(),
            'sanction_amount': float(row.get('sanction_amount', row.get('Sanction Amount ( ₹ )', 0.0)) or 0.0),
            'cost_risk_level': cost_level,
            'delay_status': str(row.get('delay_status', 'UNKNOWN')),
            'compliance_severity': str(row.get('compliance_severity', 'UNKNOWN')),
            'vendor_concentration_risk': v_conc_risk,
            'inadmissible_work_signal': inad_signal,
            'private_beneficiary_signal': priv_signal,
            'duplicate_expenditure_signal': dup_exp_signal,
            'idle_utilization_signal': idle_util_signal,
            'misuse_priority_score': misuse_priority_score,
            'display_score': display_score,
            'audit_priority': audit_priority,
            'fired_signal_count': fired_signal_count,
            'cost_signal': cost_signal,
            'delay_signal': sig_delay,
            'compliance_signal': sig_comp,
            'combined_evidence': combined_evidence,
            'disclaimer': DISCLAIMER_TEXT
        })
        
    df_priority = pd.DataFrame(records)
    
    summary = {
        'total_works_processed': len(df_priority),
        'critical_audit_priority_count': int((df_priority['audit_priority'] == 'CRITICAL_AUDIT_PRIORITY').sum()),
        'standard_review_count': int((df_priority['audit_priority'] == 'STANDARD_REVIEW').sum()),
        'low_priority_count': int((df_priority['audit_priority'] == 'LOW_PRIORITY').sum()),
        'fired_signals_breakdown': {
            'three_plus_signals': int((df_priority['fired_signal_count'] >= 3).sum()),
            'two_signals': int((df_priority['fired_signal_count'] == 2).sum()),
            'one_signal': int((df_priority['fired_signal_count'] == 1).sum()),
            'zero_signals': int((df_priority['fired_signal_count'] == 0).sum())
        },
        'contributing_signals': {
            'cost_high_signals': int(df_priority['cost_signal'].sum()),
            'delay_signals': int(df_priority['delay_signal'].sum()),
            'compliance_signals': int(df_priority['compliance_signal'].sum()),
            'vendor_concentration_signals': int(df_priority['vendor_concentration_risk'].sum()),
            'inadmissible_work_signals': int(df_priority['inadmissible_work_signal'].sum()),
            'private_beneficiary_signals': int(df_priority['private_beneficiary_signal'].sum()),
            'duplicate_expenditure_signals': int(df_priority['duplicate_expenditure_signal'].sum()),
            'idle_utilization_signals': int(df_priority['idle_utilization_signal'].sum())
        },
        'disclaimer': DISCLAIMER_TEXT
    }
    
    return df_priority, summary
