# External Repository Integration Audit & Verification Report
**SIH 2026 | Problem Statement: SIH26102**  
**AI-Powered MPLADS Audit Intelligence Platform — Team CodeBlooded**  

---

## 1. Code-Level External Repository Audit Table

| Repository | Actual Code Used | Production Model | Affects Final Prediction/Score | Role | Evidence | Verdict |
|---|---|---|---|---|---|---|
| **vendor/funNLP** | `GLOBAL_STOPWORDS`, `clean_nlp_text()`, `extract_nlp_keywords()`, `extract_entity_mentions()` | **M2** & **M3** | **YES (Preprocessing & Feature Selection)** | **Production Preprocessing & Entity Screening** | Administrative noise stopwords (`gp`, `tq`, `ward`, `no`) filtered before TF-IDF vectorization in M2. Semantically meaningful domain terms (`road`, `school`, `hospital`, `hall`, `construction`) strictly preserved. Landmark mentions extracted for M3 review. | **PASS** |
| **vendor/ML-From-Scratch** | `ScratchIsolationForest`, `compare_scratch_vs_sklearn()` | **M1 Diagnostic** | **NO (Canonical Model is `sklearn.ensemble.IsolationForest`)** | **Research Benchmark & Diagnostic Tooling** | `ScratchIsolationForest` executes as a pure NumPy baseline model in `research/benchmark/diagnostics/scratch_ml_components.py`. Canonical production M1 relies strictly on Scikit-Learn IsolationForest (`n_estimators=300`, `contamination=0.05`). | **PASS (Diagnostic Classification)** |
| **vendor/qlib** | `compute_qlib_alpha_factors()`, `run_qlib_benchmark_analysis()` | **M4 Benchmark** | **NO (Canonical Model is 3-Month Rolling Average)** | **Optional Research / Benchmark Factor Generation** | Qlib quantitative momentum & trend velocity factors (`qlib_alpha_momentum`, `qlib_trend_velocity`) generated in `ml/model_4_forecasting/qlib_series_forecaster.py` as research signals. Canonical production M4 forecast is driven by 3-Month Rolling Average with Empirical 95% Expected Range. | **PASS (Benchmark Factor Classification)** |
| **vendor/netron** | `export_netron_model_graph()` | **None (Visualization Tooling)** | **NO (0.00% impact on predictions/scores)** | **Supporting Model Visualization / Architecture Inspection** | Generates Netron-compatible DAG graph schema at `output/model_architecture_graph.json` mapping M1–M5 node contracts. Zero impact on numerical ML calculations or risk scores. | **PASS (Visualization Classification)** |

---

## 2. Detailed Findings by Repository

### 2.1 vendor/funNLP
- **Executed Code Path**: `feature_engineering/nlp_text_processor.py` dynamically loads stop-words from `vendor/funNLP/data/停用词/`.
- **Text Normalization Timing**: Executed **BEFORE** TF-IDF vectorization in M2.
- **Token Removal Fencing**: Semantically meaningful work-description terms (`construction`, `repair`, `road`, `building`, `school`, `hospital`, `hall`, `water`, `bridge`, `drainage`, `playground`) are **STRICTLY PRESERVED**. Only genuine structural noise (`no`, `number`, `gp`, `tq`, `dist`, `district`, `block`, `ward`, `pry`, `sec`) is filtered.
- **M3 Entity Extraction**: `extract_entity_mentions()` classifies entity types. Landmark mention in text is explicitly fenced from funded object.
- **Accuracy Claim Classification**: Classified under *"candidate-generation improvement hypothesis"* (unlabeled diagnostic standard).

### 2.2 vendor/ML-From-Scratch
- **Executed Code Path**: `research/benchmark/diagnostics/scratch_ml_components.py`.
- **Production Status**: Serves as a diagnostic benchmark.
- **Canonical Model Fencing**: Canonical production M1 is `sklearn.ensemble.IsolationForest` (`n_estimators=300`, `contamination=0.05`, `random_state=42`). Zero synthetic hybrid scores are introduced into production M1.

### 2.3 vendor/qlib
- **Executed Code Path**: `ml/model_4_forecasting/qlib_series_forecaster.py`.
- **Production Status**: Serves as optional research/benchmark factor generation.
- **Canonical Model Fencing**: Canonical production M4 remains the recursive 3-month rolling-average baseline with 6-month horizon and Empirical 95% Expected Range ($[\mu - 1.96\sigma, \mu + 1.96\sigma]$).

### 2.4 vendor/netron
- **Executed Code Path**: `ml/model_visualizer_exporter.py`.
- **Production Status**: Supporting Model Visualization & Architecture Inspection.
- **Prediction Impact**: 0.00% impact on M1–M5 scores.

---

## 3. Data Count Reconciliation

- **Sanctioned Works Count (79,220 vs 79,221)**:
  - **79,221**: Total raw CSV line count including 1 header line.
  - **79,220**: Total non-header master sanctioned work entity records.
  - **Status**: **RESOLVED** (Reconciled as 1 CSV header line difference).

- **Expenditure Units (84,172 vs 56,604)**:
  - **84,172**: Total raw expenditure transaction rows across all vouchers.
  - **56,604**: Unique sanctioned works having at least one matched expenditure transaction.
  - **Status**: **RESOLVED** (Explicitly written as: *"84,172 expenditure transactions; 56,604 sanctioned works have at least one matched expenditure transaction"*).
