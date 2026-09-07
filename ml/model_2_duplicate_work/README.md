# Model 2 — Duplicate Work / Record Linkage Engine

- **Purpose**: Identifies potential duplicate work recommendations and double-dipping across geographical partitions.
- **Input**: Work descriptions, sanctioned amounts, state, district, constituency.
- **Features**: TF-IDF n-gram vector representations, character n-gram similarity, and token set overlap.
- **Algorithm**: Geographic Candidate Blocking (State + District + Work Category) with Cosine Similarity scoring.
- **Output**: Candidate duplicate pairs with risk scores (0–100%) and risk tiers (HIGH RISK, MEDIUM RISK, LOW RISK).
- **Called From**: ml.model_2_duplicate_work.double_dipping.run_double_dipping_detection()
- **Evaluation Method**: Blocked pair candidate space scoring diagnostic (61.98% candidate pairs with similarity >= 85%).
- **Known Limitations**: Cross-house (LS<->RS) duplicate matching is disabled pending verified MP linkage metadata.
