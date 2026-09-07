# FULL REAL-DATA INVENTORY & STATISTICAL SCAN REPORT
**Generated At**: 2026-09-07T15:05:07.854429 | **Total Structured Files Scanned**: 17

## Executive Summary of Scanned Datasets

| # | Dataset File | Chamber / Term | Record Grain | Rows | Cols | Dupl Rows (%) | Work ID / Key Fields |
|---|---|---|---|---:|---:|---:|---|
| 1 | `Allocated Limit for Honble MPs_LokSabha_17.csv` | 17th Lok Sabha (2019-2024) | ONE ROW = ONE MP / CONSTITUENCY ALLOCATION RECORD | 544 | 5 | 0 (0.0%) | Hon'ble Members of Parliaments |
| 2 | `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv` | 17th Lok Sabha (2019-2024) | ONE ROW = ONE EXPENDITURE / PAYMENT TRANSACTION RECORD | 138,575 | 11 | 0 (0.0%) | Work ID, Hon'ble Members of Parliament |
| 3 | `Works Completed_LokSabha_17.csv` | 17th Lok Sabha (2019-2024) | ONE ROW = ONE COMPLETED WORK RECORD | 71,256 | 11 | 0 (0.0%) | Hon'ble Members of Parliament |
| 4 | `Works Recommended_LokSabha_17.csv` | 17th Lok Sabha (2019-2024) | ONE ROW = ONE WORK RECOMMENDATION PROPOSAL | 94,749 | 11 | 0 (0.0%) | Hon'ble Members of Parliament |
| 5 | `Works Sanctioned_LokSabha_17.csv` | 17th Lok Sabha (2019-2024) | ONE ROW = ONE SANCTIONED WORK / PROJECT ENTITY | 92,117 | 12 | 0 (0.0%) | Hon'ble Members of Parliament |
| 6 | `Allocated Limit for Honble MPs_LokSabha_18.csv` | 18th Lok Sabha (2024-Present) | ONE ROW = ONE MP / CONSTITUENCY ALLOCATION RECORD | 544 | 5 | 0 (0.0%) | Hon'ble Members of Parliaments |
| 7 | `Amount consented for Calamity_LokSabha_18.csv` | 18th Lok Sabha (2024-Present) | ONE ROW = ONE CALAMITY RELIEF CONSENT EVENT | 13 | 6 | 0 (0.0%) | Hon'ble Members of Parliament |
| 8 | `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv` | 18th Lok Sabha (2024-Present) | ONE ROW = ONE EXPENDITURE / PAYMENT TRANSACTION RECORD | 84,172 | 11 | 0 (0.0%) | Work ID, Hon'ble Members of Parliament |
| 9 | `Works Completed_LokSabha_18.csv` | 18th Lok Sabha (2024-Present) | ONE ROW = ONE COMPLETED WORK RECORD | 34,440 | 11 | 0 (0.0%) | Hon'ble Members of Parliament |
| 10 | `Works Recommended_LokSabha_18.csv` | 18th Lok Sabha (2024-Present) | ONE ROW = ONE WORK RECOMMENDATION PROPOSAL | 107,024 | 11 | 0 (0.0%) | Hon'ble Members of Parliament |
| 11 | `Works Sanctioned_LokSabha_18.csv` | 18th Lok Sabha (2024-Present) | ONE ROW = ONE SANCTIONED WORK / PROJECT ENTITY | 79,220 | 12 | 0 (0.0%) | Hon'ble Members of Parliament |
| 12 | `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv` | Sitting Members (Continuous House) | ONE ROW = ONE MP / CONSTITUENCY ALLOCATION RECORD | 232 | 5 | 0 (0.0%) | Hon'ble Members of Parliament |
| 13 | `Amount_consented_for_Calamity_Rajya_Sitting.csv` | Sitting Members (Continuous House) | ONE ROW = ONE CALAMITY RELIEF CONSENT EVENT | 21 | 6 | 0 (0.0%) | Hon'ble Members of Parliament |
| 14 | `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv` | Sitting Members (Continuous House) | ONE ROW = ONE EXPENDITURE / PAYMENT TRANSACTION RECORD | 25,141 | 11 | 0 (0.0%) | Work ID, Hon'ble Members of Parliament |
| 15 | `Works_Completed_Rajya_Sitting.csv` | Sitting Members (Continuous House) | ONE ROW = ONE COMPLETED WORK RECORD | 9,979 | 11 | 0 (0.0%) | Hon'ble Members of Parliament |
| 16 | `Works_Recommended_Rajya_Sitting.csv` | Sitting Members (Continuous House) | ONE ROW = ONE WORK RECOMMENDATION PROPOSAL | 25,240 | 11 | 0 (0.0%) | Hon'ble Members of Parliament |
| 17 | `Works_Sanctioned_Rajya_Sitting.csv` | Sitting Members (Continuous House) | ONE ROW = ONE SANCTIONED WORK / PROJECT ENTITY | 19,607 | 12 | 0 (0.0%) | Hon'ble Members of Parliament |

**Total Real Data Records Scanned Across All Files**: **782,874 rows**

- **Lok Sabha Total Rows**: 702,654
- **Rajya Sabha Total Rows**: 80,220

## Detailed File-by-File Statistical Profile

### 1. `Allocated Limit for Honble MPs_LokSabha_17.csv`
- **File Path**: `data/original/LokSabha17/Allocated Limit for Honble MPs_LokSabha_17.csv`
- **Chamber**: Lok Sabha | **Term**: 17th Lok Sabha (2019-2024)
- **Record Grain**: `ONE ROW = ONE MP / CONSTITUENCY ALLOCATION RECORD`
- **Dimensions**: 544 rows × 5 columns | Size: 42,317 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 543.0, Mean: 272.0, Median: 272.0, IQR: 271.0 (Q1: 136.5, Q3: 407.5) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 37 unique. Top: Uttar Pradesh (82); Maharashtra (48); West Bengal (42) |
| `Hon'ble Members of Parliaments` | `object` | `CATEGORICAL` | 0 (0.0%) | 544 unique. Top: A Chellakumar (1); Shri Bhartruhari Mahtab (17th Lok Sabha) (1); Shri Arjun Ram Meghwal (17LS)EX (1) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 541 unique. Top: MAINPURI (2); AZAMGARH (2); MAHABUBNAGAR (2) |
| `Allocated AMOUNT ( ₹ )` | `object` | `NUMERIC` | 3 (0.55%) | Min: 0.1099999994039535, Max: 47588887166.81, Mean: 175929342.58, Median: 92880335.0, IQR: 24500000.0 (Q1: 73563957.11, Q3: 98063957.11) |

---

### 2. `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv`
- **File Path**: `data/original/LokSabha17/Expenditure on Completed and On-going Works as on Date_LokSabha17.csv`
- **Chamber**: Lok Sabha | **Term**: 17th Lok Sabha (2019-2024)
- **Record Grain**: `ONE ROW = ONE EXPENDITURE / PAYMENT TRANSACTION RECORD`
- **Dimensions**: 138,575 rows × 11 columns | Size: 36,388,867 bytes
- **Exact Duplicate Rows**: 0 (0.0%)
- **Identifier Uniqueness**:
  - `Work ID`: 84,839 unique out of 138,575 records (53,736 duplicates, 38.78%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 138574.0, Mean: 69287.5, Median: 69287.5, IQR: 69286.5 (Q1: 34644.25, Q3: 103930.75) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 36 unique. Top: Uttar Pradesh (20,806); Rajasthan (15,005); Madhya Pradesh (11,570) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 113 unique. Top: Construction of roads, link roads, pathways or any other road with or without drainage system (34,145); Construction of community centers and community halls (15,822); Lighting of public spaces (14,883) |
| `Work ID` | `object` | `CATEGORICAL` | 0 (0.0%) | 84,839 unique. Top: WS/MP726/2023-2024/10181 (98); WS/MP726/2023-2024/12232 (88); WS/MP446/2023-2024/122247 (85) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 734 unique. Top: GANGANAGAR(Zilla GANGANAGAR) (2,345); ALMORA(DISTRICT MAGISTRATE ALMORA_IDA) (2,338); HOSHIARPUR(DEPUTY COMMISSIONER HOSHIARPUR_IDA) (1,918) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 540 unique. Top: Ajay Tamta (4,855); Mala Rajya Laxmi Shah (2,474); Nihal Chand Chauhan(17th Lok Sabha) (2,424) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 538 unique. Top: ALMORA(SC) (4,855); TEHRI GARHWAL (2,474); GANGANAGAR(SC) (2,424) |
| `Expenditure Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-07-31 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 1,074 |
| `Vendor Name` | `object` | `CATEGORICAL` | 0 (0.0%) | 42,046 unique. Top: Aditya Construction (1,308); Praharsh Infrastructure (926); KRIDL BHUSIRI ACCOUNT WORKS (884) |
| `Payment Status` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: Payment Success (137,653); Payment In-Progress (921);   (1) |
| `Fund Disbursed Amount ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 0.25, Max: 38810444965.729, Mean: 560136.32, Median: 150000.0, IQR: 320961.5 (Q1: 32916.0, Q3: 353877.5) |

---

### 3. `Works Completed_LokSabha_17.csv`
- **File Path**: `data/original/LokSabha17/Works Completed_LokSabha_17.csv`
- **Chamber**: Lok Sabha | **Term**: 17th Lok Sabha (2019-2024)
- **Record Grain**: `ONE ROW = ONE COMPLETED WORK RECORD`
- **Dimensions**: 71,256 rows × 11 columns | Size: 24,075,000 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 71255.0, Mean: 35628.0, Median: 35628.0, IQR: 35627.0 (Q1: 17814.5, Q3: 53441.5) |
| `Work Category` | `object` | `CATEGORICAL` | 43 (0.06%) | 5 unique. Top: Normal/Others (70,570); Repair and Renovation (419); Trust and Society (221) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 71,256 unique. Top: WS/MP317/2023-2024/1197-Construction of community centers and community halls (1); WS/MP354/2024-2025/126311-Lighting of public spaces (1); WS/MP582/2023-2024/97140-Lighting of public spaces (1) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 36 unique. Top: Uttar Pradesh (11,717); Gujarat (5,534); Bihar (5,446) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 718 unique. Top: Bara Banki(DISTRICT MAGISTRATE BARABANKI_IDA) (1,293); RAE BARELI(DISTRICT MAGISTRATE RAE BARELI_IDA) (1,131); VARANASI(DISTRICT MAGISTRAE VARANASI_IDA) (744) |
| `Work Description` | `object` | `CATEGORICAL` | 181 (0.25%) | 61,441 unique. Top: SOLAR LIGHT (978); Semi LED Highmast Light (380); From My MP development fund place the solar lights as par attached list by Area manager Uttaar Pradesh small corporation limited Prayagraj (304) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 534 unique. Top: Upendra Singh Rawat(17th Lok Sabha) (1,281); Smt. Sonia Gandhi (2019-24) (1,128); Ajay Tamta (1,048) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 533 unique. Top: BARABANKI(SC) (1,281); RAE BARELI (1,128); ALMORA(SC) (1,048) |
| `Image` | `object` | `CATEGORICAL` | 21,193 (29.74%) | 2 unique. Top: Images (50,062);   (1) |
| `Completion Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-07-26 00:00:00, Max Date: 2026-09-06 00:00:00, Unique Dates: 1,013 |
| `Amount Disbursed ( ₹ )` | `object` | `NUMERIC` | 224 (0.31%) | Min: 1608.0, Max: 32278195509.69, Mean: 908835.33, Median: 299154.0, IQR: 333641.0 (Q1: 166358.0, Q3: 499999.0) |

---

### 4. `Works Recommended_LokSabha_17.csv`
- **File Path**: `data/original/LokSabha17/Works Recommended_LokSabha_17.csv`
- **Chamber**: Lok Sabha | **Term**: 17th Lok Sabha (2019-2024)
- **Record Grain**: `ONE ROW = ONE WORK RECOMMENDATION PROPOSAL`
- **Dimensions**: 94,749 rows × 11 columns | Size: 32,340,750 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 94748.0, Mean: 47374.5, Median: 47374.5, IQR: 47373.5 (Q1: 23687.75, Q3: 71061.25) |
| `Work category` | `object` | `CATEGORICAL` | 52 (0.05%) | 5 unique. Top: Normal/Others (93,689); Repair and Renovation (630); Trust and Society (375) |
| `WORK` | `object` | `CATEGORICAL` | 0 (0.0%) | 92,026 unique. Top: NA-Construction of community centers and community halls (663); NA-Construction of roads, link roads, pathways or any other road with or without drainage system (439); NA-Construction of buildings for community cultural activities (252) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 36 unique. Top: Uttar Pradesh (14,769); Madhya Pradesh (7,691); Gujarat (6,533) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 736 unique. Top: RAE BARELI(DISTRICT MAGISTRATE RAE BARELI_IDA) (1,483); Bara Banki(DISTRICT MAGISTRATE BARABANKI_IDA) (1,355); PRAYAGRAJ(DISTRICT MAGISTRAE ALLAHABAD_IDA) (1,303) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 540 unique. Top: Smt. Sonia Gandhi (2019-24) (1,478); Upendra Singh Rawat(17th Lok Sabha) (1,340); Ajay Tamta (1,232) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 538 unique. Top: RAE BARELI (1,478); BARABANKI(SC) (1,340); ALMORA(SC) (1,232) |
| `Work description` | `object` | `CATEGORICAL` | 197 (0.21%) | 83,138 unique. Top: SOLAR LIGHT (1,009); Semi LED Highmast Light (380); From My MP development fund place the solar lights as par attached list by Area manager Uttaar Pradesh small corporation limited Prayagraj (311) |
| `Recommended date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2019-05-23 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 638 |
| `RECOMMENDED AMOUNT   ( ₹ )` | `object` | `NUMERIC` | 5 (0.01%) | Min: 1.0, Max: 75742166.0, Mean: 469374.23, Median: 299999.0, IQR: 336302.0 (Q1: 163698.0, Q3: 500000.0) |
| `Sanction Date` | `object` | `DATE` | 2,802 (2.96%) | Min Date: 2023-05-30 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 913 |

---

### 5. `Works Sanctioned_LokSabha_17.csv`
- **File Path**: `data/original/LokSabha17/Works Sanctioned_LokSabha_17.csv`
- **Chamber**: Lok Sabha | **Term**: 17th Lok Sabha (2019-2024)
- **Record Grain**: `ONE ROW = ONE SANCTIONED WORK / PROJECT ENTITY`
- **Dimensions**: 92,117 rows × 12 columns | Size: 33,487,313 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 92116.0, Mean: 46058.5, Median: 46058.5, IQR: 46057.5 (Q1: 23029.75, Q3: 69087.25) |
| `Work category` | `object` | `CATEGORICAL` | 51 (0.06%) | 5 unique. Top: Normal/Others (91,101); Repair and Renovation (610); Trust and Society (352) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 92,117 unique. Top: WS/MP300/2023-2024/198-Installing community drinking water plants (1); WS/MP614/2023-2024/96180-Construction of bus-sheds or bus-stops (1); WS/MP498/2024-2025/96200-Street lights (1) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 36 unique. Top: Uttar Pradesh (14,614); Madhya Pradesh (7,314); Gujarat (6,498) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 734 unique. Top: RAE BARELI(DISTRICT MAGISTRATE RAE BARELI_IDA) (1,479); Bara Banki(DISTRICT MAGISTRATE BARABANKI_IDA) (1,354); PRAYAGRAJ(DISTRICT MAGISTRAE ALLAHABAD_IDA) (1,298) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 540 unique. Top: Smt. Sonia Gandhi (2019-24) (1,474); Upendra Singh Rawat(17th Lok Sabha) (1,339); Ajay Tamta (1,226) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 538 unique. Top: RAE BARELI (1,474); BARABANKI(SC) (1,339); ALMORA(SC) (1,226) |
| `Work description` | `object` | `CATEGORICAL` | 196 (0.21%) | 80,680 unique. Top: SOLAR LIGHT (1,008); Semi LED Highmast Light (380); From My MP development fund place the solar lights as par attached list by Area manager Uttaar Pradesh small corporation limited Prayagraj (311) |
| `Recommended date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2019-08-18 00:00:00, Max Date: 2026-02-04 00:00:00, Unique Dates: 545 |
| `Sanction Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-05-30 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 913 |
| `Sanction Amount ( ₹ )` | `object` | `NUMERIC` | 5 (0.01%) | Min: 3.92, Max: 75742166.0, Mean: 469009.23, Median: 299982.0, IQR: 334734.5 (Q1: 165265.5, Q3: 500000.0) |
| `Work Status` | `object` | `CATEGORICAL` | 0 (0.0%) | 7 unique. Top: Physical Inspection (64,591); Work Completed (8,650); Vendor Identification (7,222) |

---

### 6. `Allocated Limit for Honble MPs_LokSabha_18.csv`
- **File Path**: `data/original/LokSabha18/Allocated Limit for Honble MPs_LokSabha_18.csv`
- **Chamber**: Lok Sabha | **Term**: 18th Lok Sabha (2024-Present)
- **Record Grain**: `ONE ROW = ONE MP / CONSTITUENCY ALLOCATION RECORD`
- **Dimensions**: 544 rows × 5 columns | Size: 35,604 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 543.0, Mean: 272.0, Median: 272.0, IQR: 271.0 (Q1: 136.5, Q3: 407.5) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 37 unique. Top: Uttar Pradesh (80); Maharashtra (49); West Bengal (42) |
| `Hon'ble Members of Parliaments` | `object` | `CATEGORICAL` | 0 (0.0%) | 544 unique. Top: AASHTIKAR PATIL NAGESH BAPURAO (1); Rajeshbhai Naranbhai Chudasama (1); RAJA RAM SINGH (1) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 543 unique. Top: NANDED (2); HINGOLI (1); JUNAGADH (1) |
| `Allocated AMOUNT ( ₹ )` | `object` | `NUMERIC` | 1 (0.18%) | Min: 49000000.0, Max: 83336673298.01, Mean: 306949072.92, Median: 147000000.0, IQR: 1375939.11 (Q1: 147000000.0, Q3: 148375939.11) |

---

### 7. `Amount consented for Calamity_LokSabha_18.csv`
- **File Path**: `data/original/LokSabha18/Amount consented for Calamity_LokSabha_18.csv`
- **Chamber**: Lok Sabha | **Term**: 18th Lok Sabha (2024-Present)
- **Record Grain**: `ONE ROW = ONE CALAMITY RELIEF CONSENT EVENT`
- **Dimensions**: 13 rows × 6 columns | Size: 1,323 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 12.0, Mean: 6.5, Median: 6.5, IQR: 5.5 (Q1: 3.75, Q3: 9.25) |
| `Calamity Type` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: National Calamity (7); State Calamity (5);   (1) |
| `Calamity Name` | `object` | `CATEGORICAL` | 0 (0.0%) | 7 unique. Top: Flood 2025 in Punjab (3); Meppadi landslides 2024 (3); Vilangad Landslides 2024 (2) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 11 unique. Top: SHAFI PARAMBIL (2); Shri NK Premachandran (2); Shri Gurjeet Singh Aujla (1) |
| `Date of Consent` | `object` | `DATE` | 0 (0.0%) | Min Date: 2024-09-03 00:00:00, Max Date: 2025-12-07 00:00:00, Unique Dates: 11 |
| `Consent Amount ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 500000.0, Max: 40567400.0, Mean: 6241138.46, Median: 2500000.0, IQR: 6067400.0 (Q1: 1000000.0, Q3: 7067400.0) |

---

### 8. `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv`
- **File Path**: `data/original/LokSabha18/Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv`
- **Chamber**: Lok Sabha | **Term**: 18th Lok Sabha (2024-Present)
- **Record Grain**: `ONE ROW = ONE EXPENDITURE / PAYMENT TRANSACTION RECORD`
- **Dimensions**: 84,172 rows × 11 columns | Size: 21,132,004 bytes
- **Exact Duplicate Rows**: 0 (0.0%)
- **Identifier Uniqueness**:
  - `Work ID`: 56,605 unique out of 84,172 records (27,567 duplicates, 32.75%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 84171.0, Mean: 42086.0, Median: 42086.0, IQR: 42085.0 (Q1: 21043.5, Q3: 63128.5) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 36 unique. Top: Uttar Pradesh (17,487); Punjab (8,445); Madhya Pradesh (7,429) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 111 unique. Top: Construction of roads, link roads, pathways or any other road with or without drainage system (21,206); Lighting of public spaces (10,653); Street lights (7,955) |
| `Work ID` | `object` | `CATEGORICAL` | 0 (0.0%) | 56,605 unique. Top: WS/MP18170/2025-2026/194491 (49); WS/MP444/2025-2026/178196 (47); WS/MP18201/2024-2025/141045 (46) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 740 unique. Top: JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA) (1,472); HOSHIARPUR(DEPUTY COMMISSIONER HOSHIARPUR_IDA) (1,305); BIJNOR(DISTRICT MAGISTRATE BIJNOR_IDA) (1,103) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 532 unique. Top: Smt Harsimrat Kaur Badal (1,509); DR. RAJ KUMAR CHABBEWAL (1,276); DR DHARAMVIRA GANDHI (1,196) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 532 unique. Top: BHATINDA (1,509); HOSHIARPUR(SC) (1,276); PATIALA (1,196) |
| `Expenditure Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2024-07-25 00:00:00, Max Date: 2026-09-06 00:00:00, Unique Dates: 692 |
| `Vendor Name` | `object` | `CATEGORICAL` | 0 (0.0%) | 23,594 unique. Top: BHAGWATI CHAND (789); NATIONAL INFRATECH (444); MEMBER SECY OB AND OC WWB BBSR (401) |
| `Payment Status` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: Payment Success (81,503); Payment In-Progress (2,668);   (1) |
| `Fund Disbursed Amount ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 27787500708.45, Mean: 660255.21, Median: 190546.0, IQR: 336171.0 (Q1: 63829.0, Q3: 400000.0) |

---

### 9. `Works Completed_LokSabha_18.csv`
- **File Path**: `data/original/LokSabha18/Works Completed_LokSabha_18.csv`
- **Chamber**: Lok Sabha | **Term**: 18th Lok Sabha (2024-Present)
- **Record Grain**: `ONE ROW = ONE COMPLETED WORK RECORD`
- **Dimensions**: 34,440 rows × 11 columns | Size: 10,984,924 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 34439.0, Mean: 17220.0, Median: 17220.0, IQR: 17219.0 (Q1: 8610.5, Q3: 25829.5) |
| `Work Category` | `object` | `CATEGORICAL` | 0 (0.0%) | 4 unique. Top: Normal/Others (33,944); Repair and Renovation (382); Trust and Society (113) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 34,440 unique. Top: WS/MP418/2024-2025/133409-Construction of roads, link roads, pathways or any other road with or without drainage system (1); WS/MP18055/2025-2026/225032-Construction of footpaths and pedestrian ways (1); WS/MP18309/2025-2026/233190-Providing supply pipelines for drinking water (1) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 34 unique. Top: Uttar Pradesh (7,372); Tamil Nadu (2,891); Gujarat (2,812) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 671 unique. Top: JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA) (1,020); South 24 Parganas(DISTRICT MAGISTRATE SOUTH TWENTY FOUR PARGANAS_IDA) (569); KAUSHAMBI(DISTRICT MAGISTRAE KAUSHAMBI_IDA) (525) |
| `Work Description` | `object` | `CATEGORICAL` | 79 (0.23%) | 31,017 unique. Top: Installation of Solar Light at Creamation Ground. (178); HIGH MAST LIGHT WITH FOUR LED RECOMMENDED IN MY CONSTITUENCY NAGINA BY IMPLEMNETING AGENCY PCCD BIJNORE (118); Water Tenkar (78) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 504 unique. Top: PRIYA SAROJ (725); PUSHPENDRA SAROJ (610); SAMBIT PATRA (548) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 504 unique. Top: MACHHLISHAHR(SC) (725); KAUSHAMBI(SC) (610); PURI (548) |
| `Image` | `object` | `CATEGORICAL` | 9,303 (27.01%) | 2 unique. Top: Images (25,136);   (1) |
| `Completion Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2024-08-12 00:00:00, Max Date: 2026-09-06 00:00:00, Unique Dates: 600 |
| `Amount Disbursed ( ₹ )` | `object` | `NUMERIC` | 80 (0.23%) | Min: 8448.0, Max: 16665942883.4, Mean: 970078.17, Median: 298955.0, IQR: 330470.0 (Q1: 169530.0, Q3: 500000.0) |

---

### 10. `Works Recommended_LokSabha_18.csv`
- **File Path**: `data/original/LokSabha18/Works Recommended_LokSabha_18.csv`
- **Chamber**: Lok Sabha | **Term**: 18th Lok Sabha (2024-Present)
- **Record Grain**: `ONE ROW = ONE WORK RECOMMENDATION PROPOSAL`
- **Dimensions**: 107,024 rows × 11 columns | Size: 34,062,272 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 107023.0, Mean: 53512.0, Median: 53512.0, IQR: 53511.0 (Q1: 26756.5, Q3: 80267.5) |
| `Work category` | `object` | `CATEGORICAL` | 0 (0.0%) | 5 unique. Top: Normal/Others (104,864); Repair and Renovation (1,423); Trust and Society (725) |
| `WORK` | `object` | `CATEGORICAL` | 0 (0.0%) | 78,956 unique. Top: NA-Construction of roads, link roads, pathways or any other road with or without drainage system (4,608); NA-Construction of community centers and community halls (3,754); NA-Street lights (3,421) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 37 unique. Top: Uttar Pradesh (20,537); Gujarat (8,487); Madhya Pradesh (7,458) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 764 unique. Top: KAUSHAMBI(DISTRICT MAGISTRAE KAUSHAMBI_IDA) (2,404); JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA) (1,853); South 24 Parganas(DISTRICT MAGISTRATE SOUTH TWENTY FOUR PARGANAS_IDA) (879) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 539 unique. Top: PUSHPENDRA SAROJ (2,589); PRIYA SAROJ (1,396); Ram Shiromani (1,357) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 539 unique. Top: KAUSHAMBI(SC) (2,589); MACHHLISHAHR(SC) (1,396); SHRAWASTI (1,357) |
| `Work description` | `object` | `CATEGORICAL` | 115 (0.11%) | 97,685 unique. Top: HIGH MAST LIGHT WITH FOUR LED RECOMMENDED IN MY CONSTITUENCY NAGINA BY IMPLEMNETING AGENCY PCCD BIJNORE (247); MS Pole with LED semi High Mast Light (182); Installation of Solar Light at Creamation Ground. (178) |
| `Recommended date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2024-07-08 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 764 |
| `RECOMMENDED AMOUNT   ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 99965000.0, Mean: 535540.08, Median: 309000.0, IQR: 394260.0 (Q1: 198724.0, Q3: 592984.0) |
| `Sanction Date` | `object` | `DATE` | 28,172 (26.32%) | Min Date: 2024-07-09 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 665 |

---

### 11. `Works Sanctioned_LokSabha_18.csv`
- **File Path**: `data/original/LokSabha18/Works Sanctioned_LokSabha_18.csv`
- **Chamber**: Lok Sabha | **Term**: 18th Lok Sabha (2024-Present)
- **Record Grain**: `ONE ROW = ONE SANCTIONED WORK / PROJECT ENTITY`
- **Dimensions**: 79,220 rows × 12 columns | Size: 27,556,498 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 79219.0, Mean: 39610.0, Median: 39610.0, IQR: 39609.0 (Q1: 19805.5, Q3: 59414.5) |
| `Work category` | `object` | `CATEGORICAL` | 0 (0.0%) | 5 unique. Top: Normal/Others (77,645); Repair and Renovation (1,102); Trust and Society (470) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 79,220 unique. Top: WS/	 MP620/2024-2025/133166-Construction of buildings for community cultural activities (1); WS/MP323/2025-2026/234193-Construction of roads, link roads, pathways or any other road with or without drainage system (1); WS/MP18041/2025-2026/234215-Street lights (1) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 37 unique. Top: Uttar Pradesh (15,039); Gujarat (6,399); Madhya Pradesh (5,670) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 755 unique. Top: JAUNPUR(DISTRICT MAGISTRATE JAUNPUR_IDA) (1,833); South 24 Parganas(DISTRICT MAGISTRATE SOUTH TWENTY FOUR PARGANAS_IDA) (844); Shrawasti(DISTRICT MAGISTRATE SHRAVASTI_IDA) (649) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 537 unique. Top: PRIYA SAROJ (1,383); PUSHPENDRA SAROJ (715); BABU SINGH KUSHWAHA (679) |
| `Constituency` | `object` | `CATEGORICAL` | 0 (0.0%) | 537 unique. Top: MACHHLISHAHR(SC) (1,383); KAUSHAMBI(SC) (715); JAUNPUR (679) |
| `Work description` | `object` | `CATEGORICAL` | 98 (0.12%) | 72,093 unique. Top: HIGH MAST LIGHT WITH FOUR LED RECOMMENDED IN MY CONSTITUENCY NAGINA BY IMPLEMNETING AGENCY PCCD BIJNORE (246); Installation of Solar Light at Creamation Ground. (178); Muktidham Nirman (109) |
| `Recommended date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2024-07-08 00:00:00, Max Date: 2026-09-03 00:00:00, Unique Dates: 755 |
| `Sanction Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2024-07-09 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 665 |
| `Sanction Amount ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 2.46, Max: 49740000.0, Mean: 527221.95, Median: 300000.0, IQR: 350989.5 (Q1: 199010.5, Q3: 550000.0) |
| `Work Status` | `object` | `CATEGORICAL` | 0 (0.0%) | 7 unique. Top: Physical Inspection (34,383); Sanction (20,277); Vendor Identification (11,563) |

---

### 12. `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv`
- **File Path**: `data/original/RajyaSabha_Sitting/Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv`
- **Chamber**: Rajya Sabha | **Term**: Sitting Members (Continuous House)
- **Record Grain**: `ONE ROW = ONE MP / CONSTITUENCY ALLOCATION RECORD`
- **Dimensions**: 232 rows × 5 columns | Size: 21,302 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 231.0, Mean: 116.0, Median: 116.0, IQR: 115.0 (Q1: 58.5, Q3: 173.5) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 33 unique. Top: Uttar Pradesh (31); Tamil Nadu (19); Maharashtra (18) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 232 unique. Top: Dr. Abhishek Manu Singhvi (2026-32) (2026-2032) (1); Shri Ramji Lal Suman (2024-30) (2024-2030) (1); Shri R. Dharmar (2022-28) (2022-2028) (1) |
| `Elected/Nominated` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: Elected MP (220); Nominated MP (11);   (1) |
| `Allocated AMOUNT ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 23800006.0, Max: 33638482301.82, Mean: 289986916.4, Median: 147000000.0, IQR: 122563957.11 (Q1: 73500000.0, Q3: 196063957.11) |

---

### 13. `Amount_consented_for_Calamity_Rajya_Sitting.csv`
- **File Path**: `data/original/RajyaSabha_Sitting/Amount_consented_for_Calamity_Rajya_Sitting.csv`
- **Chamber**: Rajya Sabha | **Term**: Sitting Members (Continuous House)
- **Record Grain**: `ONE ROW = ONE CALAMITY RELIEF CONSENT EVENT`
- **Dimensions**: 21 rows × 6 columns | Size: 2,525 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 20.0, Mean: 10.5, Median: 10.5, IQR: 9.5 (Q1: 5.75, Q3: 15.25) |
| `Calamity Type` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: National Calamity (12); State Calamity (8);   (1) |
| `Calamity Name` | `object` | `CATEGORICAL` | 0 (0.0%) | 5 unique. Top: Flood 2025 in Punjab (9); Wayanad landslides 2024 (6); Meppadi landslides 2024 (3) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 17 unique. Top: Shri P. P. Suneer (2024-30) (2024-2030) (2); Dr. John Brittas (2021-27) (2021-2027) (2); Shri Narain Dass Gupta (2024-30) (2024-2030) (2) |
| `Date of Consent` | `object` | `DATE` | 0 (0.0%) | Min Date: 2024-09-10 00:00:00, Max Date: 2025-11-17 00:00:00, Unique Dates: 16 |
| `Consent Amount ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 500000.0, Max: 104500000.0, Mean: 9952380.95, Median: 2500000.0, IQR: 7500000.0 (Q1: 2500000.0, Q3: 10000000.0) |

---

### 14. `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv`
- **File Path**: `data/original/RajyaSabha_Sitting/Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv`
- **Chamber**: Rajya Sabha | **Term**: Sitting Members (Continuous House)
- **Record Grain**: `ONE ROW = ONE EXPENDITURE / PAYMENT TRANSACTION RECORD`
- **Dimensions**: 25,141 rows × 11 columns | Size: 7,059,699 bytes
- **Exact Duplicate Rows**: 0 (0.0%)
- **Identifier Uniqueness**:
  - `Work ID`: 15,325 unique out of 25,141 records (9,816 duplicates, 39.04%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 25140.0, Mean: 12570.5, Median: 12570.5, IQR: 12569.5 (Q1: 6285.75, Q3: 18855.25) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 30 unique. Top: Uttar Pradesh (6,793); Punjab (3,076); Madhya Pradesh (1,939) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 100 unique. Top: Construction of roads, link roads, pathways or any other road with or without drainage system (7,929); Lighting of public spaces (4,268); Construction of community centers and community halls (1,321) |
| `Work ID` | `object` | `CATEGORICAL` | 0 (0.0%) | 15,325 unique. Top: WS/MP844/2023-2024/74812 (191); WS/MP140/2023-2024/17140 (68); WS/MP235/2025-2026/241415 (61) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 532 unique. Top: RANCHI(DEPUTY COMMISSIONER RANCHI_IDA) (1,144); FEROZEPUR(DEPUTY COMMISSIONER FIROZEPUR_IDA) (1,044); SONBHADRA(DISTRICT MAGISTRATE SONBHADRA_IDA) (885) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 171 unique. Top: Dr. Sandeep Kumar Pathak (2022-28) (2022-2028) (1,154); Shri Hardeep Singh Puri (2020-26) (2020-2026) (885); Shri B.L. Verma (2020-26) (2020-2026) (804) |
| `Elected/Nominated` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: Elected MP (24,018); Nominated MP (1,122);   (1) |
| `Expenditure Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-07-27 00:00:00, Max Date: 2026-09-06 00:00:00, Unique Dates: 960 |
| `Vendor Name` | `object` | `CATEGORICAL` | 0 (0.0%) | 6,118 unique. Top: shyam swaroop manufacturere (989); SHRI NAVKAR METALS LIMITED (384); HIDAYA QIRAT ENTERPRISES (317) |
| `Payment Status` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: Payment Success (24,680); Payment In-Progress (460);   (1) |
| `Fund Disbursed Amount ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 0.01, Max: 12432221932.69, Mean: 988999.8, Median: 248250.0, IQR: 483750.0 (Q1: 90000.0, Q3: 573750.0) |

---

### 15. `Works_Completed_Rajya_Sitting.csv`
- **File Path**: `data/original/RajyaSabha_Sitting/Works_Completed_Rajya_Sitting.csv`
- **Chamber**: Rajya Sabha | **Term**: Sitting Members (Continuous House)
- **Record Grain**: `ONE ROW = ONE COMPLETED WORK RECORD`
- **Dimensions**: 9,979 rows × 11 columns | Size: 3,572,605 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 9978.0, Mean: 4989.5, Median: 4989.5, IQR: 4988.5 (Q1: 2495.25, Q3: 7483.75) |
| `Work Category` | `object` | `CATEGORICAL` | 5 (0.05%) | 5 unique. Top: Normal/Others (9,810); Repair and Renovation (97); Trust and Society (65) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 9,979 unique. Top: WS/MP187/2023-2024/1362-Street lights (1); WS/MP18304/2025-2026/196165-Construction of flood control embankments/ protection walls along riverbanks, hilltops, roadsides (1); WS/MP847/2025-2026/138297-Lighting of public spaces (1) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 29 unique. Top: Uttar Pradesh (2,996); Bihar (1,173); Tamil Nadu (744) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 430 unique. Top: PATNA(DISTRICT PLANNING OFFICER PATNA_IDA) (489); BUDAUN(DISTRICT MAGISTRATE BUDAUN_IDA) (346); SHAHJAHANPUR(DISTRICT MAGISTRAE SHAHJAHANAPUR_IDA) (336) |
| `Work Description` | `object` | `CATEGORICAL` | 6 (0.06%) | 8,087 unique. Top: High Mast LED Light (9.5 mtrs MS Pole with 6 LED Light 150 W) (204); Purchase of books and periodicals for libraries (108); Led Semi High Mast Light (6LED) with 170-watt, 9 meter pole (96) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 157 unique. Top: Shri Baburam Nishad (2022-28) (NaN-NaN) (436); Shri B.L. Verma (2020-26) (NaN-NaN) (350); Dr. Dharmasthala Veerendra Heggade (2022-28) (NaN-NaN) (301) |
| `Elected/Nominated` | `object` | `CATEGORICAL` | 0 (0.0%) | 2 unique. Top: Elected MP (9,978);   (1) |
| `Image` | `object` | `CATEGORICAL` | 3,458 (34.65%) | 2 unique. Top: Images (6,520);   (1) |
| `Completion Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-08-02 00:00:00, Max Date: 2026-09-06 00:00:00, Unique Dates: 760 |
| `Amount Disbursed ( ₹ )` | `object` | `NUMERIC` | 23 (0.23%) | Min: 10000.0, Max: 7635111513.21, Mean: 1533770.89, Median: 497618.5, IQR: 746016.25 (Q1: 239405.0, Q3: 985421.25) |

---

### 16. `Works_Recommended_Rajya_Sitting.csv`
- **File Path**: `data/original/RajyaSabha_Sitting/Works_Recommended_Rajya_Sitting.csv`
- **Chamber**: Rajya Sabha | **Term**: Sitting Members (Continuous House)
- **Record Grain**: `ONE ROW = ONE WORK RECOMMENDATION PROPOSAL`
- **Dimensions**: 25,240 rows × 11 columns | Size: 9,102,890 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 25239.0, Mean: 12620.0, Median: 12620.0, IQR: 12619.0 (Q1: 6310.5, Q3: 18929.5) |
| `Work category` | `object` | `CATEGORICAL` | 5 (0.02%) | 5 unique. Top: Normal/Others (24,457); Repair and Renovation (419); Trust and Society (350) |
| `WORK` | `object` | `CATEGORICAL` | 0 (0.0%) | 19,468 unique. Top: NA-Construction of roads, link roads, pathways or any other road with or without drainage system (1,204); NA-Lighting of public spaces (976); NA-Construction of community centers and community halls (718) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 31 unique. Top: Uttar Pradesh (5,828); Bihar (1,828); Kerala (1,540) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 622 unique. Top: RANCHI(DEPUTY COMMISSIONER RANCHI_IDA) (859); PATNA(DISTRICT PLANNING OFFICER PATNA_IDA) (661); GHAZIPUR(DISTRICT MAGISTRAE GHAZIPUR_IDA) (470) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 197 unique. Top: Shri Baburam Nishad (2022-28) (2022-2028) (649); Shri Vivek K. Tankha (2022-28) (2022-2028) (504); Dr. Dharmasthala Veerendra Heggade (2022-28) (2022-2028) (474) |
| `Elected/Nominated` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: Elected MP (24,129); Nominated MP (1,110);   (1) |
| `Work description` | `object` | `CATEGORICAL` | 23 (0.09%) | 22,160 unique. Top: High Mast LED Light (9.5 mtrs MS Pole with 6 LED Light 150 W) (204); Purchase of books and periodicals for libraries (108); Regarding for giving single walled fabrication of 5000 ltr water tanker to Village. 2mm stainless sheet AISI 304 Material etc. (SC) (102) |
| `Recommended date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-06-14 00:00:00, Max Date: 2026-09-06 00:00:00, Unique Dates: 975 |
| `RECOMMENDED AMOUNT   ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 3.89, Max: 73500000.0, Mean: 884686.19, Median: 500000.0, IQR: 757000.0 (Q1: 243000.0, Q3: 1000000.0) |
| `Sanction Date` | `object` | `DATE` | 5,861 (23.22%) | Min Date: 2023-07-07 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 812 |

---

### 17. `Works_Sanctioned_Rajya_Sitting.csv`
- **File Path**: `data/original/RajyaSabha_Sitting/Works_Sanctioned_Rajya_Sitting.csv`
- **Chamber**: Rajya Sabha | **Term**: Sitting Members (Continuous House)
- **Record Grain**: `ONE ROW = ONE SANCTIONED WORK / PROJECT ENTITY`
- **Dimensions**: 19,607 rows × 12 columns | Size: 7,641,884 bytes
- **Exact Duplicate Rows**: 0 (0.0%)

#### Column Schema & Statistics

| Column Name | Type | Category | Null Count (%) | Summary Statistics / Distribution |
|---|---|---|---:|---|
| `Sr. No.` | `object` | `NUMERIC` | 0 (0.0%) | Min: 1.0, Max: 19606.0, Mean: 9803.5, Median: 9803.5, IQR: 9802.5 (Q1: 4902.25, Q3: 14704.75) |
| `Work category` | `object` | `CATEGORICAL` | 7 (0.04%) | 5 unique. Top: Normal/Others (19,071); Repair and Renovation (299); Trust and Society (227) |
| `Work` | `object` | `CATEGORICAL` | 0 (0.0%) | 19,607 unique. Top: WS/MP187/2023-2024/1199-Construction of rooms and halls in school and colleges (1); WS/MP007/2025-2026/219573-Installing tube-wells and borewells (1); WS/MP007/2025-2026/219580-Installing tube-wells and borewells (1) |
| `State` | `object` | `CATEGORICAL` | 0 (0.0%) | 30 unique. Top: Uttar Pradesh (4,873); Bihar (1,571); Madhya Pradesh (1,103) |
| `IDA` | `object` | `CATEGORICAL` | 0 (0.0%) | 573 unique. Top: RANCHI(DEPUTY COMMISSIONER RANCHI_IDA) (652); PATNA(DISTRICT PLANNING OFFICER PATNA_IDA) (648); SONBHADRA(DISTRICT MAGISTRATE SONBHADRA_IDA) (415) |
| `Hon'ble Members of Parliament` | `object` | `CATEGORICAL` | 0 (0.0%) | 179 unique. Top: Shri Baburam Nishad (2022-28) (2022-2028) (496); Dr. Dharmasthala Veerendra Heggade (2022-28) (2022-2028) (453); Shri Harsh Mahajan (2024-30) (2024-2030) (418) |
| `Elected/Nominated` | `object` | `CATEGORICAL` | 0 (0.0%) | 3 unique. Top: Elected MP (18,648); Nominated MP (958);   (1) |
| `Work description` | `object` | `CATEGORICAL` | 11 (0.06%) | 17,157 unique. Top: High Mast LED Light (9.5 mtrs MS Pole with 6 LED Light 150 W) (204); Purchase of books and periodicals for libraries (108); Regarding for giving single walled fabrication of 5000 ltr water tanker to Village. 2mm stainless sheet AISI 304 Material etc. (SC) (102) |
| `Recommended date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-06-14 00:00:00, Max Date: 2026-09-02 00:00:00, Unique Dates: 940 |
| `Sanction Date` | `object` | `DATE` | 0 (0.0%) | Min Date: 2023-07-07 00:00:00, Max Date: 2026-09-05 00:00:00, Unique Dates: 812 |
| `Sanction Amount ( ₹ )` | `object` | `NUMERIC` | 0 (0.0%) | Min: 10000.0, Max: 73500000.0, Mean: 874629.24, Median: 500000.0, IQR: 755700.0 (Q1: 243000.0, Q3: 998700.0) |
| `Work Status` | `object` | `CATEGORICAL` | 0 (0.0%) | 7 unique. Top: Physical Inspection (9,892); Sanction (3,950); Vendor Identification (2,810) |

---
