import os
import json
import pandas as pd
import numpy as np
from cost_detection.config import (
    OUTPUT_DIR,
    DATA_DIR,
    LS17_DATA_DIR,
    FORECASTING_ENABLED,
    FORECAST_HORIZON_MONTHS,
    MIN_FORECAST_OBSERVATIONS,
    RANDOM_STATE,
)
from cost_detection.preprocessing import clean_monetary_field

def recursive_rolling_mean_forecast(history_vals, horizon=6, window=3):
    """
    Canonical Recursive Rolling Mean Forecasting Engine.
    Generates multi-step forecasts by computing the rolling mean of the latest window observations
    and appending predictions recursively to the working history.
    """
    history = list(history_vals)
    predictions = []
    for step in range(horizon):
        w = history[-window:] if len(history) >= window else history
        pred = float(np.mean(w))
        predictions.append(pred)
        history.append(pred)
    return predictions

def generate_expenditure_forecast(df_master=None, horizon_months=FORECAST_HORIZON_MONTHS, data_dir=DATA_DIR):
    """
    MPLADS Expenditure Forecasting Module (M4_FORECAST).
    Predictive time-series model analyzing actual monthly expenditure utilization trends
    and identifying significant deviations from expected historical baseline patterns.
    
    Returns:
        df_forecast: pd.DataFrame of forecasted monthly metrics for the horizon.
        results: dict with summary, metadata, and full forecast_records timeline.
    """
    np.random.seed(RANDOM_STATE)
    
    # 1. Load actual LS18 expenditure data
    ls18_exp_path = os.path.join(data_dir, "Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv")
    
    df_exp = None
    if os.path.exists(ls18_exp_path):
        df_exp = pd.read_csv(ls18_exp_path, low_memory=False)
        
    if df_exp is None or df_exp.empty:
        summary_empty = {
            'model_id': 'M4_FORECAST',
            'model_name': 'MPLADS Expenditure Forecasting Model',
            'model_version': '1.0.0',
            'aggregation_level': 'NATIONAL',
            'historical_start': 'N/A',
            'historical_end': 'N/A',
            'forecast_horizon': horizon_months,
            'forecasting_method': 'Forecast unavailable — insufficient historical observations',
            'observations_used': 0,
            'forecast_records': [],
            'total_expected_expenditure': 0.0,
            'total_actual_expenditure': 0.0,
            'anomaly_count': 0,
            'status': 'INSUFFICIENT_DATA',
            'limitations': 'Forecast models administrative spending utilization trends based on historical timelines. Forecast deviations represent administrative tracking alerts, not proof of fraud.'
        }
        return pd.DataFrame(), summary_empty

    amt_cols = [c for c in df_exp.columns if ('disbursed' in c.lower() or 'amount' in c.lower()) and 'date' not in c.lower()]
    amt_col = amt_cols[0] if amt_cols else df_exp.columns[-1]
    date_col = 'Expenditure Date' if 'Expenditure Date' in df_exp.columns else 'date'
    
    df_exp['clean_amt'] = clean_monetary_field(df_exp[amt_col])
    df_exp['dt'] = pd.to_datetime(df_exp[date_col], errors='coerce', dayfirst=True)
    df_valid = df_exp.dropna(subset=['dt', 'clean_amt']).copy()
    
    if len(df_valid) == 0:
        summary_empty = {
            'model_id': 'M4_FORECAST',
            'model_name': 'MPLADS Expenditure Forecasting Model',
            'model_version': '1.0.0',
            'aggregation_level': 'NATIONAL',
            'historical_start': 'N/A',
            'historical_end': 'N/A',
            'forecast_horizon': horizon_months,
            'forecasting_method': 'Forecast unavailable — insufficient historical observations',
            'observations_used': 0,
            'forecast_records': [],
            'total_expected_expenditure': 0.0,
            'total_actual_expenditure': 0.0,
            'anomaly_count': 0,
            'status': 'INSUFFICIENT_DATA',
            'limitations': 'Forecast models administrative spending utilization trends based on historical timelines. Forecast deviations represent administrative tracking alerts, not proof of fraud.'
        }
        return pd.DataFrame(), summary_empty
        
    df_valid['year_month'] = df_valid['dt'].dt.to_period('M').astype(str)
    min_m = df_valid['year_month'].min()
    max_m = df_valid['year_month'].max()
    all_periods = pd.period_range(start=min_m, end=max_m, freq='M').astype(str)
    monthly_series = df_valid.groupby('year_month')['clean_amt'].sum().reindex(all_periods, fill_value=0.0)
    
    obs_count = len(monthly_series)
    if obs_count < MIN_FORECAST_OBSERVATIONS:
        summary_empty = {
            'model_id': 'M4_FORECAST',
            'model_name': 'MPLADS Expenditure Forecasting Model',
            'model_version': '1.0.0',
            'aggregation_level': 'NATIONAL',
            'historical_start': str(monthly_series.index[0]) if obs_count > 0 else 'N/A',
            'historical_end': str(monthly_series.index[-1]) if obs_count > 0 else 'N/A',
            'forecast_horizon': horizon_months,
            'forecasting_method': 'Forecast unavailable — insufficient historical observations',
            'observations_used': obs_count,
            'forecast_records': [],
            'total_expected_expenditure': 0.0,
            'total_actual_expenditure': 0.0,
            'anomaly_count': 0,
            'status': 'INSUFFICIENT_DATA',
            'limitations': 'Forecast models administrative spending utilization trends based on historical timelines. Forecast deviations represent administrative tracking alerts, not proof of fraud.'
        }
        return pd.DataFrame(), summary_empty

    historical_start = str(monthly_series.index[0])
    historical_end = str(monthly_series.index[-1])
    
    # 2. Historical Baseline & Time Series Moving Trend
    monthly_vals = monthly_series.values
    mean_exp = float(np.mean(monthly_vals))
    std_exp = float(np.std(monthly_vals))
    if std_exp == 0:
        std_exp = mean_exp * 0.25
        
    all_records = []
    future_records = []
    anomaly_count = 0
    total_expected = 0.0
    total_actual = 0.0
    
    # Evaluate historical months vs rolling baseline
    window_size = min(3, obs_count)
    for idx, (ym, actual_val) in enumerate(monthly_series.items()):
        actual_val = float(actual_val)
        total_actual += actual_val
        if idx < window_size:
            fcst_val = mean_exp
        else:
            fcst_val = float(np.mean(monthly_vals[max(0, idx-window_size):idx]))
            
        margin = 1.96 * std_exp
        lower_b = max(0.0, fcst_val - margin)
        upper_b = fcst_val + margin
        
        dev = actual_val - fcst_val
        dev_pct = (dev / fcst_val * 100.0) if fcst_val > 0 else 0.0
        
        if actual_val > upper_b:
            status = "ABOVE_EXPECTED_TREND"
            anomaly_count += 1
            ev_text = f"Monthly expenditure was {abs(dev_pct):.1f}% above the forecasted utilization level and outside the empirical 95% expected range."
        elif actual_val < lower_b:
            status = "BELOW_EXPECTED_TREND"
            anomaly_count += 1
            ev_text = f"Monthly expenditure was {abs(dev_pct):.1f}% below the forecasted utilization level and outside the empirical 95% expected range."
        else:
            status = "WITHIN_EXPECTED_RANGE"
            ev_text = "Expenditure tracking within empirical 95% expected range."
            
        rec = {
            'month': ym,
            'forecast_date': ym,
            'type': 'HISTORICAL_OBSERVED',
            'expected_expenditure': round(fcst_val, 2),
            'actual_expenditure': round(actual_val, 2),
            'forecast_expenditure': round(fcst_val, 2),
            'lower_bound': round(lower_b, 2),
            'upper_bound': round(upper_b, 2),
            'deviation': round(dev, 2),
            'deviation_pct': round(dev_pct, 2),
            'deviation_status': status,
            'utilization_warning': status in ['ABOVE_EXPECTED_TREND', 'BELOW_EXPECTED_TREND'],
            'evidence': ev_text
        }
        all_records.append(rec)
        
    # 3. Generate future forecast horizon using canonical recursive rolling mean
    last_dt = pd.to_datetime(historical_end + "-01")
    future_dates = pd.date_range(start=last_dt + pd.DateOffset(months=1), periods=horizon_months, freq="MS")
    
    future_predictions = recursive_rolling_mean_forecast(monthly_vals, horizon=horizon_months, window=3)
    
    for dt, fcst_val in zip(future_dates, future_predictions):
        ym = dt.strftime("%Y-%m")
        fcst_val = round(float(fcst_val), 2)
        total_expected += fcst_val
        margin = round(1.96 * std_exp, 2)
        lower_b = max(0.0, round(fcst_val - margin, 2))
        upper_b = round(fcst_val + margin, 2)
        
        rec = {
            'month': ym,
            'forecast_date': ym,
            'type': 'FUTURE_FORECAST',
            'expected_expenditure': fcst_val,
            'actual_expenditure': None,
            'forecast_expenditure': fcst_val,
            'lower_bound': lower_b,
            'upper_bound': upper_b,
            'deviation': 0.0,
            'deviation_pct': 0.0,
            'deviation_status': 'PROJECTED_FORECAST',
            'utilization_warning': False,
            'evidence': 'Projected utilization trend based on historical monthly expenditure patterns.'
        }
        all_records.append(rec)
        future_records.append(rec)
        
    df_future = pd.DataFrame(future_records)
    df_all = pd.DataFrame(all_records)
    
    results = {
        'model_id': 'M4_FORECAST',
        'model_name': 'MPLADS Expenditure Forecasting Model',
        'model_version': '1.0.0',
        'aggregation_level': 'NATIONAL',
        'historical_start': historical_start,
        'historical_end': historical_end,
        'forecast_horizon': horizon_months,
        'forecasting_method': 'Recursive 3-Month Rolling Average with Empirical 95% Expected Range',
        'observations_used': obs_count,
        'total_expected_expenditure': round(total_expected, 2),
        'total_actual_expenditure': round(total_actual, 2),
        'anomaly_count': anomaly_count,
        'status': 'SUCCESS',
        'limitations': 'Forecast models administrative spending utilization trends based on historical timelines. Forecast deviations represent administrative tracking alerts, not proof of fraud.',
        'forecast_records': all_records,
        'timeline': all_records
    }
    
    # 4. Save outputs to output/
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "expenditure_forecast_results.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    with open(os.path.join(OUTPUT_DIR, "expenditure_forecast.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    df_all.to_csv(os.path.join(OUTPUT_DIR, "expenditure_forecast.csv"), index=False)
    
    return df_future, results
