#!/usr/bin/env python3
"""Rasterise the letterhead logos from their SVG sources into the PNGs that Word embeds.

Word renders PNG everywhere; SVG only in recent versions, and python-docx cannot embed it. The PNGs are
shipped pre-built, so this runs only when a source SVG changes:

    pip install cairosvg
    python3 prepare_logos.py

Outputs (assets/logos/), each 2400 px wide:
  wm-horizontal-blue.png   the Summit's horizontal lockup (site masthead), as supplied
  GCS-Secondary-Blue.png   Global Citizen Solutions' official one-line lockup (symbol + wordmark) in GCS blue
"""
from pathlib import Path

import cairosvg

LOGOS = Path(__file__).resolve().parent.parent / "assets" / "logos"
WIDTH = 2400


def main() -> None:
    for svg, png in (("wm-horizontal-blue.svg", "wm-horizontal-blue.png"), ("GCS-Secondary-Blue.svg", "GCS-Secondary-Blue.png")):
        cairosvg.svg2png(url=str(LOGOS / svg), write_to=str(LOGOS / png), output_width=WIDTH)
        print(f"{png}: {(LOGOS / png).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
