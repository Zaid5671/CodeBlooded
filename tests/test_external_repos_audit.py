import os
import json
import pytest
import pandas as pd
import numpy as np

from feature_engineering.nlp_text_processor import (
    clean_nlp_text,
    extract_nlp_keywords,
    extract_entity_mentions,
    compute_nlp_jaccard_similarity
)
from research.benchmark.diagnostics.scratch_ml_components import ScratchIsolationForest, compare_scratch_vs_sklearn
from ml.model_4_forecasting.qlib_series_forecaster import compute_qlib_alpha_factors, run_qlib_benchmark_analysis
from ml.model_visualizer_exporter import export_netron_model_graph

def test_funnlp_execution_path():
    """Verify funNLP text processor cleans text and extracts entity mentions."""
    text = "Construction of Gram Panchayat Samudaya Bhavan at Ward No 5 near High School"
    cleaned = clean_nlp_text(text)
    keywords = extract_nlp_keywords(text)
    mentions = extract_entity_mentions(text)
    
    assert "gram" not in keywords
    assert "panchayat" not in keywords
    assert "school" in keywords  # Semantically meaningful domain noun preserved
    assert mentions['is_educational'] is True
    assert mentions['is_community'] is True

def test_scratch_ml_diagnostic_execution():
    """Verify ML-From-Scratch diagnostic benchmark executes."""
    X = np.random.randn(100, 2)
    from sklearn.ensemble import IsolationForest
    sk_model = IsolationForest(n_estimators=10, random_state=42).fit(X)
    res = compare_scratch_vs_sklearn(X, sk_model)
    
    assert res['role'] == 'RESEARCH_BENCHMARK_DIAGNOSTIC'
    assert 'score_correlation' in res

def test_qlib_benchmark_factor_execution():
    """Verify Qlib quantitative factor analysis executes."""
    s = pd.Series([100.0, 150.0, 200.0, 180.0, 220.0], index=pd.date_range("2025-01-01", periods=5, freq="MS").strftime("%Y-%m"))
    res = run_qlib_benchmark_analysis(s)
    
    assert res['role'] == 'OPTIONAL_RESEARCH_BENCHMARK_FACTOR_GENERATION'
    assert 'momentum' in res['alpha_factors']

def test_netron_export_execution(tmp_path):
    """Verify Netron graph exporter generates architectural schema without altering predictions."""
    out_file = tmp_path / "test_netron_graph.json"
    res = export_netron_model_graph(str(out_file))
    
    assert os.path.exists(out_file)
    assert res['affects_model_predictions'] is False
