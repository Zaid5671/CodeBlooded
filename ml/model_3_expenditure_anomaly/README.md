# Model 3 — Expenditure & Disbursement Anomaly Detector

- **Purpose**: Evaluates payment disbursement structure and transaction velocity across works.
- **Input**: Expenditure disbursement records and voucher details.
- **Features**: Tranche count, payment frequency, payment fragmentation heuristic flags.
- **Algorithm**: Deterministic payment pattern matching and multi-tranche variance analysis.
- **Output**: Expenditure matching flags and payment fragmentation candidate tags.
- **Called From**: ml.pipeline.run_detection_pipeline() and ml.model_3_expenditure_anomaly.duplicate_expenditure
- **Evaluation Method**: Transaction voucher coverage audit (84,172 disbursement records evaluated).
- **Known Limitations**: Requires expenditure voucher records; missing vouchers are tracked separately from zero expenditure.
