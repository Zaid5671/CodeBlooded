# 04. UI/UX Design Brief & Interaction Guide
> **MPLADS Audit Intelligence Platform — SIH 2026 (Problem Statement SIH26102)**  
> *Visual direction, typography, design tokens, component specifications, and accessibility.*

---

## 1. Aesthetic Direction & Inspiration

- **Aesthetic**: Positivus Neubrutalist System inspired by macOS Tahoe, Apple Human Interface Guidelines, and enterprise government monitoring consoles.
- **Visual Style**: Heavy 2px solid borders (`#191919`), hard drop shadows (`box-shadow: 0 4px 0 #191919`), vibrant lime accent highlights (`#b9fd50`), and crisp high-contrast readability.

---

## 2. Color Palette & Design Tokens

```css
:root {
    /* Color Tokens */
    --accent-lime: #b9fd50;        /* Primary Brand Accent */
    --accent-blue: #3b82f6;        /* Info / Link Accent */
    --accent-green: #22c55e;       /* Healthy Status */
    --accent-yellow: #f59e0b;      /* Warning Status */
    --accent-red: #ef4444;         /* Destructive / Critical Status */
    
    /* Surface Tokens (Light Mode) */
    --canvas-bg: #f8fafc;
    --card-bg: #ffffff;
    --text-main: #191919;
    --text-secondary: #64748b;
    --border-color: #191919;
    --shadow-hard: 0 4px 0 #191919;
}

body.dark-mode {
    /* Surface Tokens (Dark Mode) */
    --canvas-bg: #141414;
    --card-bg: #1e1e1e;
    --text-main: #ffffff;
    --text-secondary: #94a3b8;
    --border-color: #333333;
    --shadow-hard: 0 4px 0 #000000;
}
```

---

## 3. Typography System

| Usage | Font Family | Size | Weight | Line Height |
|---|---|---|---|---|
| **Headings & Display** | `Space Grotesk`, sans-serif | 1.1rem – 1.8rem | 700 / 800 | 1.2 |
| **Body & UI Controls** | `Plus Jakarta Sans`, sans-serif | 0.85rem – 0.95rem | 500 / 600 | 1.5 |
| **Monospace / Code / IDs** | `Fira Code`, monospace | 0.8rem – 0.85rem | 500 | 1.4 |

---

## 4. Key UI Components & Layout Specs

- **Buttons**: Heavy 2px solid border, 6px border-radius, hard shadow, active push transition (`transform: translateY(2px)`).
- **Cards**: Fenced border, hard shadow, subtle padding (`16px – 24px`), responsive grid system (`grid-4`, `grid-3`, `grid-2`).
- **Pill Badges (`.badge-pill`)**: Rounded full radius (`999px`), bold uppercase font (`0.7rem`), custom risk background colors (`badge-lime`, `badge-critical`, `badge-warning`, `badge-neutral`).
- **Data Tables (`.data-table`)**: Sticky header, hover highlight, clickable sort headers (`data-sort-col`), truncated description cells.

---

## 5. Accessibility & Responsive Design

- **GIGW 3.0 & WCAG 2.1 AA Compliance**: Contrast ratios > 7:1 for text on lime/dark surfaces.
- **Keyboard Navigation**: Full `Tab` focus support, Spotlight search trigger via `Cmd+K` / `Ctrl+K`, modal close via `ESC`.
- **Responsive Layout**: Fluid breakpoints adapting from 4-column desktop grid down to 1-column mobile view.
