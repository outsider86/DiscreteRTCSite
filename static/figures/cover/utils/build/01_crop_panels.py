"""
Step 1: crop the three source frames into per-panel images.

We use the same crop box for all three frames so the table/turntable scale is
identical across the triptych. Output: build/panel_{1,2,3}_raw.jpg
"""
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[4]
FRAMES = ROOT / "DiscreteRTCSite" / "Videos" / "DynamicalPNP" / "frames"
OUT = Path(__file__).resolve().parent.parent / "build"
OUT.mkdir(exist_ok=True)

# (frame_index, role)
SELECTIONS = [
    (26, "panel_1_raw"),   # Start
    (28, "panel_2_raw"),   # Mediate
    (30, "panel_3_raw"),   # Final
]

# Source frames are 1920x1080. Tight crop concentrating on the picking area
# only: gripper (top), suction cup, cube + red mat, and the surrounding plate.
# Drops the entire robot body, second arm, phone clock, lab clutter.
#
# After eyeballing frames 26/28/30, the action lives in:
#   x ~ [540, 1140]   (600 px wide, gripper column + plate)
#   y ~ [340, 920]    (580 px tall, gripper top down to below cube)
# Aspect ~1.03:1 -> near-square, so all 3 panels can share the same proportions.
CROP_BOX = (700, 340, 1140, 770)   # (left, top, right, bottom) -> 440x430

# Mild post-crop enhancement so the three panels feel uniform & punchy.
COLOR_BOOST    = 1.08
CONTRAST_BOOST = 1.07
BRIGHT_BOOST   = 1.02


def process(frame_idx: int, name: str) -> None:
    src = FRAMES / f"frame_{frame_idx:04d}.jpg"
    img = Image.open(src).convert("RGB")
    img = img.crop(CROP_BOX)
    img = ImageEnhance.Color(img).enhance(COLOR_BOOST)
    img = ImageEnhance.Contrast(img).enhance(CONTRAST_BOOST)
    img = ImageEnhance.Brightness(img).enhance(BRIGHT_BOOST)
    out = OUT / f"{name}.jpg"
    img.save(out, quality=95)
    print(f"  {src.name:>20} -> {out.relative_to(ROOT)}  ({img.size[0]}x{img.size[1]})")


def main() -> None:
    print(f"crop box (LTRB) = {CROP_BOX}")
    for idx, name in SELECTIONS:
        process(idx, name)


if __name__ == "__main__":
    main()
