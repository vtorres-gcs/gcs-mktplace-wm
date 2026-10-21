"""Build the editable deck HTML, render PNGs with Playwright, assemble the PDF.

    import sys
    from pathlib import Path
    SKILL_DIR = Path("<the folder you read SKILL.md from>")
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    from summit_assets import *            # LOGO_GCS_WHITE, embed_image, flag_uri …
    from summit_render import build_document, render, pngs_to_pdf, CANVASES

HTML is always written from Python (Path.write_text) — never a shell heredoc, which
corrupts base64 through $ and backtick interpolation.
"""

from pathlib import Path
import asyncio
import os

from summit_assets import FONTS_CSS, TOKENS_CSS, BASE_CSS

# name -> (width, height, canvas class)
CANVASES = {
    "carousel-4x5": (1080, 1350, "canvas-feed"),
    "carousel-1x1": (1080, 1080, "canvas-feed"),
    "post":         (1080, 1350, "canvas-feed"),
    "story":        (1080, 1920, "canvas-story"),
    "linkedin-landscape": (1200, 627, "canvas-landscape"),
    "linkedin-square":    (1080, 1080, "canvas-feed"),
}


def build_document(slides_html: list, canvas: str, title: str) -> str:
    """One standalone HTML file: fonts + tokens + base css inlined, one [data-slide] per slide.

    Each item of `slides_html` is the INNER markup of one slide (see slide-library.md).
    Wrap-level classes (ground tone etc.) are passed as a tuple: (inner_html, "g-deep").
    """
    w, h, cls = CANVASES[canvas]
    out = []
    for i, item in enumerate(slides_html, 1):
        inner, extra = (item if isinstance(item, tuple) else (item, "g-navy"))
        out.append(
            f'<div data-slide="{i}" class="slide {cls} {extra}" style="width:{w}px; height:{h}px;">{inner}</div>'
        )
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{title}</title>\n<style>\n{FONTS_CSS}\n{TOKENS_CSS}\n{BASE_CSS}\n</style></head><body>\n"
        + "\n".join(out)
        + "\n</body></html>"
    )


async def render(html_path: str, out_dir: str, prefix: str, w: int, h: int) -> list:
    """Screenshot every [data-slide]. Idempotent: reloads the HTML, overwrites the PNGs."""
    from playwright.async_api import async_playwright
    paths = []
    os.makedirs(out_dir, exist_ok=True)
    async with async_playwright() as p:
        # --no-sandbox is required in this execution environment; never omit it.
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = await browser.new_page(viewport={"width": w + 100, "height": h + 100})
        await page.goto(f"file://{html_path}", wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(500)
        slides = await page.query_selector_all("[data-slide]")
        for i, el in enumerate(slides, 1):
            name = f"{prefix}_slide_{i:02d}.png" if len(slides) > 1 else f"{prefix}.png"
            out = os.path.join(out_dir, name)
            await el.screenshot(path=out)
            paths.append(out)
        await browser.close()
    return paths


def render_sync(*a, **k):
    return asyncio.run(render(*a, **k))


def pngs_to_pdf(png_paths: list, pdf_path: str) -> str:
    from PIL import Image
    images = [Image.open(p).convert("RGB") for p in png_paths]
    images[0].save(pdf_path, save_all=True, append_images=images[1:], resolution=150)
    return pdf_path
