"""
Step 2: compose the cover triptych.

Modular pipeline as specified in discrete_rtc_cover_figure_implementation_spec.md
sec. 13. Each visual layer is its own helper so individual elements can be re-tuned.
"""
from __future__ import annotations
import math
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- paths -------
HERE = Path(__file__).resolve().parent
BUILD = HERE.parent / "build"
OUT_PNG = HERE.parent / "cover_figure_final.png"

PANEL_PATHS = [BUILD / f"panel_{i}_raw.jpg" for i in (1, 2, 3)]

# ---------------------------------------------------------------- canvas ------
# Equal-width panels: all three frames share an identical narrowed view of the
# pick area, so the layout reflects that visual symmetry.
PANEL_W = 1100
LEFT_W = MID_W = RIGHT_W = PANEL_W
PANEL_H = 1075        # source crop ~440x430 (~1.02:1) -> panel matches
GAP = 28
PADDING_X = 32
PADDING_TOP = 32
PADDING_BOTTOM = 32

CANVAS_W = LEFT_W + MID_W + RIGHT_W + 2 * GAP + 2 * PADDING_X
CANVAS_H = PANEL_H + PADDING_TOP + PADDING_BOTTOM
BG = (255, 255, 255)
PANEL_RADIUS = 22

# ---------------------------------------------------------------- colours -----
GREEN = (61, 165, 92)
GREEN_BRIGHT = (110, 215, 140)
YELLOW = (242, 199, 76)
YELLOW_DIM = (200, 165, 60)
CYAN = (86, 204, 242)
WHITE = (242, 246, 252)
WHITE_DIM = (200, 207, 220)
RED_BOUNDARY = (255, 102, 102)
HUD_BG = (255, 255, 255, 215)
HUD_BORDER = (40, 50, 70, 220)


# ---------------------------------------------------------------- fonts -------
def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    ) + [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


# ============================================================================
# Helpers
# ============================================================================

def rounded_mask(size: Tuple[int, int], radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    return m


def fit_panel(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    sw, sh = img.size
    sr, tr = sw / sh, target_w / target_h
    if sr > tr:
        new_h = target_h
        new_w = int(round(sr * new_h))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        x0 = (new_w - target_w) // 2
        return img.crop((x0, 0, x0 + target_w, target_h))
    else:
        new_w = target_w
        new_h = int(round(new_w / sr))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        y0 = (new_h - target_h) // 2
        return img.crop((0, y0, target_w, y0 + target_h))


def darken_background(panel: Image.Image, vignette: float = 0.35) -> Image.Image:
    """Soft radial vignette to focus the eye on the robot/turntable area."""
    w, h = panel.size
    cx, cy = w / 2, h * 0.62
    max_r = math.hypot(max(cx, w - cx), max(cy, h - cy))
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    for y in range(h):
        for x in range(w):
            r = math.hypot(x - cx, y - cy) / max_r
            t = max(0.0, (r - 0.55) / 0.45)
            px[x, y] = int(255 * min(1.0, t) * vignette)
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(dark, panel, mask)


# ============================================================================
# Layer drawers
# ============================================================================

def draw_turntable_motion(panel: Image.Image,
                          centre: Tuple[int, int],
                          radius: int,
                          arrow_alpha: int = 165,
                          loops: int = 2) -> Image.Image:
    """Curved rotation arrows around the turntable rim."""
    w, h = panel.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = centre
    sweeps = [(195, 295), (355, 95)][:loops]
    arc_color = (CYAN[0], CYAN[1], CYAN[2], arrow_alpha)
    for (a0, a1) in sweeps:
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        d.arc(bbox, start=a0, end=a1, fill=arc_color, width=7)
        end = math.radians(a1)
        ex = cx + radius * math.cos(end)
        ey = cy + radius * math.sin(end)
        tx, ty = -math.sin(end), math.cos(end)
        head = 24
        p1 = (ex, ey)
        p2 = (ex - head * tx + 0.5 * head * math.cos(end),
              ey - head * ty + 0.5 * head * math.sin(end))
        p3 = (ex - head * tx - 0.5 * head * math.cos(end),
              ey - head * ty - 0.5 * head * math.sin(end))
        d.polygon([p1, p2, p3], fill=arc_color)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=0.6))
    return Image.alpha_composite(panel.convert("RGBA"), layer).convert("RGB")


def draw_object_ghosts_along_arc(panel: Image.Image,
                                 centre: Tuple[int, int],
                                 radius: int,
                                 angles_deg: list[float],
                                 size: int = 60,
                                 color=YELLOW,
                                 y_squish: float = 0.45) -> Image.Image:
    """Place translucent rectangles along an ellipse -> motion history on a tilted disc.

    `y_squish` < 1 compresses the vertical dimension to mimic the table's perspective
    foreshortening (the turntable is roughly an ellipse in 2D, not a circle).
    """
    w, h = panel.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    n = len(angles_deg)
    for i, ang in enumerate(angles_deg):
        alpha = int(60 + (i + 1) / n * 170)
        s = size
        ghost = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0))
        gd = ImageDraw.Draw(ghost)
        # filled translucent rect (more legible than outline-only at small sizes)
        gd.rounded_rectangle([s // 2, s // 2, s // 2 + s, s // 2 + s],
                             radius=8,
                             fill=(*color, alpha // 2),
                             outline=(*color, min(255, alpha + 40)),
                             width=3)
        rad = math.radians(ang)
        gx = centre[0] + int(radius * math.cos(rad)) - s
        gy = centre[1] + int(radius * y_squish * math.sin(rad)) - s
        layer.alpha_composite(ghost, dest=(gx, gy))
    return Image.alpha_composite(panel.convert("RGBA"), layer).convert("RGB")


def draw_intent_arrow(panel: Image.Image,
                      tip: Tuple[int, int],
                      direction_deg: float = 250.0,
                      length: int = 220,
                      color=GREEN_BRIGHT) -> Image.Image:
    """A clean dashed arrow pointing at the gripper -> 'committed action being executed'."""
    w, h = panel.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rad = math.radians(direction_deg)
    # tail point is opposite the tip along the direction
    tail = (tip[0] - length * math.cos(rad), tip[1] - length * math.sin(rad))
    # dashed line: split into segments
    n_dash = 9
    for i in range(n_dash):
        if i % 2 == 0:
            t0 = i / n_dash
            t1 = (i + 1) / n_dash
            x0 = tail[0] + (tip[0] - tail[0]) * t0
            y0 = tail[1] + (tip[1] - tail[1]) * t0
            x1 = tail[0] + (tip[0] - tail[0]) * t1
            y1 = tail[1] + (tip[1] - tail[1]) * t1
            d.line([(x0, y0), (x1, y1)], fill=(*color, 230), width=8)
    # arrow head at tip
    head = 28
    perp = (math.cos(rad + math.pi / 2), math.sin(rad + math.pi / 2))
    base = (tip[0] - head * math.cos(rad), tip[1] - head * math.sin(rad))
    h1 = (base[0] + head * 0.55 * perp[0], base[1] + head * 0.55 * perp[1])
    h2 = (base[0] - head * 0.55 * perp[0], base[1] - head * 0.55 * perp[1])
    d.polygon([tip, h1, h2], fill=(*color, 245))
    # subtle outer glow
    glow = layer.filter(ImageFilter.GaussianBlur(radius=4))
    out = Image.alpha_composite(panel.convert("RGBA"), glow)
    out = Image.alpha_composite(out, layer)
    return out.convert("RGB")


def draw_unified_overlay(panel: Image.Image,
                         origin: Tuple[int, int],
                         token_n: Tuple[int, int, int],
                         boundary_after: int) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    """One consolidated HUD card containing the async timeline AND the token strip.

    Returns (composited image, card bbox).
    """
    n_committed, n_inpaint, n_masked = token_n
    n_total = n_committed + n_inpaint + n_masked
    cell = 50
    gap = 7
    strip_w = n_total * cell + (n_total - 1) * gap

    pad = 22
    title_h = 30
    timeline_h = 56     # 2 tracks of ~22 px each
    spacer = 14
    bracket_block_h = 42

    card_w = strip_w + 2 * pad
    card_h = pad + title_h + timeline_h + spacer + cell + bracket_block_h + pad

    w, h = panel.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = origin
    bbox = (x0, y0, x0 + card_w, y0 + card_h)

    # card backdrop
    d.rounded_rectangle([x0, y0, x0 + card_w, y0 + card_h],
                        radius=18, fill=HUD_BG, outline=HUD_BORDER, width=2)

    # ---- async timeline -----------
    tl_y = y0 + pad + title_h + 6
    label_w = 130
    track_h = 20
    track_gap = 12
    bar_x0 = x0 + pad + label_w
    bar_x1 = x0 + card_w - pad - 12

    # execution bar (full)
    d.rounded_rectangle([bar_x0, tl_y, bar_x1, tl_y + track_h],
                        radius=6, fill=(*GREEN, 240))
    # arrow tip
    d.polygon([(bar_x1, tl_y - 4),
               (bar_x1 + 14, tl_y + track_h // 2),
               (bar_x1, tl_y + track_h + 4)], fill=(*GREEN, 240))

    # inference bar (offset, gradient yellow->green)
    iy = tl_y + track_h + track_gap
    inf_x0 = bar_x0 + int((bar_x1 - bar_x0) * 0.18)
    inf_x1 = bar_x0 + int((bar_x1 - bar_x0) * 0.85)
    bar = Image.new("RGBA", (inf_x1 - inf_x0, track_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bw = inf_x1 - inf_x0
    for px in range(bw):
        t = px / max(1, bw - 1)
        r = int(YELLOW[0] * (1 - t) + GREEN[0] * t)
        g = int(YELLOW[1] * (1 - t) + GREEN[1] * t)
        b = int(YELLOW[2] * (1 - t) + GREEN[2] * t)
        bd.line([(px, 0), (px, track_h)], fill=(r, g, b, 240))
    rmask = Image.new("L", bar.size, 0)
    ImageDraw.Draw(rmask).rounded_rectangle([(0, 0), bar.size], radius=6, fill=255)
    layer.paste(bar, (inf_x0, iy), rmask)
    d.polygon([(inf_x1, iy - 4),
               (inf_x1 + 14, iy + track_h // 2),
               (inf_x1, iy + track_h + 4)], fill=(*GREEN, 240))

    # ---- token strip -----------
    sx = x0 + pad
    sy = y0 + pad + title_h + timeline_h + spacer
    for i in range(n_total):
        cx = sx + i * (cell + gap)
        if i < n_committed:
            fill = GREEN; outline = GREEN_BRIGHT
        elif i < n_committed + n_inpaint:
            fill = GREEN_BRIGHT; outline = (255, 255, 255)
        else:
            fill = YELLOW; outline = YELLOW_DIM
        d.rounded_rectangle([cx, sy, cx + cell, sy + cell],
                            radius=8, fill=(*fill, 245),
                            outline=(*outline[:3], 255), width=2)
        # drawing diagonal hatch on masked-future cells for extra differentiation
        if i >= n_committed + n_inpaint:
            for off in range(-cell, cell, 9):
                d.line([(cx + off, sy + cell), (cx + off + cell, sy)],
                       fill=(255, 255, 255, 35), width=1)

    # boundary line
    bx = sx + boundary_after * (cell + gap) - gap // 2
    d.line([(bx, sy - 12), (bx, sy + cell + 12)], fill=(*RED_BOUNDARY, 245), width=4)
    d.polygon([(bx - 9, sy - 18), (bx + 9, sy - 18), (bx, sy - 4)],
              fill=(*RED_BOUNDARY, 245))

    # bracket markers (no labels)
    seg = [
        (0, n_committed, GREEN_BRIGHT),
        (n_committed, n_committed + n_inpaint, WHITE),
        (n_committed + n_inpaint, n_total, YELLOW),
    ]
    by = sy + cell + 14
    for s, e, color in seg:
        sxa = sx + s * (cell + gap)
        exa = sx + e * (cell + gap) - gap
        d.line([(sxa, by), (exa, by)], fill=(*color, 240), width=3)
        d.line([(sxa, by - 4), (sxa, by + 4)], fill=(*color, 240), width=3)
        d.line([(exa, by - 4), (exa, by + 4)], fill=(*color, 240), width=3)

    out = Image.alpha_composite(panel.convert("RGBA"), layer).convert("RGB")
    return out, bbox


# ============================================================================
# Per-panel composition
# ============================================================================

def build_panel_1(p: Image.Image) -> Image.Image:
    return p


def build_panel_2(p: Image.Image) -> Image.Image:
    return p


def build_panel_3(p: Image.Image) -> Image.Image:
    return p


# ============================================================================
# Top-level composition
# ============================================================================

def compose() -> Image.Image:
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)

    # ----- panels -----
    raws = [Image.open(p).convert("RGB") for p in PANEL_PATHS]
    widths = [LEFT_W, MID_W, RIGHT_W]
    panels = [fit_panel(img, w, PANEL_H) for img, w in zip(raws, widths)]
    panels[0] = build_panel_1(panels[0])
    panels[1] = build_panel_2(panels[1])
    panels[2] = build_panel_3(panels[2])

    cursor_x = PADDING_X
    panel_y = PADDING_TOP
    for panel, tw in zip(panels, widths):
        mask = rounded_mask((tw, PANEL_H), PANEL_RADIUS)
        canvas.paste(panel, (cursor_x, panel_y), mask)
        cursor_x += tw + GAP

    return canvas


def main() -> None:
    fig = compose()
    fig.save(OUT_PNG, "PNG", optimize=True)
    print(f"-> {OUT_PNG}  ({fig.size[0]}x{fig.size[1]})")


if __name__ == "__main__":
    main()
