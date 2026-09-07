import os
import json
import pandas as pd
from .expenditure_forecast import generate_expenditure_forecast

def run_expenditure_forecasting(df_master=None):
    """
    Wrapper for MPLADS Expenditure Forecasting Model.
    Calls generate_expenditure_forecast to produce deterministic time-series trends and prediction bounds.
    """
    df_forecast, results = generate_expenditure_forecast(df_master=df_master)
    return df_forecast, results
