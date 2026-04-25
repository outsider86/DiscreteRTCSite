# continuousRTC.svg — Full Implementation & Style Guide

Use this as the reference style for all method figures.

## Overall Structure

```
Canvas viewBox="50 74 766 254"
├── Background rect (fills viewBox)
├── LEFT: Main figure (nested SVG)
│   ├── Title
│   ├── Top action chunk (Before Inference)
│   ├── Arrow + Π_GDM
│   ├── Bottom action chunk (After Inference)
│   ├── Dashed boundary lines
│   └── Bottom annotations (equations + bracket labels)
└── RIGHT: 3 subfigures (nested SVGs)
    ├── TOP (1×2): Subfigure (a)+(b) — noise comparison
    ├── BOTTOM-LEFT: Subfigure (c) — guidance plot
    └── BOTTOM-RIGHT: Subfigure (d) — bar chart
```

## Canvas & Background

- **viewBox**: `"50 74 766 254"` — tightly cropped to content
- **Background**: `#f4f4f0` (warm off-white)
- **Font**: `'Helvetica Neue', Helvetica, Arial, sans-serif` (global default)

## Composition: Nested SVGs

All panels are embedded as `<svg>` elements with `preserveAspectRatio="xMidYMid meet"` — content scales uniformly without distortion and centers within the allocated box.

| Panel | x | y | width | height | viewBox |
|-------|---|---|-------|--------|---------|
| Main figure | 0 | 0 | 510 | 420 | `30 0 590 290` |
| Subfig (a)+(b) | 480 | 98 | 335 | 109 | `0 0 520 170` |
| Subfig (c) | 480 | 213 | 165 | 108 | `0 0 260 170` |
| Subfig (d) | 650 | 213 | 165 | 108 | `0 0 260 170` |

**Key**: bottom two subfigure widths (165+5+165=335) match the top subfigure width (335) for alignment.

## Color Palette

| Role | Color | Usage |
|------|-------|-------|
| Deep green | `#2e8b57` | Trusted/inferred actions |
| Green transition 1 | `#5a9e45` | Gradient cell 3 |
| Green transition 2 | `#8bb832` | Gradient cell 4 / uniform noise |
| Green-yellow transition | `#bdd01e` | Gradient cell 5 |
| Yellow | `#e8d810` | Noisy/new actions |
| Gray bar | `#a0a8a0` | "Original" bar in chart |
| Blue curve | `#4A7DC0` | Guidance weight curve |
| Background | `#f4f4f0` | Canvas background |
| Subfigure fill | `#eeeee8` | Rounded rect interior |
| Text / labels | `#333` | Primary text color |
| Arrow / strokes | `#555` | Arrows and model labels |
| Borders | `#888` | Cell dividers and outer borders |
| Dashed lines | `#777` | Section boundary dashes |
| Subfigure border | `#aaa` | Rounded rect stroke |
| Dashed divider | `#999` | Internal panel dividers |

## Typography

| Element | Font | Size | Weight | Style | Color |
|---------|------|------|--------|-------|-------|
| Main title | Times New Roman / CMU Serif / Georgia, serif | 20 | bold | — | `#333` |
| Before/After Inference | Helvetica Neue (default) | 13 | bold | — | `#333` |
| Π_GDM | default | 15 (Π) / 11 (GDM) | — | italic (Π) | `#444` |
| Equation vars (d, H−d−s, s) | Times New Roman / serif | 11 | bold | italic | `#333` |
| Bracket labels | default | 10 | bold | italic | `#333` |
| Subfigure panel labels | default | 11 | bold | — | `#333` |
| Subfigure descriptions | default | 9 | bold | — | `#333` |
| Y-axis labels | default | 10 | bold | — | `#333` |
| X-axis labels (bar chart) | default | 9 | bold | — | `#333` |

## Action Chunk Pattern (1×8 strip)

### Main figure chunks (48×48 cells)
- 8 cells, each `width="48" height="48"`, flush (no gaps, no rounded corners)
- Outer border: `stroke="#888" stroke-width="1.5"`
- Internal dividers: `stroke="#888" stroke-width="1.2"`
- **Top chunk colors** (left to right):
  - Cells 1–2: `#2e8b57` (frozen)
  - Cell 3: `#5a9e45` (transition)
  - Cell 4: `#8bb832` (transition)
  - Cell 5: `#bdd01e` (transition)
  - Cells 6–8: `#e8d810` (noisy)
- **Bottom chunk**: all 8 cells `#2e8b57`

### Subfigure chunks (26×26 cells)
- Same pattern but smaller: `width="26" height="26"`
- Outer border: `stroke="#888" stroke-width="1.2"`
- Internal dividers: `stroke="#888" stroke-width="1"`

## Arrow Markers

All arrowheads use `refX` set to roughly half the marker width (not full width) so the arrowhead extends forward past the line endpoint, covering the arrow body.

```svg
<!-- Standard downward arrow (main figure) -->
<marker id="arrowhead" markerWidth="7" markerHeight="5" refX="4" refY="2.5" orient="auto">
  <polygon points="0 0, 7 2.5, 0 5" fill="#555"/>
</marker>

<!-- Subfigure arrows -->
<marker id="arrow" markerWidth="7" markerHeight="5" refX="4" refY="2.5" orient="auto">
  <polygon points="0 0, 7 2.5, 0 5" fill="#555"/>
</marker>

<!-- Axis arrows (smaller) -->
<marker id="axisArrow" markerWidth="6" markerHeight="4" refX="3" refY="2" orient="auto">
  <polygon points="0 0, 6 2, 0 4" fill="#333"/>
</marker>

<!-- Curved arrow (bar chart annotation) -->
<marker id="curveArrow" markerWidth="7" markerHeight="5" refX="4" refY="2.5" orient="auto">
  <polygon points="0 0, 7 2.5, 0 5" fill="#555"/>
</marker>
```

## Dashed Lines

- **Section boundaries** (spanning both chunks): `stroke="#777" stroke-width="1.2" stroke-dasharray="5,4"`
- **Subfigure internal divider**: `stroke="#999" stroke-width="1" stroke-dasharray="5,4"`
- **Plot dashed boundaries**: `stroke="#888" stroke-width="1" stroke-dasharray="4,3"`

## Bracket Annotations

Bottom of main figure, below both chunks:
- Horizontal line: `stroke="#333" stroke-width="1"`
- Vertical tick marks at ends: 8px tall (y±4), `stroke="#333" stroke-width="1"`
- Label text centered below bracket

## Subfigure Rounded Rectangles

All subfigures are wrapped in a rounded rect:
- `rx="8"`
- Fill: `#eeeee8`
- Stroke: `#aaa`, `stroke-width="1.2"`
- Panel label at top-left inside the rect (e.g., "(a) Pre-training")

## Guidance Plot (Subfigure c)

- Axes: `stroke="#333" stroke-width="1.2"` with `axisArrow` marker
- Y-axis label: rotated −90°, positioned close to axis
- Curve: `stroke="#4A7DC0" stroke-width="2" stroke-linecap="round"`
- Shape: flat at 1 → steep exponential decay → flat at 0
- Two dashed vertical boundaries at transition points

## Bar Chart (Subfigure d)

- Y-axis with arrow, X-axis without arrow (baseline only)
- Two bars: "Original" (`#a0a8a0`, height=1 unit) and "RTC" (`#2e8b57`, height=2.5 units)
- Bars: `rx="2"` for slight rounding
- Curved arrow between bars: `stroke="#555" stroke-width="1.5"` with `curveArrow` marker
- "2.5x" label: `font-size="10" font-weight="bold"`

## PDF Generation

```python
import cairosvg
cairosvg.svg2pdf(url='continuousRTC.svg', write_to='continuousRTC.pdf')
```
