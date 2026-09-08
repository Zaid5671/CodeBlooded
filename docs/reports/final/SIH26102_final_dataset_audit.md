# SIH26102 Final Dataset Audit Report
**SIH 2026 | Problem Statement: SIH26102**  
**AI-Powered MPLADS Audit Intelligence Platform — Team CodeBlooded**  

---

## 1. Complete Dataset Inventory (23 CSV Source Files)

A complete scan of all raw source CSV files in `data/original/` yields **863,032 raw rows** across 4 parliamentary corpora:

| Corpus Directory | CSV File Name | Raw Row Count | Column Count | Primary Monetary Field | Date Range |
|---|---|---|---|---|---|
| **LokSabha18** | `Works Sanctioned_LokSabha_18.csv` | **79,220** | 12 | `Sanctioned Amount ( ₹ )` | 2024-07 to 2026-09 |
| **LokSabha18** | `Works Recommended_LokSabha_18.csv` | **107,024** | 11 | `RECOMMENDED AMOUNT ( ₹ )` | 2024-06 to 2026-09 |
| **LokSabha18** | `Works Completed_LokSabha_18.csv` | **34,440** | 11 | `Amount Disbursed ( ₹ )` | 2024-07 to 2026-09 |
| **LokSabha18** | `Expenditure on Completed and On-going Works...` | **84,172** | 11 | `Fund Disbursed Amount ( ₹ )` | 2024-07 to 2026-09 |
| **LokSabha18** | `Allocated Limit for Honble MPs_LokSabha_18.csv` | **544** | 5 | `Allocated AMOUNT ( ₹ )` | N/A |
| **LokSabha18** | `Amount consented for Calamity_LokSabha_18.csv` | **13** | 6 | `Amount Consented ( ₹ )` | N/A |
| **LokSabha17** | `Works Sanctioned_LokSabha_17.csv` | **92,117** | 12 | `Sanctioned Amount ( ₹ )` | 2019-05 to 2024-05 |
| **LokSabha17** | `Works Recommended_LokSabha_17.csv` | **94,749** | 11 | `RECOMMENDED AMOUNT ( ₹ )` | 2019-05 to 2024-05 |
| **LokSabha17** | `Works Completed_LokSabha_17.csv` | **71,256** | 11 | `Amount Disbursed ( ₹ )` | 2019-05 to 2024-05 |
| **LokSabha17** | `Expenditure on Completed and On-going Works...` | **138,575** | 11 | `Fund Disbursed Amount ( ₹ )` | 2019-05 to 2024-05 |
| **LokSabha17** | `Allocated Limit for Honble MPs_LokSabha_17.csv` | **544** | 5 | `Allocated AMOUNT ( ₹ )` | N/A |
| **RajyaSabha_Sitting** | `Works_Sanctioned_Rajya_Sitting.csv` | **19,607** | 12 | `Sanctioned Amount ( ₹ )` | Active Term |
| **RajyaSabha_Sitting** | `Works_Recommended_Rajya_Sitting.csv` | **25,240** | 11 | `RECOMMENDED AMOUNT ( ₹ )` | Active Term |
| **RajyaSabha_Sitting** | `Works_Completed_Rajya_Sitting.csv` | **9,979** | 11 | `Amount Disbursed ( ₹ )` | Active Term |
| **RajyaSabha_Sitting** | `Expenditure_on_Completed_and_On-going...` | **25,141** | 11 | `Fund Disbursed Amount ( ₹ )` | Active Term |
| **RajyaSabha_Sitting** | `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv` | **232** | 5 | `Allocated AMOUNT ( ₹ )` | N/A |
| **RajyaSabha_Sitting** | `Amount_consented_for_Calamity_Rajya_Sitting.csv` | **21** | 6 | `Amount Consented ( ₹ )` | N/A |
| **RajyaSabha_Retired** | `Works Sanctioned.csv` | **19,607** | 12 | `Sanctioned Amount ( ₹ )` | Historical Term |
| **RajyaSabha_Retired** | `Works Recommended.csv` | **25,204** | 11 | `RECOMMENDED AMOUNT ( ₹ )` | Historical Term |
| **RajyaSabha_Retired** | `Works Completed.csv` | **9,964** | 11 | `Amount Disbursed ( ₹ )` | Historical Term |
| **RajyaSabha_Retired** | `Expenditure on Completed and On-going...` | **25,130** | 11 | `Fund Disbursed Amount ( ₹ )` | Historical Term |
| **RajyaSabha_Retired** | `Allocated Limit for Honble MPs (1).csv` | **232** | 5 | `Allocated AMOUNT ( ₹ )` | N/A |
| **RajyaSabha_Retired** | `Amount consented for Calamity.csv` | **21** | 6 | `Amount Consented ( ₹ )` | N/A |

---

## 2. Row Count & Master Works Reconciliation

- **Master Sanctioned Works Baseline**:
  - `LokSabha18`: **79,220 works** (Primary active baseline; total outlay = ₹3.0 Cr in micro sample, combined total = ₹4,176.6 Cr across master dataset).
  - `LokSabha17`: **92,117 works**
  - `RajyaSabha_Sitting`: **19,607 works**
  - `RajyaSabha_Retired`: **19,607 works**
- **Reconciliation Audit Result**: All row counts match 1:1 between raw CSV source files and canonical API endpoint responses. **Zero unexplained row count drops**.

---

## 3. Monetary Unit & Currency Sanitization Audit

- **Source Monetary Unit**: **Indian Rupees (₹)**.
- **Conversion Verification**:
  - `sanctioned_amount`: Stored natively in **₹** (e.g. ₹5,00,000).
  - UI Display: Converted to **₹ Cr** ($/\,10,000,000$) or **Lakh ₹** ($/\,100,000$) explicitly for presentation.
  - Max Outlay Check: ₹75,742,166.0 (₹7.57 Cr) max single sanction. Median outlay: ₹300,000 (₹3.0 Lakh).
- **Sanity Result**: **PASS** (Zero wrong unit scaling factors).

---

## 4. Date Parsing & Null Policy Audit

- **Date Range**: 2019-05-23 to 2026-09-06.
- **Anomalous Date Check**: Zero future dates beyond 2026-09-06. Zero negative durations.
- **Null Policy**: `NULL != 0.0`. Missing sanction amounts are imputed via peer state/category medians with `is_imputed` flags preserved.
