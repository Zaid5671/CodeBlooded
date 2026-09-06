import pandas as pd
import numpy as np

def evaluate_compliance_rules(df):
    """
    Phase 1 & 8: SLA / Compliance Engine.
    Enforces strict status-branching rules:
    - Rule 1: PENDING / UNDER PROCESS & recommendation_date exists & current_date - recommendation_date > 75 days -> SANCTION_SLA_BREACH
    - Rule 2: REJECTED & recommendation_date exists & rejection_date - recommendation_date > 45 days -> REJECTION_NOTIFICATION_SLA_BREACH
    - Rule 3: SANCTIONED / COMPLETED (including execution stages) -> COMPLIANT
    - Rule 4: Required dates missing or invalid -> DATA_QUALITY_REVIEW
    """
    df_out = df.copy()

    df_out['sla_sanction_breach'] = False
    df_out['sla_rejection_breach'] = False
    df_out['compliance_status'] = 'COMPLIANT'
    df_out['compliance_flag'] = False
    df_out['mp_allocation_status'] = 'WITHIN_ALLOCATION'

    rec_dt = df_out['rec_dt'] if 'rec_dt' in df_out.columns else pd.to_datetime(df_out.get('Recommended date'), errors='coerce')
    sanc_dt = df_out['sanc_dt'] if 'sanc_dt' in df_out.columns else pd.to_datetime(df_out.get('Sanction Date'), errors='coerce')

    status_col = None
    for candidate in ['Work Status', 'Status', 'Sanction Status', 'Recommendation Status']:
        if candidate in df_out.columns:
            status_col = candidate
            break

    max_ref_date = sanc_dt.max() if sanc_dt.notnull().any() else pd.to_datetime('today')

    for idx, row in df_out.iterrows():
        r_dt = rec_dt.iloc[idx]
        status_str = str(row[status_col]).upper() if status_col and pd.notnull(row[status_col]) else ''

        if pd.isna(r_dt):
            df_out.at[idx, 'compliance_status'] = 'DATA_QUALITY_REVIEW'
            continue

        # Check explicit status branches
        if 'PEND' in status_str or 'UNDER PROCESS' in status_str:
            pending_days = (max_ref_date - r_dt).days
            if pending_days > 75:
                df_out.at[idx, 'sla_sanction_breach'] = True
                df_out.at[idx, 'compliance_status'] = 'SANCTION_SLA_BREACH'
                df_out.at[idx, 'compliance_flag'] = True
            else:
                df_out.at[idx, 'compliance_status'] = 'COMPLIANT'
        elif 'REJECT' in status_str:
            rej_dt = pd.to_datetime(row.get('Rejection Date'), errors='coerce') if 'Rejection Date' in row else sanc_dt.iloc[idx]
            if pd.notnull(rej_dt) and (rej_dt - r_dt).days > 45:
                df_out.at[idx, 'sla_rejection_breach'] = True
                df_out.at[idx, 'compliance_status'] = 'REJECTION_NOTIFICATION_SLA_BREACH'
                df_out.at[idx, 'compliance_flag'] = True
            else:
                df_out.at[idx, 'compliance_status'] = 'COMPLIANT'
        else:
            # SANCTIONED / COMPLETED work execution stages
            df_out.at[idx, 'compliance_status'] = 'COMPLIANT'

    # MP Annual Policy Allocation Aggregation
    mp_col = "Hon'ble Members of Parliament"
    if mp_col in df_out.columns and 'sanc_dt' in df_out.columns:
        df_out['fin_year'] = df_out['sanc_dt'].dt.year
        valid_sanc = df_out[~df_out['is_below_floor'] & df_out['fin_year'].notnull()].copy()
        
        mp_year_sums = valid_sanc.groupby([mp_col, 'fin_year'])['sanction_amount'].sum()
        over_cap_keys = set(mp_year_sums[mp_year_sums > 50000000.0].index)  # ₹5 Crore policy limit
        
        for idx, row in df_out.iterrows():
            key = (row.get(mp_col), row.get('fin_year'))
            if key in over_cap_keys:
                df_out.at[idx, 'mp_allocation_status'] = 'POLICY_REVIEW'

        df_out.drop(columns=['fin_year'], errors='ignore', inplace=True)

    return df_out
