"""
SIH26102 — QLIB QUANTITATIVE FACTOR GENERATOR (Benchmark / Research Factor Tooling)
=====================================================================================
Quantitative time-series factor analyzer inspired by Microsoft Qlib.
Generates research benchmark factors (Momentum, Volatility Ratio, Trend Velocity)
to evaluate auxiliary time-series signals alongside the production M4 forecast.

Role: OPTIONAL RESEARCH / BENCHMARK FACTOR GENERATION
Canonical Production M4 Algorithm: Recursive 3-Month Rolling Average Baseline (6-Month Horizon)
Interval Designation: Empirical 95% Expected Range
"""

import numpy as np
import pandas as pd

def compute_qlib_alpha_factors(monthly_series):
    """
    Computes quantitative research alpha factors (Momentum, Volatility Ratio, Trend Velocity)
    for monthly expenditure utilization series.
    Classification: Auxiliary Research Benchmark Signals.
    """
    vals = monthly_series.values
    if len(vals) < 3:
        return {'momentum': 0.0, 'volatility_ratio': 1.0, 'trend_velocity': 0.0}
        
    ema3 = pd.Series(vals).ewm(span=3).mean().values
    mom = (vals[-1] - vals[0]) / max(vals[0], 1.0)
    vol_ratio = float(np.std(vals[-3:])) / float(np.std(vals) + 1e-8)
    velocity = float(ema3[-1] - ema3[-2]) if len(ema3) >= 2 else 0.0
    
    return {
        'momentum': round(float(mom), 4),
        'volatility_ratio': round(float(vol_ratio), 4),
        'trend_velocity': round(float(velocity), 2)
    }

def run_qlib_benchmark_analysis(monthly_series):
    """
    Evaluates quantitative research alpha factors for time-series diagnostics.
    """
    factors = compute_qlib_alpha_factors(monthly_series)
    return {
        'role': 'OPTIONAL_RESEARCH_BENCHMARK_FACTOR_GENERATION',
        'alpha_factors': factors,
        'canonical_m4_model': 'Recursive 3-Month Rolling Average Baseline with Empirical 95% Expected Range'
    }
