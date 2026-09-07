# MPLADS Audit Intelligence — macOS Tahoe Liquid Glass Design System Specification
## SIH 2026 — SIH26102 — CodeBlooded
**Document Status**: Production Design Specification
**Design Intelligence Engine**: `ui-ux-pro-max` + Apple Human Interface Guidelines (HIG)

---

### 1. Visual Identity & Design Philosophy

The **MPLADS Audit Intelligence Platform** is designed as a desktop-first, government-grade macOS application. It eschews generic SaaS templates, AI dashboard clichés, and glassmorphism over-saturation in favor of a restrained, calm, authoritative, and evidence-focused desktop experience.

#### Core Principles:
1. **Material Layering (HIG Liquid Glass Rule)**:
   - **Functional Layers** (Navigation Sidebar, Application Header/Toolbar, Cmd+K Spotlight Modal, Filter Popovers, Segmented Controls, Toast Notifications) use **Liquid Glass Material** with controlled backdrop blur (`backdrop-filter: blur(20px)`), dynamic optical borders, and subtle lensing.
   - **Content Layers** (Data Tables, Analytical Charts, Audit Evidence Panels, Work Detail Drawers, Long-form Text) sit on **Clean, Solid Content Surfaces** with high legibility and zero visual noise.
2. **Concentric Geometry**:
   - Window Radius: `16px`
   - Card / Container Radius: `12px`
   - Control / Button Radius: `8px`
   - Inner Pill / Badge Radius: `6px`
3. **Ambient Liquid Light Environment**:
   - Subtle, slow-moving orbital background light fields (blur: `120px`, opacity: `0.12 - 0.18`) that respond softly to pointer position and view navigation without distracting from readability.
4. **Strict Non-Fabrication & Truthful Reporting**:
   - Zero synthetic fraud claims (`"Potential anomaly — requires audit review"`).
   - Missing data rendered as `"Data unavailable in source record"` (never converted to 0).

---

### 2. Typography System

- **Primary Font Stack**: `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Fira Sans", system-ui, sans-serif`
- **Monospace Font Stack**: `"SF Mono", "Fira Code", Menlo, Monaco, Consolas, monospace`
- **Numeric Tabular Display**: All financial, score, and statistical columns enforce `font-variant-numeric: tabular-nums;`.

| Scale | Size | Line Height | Weight | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Display** | 28px (1.75rem) | 1.2 | 700 (Bold) | Major Section Headers |
| **Page Title** | 20px (1.25rem) | 1.3 | 600 (SemiBold) | Application Toolbar Title |
| **Section Header**| 15px (0.9375rem)| 1.4 | 600 (SemiBold) | Card & Panel Titles |
| **Body** | 13px (0.8125rem)| 1.5 | 400 (Regular) | Primary Content & Tables |
| **Metadata** | 11px (0.6875rem)| 1.4 | 500 (Medium) | Badges, Timestamps, Labels |

---

### 3. Material & Color Palette

#### Light Mode (Primary Desktop Mode):
- **Window Base Canvas**: `#F8FAFC`
- **Content Surface**: `#FFFFFF` (Solid with `1px solid rgba(226, 232, 240, 0.8)`)
- **Liquid Glass Navigation**: `rgba(255, 255, 255, 0.72)` + `backdrop-filter: blur(25px) saturate(180%)`
- **Liquid Glass Border**: `rgba(255, 255, 255, 0.8)` top/left highlight, `rgba(203, 213, 225, 0.5)` bottom/right shadow
- **Primary Text**: `#0F172A`
- **Muted Text**: `#64748B`
- **Accent Blue**: `#2563EB` (Selection, Active Navigation, Key CTA)

#### Dark Mode:
- **Window Base Canvas**: `#0B1120`
- **Content Surface**: `#1E293B` (Solid with `1px solid rgba(51, 65, 85, 0.6)`)
- **Liquid Glass Navigation**: `rgba(15, 23, 42, 0.75)` + `backdrop-filter: blur(25px) saturate(180%)`
- **Liquid Glass Border**: `rgba(255, 255, 255, 0.12)` top/left highlight, `rgba(0, 0, 0, 0.4)` bottom/right
- **Primary Text**: `#F8FAFC`
- **Muted Text**: `#94A3B8`
- **Accent Blue**: `#38BDF8`

#### Semantic Risk Colors (WCAG AA High-Contrast):
- **Critical Audit Priority**: `#EF4444` (Crimson)
- **Standard Review**: `#F59E0B` (Amber)
- **Low Priority / Healthy**: `#10B981` (Emerald)
- **Informational / Neutral**: `#64748B` (Slate)

---

### 4. Interactive Components & Functional Liquid Glass

1. **Top Application Toolbar (`GlassToolbar`)**:
   - Fixed height (`52px`), floating glass material.
   - Left: Compact MPLADS Mark + "Audit Intelligence".
   - Center: Contextual Breadcrumb & Page Title.
   - Right: Cmd+K Search trigger (`GlassSearch`), Global Filter popover button (`GlassFilterBar`), Alert Center indicator, Persona switcher.
2. **Mac Sidebar (`GlassNavigation`)**:
   - Width: `240px`, collapsible to `64px` on tablet/compact widths.
   - Sectioned Navigation:
     - **Main**: Overview, Works Explorer, Audit Queue, Alert Center
     - **Monitoring**: Expenditure, Compliance Review, Delay & Execution
     - **Intelligence**: Duplicate Works, Expenditure Forecast, Agency Risk, Risk Analytics
     - **Governance**: AI & Methodology, Audit Reports
3. **Mac Spotlight Search Overlay (`GlassSpotlight`)**:
   - Triggered by `Cmd+K` / `Ctrl+K` or clicking search bar.
   - Liquid glass overlay card with keyboard navigation (Up/Down/Enter/Esc).
   - Real-time instant query matching across Work IDs, Descriptions, Districts, MPs, Agencies.
4. **Data Tables & Inspection Drawers**:
   - Clean, non-glass tabular content with sticky headers, subtle row hover highlighting, and direct row click opening the **Work Investigation Drawer**.

---

### 5. Motion & Interaction Rules

- **Spring Physics**: `cubic-bezier(0.16, 1, 0.3, 1)` for smooth, responsive desktop feel.
- **Duration**: `150ms` for buttons/hovers, `250ms` for drawers/modals, `350ms` for view transitions.
- **Ambient Light Orbs**: 2 slow background light blobs with `transform: translate3d()` and `pointer-events: none` running at 60fps.
- **Reduced Motion (`prefers-reduced-motion: reduce`)**: Background light animation disabled, modal fade duration reduced to 50ms with zero scale transform.
