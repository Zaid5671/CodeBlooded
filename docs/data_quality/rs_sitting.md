# Data Quality Report — RS_SITTING (Rajya Sabha - RajyaSabha_Sitting)

- **House**: Rajya Sabha
- **Corpus**: RS_SITTING
- **Source Folder**: `data/original/RajyaSabha_Sitting/`
- **Total Files**: 6

## Dataset Grain & Row Count Inventory

| File Name | Data Grain | Total Rows | Null % |
|---|---|---|---|
| `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv` | MP ALLOCATION | 232 | 0.0% |
| `Amount_consented_for_Calamity_Rajya_Sitting.csv` | CALAMITY CONSENT | 21 | 0.0% |
| `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv` | TRANSACTION / VOUCHER | 25,141 | 0.0% |
| `Works_Completed_Rajya_Sitting.csv` | COMPLETION RECORD | 9,979 | 3.18% |
| `Works_Recommended_Rajya_Sitting.csv` | RECOMMENDATION | 25,240 | 2.12% |
| `Works_Sanctioned_Rajya_Sitting.csv` | WORK (SANCTIONED) | 19,607 | 0.01% |

## Data Integrity & Null Analysis
- **Monetary Unit**: Indian Rupees (₹ / INR). Verified clean string parsing.
- **Null Value Handling**: Nulls are preserved as legitimately unavailable source fields. Zero substitution is enforced ONLY when semantic contract proves zero.
- **House Isolation**: Preserved strictly under `house` and `corpus` flags.
