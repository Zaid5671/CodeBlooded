# 3-MODEL & ANALYTICAL PIPELINE DATA UTILIZATION REPORT
**Generated At**: 2026-09-07T15:19:11.668472

## Dataset Utilization Matrix across System Modules

| Dataset File | Chamber / Term | Rows | Model 1 (Dupl) | Model 2 (Cost) | Model 3 (Forecast) | Model 4 (Compliance) | Vendor/Agency | Module 6 (Repeated Exp) | Module 7 (Velocity) | Status / Technical Reason |
|---|---|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `Works Sanctioned_LokSabha_18.csv` | LS18 | 79,220 | USED | USED | USED (Agg) | USED | USED | USED | USED | Primary work-level entity dataset for Lok Sabha 18th |
| `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv` | LS18 | 84,172 | USED (Join) | USED | USED | N/A | USED | USED | USED | Primary expenditure & vendor transaction records for LS18 |
| `Works Recommended_LokSabha_18.csv` | LS18 | 107,024 | USED (Join) | N/A | N/A | USED | N/A | N/A | USED | Provides recommendation dates for 45-day compliance (Model 4) |
| `Works Completed_LokSabha_18.csv` | LS18 | 34,440 | USED (Join) | USED (Join) | N/A | N/A | N/A | N/A | USED | Provides project completion milestones and completion dates |
| `Allocated Limit for Honble MPs_LokSabha_18.csv` | LS18 | 544 | N/A | N/A | N/A | N/A | N/A | N/A | USED | MP-level allocation ceilings for fund entitlement tracking |
| `Amount consented for Calamity_LokSabha_18.csv` | LS18 | 13 | N/A | N/A | N/A | N/A | N/A | N/A | USED | Calamity fund consent tracking (statutory deductions) |
| `Works Sanctioned_LokSabha_17.csv` | LS17 | 92,117 | USED (Hist) | USED (Hist) | N/A | N/A | N/A | N/A | N/A | Historical baseline comparison and term entity profiling |
| `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv` | LS17 | 138,575 | N/A | N/A | USED (Hist) | N/A | N/A | N/A | N/A | Historical monthly expenditure time series training for Model 3 |
| `Works Recommended_LokSabha_17.csv` | LS17 | 94,749 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Historical recommendation records from 17th Lok Sabha |
| `Works Completed_LokSabha_17.csv` | LS17 | 71,256 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Historical completion records from 17th Lok Sabha |
| `Allocated Limit for Honble MPs_LokSabha_17.csv` | LS17 | 544 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Historical MP allocation limits from 17th Lok Sabha |
| `Works_Sanctioned_Rajya_Sitting.csv` | RS Sitting | 19,607 | CROSS_READY | N/A | N/A | N/A | N/A | N/A | N/A | Rajya Sabha sitting works; cross-house ready pending house linkage |
| `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv` | RS Sitting | 25,141 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Rajya Sabha sitting expenditure records |
| `Works_Recommended_Rajya_Sitting.csv` | RS Sitting | 25,240 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Rajya Sabha sitting recommendation records |
| `Works_Completed_Rajya_Sitting.csv` | RS Sitting | 9,979 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Rajya Sabha sitting completion records |
| `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv` | RS Sitting | 232 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Rajya Sabha MP allocated limits |
| `Amount_consented_for_Calamity_Rajya_Sitting.csv` | RS Sitting | 21 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Rajya Sabha calamity relief consents |

## Detailed Module-by-Module Data Pipeline

### MODEL 1: Record Linkage / Potential Double-Dipping Detection
- **Primary Dataset**: `data/original/LokSabha18/Works Sanctioned_LokSabha_18.csv` (79,220 works)
- **Features Used**: `Work description` (text TF-IDF representation), `Work category`, `State`, `Constituency`, `IDA (District)`, `Sanction Amount ( ₹ )`, `Sanction Date`
- **Candidate Generation**: Block-level spatial-category partitioning yielding 1,262 blocks and 6,954,003 raw candidate pairs, top-5,000 evaluated pairs.
- **Cross-House Integration**: Ingested Rajya Sabha sitting works architecture is prepared, with strict isolation to prevent cross-house contamination without verified MP house cross-linkage.

### MODEL 2: Unsupervised Cost Anomaly Detection (Isolation Forest + Peer IQR/MAD)
- **Primary Datasets**: `Works Sanctioned_LokSabha_18.csv` (79,220 works) ⟕ `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv` (84,172 records)
- **Features Used**: `sanction_amount`, `expenditure_amount`, `expenditure_ratio`, `peer_median_cost`, `cost_per_peer_ratio`, `payment_count`, `max_payment`, `max_payment_ratio`, `payment_variance`, `is_payment_concentrated`, `cost_overrun_pct`, `is_below_floor`
- **Detectors**: Multi-detector consensus between Peer Category-State IQR/MAD and 300-tree Isolation Forest.

### MODEL 3: Expenditure Time-Series Forecasting
- **Primary Datasets**: `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv` (84,172 records) + `Expenditure on Completed and On-going Works as on Date_LokSabha17.csv` (138,575 records)
- **Features Used**: Monthly aggregated disbursed expenditure amounts over continuous chronological monthly bins.
- **Evaluation**: 80% chronological train vs 20% held-out test evaluation against naïve previous-month and 3-month rolling average baselines.

### MODEL 4: Statutory Compliance & Speed
- **Primary Datasets**: `Works Recommended_LokSabha_18.csv` ⟕ `Works Sanctioned_LokSabha_18.csv`
- **Logic**: Computes duration between `Recommended date` and `Sanction Date` against the 45-day statutory guideline deadline.

### VENDOR & AGENCY RISK: Network Analytics & Payment Concentration
- **Primary Dataset**: `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv`
- **Logic**: Computes Herfindahl-Hirschman Index (HHI) concentration across implementing agencies and vendors.

### MODULE 6: Duplicate & Split Payment Detection
- **Primary Dataset**: `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv`
- **Logic**: Flags repeated identical transaction amounts to the same vendor within tight temporal windows.

### MODULE 7: Fund Utilization & Expenditure Velocity
- **Primary Datasets**: `Allocated Limit for Honble MPs_LokSabha_18.csv` ⟕ `Works Sanctioned_LokSabha_18.csv` ⟕ `Expenditure on Completed and On-going Works as on Date_LokSabha_18.csv`
- **Logic**: Computes MP-level fund utilization percentage and disbursement velocity ratios.

### MODEL 5: Multi-Signal Audit Priority Aggregator
- **Inputs**: Synthesizes output signals from Models 1, 2, 4, Vendor, Module 6, and Module 7 into a single normalized score $\in [0, 1]$ using validated weights summing to 1.00 (`0.30` Cost + `0.25` Delay + `0.25` Compliance + `0.10` Vendor + `0.10` Eligibility).
