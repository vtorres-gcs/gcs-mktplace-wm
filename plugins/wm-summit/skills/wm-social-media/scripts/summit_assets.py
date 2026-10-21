"""Wealth & Migration Summit 2026 — social asset loader and token sheet.

Everything a slide needs is built here and returned as strings:

  FONTS_CSS    @font-face rules, TTFs inlined (Caladea 400, Archivo 400/500/600)
  TOKENS_CSS   :root custom properties — the palette is READ FROM
               references/DESIGN.md at import time, so replacing that file with a
               newer export re-colours every future slide. Alpha roles, light
               sources and the type ramp are derived here, named, and nowhere else.
  BASE_CSS     the class vocabulary the slide templates use (see
               references/slide-library.md). Slides never write a literal
               font-size, rgba() or box-shadow; they use these classes and tokens.
  LOGO_GCS_WHITE / LOGO_GCS_WORDMARK_WHITE / LOGO_GCS_SYMBOL_WHITE
               Global Citizen Solutions marks (dark grounds only).
  LOGO_GCS_BLUE
               Global Citizen Solutions primary mark, blue (white grounds only).
  mast(on)     masthead HTML: the event's horizontal lockup, dark or light ground.
  marks(on)    footer marks HTML: Global Citizen Solutions + CNN Portugal, as in the site hero.
               Nothing is ever written above, beside or over the GCS mark.
  embed_image  user/client photo -> data: URI
  flag_uri     country flag (the one network call)

Standard library only. No repo checkout, no network (except flag_uri).

    import sys
    from pathlib import Path
    SKILL_DIR = Path("<the folder you read SKILL.md from>")
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    from summit_assets import FONTS_CSS, TOKENS_CSS, BASE_CSS, LOGO_GCS_WHITE, embed_image

Self-check (also verifies palette contrast):

    python3 scripts/summit_assets.py
"""

from pathlib import Path
import base64
import re
import urllib.error
import urllib.request

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
REFS = SKILL_DIR / "references"

_MIME = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".svg": "image/svg+xml", ".ttf": "font/ttf",
}


class MissingAsset(RuntimeError):
    """A required asset is not on disk (or not reachable)."""


def data_uri(path) -> str:
    p = Path(path)
    if not p.is_file():
        raise MissingAsset(
            f"asset not found: {p}\n  SKILL_DIR resolved to: {SKILL_DIR}\n"
            f"The skill folder was copied incompletely — re-copy all of it and run: "
            f"python3 {SKILL_DIR / 'scripts' / 'summit_assets.py'}"
        )
    mime = _MIME.get(p.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def embed_image(file_path) -> str:
    """Embed a user/client image as a data URI, MIME sniffed by magic bytes."""
    p = Path(file_path)
    if not p.is_file():
        raise MissingAsset(f"image not found: {p}")
    raw = p.read_bytes()
    head = raw[:12]
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    elif head.startswith(b"\xff\xd8\xff"):
        mime = "image/jpeg"
    elif head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        mime = "image/webp"
    elif raw.lstrip()[:5] in (b"<svg ", b"<?xml"):
        mime = "image/svg+xml"
    else:
        mime = _MIME.get(p.suffix.lower(), "image/jpeg")
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


# ----------------------------------------------------------------------------
# Palette — read from references/DESIGN.md (front matter, `colors:` block)
# ----------------------------------------------------------------------------

_REQUIRED = ["navy", "navy-deep", "navy-wash", "dawn-blue", "dawn-low",
             "gold", "gold-bright", "mist", "white"]


def parse_palette(design_md: Path = REFS / "DESIGN.md") -> dict:
    if not design_md.is_file():
        raise MissingAsset(f"DESIGN.md not found at {design_md}")
    text = design_md.read_text(encoding="utf-8")
    block = re.search(r"^colors:\s*\n((?:[ \t]+[\w-]+:\s*\"#[0-9A-Fa-f]{6}\"[ \t]*\n)+)",
                      text, re.M)
    if not block:
        raise ValueError("DESIGN.md: could not find a `colors:` block in the front matter")
    palette = {k: v.upper() for k, v in
               re.findall(r"([\w-]+):\s*\"(#[0-9A-Fa-f]{6})\"", block.group(1))}
    missing = [k for k in _REQUIRED if k not in palette]
    if missing:
        raise ValueError(f"DESIGN.md colors block is missing: {', '.join(missing)}")
    return palette


PALETTE = parse_palette()


def _rgb(hex_):
    h = hex_.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgba(name_or_hex, a):
    r, g, b = _rgb(PALETTE.get(name_or_hex, name_or_hex))
    return f"rgba({r},{g},{b},{a})"


# ----------------------------------------------------------------------------
# Fonts — Caladea (display) + Archivo (reading). Archivo is set at 400/500/600 only.
# ----------------------------------------------------------------------------

_FACES = [
    ("Caladea", 400, "normal", "Caladea-Regular.ttf"),
    ("Archivo", 400, "normal", "Archivo-400.ttf"),
    ("Archivo", 500, "normal", "Archivo-500.ttf"),
    ("Archivo", 600, "normal", "Archivo-600.ttf"),
]


def build_fonts_css() -> str:
    return "\n".join(
        f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{w};"
        f"font-display:block;src:url('{data_uri(ASSETS / 'fonts' / ttf)}') format('truetype');}}"
        for fam, w, style, ttf in _FACES
    )


FONTS_CSS = build_fonts_css()

# ----------------------------------------------------------------------------
# Logos — Global Citizen Solutions. White marks on dark grounds, the blue primary on white (marks() picks the right file per ground).
# ----------------------------------------------------------------------------

LOGO_GCS_BLUE = data_uri(ASSETS / "logos" / "GCS-Primary-Blue.png")
LOGO_GCS_WHITE = data_uri(ASSETS / "logos" / "GCS-Primary-White.png")
LOGO_GCS_WORDMARK_WHITE = data_uri(ASSETS / "logos" / "GCS-Secondary-White.png")
LOGO_GCS_SYMBOL_WHITE = data_uri(ASSETS / "logos" / "GCS-Symbol-White.png")

# ----------------------------------------------------------------------------
# Asset library — everything under assets/ the skill may use, by key.
# `category.name` -> path relative to assets/. Rules of use: references/FACTS.md (partner marks need the user's confirmation).
# ----------------------------------------------------------------------------

ASSET_LIBRARY = {
    # Summit marks (supplied) — "light" = for dark grounds, "blue" = for white grounds
    "summit.horizontal-white": "logos/w&m-horizontal White.svg",
    "summit.horizontal-blue":  "logos/w&m-horizontal blue.svg",
    "summit.default-white":    "logos/w&m-default white.svg",
    "summit.default-blue":     "logos/w&m-default blue.svg",
    "summit.vertical-white":   "logos/w&m-vertical white.svg",
    "summit.vertical-blue":    "logos/w&m-vertical blue.svg",
    "summit.symbol":           "logos/w&m-symbol.svg",
    "summit.symbol-gold":      "img/Symbol-W&MS.svg",
    # Global Citizen Solutions marks (white for dark grounds, primary blue for white grounds)
    "gcs.primary-blue":        "logos/GCS-Primary-Blue.png",
    "gcs.primary-white":       "logos/GCS-Primary-White.png",
    "gcs.wordmark-white":      "logos/GCS-Secondary-White.png",
    "gcs.symbol-white":        "logos/GCS-Symbol-White.png",
    "gcs.primary-white-svg":   "img/GCS-Primary-White.svg",
    "gcs.hero-symbol":         "img/hero-gcs-symbol.svg",
    "gcs.hero-text":           "img/hero-gcs-text.svg",
    "gcs.footer-symbol-navy":  "logos/gcs-footer-symbol-navy.svg",
    "gcs.footer-text-navy":    "logos/gcs-footer-text-navy.svg",
    "gcs.footer-symbol-white": "logos/gcs-footer-symbol-white.svg",
    "gcs.footer-text-white":   "logos/gcs-footer-text-white.svg",
    # Photography (landing-page imagery, on the client's replacement list)
    "photo.bridge":            "img/hero-1920.webp",
    "photo.bridge-1080p":      "img/hero.jpg",
    "photo.bridge-small":      "img/hero-900.webp",
    "photo.bridge-cover":      "img/carousel-cover-2160.webp",
    "photo.venue":             "img/epic-sana-1440.webp",
    "photo.venue-small":       "img/epic-sana-900.webp",
    "photo.reception":         "img/claim-your-seat.webp",
    "photo.water-night":       "img/nocturne-texture-1440.webp",
    "photo.water-night-small": "img/nocturne-texture-900.webp",
    "photo.banner-maat-dark":  "img/carousel-banner-maat-dark-1600.webp",
    "photo.banner-castle-dark":"img/carousel-banner-castle-dark-1600.webp",
    # Licensed stock-library photographs of Lisbon (real photos, rights cleared)
    "photo.vasco-da-gama-sunrise": "img/lisbon-vasco-da-gama-sunrise-2400.webp",
    "photo.lisbon-sunset":         "img/lisbon-sunset-panorama-2400.webp",
    "photo.arco-rua-augusta":      "img/lisbon-arco-rua-augusta-2400.webp",
    # Finished artwork — never reuse as a photograph
    "artwork.og-share":        "img/og-share.jpg",
    # Partner / media marks as shown on the landing page (white or light, dark grounds only).
    # Role of each (sponsor / partner / media) is NOT confirmed — see references/FACTS.md, "Partners and media".
    "partner.blue-crow":       "img/Blue-Crow.png",
    "partner.lisboa-2030":     "img/LISBOA-2030.png",
    "partner.optimize":        "img/Optimize-Investment-Partners_Horizontal.png",
    "partner.atlantico-europa":"img/atlantico-europa.svg",
    "partner.capital-partners":"img/capitalpartners.png",
    "partner.cascais-ventures":"img/cascais-ventures.svg",
    "partner.cnn-portugal":    "img/cnn-portugal.png",
    "partner.cnn-portugal-white":"img/hero-cnn-portugal.png",
    "partner.goldcrest":       "img/goldcrest.png",
    "partner.joao-m-barbosa":  "img/joao-m-barbosa.svg",
    "partner.portuguese-chamber":"img/portuguese-chamber.png",
    # CNN Portugal (supplied) - white for dark grounds, red (Float Final) for white grounds
    "cnn.white":               "logos/Logo CNN PORTUGAL Float BRANCO Final.png",
    "cnn.black":               "logos/Logo CNN PORTUGAL Float BLACK Final.png",
    "cnn.red":                 "logos/Logo CNN PORTUGAL Float Final.png",
    "cnn.square":              "logos/Logo CNN PORTUGAL Final.png",
    # Small icons from the registration section
    "icon.arrow-right":        "img/reg-arrow-right.svg",
    "icon.check":              "img/reg-check.svg",
    "icon.users":              "img/reg-users.svg",
}


def asset_path(key: str) -> Path:
    """Absolute path of a library asset, e.g. asset_path("photo.bridge")."""
    try:
        rel = ASSET_LIBRARY[key]
    except KeyError:
        raise KeyError(f"unknown asset {key!r}; run list_assets() for the keys") from None
    return ASSETS / rel


def asset_uri(key: str) -> str:
    """Library asset as a data: URI — the only form that renders from file:// in Playwright."""
    return data_uri(asset_path(key))


def speaker_path(slug: str) -> Path:
    """Headshot by slug (assets/speakers/<slug>.webp). Prefer facts.speaker_photo(name), which also
    checks the name against the site's roster; a file here does not by itself confirm a speaker."""
    return ASSETS / "speakers" / f"{slug}.webp"


def list_assets(category: str = None) -> list:
    """[(key, relative path)] — optionally for one category (summit, gcs, photo, artwork, partner, icon)."""
    return [(k, v) for k, v in ASSET_LIBRARY.items() if category is None or k.startswith(category + ".")]


# ----------------------------------------------------------------------------
# Logos in context - one place decides which file goes on which ground
# ----------------------------------------------------------------------------

def mast(on: str = "dark") -> str:
    """Masthead: the event's horizontal lockup (W mark + name, one line, no GCS line), top-left.
    on='dark' (navy / photo) or 'light' (white slide)."""
    key = "summit.horizontal-white" if on == "dark" else "summit.horizontal-blue"
    return (f'<div class="mast"><span class="lockup"><img class="logo-event" src="{asset_uri(key)}" '
            f'alt="Wealth and Migration Summit"></span></div>')


def marks(on: str = "dark") -> str:
    """Global Citizen Solutions + CNN Portugal, side by side, as in the site hero.

    The GCS mark stands alone: no label above, beside or over it (its own name is in the mark).
    Dark grounds: white GCS lockup + white CNN. White grounds: primary blue GCS lockup + red CNN."""
    if on == "dark":
        gcs = f'<span class="logo-gcs-wrap"><img class="logo-gcs" src="{LOGO_GCS_WHITE}" alt="Global Citizen Solutions"></span>'
        cnn = f'<img class="logo-cnn" src="{asset_uri("cnn.white")}" alt="CNN Portugal">'
    else:
        gcs = f'<span class="logo-gcs-wrap"><img class="logo-gcs" src="{LOGO_GCS_BLUE}" alt="Global Citizen Solutions"></span>'
        cnn = f'<img class="logo-cnn" src="{asset_uri("cnn.red")}" alt="CNN Portugal">'
    return f'<div class="marks">{gcs}{cnn}</div>'


# ----------------------------------------------------------------------------
# Tokens
# ----------------------------------------------------------------------------


def build_tokens_css() -> str:
    p = PALETTE
    colours = "\n".join(f"  --{k}: {v};" for k, v in p.items())
    return f""":root {{
{colours}
  /* named alphas — every colour below full opacity has a role */
  --rule: {_rgba('mist', .16)};
  --rule-strong: {_rgba('mist', .32)};
  --mist-dim: {_rgba('mist', .72)};
  --rule-on-paper: {_rgba('navy', .16)};
  --rule-strong-on-paper: {_rgba('navy', .32)};
  --ink-soft: {_rgba('navy', .72)};
  --scrim-chip: {_rgba('navy-deep', .72)};
  --gold-edge: {_rgba('gold', .35)};
  --gold-veil: {_rgba('gold', .12)};
  /* the two lights of a photographic scrim: one rises from the ground, one crosses from the text side */
  --scrim-rise: linear-gradient(to top, {_rgba('navy-deep', .96)} 0%, {_rgba('navy-deep', .86)} 26%, {_rgba('navy-deep', .5)} 52%, {_rgba('navy-deep', 0)} 80%);
  --scrim-cross: linear-gradient(to right, {_rgba('navy-wash', .92)} 0%, {_rgba('navy-wash', .6)} 42%, {_rgba('navy-wash', 0)} 85%);
  --scrim-flat: {_rgba('navy-deep', .62)};
  /* the cover wash, fitted to the client's reference cover (20 Oct 2026): a dawn-blue tint over the whole photograph, 75% at the
     masthead easing to ~70% where the service line and headline sit (the reference is ~50%; the gold service line needs 3:1), then navy-wash closing to ~96% at the foot where the marks sit */
  --scrim-cover: linear-gradient(to bottom,
    {_rgba('dawn-blue', .75)} 0%, {_rgba('dawn-blue', .60)} 17%, {_rgba('dawn-blue', .56)} 35%, {_rgba('dawn-blue', .70)} 42%,
    {_rgba('dawn-blue', .70)} 52%, {_rgba('navy-wash', .74)} 67%, {_rgba('navy-wash', .80)} 78%, {_rgba('navy-wash', .94)} 89%, {_rgba('navy-wash', .96)} 100%);
  --scrim-top: linear-gradient(to bottom, {_rgba('navy-deep', .72)} 0%, {_rgba('navy-deep', 0)} 30%);
  --line-gold: linear-gradient(to bottom, {p['gold']} 0%, {_rgba('gold', .35)} 100%);
  /* light sources — nothing else casts a shadow */
  --glow-mark: 0 0 22px {_rgba('gold', .55)};
  --glow-line: 0 0 24px {_rgba('gold', .35)};
  --glow-dot: 0 0 28px 4px {_rgba('gold', .55)};
  --lift-night: 0 80px 180px -100px rgba(0,0,0,.85), 0 0 0 2px {_rgba('gold', .35)};
  /* families */
  --font-serif: Caladea, Georgia, 'Times New Roman', serif;
  --font-sans: Archivo, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
  /* the ten-step ramp, canvas scale (feed 1080 wide). The ramp is closed. */
  --t-display: 96px;  --lh-display: .95;  --ls-display: -.015em;
  --t-headline: 76px; --lh-headline: 1;   --ls-headline: -.01em;
  --t-title: 56px;    --lh-title: 1.05;   --ls-title: -.005em;
  --t-subtitle: 44px; --lh-subtitle: 1.05; --ls-subtitle: .005em;
  --t-lead: 42px;     --lh-lead: 1.5;
  --t-body: 38px;     --lh-body: 1.55;
  --t-session: 40px;  --lh-session: 1.2;
  --t-datum: 32px;    --lh-datum: 1.4;
  --t-label: 28px;    --ls-label: .16em;
  --t-label-sm: 24px;
  /* canvas geometry */
  --pad-x: 125px; --pad-top: 125px; --pad-bottom: 125px;   /* the client's reference cover: 125 on every side */
}}
.canvas-story {{
  --t-display: 92px; --t-headline: 72px; --t-title: 54px; --t-lead: 40px;
  --t-body: 36px; --t-session: 38px;
  --pad-x: 125px; --pad-top: 250px; --pad-bottom: 310px;
}}
.canvas-landscape {{
  --t-display: 76px; --t-headline: 60px; --t-datum: 28px; --t-label: 26px;
  --pad-x: 72px; --pad-top: 64px; --pad-bottom: 64px;
}}
/* the Hour Rule: a slide takes the tone of its position in the arc */
.g-navy {{ --ground: var(--navy); }}
.g-deep {{ --ground: var(--navy-deep); }}
.g-low  {{ --ground: var(--dawn-low); }}
.g-dawn {{ --ground: var(--dawn-blue); }}
.g-white {{ --ground: var(--white); }}
"""


TOKENS_CSS = build_tokens_css()

BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--navy-deep); display: flex; flex-direction: column; align-items: center; gap: 40px; padding: 40px; }
.slide { position: relative; overflow: hidden; flex-shrink: 0; background: var(--ground, var(--navy)); color: var(--white);
  font-family: var(--font-sans); font-weight: 400; -webkit-font-smoothing: antialiased; }
.frame { position: absolute; inset: 0; z-index: 2; display: flex; flex-direction: column;
  padding: var(--pad-top) var(--pad-x) var(--pad-bottom); }
.stack { display: flex; flex-direction: column; }
.grow { flex: 1; }
.centre { justify-content: center; }
.end { justify-content: flex-end; }
.between { justify-content: space-between; }
.gap-s { gap: 16px; } .gap-m { gap: 32px; } .gap-l { gap: 48px; }

/* type — ten steps */
.display  { font-family: var(--font-serif); font-size: var(--t-display);  line-height: var(--lh-display);  letter-spacing: var(--ls-display);  font-weight: 400; color: var(--white); }
.headline { font-family: var(--font-serif); font-size: var(--t-headline); line-height: var(--lh-headline); letter-spacing: var(--ls-headline); font-weight: 400; color: var(--white); }
.title    { font-family: var(--font-serif); font-size: var(--t-title);    line-height: var(--lh-title);    letter-spacing: var(--ls-title);    font-weight: 400; color: var(--white); }
.subtitle { font-family: var(--font-serif); font-size: var(--t-subtitle); line-height: var(--lh-subtitle); letter-spacing: var(--ls-subtitle); font-weight: 400; color: var(--white); }
.session  { font-family: var(--font-serif); font-size: var(--t-session);  line-height: var(--lh-session);  font-weight: 400; color: var(--white); }
.lead     { font-family: var(--font-sans);  font-size: var(--t-lead);     line-height: var(--lh-lead);     letter-spacing: .005em; font-weight: 400; color: var(--white); }
.body     { font-family: var(--font-sans);  font-size: var(--t-body);     line-height: var(--lh-body);     letter-spacing: .005em; font-weight: 400; color: var(--mist); }
.datum    { font-family: var(--font-sans);  font-size: var(--t-datum);    line-height: var(--lh-datum);    letter-spacing: .02em;  font-weight: 400; color: var(--mist); font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1; }
.label    { font-family: var(--font-sans);  font-size: var(--t-label);    line-height: 1; letter-spacing: var(--ls-label); font-weight: 500; text-transform: uppercase; color: var(--mist); }
.label-sm { font-family: var(--font-sans);  font-size: var(--t-label-sm); line-height: 1; letter-spacing: var(--ls-label); font-weight: 500; text-transform: uppercase; color: var(--mist); }
.dim { color: var(--mist); }
.quiet { color: var(--mist-dim); }
.ink-gold { color: var(--gold); }
.ink-gold-bright { color: var(--gold-bright); }
.ink-white { color: var(--white); }

/* masthead: the gold square lamp + the name */
.mast { display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.lockup { display: inline-flex; align-items: center; gap: 18px; }
.lamp-sq { display: block; width: 16px; height: 16px; background: var(--gold); box-shadow: var(--glow-mark); flex-shrink: 0; }
.lockup .label { color: var(--white); }
/* service line: the date-and-place datum in gold, as on the reference cover - no lamp. The only label allowed above a headline (with the day marker). */
.service { display: block; color: var(--gold); font-weight: 600; letter-spacing: .03em; }
.day { color: var(--gold); }

/* rules */
.rule { border-top: 1px solid var(--rule); }
.rule-strong { border-top: 1px solid var(--rule-strong); }
.mark-gold { display: block; width: 96px; height: 4px; background: var(--gold); }

/* the one lit block (one per canvas) */
.lit { display: inline-flex; align-items: center; background: var(--gold); color: var(--navy); padding: 22px 32px; font-family: var(--font-sans); font-size: var(--t-label); line-height: 1; letter-spacing: var(--ls-label); font-weight: 500; text-transform: uppercase; }

/* photographic material */
.photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
.scrim-rise { position: absolute; inset: 0; background: var(--scrim-rise); }
.scrim-cross { position: absolute; inset: 0; background: var(--scrim-cross); }
.scrim-flat { position: absolute; inset: 0; background: var(--scrim-flat); }
.scrim-top { position: absolute; inset: 0; background: var(--scrim-top); }
/* the cover wash (see --scrim-cover) */
.scrim-cover { position: absolute; inset: 0; background: var(--scrim-cover); }
.plate { position: relative; overflow: hidden; flex-shrink: 0; }
.plate img { display: block; width: 100%; height: 100%; object-fit: cover; }
.plate-fade img { -webkit-mask-image: linear-gradient(to bottom, #000 55%, transparent 100%); mask-image: linear-gradient(to bottom, #000 55%, transparent 100%); }
.caption { position: absolute; left: 0; bottom: 0; padding: 14px 22px; background: var(--scrim-chip); }
.plate-initials { background: var(--dawn-low); display: flex; align-items: center; justify-content: center; }

/* the wet-street echo under a heading: a mirrored sliver, never a second headline */
.reflect { position: relative; height: .44em; overflow: hidden; opacity: .2; filter: blur(1.2px); pointer-events: none;
  -webkit-mask-image: linear-gradient(to bottom, #000, transparent); mask-image: linear-gradient(to bottom, #000, transparent); }
.reflect > * { transform: scaleY(-1); }

/* the timed line (signature) */
.timed { list-style: none; position: relative; padding-left: 56px; }
.timed::before { content: ""; position: absolute; left: 6px; top: 0; bottom: 0; width: 4px; background: var(--line-gold); box-shadow: var(--glow-line); }
.station { position: relative; display: grid; grid-template-columns: 170px 1fr; gap: 32px; align-items: baseline; padding: 28px 0; border-top: 1px solid var(--rule); }
.station:first-child { border-top: 0; }
.station-solo { grid-template-columns: 1fr; }
.station::before { content: ""; position: absolute; left: -56px; top: 38px; width: 16px; height: 16px; border-radius: 50%; background: var(--navy-deep); border: 3px solid var(--gold); }
.station.is-active::before { background: var(--gold); box-shadow: var(--glow-dot); }
.station.is-active .session { color: var(--gold-bright); }

/* ledger: figures and descriptions between hairlines (no boxes) */
.ledger { display: flex; flex-direction: column; }
.ledger-row { display: grid; grid-template-columns: auto 1fr; gap: 40px; align-items: baseline; padding: 30px 0; border-top: 1px solid var(--rule); }
.ledger-row:last-child { border-bottom: 1px solid var(--rule-strong); }
.ledger-row .subtitle { color: var(--gold); min-width: 200px; }

/* ruled table (comparisons) — hairlines, no box */
.rtable { display: flex; flex-direction: column; }
.rtable-row { display: grid; grid-template-columns: var(--cols, 1.3fr repeat(3, 1fr)); gap: 24px; align-items: baseline; padding: 26px 0; border-top: 1px solid var(--rule); }
.rtable-row:last-child { border-bottom: 1px solid var(--rule-strong); }
.rtable-head { align-items: end; border-top: 0; }
.flag { display: block; width: 54px; height: 36px; object-fit: cover; margin-bottom: 14px; }

/* ruled entries (audience, themes) */
.entries { display: flex; flex-direction: column; }
.entry { display: flex; flex-direction: column; gap: 10px; padding: 28px 0; border-top: 1px solid var(--rule); }
.entry:last-child { border-bottom: 1px solid var(--rule-strong); }

/* the register panel: the only paper */
.panel { background: var(--white); color: var(--navy); box-shadow: var(--lift-night); padding: 80px; display: flex; flex-direction: column; gap: 40px; }
.panel .headline, .panel .title, .panel .subtitle { color: var(--navy); }
.panel .lead { color: var(--navy); }
.panel .body, .panel .datum { color: var(--ink-soft); }
.panel .label, .panel .label-sm { color: var(--ink-soft); }
.panel .rule { border-top-color: var(--rule-on-paper); }

/* logos: sized by class, never by inline style. The GCS mark stands alone. */
.logo-event { display: block; width: 705px; height: auto; }
.marks { display: flex; align-items: center; gap: 40px; flex-shrink: 0; }
.logo-gcs-wrap { display: inline-flex; align-items: center; gap: 14px; }
.logo-gcs { display: block; height: 80px; width: auto; }
.logo-cnn { display: block; height: 80px; width: auto; }
.canvas-landscape .logo-event { width: 460px; height: auto; } .canvas-landscape .logo-gcs { height: 56px; } .canvas-landscape .logo-cnn { height: 52px; } .canvas-landscape .marks { gap: 40px; }

/* white slide: alternates with navy. Navy ink; gold only as a mark (rule, dot, lamp, lit block), never as text. */
.g-white { color: var(--navy); }
.g-white .display, .g-white .headline, .g-white .title, .g-white .subtitle, .g-white .session, .g-white .lead { color: var(--navy); }
.g-white .body, .g-white .datum, .g-white .label, .g-white .label-sm, .g-white .dim, .g-white .quiet { color: var(--ink-soft); }
.g-white .service, .g-white .day, .g-white .lockup .label, .g-white .swipe { color: var(--navy); }
.g-white .rule, .g-white .ledger-row, .g-white .station, .g-white .entry, .g-white .rtable-row { border-top-color: var(--rule-on-paper); }
.g-white .ledger-row:last-child, .g-white .entry:last-child, .g-white .rtable-row:last-child { border-bottom-color: var(--rule-strong-on-paper); }
.g-white .ledger-row .subtitle { color: var(--navy); }
.g-white .station::before { background: var(--white); }
.g-white .station.is-active::before { background: var(--gold); }
.g-white .station.is-active .session { color: var(--navy); }
.g-white .timed::before { box-shadow: none; }

/* swipe cue */
.swipe { display: inline-flex; align-items: center; gap: 48px; color: var(--white); }
/* the cover's bottom block: service line, headline, swipe cue, marks - left-aligned, as on the reference */
.cover-stack { display: flex; flex-direction: column; align-items: flex-start; }
.cover-stack .service { margin-bottom: 24px; }
.cover-stack .swipe { margin-top: 56px; }
.cover-stack .marks { margin-top: 72px; }
.swipe svg { display: block; }
"""

# ----------------------------------------------------------------------------
# Flags — the one network call. Rectangular, never circular (square system).
# ----------------------------------------------------------------------------


def flag_uri(iso2: str) -> str:
    """Country flag PNG (1200x800) from msikma/country-flags as a data URI. 'gb' maps to 'uk'."""
    code = iso2.strip().lower()
    code = "uk" if code == "gb" else code
    url = f"https://raw.githubusercontent.com/msikma/country-flags/master/flags/png/{code}.png"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        raise MissingAsset(f"flag '{code}' returned HTTP {e.code}; show the country name without a flag.") from e
    except OSError as e:
        raise MissingAsset(f"flag '{code}' needs network access ({e}); show the name without a flag.") from e
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"


# ----------------------------------------------------------------------------
# Self-check
# ----------------------------------------------------------------------------

def selfcheck() -> None:
    for name in ("LOGO_GCS_WHITE", "LOGO_GCS_WORDMARK_WHITE", "LOGO_GCS_SYMBOL_WHITE", "LOGO_GCS_BLUE"):
        uri = globals()[name]
        raw = base64.b64decode(uri.partition(",")[2], validate=True)
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(f"{name}: not a valid PNG")
        print(f"  ok  {name:<26} {len(uri) // 1024:>4} KB")
    for fam, w, style, ttf in _FACES:
        raw = (ASSETS / "fonts" / ttf).read_bytes()
        if raw[:4] not in (b"\x00\x01\x00\x00", b"true", b"OTTO"):
            raise ValueError(f"{ttf}: not a TrueType font")
        print(f"  ok  {fam} {w:<4} {ttf}")
    missing = [k for k, v in ASSET_LIBRARY.items() if not (ASSETS / v).is_file()]
    if missing:
        raise MissingAsset("ASSET_LIBRARY entries missing on disk: " + ", ".join(missing))
    listed = {ASSETS / v for v in ASSET_LIBRARY.values()}
    known_dirs = ("fonts", "speakers")
    extra = sorted(str(f.relative_to(ASSETS)) for f in ASSETS.rglob("*")
                   if f.is_file() and f not in listed and f.suffix.lower() in _MIME
                   and not any(d in f.parts for d in known_dirs))
    print(f"  ok  ASSET_LIBRARY {len(ASSET_LIBRARY)} assets, "
          f"{len(list((ASSETS / 'img' / 'speakers').glob('*.webp')))} headshots")
    if extra:
        print("  --  on disk but not in ASSET_LIBRARY (add to the library or archive them):")
        for e in extra:
            print("      " + e)
    print("\nPalette read from references/DESIGN.md:")
    for k, v in PALETTE.items():
        print(f"  {k:<12} {v}")
    try:
        from qa import check_palette  # same folder
        print("\nContrast (text on ground):")
        check_palette(verbose=True)
    except ImportError:
        print("\n(qa.py not found next to this file — contrast check skipped)")
    print(f"\nFONTS_CSS {len(FONTS_CSS) // 1024} KB · TOKENS_CSS {len(TOKENS_CSS)} B · BASE_CSS {len(BASE_CSS)} B")
    print(f"SKILL_DIR = {SKILL_DIR}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    selfcheck()
