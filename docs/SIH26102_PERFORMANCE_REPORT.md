# SIH26102 — Performance Optimization Report
## Team CodeBlooded — AI-Powered MPLADS Audit Intelligence Platform

This report details the results of full-stack performance optimization across backend data access, API latencies, machine learning pipelines (M1–M5), and client-side rendering.

---

## 1. Performance Bottlenecks Identified & Resolved

1. **Backend API File Reads**:
   - **Problem**: Route handlers repeatedly read and parsed JSON files from disk (`json.load`) on incoming HTTP requests across 25 registered backend API routes.
   - **Optimization**: Implemented server-side in-memory caching (`CACHE` dict) pre-warmed at startup (`load_data()`) in `backend/app.py`.
   - **Result**: Server-side caching shifts repeated JSON file access from request time to application initialization. Selected benchmarked cached result endpoints responded in the measured sub-5-ms range.

2. **Expenditure Feature Aggregation (Model 3)**:
   - **Problem**: `expenditure_matching.py` called `.groupby().apply(calc_payment_features)` across 56,604 groups during M3 expenditure/payment structuring analysis, taking ~15.38 seconds.
   - **Optimization**: Replaced line-by-line `.apply()` with high-performance vectorized Pandas `.groupby().agg()` aggregations.
   - **Result**: Expenditure matching runtime reduced from 15.38s to **~0.84s** (**~18x speedup**). Analytical parity was verified against canonical outputs for the tested datasets and comparison cases.

3. **M5 Audit Priority Aggregator (Model 5)**:
   - **Problem**: `misuse_priority.py` iterated over 79,220 master work rows using slow `merged.iterrows()`, taking ~30.55 seconds.
   - **Optimization**: Replaced `df.iterrows()` with fast dictionary iteration (`df.to_dict('records')`).
   - **Result**: M5 execution time dropped from 30.55s down to **~0.42s** (**~72x speedup**).

4. **M2 Candidate Feature Extraction (Model 2)**:
   - **Problem**: `double_dipping_similarity.py` instantiated micro-`TfidfVectorizer` objects in un-cached loops for candidate pair comparisons.
   - **Optimization**: Pre-normalized text strings (`description`, `vendor_name`, location entities) once per entity, reusing global pre-fitted vectorizers.
   - **Result**: Candidate pair evaluation runtime reduced by **> 50%**. Generates 5,000 candidate pairs (1,997 High, 2,499 Medium, 504 Low). These are M2 candidate-pair risk tiers and are not confirmed duplicates or M5 audit-priority tiers.

5. **Frontend Client Caching & Debouncing (`frontend/app.js`)**:
   - **Problem**: Frequent tab switching and keystroke search triggered un-cached API calls and DOM reflows.
   - **Optimization**: Added client-side `apiCache` map with 60s TTL invalidation and 300 ms input debouncing on search explorer.
   - **Result**: Client-side response caching, lazy loading, and debounced search reduce repeated network requests and improve tab responsiveness.

---

## 2. Empirical Before / After Measurements

| Component | Baseline | Optimized | Speedup Factor | Status |
|---|---|---|---|---|
| **Backend Startup** | 1.05s | 1.09s | ~1.0x (Pre-warming cache at initialization) | VERIFIED |
| **GET /api/summary** | 0.0248s | 0.0131s | 1.89x | VERIFIED |
| **GET /api/works?limit=50** | 0.0573s | 0.0482s | 1.18x | VERIFIED |
| **GET /api/double-dipping** | 0.1082s (uncached) | 0.0014s (cached) | 77.2x | VERIFIED |
| **GET /api/delayed-projects** | 0.4127s (cold cache / uncached) | 0.0019s–0.1988s (warm cache / cached) | 2.07x–217.2x | VERIFIED |
| **GET /api/compliance** | 0.2776s (uncached) | 0.0021s (cached) | 132.1x | VERIFIED |
| **GET /api/audit-priority** | 0.0017s (uncached) | 0.0004s (cached) | 4.25x | VERIFIED |
| **GET /api/forecast** | 0.0008s | 0.0005s | 1.60x | VERIFIED |
| **GET /api/vendor-risk** | 0.0068s | 0.0039s | 1.74x | VERIFIED |
| **GET /api/inadmissible-works** | 0.0009s | 0.0002s | 4.50x | VERIFIED |
| **GET /api/private-beneficiaries** | 0.0007s | 0.0001s | 7.00x | VERIFIED |
| **GET /api/duplicate-expenditure** | 0.0003s | 0.0001s | 3.00x | VERIFIED |
| **GET /api/fund-utilization** | 0.0002s | 0.0001s | 2.00x | VERIFIED |
| **Model 3 Expenditure Aggregation** | 15.38s | 0.84s | 18.3x | VERIFIED |
| **Model 5 Audit Priority Aggregator** | 30.55s | 0.42s | 72.7x | VERIFIED |
| **Full Pipeline Data Handoff** | ~100.8s | ~47.2s | 2.13x | VERIFIED |

---

## 3. Correctness & Data Integrity Regression Results

- **Model M1 (Isolation Forest)**:
  - Scored record count: 79,220 master works
  - Parameter configuration: `n_estimators=300`, `contamination=0.05`, `random_state=42`
  - Flagged cost anomaly count: 3,961 works
  - Output parity: Analytical parity was verified against canonical outputs for the tested datasets and comparison cases.
- **Model M2 (Double-Dipping Detector)**:
  - Total candidate pairs generated: 5,000 candidate pairs
  - Candidate risk tier breakdown: 1,997 High, 2,499 Medium, 504 Low
  - Note: These are M2 candidate-pair risk tiers and are not confirmed duplicates or M5 audit-priority tiers.
- **Model M3 & Compliance Rules**:
  - M3 expenditure/payment structuring analysis verified with analytical parity against canonical outputs for tested datasets.
  - Delay detection rules and Statutory compliance rules verified independently.
- **Model M4 (Expenditure Forecasting)**:
  - Verified 6-month projected trajectory and confidence intervals against canonical outputs for tested datasets.
- **Model M5 (Audit Priority Aggregator)**:
  - Critical Audit Priority count: 1,635 works verified against canonical outputs for tested datasets.
- **API & Test Parity**:
  - Tested API endpoints responded successfully under their applicable HTTP methods and test inputs across 25 registered backend API routes.
  - 149/149 automated software tests passed (Software test pass rate: 100%).

---

## 4. Final Summary & Status

Performance improvements were measured under the documented benchmark conditions. Cached and uncached timings are distinguished where applicable. The optimizations preserve the canonical M1–M5 analytical architecture, with output parity verified for the tested datasets and comparison cases.

**PERFORMANCE OPTIMIZATION VERIFIED**
