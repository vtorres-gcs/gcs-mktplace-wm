#!/usr/bin/env python3
"""Wealth & Migration Summit web banners: spec JSON -> editable HTML -> PNG or animated GIF.

    python3 banner.py presets
    python3 banner.py build  spec.json [--out DIR]
    python3 banner.py check  banner.html [--on YYYY-MM-DD]
    python3 banner.py render banner.html --type png [--scale 2] [--max-kb N]
    python3 banner.py render banner.html --type gif --max-kb 150 [--plays 3] [--fps 20]
    python3 banner.py sheet  banner.gif [--frames 12]        # contact sheet, to look at an animation

The navy ground, the type, the logos and the palette all come from this folder. Needs
Python 3, `playwright` (with Chromium) and `pillow`. HTML is always written from Python,
never a shell heredoc, which corrupts base64 through $ and backtick interpolation.

Every banner carries the Global Citizen Solutions and CNN Portugal marks (the pair the site's
hero shows beside the title) plus the Summit lockup. There is no switch to turn them off.

Spec (JSON). Only width, height and a headline are required:

    {
      "name": "plan-b",                      # slug, used in file names
      "width": 728, "height": 90,
      "scenes": [                            # 1-3 messages; or give headline/subline at top level
        {"headline": "Your residency, your citizenship, your Plan B.",
         "subline": "5–6 November 2026 · Lisbon"}
      ],
      "cta": "Secure your place",            # null / "" for no button
      "logo": "auto",                        # Summit lockup: auto | horizontal | vertical | default | symbol
      "border": true,                        # 1px hairline at the edge
      "url_confirmed": false,                # only if the user asked for / confirmed a URL on the graphic
      "scene_seconds": 3.0, "final_hold": 3.0
      # per scene: "plain": true sets the sub line in lowercase (automatic when it holds a URL)
    }
"""

from datetime import date
from io import BytesIO
from pathlib import Path
from string import Template
import argparse
import base64
import html
import json
import re
import sys

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
DATA = SKILL_DIR / "references" / "data"

# Palette — pinned by the site's DESIGN.md. Navy is the ground; gold is the one lit thing (the button) and a rule.
NAVY, GOLD, MIST, WHITE = "#121B31", "#C2A358", "#C8CCD7", "#FFFFFF"
RULE_LINE = "rgba(200,204,215,.16)"  # --rule: hairlines on navy
SERVICE_LINE = "5–6 November 2026 · Lisbon"
DEFAULT_CTA = "Secure your place"
MIN_PX = 12  # the site's closed type ramp: nothing below 12px

LOGOS = {  # Summit lockups for a navy ground: key -> (file, intrinsic w, intrinsic h)
    "horizontal": ("w&m-horizontal White.svg", 1124, 85),
    "vertical": ("w&m-vertical white.svg", 1006, 390),
    "default": ("w&m-default white.svg", 523, 397),
    "symbol": ("w&m-symbol.svg", 600, 252),
}
GCS_SYMBOL = ("hero-gcs-symbol.svg", 62, 64)       # the site hero's pair: symbol + wordmark, side by side
GCS_TEXT = ("hero-gcs-text.svg", 105.186, 46.2476)
CNN = ("cnn-portugal-white.png", 905, 625)          # CNN Portugal, white, as the hero shows it (92x64 there)
GCS_GAP, PARTNER_GAP = 0.12, 0.6                    # in units of the partner height

PRESETS = [  # (w, h, note)
    (300, 250, "medium rectangle"), (336, 280, "large rectangle"), (250, 250, "square"), (200, 200, "small square"),
    (728, 90, "leaderboard"), (970, 90, "large leaderboard"), (900, 200, "wide banner"), (970, 250, "billboard"),
    (468, 60, "banner"), (300, 600, "half page"), (160, 600, "wide skyscraper"), (120, 600, "skyscraper"),
    (320, 50, "mobile leaderboard"), (320, 100, "large mobile banner"),
    (1200, 627, "LinkedIn / link-preview landscape"), (1080, 1080, "square social"),
]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def layout_for(w, h):
    ar = w / h
    return "row" if ar >= 2.6 else ("box" if ar >= 0.75 else "tall")


# ---------------------------------------------------------------------------------------------
# Facts the copy lint needs (rates, programme times) — read from references/data, never typed
# ---------------------------------------------------------------------------------------------

def _data(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def rate_on(on):
    for t in _data("rates.json")["tiers"]:
        if date.fromisoformat(t["start"]) <= on <= date.fromisoformat(t["end"]):
            return t
    return None


def known_times():
    return {r["time"] for d in _data("programme.json")["days"] for k in ("main", "workshops") for r in d[k]}


# ---------------------------------------------------------------------------------------------
# Copy lint — the words on the banner
# ---------------------------------------------------------------------------------------------

URGENCY = re.compile(r"last chance|book now|hurry|don[’']?t miss|act now|limited time|only \d+ (?:seats?|places?|tickets?|spots?)"
                     r"|running out|selling fast|sold out|final call|ends soon|now or never", re.I)
GCS_TERMS = re.compile(r"relocation firm|passport shop|passport scheme|passport programme|borderless living|dream lifestyle|fallback option", re.I)
STALE = [
    (r"golden visa pathway", "retired Day One theme (now 'The New Geography of Wealth & Mobility')"),
    (r"structuring, context", "retired Day Two theme (now 'Global Wealth & the International Family')"),
    (r"\bdinner\b", "there is no networking dinner on the programme"),
    (r"\b150\b", "the cap is 200 attendees, not 150"),
    (r"register (?:your )?interest", "the CTA is 'Secure your place'"),
]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
URL = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(?:com|pt|org|net|io|co)\b|@[a-z0-9-]+\.", re.I)
PRICE = re.compile(r"(?:€|EUR\s?)\s?(\d[\d,.]*)|(\d[\d,.]*)\s?(?:€|EUR\b)", re.I)
TIME = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")


def lint_copy(spec, on):
    """Return (errors, warnings) for the words on the banner."""
    errs, warns = [], []
    texts = [s["headline"] for s in spec["scenes"]] + [s.get("subline") or "" for s in spec["scenes"]] + [spec.get("cta") or ""]
    blob = "\n".join(texts)
    if "!" in blob:
        errs.append("exclamation mark — the voice is restrained, factual, institutional")
    if EMOJI.search(blob):
        errs.append("emoji — none, anywhere")
    if URGENCY.search(blob):
        errs.append(f"urgency mechanic ({URGENCY.search(blob).group(0)!r}) — scarcity is factual (\"Limited to 200 attendees\"), a deadline is a date")
    if GCS_TERMS.search(blob):
        errs.append(f"term GCS never uses ({GCS_TERMS.search(blob).group(0)!r})")
    for pat, why in STALE:
        if re.search(pat, blob, re.I):
            errs.append(f"stale or retired fact: {why}")
    if re.search(r"\bturkey\b", blob, re.I):
        warns.append("'Turkey' is in the site's intro sentence but not in the timed workshop list — confirm with the user")
    if URL.search(blob) and not spec.get("url_confirmed"):
        errs.append("a URL / address is printed on the graphic but the user has not confirmed it (the site may still sit behind its staging gate) — put it in the click-through, not the artwork")
    tiers = {t["eur"]: t for t in _data("rates.json")["tiers"]}
    for m in PRICE.finditer(blob):
        raw = (m.group(1) or m.group(2)).replace(",", "")
        try:
            amt = int(float(raw))
        except ValueError:
            continue
        if amt not in tiers:
            errs.append(f"price {m.group(0).strip()} is not one of the three published tiers (€399 / €499 / €599)")
            continue
        now = rate_on(on)
        if now is None:
            errs.append(f"price on the banner but no tier is published for {on} — say nothing about price")
        elif now["eur"] != amt:
            errs.append(f"{tiers[amt]['name']} (€{amt}) is not the tier in force on {on} — that is the {now['name']} (€{now['eur']})")
    times = known_times()
    for m in TIME.finditer(blob):
        hhmm = f"{int(m.group(1)):02d}:{m.group(2)}"
        if hhmm not in times:
            errs.append(f"time {hhmm} is not on the site's published programme")
    for s in spec["scenes"]:
        n = len(s["headline"].split())
        if n > 12:
            warns.append(f"headline is {n} words (bar: 12 or fewer): {s['headline'][:48]}…")
    return errs, warns


# ---------------------------------------------------------------------------------------------
# Spec -> HTML
# ---------------------------------------------------------------------------------------------

def normalise(spec):
    s = dict(spec)
    for k in ("width", "height"):
        if not isinstance(s.get(k), int) or not (30 <= s[k] <= 4000):
            raise SystemExit(f"spec: '{k}' must be an integer number of pixels (30–4000)")
    if "scenes" not in s:
        if not s.get("headline"):
            raise SystemExit("spec: give 'scenes' or a 'headline'")
        s["scenes"] = [{"headline": s["headline"], **({"subline": s["subline"]} if "subline" in s else {})}]
    if not 1 <= len(s["scenes"]) <= 3:
        raise SystemExit("spec: 1–3 scenes (a banner is read in seconds)")
    s["scenes"] = [dict(x) for x in s["scenes"]]
    for sc in s["scenes"]:
        if not sc.get("headline"):
            raise SystemExit("spec: every scene needs a headline")
        sc.setdefault("subline", SERVICE_LINE)
    s.setdefault("cta", DEFAULT_CTA)
    s.setdefault("logo", "auto")
    s.setdefault("border", True)
    s.setdefault("scene_seconds", 3.0)
    s.setdefault("final_hold", 3.0)
    s.setdefault("name", "wms-banner")
    s["name"] = re.sub(r"[^a-z0-9_-]+", "-", s["name"].lower()).strip("-") or "wms-banner"
    return s


def esc(text):
    """Escape, and keep a hyphenated word ("Twenty-six") from breaking across lines."""
    return re.sub(r"\b\w+(?:-\w+)+\b", lambda m: f'<span class="nb">{m.group(0)}</span>', html.escape(text))


def b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


def svg_uri(path):
    return "data:image/svg+xml;base64," + b64(path)


def png_uri(path):
    return "data:image/png;base64," + b64(path)


def font_css():
    faces = [("Caladea", 400, "Caladea-Regular.ttf"), ("Archivo", 400, "Archivo-400.ttf"),
             ("Archivo", 500, "Archivo-500.ttf"), ("Archivo", 600, "Archivo-600.ttf")]
    return "\n".join(
        f'@font-face{{font-family:"{fam}";font-weight:{wt};font-display:block;'
        f'src:url(data:font/ttf;base64,{b64(ASSETS / "fonts" / f)}) format("truetype")}}' for fam, wt, f in faces)


def partners(ph, stack=False, symbol_only=False):
    """The GCS mark and CNN Portugal, both `ph` px high — the pair the site's hero shows next to the title.
    Returns (html, width, height)."""
    k = ph / 64
    sw, tw, th = GCS_SYMBOL[1] * k, GCS_TEXT[1] * k, GCS_TEXT[2] * k
    gap = ph * GCS_GAP
    gcs_w = sw if symbol_only else sw + gap + tw
    cnn_w = ph * CNN[1] / CNN[2]
    gcs = (f'<span class="gcs"><img alt="Global Citizen Solutions" src="{svg_uri(ASSETS / "logos" / GCS_SYMBOL[0])}" width="{sw:.1f}" height="{ph:.1f}">'
           + ("" if symbol_only else f'<img alt="" src="{svg_uri(ASSETS / "logos" / GCS_TEXT[0])}" width="{tw:.1f}" height="{th:.1f}">')
           + "</span>")
    cnn = f'<img class="cnn" alt="CNN Portugal" src="{png_uri(ASSETS / "logos" / CNN[0])}" width="{cnn_w:.1f}" height="{ph:.1f}">'
    g = ph * PARTNER_GAP
    if stack:
        return f'<div class="partners stack" style="gap:{g:.1f}px">{gcs}{cnn}</div>', max(gcs_w, cnn_w), 2 * ph + g
    return f'<div class="partners" style="gap:{g:.1f}px">{gcs}{cnn}</div>', gcs_w + g + cnn_w, ph


def lockup(key, w=None, h=None):
    f, iw, ih = LOGOS[key]
    if h is not None:
        w = h * iw / ih
    else:
        h = w * ih / iw
    return (f'<div class="logo"><img alt="Wealth &amp; Migration Summit" src="{svg_uri(ASSETS / "logos" / f)}" '
            f'width="{w:.1f}" height="{h:.1f}"></div>'), w, h


def timeline(n, scene_s):
    """Start times and the total animation length T (end of the last move). Seconds."""
    t0 = 0.25
    starts = [t0 + i * scene_s for i in range(n)]
    cta_at = starts[-1] + 0.95
    return {"starts": starts, "cta": cta_at, "T": round(cta_at + 0.5, 3), "scene_s": scene_s}


def keyframes(T, name, t0, dur, frm, to):
    p0, p1 = t0 / T * 100, min(100, (t0 + dur) / T * 100)
    return f"@keyframes {name}{{0%,{p0:.3f}%{{{frm}}}{p1:.3f}%,100%{{{to}}}}}"


def build_html(spec):
    """Returns (html, layout, notes). Order of the marks: row = lockup | copy | partners | button;
    box = [lockup … partners] header, copy, button; tall = lockup, copy, button, partners."""
    w, h = spec["width"], spec["height"]
    layout = layout_for(w, h)
    n = len(spec["scenes"])
    tl = timeline(n, spec["scene_seconds"])
    T = tl["T"]
    has_cta = bool(spec["cta"])
    notes = []
    key = spec["logo"]

    # --- geometry, marks ---------------------------------------------------------------------
    if layout == "row":
        pad_x = clamp(h * 0.2, 10, 36)
        pad_y = clamp(h * 0.1, 5, 24)
        gap = pad_x * 0.9
        tiny = h < 60
        mini = tiny and w < 400
        if key == "auto":
            key = "symbol" if tiny else "default"
        if mini:
            logo_html = ""
            notes.append("Summit lockup left off — a banner this small carries the GCS and CNN marks first; name the Summit in the headline")
        else:
            logo_html, lw, lh = lockup(key, h=h * (0.4 if key == "symbol" else 0.62 if h < 120 else 0.36))
        if tiny:
            part_html, pw, ph_ = partners(clamp(h * 0.42, 18, 40), symbol_only=True)
        elif h < 80:
            part_html, pw, ph_ = partners(h * 0.3)
        else:
            part_html, pw, ph_ = partners(clamp(h * 0.3, 20, 56) if h < 120 else clamp(h * 0.2, 28, 52), stack=True)
        hmax = clamp(h * 0.3, 15, 64)
        s_px = clamp(h * 0.06, MIN_PX, 20)
        cta_px = 12 if h < 120 else clamp(h * 0.1, MIN_PX, 18)
        show_sub, show_rule = h >= 80, h >= 110
        body_order = ["logo", "copy", "partners", "cta"]
        copy_w = 1.0
    elif layout == "box":
        p = clamp(min(w, h) * 0.07, 14, 48)
        pad_x = pad_y = p
        gap = p * 0.7
        part_html, pw, ph_ = partners(clamp(min(w, h) * 0.1, 18, 60))
        if key == "auto":
            key = "vertical"
        avail = w - 2 * p - pw - gap
        lw = clamp(min(min(w, h) * 0.5, avail), 56, 320)
        logo_html, lw, lh = lockup(key, w=lw)
        if lw > avail + 0.5:
            notes.append("the Summit lockup and the partner marks barely fit side by side — widen the banner or use logo:'symbol'")
        hmax = clamp(min(w, h) * 0.1, 18, 88)
        s_px = clamp(min(w, h) * 0.045, MIN_PX, 22)
        cta_px = clamp(min(w, h) * 0.05, MIN_PX, 22)
        show_sub = show_rule = True
        body_order = ["top", "copy", "cta"]
        copy_w = 0.72 if w / h > 1.5 else 1.0
    else:  # tall
        p = clamp(w * 0.075, 10, 40)
        pad_x = pad_y = p
        gap = p * 0.8
        avail = w - 2 * p
        if key == "auto":
            key = "vertical"
        logo_html, lw, lh = lockup(key, w=avail)
        ph = clamp(avail / (2.61 + 1.448 + PARTNER_GAP + GCS_GAP) * 0.95, 14, 60)
        part_html, pw, ph_ = partners(ph)
        hmax = clamp(w * 0.17, 16, 64)
        s_px = clamp(w * 0.055, MIN_PX, 18)
        cta_px = clamp(w * 0.06, MIN_PX, 16)
        show_sub = show_rule = True
        body_order = ["logo", "copy", "cta", "partners"]
        copy_w = 1.0
    if ph_ < 18:
        notes.append(f"partner marks are only {ph_:.0f}px high — legible as marks, not as words; a bigger banner shows them better")

    # --- scenes + animation ------------------------------------------------------------------
    kfs, scenes_html, anim_rules = [], [], []
    ease = "cubic-bezier(.2,.7,.2,1)"
    for i, sc in enumerate(spec["scenes"]):
        s0 = tl["starts"][i]
        last = i == n - 1
        parts = [f'<p class="h" id="h{i}">{esc(sc["headline"])}</p>']
        kfs.append(keyframes(T, f"h{i}", s0, 0.55, "opacity:0;transform:translateY(8px)", "opacity:1;transform:none"))
        anim_rules.append(f".play #h{i}{{animation:h{i} {T}s {ease} both}}")
        if show_rule and sc.get("subline"):
            parts.append(f'<i class="rule" id="r{i}"></i>')
            kfs.append(keyframes(T, f"r{i}", s0 + 0.45, 0.5, "transform:scaleX(0)", "transform:scaleX(1)"))
            anim_rules.append(f".play #r{i}{{animation:r{i} {T}s {ease} both}}")
        if sc.get("subline"):
            if show_sub:
                plain = " plain" if sc.get("plain") or URL.search(sc["subline"]) else ""  # a URL stays lowercase
                parts.append(f'<p class="s{plain}" id="s{i}">{html.escape(sc["subline"])}</p>')
                kfs.append(keyframes(T, f"s{i}", s0 + 0.65, 0.5, "opacity:0;transform:translateY(6px)", "opacity:1;transform:none"))
                anim_rules.append(f".play #s{i}{{animation:s{i} {T}s {ease} both}}")
            elif i == 0:
                notes.append("sub line hidden — the banner is too short for a second line of text at 12px or more")
        if not last:
            e0 = s0 + tl["scene_s"] - 0.45
            kfs.append(keyframes(T, f"x{i}", e0, 0.4, "opacity:1", "opacity:0"))
            anim_rules.append(f".play #sc{i}{{animation:x{i} {T}s linear both}}")
        scenes_html.append(f'<div class="sc" id="sc{i}" data-i="{i}">{"".join(parts)}</div>')

    cta_html = ""
    cta_h = 0
    if has_cta:
        cta_html = f'<div class="cta" id="cta">{html.escape(spec["cta"])}</div>'
        cta_h = clamp(cta_px * 2.7, 30, 56)
        kfs.append(keyframes(T, "cta", tl["cta"], 0.5, "opacity:0;transform:translateY(6px)", "opacity:1;transform:none"))
        anim_rules.append(f".play #cta{{animation:cta {T}s {ease} both}}")
    cta_full = layout == "tall" or (layout == "box" and w <= 420)
    cta_padx = cta_px * (0.9 if h < 60 else 1.1 if layout == "row" and h < 120 else 1.3 if layout == "row" else 1.5)

    copy = f'<div class="copy">{"".join(scenes_html)}</div>'
    pieces = {"logo": logo_html, "copy": copy, "partners": part_html, "cta": cta_html,
              "top": f'<div class="top">{logo_html}{part_html}</div>'}
    body = "".join(pieces[k] for k in body_order)

    # --- css ---------------------------------------------------------------------------------
    css = CSS_BASE.substitute(
        FONTS=font_css(), W=w, H=h, NAVY=NAVY, GOLD=GOLD, WHITE=WHITE, MIST=MIST, RULE_LINE=RULE_LINE,
        PADX=f"{pad_x:.1f}", PADY=f"{pad_y:.1f}", GAP=f"{gap:.1f}", HMAX=f"{hmax:.1f}", S=f"{s_px:.1f}",
        CTA_PX=f"{cta_px:.1f}", CTA_H=f"{cta_h:.1f}", CTA_PADX=f"{cta_padx:.1f}",
        BORDER="" if spec["border"] else ".banner::after{display:none}")
    css += LAYOUT_CSS[layout]
    if layout == "box" and copy_w < 1.0:
        css += f".copy{{max-width:{copy_w * 100:.0f}%}}"
    if cta_full:
        css += ".banner .cta{align-self:stretch;white-space:normal;padding-left:.8em;padding-right:.8em}"
    css += "\n" + "\n".join(kfs) + "\n" + "\n".join(anim_rules)

    banner = (f'<div class="banner L-{layout}" data-w="{w}" data-h="{h}" data-total="{T}" data-hold="{spec["final_hold"]}" '
              f'data-hmax="{hmax:.1f}" data-hmin="{MIN_PX}">{body}</div>')
    doc = (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(spec["name"])} — {w}×{h}</title>'
           f'<style>\n{css}\n</style></head><body>{banner}\n'
           f'<script type="application/json" id="spec">{json.dumps(spec, ensure_ascii=False)}</script>\n'
           f'<script>{FIT_JS}</script></body></html>')
    return doc, layout, notes


CSS_BASE = Template("""
$FONTS
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#E9EBF0}
.banner{position:relative;width:${W}px;height:${H}px;background:$NAVY;color:$WHITE;overflow:hidden;
  font-family:Archivo,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;
  padding:${PADY}px ${PADX}px;display:flex;--gap:${GAP}px}
.banner::after{content:"";position:absolute;inset:0;border:1px solid $RULE_LINE;pointer-events:none}
$BORDER
.logo{flex:none;display:flex;align-items:center}
.logo img,.partners img,.gcs img{display:block}
.partners{flex:none;display:flex;align-items:center}.partners.stack{flex-direction:column;align-items:flex-start}
.gcs{display:flex;align-items:center;gap:12%}
.top{flex:none;display:flex;align-items:center;justify-content:space-between;gap:var(--gap)}
.copy{position:relative;flex:1 1 0;min-width:0;min-height:0}
.sc{position:absolute;inset:0;display:none;flex-direction:column}
.sc:last-child{display:flex}
.play0 .sc,.play .sc{display:flex}
.h{margin-top:auto;font-family:Caladea,Georgia,"Times New Roman",serif;font-weight:400;font-size:${HMAX}px;
  line-height:1.06;letter-spacing:-.01em;text-wrap:balance;color:$WHITE}
.nb{white-space:nowrap}
.rule{display:block;width:32px;height:2px;margin:.9em 0 .8em;background:$GOLD;transform-origin:left}
.s{margin-bottom:auto;font-weight:500;font-size:${S}px;line-height:1.3;letter-spacing:.16em;text-transform:uppercase;color:$MIST;margin-top:.5em}
.rule+.s{margin-top:0}
.s.plain{text-transform:none;letter-spacing:.02em;font-size:calc(${S}px + 1px)}
.sc>.h:last-child{margin-bottom:auto}
.cta{flex:none;display:flex;align-items:center;justify-content:center;text-align:center;line-height:1.2;min-height:${CTA_H}px;padding:.6em ${CTA_PADX}px;
  background:$GOLD;color:$NAVY;font-weight:500;font-size:${CTA_PX}px;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap}
.play .h,.play .s,.play .cta,.play .rule{will-change:opacity,transform}
@media (prefers-reduced-motion:reduce){.play .sc{display:none}.play .sc:last-child{display:flex}.banner *{animation:none!important}}
""")

LAYOUT_CSS = {
    "row": ".L-row{flex-direction:row;align-items:center;gap:var(--gap)}.L-row .copy{align-self:stretch}",
    "box": ".L-box{flex-direction:column;gap:var(--gap)}.L-box .copy{flex:1 1 0}.L-box .cta{align-self:flex-start}",
    "tall": ".L-tall{flex-direction:column;gap:var(--gap)}.L-tall .copy{flex:1 1 0}.L-tall .partners{align-self:flex-start}",
}

FIT_JS = r"""
(async () => {
  await document.fonts.ready;
  const b = document.querySelector('.banner');
  b.classList.add('play0');
  const hmax = +b.dataset.hmax, hmin = +b.dataset.hmin;
  const over = sc => {
    const h = sc.querySelector('.h');
    return sc.scrollHeight > sc.clientHeight + 1 || sc.scrollWidth > sc.clientWidth + 1 || h.scrollWidth > h.clientWidth + 1;
  };
  const hs = [...document.querySelectorAll('.h')];
  let best = hmax;
  for (const h of hs) {
    let fs = hmax; h.style.fontSize = fs + 'px';
    while (fs > hmin && over(h.closest('.sc'))) { fs -= 0.5; h.style.fontSize = fs + 'px'; }
    best = Math.min(best, fs);
  }
  hs.forEach(h => h.style.fontSize = best + 'px');
  const bg = { h: [18,27,49,1], s: [18,27,49,1], cta: [194,163,88,1] };
  const texts = [...document.querySelectorAll('.h,.s,.cta')].map(el => {
    const cs = getComputedStyle(el);
    const cls = el.classList.contains('h') ? 'h' : el.classList.contains('s') ? 's' : 'cta';
    return { id: el.id, cls, fs: parseFloat(cs.fontSize), color: cs.color, bg: bg[cls],
             clipped: el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1 };
  });
  const sceneOver = [...document.querySelectorAll('.sc')].map(sc => ({ id: sc.id, over: over(sc) }));
  const bb = b.getBoundingClientRect();
  const outside = [...b.querySelectorAll('.logo,.cta,.partners,.top,.copy')].filter(el => {
    const r = el.getBoundingClientRect();
    return r.left < bb.left - 0.5 || r.top < bb.top - 0.5 || r.right > bb.right + 0.5 || r.bottom > bb.bottom + 0.5;
  }).map(el => el.className);
  // marks must not overlap each other or the copy
  const boxes = [...b.querySelectorAll('.logo,.partners,.cta,.copy')].map(el => [el.className, el.getBoundingClientRect()]);
  const overlaps = [];
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i][1], c = boxes[j][1];
    if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) overlaps.push(boxes[i][0] + ' / ' + boxes[j][0]);
  }
  const marks = { gcs: !!b.querySelector('.gcs'), cnn: !!b.querySelector('.cnn') };
  b.classList.add('play');  // after measuring: the entrance transforms would count as overflow
  b.addEventListener('click', () => document.getAnimations().forEach(a => { a.cancel(); a.play(); }));
  window.__fit = { headline_px: best, texts, sceneOver, outside, overlaps, marks };
  document.documentElement.dataset.ready = '1';
})();
"""


# ---------------------------------------------------------------------------------------------
# Browser pass: fit, contrast, overflow
# ---------------------------------------------------------------------------------------------

def _launch():
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    # --no-sandbox is required in this execution environment; never omit it.
    browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
    return p, browser


def _open(browser, html_path, w, h, scale=1):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=scale)
    page = ctx.new_page()
    page.goto(Path(html_path).resolve().as_uri(), wait_until="load")
    page.wait_for_function("document.documentElement.dataset.ready === '1'", timeout=20000)
    return ctx, page


def _spec_of(html_path):
    m = re.search(r'<script type="application/json" id="spec">(.*?)</script>', Path(html_path).read_text(encoding="utf-8"), re.S)
    if not m:
        raise SystemExit(f"{html_path}: no embedded spec — build it with `banner.py build`")
    return json.loads(m.group(1))


def _lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def _parse_rgba(css):
    nums = [float(x) for x in re.findall(r"[\d.]+", css)]
    return (nums + [1.0])[:4] if len(nums) >= 3 else [0, 0, 0, 1.0]


def contrast(fg_css, bg):
    fg = _parse_rgba(fg_css)
    a = fg[3]
    blended = [fg[i] * a + bg[i] * (1 - a) for i in range(3)]
    l1, l2 = _lum(blended), _lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def run_check(html_path, on):
    spec = _spec_of(html_path)
    w, h = spec["width"], spec["height"]
    errs, warns = lint_copy(spec, on)
    p, browser = _launch()
    try:
        ctx, page = _open(browser, html_path, w, h)
        fit = page.evaluate("window.__fit")
        ctx.close()
    finally:
        browser.close(); p.stop()
    for sc in fit["sceneOver"]:
        if sc["over"]:
            errs.append(f"{sc['id']}: copy does not fit at {MIN_PX}px or larger — shorten the headline or use a taller banner")
    for t in fit["texts"]:
        if t["fs"] < MIN_PX - 0.01:
            errs.append(f"{t['id']}: {t['fs']:.1f}px is below the 12px floor")
        if t["clipped"] and t["cls"] != "h":
            errs.append(f"{t['id']}: text is clipped ({t['cls']})")
        c = contrast(t["color"], t["bg"])
        need = 3.0 if t["fs"] >= 24 else 4.5
        if c < need:
            errs.append(f"{t['id']}: contrast {c:.1f}:1 is under {need}:1 (gold is never text on white)")
    if not (fit["marks"]["gcs"] and fit["marks"]["cnn"]):
        errs.append("the GCS and CNN Portugal marks are missing — every banner carries both")
    if fit["overlaps"]:
        errs.append(f"elements overlap: {', '.join(fit['overlaps'])} — shorten the copy, drop the button or use a bigger banner")
    if fit["outside"]:
        errs.append(f"layout spills outside the canvas: {', '.join(fit['outside'])} — a layout this tight needs shorter copy or no CTA/logo")
    if fit["headline_px"] < 16:
        warns.append(f"headline settled at {fit['headline_px']:.1f}px — very small; consider fewer words")
    return spec, fit, errs, warns


# ---------------------------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------------------------

BRAND_EXACT = [(18, 27, 49), (255, 255, 255), (194, 163, 88)]  # ground, type, the lit button: these must survive quantising exactly


def lock_palette(q):
    """Set the palette entries nearest to navy, white and gold to exactly those colours, return their indices.
    Median cut lands on (16,24,45) and (252,252,252); on a brand banner the ground is a visible wrong when it drifts."""
    pal = q.getpalette()[:768]
    n = len(pal) // 3
    taken, idx = set(), []
    for rgb in BRAND_EXACT:
        best = min((i for i in range(n) if i not in taken), key=lambda i: sum((rgb[k] - pal[3 * i + k]) ** 2 for k in range(3)))
        taken.add(best); idx.append(best)
        pal[3 * best:3 * best + 3] = list(rgb)
    q.putpalette(pal)
    return idx


def quantize_exact(im, pal, idx):
    """Quantise to the shared palette, then pin pixels that are exactly navy / white / gold to their locked entries.
    Pillow's palette lookup uses a coarse colour cube and would otherwise send the exact brand colours to near ones."""
    from PIL import Image, ImageChops
    q = im.quantize(palette=pal, dither=Image.Dither.NONE)
    for rgb, i in zip(BRAND_EXACT, idx):
        diff = ImageChops.difference(im, Image.new("RGB", im.size, rgb))
        r, g, b = diff.split()
        same = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v == 0 else 0)
        q.paste(i, mask=same)
    return q


def _png_bytes(im, colors=None):
    buf = BytesIO()
    if colors:
        pal = im.quantize(colors, method=2, dither=0)  # 2 = FASTOCTREE; flat colour art survives it
        im = quantize_exact(im, pal, lock_palette(pal))
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def render_png(html_path, spec, out_dir, scale, max_kb):
    from PIL import Image
    w, h = spec["width"], spec["height"]
    p, browser = _launch()
    outs = []
    try:
        for sc in sorted({1, scale}):
            ctx, page = _open(browser, html_path, w, h, scale=sc)
            page.evaluate("T => document.getAnimations().forEach(a => { a.pause(); a.currentTime = T * 1000 })", float(page.evaluate("+document.querySelector('.banner').dataset.total")))
            raw = page.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h})
            ctx.close()
            im = Image.open(BytesIO(raw)).convert("RGB")
            data = _png_bytes(im)
            note = ""
            if max_kb and len(data) > max_kb * 1024:
                for colors in (256, 128, 64, 32):
                    data = _png_bytes(im, colors)
                    if len(data) <= max_kb * 1024:
                        note = f" (PNG-8, {colors} colours)"
                        break
            name = f"{spec['name']}_{w}x{h}" + ("" if sc == 1 else f"@{sc}x") + ".png"
            path = Path(out_dir) / name
            path.write_bytes(data)
            outs.append((path, len(data), note, im.size))
    finally:
        browser.close(); p.stop()
    return outs


def capture_frames(html_path, spec, fps):
    """Seek the page's animations to each instant and screenshot. Returns ([(t, PIL RGB)], T)."""
    from PIL import Image
    w, h = spec["width"], spec["height"]
    p, browser = _launch()
    frames = []
    try:
        ctx, page = _open(browser, html_path, w, h)
        T = float(page.evaluate("+document.querySelector('.banner').dataset.total"))
        n = int(T * fps)
        times = [i / fps for i in range(n + 1)]
        if T - times[-1] > 1e-6:
            times.append(T)
        for t in times:
            page.evaluate("t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t * 1000 })", t)
            frames.append((t, Image.open(BytesIO(page.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h}))).convert("RGB")))
        ctx.close()
    finally:
        browser.close(); p.stop()
    return frames, T


def _gif_candidates(fps):
    """Quality ladder: keep the frame rate first, then colours, then thin the frames. Never the dimensions."""
    steps = [(256, 1), (128, 1), (64, 1), (32, 1), (64, 2), (32, 2), (16, 2), (32, 3), (16, 3), (16, 4), (8, 4)]
    return [(c, k) for c, k in steps]


def encode_gif(frames, hold, colors, thin, plays):
    """frames: [(t, RGB image)]. Thin by `thin`, merge identical neighbours, quantise to one shared palette."""
    from PIL import Image
    kept = [frames[i] for i in range(0, len(frames), thin)]
    if kept[-1][0] != frames[-1][0]:
        kept.append(frames[-1])
    durs = [kept[i + 1][0] - kept[i][0] for i in range(len(kept) - 1)] + [hold]
    merged = []  # [image, seconds]
    for (t, im), d in zip(kept, durs):
        if merged and merged[-1][0].tobytes() == im.tobytes():
            merged[-1][1] += d
        else:
            merged.append([im, d])
    pick = [m[0] for m in merged]
    step = max(1, len(pick) // 12)
    sample = pick[::step][:12]
    w, h = sample[0].size
    mont = Image.new("RGB", (w, h * len(sample)))
    for i, im in enumerate(sample):
        mont.paste(im, (0, i * h))
    pal = mont.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    idx = lock_palette(pal)
    q = [quantize_exact(im, pal, idx) for im in pick]
    ms = [max(20, int(round(m[1] * 100)) * 10) for m in merged]
    kw = {}
    if plays == 0:
        kw["loop"] = 0
    elif plays > 1:
        kw["loop"] = plays - 1  # the loop field counts repeats after the first play
    buf = BytesIO()
    q[0].save(buf, "GIF", save_all=True, append_images=q[1:], duration=ms, optimize=True, disposal=1, **kw)
    return buf.getvalue(), len(q), sum(ms) / 1000


def render_gif(html_path, spec, out_dir, max_kb, plays, fps):
    frames, T = capture_frames(html_path, spec, fps)
    hold = float(spec["final_hold"])
    w, h = spec["width"], spec["height"]
    limit = max_kb * 1024 if max_kb else None
    best = None
    tried = []
    for colors, thin in _gif_candidates(fps):
        data, nf, total = encode_gif(frames, hold, colors, thin, plays)
        tried.append((colors, thin, len(data)))
        if best is None or len(data) < len(best[0]):
            best = (data, colors, thin, nf, total)
        if limit is None or len(data) <= limit:
            best = (data, colors, thin, nf, total)
            break
    data, colors, thin, nf, total = best
    path = Path(out_dir) / f"{spec['name']}_{w}x{h}.gif"
    path.write_bytes(data)
    # static companion: the final state, for clients that block animation or show only the first frame
    from PIL import Image
    chk = Image.open(path).convert("RGB")
    ground_ok = chk.getpixel((w // 2, 3)) == (18, 27, 49)  # just inside the hairline, top edge
    static = Path(out_dir) / f"{spec['name']}_{w}x{h}_static.png"
    static.write_bytes(_png_bytes(frames[-1][1]))
    fits = limit is None or len(data) <= limit
    return {"path": path, "bytes": len(data), "fits": fits, "colors": colors, "fps": round(fps / thin, 1), "frames": nf,
            "seconds_one_play": round(total, 2), "ground_ok": ground_ok, "plays": plays, "static": static, "tried": tried, "limit_kb": max_kb}


# ---------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------

def cmd_presets(_):
    print(f"{'size':>10}  {'layout':<6} note")
    for w, h, note in PRESETS:
        print(f"{w}x{h:<6} {layout_for(w, h):<6} {note}")
    print("\nAny other WxH works. row = logo | copy | button; box = stacked; tall = stacked and narrow.")


def cmd_build(a):
    spec = normalise(json.loads(Path(a.spec).read_text(encoding="utf-8")))
    doc, layout, notes = build_html(spec)
    out = Path(a.out or Path(a.spec).resolve().parent)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{spec['name']}_{spec['width']}x{spec['height']}.html"
    path.write_text(doc, encoding="utf-8")
    print(f"built {path}  ({spec['width']}x{spec['height']}, layout: {layout}, {len(spec['scenes'])} scene(s))")
    for n in notes:
        print("  note:", n)


def _report(errs, warns):
    for e in errs:
        print("  ERROR:", e)
    for w in warns:
        print("  WARN: ", w)


def cmd_check(a):
    on = date.fromisoformat(a.on) if a.on else date.today()
    spec, fit, errs, warns = run_check(a.html, on)
    print(f"{spec['name']} {spec['width']}x{spec['height']} — headline settled at {fit['headline_px']:.1f}px, checked for {on}")
    _report(errs, warns)
    print("OK" if not errs else f"{len(errs)} error(s)")
    sys.exit(1 if errs else 0)


def cmd_render(a):
    on = date.fromisoformat(a.on) if a.on else date.today()
    spec, fit, errs, warns = run_check(a.html, on)
    _report(errs, warns)
    if errs and not a.force:
        print("not rendered — fix the errors (or --force to render anyway)")
        sys.exit(1)
    out = Path(a.out or Path(a.html).resolve().parent)
    out.mkdir(parents=True, exist_ok=True)
    if a.type == "png":
        for path, size, note, dims in render_png(a.html, spec, out, a.scale, a.max_kb):
            print(f"PNG  {path}  {dims[0]}x{dims[1]}  {size / 1024:.1f} KB{note}")
    else:
        r = render_gif(a.html, spec, out, a.max_kb, a.plays, a.fps)
        status = "within" if r["fits"] else "OVER"
        lim = f"{r['limit_kb']} KB" if r["limit_kb"] else "no limit set"
        print(f"GIF  {r['path']}  {spec['width']}x{spec['height']}  {r['bytes'] / 1024:.1f} KB — {status} {lim}")
        print(f"     {r['colors']} colours · {r['fps']} fps · {r['frames']} frames · {r['seconds_one_play']} s per play · "
              f"{'loops forever' if r['plays'] == 0 else str(r['plays']) + ' play(s)'}")
        if not r["ground_ok"]:
            print("     WARN: the ground did not come out exact navy (#121B31) — do not ship; report this")
        print(f"STATIC {r['static']}  (final state — for clients that block animation)")
        if not r["fits"]:
            print("     could not reach the limit without changing the dimensions; smallest attempt kept. "
                  "Shorten the copy, drop a scene or raise the limit. Tried (colours, thinning, bytes): " + str(r["tried"]))
            sys.exit(2)


def cmd_sheet(a):
    """Contact sheet of an animated GIF's distinct frames — the way to look at an animation you cannot play."""
    from PIL import Image
    im = Image.open(a.gif)
    n = im.n_frames
    idx = sorted({round(i * (n - 1) / (a.frames - 1)) for i in range(a.frames)}) if n > a.frames else list(range(n))
    w, h = im.size
    cols = min(len(idx), max(1, 1600 // (w + 8)))
    rows = -(-len(idx) // cols)
    sheet = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 8) + 8), (233, 235, 240))
    for k, i in enumerate(idx):
        im.seek(i)
        sheet.paste(im.convert("RGB"), (8 + (k % cols) * (w + 8), 8 + (k // cols) * (h + 8)))
    out = Path(a.out or Path(a.gif).with_name(Path(a.gif).stem + "_frames.png"))
    sheet.save(out)
    print(f"{out}  ({len(idx)} of {n} frames)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("presets").set_defaults(fn=cmd_presets)
    b = sub.add_parser("build"); b.add_argument("spec"); b.add_argument("--out"); b.set_defaults(fn=cmd_build)
    c = sub.add_parser("check"); c.add_argument("html"); c.add_argument("--on", help="date the banner goes live (rate tier check)"); c.set_defaults(fn=cmd_check)
    r = sub.add_parser("render"); r.add_argument("html"); r.add_argument("--type", choices=["png", "gif"], required=True)
    r.add_argument("--max-kb", type=float, help="file-size ceiling (GIF: required in practice; PNG: optional)")
    r.add_argument("--plays", type=int, default=3, help="GIF plays; 0 = loop forever (default 3, ending on the final frame)")
    r.add_argument("--fps", type=int, default=20); r.add_argument("--scale", type=int, default=1, help="PNG only: also write an @Nx file")
    r.add_argument("--on"); r.add_argument("--out"); r.add_argument("--force", action="store_true"); r.set_defaults(fn=cmd_render)
    g = sub.add_parser("sheet"); g.add_argument("gif"); g.add_argument("--frames", type=int, default=12); g.add_argument("--out"); g.set_defaults(fn=cmd_sheet)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
