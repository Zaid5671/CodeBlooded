# SIH26102 — Final Production ML Model Contract Specifications

This contract defines the explicit mathematical, architectural, input/output, leakage control, metric, and UI representation specifications for all **5 Core ML Models (M1–M5)** in the MPLADS Audit Intelligence Platform (`SIH26102`).

---

## 1. MODEL M1 — Anomalous Cost Outlier Detection

- **NAME**: Model M1 (Cost Estimate Anomaly Model)
- **PROBLEM**: Detect works where the sanctioned outlay deviates significantly from state and category peer-group distributions.
- **INPUT**: `sanctioned_amount`, `state`, `standardized_category`, `constituency`
- **OUTPUT**: `m1_cost_anomaly_flag` (Boolean: 0/1), `m1_risk_score` (Float: [0, 100])
- **TYPE**: Unsupervised Anomaly Detection
- **TRAINING DATA**: Chronological 80% partition of master sanctioned works (63,375 records)
- **EVALUATION DATA**: Chronological 20% holdout partition (15,844 records)
- **FEATURES**: `log_sanction_amount`, `peer_median_deviation`, `peer_z_score`, `peer_mad_ratio`
- **LEAKAGE CONTROLS**:
  1. Fit peer statistics (median, MAD) **strictly on training partition**.
  2. Fenced sanction-stage features only — zero post-sanction expenditure or payment fields used.
- **METRIC**: Test Anomaly Rate (**5.02%** vs 5.00% target contamination)
- **BASELINE**: 1D IQR Outlier Cutoff
- **GROUND TRUTH**: `NOT ESTIMABLE — NO INDEPENDENT GROUND-TRUTH LABELS` (Unsupervised model)
- **LIMITATIONS**: High outlay does not automatically equal financial misrepresentation; requires ground physical verification.
- **UI REPRESENTATION**: Highlighted in Overview KPIs, Works Explorer ("M1 Cost Outlier" badge), and Work Investigation Drawer.

---

## 2. MODEL M2 — Duplicate Work Semantic Linkage

- **NAME**: Model M2 (Duplicate Work Linkage Model)
- **PROBLEM**: Identify potential duplicate or recurrent work recommendations within geographic boundaries.
- **INPUT**: `work_description`, `state`, `district`, `constituency`, `sanctioned_amount`
- **OUTPUT**: `candidate_pairs` (List of tuples), `cosine_similarity_score` (Float: [0.0, 1.0])
- **TYPE**: Record Linkage & Candidate Pair Generation
- **TRAINING DATA**: Master Sanctioned Works Corpus
- **EVALUATION DATA**: Full Candidate Blocking Partition
- **FEATURES**: TF-IDF n-gram vectors, Sentence-Transformer embeddings, spatial boundary equivalence
- **LEAKAGE CONTROLS**:
  1. Candidate blocking strictly within `State + District` to prevent cross-partition contamination.
  2. Canonical key ordering `pair_key = tuple(sorted([id1, id2]))` prevents duplicate pair reporting.
- **METRIC**: Retained Candidate Pair Count (**5,000 Scored Pairs** at $>90\%$ cosine parity; 0 self-pairs; 0 duplicate canonical pair keys)
- **BASELINE**: Exact string match ($O(N^2)$ brute force)
- **GROUND TRUTH**: `NOT ESTIMABLE — NO INDEPENDENT GROUND-TRUTH LABELS`
- **LIMITATIONS**: Semantic similarity indicates candidate duplication; physical ground seal verification required.
- **UI REPRESENTATION**: Duplicate Works Explorer view (`#view-duplicates`) and Side-by-Side Duplicate Comparison Modal (`#duplicate-modal`).

---

## 3. MODEL M3 — Expenditure & Payment Behavioral Screening

- **NAME**: Model M3 (Expenditure & Payment Behavioral Screening)
- **PROBLEM**: Screen for unusual payment disbursement velocity and transaction structuring patterns.
- **INPUT**: `payment_records` (List of transactions with `disbursed_amount`, `payment_date`, `vendor_name`)
- **OUTPUT**: `m3_spending_anomaly_flag` (Boolean: 0/1), `structuring_signal_score` (Float: [0, 100])
- **TYPE**: Transaction-Grain Behavioral Rule & Threshold Screening
- **TRAINING DATA**: Expenditure Transaction Datasets (138,575 records in LS17; 84,172 records in LS18)
- **EVALUATION DATA**: Full Transaction Corpus
- **FEATURES**: `num_payments`, `total_spent`, `max_payment`, `payment_spacing_days`
- **LEAKAGE CONTROLS**: `NaN` missing values handled distinctly from `0.0` spending; zero post-dated transactions processed.
- **METRIC**: Structuring Flag Count & Risk Distribution (`num_payments >= 5`, `total_spent > ₹500k`, `max_payment < ₹200k`)
- **BASELINE**: Uniform payment velocity assumption
- **GROUND TRUTH**: `NOT ESTIMABLE — NO INDEPENDENT GROUND-TRUTH LABELS`
- **LIMITATIONS**: Analytical screening parameter; serves as administrative decision support, not legal proof.
- **UI REPRESENTATION**: Expenditure Intelligence view (`#view-expenditure`) and Work Investigation Drawer signals.

---

## 4. MODEL M4 — Expenditure Forecasting Model

- **NAME**: Model M4 (Expenditure Forecasting Model)
- **PROBLEM**: Predict future monthly expenditure and fund utilization over a 6-month horizon.
- **INPUT**: Monthly aggregated historical outlay time-series (`STATE × CALENDAR MONTH`)
- **OUTPUT**: `projected_monthly_outlay` (Float ₹ Cr), `lower_bound_95`, `upper_bound_95`
- **TYPE**: Chronological Time-Series Forecasting
- **PRODUCTION HORIZON**: 6 Months (`FORECAST_HORIZON_MONTHS = 6`)
- **EVALUATION DESIGN**: Recursive multi-step forecast evaluation over the held-out period (19 train months: 2024-07 to 2026-01; 8 test months: 2026-02 to 2026-09)
- **FEATURES**: Recursive 3-Month Rolling Average Outlay with Empirical 95% Expected Range
- **LEAKAGE CONTROLS**: Evaluated strictly on chronological holdout set; zero future expenditure included in rolling window.
- **METRIC**: **MAE = ₹34,493,984.47 (₹3.45 Cr)**, **RMSE = ₹63,253,503.79 (₹6.33 Cr)**, **WAPE = 470.32%** (State-month panel; WAPE expands in state-month cells where actual expenditure is small or zero relative to prediction error), **sMAPE = 54.21%**
- **BASELINE**: Naïve Previous Month Baseline (MAE = ₹37,114,452.69)
- **MAE IMPROVEMENT VS NAÏVE BASELINE**: **+7.06%**
- **GROUND TRUTH**: Actual monthly historical disbursement records in holdout window
- **LIMITATIONS**: Evaluated at state macro level; subject to fiscal quarter policy shifts.
- **UI REPRESENTATION**: Expenditure Outlook view (`#view-forecast`) featuring interactive Plotly 6-month projection chart with 95% confidence bands.

---

## 5. MODEL M5 — Unified Audit Priority Model

- **NAME**: Model M5 (Unified Audit Priority Scoring Model)
- **PROBLEM**: Combine independent risk signals into a single composite audit priority score to optimize field audit allocation.
- **INPUT**: Risk signals from M1 (Cost: 0.30), Delay (Speed: 0.25), Compliance (0.25), Vendor Concentration (0.10), Eligibility (0.10)
- **OUTPUT**: `priority_score` (Float: [0, 100]), `priority_tier` (`CRITICAL`, `STANDARD`, `LOW`)
- **TYPE**: Multi-Signal Composite Triage & Ranking
- **TRAINING DATA**: Full Master Works Corpus
- **EVALUATION DATA**: Full Master Works Corpus
- **FEATURES**: Normalized 5-signal risk vector
- **LEAKAGE CONTROLS**: Weights sum strictly to `1.00`; supporting-only invariant verified (secondary signals alone cannot trigger `CRITICAL`).
- **METRIC**: Tier Distribution (**1,635 Critical Works**, 58,176 Standard, 19,409 Low)
- **BASELINE**: Equal-weighted linear sum
- **GROUND TRUTH**: `NOT ESTIMABLE — NO INDEPENDENT GROUND-TRUTH LABELS`
- **LIMITATIONS**: Prioritization ranking tool; does not compute criminal probability.
- **UI REPRESENTATION**: Audit Priority Queue (`#view-priority`), Overview KPI counter, and Alert Center.
