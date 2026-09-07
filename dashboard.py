import os
import sys
import json
import pandas as pd
import numpy as np

# Add local vendor directory to sys.path if present for maximum portability
vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
SCORED_JSON_PATH = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json")
SUMMARY_JSON_PATH = os.path.join(OUTPUT_DIR, "pipeline_summary.json")
DOUBLE_DIPPING_JSON_PATH = os.path.join(OUTPUT_DIR, "double_dipping_results.json")
DELAYED_JSON_PATH = os.path.join(OUTPUT_DIR, "delayed_projects_results.json")
COMPLIANCE_JSON_PATH = os.path.join(OUTPUT_DIR, "compliance_results.json")
VENDOR_JSON_PATH = os.path.join(OUTPUT_DIR, "vendor_agency_risk.json")
FORECAST_JSON_PATH = os.path.join(OUTPUT_DIR, "expenditure_forecast.json")
PRIORITY_JSON_PATH = os.path.join(OUTPUT_DIR, "misuse_priority_results.json")

def generate_static_html_dashboard():
    """Generates a standalone HTML dashboard organized into DETECT, PREDICT, VERIFY, and PRIORITIZE tabs."""
    if not os.path.exists(SUMMARY_JSON_PATH) or not os.path.exists(SCORED_JSON_PATH):
        print("Scored output files not found. Run pipeline first.")
        return

    with open(SUMMARY_JSON_PATH) as f:
        summary = json.load(f)
        
    with open(SCORED_JSON_PATH) as f:
        works = json.load(f)

    dd_data = json.load(open(DOUBLE_DIPPING_JSON_PATH)) if os.path.exists(DOUBLE_DIPPING_JSON_PATH) else None
    delay_data = json.load(open(DELAYED_JSON_PATH)) if os.path.exists(DELAYED_JSON_PATH) else None
    compliance_data = json.load(open(COMPLIANCE_JSON_PATH)) if os.path.exists(COMPLIANCE_JSON_PATH) else None
    vendor_data = json.load(open(VENDOR_JSON_PATH)) if os.path.exists(VENDOR_JSON_PATH) else None
    forecast_data = json.load(open(FORECAST_JSON_PATH)) if os.path.exists(FORECAST_JSON_PATH) else None
    priority_data = json.load(open(PRIORITY_JSON_PATH)) if os.path.exists(PRIORITY_JSON_PATH) else None

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MPLADS AI Intelligence System — Operational Audit Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <style>
        body {{ background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }}
        .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }}
        .kpi-title {{ font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 1.7rem; font-weight: 700; margin-top: 5px; }}
        .badge-high {{ background-color: #ef4444; color: #fff; font-size: 0.85rem; padding: 6px 12px; }}
        .badge-medium {{ background-color: #f59e0b; color: #fff; font-size: 0.85rem; padding: 6px 12px; }}
        .badge-low {{ background-color: #10b981; color: #fff; font-size: 0.85rem; padding: 6px 12px; }}
        .disclaimer-box {{ background-color: #1e1b4b; border-left: 4px solid #6366f1; padding: 15px; border-radius: 6px; margin-bottom: 25px; }}
        .pipeline-flow {{ background-color: #0f172a; border: 1px dashed #475569; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.85rem; color: #38bdf8; }}
        table {{ color: #cbd5e1 !important; }}
        th {{ background-color: #334155 !important; color: #f8fafc !important; font-size: 0.85rem; }}
        td {{ font-size: 0.85rem; border-color: #334155 !important; }}
        .nav-tabs .nav-link {{ color: #94a3b8; font-weight: 600; font-size: 1rem; border: none; padding: 12px 20px; }}
        .nav-tabs .nav-link.active {{ color: #38bdf8; background-color: #1e293b; border-bottom: 3px solid #38bdf8; border-radius: 6px 6px 0 0; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <h2 class="fw-bold text-white mb-1">🏛️ MPLADS AI Intelligence & Audit Decision-Support System</h2>
                <p class="text-secondary mb-0">Lok Sabha 18th Master Operational Dashboard | DETECT • PREDICT • VERIFY • PRIORITIZE</p>
            </div>
            <span class="badge bg-primary fs-6">Lok Sabha 18th ONLY</span>
        </div>

        <div class="disclaimer-box">
            <h6 class="fw-bold text-indigo-400 mb-1">ℹ️ Statutory Audit Decision-Support Governance Standard</h6>
            <p class="mb-0 text-slate-300 small">This system performs multi-model statistical, procedural, network, and record-linkage anomaly triage to prioritize administrative audit reviews. Classifications such as <b>CRITICAL AUDIT PRIORITY</b> or <b>HIGH RISK — REQUIRES AUDIT REVIEW</b> do NOT indicate fraud or criminal intent. All anomalies require human administrative investigation.</p>
        </div>

        <!-- KPI Summary Cards -->
        <div class="row text-center mb-3">
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Master Work Entities</div>
                    <div class="kpi-val text-white">{summary.get('reconciliation', {}).get('master_work_entities', summary.get('total_sanctioned_works', 0)):,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Critical Audit Priority</div>
                    <div class="kpi-val text-danger">{priority_data.get('summary', {}).get('critical_audit_priority_count', 0) if priority_data else 0:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Cost Anomaly High</div>
                    <div class="kpi-val text-warning">{summary.get('model_2_cost_overrun', {}).get('risk_breakdown', {}).get('HIGH', 0):,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Delayed Works</div>
                    <div class="kpi-val text-warning">{delay_data.get('summary', {}).get('total_delayed_works', 0) if delay_data else 0:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Compliance Deviations</div>
                    <div class="kpi-val text-info">{compliance_data.get('summary', {}).get('total_deviations', 0) if compliance_data else 0:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Vendor Concentration Risk</div>
                    <div class="kpi-val text-danger">{vendor_data.get('summary', {}).get('high_concentration_agencies', 0) if vendor_data else 0:,}</div>
                </div>
            </div>
        </div>

        <!-- OPERATIONAL TABS -->
        <ul class="nav nav-tabs mb-4" id="auditTabs" role="tablist">
            <li class="nav-item"><button class="nav-link active" id="prioritize-tab" data-bs-toggle="tab" data-bs-target="#prioritize" type="button">1. PRIORITIZE (Model 5)</button></li>
            <li class="nav-item"><button class="nav-link" id="detect-tab" data-bs-toggle="tab" data-bs-target="#detect" type="button">2. DETECT (Models 1 & 2)</button></li>
            <li class="nav-item"><button class="nav-link" id="verify-tab" data-bs-toggle="tab" data-bs-target="#verify" type="button">3. VERIFY (Models 3, 4 & Vendor Risk)</button></li>
            <li class="nav-item"><button class="nav-link" id="predict-tab" data-bs-toggle="tab" data-bs-target="#predict" type="button">4. PREDICT (Forecasting)</button></li>
        </ul>

        <div class="tab-content" id="auditTabsContent">
            <!-- TAB 1: PRIORITIZE -->
            <div class="tab-pane fade show active" id="prioritize" role="tabpanel">
                <div class="card p-4 mb-4" style="border: 2px solid #ef4444;">
                    <h4 class="fw-bold text-white mb-2">🎯 Model 5 — Audit Priority & Misuse Aggregator</h4>
                    <p class="text-secondary small mb-3">Multi-signal priority scoring combining Cost Overrun, Peer Delay, Statutory Compliance, Vendor Concentration, and Duplicate Record Linkage.</p>
                    <div class="table-responsive">
                        <table class="table table-dark table-hover table-bordered align-middle">
                            <thead>
                                <tr><th>#</th><th>Work ID</th><th>MP / Constituency</th><th>Sanction Amt</th><th>Cost</th><th>Delay</th><th>Compliance</th><th>Display Score</th><th>Priority Tier</th><th>Combined Evidence</th></tr>
                            </thead>
                            <tbody>
    """
    if priority_data:
        crit_records = [r for r in priority_data.get('records', []) if r.get('audit_priority') == 'CRITICAL_AUDIT_PRIORITY'][:15]
        for idx, r in enumerate(crit_records, start=1):
            sanc = f"₹{r['sanction_amount']:,.2f}"
            ev_list = "".join([f"<li>{ev}</li>" for ev in r['combined_evidence']])
            html_content += f"""
                                <tr>
                                    <td>{idx}</td>
                                    <td><code>{r['clean_work_id']}</code></td>
                                    <td><b>{r['mp']}</b><br><small class='text-secondary'>{r['state']} | {r['constituency']}</small></td>
                                    <td class='fw-bold text-light'>{sanc}</td>
                                    <td><span class='badge bg-danger'>{r['cost_risk_level']}</span></td>
                                    <td><span class='badge bg-warning text-dark'>{r['delay_status']}</span></td>
                                    <td><span class='badge bg-info text-dark'>{r['compliance_severity']}</span></td>
                                    <td class='fw-bold text-primary fs-6'>{r['display_score']}/100</td>
                                    <td><span class='badge badge-high'>{r['audit_priority']}</span></td>
                                    <td class='small'><ul class='mb-0 ps-3 text-warning'>{ev_list}</ul></td>
                                </tr>
            """
    html_content += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 2: DETECT -->
            <div class="tab-pane fade" id="detect" role="tabpanel">
                <div class="card p-4 mb-4">
                    <h4 class="fw-bold text-white mb-2">🔍 Model 1 — Double-Dipping & Model 2 — Cost Overrun Engine</h4>
                    <p class="text-secondary small mb-3">Record linkage for distinct potential duplicate work pairs alongside hierarchical peer IQR/MAD and Isolation Forest ML cost estimate anomaly detection.</p>
    """
    cross_msg = "Cross-House LS↔RS Detection: Ready — Rajya Sabha data not currently available"
    if dd_data and 'cross_house_display_message' in dd_data:
        cross_msg = dd_data['cross_house_display_message']
    html_content += f"""
                    <div class="alert alert-info py-2 small mb-3">
                        <b>🏛️ Chamber Scope:</b> {cross_msg}
                    </div>
                </div>
            </div>

            <!-- TAB 3: VERIFY -->
            <div class="tab-pane fade" id="verify" role="tabpanel">
                <div class="card p-4 mb-4">
                    <h4 class="fw-bold text-white mb-2">⏱️ Model 3 — Peer Delay, Model 4 — Statutory Compliance & Vendor Risk</h4>
                    <p class="text-secondary small mb-3">Peer-relative Tukey IQR delay baseline checks, statutory 45-day approval window deviations, Implementing Agency (IDA) Watchlist, and Vendor Concentration Risk (HHI).</p>
                </div>
            </div>

            <!-- TAB 4: PREDICT -->
            <div class="tab-pane fade" id="predict" role="tabpanel">
                <div class="card p-4 mb-4">
                    <h4 class="fw-bold text-white mb-2">📈 MPLADS Expenditure Forecasting Model</h4>
                    <span class="badge bg-secondary mb-2" style="width: fit-content;">Predictive Insight — Not Fraud Detection</span>
                    <p class="text-secondary small mb-3">12-month expected spending trend timeline with empirical 95% prediction bounds based on actual monthly expenditure utilization patterns.</p>
    """
    if forecast_data:
        timeline = forecast_data.get('forecast_records', forecast_data.get('timeline', []))
        fcst_status = forecast_data.get('status', 'SUCCESS')
        if fcst_status == 'INSUFFICIENT_DATA' or not timeline:
            html_content += """
                    <div class="alert alert-warning py-3 text-center">
                        <b>Forecast unavailable — insufficient historical observations</b>
                    </div>
            """
        else:
            html_content += """
                    <div class="table-responsive">
                        <table class="table table-dark table-hover table-bordered align-middle">
                            <thead>
                                <tr><th>Month</th><th>Type</th><th>Forecast Expenditure</th><th>Lower Bound (95%)</th><th>Upper Bound (95%)</th><th>Actual Expenditure</th><th>Status & Evidence</th></tr>
                            </thead>
                            <tbody>
            """
            for row in timeline:
                m_str = row.get('month', row.get('forecast_date', ''))
                t_str = row.get('type', 'OBSERVED')
                fcst_str = f"₹{row.get('forecast_expenditure', row.get('expected_expenditure', 0.0)):,.2f}"
                low_str = f"₹{row.get('lower_bound', 0.0):,.2f}"
                upp_str = f"₹{row.get('upper_bound', 0.0):,.2f}"
                act_val = row.get('actual_expenditure')
                act_str = f"₹{act_val:,.2f}" if act_val is not None else "<span class='text-muted'>Pending</span>"
                
                st_val = row.get('deviation_status', 'NORMAL')
                if 'ABOVE' in st_val or 'BELOW' in st_val or row.get('utilization_warning'):
                    warn_badge = "<span class='badge bg-warning text-dark'>" + st_val + "</span>"
                else:
                    warn_badge = "<span class='badge bg-success'>" + st_val + "</span>"
                    
                ev_str = row.get('evidence', '')
                html_content += f"""
                                <tr>
                                    <td><b>{m_str}</b></td>
                                    <td><small class='text-secondary'>{t_str}</small></td>
                                    <td class='text-info'>{fcst_str}</td>
                                    <td class='text-secondary'>{low_str}</td>
                                    <td class='text-secondary'>{upp_str}</td>
                                    <td class='fw-bold text-light'>{act_str}</td>
                                    <td>{warn_badge} <small class='text-secondary d-block'>{ev_str}</small></td>
                                </tr>
                """
            html_content += """
                            </tbody>
                        </table>
                    </div>
            """
    else:
        html_content += """
                    <div class="alert alert-warning py-3 text-center">
                        <b>Forecast unavailable — insufficient historical observations</b>
                    </div>
        """
    html_content += """
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """

    out_html_path = os.path.join(OUTPUT_DIR, "dashboard.html")
    with open(out_html_path, "w") as f:
        f.write(html_content)
    print(f"Interactive HTML dashboard successfully generated at: {out_html_path}")

if __name__ == '__main__':
    generate_static_html_dashboard()

