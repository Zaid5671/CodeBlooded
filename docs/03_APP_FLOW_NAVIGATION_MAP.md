# 03. App Flow & User Journey Map
> **MPLADS Audit Intelligence Platform — SIH 2026 (Problem Statement SIH26102)**  
> *Navigation structure, user flows, modal interactions, edge cases, and redirects.*

---

## 1. Complete Screen & View Inventory

| View ID | Title | Navigation Route | Primary Purpose |
|---|---|---|---|
| `#overview` | Overview Command Center | Sidebar Item 1 | Top-level KPI cards, Geo Risk Distribution, Audit Priority Donut |
| `#works` | Works Explorer | Sidebar Item 2 | Searchable repository of 79,220 works with pagination & column sorting |
| `#priority` | Audit Priority Queue | Sidebar Item 3 | Multi-dimensional risk triage (Critical, Standard, Low tabs) |
| `#alerts` | Alert Center | Sidebar Item 4 | Real-time audit signals, category filters, and review status tracker |
| `#expenditure` | Expenditure Intelligence | Sidebar Item 5 | Disbursement velocity timeline & utilization ratio analysis |
| `#compliance` | Statutory SLA Review | Sidebar Item 6 | 45-day statutory approval window compliance breakdown |
| `#duplicates` | Duplicate Works | Sidebar Item 7 | Record linkage pairs with side-by-side comparison modal |
| `#forecast` | Expenditure Outlook | Sidebar Item 8 | 6-month rolling outlay forecast with 95% confidence bounds |
| `#agencies` | Agency & Vendor Risk | Sidebar Item 9 | Implementing agency HHI concentration risk metrics |
| `#analytics` | Consolidated Risk Analytics | Sidebar Item 10 | Outlay vs Priority Score scatter plot engine |
| `#methodology` | AI Governance | Sidebar Item 11 | Complete technical specifications for Models M1–M5 |
| `#reports` | Reports & Export | Sidebar Item 12 | Verification report document pre-viewer API |
| `#view-404` | 404 Entity Not Found | Fallback View | Invalid route / non-existent work entity fallback |
| `#view-403` | 403 Access Denied | RBAC Restriction | Restricted administrative role warning screen |
| `#view-500` | 500 Pipeline Error | Exception State | Technical failure diagnostic screen with retry button |

---

## 2. Navigation Architecture & Entry Points

```
[Entry Point: Login Modal / Demo Mode]
             │
             ▼
   [Top Toolbar Controls]
   ├── Header Dataset Selector (LS18, LS17, RS, Combined) ──► Triggers API Refetch
   ├── Header Role Selector (Ministry, SNA, DA, MP, Judge) ──► Scope Adjustment
   ├── Spotlight Search Trigger (Cmd+K / Ctrl+K) ────────────► Opens Spotlight Modal
   └── Theme Toggle Button (Light ◄► Dark) ──────────────────► Re-styles UI & Plotly
             │
             ▼
   [Sidebar Navigation (12 Views)]
             │
             ▼
   [Global Filter Bar (State, District, Category, Priority)]
             │
             ▼
   [Main View Section Display & Interactive Modals/Drawers]
   ├── Work Investigation Drawer (`#work-detail-drawer`)
   ├── Duplicate Side-by-Side Comparison Modal (`#duplicate-modal`)
   ├── Legal Compliance Policy Modal (`#legal-modal`)
   ├── Support & Help Center Modal (`#help-modal`)
   └── Profile & Entitlements Drawer (`#account-drawer`)
```

---

## 3. Core User Journeys

### User Journey 1: Critical Priority Work Investigation
1. User logs in as **District Magistrate**.
2. Selects **Audit Priority Queue** from sidebar.
3. Clicks **Critical (1,635)** tab.
4. Clicks column header `Sanction Outlay` to sort descending (`▼`).
5. Clicks **Investigate ↗** on work `WS/MP18010/2025-2026/182165`.
6. Inspects cost anomaly signals, SLA approval gaps, and peer median outlay.
7. Clicks **Send WhatsApp Alert** -> Receives dispatch confirmation `DISPATCH_READY`.

### User Journey 2: Duplicate Work Candidate Review
1. User selects **Duplicate Works** from sidebar.
2. Filter bar set to **State = Andhra Pradesh**.
3. Clicks **Compare ↗** on top candidate pair.
4. Side-by-side modal renders Work A vs Work B metrics (Text Cosine: 94.2%, Amount Parity: 100.0%, Location Match: 98.5%).
5. Clicks **Reports & Export** to generate verification docket.

---

## 4. Edge Cases & Error States

- **No Matching Filter Results**: Displays inline empty state banner: *"No matching work records found in source repository."*
- **Offline Network Disconnection**: Triggers network toast alert: *"Network Connection Disconnected. Operating in Offline Cache Mode."*
- **Expired Token**: Displays `#session-expired-modal` prompting re-authentication.
