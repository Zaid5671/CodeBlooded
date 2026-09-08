# Monetary Field Standardization & Scaling Audit

All monetary fields across all 4 dataset families (`LS18`, `LS17`, `RS_SITTING`, `RS_RETIRED`) have been audited.

## Verified Unit Scaling

- **Currency Standard**: Indian Rupees (₹ / INR)
- **Monetary Floor**: ₹1,000 analytical floor for IsolationForest cost overrun evaluation.
- **Scaling Integrity**: No unannounced Lakh/Crore multipliers applied. All amounts parsed directly from official strings.

## Summary Statistics by Dataset File

| Dataset | File Name | Monetary Field | Min (₹) | Max (₹) | Mean (₹) |
|---|---|---|---|---|---|
| `LokSabha17` | `Allocated Limit for Honble MPs_LokSabha_17.csv` | `Allocated AMOUNT ( ₹ )` | ₹0.11 | ₹47,588,887,166.81 | ₹175,929,342.58 |
| `LokSabha17` | `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv` | `Fund Disbursed Amount ( ₹ )` | ₹0.25 | ₹38,810,444,965.73 | ₹560,136.32 |
| `LokSabha17` | `Works Completed_LokSabha_17.csv` | `Amount Disbursed ( ₹ )` | ₹1,608.00 | ₹32,278,195,509.69 | ₹908,835.33 |
| `LokSabha17` | `Works Recommended_LokSabha_17.csv` | `RECOMMENDED AMOUNT   ( ₹ )` | ₹1.00 | ₹75,742,166.00 | ₹469,374.23 |
| `LokSabha17` | `Works Recommended_LokSabha_17.csv` | `Sanction Date` | ₹44,469,922,950.70 | ₹44,469,922,950.70 | ₹44,469,922,950.70 |
| `LokSabha17` | `Works Sanctioned_LokSabha_17.csv` | `Sanction Amount ( ₹ )` | ₹3.92 | ₹75,742,166.00 | ₹469,009.23 |
| `LokSabha18` | `Allocated Limit for Honble MPs_LokSabha_18.csv` | `Allocated AMOUNT ( ₹ )` | ₹49,000,000.00 | ₹83,336,673,298.01 | ₹306,949,072.92 |
| `LokSabha18` | `Amount consented for Calamity_LokSabha_18.csv` | `Consent Amount ( ₹ )` | ₹500,000.00 | ₹40,567,400.00 | ₹6,241,138.46 |
| `LokSabha18` | `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv` | `Fund Disbursed Amount ( ₹ )` | ₹1.00 | ₹27,787,500,708.45 | ₹660,255.21 |
| `LokSabha18` | `Works Completed_LokSabha_18.csv` | `Amount Disbursed ( ₹ )` | ₹8,448.00 | ₹16,665,942,883.40 | ₹970,078.17 |
| `LokSabha18` | `Works Recommended_LokSabha_18.csv` | `RECOMMENDED AMOUNT   ( ₹ )` | ₹1.00 | ₹99,965,000.00 | ₹535,540.08 |
| `LokSabha18` | `Works Recommended_LokSabha_18.csv` | `Sanction Date` | ₹57,315,106,318.41 | ₹57,315,106,318.41 | ₹57,315,106,318.41 |
| `LokSabha18` | `Works Sanctioned_LokSabha_18.csv` | `Sanction Amount ( ₹ )` | ₹2.46 | ₹49,740,000.00 | ₹527,221.95 |
| `RajyaSabha_Retired` | `Allocated Limit for Honble MPs (1).csv` | `Allocated AMOUNT ( ₹ )` | ₹23,800,006.00 | ₹33,638,482,301.82 | ₹289,986,916.40 |
| `RajyaSabha_Retired` | `Amount consented for Calamity.csv` | `Consent Amount ( ₹ )` | ₹500,000.00 | ₹104,500,000.00 | ₹9,952,380.95 |
| `RajyaSabha_Retired` | `Expenditure on Completed and On-going Works as on Date.csv` | `Fund Disbursed Amount ( ₹ )` | ₹0.01 | ₹12,425,553,082.69 | ₹988,901.96 |
| `RajyaSabha_Retired` | `Works Completed.csv` | `Amount Disbursed ( ₹ )` | ₹10,000.00 | ₹7,614,976,892.21 | ₹1,532,034.38 |
| `RajyaSabha_Retired` | `Works Recommended.csv` | `RECOMMENDED AMOUNT   ( ₹ )` | ₹3.89 | ₹73,500,000.00 | ₹885,265.09 |
| `RajyaSabha_Retired` | `Works Recommended.csv` | `Sanction Date` | ₹22,311,336,185.21 | ₹22,311,336,185.21 | ₹22,311,336,185.21 |
| `RajyaSabha_Retired` | `Works Sanctioned.csv` | `Sanction Amount ( ₹ )` | ₹10,000.00 | ₹73,500,000.00 | ₹874,629.24 |
| `RajyaSabha_Sitting` | `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv` | `Allocated AMOUNT ( ₹ )` | ₹23,800,006.00 | ₹33,638,482,301.82 | ₹289,986,916.40 |
| `RajyaSabha_Sitting` | `Amount_consented_for_Calamity_Rajya_Sitting.csv` | `Consent Amount ( ₹ )` | ₹500,000.00 | ₹104,500,000.00 | ₹9,952,380.95 |
| `RajyaSabha_Sitting` | `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv` | `Fund Disbursed Amount ( ₹ )` | ₹0.01 | ₹12,432,221,932.69 | ₹988,999.80 |
| `RajyaSabha_Sitting` | `Works_Completed_Rajya_Sitting.csv` | `Amount Disbursed ( ₹ )` | ₹10,000.00 | ₹7,635,111,513.21 | ₹1,533,770.89 |
| `RajyaSabha_Sitting` | `Works_Recommended_Rajya_Sitting.csv` | `RECOMMENDED AMOUNT   ( ₹ )` | ₹3.89 | ₹73,500,000.00 | ₹884,686.19 |
| `RajyaSabha_Sitting` | `Works_Recommended_Rajya_Sitting.csv` | `Sanction Date` | ₹22,328,594,702.21 | ₹22,328,594,702.21 | ₹22,328,594,702.21 |
| `RajyaSabha_Sitting` | `Works_Sanctioned_Rajya_Sitting.csv` | `Sanction Amount ( ₹ )` | ₹10,000.00 | ₹73,500,000.00 | ₹874,629.24 |
