# SIH26102 — Final Production Dataset Contract Specifications

This contract defines the authoritative data schema, row counts, monetary units, date fields, primary IDs, null policies, and limitations across all active datasets in the MPLADS Audit Intelligence Platform (`SIH26102`).

---

## 1. DATASET: Lok Sabha 18th Term (Active)

- **SOURCE**: `data/original/LokSabha18/`
- **HOUSE**: Lok Sabha
- **TERM**: 18th Term (Active 2024–Present)
- **GRAIN**: Individual Sanctioned Work Entity
- **ROW COUNT**:
  - `Works Sanctioned_LokSabha_18.csv`: **79,220 rows** (12 columns)
  - `Works Recommended_LokSabha_18.csv`: **107,024 rows** (11 columns)
  - `Works Completed_LokSabha_18.csv`: **34,440 rows** (11 columns)
  - `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv`: **84,172 rows** (11 columns)
  - `Allocated Limit for Honble MPs_LokSabha_18.csv`: **544 rows** (5 columns)
- **UNIQUE WORKS**: **79,220 Master Works**
- **TRANSACTION GRAIN**: Work-level disbursement records in Expenditure CSV (84,172 transactions)
- **PRIMARY ID**: `Work ID` / `WORK` (Canonical alphanumeric key, e.g., `LS18-WORK-000001`)
- **DATE FIELDS**: `Recommended date`, `Sanction Date`, `Completion Date`, `Expenditure Date`
- **MONEY UNITS**: **Indian Rupees (₹)**. Verified: Max sanctioned = ₹7.57 Cr, Median = ₹3.0 Lakh.
- **NULL POLICY**: Explicit missingness handling; `NULL != 0.0`. Missing sanction amounts imputed via peer state/category medians with `is_imputed` missingness flags.
- **LINKAGE KEYS**: `Work ID`, `State + District + Constituency`, `Implementing Agency (IDA)`
- **KNOWN LIMITATIONS**: Ongoing term; completion certificates still accumulating.

---

## 2. DATASET: Lok Sabha 17th Term (Historical Baseline)

- **SOURCE**: `data/original/LokSabha17/`
- **HOUSE**: Lok Sabha
- **TERM**: 17th Term (Historical 2019–2024)
- **GRAIN**: Individual Sanctioned Work Entity
- **ROW COUNT**:
  - `Works Sanctioned_LokSabha_17.csv`: **92,117 rows** (12 columns)
  - `Works Recommended_LokSabha_17.csv`: **94,749 rows** (11 columns)
  - `Works Completed_LokSabha_17.csv`: **71,256 rows** (11 columns)
  - `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv`: **138,575 rows** (11 columns)
  - `Allocated Limit for Honble MPs_LokSabha_17.csv`: **544 rows** (5 columns)
- **UNIQUE WORKS**: **92,117 Master Works**
- **TRANSACTION GRAIN**: 138,575 expenditure disbursement records
- **PRIMARY ID**: `Work ID` / `WORK` (Prefix `LS17-`)
- **DATE FIELDS**: `Recommended date`, `Sanction Date`, `Completion Date`, `Expenditure Date`
- **MONEY UNITS**: **Indian Rupees (₹)**. Verified: Mean outlay = ₹4.54 Lakh.
- **NULL POLICY**: `NULL != 0.0`. Missing fields preserved with explicit flag tags.
- **LINKAGE KEYS**: `Work ID`, `State + District + Constituency`
- **KNOWN LIMITATIONS**: Complete historical term; useful for baseline peer statistics.

---

## 3. DATASET: Rajya Sabha Sitting (Active Upper House)

- **SOURCE**: `data/original/RajyaSabha_Sitting/`
- **HOUSE**: Rajya Sabha
- **TERM**: Sitting Members
- **GRAIN**: Individual Sanctioned Work Entity
- **ROW COUNT**:
  - `Works_Sanctioned_Rajya_Sitting.csv`: **19,607 rows** (12 columns)
  - `Works_Recommended_Rajya_Sitting.csv`: **25,240 rows** (11 columns)
  - `Works_Completed_Rajya_Sitting.csv`: **9,979 rows** (11 columns)
  - `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv`: **25,141 rows** (11 columns)
- **UNIQUE WORKS**: **19,607 Master Works**
- **TRANSACTION GRAIN**: 25,141 disbursement records
- **PRIMARY ID**: `Work ID` / `WORK` (Prefix `RS-SIT-`)
- **DATE FIELDS**: `Recommended date`, `Sanction Date`, `Completion Date`, `Expenditure Date`
- **MONEY UNITS**: **Indian Rupees (₹)**.
- **NULL POLICY**: Explicit null isolation.
- **LINKAGE KEYS**: `Work ID`, `State + Nodal District`
- **KNOWN LIMITATIONS**: Rajya Sabha MPs recommend works state-wide; constituency bound to assigned nodal district.

---

## 4. DATASET: Rajya Sabha Retired (Historical Upper House)

- **SOURCE**: `data/original/RajyaSabha_Retired/`
- **HOUSE**: Rajya Sabha
- **TERM**: Retired Members
- **GRAIN**: Individual Sanctioned Work Entity
- **ROW COUNT**:
  - `Works Sanctioned.csv`: **19,607 rows** (12 columns)
  - `Works Recommended.csv`: **25,204 rows** (11 columns)
  - `Works Completed.csv`: **9,964 rows** (11 columns)
  - `Expenditure on Completed and On-going Works as on Date.csv`: **25,130 rows** (11 columns)
- **UNIQUE WORKS**: **19,607 Master Works**
- **TRANSACTION GRAIN**: 25,130 disbursement records
- **PRIMARY ID**: `Work ID` / `WORK` (Prefix `RS-RET-`)
- **DATE FIELDS**: `Recommended date`, `Sanction Date`, `Completion Date`, `Expenditure Date`
- **MONEY UNITS**: **Indian Rupees (₹)**.
- **NULL POLICY**: Explicit null isolation.
- **LINKAGE KEYS**: `Work ID`, `State + Nodal District`
- **KNOWN LIMITATIONS**: Historical term records.

---

## 5. DATASET: Combined Multi-Corpus Master

- **SOURCE**: Multi-corpus compilation of LS18, LS17, RS Sitting, RS Retired
- **COMPOSITION**: Full multi-parliamentary compilation preserving source house, term, and corpus origin tags (`house`, `term`, `corpus_name`).
- **TOTAL SCAN**: **863,032 raw rows** across all 23 source files.
- **PRIMARY AUDIT BASELINE**: **79,221 Master Sanctioned Works** (LS18 Primary Active Scan) with total outlay of **₹4,176.6 Cr**.
- **MONEY CONVERSION SANITY**: All monetary values normalized to **Rupees (₹)**; converted to **₹ Cr** ($/\,10,000,000$) or **Lakh ₹** ($/\,100,000$) exclusively for UI display.
