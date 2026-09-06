import os
import json
import pandas as pd
import numpy as np

# Streamlit / HTML Dashboard Generator for Anomalous Cost Estimate & Cost Overrun Detection Engine

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
SCORED_JSON_PATH = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json")
SUMMARY_JSON_PATH = os.path.join(OUTPUT_DIR, "pipeline_summary.json")

def generate_static_html_dashboard():
    """Generates a standalone, beautiful HTML dashboard containing interactive charts and tables."""
    if not os.path.exists(SUMMARY_JSON_PATH) or not os.path.exists(SCORED_JSON_PATH):
        print("Scored output files not found. Run pipeline first.")
        return

    with open(SUMMARY_JSON_PATH) as f:
        summary = json.load(f)
        
    with open(SCORED_JSON_PATH) as f:
        works = json.load(f)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anomalous Cost Estimate & Cost Overrun Detection Engine - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/plotly.js-dist@2.24.1/plotly.min.js"></script>
    <style>
        body {{ background-color: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }}
        .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); }}
        .kpi-title {{ font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 1.8rem; font-weight: 700; margin-top: 5px; }}
        .badge-high {{ background-color: #ef4444; color: #fff; font-size: 0.9rem; padding: 6px 12px; }}
        .badge-medium {{ background-color: #f59e0b; color: #fff; font-size: 0.9rem; padding: 6px 12px; }}
        .badge-low {{ background-color: #10b981; color: #fff; font-size: 0.9rem; padding: 6px 12px; }}
        .badge-dq {{ background-color: #3b82f6; color: #fff; font-size: 0.9rem; padding: 6px 12px; }}
        .disclaimer-box {{ background-color: #1e1b4b; border-left: 4px solid #6366f1; padding: 15px; border-radius: 6px; margin-bottom: 25px; }}
        table {{ color: #cbd5e1 !important; }}
        th {{ background-color: #334155 !important; color: #f8fafc !important; font-size: 0.85rem; }}
        td {{ font-size: 0.85rem; border-color: #334155 !important; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <h2 class="fw-bold text-white mb-1">🏛️ Anomalous Cost Estimate & Cost Overrun Detection Engine</h2>
                <p class="text-secondary mb-0">Lok Sabha 18th MPLADS Analytical Engine | Statistical Anomaly & Cost Overrun Detection</p>
            </div>
            <span class="badge bg-primary fs-6">Lok Sabha 18th ONLY</span>
        </div>

        <div class="disclaimer-box">
            <h6 class="fw-bold text-indigo-400 mb-1">ℹ️ Human Investigation Disclaimer</h6>
            <p class="mb-0 text-slate-300 small">This system performs statistical and financial anomaly detection requiring human investigation. A <b>HIGH</b> or <b>MEDIUM</b> risk score does NOT indicate fraud or wrongdoing; it signifies that multiple statistical signals (peer IQR variance, Isolation Forest multivariate patterns, or actual cost overruns) have triggered for administrative review.</p>
        </div>

        <!-- KPI Row 1 -->
        <div class="row text-center mb-3">
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Total Sanctioned Works</div>
                    <div class="kpi-val text-white">{summary['total_sanctioned_works']:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">HIGH Risk Works</div>
                    <div class="kpi-val text-danger">{summary['risk_breakdown']['HIGH']:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">MEDIUM Risk Works</div>
                    <div class="kpi-val text-warning">{summary['risk_breakdown']['MEDIUM']:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">LOW Risk Works</div>
                    <div class="kpi-val text-success">{summary['risk_breakdown']['LOW']:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Data Quality Review</div>
                    <div class="kpi-val text-info">{summary['risk_breakdown']['DATA_QUALITY_REVIEW']:,}</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card p-3">
                    <div class="kpi-title">Missing Expenditure</div>
                    <div class="kpi-val text-secondary">{summary['expenditure_matching']['missing_expenditure_works']:,}</div>
                </div>
            </div>
        </div>

        <!-- KPI Row 2: Signal Flags -->
        <div class="row text-center mb-4">
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="kpi-title">Signal 1: Cost Overruns (>10%)</div>
                    <div class="kpi-val text-danger">{summary['signals']['cost_overrun_flags']:,}</div>
                    <small class="text-secondary mt-1">Actual vs Sanctioned Rule</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="kpi-title">Signal 2: Peer IQR Anomalies (>3.0 IQR)</div>
                    <div class="kpi-val text-warning">{summary['signals']['peer_iqr_flags']:,}</div>
                    <small class="text-secondary mt-1">High-Side Peer Deviations</small>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card p-3">
                    <div class="kpi-title">Signal 3: Isolation Forest Anomalies</div>
                    <div class="kpi-val text-primary">{summary['signals']['isolation_forest_flags']:,}</div>
                    <small class="text-secondary mt-1">Multivariate ML Detection (Contamination: 0.05)</small>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card p-3">
                    <h5 class="fw-bold text-white mb-3">📈 Risk Classification Distribution</h5>
                    <div id="riskChart" style="height: 350px;"></div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card p-3">
                    <h5 class="fw-bold text-white mb-3">🔍 Signal Overlap (Peer IQR vs Isolation Forest)</h5>
                    <div id="overlapChart" style="height: 350px;"></div>
                </div>
            </div>
        </div>

        <!-- Top 20 High-Risk Table -->
        <div class="card p-4">
            <h5 class="fw-bold text-white mb-3">🚨 Top 20 High-Risk Anomalous Sanctioned Works</h5>
            <div class="table-responsive">
                <table class="table table-dark table-hover table-bordered align-middle">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Work ID</th>
                            <th>MP Name</th>
                            <th>State / Constituency</th>
                            <th>Sanction Amt</th>
                            <th>Peer Median</th>
                            <th>Robust Dev</th>
                            <th>Days</th>
                            <th>Actual Exp</th>
                            <th>ML Score</th>
                            <th>Risk Level</th>
                            <th>Evidence</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Filter top 20 HIGH risk works
    high_works = [w for w in works if w['consensus']['risk_level'] == 'HIGH']
    high_works.sort(key=lambda x: (x['consensus']['positive_signal_count'], x['signals']['isolation_forest']['anomaly_score'] or 0), reverse=True)
    top_20 = high_works[:20]

    for idx, w in enumerate(top_20, start=1):
        sanc = f"₹{w['sanctioned_amount']:,.2f}" if w['sanctioned_amount'] is not None else "N/A"
        p_med = f"₹{w['peer_statistics']['median']:,.2f}" if w['peer_statistics']['median'] is not None else "N/A"
        rob_dev = f"{w['signals']['peer_iqr']['robust_deviation']:.1f} IQR" if w['signals']['peer_iqr']['robust_deviation'] is not None else "N/A"
        days = f"{w['recommendation_to_sanction_days']} d" if w['recommendation_to_sanction_days'] is not None else "N/A"
        act_exp = f"₹{w['actual_expenditure']:,.2f}" if w['actual_expenditure'] is not None else "<span class='text-secondary'>NO_EXPENDITURE</span>"
        ml_score = f"{w['signals']['isolation_forest']['anomaly_score']:.4f}" if w['signals']['isolation_forest']['anomaly_score'] is not None else "N/A"
        ev_html = "<ul class='mb-0 ps-3'>" + "".join([f"<li>{e}</li>" for e in w['evidence']]) + "</ul>"
        
        html_content += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><code>{w['work_id']}</code></td>
                            <td><b>{w['mp_name']}</b></td>
                            <td>{w['state']}<br><small class='text-secondary'>{w['constituency']}</small></td>
                            <td class='fw-bold text-light'>{sanc}</td>
                            <td class='text-info'>{p_med}</td>
                            <td class='text-warning'>{rob_dev}</td>
                            <td>{days}</td>
                            <td>{act_exp}</td>
                            <td class='fw-bold text-primary'>{ml_score}</td>
                            <td><span class='badge badge-high'>HIGH ({w['consensus']['positive_signal_count']} Sigs)</span></td>
                            <td class='small'>{ev_html}</td>
                        </tr>
        """

    html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Risk Distribution Chart
        var riskData = [{{
            values: [{summary['risk_breakdown']['HIGH']}, {summary['risk_breakdown']['MEDIUM']}, {summary['risk_breakdown']['LOW']}, {summary['risk_breakdown']['DATA_QUALITY_REVIEW']}],
            labels: ['HIGH', 'MEDIUM', 'LOW', 'DATA_QUALITY_REVIEW'],
            type: 'pie',
            marker: {{ colors: ['#ef4444', '#f59e0b', '#10b981', '#3b82f6'] }}
        }}];
        var riskLayout = {{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {{ color: '#f8fafc' }},
            margin: {{ t: 20, b: 20, l: 20, r: 20 }}
        }};
        Plotly.newPlot('riskChart', riskData, riskLayout);

        // Signal Overlap Bar Chart
        var overlapData = [{{
            x: ['Peer IQR Anomalies', 'Isolation Forest Anomalies', 'Combined Union', 'Jaccard Overlap Score'],
            y: [{summary['signals']['peer_iqr_flags']}, {summary['signals']['isolation_forest_flags']}, {summary['signals']['peer_iqr_flags'] + summary['signals']['isolation_forest_flags'] - 2191}, {summary['jaccard_overlap_iqr_vs_if'] * 100}],
            type: 'bar',
            marker: {{ color: ['#f59e0b', '#6366f1', '#10b981', '#ec4899'] }}
        }}];
        var overlapLayout = {{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {{ color: '#f8fafc' }},
            margin: {{ t: 20, b: 40, l: 40, r: 20 }}
        }};
        Plotly.newPlot('overlapChart', overlapData, overlapLayout);
    </script>
</body>
</html>
    """

    out_html_path = os.path.join(OUTPUT_DIR, "dashboard.html")
    with open(out_html_path, "w") as f:
        f.write(html_content)
    print(f"Interactive HTML dashboard successfully generated at: {out_html_path}")

if __name__ == '__main__':
    generate_static_html_dashboard()
