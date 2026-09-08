import os
import json
import pandas as pd
import numpy as np
from feature_engineering.preprocessing import clean_monetary_field
from ml.model_4_forecasting.expenditure_forecast import recursive_rolling_mean_forecast
from ml.config import DATA_DIR, OUTPUT_DIR

def run_m4_empirical_reconciliation(data_dir=DATA_DIR):
    """
    Independent Empirical M4 Metric Reconciliation Script.
    Evaluates M4 (Recursive 3-Month Rolling Average) vs Naive Baseline (Lag 1 Previous Month)
    on raw canonical LokSabha18 expenditure source data.
    """
    exp_path = os.path.join(data_dir, "LokSabha18", "Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv")
    if not os.path.exists(exp_path):
        exp_path = os.path.join(data_dir, "Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv")
        
    df_exp = pd.read_csv(exp_path, low_memory=False)
    
    amt_cols = [c for c in df_exp.columns if ('disbursed' in c.lower() or 'amount' in c.lower()) and 'date' not in c.lower()]
    amt_col = amt_cols[0] if amt_cols else df_exp.columns[-1]
    date_col = 'Expenditure Date' if 'Expenditure Date' in df_exp.columns else 'date'
    state_col = 'State' if 'State' in df_exp.columns else 'State Name'
    
    df_exp['clean_amt'] = clean_monetary_field(df_exp[amt_col])
    df_exp['dt'] = pd.to_datetime(df_exp[date_col], errors='coerce', dayfirst=True)
    df_valid = df_exp.dropna(subset=['dt', 'clean_amt']).copy()
    df_valid['year_month'] = df_valid['dt'].dt.to_period('M').astype(str)
    
    min_m = df_valid['year_month'].min()
    max_m = df_valid['year_month'].max()
    all_periods = pd.period_range(start=min_m, end=max_m, freq='M').astype(str)
    
    nat_series = df_valid.groupby('year_month')['clean_amt'].sum().reindex(all_periods, fill_value=0.0)
    
    def compute_metrics(act_array, fcst_array, naive_array):
        act = np.array(act_array, dtype=float)
        fcst = np.array(fcst_array, dtype=float)
        naive = np.array(naive_array, dtype=float)
        
        mae = float(np.mean(np.abs(act - fcst)))
        rmse = float(np.sqrt(np.mean((act - fcst)**2)))
        sum_act = float(np.sum(np.abs(act)))
        wape = float(np.sum(np.abs(act - fcst)) / sum_act * 100.0) if sum_act > 0 else 0.0
        
        denom = np.abs(act) + np.abs(fcst)
        denom_safe = np.where(denom == 0, 1.0, denom)
        smape_arr = np.where(denom == 0, 0.0, 2.0 * np.abs(act - fcst) / denom_safe)
        smape = float(np.mean(smape_arr) * 100.0)
        
        naive_mae = float(np.mean(np.abs(act - naive)))
        naive_rmse = float(np.sqrt(np.mean((act - naive)**2)))
        naive_wape = float(np.sum(np.abs(act - naive)) / sum_act * 100.0) if sum_act > 0 else 0.0
        
        naive_denom = np.abs(act) + np.abs(naive)
        naive_denom_safe = np.where(naive_denom == 0, 1.0, naive_denom)
        naive_smape_arr = np.where(naive_denom == 0, 0.0, 2.0 * np.abs(act - naive) / naive_denom_safe)
        naive_smape = float(np.mean(naive_smape_arr) * 100.0)
        
        mae_improvement = float((naive_mae - mae) / naive_mae * 100.0) if naive_mae > 0 else 0.0
        
        return {
            'MAE': mae, 'RMSE': rmse, 'WAPE': wape, 'sMAPE': smape,
            'Naive_MAE': naive_mae, 'Naive_RMSE': naive_rmse, 'Naive_WAPE': naive_wape, 'Naive_sMAPE': naive_smape,
            'MAE_Improvement_%': mae_improvement
        }
        
    # Evaluation Split 1: National Aggregate 8-Month Holdout (2024-07 to 2026-01 Train; 2026-02 to 2026-09 Test)
    train_1 = nat_series.loc['2024-07':'2026-01'].values
    test_1_act = nat_series.loc['2026-02':'2026-09'].values
    fcst_1 = recursive_rolling_mean_forecast(train_1, horizon=len(test_1_act), window=3)
    naive_1 = [train_1[-1]] + list(test_1_act[:-1])
    m_1 = compute_metrics(test_1_act, fcst_1, naive_1)
    
    # Evaluation Split 2: National Aggregate 6-Month Horizon (2024-07 to 2026-02 Train; 2026-03 to 2026-08 Test)
    train_2 = nat_series.loc['2024-07':'2026-02'].values
    test_2_act = nat_series.loc['2026-03':'2026-08'].values
    fcst_2 = recursive_rolling_mean_forecast(train_2, horizon=len(test_2_act), window=3)
    naive_2 = [train_2[-1]] + list(test_2_act[:-1])
    m_2 = compute_metrics(test_2_act, fcst_2, naive_2)

    # Evaluation Split 3: State-Month Panel (2024-07 to 2026-01 Train; 2026-02 to 2026-09 Test)
    states = df_valid[state_col].dropna().unique()
    state_panel = df_valid.groupby([state_col, 'year_month'])['clean_amt'].sum()
    train_months = [p for p in all_periods if p <= '2026-01']
    test_months = [p for p in all_periods if p >= '2026-02']
    
    st_act, st_fcst, st_naive = [], [], []
    for st in states:
        s_series = state_panel.get(st, pd.Series(dtype=float)).reindex(all_periods, fill_value=0.0)
        tr = s_series.loc[train_months].values
        te = s_series.loc[test_months].values
        st_act.extend(te)
        st_fcst.extend(recursive_rolling_mean_forecast(tr, horizon=len(te), window=3))
        st_naive.extend([tr[-1]] + list(te[:-1]))
    m_3 = compute_metrics(st_act, st_fcst, st_naive)

    results = {
        'split_1_national_8m': {
            'description': 'National Aggregate 8-Month Holdout (2026-02 to 2026-09)',
            'training_period': ['2024-07', '2026-01'],
            'test_period': ['2026-02', '2026-09'],
            'n_train': len(train_1),
            'n_test': len(test_1_act),
            'actuals': test_1_act.tolist(),
            'forecasts': fcst_1,
            'naives': naive_1,
            'metrics': m_1
        },
        'split_2_national_6m': {
            'description': 'National Aggregate 6-Month Horizon (2026-03 to 2026-08 excluding partial month)',
            'training_period': ['2024-07', '2026-02'],
            'test_period': ['2026-03', '2026-08'],
            'n_train': len(train_2),
            'n_test': len(test_2_act),
            'actuals': test_2_act.tolist(),
            'forecasts': fcst_2,
            'naives': naive_2,
            'metrics': m_2
        },
        'split_3_state_panel_8m': {
            'description': 'State-Month Panel 8-Month Holdout (2026-02 to 2026-09)',
            'training_period': ['2024-07', '2026-01'],
            'test_period': ['2026-02', '2026-09'],
            'n_train': len(train_months),
            'n_test': len(test_months),
            'n_cells': len(st_act),
            'metrics': m_3
        }
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_json = os.path.join(OUTPUT_DIR, "m4_metric_reconciliation.json")
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = run_m4_empirical_reconciliation()
    print("=== M4 METRIC RECONCILIATION COMPLETE ===")
    print(json.dumps(res, indent=2))
