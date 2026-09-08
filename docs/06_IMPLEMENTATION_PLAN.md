# 06. Implementation Plan & Build Sequence
> **MPLADS Audit Intelligence Platform — SIH 2026 (Problem Statement SIH26102)**  
> *The Build Roadmap: Numbered phases, milestones, testing criteria, and deployment.*

---

## Phase 1: Environment Setup & Data Pipeline Foundation
- **Goals**: Ingest raw MPLADS CSV datasets across 23 parliamentary files, clean canonical work IDs, build state/constituency indexes, and pre-compute pipeline cache.
- **Completion Criteria**: `output/scored_sanctioned_works.json.gz` generated with 79,220 master work entities.

## Phase 2: Machine Learning Engine Implementation (Models M1–M5)
- **Goals**: Implement M1 Isolation Forest & Peer IQR baseline, M2 TF-IDF sentence-transformer cosine linkage, M3 45-day SLA compliance detector, M4 6-month forecast model, and M5 unified audit priority aggregator.
- **Completion Criteria**: Models produce validated risk scores (0–100) saved to `output/misuse_priority_results.json` and `output/double_dipping_results.json`.

## Phase 3: Flask REST API Backend Engine (`backend/app.py`)
- **Goals**: Build Flask API server handling dataset query parameter (`LokSabha18`, `LokSabha17`, `RajyaSabha`, `Combined`), search, pagination, report exports, and WhatsApp dispatch webhooks.
- **Completion Criteria**: REST endpoints return JSON payloads in <100ms on `http://127.0.0.1:5052/`.

## Phase 4: Production Frontend UI/UX Redesign
- **Goals**: Build 12 core views using Neubrutalist Lime Green CSS system, dynamic Plotly visualizers, Spotlight `Cmd+K` search, Work Drawer, and Side-by-Side Comparison modal.
- **Completion Criteria**: 100% interactive views with dynamic chart re-rendering.

## Phase 5: Production UX States & Legal Compliance Infrastructure
- **Goals**: Implement DPDP Act 2023 Privacy Policy, Terms, Cookie Preferences banner, Security Disclosure, Accessibility Statement, and 404/403/500 error fallbacks.
- **Completion Criteria**: All legal tabs functional and system fallback screens active.

## Phase 6: Verification, Testing & Documentation
- **Goals**: Execute bytecode compilation and automated test suite.
- **Completion Criteria**: **136/136 pytest unit test suites passing** (`python3 -m pytest tests/`).
