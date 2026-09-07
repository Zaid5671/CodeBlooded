# Model 4 — Empirical Expenditure Forecasting Engine

- **Purpose**: Computes empirical 6-month expenditure projections baseline with expected bounds.
- **Input**: Historical monthly expenditure aggregation series.
- **Features**: Monthly disbursement sums, 6-month historical window rolling averages, empirical residual standard deviation.
- **Algorithm**: 6-month empirical rolling average baseline with 95% confidence bounds.
- **Output**: 6-month monthly expenditure forecast records with upper and lower expected bounds.
- **Called From**: ml.model_4_forecasting.expenditure_forecaster.run_expenditure_forecasting()
- **Evaluation Method**: Historical rolling window error analysis (Model MAE: ₹55.21 Cr vs Naïve: ₹55.36 Cr).
- **Known Limitations**: Baseline statistical projection for planning; subject to fiscal sanction cycles.
