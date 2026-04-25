"""
Surgery: turn the original continuousRTC.svg (where labels are frozen as
<path> glyph outlines) into an Inkscape-friendly variant where every text
block is a real <text> element.

Strategy
--------
The original SVG encodes every label as a <g>...</g> group of <path> glyphs,
each path positioned by  transform="translate(X,Y) scale(F,-F)"  where F is
small (~0.005 to 0.01).  We:
  1. Find every such group.
  2. Read the first glyph's translate(X,Y) and the common scale factor F.
  3. Estimate font size from F (size ≈ 1 / F in the path's local units, which
     translates to roughly the visual pixel size since matplotlib's TextPath
     draws at 1 unit = 1 em).
  4. Replace the entire group with  <text x="X" y="Y" font-size="S">…</text>.

Because we can't reliably decode the original string from the path outlines,
each group is given a placeholder label (TEXT_1, TEXT_2, …) along with an
XML comment that records the (x,y,size) metadata.  Edit the labels in
Inkscape (or a text editor) — the geometry matches what was there before.

Run:
    python3 surgery.py
→ writes continuousRTC_from_paths.svg  alongside continuousRTC.svg
"""

import re
from pathlib import Path

SRC = Path(__file__).parent / "continuousRTC.svg"
DST = Path(__file__).parent / "continuousRTC_from_paths.svg"

# A "glyph group" is <g>…</g> whose children are <path> elements with a
# transform of the form translate(X,Y) scale(F,-F) where F < 0.02.
# Groups may also carry their own outer transform (e.g. italic rotation).
GLYPH_GROUP_RE = re.compile(
    r'<g([^>]*)>((?:\s*<path[^/]*?transform="translate\([^)]*\)\s*scale\([^)]*\)"[^/]*/>\s*)+)</g>',
    re.DOTALL,
)
# First translate inside a group, used as the text anchor.
FIRST_TRANSLATE_RE = re.compile(
    r'transform="translate\(([-\d.]+)\s*,?\s*([-\d.]+)\)\s*scale\(([-\d.]+)\s*,?\s*([-\d.]+)\)"'
)


def replace_group(match, counter=[0]):
    outer_attrs = match.group(1)
    inner = match.group(2)

    first = FIRST_TRANSLATE_RE.search(inner)
    if not first:
        return match.group(0)  # leave anything weird untouched

    x = float(first.group(1))
    y = float(first.group(2))
    sx = float(first.group(3))
    sy = float(first.group(4))
    # Matplotlib TextPath uses scale=(s, -s) where s = font_size / 1000 * units.
    # Visual pixel size ≈ 1000 * |sx|   (empirically matches the original).
    size = max(6, round(1000 * abs(sx)))

    # Count glyphs in group to estimate how long the label was.
    n_glyphs = inner.count("<path")

    counter[0] += 1
    placeholder = f"LABEL_{counter[0]}"

    # If the outer group carried a transform (e.g. rotate(-90,...)), preserve it.
    outer_attrs = outer_attrs.strip()
    keep_attrs = ""
    mt = re.search(r'transform="([^"]+)"', outer_attrs)
    if mt:
        keep_attrs = f' transform="{mt.group(1)}"'

    return (f'<!-- surgery: was {n_glyphs}-glyph path text at '
            f'({x:.1f},{y:.1f}), size≈{size} -->'
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}"'
            f' fill="#333"{keep_attrs}>{placeholder}</text>')


def main():
    svg = SRC.read_text()
    before = svg
    new_svg, n = GLYPH_GROUP_RE.subn(replace_group, svg)
    print(f"replaced {n} glyph groups with <text> placeholders")
    DST.write_text(new_svg)
    print(f"wrote {DST}  ({DST.stat().st_size/1024:.1f} KB, "
          f"was {len(before)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
