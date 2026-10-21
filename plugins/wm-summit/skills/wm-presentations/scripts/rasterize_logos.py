"""Rasterize the W&M SVG lockups to transparent PNGs (python-pptx cannot place SVG).

    python3 scripts/rasterize_logos.py

Writes assets/logos/<name>.png at up to 4x the SVG's own size, capped at 2400px wide.
Needs `playwright` with Chromium (pip install playwright && python3 -m playwright install chromium).
Only needed when the SVGs change — the PNGs are bundled.
"""
from pathlib import Path
import re
import sys

LOGOS = Path(__file__).resolve().parent.parent / "assets" / "logos"


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright missing: pip install playwright && python3 -m playwright install chromium")
        return 2
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for svg in sorted(LOGOS.glob("*.svg")):
            text = svg.read_text(encoding="utf-8")
            m = re.search(r'width="([\d.]+)"\s+height="([\d.]+)"', text)
            w, h = (float(m.group(1)), float(m.group(2))) if m else (800.0, 400.0)
            scale = min(4.0, 2400.0 / w)
            page = browser.new_page(viewport={"width": int(w), "height": int(h)}, device_scale_factor=scale)
            page.goto(svg.as_uri())
            page.wait_for_timeout(150)
            out = svg.with_suffix(".png")
            page.screenshot(path=str(out), omit_background=True)
            print(f"{out.name}  {int(w*scale)}x{int(h*scale)}")
            page.close()
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
