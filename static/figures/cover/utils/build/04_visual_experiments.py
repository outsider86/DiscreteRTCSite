"""
Visual experiments: try several "calm down" treatments on the panel images so
that future colour overlays (action tokens, arrows, etc.) read on top.

Generates a comparison sheet labelled with the treatment name + per-panel
test outputs you can swap into the composer if you pick one.
"""
from __future__ import annotations
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent / "build"
EXPERIMENTS = HERE.parent / "experiments"
EXPERIMENTS.mkdir(exist_ok=True)

PANELS = [BUILD / f"panel_{i}_raw.jpg" for i in (1, 2, 3)]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    cand = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    if Path(cand).exists():
        return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


# ============================================================================
# Treatments
# ============================================================================

def t_original(img: Image.Image) -> Image.Image:
    return img.copy()


def t_desat_strong(img: Image.Image) -> Image.Image:
    """Drop saturation hard (~25% of original) -> background grayscale-ish."""
    return ImageEnhance.Color(img).enhance(0.25)


def t_grayscale(img: Image.Image) -> Image.Image:
    """Pure grayscale."""
    return ImageOps.grayscale(img).convert("RGB")


def t_keep_red_only(img: Image.Image, sat_keep: float = 1.60,
                    sat_drop: float = 0.0,
                    value_boost: float = 1.12,
                    bg_white_mix: float = 0.22) -> Image.Image:
    """Make red mat + purple cube pop, push everything else into a quiet
    grayscale-with-slight-white-wash base.

    - sat_keep: how much to amplify saturation inside the kept mask (>1 = punch).
    - sat_drop: saturation factor outside the mask (0 = full grayscale).
    - value_boost: brightness multiplier on kept pixels so they read against
      the desaturated/washed background.
    - bg_white_mix: alpha of a white wash mixed into the non-kept regions, so
      the photo recedes further. 0 = no wash."""
    hsv = np.asarray(img.convert("HSV"), dtype=np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # narrow red band: only hues within ~10 units of pure red survive
    hue_red = np.minimum(h, 255 - h) / 10.0
    hue_red_score = np.clip(1.0 - hue_red, 0.0, 1.0)
    # red mat is highly saturated -> require strong sat to qualify (rejects
    # the orange cables, which sit just outside the hue band anyway).
    sat_score_red = np.clip((s - 80) / 80.0, 0.0, 1.0)
    val_score_red = np.clip((v - 60) / 80.0, 0.0, 1.0)
    red_mask = hue_red_score * sat_score_red * val_score_red

    # purple band: real cube pixels live at hue ~200-225 with sat ~60-110.
    # Center on 210, widen to /28, and drop the sat threshold so the muted
    # cube actually qualifies for the mask.
    hue_purple_score = np.clip(1.0 - np.abs(h - 210) / 28.0, 0.0, 1.0)
    sat_score_purple = np.clip((s - 45) / 60.0, 0.0, 1.0)
    val_score_purple = np.clip((v - 50) / 70.0, 0.0, 1.0)
    purple_mask = hue_purple_score * sat_score_purple * val_score_purple

    mask = np.maximum(red_mask, purple_mask)
    # soften mask edges so the boundary doesn't read as a hard cutout
    mask = np.clip(mask ** 0.75, 0.0, 1.0)

    # Saturation: amplified inside mask, crushed outside. Add a floor so the
    # low-saturation cube pixels actually become visibly purple, not just
    # slightly-less-gray.
    factor = sat_drop + (sat_keep - sat_drop) * mask
    new_s = np.maximum(s * factor, 170.0 * mask)
    new_s = np.clip(new_s, 0, 255)
    # value: boost only inside mask so red/purple gain a bit of luminance
    new_v = np.clip(v * (1.0 + (value_boost - 1.0) * mask), 0, 255)

    out_hsv = np.stack([h, new_s, new_v], axis=-1).astype(np.uint8)
    out = Image.fromarray(out_hsv, "HSV").convert("RGB")

    if bg_white_mix > 0:
        # Mix in a white wash everywhere, then re-paste the kept regions on top
        # so only the background (low-mask) gets washed out.
        out_arr = np.asarray(out, dtype=np.float32)
        white = np.full_like(out_arr, 255.0)
        wash_alpha = bg_white_mix * (1.0 - mask)[..., None]
        out_arr = out_arr * (1.0 - wash_alpha) + white * wash_alpha
        out = Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8), "RGB")

    return out


def t_keep_purple_only(img: Image.Image, sat_keep: float = 1.10,
                       sat_drop: float = 0.08) -> Image.Image:
    """Keep only the purple cube saturated; desaturate everything else
    (including the red mat). Purple hue ~ 188 in PIL HSV (8-bit hue space)."""
    hsv = np.asarray(img.convert("HSV"), dtype=np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # narrow purple band only
    hue_purple = np.clip(1.0 - np.abs(h - 188) / 18.0, 0.0, 1.0)
    sat_score = np.clip((s - 60) / 90.0, 0.0, 1.0)
    val_score = np.clip((v - 50) / 90.0, 0.0, 1.0)
    mask = hue_purple * sat_score * val_score
    factor = sat_drop + (sat_keep - sat_drop) * mask
    new_s = np.clip(s * factor, 0, 255)
    out_hsv = np.stack([h, new_s, v], axis=-1).astype(np.uint8)
    return Image.fromarray(out_hsv, "HSV").convert("RGB")


def t_low_contrast(img: Image.Image) -> Image.Image:
    """Compress dynamic range -> overall flatter photo."""
    return ImageEnhance.Contrast(img).enhance(0.55)


def t_high_key_wash(img: Image.Image) -> Image.Image:
    """Brighten + lift midtones + reduce saturation -> diagram-like."""
    img = ImageEnhance.Color(img).enhance(0.45)
    img = ImageEnhance.Brightness(img).enhance(1.18)
    img = ImageEnhance.Contrast(img).enhance(0.78)
    return img


def t_blur_bg(img: Image.Image) -> Image.Image:
    """Light gaussian blur -> photo softer, less detail competition."""
    return img.filter(ImageFilter.GaussianBlur(radius=1.6))


def t_posterize(img: Image.Image) -> Image.Image:
    """Quantise to 4 levels per channel -> flat poster look."""
    return ImageOps.posterize(img, 3)


def t_overlay_white(img: Image.Image, alpha: float = 0.35) -> Image.Image:
    """Mix in a white overlay -> photo recedes, ready to take colour on top."""
    white = Image.new("RGB", img.size, (255, 255, 255))
    return Image.blend(img, white, alpha)


def t_desat_plus_white(img: Image.Image) -> Image.Image:
    """Combo: desaturate strongly + white wash -> very quiet base."""
    img = t_desat_strong(img)
    return t_overlay_white(img, alpha=0.30)


TREATMENTS = [
    ("original",        t_original),
    ("desaturate 0.25", t_desat_strong),
    ("grayscale",       t_grayscale),
    ("keep red+purple", t_keep_red_only),
    ("keep purple only", t_keep_purple_only),
    ("low contrast",    t_low_contrast),
    ("high-key wash",   t_high_key_wash),
    ("soft blur",       t_blur_bg),
    ("posterize",       t_posterize),
    ("white overlay",   t_overlay_white),
    ("desat + white",   t_desat_plus_white),
]


# ============================================================================
# Comparison sheet
# ============================================================================

def main() -> None:
    panel = Image.open(PANELS[1]).convert("RGB")    # use the middle frame
    panel = panel.resize((520, 510), Image.LANCZOS)
    pw, ph = panel.size

    cols = 2
    rows = (len(TREATMENTS) + cols - 1) // cols
    pad = 18
    label_h = 36
    sheet_w = cols * pw + (cols + 1) * pad
    sheet_h = rows * (ph + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (240, 240, 245))
    d = ImageDraw.Draw(sheet)
    font = load_font(22, bold=True)

    for i, (name, fn) in enumerate(TREATMENTS):
        r, c = divmod(i, cols)
        x = pad + c * (pw + pad)
        y = pad + r * (ph + label_h + pad)
        result = fn(panel)
        sheet.paste(result, (x, y + label_h))
        # label band
        d.rectangle([x, y, x + pw, y + label_h], fill=(30, 35, 45))
        d.text((x + 12, y + 8), f"[{i}] {name}", fill=(245, 245, 250), font=font)

        # also save the per-treatment variant on all 3 panels for easy preview
        for j, src_path in enumerate(PANELS):
            full = Image.open(src_path).convert("RGB")
            out = fn(full)
            slug = name.replace(" ", "_").replace("+", "plus")
            out.save(EXPERIMENTS / f"treat-{i:02d}_{slug}_panel{j+1}.png")

    sheet.save(EXPERIMENTS / "comparison_sheet.png", optimize=True)
    print(f"-> comparison sheet: {EXPERIMENTS / 'comparison_sheet.png'}")
    print(f"-> per-panel variants in {EXPERIMENTS}/treat-NN_*")


if __name__ == "__main__":
    main()
