import base64, io
from PIL import Image
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MPath


def text_path(text, cx, cy, font_size=20, font_family='DejaVu Sans', weight='normal', fill='#333'):
    """Render <text> as an SVG <path> (visually centered at (cx, cy)) so SVG and PDF match exactly."""
    fp = FontProperties(family=font_family, weight=weight, size=font_size)
    tp = TextPath((0, 0), text, size=font_size, prop=fp)
    verts, codes = tp.vertices, tp.codes
    parts = []
    i = 0
    while i < len(codes):
        c = codes[i]
        if c == MPath.MOVETO:
            parts.append(f"M{verts[i][0]:.3f} {verts[i][1]:.3f}"); i += 1
        elif c == MPath.LINETO:
            parts.append(f"L{verts[i][0]:.3f} {verts[i][1]:.3f}"); i += 1
        elif c == MPath.CURVE3:
            parts.append(f"Q{verts[i][0]:.3f} {verts[i][1]:.3f} {verts[i+1][0]:.3f} {verts[i+1][1]:.3f}"); i += 2
        elif c == MPath.CURVE4:
            parts.append(f"C{verts[i][0]:.3f} {verts[i][1]:.3f} {verts[i+1][0]:.3f} {verts[i+1][1]:.3f} {verts[i+2][0]:.3f} {verts[i+2][1]:.3f}"); i += 3
        elif c == MPath.CLOSEPOLY:
            parts.append("Z"); i += 1
        else:
            i += 1
    bb = tp.get_extents()
    cx0, cy0 = (bb.x0 + bb.x1)/2, (bb.y0 + bb.y1)/2
    tx, ty = cx - cx0, cy + cy0
    return (f'<path d="{" ".join(parts)}" fill="{fill}" '
            f'transform="translate({tx:.3f} {ty:.3f}) scale(1 -1)" />')

# --- Embed cover image (resized JPEG, base64) ---
src = Image.open('/scratch/wangpc/DiscreteRTCVisualization/PnPcover3.png').convert('RGB')
enc_w = 1440
enc_h = int(src.size[1] * enc_w / src.size[0])
buf = io.BytesIO()
src.resize((enc_w, enc_h), Image.LANCZOS).save(buf, format='JPEG', quality=85, optimize=True)
img_b64 = base64.b64encode(buf.getvalue()).decode('ascii')

# --- Token colors (matching discreteRTC.svg) ---
GREEN  = '#2e8b57'
YELLOW = '#e8d810'

G_FULL_GREEN  = [[1,1,1],[1,1,1],[1,1,1]]
G_FULL_YELLOW = [[0,0,0],[0,0,0],[0,0,0]]

# Mixed-region set 1 (chunk 1, actions 4-6) -- original from discreteRTC
G_MIX_A1 = [[1,1,1],[1,1,0],[1,0,1]]   # 7 green, 2 yellow
G_MIX_B1 = [[1,1,1],[1,0,0],[0,1,0]]   # 5 green, 4 yellow
G_MIX_C1 = [[1,0,0],[0,0,0],[0,1,0]]   # 2 green, 7 yellow

# Mixed-region set 2 (chunks 2 & 3, actions 7-9) -- randomized, same green-count gradient
G_MIX_A2 = [[0,1,1],[1,1,1],[1,1,0]]   # 7 green, 2 yellow
G_MIX_B2 = [[1,0,1],[0,1,0],[1,1,0]]   # 5 green, 4 yellow
G_MIX_C2 = [[0,0,1],[1,0,0],[0,0,0]]   # 2 green, 7 yellow

# Mixed-region set 3 (chunk 4, actions 7-9) -- randomized, same green-count gradient
G_MIX_A3 = [[1,1,0],[1,0,1],[1,1,1]]   # 7 green, 2 yellow
G_MIX_B3 = [[0,1,0],[1,1,0],[1,0,1]]   # 5 green, 4 yellow
G_MIX_C3 = [[0,1,0],[0,0,1],[0,0,0]]   # 2 green, 7 yellow

# Four chunks (top to bottom):
#   chunk 1 : 3 green + 3 mixed (set 1) + 3 yellow
#   chunk 2 : 6 green + 3 mixed (set 2)
#   chunk 3 : chunk 2's actions 4-9 passed into actions 1-6, + 3 yellow at actions 7-9
#   chunk 4 : 6 green + 3 mixed (set 3)
PATTERN_1 = [
    G_FULL_GREEN,  G_FULL_GREEN,  G_FULL_GREEN,
    G_MIX_A1,      G_MIX_B1,      G_MIX_C1,
    G_FULL_YELLOW, G_FULL_YELLOW, G_FULL_YELLOW,
]
PATTERN_2 = [
    G_FULL_GREEN, G_FULL_GREEN, G_FULL_GREEN,
    G_FULL_GREEN, G_FULL_GREEN, G_FULL_GREEN,
    G_MIX_A2,     G_MIX_B2,     G_MIX_C2,
]
PATTERN_3 = [
    # actions 1-6 <- chunk 2 actions 4-9 (3 green + mixed set 2)
    G_FULL_GREEN, G_FULL_GREEN, G_FULL_GREEN,
    G_MIX_A2,     G_MIX_B2,     G_MIX_C2,
    # actions 7-9: new, all yellow
    G_FULL_YELLOW, G_FULL_YELLOW, G_FULL_YELLOW,
]
PATTERN_4 = [
    G_FULL_GREEN, G_FULL_GREEN, G_FULL_GREEN,
    G_FULL_GREEN, G_FULL_GREEN, G_FULL_GREEN,
    G_MIX_A3,     G_MIX_B3,     G_MIX_C3,
]

# --- Dimensions ---
CELL  = 20
GROUP = 3 * CELL        # 60
NG    = 9               # chunk size
CW    = NG * GROUP      # 540
CH    = 3 * CELL        # 60

IMG_X, IMG_Y = 40, 20
IMG_W = 3 * GROUP * 4   # 720 (4 images, each 3 groups wide)
IMG_H = int(src.size[1] * IMG_W / src.size[0])  # 183

# Pair 1 (chunks 1 & 2) start at image-1 left
C1_X  = IMG_X                          # 40
C1_Y  = IMG_Y + IMG_H + 42             # chunk 1 top
C2_Y  = C1_Y + CH + 16                 # chunk 2 top

# Pair 2 (chunks 3 & 4) staggered right by 3 groups = one image width
P2_X  = C1_X + 3*GROUP                 # 220
C3_Y  = C2_Y + CH + 48
C4_Y  = C3_Y + CH + 16

# Dashed reference lines at green/mixed and mixed/yellow boundaries of chunk 1's BEFORE pattern
DASH1 = C1_X + 3*GROUP   # 220
DASH2 = C1_X + 6*GROUP   # 400

VB_W = IMG_X + IMG_W + IMG_X   # 800
VB_H = C4_Y + CH + 30


def chunk(x0, y0, pattern):
    out = []
    for gi, pat in enumerate(pattern):
        for r in range(3):
            for c in range(3):
                col = GREEN if pat[r][c] else YELLOW
                out.append(f'<rect x="{x0+gi*GROUP+c*CELL}" y="{y0+r*CELL}" '
                           f'width="{CELL}" height="{CELL}" fill="{col}" />')
    out.append(f'<rect x="{x0}" y="{y0}" width="{CW}" height="{CH}" '
               f'fill="none" stroke="#555" stroke-width="1.5" />')
    for g in range(1, NG):
        x = x0 + g*GROUP
        out.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0+CH}" '
                   f'stroke="#888" stroke-width="1.2" />')
    for r in range(1, 3):
        y = y0 + r*CELL
        out.append(f'<line x1="{x0}" y1="{y}" x2="{x0+CW}" y2="{y}" '
                   f'stroke="#888" stroke-width="0.5" />')
    for c in range(1, NG*3):
        if c % 3 == 0:
            continue
        x = x0 + c*CELL
        out.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y0+CH}" '
                   f'stroke="#888" stroke-width="0.5" />')
    return '\n    '.join(out)


svg = f'''<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {VB_W} {VB_H}"
     font-family="'DejaVu Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
     style="background:white">
  <rect width="{VB_W}" height="{VB_H}" fill="white" />

  <defs>
    <marker id="passArrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="{GREEN}" />
    </marker>
  </defs>

  <!-- Cover image (embedded base64 JPEG, no border) -->
  <image xlink:href="data:image/jpeg;base64,{img_b64}"
         x="{IMG_X}" y="{IMG_Y}" width="{IMG_W}" height="{IMG_H}"
         preserveAspectRatio="xMidYMid meet" />

  <!-- chunk 1 -->
  <g>
    {chunk(C1_X, C1_Y, PATTERN_1)}
  </g>
  <!-- chunk 2 -->
  <g>
    {chunk(C1_X, C2_Y, PATTERN_2)}
  </g>
  <!-- chunk 3: inherits chunk-2 actions 4-9 into actions 1-6, new yellow at 7-9 -->
  <g>
    {chunk(P2_X, C3_Y, PATTERN_3)}
  </g>
  <!-- chunk 4 -->
  <g>
    {chunk(P2_X, C4_Y, PATTERN_4)}
  </g>

  <!-- dashed reference lines spanning both pairs -->
  <line x1="{DASH1}" y1="{C1_Y-6}" x2="{DASH1}" y2="{C4_Y+CH+6}"
        stroke="#aaa" stroke-width="1.2" stroke-dasharray="5,4" />
  <line x1="{DASH2}" y1="{C1_Y-6}" x2="{DASH2}" y2="{C4_Y+CH+6}"
        stroke="#aaa" stroke-width="1.2" stroke-dasharray="5,4" />
  <!-- dashed line at the rear of chunks 1 & 2 (= x end of pair 1), passing through chunks 3 & 4 -->
  <line x1="{C1_X+CW}" y1="{C1_Y-6}" x2="{C1_X+CW}" y2="{C4_Y+CH+6}"
        stroke="#aaa" stroke-width="1.2" stroke-dasharray="5,4" />

  <!-- partial-pass arrow between pair 1 (chunk 2) and pair 2 (chunk 3) -->
  <line x1="{(P2_X + C1_X+CW)//2}" y1="{C2_Y+CH+6}"
        x2="{(P2_X + C1_X+CW)//2}" y2="{C3_Y-6}"
        stroke="{GREEN}" stroke-width="2" marker-end="url(#passArrow)" />

  <!-- labels in the blank regions (rendered as SVG <path> glyphs so SVG/PDF match) -->
  {text_path("Inference K",
             (C1_X+CW + IMG_X+IMG_W)/2, (C1_Y+CH + C2_Y)/2,
             font_size=20, weight='bold', fill='#333')}
  {text_path("Inference K+1",
             (IMG_X + P2_X)/2, (C3_Y+CH + C4_Y)/2,
             font_size=20, weight='bold', fill='#333')}
</svg>
'''

out_svg = '/scratch/wangpc/DiscreteRTCVisualization/figures/methods/asyncInference/asyncInference.svg'
out_pdf = out_svg.replace('.svg', '.pdf')
with open(out_svg, 'w') as f:
    f.write(svg)
print(f'wrote {out_svg}  ({len(svg)/1024:.1f} KB)')

import cairosvg
cairosvg.svg2pdf(bytestring=svg.encode('utf-8'), write_to=out_pdf)
import os
print(f'wrote {out_pdf}  ({os.path.getsize(out_pdf)/1024:.1f} KB)')
