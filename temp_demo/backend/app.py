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
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "output"))

# Data Cache
CACHE = {
    "summary": None,
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

@app.route("/api/summary", methods=["GET"])
def get_summary():
    """GET /api/summary - Returns top-level KPI metrics."""
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
    Query params: page, limit, risk, state, search, sort_by, order
    """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    risk_filter = request.args.get("risk", "").strip().upper()
    state_filter = request.args.get("state", "").strip()
    search_query = request.args.get("search", "").strip().lower()
    sort_by = request.args.get("sort_by", "score").strip()
    order = request.args.get("order", "desc").strip().lower()

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
