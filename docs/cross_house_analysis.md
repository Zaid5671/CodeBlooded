# Cross-House Analysis & Rajya Sabha Identity Audit

## 1. RS Sitting vs RS Retired Source Identity Audit

An empirical source-level audit was conducted across `data/original/RajyaSabha_Sitting` and `data/original/RajyaSabha_Retired`.

### Source Files Inspected
- **Rajya Sabha Sitting**:
  - `Works_Sanctioned_Rajya_Sitting.csv`: 19,607 records
  - `Expenditure_on_Completed_and_On-going_Works_as_on_Date_Rajya_Sitting.csv`: 25,141 records
  - `Works_Completed_Rajya_Sitting.csv`: 9,979 records
  - `Works_Recommended_Rajya_Sitting.csv`: 25,240 records
  - `Allocated_Limit_for_Honble_MPs_Rajya_Sabha.csv`: 232 records
  - `Amount_consented_for_Calamity_Rajya_Sitting.csv`: 21 records

- **Rajya Sabha Retired**:
  - `Works Sanctioned.csv`: 19,607 records
  - `Expenditure on Completed and On-going Works as on Date.csv`: 25,130 records
  - `Works Completed.csv`: 9,964 records
  - `Works Recommended.csv`: 25,204 records
  - `Allocated Limit for Honble MPs (1).csv`: 232 records
  - `Amount consented for Calamity.csv`: 21 records

### Empirical Identity Audit Results
- `s_ids` (Rajya Sabha Sitting unique Work IDs): **19,607**
- `r_ids` (Rajya Sabha Retired unique Work IDs): **19,607**
- `intersection_count`: **19,607** (100% Work ID overlap)
- `sitting_only_count`: **0**
- `retired_only_count`: **0**
- `union_count`: **19,607**
- `exact_identical_rows`: **19,606** out of 19,607 rows (1 row differs in `Work Status`: Sitting="Work partially Completed" vs Retired="Physical Inspection")

### Architectural Conclusion
`RS_SITTING` and `RS_RETIRED` datasets represent two status snapshots/views of the exact same 19,607 Rajya Sabha work portfolio entities. 
They must **NOT** be reported as 39,214 distinct work entities.

---

## 2. Source ID Preservation & Key Schema

To avoid collisions across corpora while preserving source data integrity:
- `source_work_id`: Preserves the raw extracted clean work ID for each corpus without replacement.
- `canonical_work_key`: Deterministic source-qualified representation computed as `CORPUS + "|" + source_work_id` (e.g., `LS18|WS/MP620/2024-2025/133166`).
- **Collision Fencing**: Fences `LS18|source_work_id`, `LS17|source_work_id`, `RS_SITTING|source_work_id`, and `RS_RETIRED|source_work_id` to guarantee 0 silent collisions across all 210,551 corpus records.

---

## 3. Combined Master Count Breakdown

| Metric | Record Count | Description |
|---|---|---|
| **Total Corpus Records** | **210,551** | Sum of all rows across LS18 (79,220), LS17 (92,117), RS_SITTING (19,607), and RS_RETIRED (19,607). |
| **Unique Source Works** | **190,944** | Distinct work entities across all corpora (LS18: 79,220 + LS17: 92,117 + RS Unique: 19,607). |
| **Overlapping Records** | **19,607** | RS_RETIRED records that overlap 100% in Work ID with RS_SITTING. |

---

## 4. Cross-House Duplicate Language & Safety

Candidate pairs identified across chambers or corpora are tagged with:
`"POTENTIAL CROSS-HOUSE DUPLICATE — REQUIRES REVIEW"`

Similarity matches are strictly presented as decision-support candidate pairs requiring human review and are never labeled as "same work", "confirmed duplicate", or "duplicate funding".
