# MPLADS Audit Intelligence — Immersive Product Design System Specification
## SIH 2026 — SIH26102 — CodeBlooded
**Document Status**: Production Design Specification
**Visual Language**: Deep Black Environment + 3D WebGL Particle System + Liquid Glass Controls + HIG Typography

---

### 1. Visual Identity & Design Philosophy

The **MPLADS Audit Intelligence Platform** is designed as a cinematic, immersive product experience that blends Apple HIG desktop precision with a 3D WebGL visualization engine.

#### Core Principles:
1. **Deep Black Environment**:
   - Canvas: `#030712` (Deep Space Black)
   - Content Surface: `#0f172a` / `#1e293b` (Slate Glass)
   - Border: `rgba(255, 255, 255, 0.1)`
2. **3D WebGL Particle Engine (Three.js)**:
   - GPU-accelerated particle cloud with 3,000 instanced points representing MPLADS works activity.
   - Morphing across 6 analytical states (National Network, Geographic Distribution, Signal Chaos, Priority Convergence, Financial Flow, Forecast Trajectory).
3. **Scroll-Driven Analytical Narrative**:
   - Scroll position dynamically interpolates particle positions and opacity in sync with screen sections ("See the whole system", "Follow the money", "Find what needs review", "Know where to look first").
4. **Functional Layer vs Solid Content Layer**:
   - Liquid Glass (`backdrop-filter: blur(25px)`) applied to Top Toolbar, Floating Navigation Sidebar, Cmd+K Spotlight Modal, and Filter Popovers.
   - Clean, solid high-contrast surfaces for Data Tables, Plotly Charts, and Audit Evidence to guarantee 100% legibility.

---

### 2. Particle Morph States Specification

| State | Name | Visual Behavior | Semantic Palette |
| :--- | :--- | :--- | :--- |
| **State 1** | National Network | Dense 3D sphere/torus network of interconnected works | White `#FFFFFF` + Sapphire `#38BDF8` |
| **State 2** | Geographic Distribution | Abstract 2D/3D map layout representing works across India | Cool Slate `#94A3B8` + Accent `#2563EB` |
| **State 3** | Signal Chaos | Particles scatter into high-entropy outlier clouds | Warning Amber `#F59E0B` + Crimson `#EF4444` |
| **State 4** | Priority Convergence | Particles assemble into 3 distinct priority rings | Crimson `#EF4444` (Critical), Amber `#F59E0B` (Standard), Emerald `#10B981` (Low) |
| **State 5** | Financial Flow | Flowing horizontal stream representing monthly expenditure | Emerald `#10B981` + Cyan `#06B6D4` |
| **State 6** | Forecast Trajectory | Forward-projecting curve into 6-month expected horizon | Cyan `#38BDF8` with shaded bounds |

---

### 3. Typography & Composition Rules

- **Headline Font**: `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif`
- **Body Font**: `"SF Pro Text", "Fira Sans", sans-serif`
- **Data Font**: `"SF Mono", "Fira Code", monospace` (enforcing `font-variant-numeric: tabular-nums`)
- **50/50 Cinematic Layout**: Left side houses large white display text and narrative controls; Right side presents interactive 3D WebGL visualization and clean analytical panels.
