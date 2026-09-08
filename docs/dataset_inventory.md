# MPLADS Complete Dataset Inventory Audit

> **System**: SIH26102 AI-Powered MPLADS Audit Intelligence Platform  
> **Source Directory**: `data/original/`  
> **Total Discovered Source Files**: 23 CSV Files

## 1. Summary of All 4 Dataset Families

| Corpus / Family | File Name | Data Grain | Rows | Cols | Null % | Primary Key Candidate |
|---|---|---|---|---|---|---|
| `LokSabha17` | `Allocated Limit for Honble MPs_LokSabha_17.csv` | **MP ALLOCATION** | 544 | 5 | 0.11% | `MP ID / District` |
| `LokSabha17` | `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv` | **TRANSACTION / VOUCHER** | 138,575 | 11 | 0.0% | `Work ID / Sanction ID` |
| `LokSabha17` | `Works Completed_LokSabha_17.csv` | **COMPLETION RECORD** | 71,256 | 11 | 2.76% | `MP ID / District` |
| `LokSabha17` | `Works Recommended_LokSabha_17.csv` | **RECOMMENDATION** | 94,749 | 11 | 0.29% | `Work ID / Sanction ID` |
| `LokSabha17` | `Works Sanctioned_LokSabha_17.csv` | **WORK (SANCTIONED)** | 92,117 | 12 | 0.02% | `Work ID / Sanction ID` |
| `LokSabha18` | `Allocated Limit for Honble MPs_LokSabha_18.csv` | **MP ALLOCATION** | 544 | 5 | 0.04% | `MP ID / District` |
| `LokSabha18` | `Amount consented for Calamity_LokSabha_18.csv` | **CALAMITY CONSENT** | 13 | 6 | 0.0% | `MP ID / District` |
| `LokSabha18` | `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv` | **TRANSACTION / VOUCHER** | 84,172 | 11 | 0.0% | `Work ID / Sanction ID` |
| `LokSabha18` | `Works Completed_LokSabha_18.csv` | **COMPLETION RECORD** | 34,440 | 11 | 2.5% | `MP ID / District` |
| `LokSabha18` | `Works Recommended_LokSabha_18.csv` | **RECOMMENDATION** | 107,024 | 11 | 2.4% | `Work ID / Sanction ID` |
| `LokSabha18` | `Works Sanctioned_LokSabha_18.csv` | **WORK (SANCTIONED)** | 79,220 | 12 | 0.01% | `Work ID / Sanction ID` |
| `RajyaSabha_Retired` | `Allocated Limit for Honble MPs (1).csv` | **MP ALLOCATION** | 232 | 5 | 0.0% | `MP ID / District` |
| `RajyaSabha_Retired` | `Amount consented for Calamity.csv` | **CALAMITY CONSENT** | 21 | 6 | 0.0% | `MP ID / District` |
| `RajyaSabha_Retired` | `Expenditure on Completed and On-going Works as on Date.csv` | **TRANSACTION / VOUCHER** | 25,130 | 11 | 0.0% | `Work ID / Sanction ID` |
| `RajyaSabha_Retired` | `Works Completed.csv` | **COMPLETION RECORD** | 9,964 | 11 | 3.19% | `MP ID / District` |
| `RajyaSabha_Retired` | `Works Recommended.csv` | **RECOMMENDATION** | 25,204 | 11 | 2.11% | `Work ID / Sanction ID` |
| `RajyaSabha_Retired` | `Works Sanctioned.csv` | **WORK (SANCTIONED)** | 19,607 | 12 | 0.01% | `Work ID / Sanction ID` |
| `RajyaSabha_Sitting` | `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv` | **MP ALLOCATION** | 232 | 5 | 0.0% | `MP ID / District` |
| `RajyaSabha_Sitting` | `Amount_consented_for_Calamity_Rajya_Sitting.csv` | **CALAMITY CONSENT** | 21 | 6 | 0.0% | `MP ID / District` |
| `RajyaSabha_Sitting` | `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv` | **TRANSACTION / VOUCHER** | 25,141 | 11 | 0.0% | `Work ID / Sanction ID` |
| `RajyaSabha_Sitting` | `Works_Completed_Rajya_Sitting.csv` | **COMPLETION RECORD** | 9,979 | 11 | 3.18% | `MP ID / District` |
| `RajyaSabha_Sitting` | `Works_Recommended_Rajya_Sitting.csv` | **RECOMMENDATION** | 25,240 | 11 | 2.12% | `Work ID / Sanction ID` |
| `RajyaSabha_Sitting` | `Works_Sanctioned_Rajya_Sitting.csv` | **WORK (SANCTIONED)** | 19,607 | 12 | 0.01% | `Work ID / Sanction ID` |

## 2. Granular File Specifications & Schema Breakdown

### File: `LokSabha17/Allocated Limit for Honble MPs_LokSabha_17.csv`
- **Data Grain**: `MP ALLOCATION`
- **Row Count**: 544 records
- **Column Count**: 5 columns
- **Null Cell Percentage**: 0.11%
- **Columns**: `Sr. No., State, Hon'ble Members of Parliaments, Constituency, Allocated AMOUNT ( ₹ )`

### File: `LokSabha17/Expenditure on Completed and On-going Works as on Date_LokSabha17.csv`
- **Data Grain**: `TRANSACTION / VOUCHER`
- **Row Count**: 138,575 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., State, Work, Work ID, IDA, Hon'ble Members of Parliament, Constituency, Expenditure Date, Vendor Name, Payment Status, Fund Disbursed Amount ( ₹ )`

### File: `LokSabha17/Works Completed_LokSabha_17.csv`
- **Data Grain**: `COMPLETION RECORD`
- **Row Count**: 71,256 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 2.76%
- **Columns**: `Sr. No., Work Category, Work, State, IDA, Work Description, Hon'ble Members of Parliament, Constituency, Image, Completion Date, Amount Disbursed ( ₹ )`

### File: `LokSabha17/Works Recommended_LokSabha_17.csv`
- **Data Grain**: `RECOMMENDATION`
- **Row Count**: 94,749 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 0.29%
- **Columns**: `Sr. No., Work category, WORK, State, IDA, Hon'ble Members of Parliament, Constituency, Work description, Recommended date, RECOMMENDED AMOUNT   ( ₹ ), Sanction Date`

### File: `LokSabha17/Works Sanctioned_LokSabha_17.csv`
- **Data Grain**: `WORK (SANCTIONED)`
- **Row Count**: 92,117 records
- **Column Count**: 12 columns
- **Null Cell Percentage**: 0.02%
- **Columns**: `Sr. No., Work category, Work, State, IDA, Hon'ble Members of Parliament, Constituency, Work description, Recommended date, Sanction Date, Sanction Amount ( ₹ ), Work Status`

### File: `LokSabha18/Allocated Limit for Honble MPs_LokSabha_18.csv`
- **Data Grain**: `MP ALLOCATION`
- **Row Count**: 544 records
- **Column Count**: 5 columns
- **Null Cell Percentage**: 0.04%
- **Columns**: `Sr. No., State, Hon'ble Members of Parliaments, Constituency, Allocated AMOUNT ( ₹ )`

### File: `LokSabha18/Amount consented for Calamity_LokSabha_18.csv`
- **Data Grain**: `CALAMITY CONSENT`
- **Row Count**: 13 records
- **Column Count**: 6 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., Calamity Type, Calamity Name, Hon'ble Members of Parliament, Date of Consent, Consent Amount ( ₹ )`

### File: `LokSabha18/Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv`
- **Data Grain**: `TRANSACTION / VOUCHER`
- **Row Count**: 84,172 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., State, Work, Work ID, IDA, Hon'ble Members of Parliament, Constituency, Expenditure Date, Vendor Name, Payment Status, Fund Disbursed Amount ( ₹ )`

### File: `LokSabha18/Works Completed_LokSabha_18.csv`
- **Data Grain**: `COMPLETION RECORD`
- **Row Count**: 34,440 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 2.5%
- **Columns**: `Sr. No., Work Category, Work, State, IDA, Work Description, Hon'ble Members of Parliament, Constituency, Image, Completion Date, Amount Disbursed ( ₹ )`

### File: `LokSabha18/Works Recommended_LokSabha_18.csv`
- **Data Grain**: `RECOMMENDATION`
- **Row Count**: 107,024 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 2.4%
- **Columns**: `Sr. No., Work category, WORK, State, IDA, Hon'ble Members of Parliament, Constituency, Work description, Recommended date, RECOMMENDED AMOUNT   ( ₹ ), Sanction Date`

### File: `LokSabha18/Works Sanctioned_LokSabha_18.csv`
- **Data Grain**: `WORK (SANCTIONED)`
- **Row Count**: 79,220 records
- **Column Count**: 12 columns
- **Null Cell Percentage**: 0.01%
- **Columns**: `Sr. No., Work category, Work, State, IDA, Hon'ble Members of Parliament, Constituency, Work description, Recommended date, Sanction Date, Sanction Amount ( ₹ ), Work Status`

### File: `RajyaSabha_Retired/Allocated Limit for Honble MPs (1).csv`
- **Data Grain**: `MP ALLOCATION`
- **Row Count**: 232 records
- **Column Count**: 5 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., State, Hon'ble Members of Parliament, Elected/Nominated, Allocated AMOUNT ( ₹ )`

### File: `RajyaSabha_Retired/Amount consented for Calamity.csv`
- **Data Grain**: `CALAMITY CONSENT`
- **Row Count**: 21 records
- **Column Count**: 6 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., Calamity Type, Calamity Name, Hon'ble Members of Parliament, Date of Consent, Consent Amount ( ₹ )`

### File: `RajyaSabha_Retired/Expenditure on Completed and On-going Works as on Date.csv`
- **Data Grain**: `TRANSACTION / VOUCHER`
- **Row Count**: 25,130 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., State, Work, Work ID, IDA, Hon'ble Members of Parliament, Elected/Nominated, Expenditure Date, Vendor Name, Payment Status, Fund Disbursed Amount ( ₹ )`

### File: `RajyaSabha_Retired/Works Completed.csv`
- **Data Grain**: `COMPLETION RECORD`
- **Row Count**: 9,964 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 3.19%
- **Columns**: `Sr. No., Work Category, Work, State, IDA, Work Description, Hon'ble Members of Parliament, Elected/Nominated, Image, Completion Date, Amount Disbursed ( ₹ )`

### File: `RajyaSabha_Retired/Works Recommended.csv`
- **Data Grain**: `RECOMMENDATION`
- **Row Count**: 25,204 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 2.11%
- **Columns**: `Sr. No., Work category, WORK, State, IDA, Hon'ble Members of Parliament, Elected/Nominated, Work description, Recommended date, RECOMMENDED AMOUNT   ( ₹ ), Sanction Date`

### File: `RajyaSabha_Retired/Works Sanctioned.csv`
- **Data Grain**: `WORK (SANCTIONED)`
- **Row Count**: 19,607 records
- **Column Count**: 12 columns
- **Null Cell Percentage**: 0.01%
- **Columns**: `Sr. No., Work category, Work, State, IDA, Hon'ble Members of Parliament, Elected/Nominated, Work description, Recommended date, Sanction Date, Sanction Amount ( ₹ ), Work Status`

### File: `RajyaSabha_Sitting/Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv`
- **Data Grain**: `MP ALLOCATION`
- **Row Count**: 232 records
- **Column Count**: 5 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., State, Hon'ble Members of Parliament, Elected/Nominated, Allocated AMOUNT ( ₹ )`

### File: `RajyaSabha_Sitting/Amount_consented_for_Calamity_Rajya_Sitting.csv`
- **Data Grain**: `CALAMITY CONSENT`
- **Row Count**: 21 records
- **Column Count**: 6 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., Calamity Type, Calamity Name, Hon'ble Members of Parliament, Date of Consent, Consent Amount ( ₹ )`

### File: `RajyaSabha_Sitting/Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv`
- **Data Grain**: `TRANSACTION / VOUCHER`
- **Row Count**: 25,141 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 0.0%
- **Columns**: `Sr. No., State, Work, Work ID, IDA, Hon'ble Members of Parliament, Elected/Nominated, Expenditure Date, Vendor Name, Payment Status, Fund Disbursed Amount ( ₹ )`

### File: `RajyaSabha_Sitting/Works_Completed_Rajya_Sitting.csv`
- **Data Grain**: `COMPLETION RECORD`
- **Row Count**: 9,979 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 3.18%
- **Columns**: `Sr. No., Work Category, Work, State, IDA, Work Description, Hon'ble Members of Parliament, Elected/Nominated, Image, Completion Date, Amount Disbursed ( ₹ )`

### File: `RajyaSabha_Sitting/Works_Recommended_Rajya_Sitting.csv`
- **Data Grain**: `RECOMMENDATION`
- **Row Count**: 25,240 records
- **Column Count**: 11 columns
- **Null Cell Percentage**: 2.12%
- **Columns**: `Sr. No., Work category, WORK, State, IDA, Hon'ble Members of Parliament, Elected/Nominated, Work description, Recommended date, RECOMMENDED AMOUNT   ( ₹ ), Sanction Date`

### File: `RajyaSabha_Sitting/Works_Sanctioned_Rajya_Sitting.csv`
- **Data Grain**: `WORK (SANCTIONED)`
- **Row Count**: 19,607 records
- **Column Count**: 12 columns
- **Null Cell Percentage**: 0.01%
- **Columns**: `Sr. No., Work category, Work, State, IDA, Hon'ble Members of Parliament, Elected/Nominated, Work description, Recommended date, Sanction Date, Sanction Amount ( ₹ ), Work Status`

---

## 3. RS Sitting vs RS Retired Identity Audit & Combined Master Identity

### Empirical Source Identity Audit Results
- **Sitting Sanctioned Works**: 19,607 records
- **Retired Sanctioned Works**: 19,607 records
- `intersection_count`: **19,607** (100% Work ID overlap)
- `sitting_only_count`: **0**
- `retired_only_count`: **0**
- `union_count`: **19,607**
- `exact_identical_rows`: **19,606** out of 19,607.

**Conclusion**: `RS_SITTING` and `RS_RETIRED` represent two historical snapshot views of the same 19,607 Rajya Sabha work entities.

### Combined Master Entity Breakdown
- **Total Corpus Records**: **210,551** (LS18: 79,220 + LS17: 92,117 + RS_SITTING: 19,607 + RS_RETIRED: 19,607).
- **Unique Source Works**: **190,944** (LS18: 79,220 + LS17: 92,117 + RS Unique: 19,607).
- **Overlapping Records**: **19,607** (RS_RETIRED records overlapping 100% with RS_SITTING).


