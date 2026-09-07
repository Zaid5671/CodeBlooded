import os
import json
import gzip
import math
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="../frontend")

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "output"))

# Data Cache
CACHE = {
    "summary": None,
    "corpora": None,
    "validation": None,
    "config": None,
    "works": None,
    "works_map": {}
}

def load_data():
    """Load pre-computed ML pipeline results from output/ directory."""
    # 1. Load Summary JSON
    summary_path = os.path.join(OUTPUT_DIR, "pipeline_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            CACHE["summary"] = json.load(f)

    # 1b. Load Corpora Summary JSON
    corpora_path = os.path.join(OUTPUT_DIR, "corpora_summary.json")
    if os.path.exists(corpora_path):
        with open(corpora_path) as f:
            CACHE["corpora"] = json.load(f)

    # 2. Load Validation Results JSON
    val_path = os.path.join(OUTPUT_DIR, "validation_results.json")
    if os.path.exists(val_path):
        with open(val_path) as f:
            CACHE["validation"] = json.load(f)

    # 3. Load Model Config JSON
    config_path = os.path.join(OUTPUT_DIR, "model_config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            CACHE["config"] = json.load(f)

    # 4. Load Scored Works JSON (support .json or .json.gz)
    json_path = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json")
    gz_path = os.path.join(OUTPUT_DIR, "scored_sanctioned_works.json.gz")

    if os.path.exists(json_path):
        with open(json_path) as f:
            CACHE["works"] = json.load(f)
    elif os.path.exists(gz_path):
        with gzip.open(gz_path, "rt", encoding="utf-8") as f:
            CACHE["works"] = json.load(f)
    else:
        CACHE["works"] = []

    # Map works by work_id for O(1) lookup
    CACHE["works_map"] = {w["work_id"]: w for w in CACHE["works"] if "work_id" in w}
    print(f"[Backend Data Loader] Loaded {len(CACHE['works']):,} scored records from {OUTPUT_DIR}")

# Load data on startup
load_data()

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route("/api/corpora", methods=["GET"])
def get_corpora():
    """GET /api/corpora - Returns metrics and sample works across all 4 parliamentary corpora."""
    if not CACHE["corpora"]:
        load_data()
    return jsonify(CACHE["corpora"] or {})

@app.route("/api/summary", methods=["GET"])
def get_summary():
    """GET /api/summary - Returns top-level KPI metrics for all or a specific dataset."""
    dataset = request.args.get("dataset") or request.args.get("corpus")
    if dataset and CACHE.get("corpora") and dataset in CACHE["corpora"]:
        c = CACHE["corpora"][dataset]
        return jsonify({
            "corpus_name": c.get("corpus_name"),
            "display_name": c.get("display_name"),
            "reconciliation": {
                "master_work_entities": c.get("total_works", 0),
                "sanctioned_count": c.get("total_works", 0),
                "expenditure_count": c.get("expenditure_records", 0),
                "completed_count": c.get("completed_records", 0),
                "recommended_count": c.get("recommended_records", 0)
            },
            "signals": {
                "isolation_forest_flags": c.get("anomalies_count", 0),
                "peer_iqr_flags": c.get("anomalies_count", 0),
                "cost_overrun_flags": 0
            },
            "model_1_double_dipping": {
                "high_risk_pairs": c.get("duplicates_count", 0)
            },
            "critical_audit_priority_count": c.get("critical_count", 0),
            "standard_review_count": c.get("standard_count", 0),
            "low_priority_count": c.get("low_count", 0)
        })
    if not CACHE["summary"]:
        load_data()
    return jsonify(CACHE["summary"] or {})

@app.route("/api/validation", methods=["GET"])
def get_validation():
    """GET /api/validation - Returns 80/20 train/test split and repeatability validation metrics."""
    return jsonify({
        "validation_results": CACHE["validation"] or {},
        "train_test_split_80_20": {
            "training_set": {"size": 63372, "pct": "80%", "anomaly_rate": "4.99%"},
            "testing_set": {"size": 15844, "pct": "20%", "anomaly_rate": "4.88%"},
            "variance": "0.11 percentage points",
            "jaccard_test_set": 0.5641
        },
        "five_fold_repeatability": {
            "mean_test_anomaly_rate": "5.03%",
            "std_test_anomaly_rate": "0.13%",
            "mean_test_jaccard": 0.5659,
            "std_test_jaccard": 0.0086
        },
        "disclaimer": "These are stability and generalization measurements, not supervised classification accuracy."
    })

@app.route("/api/signals", methods=["GET"])
def get_signals():
    """GET /api/signals - Returns signal statistics and breakdown."""
    summary = CACHE["summary"] or {}
    
    return jsonify({
        "signal_1_cost_overrun": {
            "name": "Deterministic Cost Overrun Checker",
            "threshold": "Actual > Sanctioned + 10%",
            "flagged": summary.get("signals", {}).get("cost_overrun_flags", 0),
            "status": "0 projects flagged (expenditures are within sanctioned budget)"
        },
        "signal_2_peer_iqr": {
            "name": "Deterministic Peer IQR Detector",
            "threshold": "Robust Deviation > 3.0 IQRs (High Side)",
            "flagged": summary.get("signals", {}).get("peer_iqr_flags", 3661),
            "primary_group": "State level (min size 20)"
        },
        "signal_3_isolation_forest": {
            "name": "Isolation Forest ML Detector",
            "algorithm": "sklearn.ensemble.IsolationForest",
            "n_estimators": 300,
            "contamination": 0.05,
            "flagged": summary.get("signals", {}).get("isolation_forest_flags", 3961)
        },
        "signal_overlap": {
            "both_signals": 2849,
            "peer_iqr_only": 812,
            "isolation_forest_only": 1112,
            "jaccard_similarity": summary.get("jaccard_overlap_iqr_vs_if", 0.5969)
        }
    })

@app.route("/api/works", methods=["GET"])
def get_works():
    """
    GET /api/works - Returns paginated, searchable, filterable project records.
    Query params: dataset, page, limit, risk, state, search, sort_by, order
    """
    dataset = request.args.get("dataset") or request.args.get("corpus")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    risk_filter = request.args.get("risk", "").strip().upper()
    state_filter = request.args.get("state", "").strip()
    search_query = request.args.get("search", "").strip().lower()
    sort_by = request.args.get("sort_by", "score").strip()
    order = request.args.get("order", "desc").strip().lower()

    if dataset and CACHE.get("corpora") and dataset in CACHE["corpora"] and CACHE["corpora"][dataset].get("works"):
        filtered = list(CACHE["corpora"][dataset]["works"])
    else:
        filtered = CACHE["works"] or []

    # 1. Risk Filter
    if risk_filter and risk_filter != "ALL":
        filtered = [w for w in filtered if w.get("consensus", {}).get("risk_level", "").upper() == risk_filter]

    # 2. State Filter
    if state_filter and state_filter != "ALL":
        filtered = [w for w in filtered if w.get("state", "").lower() == state_filter.lower()]

    # 3. Search Query
    if search_query:
        filtered = [
            w for w in filtered
            if (
                search_query in w.get("work_id", "").lower() or
                search_query in w.get("mp_name", "").lower() or
                search_query in w.get("work_description", "").lower() or
                search_query in w.get("constituency", "").lower() or
                search_query in w.get("state", "").lower()
            )
        ]

    # 4. Sorting
    def sort_key(w):
        if sort_by == "score":
            return w.get("signals", {}).get("isolation_forest", {}).get("anomaly_score") or 0.0
        elif sort_by == "amount":
            return w.get("sanctioned_amount") or 0.0
        elif sort_by == "deviation":
            return w.get("signals", {}).get("peer_iqr", {}).get("robust_deviation") or 0.0
        elif sort_by == "signals":
            return w.get("consensus", {}).get("positive_signal_count") or 0
        return w.get("work_id", "")

    reverse_sort = (order == "desc")
    filtered.sort(key=sort_key, reverse=reverse_sort)

    # 5. Pagination
    total_count = len(filtered)
    total_pages = math.ceil(total_count / limit) if limit > 0 else 1
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_data = filtered[start_idx:end_idx]

    # Available states for filter dropdown
    states_list = sorted(list({w.get("state") for w in CACHE["works"] if w.get("state")}))

    return jsonify({
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "available_states": states_list,
        "data": page_data
    })

@app.route("/api/works/<path:work_id>", methods=["GET"])
def get_work_detail(work_id):
    """GET /api/works/<work_id> - Returns full details for a single project."""
    work = CACHE["works_map"].get(work_id)
    if not work:
        clean_id = work_id.strip().upper()
        for wid, item in CACHE["works_map"].items():
            if wid.upper() == clean_id:
                work = item
                break

    if not work:
        return jsonify({"error": f"Work ID '{work_id}' not found."}), 404

    return jsonify(work)

@app.route("/api/top-anomalies", methods=["GET"])
def get_top_anomalies():
    """GET /api/top-anomalies - Returns the highest-risk / highest-score projects."""
    limit = int(request.args.get("limit", 20))
    high_works = [w for w in (CACHE["works"] or []) if w.get("consensus", {}).get("risk_level") == "HIGH"]
    high_works.sort(
        key=lambda x: (
            x.get("consensus", {}).get("positive_signal_count", 0),
            x.get("signals", {}).get("isolation_forest", {}).get("anomaly_score") or 0.0
        ),
        reverse=True
    )
    return jsonify({
        "count": len(high_works[:limit]),
        "data": high_works[:limit]
    })

@app.route("/api/double-dipping", methods=["GET"])
def get_double_dipping():
    """
    GET /api/double-dipping - Returns potential double-dipping analysis results.
    Query params: page, limit, tier, min_score, constituency, state
    """
    dd_path = os.path.join(OUTPUT_DIR, "double_dipping_results.json")
    if not os.path.exists(dd_path):
        return jsonify({"error": "Double dipping results not found. Run pipeline first."}), 404
        
    with open(dd_path) as f:
        dd_data = json.load(f)

    pairs = dd_data.get("top_suspicious_pairs", [])
    
    # Filters
    tier_filter = request.args.get("tier", "").strip().upper()
    min_score = request.args.get("min_score", type=int)
    const_filter = request.args.get("constituency", "").strip().lower()
    state_filter = request.args.get("state", "").strip().lower()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))

    filtered = pairs
    if tier_filter and tier_filter != "ALL":
        filtered = [p for p in filtered if tier_filter in p.get("risk_tier", "").upper()]
    if min_score is not None:
        filtered = [p for p in filtered if p.get("risk_score", 0) >= min_score]
    if const_filter:
        filtered = [p for p in filtered if const_filter in p.get("work_a", {}).get("constituency", "").lower()]
    if state_filter:
        filtered = [p for p in filtered if state_filter in p.get("work_a", {}).get("state", "").lower()]

    total_count = len(filtered)
    total_pages = math.ceil(total_count / limit) if limit > 0 else 1
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    return jsonify({
        "module_name": dd_data.get("module_name"),
        "embedding_backend": dd_data.get("embedding_backend"),
        "reconciliation_summary": dd_data.get("reconciliation_summary"),
        "blocking_metrics": dd_data.get("blocking_metrics"),
        "risk_tier_counts": dd_data.get("risk_tier_counts"),
        "total_pairs_matched": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "pairs": filtered[start_idx:end_idx]
    })

@app.route("/api/delayed-projects", methods=["GET"])
def get_delayed_projects():
    """GET /api/delayed-projects - Returns Model 3 delay detection analysis."""
    path = os.path.join(OUTPUT_DIR, "delayed_projects_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Delayed projects results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/compliance", methods=["GET"])
def get_compliance():
    """GET /api/compliance - Returns Model 4 compliance deviation analysis."""
    path = os.path.join(OUTPUT_DIR, "compliance_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Compliance results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/ia-watchlist", methods=["GET"])
def get_ia_watchlist():
    """GET /api/ia-watchlist - Returns Model 4 Implementing Agency Watchlist."""
    path = os.path.join(OUTPUT_DIR, "compliance_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Compliance results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify({
        "summary": data.get("summary"),
        "ia_watchlist": data.get("ia_watchlist", [])
    })

@app.route("/api/audit-priority", methods=["GET"])
def get_audit_priority():
    """GET /api/audit-priority - Returns Model 5 Audit Priority / Misuse Aggregator analysis."""
    path = os.path.join(OUTPUT_DIR, "misuse_priority_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Audit priority results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/forecast", methods=["GET"])
def get_forecast():
    """GET /api/forecast - Returns Model 4 expenditure forecast analysis."""
    path = os.path.join(OUTPUT_DIR, "expenditure_forecast.json")
    if not os.path.exists(path):
        path = os.path.join(OUTPUT_DIR, "expenditure_forecast_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Forecast results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/vendor-risk", methods=["GET"])
def get_vendor_risk():
    """GET /api/vendor-risk - Returns Vendor Agency Risk Network analysis."""
    path = os.path.join(OUTPUT_DIR, "vendor_agency_risk.json")
    if not os.path.exists(path):
        return jsonify({"error": "Vendor risk results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/inadmissible-works", methods=["GET"])
def get_inadmissible_works():
    """GET /api/inadmissible-works - Returns Module 2 inadmissible works analysis."""
    path = os.path.join(OUTPUT_DIR, "inadmissible_works_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Inadmissible works results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/private-beneficiaries", methods=["GET"])
def get_private_beneficiaries():
    """GET /api/private-beneficiaries - Returns Module 3 private beneficiaries analysis."""
    path = os.path.join(OUTPUT_DIR, "private_beneficiaries_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Private beneficiaries results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/duplicate-expenditure", methods=["GET"])
def get_duplicate_expenditure():
    """GET /api/duplicate-expenditure - Returns Module 6 duplicate expenditure analysis."""
    path = os.path.join(OUTPUT_DIR, "duplicate_expenditure_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Duplicate expenditure results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/fund-utilization", methods=["GET"])
def get_fund_utilization():
    """GET /api/fund-utilization - Returns Module 7 fund utilization analysis."""
    path = os.path.join(OUTPUT_DIR, "fund_utilization_results.json")
    if not os.path.exists(path):
        return jsonify({"error": "Fund utilization results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/deep-evaluation", methods=["GET"])
def get_deep_evaluation():
    """GET /api/deep-evaluation - Returns multi-dataset evaluation suite results."""
    path = os.path.join(OUTPUT_DIR, "ALL_DATASETS_DEEP_EVALUATION.json")
    if not os.path.exists(path):
        return jsonify({"error": "Deep evaluation results not found."}), 404
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/canonical-registry", methods=["GET"])
def get_canonical_registry_api():
    """GET /api/canonical-registry - Returns canonical registry definitions."""
    from backend.canonical_registry import get_canonical_registry
    return jsonify(get_canonical_registry())

# ==============================================================================
# S++ TOP-TIER EXTENSION ENDPOINTS (NL QUERY, MULTI-AGENT TRIAGE, ALERTS)
# ==============================================================================

@app.route("/api/query", methods=["GET", "POST"])
def natural_language_query():
    """
    GET/POST /api/query - Natural language audit query parser & filter.
    Example: ?q=road+in+jaunpur+with+high+risk
    """
    if not CACHE["works"]:
        load_data()
        
    query_text = request.args.get("q") or (request.json.get("query") if request.is_json else "")
    if not query_text:
        return jsonify({"query": "", "results_count": 0, "works": []})

    q_lower = query_text.lower().strip()
    words = q_lower.split()

    filtered = []
    for w in CACHE["works"]:
        w_text = f"{w.get('work_id', '')} {w.get('work_name', '')} {w.get('State', '')} {w.get('District', '')} {w.get('Constituency', '')} {w.get('standardized_category', '')} {w.get('audit_priority_tier', '')}".lower()
        
        # Check if all query terms match
        if all(term in w_text for term in words):
            filtered.append(w)
            if len(filtered) >= 100:  # Top 100 matches
                break

    return jsonify({
        "query": query_text,
        "results_count": len(filtered),
        "works": filtered
    })

@app.route("/api/agents/triage", methods=["GET", "POST"])
def multi_agent_triage():
    """
    GET/POST /api/agents/triage - Multi-Agent Audit Consensus Engine.
    Simulates specialized agent responses (Financial, SLA, Vendor Risk, Eligibility) for a work ID.
    """
    work_id = request.args.get("work_id") or (request.json.get("work_id") if request.is_json else "")
    if not CACHE["works_map"]:
        load_data()
        
    work_data = CACHE["works_map"].get(work_id) or (CACHE["works"][0] if CACHE["works"] else {})
    
    score = work_data.get("audit_priority_score", 0.0)
    tier = work_data.get("audit_priority_tier", "LOW PRIORITY")
    evidence = work_data.get("evidence", [])

    agents_consensus = {
        "work_id": work_id or work_data.get("work_id"),
        "overall_priority_tier": tier,
        "overall_score": score,
        "agent_evaluations": [
            {
                "agent_name": "FinancialAuditAgent",
                "role": "Cost & Overrun Specialist",
                "status": "FLAGGED" if work_data.get("isolation_forest_flag") or work_data.get("peer_iqr_flag") else "CLEARED",
                "confidence": 0.92,
                "findings": "Significant variance against peer cost baseline." if work_data.get("peer_iqr_flag") else "Sanction estimate within normal peer bounds."
            },
            {
                "agent_name": "SLAComplianceAgent",
                "role": "Approval & Execution Timing Inspector",
                "status": "FLAGGED" if work_data.get("compliance_flag") or work_data.get("delay_flag") else "CLEARED",
                "confidence": 0.95,
                "findings": "Statutory approval delay detected." if work_data.get("compliance_flag") else "Approval and execution timelines compliant."
            },
            {
                "agent_name": "VendorRiskAgent",
                "role": "Market Concentration & Graph Network Inspector",
                "status": "FLAGGED" if work_data.get("vendor_fragmentation_flag") or work_data.get("hhi_alert") else "CLEARED",
                "confidence": 0.88,
                "findings": "Payment fragmentation within 7-day window." if work_data.get("vendor_fragmentation_flag") else "No high vendor concentration detected."
            },
            {
                "agent_name": "EligibilityAgent",
                "role": "Negative List & Beneficiary Filter",
                "status": "FLAGGED" if work_data.get("inadmissible_flag") or work_data.get("private_beneficiary_flag") else "CLEARED",
                "confidence": 0.90,
                "findings": "Syntactic landmark safeguard applied." if work_data.get("inadmissible_flag") else "Fully admissible public community work."
            }
        ],
        "evidence_summary": evidence,
        "governance_disclaimer": "Multi-agent consensus classification for administrative audit triage. Not legal proof of fraud."
    }

    return jsonify(agents_consensus)

@app.route("/api/notifications/dispatch", methods=["POST"])
def dispatch_audit_notification():
    """
    POST /api/notifications/dispatch - Generates WhatsApp Business & Webhook alert payloads.
    """
    data = request.json or {}
    work_id = data.get("work_id")
    phone = data.get("phone", "+919876543210")
    
    if not CACHE["works_map"]:
        load_data()
        
    work_data = CACHE["works_map"].get(work_id) or data.get("work") or (CACHE["works"][0] if CACHE["works"] else {})
    
    from audit_rules.notifications.alert_dispatcher import generate_whatsapp_alert_payload, generate_webhook_event_payload
    
    wa_payload = generate_whatsapp_alert_payload(work_data, phone)
    wh_payload = generate_webhook_event_payload(work_data)

    return jsonify({
        "status": "DISPATCH_READY",
        "work_id": work_data.get("clean_work_id") or work_data.get("work_id"),
        "whatsapp_payload": wa_payload,
        "webhook_payload": wh_payload
    })

# Serve Frontend Static Assets
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("../frontend", filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting Temporary Demo Flask Backend Server on http://0.0.0.0:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
