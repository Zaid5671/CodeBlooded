// Frontend JavaScript for Temporary Demo Dashboard

const API_BASE = ""; // relative paths for Flask API

let state = {
    page: 1,
    limit: 15,
    risk: "HIGH",
    selectedState: "ALL",
    search: "",
    sortBy: "score",
    totalPages: 1,
    works: []
};

document.addEventListener("DOMContentLoaded", () => {
    initDashboard();
});

async function initDashboard() {
    await fetchSummary();
    await fetchSignals();
    await fetchWorks();
    initCharts();
    initPlayground();
    setupEventListeners();
}

// 1. Fetch Top-Level Summary
async function fetchSummary() {
    try {
        const res = await fetch(`${API_BASE}/api/summary`);
        const data = await res.json();

        if (data.total_sanctioned_works) {
            document.getElementById("kpi-total").innerText = data.total_sanctioned_works.toLocaleString();
            document.getElementById("kpi-high").innerText = data.risk_breakdown.HIGH.toLocaleString();
            document.getElementById("kpi-medium").innerText = data.risk_breakdown.MEDIUM.toLocaleString();
            document.getElementById("kpi-low").innerText = data.risk_breakdown.LOW.toLocaleString();
            document.getElementById("kpi-iso").innerText = data.signals.isolation_forest_flags.toLocaleString();
            document.getElementById("kpi-iqr").innerText = data.signals.peer_iqr_flags.toLocaleString();
            document.getElementById("kpi-overrun").innerText = data.signals.cost_overrun_flags.toLocaleString();
            document.getElementById("kpi-jaccard").innerText = data.jaccard_overlap_iqr_vs_if.toFixed(4);
        }
    } catch (e) {
        console.error("Failed to fetch summary:", e);
    }
}

// 2. Fetch Signals & Overlap Stats
async function fetchSignals() {
    try {
        const res = await fetch(`${API_BASE}/api/signals`);
        const data = await res.json();
        renderOverlapChart(data.signal_overlap);
    } catch (e) {
        console.error("Failed to fetch signals:", e);
    }
}

// 3. Fetch Paginated Works Table Data
async function fetchWorks() {
    try {
        const tbody = document.getElementById("works-table-body");
        tbody.innerHTML = `<tr><td colspan="11" class="text-center py-4 text-secondary"><i class="fa-solid fa-spinner fa-spin me-2"></i> Loading records...</td></tr>`;

        const url = `${API_BASE}/api/works?page=${state.page}&limit=${state.limit}&risk=${encodeURIComponent(state.risk)}&state=${encodeURIComponent(state.selectedState)}&search=${encodeURIComponent(state.search)}&sort_by=${state.sortBy}`;
        const res = await fetch(url);
        const data = await res.json();

        state.works = data.data || [];
        state.totalPages = data.total_pages || 1;

        // Populate State Dropdown if empty
        const stateSelect = document.getElementById("state-filter");
        if (stateSelect.options.length <= 1 && data.available_states) {
            data.available_states.forEach(st => {
                const opt = document.createElement("option");
                opt.value = st;
                opt.innerText = st;
                stateSelect.appendChild(opt);
            });
        }

        renderWorksTable(state.works);
        updatePagination(data.total || 0, data.page || 1, data.total_pages || 1);
    } catch (e) {
        console.error("Failed to fetch works:", e);
        document.getElementById("works-table-body").innerHTML = `<tr><td colspan="11" class="text-center py-4 text-danger">Failed to load data. Is backend running?</td></tr>`;
    }
}

// Render Works Table Rows
function renderWorksTable(works) {
    const tbody = document.getElementById("works-table-body");

    if (!works || works.length === 0) {
        tbody.innerHTML = `<tr><td colspan="11" class="text-center py-4 text-secondary">No matching project records found.</td></tr>`;
        return;
    }

    tbody.innerHTML = works.map((w, idx) => {
        const risk = w.consensus.risk_level;
        let badgeClass = "badge-low";
        if (risk === "HIGH") badgeClass = "badge-high";
        if (risk === "MEDIUM") badgeClass = "badge-medium";
        if (risk === "DATA_QUALITY_REVIEW") badgeClass = "badge-dq";

        const sanc = w.sanctioned_amount ? `₹${w.sanctioned_amount.toLocaleString("en-IN", {maximumFractionDigits:2})}` : "N/A";
        const med = w.peer_statistics && w.peer_statistics.median ? `₹${w.peer_statistics.median.toLocaleString("en-IN", {maximumFractionDigits:2})}` : "N/A";
        const robDev = w.signals.peer_iqr.robust_deviation ? `${w.signals.peer_iqr.robust_deviation.toFixed(1)} IQR` : "N/A";
        const mlScore = w.signals.isolation_forest.anomaly_score ? w.signals.isolation_forest.anomaly_score.toFixed(4) : "N/A";
        const actExp = w.actual_expenditure ? `₹${w.actual_expenditure.toLocaleString("en-IN", {maximumFractionDigits:2})}` : `<span class="text-secondary">NO_EXPENDITURE</span>`;
        const workDesc = (w.work_description || w.work_id).substring(0, 50) + "...";

        return `
            <tr>
                <td><span class="badge ${badgeClass}">${risk}</span></td>
                <td><code>${w.work_id}</code></td>
                <td><b>${w.mp_name || 'N/A'}</b></td>
                <td>${w.state}<br><small class="text-slate-400">${w.constituency || ''}</small></td>
                <td title="${w.work_description}">${workDesc}</td>
                <td class="fw-bold text-light">${sanc}</td>
                <td class="text-info">${med}</td>
                <td class="text-warning">${robDev}</td>
                <td class="fw-bold text-purple">${mlScore}</td>
                <td>${actExp}</td>
                <td>
                    <button class="btn btn-outline-indigo btn-sm" onclick="openWorkModal('${w.work_id}')">
                        <i class="fa-solid fa-eye"></i> Details
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

// Update Pagination Controls
function updatePagination(total, page, totalPages) {
    document.getElementById("page-info").innerText = `Showing ${Math.min((page-1)*state.limit + 1, total)}-${Math.min(page*state.limit, total)} of ${total.toLocaleString()} works`;
    document.getElementById("btn-prev").disabled = (page <= 1);
    document.getElementById("btn-next").disabled = (page >= totalPages);
}

// Open Project Detail Modal
function openWorkModal(workId) {
    const work = state.works.find(w => w.work_id === workId);
    if (!work) return;

    document.getElementById("m-work-id").innerText = work.work_id;
    document.getElementById("m-mp-name").innerText = work.mp_name || "N/A";
    document.getElementById("m-state").innerText = work.state || "N/A";
    document.getElementById("m-constituency").innerText = work.constituency || "N/A";
    document.getElementById("m-work-desc").innerText = work.work_description || "N/A";
    
    document.getElementById("m-sanction-amt").innerText = work.sanctioned_amount ? `₹${work.sanctioned_amount.toLocaleString("en-IN", {maximumFractionDigits:2})}` : "N/A";
    document.getElementById("m-actual-exp").innerText = work.actual_expenditure ? `₹${work.actual_expenditure.toLocaleString("en-IN", {maximumFractionDigits:2})}` : "NO_EXPENDITURE_RECORD_YET";
    document.getElementById("m-peer-median").innerText = work.peer_statistics && work.peer_statistics.median ? `₹${work.peer_statistics.median.toLocaleString("en-IN", {maximumFractionDigits:2})}` : "N/A";
    document.getElementById("m-robust-dev").innerText = work.signals.peer_iqr.robust_deviation ? `${work.signals.peer_iqr.robust_deviation.toFixed(2)} IQRs` : "N/A";
    document.getElementById("m-days").innerText = work.recommendation_to_sanction_days !== null ? `${work.recommendation_to_sanction_days} days` : "N/A";
    document.getElementById("m-ml-score").innerText = work.signals.isolation_forest.anomaly_score ? work.signals.isolation_forest.anomaly_score.toFixed(4) : "N/A";

    const riskBadge = document.getElementById("m-risk-badge");
    const risk = work.consensus.risk_level;
    riskBadge.innerText = `${risk} (${work.consensus.positive_signal_count} Sigs)`;
    riskBadge.className = "badge fs-6 " + (risk === "HIGH" ? "bg-danger" : risk === "MEDIUM" ? "bg-warning text-dark" : "bg-success");

    const evList = document.getElementById("m-evidence-list");
    evList.innerHTML = "<ul class='mb-0 ps-3'>" + (work.evidence || []).map(e => `<li class='mb-1'>${e}</li>`).join("") + "</ul>";

    const modal = new bootstrap.Modal(document.getElementById("projectModal"));
    modal.show();
}

// 4. Setup Interactive Event Listeners
function setupEventListeners() {
    document.getElementById("btn-search").addEventListener("click", () => {
        state.search = document.getElementById("search-input").value;
        state.risk = document.getElementById("risk-filter").value;
        state.selectedState = document.getElementById("state-filter").value;
        state.sortBy = document.getElementById("sort-filter").value;
        state.page = 1;
        fetchWorks();
    });

    document.getElementById("btn-prev").addEventListener("click", () => {
        if (state.page > 1) {
            state.page--;
            fetchWorks();
        }
    });

    document.getElementById("btn-next").addEventListener("click", () => {
        if (state.page < state.totalPages) {
            state.page++;
            fetchWorks();
        }
    });
}

// 5. Initialize Visualizations via Plotly.js
function initCharts() {
    // Risk Distribution Pie Chart
    Plotly.newPlot("chart-risk", [{
        values: [2849, 1924, 74443, 4],
        labels: ["HIGH Risk", "MEDIUM Risk", "LOW Normal", "Data Quality"],
        type: "pie",
        marker: { colors: ["#ef4444", "#f59e0b", "#10b981", "#3b82f6"] }
    }], {
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: { color: "#cbd5e1" },
        margin: { t: 10, b: 10, l: 10, r: 10 }
    });

    // 80/20 Train vs Test Bar Chart
    Plotly.newPlot("chart-traintest", [{
        x: ["80% Training Set (63,372)", "20% Test Set (15,844)"],
        y: [4.99, 4.88],
        type: "bar",
        marker: { color: ["#6366f1", "#10b981"] }
    }], {
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: { color: "#cbd5e1" },
        yaxis: { title: "Anomaly Rate (%)", range: [0, 8] },
        margin: { t: 20, b: 40, l: 40, r: 20 }
    });

    // 5-Seed Anomaly Rate Stability
    Plotly.newPlot("chart-seeds", [{
        x: ["Seed 42", "Seed 100", "Seed 200", "Seed 300", "Seed 400"],
        y: [4.88, 5.15, 5.18, 5.09, 4.87],
        type: "scatter",
        mode: "lines+markers",
        marker: { size: 10, color: "#f59e0b" },
        line: { color: "#f59e0b", width: 3 }
    }], {
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: { color: "#cbd5e1" },
        yaxis: { title: "Test Anomaly Rate (%)", range: [4.0, 6.0] },
        margin: { t: 20, b: 40, l: 40, r: 20 }
    });
}

function renderOverlapChart(overlapData) {
    const data = overlapData || { both_signals: 2849, peer_iqr_only: 812, isolation_forest_only: 1112 };
    Plotly.newPlot("chart-overlap", [{
        x: ["Both Signals (HIGH)", "Peer IQR Only (MED)", "Isolation Forest Only (MED)"],
        y: [data.both_signals, data.peer_iqr_only, data.isolation_forest_only],
        type: "bar",
        marker: { color: ["#ef4444", "#f59e0b", "#9333ea"] }
    }], {
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: { color: "#cbd5e1" },
        margin: { t: 20, b: 40, l: 40, r: 20 }
    });
}

// 6. Model Playground Event Handlers
function initPlayground() {
    const sancSlider = document.getElementById("pg-sanc-slider");
    const medSlider = document.getElementById("pg-med-slider");
    const daysSlider = document.getElementById("pg-days-slider");

    function updatePlayground() {
        const sanc = parseFloat(sancSlider.value);
        const med = parseFloat(medSlider.value);
        const days = parseInt(daysSlider.value);

        document.getElementById("pg-sanc-val").innerText = `₹${sanc.toLocaleString("en-IN")}`;
        document.getElementById("pg-med-val").innerText = `₹${med.toLocaleString("en-IN")}`;
        document.getElementById("pg-days-val").innerText = `${days} days`;

        // Robust Dev simulation (IQR ~ ₹500,000)
        const iqr = 500000.0;
        const robDev = (sanc - med) / iqr;
        const iqrFlag = (robDev > 3.0);

        // ML Score simulation
        const ratio = (sanc - med) / med;
        let isoScore = 0.10 + (ratio * 0.02) + (robDev * 0.01) + (days * 0.001);
        isoScore = Math.min(0.9999, Math.max(0.01, isoScore));
        const isoFlag = (isoScore > 0.45);

        const sigCount = (iqrFlag ? 1 : 0) + (isoFlag ? 1 : 0);
        let risk = "LOW";
        if (sigCount >= 2) risk = "HIGH";
        else if (sigCount === 1) risk = "MEDIUM";

        document.getElementById("pg-iqr-status").innerHTML = iqrFlag ? 
            `<span class="badge bg-danger fs-6">FLAGGED (${robDev.toFixed(2)} IQRs)</span>` : 
            `<span class="badge bg-success fs-6">NORMAL (${robDev.toFixed(2)} IQRs)</span>`;

        document.getElementById("pg-iso-status").innerHTML = isoFlag ? 
            `<span class="badge bg-purple fs-6">${isoScore.toFixed(4)} (ANOMALOUS)</span>` : 
            `<span class="badge bg-success fs-6">${isoScore.toFixed(4)} (NORMAL)</span>`;

        document.getElementById("pg-risk-status").innerText = risk === "HIGH" ? `🚨 HIGH (${sigCount} Signals)` : risk === "MEDIUM" ? `⚠️ MEDIUM (${sigCount} Signal)` : `✅ LOW (${sigCount} Signals)`;
        document.getElementById("pg-risk-status").className = "fs-4 fw-bold " + (risk === "HIGH" ? "text-danger" : risk === "MEDIUM" ? "text-warning" : "text-success");
    }

    sancSlider.addEventListener("input", updatePlayground);
    medSlider.addEventListener("input", updatePlayground);
    daysSlider.addEventListener("input", updatePlayground);

    document.getElementById("pg-project-select").addEventListener("change", (e) => {
        const val = e.target.value;
        if (val === "WS/MP492/2024-2025/134984") {
            sancSlider.value = 37908000;
            medSlider.value = 232198;
            daysSlider.value = 153;
        } else if (val === "WS/MP345/2024-2025/134123") {
            sancSlider.value = 4740188;
            medSlider.value = 255470;
            daysSlider.value = 85;
        } else if (val === "WS/MP620/2025-2026/133191") {
            sancSlider.value = 1500000;
            medSlider.value = 500000;
            daysSlider.value = 45;
        }
        updatePlayground();
    });
}
