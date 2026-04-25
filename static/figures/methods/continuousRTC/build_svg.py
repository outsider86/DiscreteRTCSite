"""
Generator for continuousRTC.svg.

Unlike the original hand-authored SVG (which bakes every letter as a <path>
glyph outline), this script emits real <text> elements — so the output is
editable in Inkscape / any SVG editor, and label text is trivially editable
by changing the strings in this file.

Edit the LABEL_* constants below to change the figure's text, then run:

    python3 build_svg.py

The script writes `continuousRTC.svg` next to itself.  PDF export is optional
(requires cairosvg, rsvg-convert, or inkscape).

Layout follows the spec in continuousRTC.md.
"""

from pathlib import Path

# =============================================================================
# CANVAS
# =============================================================================
VB_X, VB_Y, VB_W, VB_H = 50, 74, 766, 254
BG_COLOR = "#ffffff"          # main.tex uses \includegraphics on white bg
FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"
SERIF = "'Times New Roman', 'CMU Serif', Georgia, serif"

# =============================================================================
# PALETTE
# =============================================================================
GREEN0 = "#2e8b57"   # trusted / frozen
GREEN1 = "#5a9e45"
GREEN2 = "#8bb832"
GREEN3 = "#bdd01e"
YELLOW = "#e8d810"   # pure noise
GRAY_BAR = "#a0a8a0"
BLUE = "#4A7DC0"
SUBFIG_FILL = "#fdf5e0"
TEXT = "#333"
STROKE = "#555"
BORDER = "#888"
DASH = "#777"
SUBFIG_BORDER = "#aaa"

# Gradient used by BEFORE chunk (left→right): 2 frozen, 3 transition, 3 noisy
TOP_COLORS = [GREEN0, GREEN0, GREEN1, GREEN2, GREEN3, YELLOW, YELLOW, YELLOW]
BOT_COLORS = [GREEN0] * 8

# =============================================================================
# LABELS  (edit here or in the SVG — both work)
# =============================================================================
MAIN_TITLE       = "Continuous RTC Inference"
BEFORE_LABEL     = "Action Chunk"
PI_GDM           = ("\u03a0", "GDM")           # Π, GDM
BRACKET_LEFT     = "Frozen Actions"
BRACKET_RIGHT    = "New Actions"

SUBFIG_A_TITLE   = "(a) Pre-training Data"
SUBFIG_B_TITLE   = "(b) Fine-tuning Data"
SUBFIG_C_TITLE   = "(c) Guidance Weight"
SUBFIG_D_TITLE   = "(d) Compute Cost"

C_Y_AXIS         = "weight"
C_X_AXIS         = "denoising step"
D_Y_AXIS         = "NFEs"                      # number of function evaluations
D_X_LABELS       = ("Original", "RTC")
D_RATIO_LABEL    = "2.5\u00d7"                 # "2.5×"


# =============================================================================
# HELPERS
# =============================================================================
def text(x, y, s, *, size=11, weight="normal", style="normal",
         anchor="middle", family=FONT, fill=TEXT, extra=""):
    """Emit an <text> element."""
    w = f' font-weight="{weight}"' if weight != "normal" else ""
    st = f' font-style="{style}"' if style != "normal" else ""
    fam = f' font-family="{family}"' if family != FONT else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}"{fam}'
            f' text-anchor="{anchor}" fill="{fill}"{w}{st}{extra}>{s}</text>')


def chunk(x, y, n, cell_w, cell_h, colors,
          *, outer_sw=1.5, inner_sw=1.2):
    """Emit a 1×n strip of colored cells with dividers and an outer border."""
    parts = []
    for i, c in enumerate(colors[:n]):
        parts.append(f'<rect x="{x + i*cell_w}" y="{y}"'
                     f' width="{cell_w}" height="{cell_h}" fill="{c}" />')
    parts.append(f'<rect x="{x}" y="{y}" width="{n*cell_w}" height="{cell_h}"'
                 f' fill="none" stroke="{BORDER}" stroke-width="{outer_sw}" />')
    for i in range(1, n):
        xi = x + i * cell_w
        parts.append(f'<line x1="{xi}" y1="{y}" x2="{xi}" y2="{y + cell_h}"'
                     f' stroke="{BORDER}" stroke-width="{inner_sw}" />')
    return "\n    ".join(parts)


def bracket(x1, x2, y, label, *, tick=4, label_dy=14):
    """Horizontal bracket with a centered label below."""
    cx = (x1 + x2) / 2
    return "\n    ".join([
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{TEXT}" stroke-width="1" />',
        f'<line x1="{x1}" y1="{y - tick}" x2="{x1}" y2="{y + tick}" stroke="{TEXT}" stroke-width="1" />',
        f'<line x1="{x2}" y1="{y - tick}" x2="{x2}" y2="{y + tick}" stroke="{TEXT}" stroke-width="1" />',
        text(cx, y + label_dy, label, size=10, weight="bold", style="italic"),
    ])


# =============================================================================
# LEFT: main figure
# =============================================================================
def left_panel():
    # Nested SVG with its own viewBox so positions match the spec's numbers.
    # viewBox width = 444, height = 265 ; placed at (0,0), rendered 470×420.
    CX = 382                 # horizontal center of chunks (within inner VB)
    CHUNK_X = 190            # chunk starts here, 8 cells × 48 = 384 wide
    CELL = 48

    body = [
        # Title
        text(CX, 45, MAIN_TITLE, size=20, weight="bold", family=SERIF),

        # Before chunk
        chunk(CHUNK_X, 72, 8, CELL, CELL, TOP_COLORS),

        # Downward arrow between chunks, with Π_GDM label to its right
        '<line x1="{x}" y1="130" x2="{x}" y2="150"'
        ' stroke="{s}" stroke-width="1.8" marker-end="url(#arrowhead)" />'
        .format(x=CX, s=STROKE),
        text(CX + 18, 148, f"\u03a0", size=15, style="italic",
             family=SERIF, fill="#444", anchor="start"),
        text(CX + 28, 151, "GDM", size=11, anchor="start", fill="#444",
             extra=' font-style="normal"'),

        # After chunk
        chunk(CHUNK_X, 158, 8, CELL, CELL, BOT_COLORS),

        # Bracket annotations below the bottom chunk
        bracket(CHUNK_X,            CHUNK_X + 5*CELL, 230, BRACKET_LEFT),
        bracket(CHUNK_X + 5*CELL,   CHUNK_X + 8*CELL, 230, BRACKET_RIGHT),

        # Optional sub-label above top chunk (small)
        text(CX, 62, BEFORE_LABEL, size=11, weight="bold"),
    ]

    defs = '''
    <defs>
      <marker id="arrowhead" markerWidth="7" markerHeight="5" refX="4" refY="2.5" orient="auto">
        <polygon points="0 0, 7 2.5, 0 5" fill="{s}" />
      </marker>
    </defs>'''.format(s=STROKE)

    return (f'<svg x="0" y="0" width="470" height="420"'
            f' viewBox="130 15 444 265" preserveAspectRatio="xMidYMid meet">'
            f'{defs}\n    ' + "\n    ".join(body) + '\n  </svg>')


# =============================================================================
# RIGHT TOP: (a) + (b) — noise-pattern comparison
# =============================================================================
def right_top_panel():
    # viewBox 520×168, displayed at 335×108 at (480, 94)
    CELL = 26
    Y_CHUNK = 52
    X_A = 30
    X_B = 280
    GAP_DASH_X = 262   # dashed divider between (a) and (b)

    # (a) shows uniform noise — all YELLOW (pre-training style: uniform noise)
    # (b) shows mixed chunk — green→yellow gradient (RTC inference style)
    a_colors = [YELLOW] * 8
    b_colors = TOP_COLORS

    body = [
        f'<rect x="2" y="2" width="516" height="164" rx="8"'
        f' fill="{SUBFIG_FILL}" stroke="{SUBFIG_BORDER}" stroke-width="1.2" />',
        f'<line x1="{GAP_DASH_X}" y1="20" x2="{GAP_DASH_X}" y2="152"'
        f' stroke="{SUBFIG_BORDER}" stroke-width="1" stroke-dasharray="5,4" />',

        # Panel titles
        text(X_A + 9, 26, SUBFIG_A_TITLE, size=11, weight="bold", anchor="start"),
        text(X_B + 9, 26, SUBFIG_B_TITLE, size=11, weight="bold", anchor="start"),

        # Panel (a): single noisy chunk
        chunk(X_A, Y_CHUNK, 8, CELL, CELL, a_colors,
              outer_sw=1.2, inner_sw=1.0),
        # Panel (b): gradient chunk
        chunk(X_B, Y_CHUNK, 8, CELL, CELL, b_colors,
              outer_sw=1.2, inner_sw=1.0),

        # Down arrows + result chunks (all-green inferred)
        f'<line x1="{X_A + 4*CELL}" y1="{Y_CHUNK+CELL+6}" x2="{X_A + 4*CELL}" y2="{Y_CHUNK+CELL+26}"'
        f' stroke="{STROKE}" stroke-width="1.6" marker-end="url(#arrow)" />',
        f'<line x1="{X_B + 4*CELL}" y1="{Y_CHUNK+CELL+6}" x2="{X_B + 4*CELL}" y2="{Y_CHUNK+CELL+26}"'
        f' stroke="{STROKE}" stroke-width="1.6" marker-end="url(#arrow)" />',

        chunk(X_A, 116, 8, CELL, CELL, [GREEN0]*8,
              outer_sw=1.2, inner_sw=1.0),
        chunk(X_B, 116, 8, CELL, CELL, [GREEN0]*8,
              outer_sw=1.2, inner_sw=1.0),
    ]

    defs = '''
    <defs>
      <marker id="arrow" markerWidth="7" markerHeight="5" refX="4" refY="2.5" orient="auto">
        <polygon points="0 0, 7 2.5, 0 5" fill="{s}" />
      </marker>
    </defs>'''.format(s=STROKE)

    return (f'<svg x="480" y="94" width="335" height="108"'
            f' viewBox="0 0 520 168" preserveAspectRatio="xMidYMid meet">'
            f'{defs}\n    ' + "\n    ".join(body) + '\n  </svg>')


# =============================================================================
# RIGHT BOTTOM-LEFT: (c) guidance weight curve
# =============================================================================
def right_bottom_left_panel():
    body = [
        f'<rect x="2" y="2" width="256" height="177" rx="8"'
        f' fill="{SUBFIG_FILL}" stroke="{SUBFIG_BORDER}" stroke-width="1.2" />',
        text(18, 22, SUBFIG_C_TITLE, size=11, weight="bold", anchor="start"),

        # Axes (origin around (58,138); scale ~×1.1 like original)
        f'<g transform="translate(-10, 6) scale(1.1)">',
        f'<line x1="58" y1="138" x2="58" y2="36" stroke="#333" stroke-width="1.2"'
        f' marker-end="url(#axisArrowC)" />',
        f'<line x1="58" y1="138" x2="230" y2="138" stroke="#333" stroke-width="1.2"'
        f' marker-end="url(#axisArrowC)" />',

        # Axis labels
        text(46, 90, C_Y_AXIS, size=10, weight="bold", anchor="middle",
             extra=f' transform="rotate(-90,46,90)"'),
        text(144, 158, C_X_AXIS, size=10, weight="bold"),

        # Dashed region boundaries
        f'<line x1="115" y1="40" x2="115" y2="138" stroke="{BORDER}"'
        f' stroke-width="1" stroke-dasharray="4,3" />',
        f'<line x1="185" y1="40" x2="185" y2="138" stroke="{BORDER}"'
        f' stroke-width="1" stroke-dasharray="4,3" />',

        # Curve: flat-1 → exp decay → flat-0
        f'<path d="M 58,48 L 115,48 C 118,48 120,50 122,55'
        f' C 126,68 130,85 135,98 C 140,110 146,120 152,128'
        f' C 158,133 165,136 175,137.5 C 180,138 185,138 185,138'
        f' L 224,138" fill="none" stroke="{BLUE}" stroke-width="2"'
        f' stroke-linecap="round" />',
        f'</g>',
    ]

    defs = '''
    <defs>
      <marker id="axisArrowC" markerWidth="6" markerHeight="4" refX="3" refY="2" orient="auto">
        <polygon points="0 0, 6 2, 0 4" fill="#333" />
      </marker>
    </defs>'''

    return (f'<svg x="480" y="213" width="165" height="115"'
            f' viewBox="0 0 260 181" preserveAspectRatio="xMidYMid meet">'
            f'{defs}\n    ' + "\n    ".join(body) + '\n  </svg>')


# =============================================================================
# RIGHT BOTTOM-RIGHT: (d) compute-cost bar chart
# =============================================================================
def right_bottom_right_panel():
    body = [
        f'<rect x="2" y="2" width="256" height="177" rx="8"'
        f' fill="{SUBFIG_FILL}" stroke="{SUBFIG_BORDER}" stroke-width="1.2" />',
        text(18, 22, SUBFIG_D_TITLE, size=11, weight="bold", anchor="start"),

        f'<g transform="translate(-10, 6) scale(1.1)">',
        f'<line x1="65" y1="138" x2="65" y2="36" stroke="#333" stroke-width="1.2"'
        f' marker-end="url(#axisArrowD)" />',
        f'<line x1="65" y1="138" x2="235" y2="138" stroke="#333" stroke-width="1.2" />',

        # Y-axis label
        text(54, 90, D_Y_AXIS, size=10, weight="bold",
             extra=f' transform="rotate(-90,54,90)"'),

        # Bars
        f'<rect x="85"  y="105" width="40" height="33" fill="{GRAY_BAR}" rx="2" />',
        f'<rect x="170" y="55"  width="40" height="83" fill="{YELLOW}"   rx="2" />',

        # X-axis labels under each bar
        text(105, 152, D_X_LABELS[0], size=9, weight="bold"),
        text(190, 152, D_X_LABELS[1], size=9, weight="bold"),

        # Curved arrow between bars + ratio label
        f'<path d="M 115,95 C 155,95 160,70 170,58" fill="none"'
        f' stroke="{STROKE}" stroke-width="1.5" marker-end="url(#curveArrow)" />',
        text(145, 82, D_RATIO_LABEL, size=10, weight="bold"),

        f'</g>',
    ]

    defs = '''
    <defs>
      <marker id="axisArrowD" markerWidth="6" markerHeight="4" refX="3" refY="2" orient="auto">
        <polygon points="0 0, 6 2, 0 4" fill="#333" />
      </marker>
      <marker id="curveArrow" markerWidth="7" markerHeight="5" refX="4" refY="2.5" orient="auto">
        <polygon points="0 0, 7 2.5, 0 5" fill="{s}" />
      </marker>
    </defs>'''.format(s=STROKE)

    return (f'<svg x="650" y="213" width="165" height="115"'
            f' viewBox="0 0 260 181" preserveAspectRatio="xMidYMid meet">'
            f'{defs}\n    ' + "\n    ".join(body) + '\n  </svg>')


# =============================================================================
# COMPOSE
# =============================================================================
def build():
    svg = f'''<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{VB_X} {VB_Y} {VB_W} {VB_H}"
     font-family="{FONT}"
     style="background:white">
  <rect x="{VB_X}" y="{VB_Y}" width="{VB_W}" height="{VB_H}" fill="{BG_COLOR}" />

  {left_panel()}

  {right_top_panel()}

  {right_bottom_left_panel()}

  {right_bottom_right_panel()}
</svg>
'''
    return svg


if __name__ == "__main__":
    # Write to a side-by-side file by default so the original hand-authored
    # continuousRTC.svg isn't overwritten. Rename/point this to
    # "continuousRTC.svg" once you're happy with the generator.
    out = Path(__file__).parent / "continuousRTC_editable.svg"
    out.write_text(build())
    print(f"wrote {out}  ({out.stat().st_size/1024:.1f} KB)")

    # Optional PDF export — try each available backend, skip silently if none
    pdf = out.with_suffix(".pdf")
    try:
        import cairosvg
        cairosvg.svg2pdf(url=str(out), write_to=str(pdf))
        print(f"wrote {pdf}")
    except ImportError:
        import shutil, subprocess
        for cmd in (["rsvg-convert", "-f", "pdf", "-o", str(pdf), str(out)],
                    ["inkscape", str(out), "--export-filename=" + str(pdf)]):
            if shutil.which(cmd[0]):
                subprocess.run(cmd, check=False)
                print(f"wrote {pdf} via {cmd[0]}")
                break
        else:
            print("(no SVG→PDF backend found — install cairosvg, "
                  "librsvg2-bin, or inkscape to regenerate the PDF)")
