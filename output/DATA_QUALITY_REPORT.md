# COMPREHENSIVE DATA QUALITY & ANOMALY INVENTORY REPORT
**Generated At**: 2026-09-07T15:05:11.904578

## 1. Summary of Data Quality Findings Across All 17 Real Datasets

| File Name | Total Rows | Total Cells | Null Cells (%) | Exact Dup Rows | Negative Amounts | Small Value (< ₹1k) Amounts | Malformed Dates |
|---|---:|---:|---:|---:|---|---|---|
| `Allocated Limit for Honble MPs_LokSabha_17.csv` | 544 | 2,720 | 3 (0.11%) | 0 | None (0) | Allocated AMOUNT ( ₹ ): 1 | None (0) |
| `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv` | 138,575 | 1,524,325 | 0 (0.0%) | 0 | None (0) | Fund Disbursed Amount ( ₹ ): 1180 | Expenditure Date: 1 |
| `Works Completed_LokSabha_17.csv` | 71,256 | 783,816 | 21,641 (2.76%) | 0 | None (0) | None (0) | Completion Date: 1 |
| `Works Recommended_LokSabha_17.csv` | 94,749 | 1,042,239 | 3,056 (0.29%) | 0 | None (0) | RECOMMENDED AMOUNT   ( ₹ ): 9 | Recommended date: 1, Sanction Date: 1 |
| `Works Sanctioned_LokSabha_17.csv` | 92,117 | 1,105,404 | 252 (0.02%) | 0 | None (0) | Sanction Amount ( ₹ ): 4 | Recommended date: 1, Sanction Date: 1 |
| `Allocated Limit for Honble MPs_LokSabha_18.csv` | 544 | 2,720 | 1 (0.04%) | 0 | None (0) | None (0) | None (0) |
| `Amount consented for Calamity_LokSabha_18.csv` | 13 | 78 | 0 (0.0%) | 0 | None (0) | None (0) | Date of Consent: 1 |
| `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv` | 84,172 | 925,892 | 0 (0.0%) | 0 | None (0) | Fund Disbursed Amount ( ₹ ): 695 | Expenditure Date: 1 |
| `Works Completed_LokSabha_18.csv` | 34,440 | 378,840 | 9,462 (2.5%) | 0 | None (0) | None (0) | Completion Date: 1 |
| `Works Recommended_LokSabha_18.csv` | 107,024 | 1,177,264 | 28,287 (2.4%) | 0 | None (0) | RECOMMENDED AMOUNT   ( ₹ ): 44 | Recommended date: 1, Sanction Date: 1 |
| `Works Sanctioned_LokSabha_18.csv` | 79,220 | 950,640 | 98 (0.01%) | 0 | None (0) | Sanction Amount ( ₹ ): 3 | Recommended date: 1, Sanction Date: 1 |
| `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv` | 232 | 1,160 | 0 (0.0%) | 0 | None (0) | None (0) | None (0) |
| `Amount_consented_for_Calamity_Rajya_Sitting.csv` | 21 | 126 | 0 (0.0%) | 0 | None (0) | None (0) | Date of Consent: 1 |
| `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv` | 25,141 | 276,551 | 0 (0.0%) | 0 | None (0) | Fund Disbursed Amount ( ₹ ): 93 | Expenditure Date: 1 |
| `Works_Completed_Rajya_Sitting.csv` | 9,979 | 109,769 | 3,492 (3.18%) | 0 | None (0) | None (0) | Completion Date: 1 |
| `Works_Recommended_Rajya_Sitting.csv` | 25,240 | 277,640 | 5,889 (2.12%) | 0 | None (0) | RECOMMENDED AMOUNT   ( ₹ ): 4 | Recommended date: 1, Sanction Date: 1 |
| `Works_Sanctioned_Rajya_Sitting.csv` | 19,607 | 235,284 | 18 (0.01%) | 0 | None (0) | None (0) | Recommended date: 1, Sanction Date: 1 |

## 2. Policy on Data Cleaning & Quality Remediation

1. **No Silent Row Deletion**: Problematic rows, incomplete lifecycle stages, and missing expenditure values are preserved with explicit missingness flags rather than dropped.
2. **Small-Value Floor Filter**: Small-value records with sanctioned amounts under ₹1,000 (e.g. ₹0 or nominal placeholder entries in 1,228 LS18 records) are flagged as `is_below_floor = True` and isolated from peer cost distribution modeling (Model 2) to avoid dividing by near-zero denominators.
3. **Null vs Zero Preservation**: Unmatched expenditure records maintain `NaN` / `None` for expenditure amounts and are never artificially populated with ₹0.00.
4. **Standardization & Entity Resolution**: District and constituency names undergo deterministic string normalization (e.g., stripping administrative IDA titles like `JAUNPUR(DISTRICT MAGISTRATE...)` -> `JAUNPUR`) to ensure robust spatial grouping.
