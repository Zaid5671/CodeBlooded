# Model 1 — Anomalous Cost Estimate & Cost Overrun Detection

- **Purpose**: Flags projects exhibiting statistically extreme sanction amounts relative to peer groups and cost overruns.
- **Input**: Sanctioned works dataset (Sanction Amount, Work Category, State, District).
- **Features**: 8 synchronized numerical features including log sanction amount, peer z-score, robust deviation, and approval interval.
- **Algorithm**: sklearn.ensemble.IsolationForest (n_estimators=300, contamination=0.05) + Hierarchical Peer IQR/MAD Tukey Fences.
- **Output**: Anomaly score (0.0–1.0), isolation_forest_flag (boolean), peer_iqr_flag (boolean).
- **Called From**: ml.pipeline.run_detection_pipeline()
- **Evaluation Method**: Chronological 80/20 train/test split stability audit (4.46% out-of-sample anomaly rate, Jaccard 0.3862).
- **Known Limitations**: Detects statistical & financial outliers requiring human investigation; does not constitute proof of fraud.
