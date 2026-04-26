"""
Step 3: export the final cover figure as PDF (and a smaller draft PNG).
The master PNG is already produced by 02_compose.py. We embed it in a PDF at
its native resolution so LaTeX can include it without re-rasterising.
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
COVER_DIR = HERE.parent
SRC_PNG = COVER_DIR / "cover_figure_final.png"
OUT_PDF = COVER_DIR / "cover_figure_final.pdf"
DRAFT_PNG = COVER_DIR / "cover_figure_draft.png"


def main() -> None:
    img = Image.open(SRC_PNG).convert("RGB")

    # Smaller draft for quick previewing
    draft = img.resize((1800, img.size[1] * 1800 // img.size[0]), Image.LANCZOS)
    draft.save(DRAFT_PNG, "PNG", optimize=True)
    print(f"-> {DRAFT_PNG}  ({draft.size[0]}x{draft.size[1]})")

    # PDF — Pillow embeds the raster directly. Set DPI so physical size is sane
    # (target ~7" wide @ 600 DPI -> 4200 px; we have 3600 px so ~600 DPI works).
    img.save(OUT_PDF, "PDF", resolution=600.0)
    print(f"-> {OUT_PDF}")


if __name__ == "__main__":
    main()
