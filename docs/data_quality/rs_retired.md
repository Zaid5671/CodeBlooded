# Data Quality Report — RS_RETIRED (Rajya Sabha - RajyaSabha_Retired)

- **House**: Rajya Sabha
- **Corpus**: RS_RETIRED
- **Source Folder**: `data/original/RajyaSabha_Retired/`
- **Total Files**: 6

## Dataset Grain & Row Count Inventory

| File Name | Data Grain | Total Rows | Null % |
|---|---|---|---|
| `Allocated Limit for Honble MPs (1).csv` | MP ALLOCATION | 232 | 0.0% |
| `Amount consented for Calamity.csv` | CALAMITY CONSENT | 21 | 0.0% |
| `Expenditure on Completed and On-going Works as on Date.csv` | TRANSACTION / VOUCHER | 25,130 | 0.0% |
| `Works Completed.csv` | COMPLETION RECORD | 9,964 | 3.19% |
| `Works Recommended.csv` | RECOMMENDATION | 25,204 | 2.11% |
| `Works Sanctioned.csv` | WORK (SANCTIONED) | 19,607 | 0.01% |

## Data Integrity & Null Analysis
- **Monetary Unit**: Indian Rupees (₹ / INR). Verified clean string parsing.
- **Null Value Handling**: Nulls are preserved as legitimately unavailable source fields. Zero substitution is enforced ONLY when semantic contract proves zero.
- **House Isolation**: Preserved strictly under `house` and `corpus` flags.
