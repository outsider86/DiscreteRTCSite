"""
Decode every glyph-path group in continuousRTC.svg back to plain text by
matching each glyph's path data against a dictionary built with matplotlib's
TextPath — the same tool that produced the outlines (font: DejaVu Sans Bold,
size=2048; verified by reproducing the '(' glyph exactly).

Produces `continuousRTC_editable.svg`: visually identical to the original,
but every text group is a single <text> element editable in Inkscape.

Run:  python3 decode.py
"""

import re
from pathlib import Path

from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MPath
from matplotlib.textpath import TextPath

SRC = Path(__file__).parent / "continuousRTC.svg"
DST = Path(__file__).parent / "continuousRTC_editable.svg"


# =============================================================================
# Reference: render a glyph with matplotlib and serialise to the SAME
# canonical form we use for the originals.
# =============================================================================
FONT_SIZE = 2048
STYLES = [
    # name                family         weight    style
    ("sans_bold",          "DejaVu Sans", "bold",   "normal"),
    ("sans_bolditalic",    "DejaVu Sans", "bold",   "italic"),
    ("sans_regular",       "DejaVu Sans", "normal", "normal"),
    ("sans_italic",        "DejaVu Sans", "normal", "italic"),
    ("serif_bold",         "DejaVu Serif","bold",   "normal"),
    ("serif_bolditalic",   "DejaVu Serif","bold",   "italic"),
    ("serif_regular",      "DejaVu Serif","normal", "normal"),
    ("serif_italic",       "DejaVu Serif","normal", "italic"),
]

CHARS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    " .,-+=/\\*()[]{}:;!?#$%&'\"<>_|~"
    "\u03a0"   # Π
    "\u03c0"   # π
    "\u2212"   # − minus
    "\u00d7"   # × times
    "\u00b7"   # · middot
)


def canonical(verts, codes):
    """Serialise vertex/code arrays to a canonical string, always using
    M/L/Q/C/Z commands (no H/V shortcuts), rounding coordinates to nearest
    integer for M/L/Z anchors and 1 decimal for Q/C control points."""
    out = []
    i = 0
    while i < len(codes):
        c = codes[i]
        if c == MPath.MOVETO:
            out.append(f"M{round(verts[i][0])} {round(verts[i][1])}")
            i += 1
        elif c == MPath.LINETO:
            out.append(f"L{round(verts[i][0])} {round(verts[i][1])}")
            i += 1
        elif c == MPath.CURVE3:
            out.append(
                f"Q{verts[i][0]:.1f} {verts[i][1]:.1f} "
                f"{round(verts[i+1][0])} {round(verts[i+1][1])}"
            )
            i += 2
        elif c == MPath.CURVE4:
            out.append(
                f"C{verts[i][0]:.1f} {verts[i][1]:.1f} "
                f"{verts[i+1][0]:.1f} {verts[i+1][1]:.1f} "
                f"{round(verts[i+2][0])} {round(verts[i+2][1])}"
            )
            i += 3
        elif c == MPath.CLOSEPOLY:
            out.append("Z")
            i += 1
        else:
            i += 1
    return " ".join(out)


def reference_d(ch, fp):
    tp = TextPath((0, 0), ch, size=FONT_SIZE, prop=fp)
    return canonical(tp.vertices, tp.codes)


print("Building glyph lookup…")
LOOKUP = {}   # canonical-d -> list[(char, style_name)]
STYLE_OF = {} # style_name -> (family, weight, style)
for name, family, weight, style in STYLES:
    STYLE_OF[name] = (family, weight, style)
    fp = FontProperties(family=family, weight=weight, style=style)
    for ch in CHARS:
        try:
            d = reference_d(ch, fp)
        except Exception:
            continue
        if not d:
            # space has no outline
            if ch == " ":
                LOOKUP.setdefault("__SPACE__", []).append((ch, name))
            continue
        LOOKUP.setdefault(d, []).append((ch, name))
print(f"  {sum(len(v) for v in LOOKUP.values())} glyph entries")


# =============================================================================
# Parse SVG path `d` strings that may contain H/V/T/S shortcuts and
# re-serialise them to the SAME canonical form.
# =============================================================================
PATH_TOKEN = re.compile(r"([MmLlHhVvCcQqTtSsAaZz])|(-?\d+(?:\.\d+)?)")


def parse_and_canonicalise(d_str):
    """Walk the SVG path, tracking current-point to expand H/V shortcuts,
    and emit the canonical form (only M/L/Q/C/Z, rounded like reference)."""
    tokens = PATH_TOKEN.findall(d_str)
    out = []
    cur_x, cur_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    cmd = None
    nums = []

    def need():
        return {"M": 2, "L": 2, "H": 1, "V": 1,
                "Q": 4, "C": 6, "T": 2, "S": 4,
                "Z": 0}.get(cmd, 0)

    def consume():
        nonlocal cur_x, cur_y, start_x, start_y
        if cmd == "M":
            x, y = nums
            out.append(f"M{round(x)} {round(y)}")
            cur_x, cur_y = x, y
            start_x, start_y = x, y
        elif cmd == "L":
            x, y = nums
            out.append(f"L{round(x)} {round(y)}")
            cur_x, cur_y = x, y
        elif cmd == "H":
            x = nums[0]
            out.append(f"L{round(x)} {round(cur_y)}")
            cur_x = x
        elif cmd == "V":
            y = nums[0]
            out.append(f"L{round(cur_x)} {round(y)}")
            cur_y = y
        elif cmd == "Q":
            cx, cy, x, y = nums
            out.append(f"Q{cx:.1f} {cy:.1f} {round(x)} {round(y)}")
            cur_x, cur_y = x, y
        elif cmd == "C":
            a, b, c, d, x, y = nums
            out.append(f"C{a:.1f} {b:.1f} {c:.1f} {d:.1f} {round(x)} {round(y)}")
            cur_x, cur_y = x, y
        elif cmd == "Z":
            out.append("Z")
            cur_x, cur_y = start_x, start_y

    for letter, num in tokens:
        if letter:
            # Starting a new command — any trailing nums shouldn't happen.
            cmd = letter.upper()
            nums = []
            if cmd == "Z":
                consume()
                cmd = None
        else:
            nums.append(float(num))
            if cmd and len(nums) == need():
                consume()
                nums = []
                # implicit repetition: M becomes L after first pair
                if cmd == "M":
                    cmd = "L"
    return " ".join(out)


# =============================================================================
# Group extraction (same regex as surgery.py)
# =============================================================================
GROUP_RE = re.compile(
    r'<g(?P<outer>[^>]*)>(?P<body>(?:\s*<path[^/]*?transform="translate\([^)]*\)\s*'
    r'scale\([^)]*\)"\s*/>)+)</g>',
    re.DOTALL,
)
PATH_RE = re.compile(
    r'<path\s+d="([^"]+)"\s+fill="([^"]+)"\s+'
    r'transform="translate\(([-\d.]+)\s*,?\s*([-\d.]+)\)\s*'
    r'scale\(([-\d.]+)\s*,?\s*([-\d.]+)\)"\s*/>'
)


def decode_group(match):
    body = match.group("body")
    paths = PATH_RE.findall(body)
    if not paths:
        return match.group(0)

    entries = []  # (x, y, ch, style, scale, fill)
    fill = "#333"
    for d_attr, fill_attr, tx, ty, sx, sy in paths:
        fill = fill_attr
        canon = parse_and_canonicalise(d_attr)
        candidates = LOOKUP.get(canon, [])
        if candidates:
            ch, style = candidates[0]
        else:
            ch, style = "?", None
        entries.append((float(tx), float(ty), ch, style, float(sx), fill_attr))

    entries.sort(key=lambda t: (t[1], t[0]))  # top-to-bottom, then left-to-right

    # Group by y so baseline shifts (e.g. sub/super-script) don't scramble
    ys = sorted({round(e[1], 1) for e in entries})

    # Compute median glyph advance for space detection
    # Within the same y line
    def detect_line(line_entries):
        line_entries = sorted(line_entries, key=lambda t: t[0])
        gaps = []
        for i in range(1, len(line_entries)):
            gaps.append(line_entries[i][0] - line_entries[i-1][0])
        med = sorted(gaps)[len(gaps)//2] if gaps else 0
        s = []
        for i, (x, y, ch, st, sc, fi) in enumerate(line_entries):
            if i > 0 and med > 0 and (x - line_entries[i-1][0]) > 1.7 * med:
                s.append(" ")
            s.append(ch)
        return "".join(s)

    lines = []
    for y in ys:
        line = [e for e in entries if round(e[1], 1) == y]
        lines.append(detect_line(line))
    text_str = " ".join(lines)

    # Anchor = first glyph's translate coords (this is where the SVG places
    # the left edge of the first character's bounding box in matplotlib's
    # coordinate system)
    first = entries[0]
    anchor_x, anchor_y = first[0], first[1]
    scale = abs(first[4])
    font_px = FONT_SIZE * scale  # visual pixel size

    # Determine dominant style
    style_votes = {}
    for e in entries:
        if e[3]:
            style_votes[e[3]] = style_votes.get(e[3], 0) + 1
    dom_style = max(style_votes, key=style_votes.get) if style_votes else "sans_bold"
    family, weight, style = STYLE_OF[dom_style]
    # map matplotlib family → SVG font-family
    svg_family = ("serif"
                  if "serif" in family.lower()
                  else "'DejaVu Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif")

    # Preserve outer group transform (e.g. the rotate(-90,...) on axis labels,
    # or the "translate(X,Y) scale(0.82) translate(-X,-Y)" wrappers on subfigs)
    outer = match.group("outer").strip()
    mt = re.search(r'transform="([^"]+)"', outer)
    outer_tx = f' transform="{mt.group(1)}"' if mt else ""

    w_attr = f' font-weight="{weight}"' if weight != "normal" else ""
    s_attr = f' font-style="italic"' if style == "italic" else ""

    text_esc = (text_str
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

    return (
        f'<text x="{anchor_x:.3f}" y="{anchor_y:.3f}"'
        f' font-size="{font_px:.2f}" font-family="{svg_family}"'
        f'{w_attr}{s_attr} fill="{fill}"{outer_tx}>{text_esc}</text>'
    )


# =============================================================================
def main():
    svg = SRC.read_text()
    new_svg, n = GROUP_RE.subn(decode_group, svg)
    print(f"Replaced {n} glyph groups with <text> elements.")
    DST.write_text(new_svg)
    print(f"Wrote {DST}  ({DST.stat().st_size/1024:.1f} KB, "
          f"was {SRC.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
