import os
import sys
import json
import gzip
import pandas as pd
import numpy as np

# Add local vendor directory to sys.path if present for maximum portability
vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
SCORED_JSON_PATH = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json")
SCORED_GZ_PATH = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json.gz")
SUMMARY_JSON_PATH = os.path.join(OUTPUT_DIR, "pipeline_summary.json")
DOUBLE_DIPPING_JSON_PATH = os.path.join(OUTPUT_DIR, "double_dipping_results.json")
DELAYED_JSON_PATH = os.path.join(OUTPUT_DIR, "delayed_projects_results.json")
COMPLIANCE_JSON_PATH = os.path.join(OUTPUT_DIR, "compliance_results.json")
VENDOR_JSON_PATH = os.path.join(OUTPUT_DIR, "vendor_agency_risk.json")
FORECAST_JSON_PATH = os.path.join(OUTPUT_DIR, "expenditure_forecast.json")
PRIORITY_JSON_PATH = os.path.join(OUTPUT_DIR, "misuse_priority_results.json")
INADMISSIBLE_JSON_PATH = os.path.join(OUTPUT_DIR, "inadmissible_works_results.json")
PRIVATE_JSON_PATH = os.path.join(OUTPUT_DIR, "private_beneficiaries_results.json")
DUP_EXP_JSON_PATH = os.path.join(OUTPUT_DIR, "duplicate_expenditure_results.json")
FUND_UTIL_JSON_PATH = os.path.join(OUTPUT_DIR, "fund_utilization_results.json")
CORPORA_JSON_PATH = os.path.join(OUTPUT_DIR, "corpora_summary.json")
DEEP_EVAL_JSON_PATH = os.path.join(OUTPUT_DIR, "ALL_DATASETS_DEEP_EVALUATION.json")

def generate_static_html_dashboard():
    """Generates a standalone Apple-inspired Audit Intelligence HTML Dashboard with embedded data."""
    if not os.path.exists(SUMMARY_JSON_PATH):
        print("Pipeline summary missing. Run pipeline first.")
        return

    with open(SUMMARY_JSON_PATH) as f:
        summary = json.load(f)

    corpora_data = json.load(open(CORPORA_JSON_PATH)) if os.path.exists(CORPORA_JSON_PATH) else {}
    dd_data = json.load(open(DOUBLE_DIPPING_JSON_PATH)) if os.path.exists(DOUBLE_DIPPING_JSON_PATH) else {}
    compliance_data = json.load(open(COMPLIANCE_JSON_PATH)) if os.path.exists(COMPLIANCE_JSON_PATH) else {}
    vendor_data = json.load(open(VENDOR_JSON_PATH)) if os.path.exists(VENDOR_JSON_PATH) else {}
    forecast_data = json.load(open(FORECAST_JSON_PATH)) if os.path.exists(FORECAST_JSON_PATH) else {}
    priority_data = json.load(open(PRIORITY_JSON_PATH)) if os.path.exists(PRIORITY_JSON_PATH) else {}
    inadmissible_data = json.load(open(INADMISSIBLE_JSON_PATH)) if os.path.exists(INADMISSIBLE_JSON_PATH) else {}
    private_data = json.load(open(PRIVATE_JSON_PATH)) if os.path.exists(PRIVATE_JSON_PATH) else {}
    dup_exp_data = json.load(open(DUP_EXP_JSON_PATH)) if os.path.exists(DUP_EXP_JSON_PATH) else {}
    fund_util_data = json.load(open(FUND_UTIL_JSON_PATH)) if os.path.exists(FUND_UTIL_JSON_PATH) else {}
    deep_eval_data = json.load(open(DEEP_EVAL_JSON_PATH)) if os.path.exists(DEEP_EVAL_JSON_PATH) else {}

    scored_works = []
    if os.path.exists(SCORED_JSON_PATH):
        with open(SCORED_JSON_PATH) as f:
            scored_works = json.load(f)
    elif os.path.exists(SCORED_GZ_PATH):
        with gzip.open(SCORED_GZ_PATH, "rt", encoding="utf-8") as f:
            scored_works = json.load(f)

    # Take top scored works, priority records, and candidate pairs sample for standalone offline rendering (keep under 20MB)
    scored_sample = scored_works[:200]
    priority_sample = {
        "summary": priority_data.get("summary", {}),
        "disclaimer": priority_data.get("disclaimer", ""),
        "records": priority_data.get("records", [])[:200]
    } if priority_data else {}

    dd_sample = {}
    if dd_data:
        for k, v in dd_data.items():
            if k not in ['top_suspicious_pairs', 'pairs']:
                dd_sample[k] = v
        if 'top_suspicious_pairs' in dd_data:
            dd_sample['top_suspicious_pairs'] = dd_data['top_suspicious_pairs'][:200]
        if 'pairs' in dd_data:
            dd_sample['pairs'] = dd_data['pairs'][:200]

    compliance_sample = {}
    if compliance_data:
        compliance_sample = {
            "summary": compliance_data.get("summary", {}),
            "ia_watchlist": compliance_data.get("ia_watchlist", [])
        }

    embedded_payload = {
        "summary": summary,
        "corpora": corpora_data,
        "priority": priority_sample,
        "double_dipping": dd_sample,
        "compliance": compliance_sample,
        "vendor": vendor_data,
        "forecast": forecast_data,
        "inadmissible": inadmissible_data,
        "private": private_data,
        "dup_exp": dup_exp_data,
        "fund_util": fund_util_data,
        "deep_eval": deep_eval_data,
        "works": scored_sample
    }

    # Load CSS and JS from frontend template
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_demo", "frontend")
    css_path = os.path.join(frontend_dir, "style.css")
    js_path = os.path.join(frontend_dir, "app.js")
    html_path = os.path.join(frontend_dir, "index.html")

    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

    js_content = ""
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

    html_template = ""
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_template = f.read()

    # Inject embedded CSS, payload, and JS into standalone HTML
    standalone_html = html_template.replace(
        '<link rel="stylesheet" href="style.css">',
        f'<style>{css_content}</style>'
    ).replace(
        '<script src="app.js"></script>',
        f'<script>window.__EMBEDDED_DATA__ = {json.dumps(embedded_payload)};</script>\n<script>{js_content}</script>'
    )

    out_html_path = os.path.join(OUTPUT_DIR, "dashboard.html")
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(standalone_html)
    print(f"Standalone Apple-Inspired HTML dashboard successfully generated at: {out_html_path}")

if __name__ == '__main__':
    generate_static_html_dashboard()
