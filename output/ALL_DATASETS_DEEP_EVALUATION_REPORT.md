# SIH26102 — ALL-DATASET DEEP FORENSIC & MODEL EVALUATION REPORT

**Audit Scope**: Multi-corpus comparative evaluation across Lok Sabha 18, Lok Sabha 17, Rajya Sabha Sitting, and Rajya Sabha Retired.

**Governance Notice**: *All identified patterns are statistical/financial anomalies requiring human administrative audit investigation. Not proof of fraud, crime, or wrongdoing.*


---

## 1. Multi-Corpus Inventory & Dimensions

| Dataset Identifier | Scope / Category | CSV Files | Total Scanned Rows | Clean Sanctioned Works |
| :--- | :--- | :---: | :---: | :---: |
| **`LokSabha18`** | 18th Lok Sabha (Active Corpus) | 6 | 305,413 | 79,220 |
| **`LokSabha17`** | 17th Lok Sabha (Historical Corpus) | 5 | 397,241 | 92,117 |
| **`RajyaSabha_Sitting`** | Rajya Sabha Sitting (Upper House) | 6 | 80,220 | 19,607 |
| **`RajyaSabha_Retired`** | Rajya Sabha Retired (Upper House) | 6 | 80,158 | 19,607 |
| **GRAND TOTAL** | **Entire MPLADS Corpus** | **23 Files** | **863,032 Rows** | **210,551 Works** |


---

## 2. Model 1: Record Linkage & Duplicate Work Evaluation Across Datasets

| Dataset | Works Sampled | High Risk (Cosine $\ge 85$) | Medium Risk (65–84) | Low Risk (<65) | Mean Max Sim | P95 Sim |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LokSabha18** | 15,000 | 1,018 | 847 | 1,135 | 71.56% | 100.00% |
| **LokSabha17** | 15,000 | 1,395 | 716 | 889 | 76.42% | 100.00% |
| **RajyaSabha_Sitting** | 15,000 | 1,598 | 486 | 916 | 76.81% | 100.00% |
| **RajyaSabha_Retired** | 15,000 | 1,598 | 486 | 916 | 76.81% | 100.00% |

> **Note**: High text similarities reflect repetitive municipal civic works (e.g. CC roads, solar lights, community halls) blocked by geographic district clusters.


---

## 3. Model 2: Cost Anomaly & Outlier Distribution Across Datasets

| Dataset | Evaluated Works | Anomalies Flagged | Anomaly Rate | Mean Sanction Cost | Median Sanction Cost | P95 Sanction Cost | Max Sanction Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **LokSabha18** | 79,219 | 3,703 | 4.67% | ₹527,221.95 | ₹300,000.00 | ₹1,500,000.00 | ₹49,740,000.00 |
| **LokSabha17** | 92,111 | 4,606 | 5.00% | ₹469,009.23 | ₹299,982.00 | ₹1,338,265.00 | ₹75,742,166.00 |
| **RajyaSabha_Sitting** | 19,606 | 923 | 4.71% | ₹874,629.24 | ₹500,000.00 | ₹2,500,000.00 | ₹73,500,000.00 |
| **RajyaSabha_Retired** | 19,606 | 923 | 4.71% | ₹874,629.24 | ₹500,000.00 | ₹2,500,000.00 | ₹73,500,000.00 |

---

## 4. Model 3: Execution Delay & Timeline Benchmarking Across Datasets

| Dataset | Evaluated Works | Median Duration | P90 Duration | Tukey Fence | Flagged Delayed Works | Delayed Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LokSabha18** | 79,219 | 327.0 days | 580.0 days | 896.0 days | 0 | 0.00% |
| **LokSabha17** | 92,116 | 917.0 days | 1033.0 days | 1243.5 days | 0 | 0.00% |
| **RajyaSabha_Sitting** | 19,606 | 417.0 days | 938.0 days | 1271.5 days | 0 | 0.00% |
| **RajyaSabha_Retired** | 19,606 | 417.0 days | 938.0 days | 1271.5 days | 0 | 0.00% |

---

## 5. Model 4: Statutory Compliance (45-Day Rule) Across Datasets

| Dataset | Evaluated Works | Compliant ($\le$ 45d) | Minor (46–90d) | Moderate (91–180d) | Severe (>180d) | Compliance Rate | Median Gap |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LokSabha18** | 79,219 | 23,337 | 20,937 | 21,611 | 13,334 | 29.46% | 79.0 days |
| **LokSabha17** | 92,116 | 30,929 | 16,501 | 19,963 | 24,723 | 33.58% | 86.0 days |
| **RajyaSabha_Sitting** | 19,606 | 6,474 | 5,176 | 4,673 | 3,283 | 33.02% | 69.0 days |
| **RajyaSabha_Retired** | 19,606 | 6,474 | 5,176 | 4,673 | 3,283 | 33.02% | 69.0 days |

---

## 6. Model 5: Misuse Priority Tiers & Risk Aggregation Across Datasets

| Dataset | Total Works | Critical Audit Priority | Standard Review | Low Priority | Score Range |
| :--- | :---: | :---: | :---: | :---: |
| **LokSabha18** | 79,220 | **2,352 (2.97%)** | 39,518 (49.88%) | 37,350 (47.15%) | [0.00, 0.90] |
| **LokSabha17** | 92,117 | **2,692 (2.92%)** | 46,007 (49.94%) | 43,418 (47.13%) | [0.00, 0.90] |
| **RajyaSabha_Sitting** | 19,607 | **583 (2.97%)** | 9,797 (49.97%) | 9,227 (47.06%) | [0.00, 0.90] |
| **RajyaSabha_Retired** | 19,607 | **583 (2.97%)** | 9,797 (49.97%) | 9,227 (47.06%) | [0.00, 0.90] |

---

## 7. Cross-House & Cross-Term Comparative Insights

1. **Upper House Quota Distribution**: Rajya Sabha sitting and retired datasets represent statewide nominations rather than single constituency geographic boundaries, creating broader distribution across implementing agencies.
2. **Historical vs Active Parity**: Lok Sabha 17 shows completed project lifecycle maturities, validating duration fences for Lok Sabha 18 ongoing works.
3. **Cross-House Linking Safeguards**: In accordance with MoSPI operational norms, cross-house work linkage remains gated under `PENDING_RAJYA_SABHA_DATA` for production matching to prevent false duplicate pairings across disjoint houses.
