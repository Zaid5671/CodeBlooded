# Master Architecture & Product Specification Suite
> **MPLADS Audit Intelligence Platform — SIH 2026 (Problem Statement SIH26102)**  
> *The Complete 6-Document Architectural Specification Suite*

---

## Architecture Documents Sitemap

```
docs/
├── 01_PRD_PRODUCT_REQUIREMENTS.md     # Document 01: Product vision, user personas, core features, success metrics
├── 02_TRD_TECHNICAL_REQUIREMENTS.md   # Document 02: Tech stack, Flask REST API specs, libraries, env vars, constraints
├── 03_APP_FLOW_NAVIGATION_MAP.md      # Document 03: 12 views, navigation tree, user journeys, modals, edge cases
├── 04_UI_UX_DESIGN_BRIEF.md           # Document 04: Neubrutalist design tokens, Space Grotesk typography, color palette
├── 05_BACKEND_SCHEMA_AUTH.md          # Document 05: Data model JSON schemas, RBAC access matrix, security encryption
└── 06_IMPLEMENTATION_PLAN.md          # Document 06: 6-phase build sequence, milestones, automated test criteria
```

---

## Executive Overview

1. **Document 01 — PRD**: Establishes the product north star for monitoring 79,220+ MPLADS works across India.
2. **Document 02 — TRD**: Defines the zero-dependency Python 3.13 Flask + Vanilla JS + Plotly.js tech stack.
3. **Document 03 — App Flow**: Maps every screen, user journey, modal interaction, and fallback error state (`404`, `403`, `500`).
4. **Document 04 — UI/UX Design Brief**: Details the Positivus Neubrutalist Lime Green CSS System (`#b9fd50`) with dark/light mode custom properties.
5. **Document 05 — Backend Schema**: Outlines JSON entity schemas for master works, misuse priority, double-dipping, statutory compliance, and vendor HHI concentration.
6. **Document 06 — Implementation Plan**: Tracks the 6 build phases leading to **136/136 pytest unit test pass rate**.
