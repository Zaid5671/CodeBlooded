# 05. Backend Schema & Auth Architecture
> **MPLADS Audit Intelligence Platform — SIH 2026 (Problem Statement SIH26102)**  
> *Data structure, JSON schemas, auth logic, RBAC matrix, and security relationships.*

---

## 1. Primary Data Models & Schemas

### Table 1: `master_sanctioned_works`
```json
{
  "work_id": "string (PK, e.g. WS/MP620/2024-2025/133166)",
  "clean_work_id": "string",
  "mp_name": "string",
  "state": "string (Indexed)",
  "constituency": "string (Indexed)",
  "work_description": "string",
  "standardized_category": "string",
  "sanctioned_amount": "number (float)",
  "actual_expenditure": "number (float)",
  "expenditure_record_count": "integer",
  "recommendation_to_sanction_days": "integer",
  "compliance": {
    "approval_gap_days": "float",
    "compliance_severity": "string (COMPLIANT | MINOR_GAP | MODERATE_GAP | SEVERE_BREACH)",
    "signal_compliance": "boolean"
  },
  "peer_statistics": {
    "median": "float",
    "iqr": "float",
    "robust_deviation": "float"
  },
  "signals": {
    "cost_overrun": "object",
    "peer_iqr": "object",
    "isolation_forest": "object"
  },
  "consensus": {
    "priority_score": "integer (0-100)",
    "risk_level": "string (CRITICAL | STANDARD | LOW)"
  }
}
```

### Table 2: `misuse_priority_records`
```json
{
  "clean_work_id": "string (FK -> master_sanctioned_works.work_id)",
  "display_score": "float (0.0 - 100.0)",
  "misuse_priority_score": "float (0.0 - 1.0)",
  "audit_priority": "string (CRITICAL_AUDIT_PRIORITY | STANDARD_REVIEW | LOW_PRIORITY)",
  "fired_major_dimensions": "array of strings",
  "fired_supporting_dimensions": "array of strings",
  "cost_signal": "boolean",
  "compliance_signal": "boolean",
  "delay_signal": "boolean",
  "inadmissible_work_signal": "boolean",
  "vendor_concentration_risk": "boolean",
  "combined_evidence": "array of strings"
}
```

### Table 3: `double_dipping_pairs`
```json
{
  "pair_id": "string (PK)",
  "source_work_id": "string (FK)",
  "matched_work_id": "string (FK)",
  "risk_score": "integer (0-100)",
  "similarity_score": "float",
  "work_a": "object (Embedded Work A)",
  "work_b": "object (Embedded Work B)",
  "features": {
    "semantic_similarity": "float"
  },
  "similarity_breakdown": {
    "amount_similarity_pct": "float",
    "location_similarity_pct": "float"
  }
}
```

---

## 2. Role-Based Access Control (RBAC) Matrix

| User Role | View Perms | Query Scope | WhatsApp Dispatch | Report Export |
|---|---|---|---|---|
| **Ministry (MoSPI)** | All 12 Views | National (All States/Districts) | Full Access | Full Access |
| **State Nodal Authority (SNA)** | All 12 Views | State-Wide (Selected State) | State Officers | Full Access |
| **District Authority (DA)** | All 12 Views | District Scope | Field Officers | Full Access |
| **MP / Constituency Office** | All 12 Views | Constituency Scope | Read-Only | Full Access |
| **SIH Judge / Evaluator** | All 12 Views | Full Unrestricted Access | Simulated Mode | Full Access |

---

## 3. Data Encryption & Security Standards

- **In-Transit**: TLS 1.3 encryption for REST API responses.
- **At-Rest**: Pre-computed gzip compression (`.json.gz`) with file integrity checksums.
- **Sanitization**: All search queries and parameter inputs sanitized via `urllib.parse` and regex filtering.
