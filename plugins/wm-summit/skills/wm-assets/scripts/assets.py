#!/usr/bin/env python3
"""Wealth & Migration Summit 2026 — asset library: find a file, hand it over.

    python3 assets.py list [--group G]            the catalogue, grouped (ids to pass to `get`)
    python3 assets.py find <words…>               filter by any words, PT or EN ("logo branco", "palestrante joe")
    python3 assets.py speaker <name>              the roster: name, role, portrait id
    python3 assets.py get <id|group:G|bundle:B|name> … [--dest DIR] [--format auto|keep|png|jpg]
                          [--width N] [--bg HEX] [--zip NAME]
                                                  copy (or convert) into DIR and print the paths
    python3 assets.py check [--site REPO] [--update]
                                                  the library is intact; with --site, drift against the site repo

`get` default format is `auto`: files are delivered as they are, except WebP photographs, which become JPG
(PNG if they have transparency) because not every app opens WebP. `--format keep` forces the original.
SVG -> PNG needs playwright (+ Chromium); everything else is Pillow or the standard library.
Nothing here recolours, redraws or crops a logo: only the container format and, if asked, the pixel width change.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
LIB = SKILL_DIR / "assets"
CATALOG = SKILL_DIR / "references" / "catalog.json"
ROSTER = SKILL_DIR / "references" / "data" / "speakers.json"
AUTO_ZIP_OVER = 8  # a request that resolves to more files than this is delivered as one zip


# ----------------------------------------------------------------------------- catalogue

def _fold(s: str) -> str:
    """Case- and accent-insensitive key: 'João' ~ 'joao'; curly and straight quotes alike."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("’", "'").replace("'", "").replace("-", " ").replace("&", " and ").split())


def load():
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = list(cat["entries"])
    for s in json.loads(ROSTER.read_text(encoding="utf-8"))["speakers"]:
        entries.append({
            "id": "speaker." + s["slug"],
            "title": "%s — %s" % (s["display"], s["role"]),
            "kind": "portrait", "group": "speakers", "ground": "any",
            "files": ["speakers/%s.webp" % s["slug"]],
            "aliases": ["speaker", "palestrante", "orador", "oradora", "foto", "fotografia", "retrato", "headshot", "portrait", s["name"]],
            "caution": cat["speaker_caution"],
            "_speaker": s,
        })
    return cat, entries


def _haystack(e: dict) -> str:
    return _fold(" ".join([e["id"], e["title"], e["group"], e["kind"], e.get("note", "")] + e.get("aliases", [])))


def search(entries, words):
    toks = _fold(" ".join(words)).split()
    scored = []
    for e in entries:
        h = _haystack(e)
        n = sum(1 for t in toks if t in h)
        if n:
            scored.append((n, e))
    if not scored:
        return []
    best = max(n for n, _ in scored)
    # every word matched → only those; otherwise the best partial matches
    return [e for n, e in scored if n == best]


def speaker_hits(entries, query):
    q = _fold(query)
    out = []
    for e in entries:
        s = e.get("_speaker")
        if s and (q in _fold(s["name"]) or q in _fold(s["display"]) or q == _fold(s["slug"].replace("-", " "))):
            out.append(e)
    return out


def fmts(e) -> str:
    return "+".join(sorted({Path(f).suffix.lstrip(".").lower() for f in e["files"]}))


def line(e) -> str:
    flags = []
    if e.get("cleared") is False:
        flags.append("not cleared")
    if e.get("status") == "draft":
        flags.append("DRAFT")
    return "%-34s %-5s %-6s %s%s" % (e["id"], e["ground"], fmts(e), e["title"], ("  [%s]" % ", ".join(flags)) if flags else "")


def cmd_list(args, cat, entries):
    groups = {}
    for e in entries:
        groups.setdefault(e["group"], []).append(e)
    if args.group:
        groups = {g: v for g, v in groups.items() if g == args.group}
        if not groups:
            sys.exit("no group %r — groups: %s" % (args.group, ", ".join(sorted({e["group"] for e in entries}))))
    print("id (ground: dark = for navy/dark backgrounds, light = for white/light, any = both)")
    for g, items in groups.items():
        print("\n== %s  (get group:%s, %d)" % (g, g, len(items)))
        for e in items:
            print("  " + line(e))
    if not args.group:
        print("\nbundles: " + "; ".join("bundle:%s = %s" % (k, "+".join(v)) for k, v in cat["bundles"].items()))


def cmd_find(args, cat, entries):
    hits = search(entries, args.words)
    if not hits:
        print("no match for %r — `list` shows everything; if it is not in the library, say so." % " ".join(args.words))
        return 1
    for e in hits[:40]:
        print(line(e))
    if len(hits) > 40:
        print("… %d more — narrow the words" % (len(hits) - 40))
    return 0


def cmd_speaker(args, cat, entries):
    hits = speaker_hits(entries, " ".join(args.name))
    if not hits:
        print("%r is not on the site's roster — not available, and not to be named or drawn." % " ".join(args.name))
        return 1
    for e in hits:
        s = e["_speaker"]
        print("%2d  %-28s %s  [%s]" % (s["order"], s["display"], s["role"], e["id"]))
    return 0


# ----------------------------------------------------------------------------- delivery

def default_dest() -> Path:
    out = Path("/mnt/user-data/outputs")
    return out if out.is_dir() else Path.cwd() / "output" / "assets"


def resolve(tokens, cat, entries):
    by_id = {e["id"]: e for e in entries}
    out = []
    for t in tokens:
        if t.startswith("group:"):
            ms = [e for e in entries if e["group"] == t[6:]]
        elif t.startswith("bundle:"):
            groups = cat["bundles"].get(t[7:])
            if groups is None:
                sys.exit("no bundle %r — bundles: %s" % (t[7:], ", ".join(cat["bundles"])))
            ms = [e for e in entries if e["group"] in groups]
        elif t in by_id:
            ms = [by_id[t]]
        else:
            ms = speaker_hits(entries, t)
            if len(ms) != 1:
                near = ms or search(entries, [t])
                sys.exit("%r is not one id (%s) — pick from: %s" % (t, "no match" if not near else "%d matches" % len(near),
                                                                     ", ".join(e["id"] for e in near[:8]) or "`list`"))
        if not ms:
            sys.exit("nothing for %r — `list` shows the groups" % t)
        out += ms
    seen, uniq = set(), []
    for e in out:
        if e["id"] not in seen:
            seen.add(e["id"])
            uniq.append(e)
    return uniq


def _svg_to_png(src: Path, dst: Path, width: int):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("SVG -> PNG needs playwright: pip install playwright && python3 -m playwright install chromium")
    import re
    text = src.read_text(encoding="utf-8")
    m = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)"', text)
    vw, vh = (float(m.group(1)), float(m.group(2))) if m else (4.0, 3.0)
    height = max(1, round(width * vh / vw))
    with tempfile.TemporaryDirectory() as td:
        page_html = Path(td) / "p.html"
        page_html.write_text('<html><body style="margin:0;background:transparent"><img src="%s" style="display:block;width:%dpx;height:%dpx"></body></html>'
                             % (src.as_uri(), width, height), encoding="utf-8")
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": width, "height": height})
            pg.goto(page_html.as_uri())
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(dst), omit_background=True)
            b.close()


def _hex(s: str):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def deliver_file(src: Path, dest: Path, fmt: str, width, bg: str, notes: list) -> Path:
    from_ext = src.suffix.lower()
    want = fmt
    if fmt == "auto":
        want = "jpg" if from_ext == ".webp" else "keep"
    passthrough = from_ext in (".ttf", ".otf", ".pdf", ".txt")
    if passthrough or (want == "keep" and not width):
        out = dest / src.name
        shutil.copy2(src, out)
        if passthrough and (width or fmt in ("png", "jpg")):
            notes.append("%s: format/width ignored (not an image)" % src.name)
        return out
    if from_ext == ".svg":
        if want in ("keep", "svg") and not width:
            out = dest / src.name
            shutil.copy2(src, out)
            return out
        w = width or 1600
        out = dest / ("%s%s.png" % (src.stem, "-%dw" % width if width else ""))
        if want == "jpg":
            notes.append("%s: an SVG logo has transparency — delivered as PNG, not JPG" % src.name)
        _svg_to_png(src, out, w)
        return out
    from PIL import Image
    im = Image.open(src)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    ext = {"keep": from_ext.lstrip("."), "jpg": "jpg", "png": "png", "webp": "webp"}[want]
    if ext in ("jpg", "jpeg") and has_alpha:
        if from_ext == ".webp" and fmt == "auto":
            ext = "png"  # auto never flattens transparency
        else:
            notes.append("%s: transparent areas flattened onto %s for JPG" % (src.name, bg))
    resized = False
    if width:
        if width >= im.width:
            notes.append("%s: source is %d px wide — not upscaled" % (src.name, im.width))
        else:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            resized = True
    out = dest / ("%s%s.%s" % (src.stem, "-%dw" % width if resized else "", ext))
    if ext in ("jpg", "jpeg"):
        if has_alpha:
            base = Image.new("RGB", im.size, _hex(bg))
            base.paste(im.convert("RGBA"), mask=im.convert("RGBA").getchannel("A"))
            im = base
        im.convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    elif ext == "png":
        im.save(out, "PNG", optimize=True)
    else:
        im.save(out)
    return out


def pick_files(e: dict, fmt: str):
    """With --format png/jpg prefer an entry's native file of that type over converting its other one."""
    files = [LIB / f for f in e["files"]]
    if fmt in ("png", "jpg"):
        native = [p for p in files if p.suffix.lower().lstrip(".").replace("jpeg", "jpg") == fmt]
        if native:
            return native
    return files


def cmd_get(args, cat, entries):
    items = resolve(args.ids, cat, entries)
    dest = Path(args.dest) if args.dest else default_dest()
    dest.mkdir(parents=True, exist_ok=True)
    srcs = [(e, p) for e in items for p in pick_files(e, args.format)]
    zip_name = args.zip
    if not zip_name and len(srcs) > AUTO_ZIP_OVER:
        zip_name = "wm-assets-" + _fold(args.ids[0]).replace(" ", "-").replace(":", "-").replace(".", "-")
        print("auto-zip: %d files" % len(srcs))
    work = Path(tempfile.mkdtemp(prefix="wm-assets-")) if zip_name else dest
    notes, done = [], []
    try:
        for e, p in srcs:
            if not p.is_file():
                sys.exit("library file missing: %s — run `check`" % p.relative_to(SKILL_DIR))
            done.append((e, deliver_file(p, work, args.format, args.width, args.bg, notes)))
        if zip_name:
            zp = dest / (zip_name if zip_name.endswith(".zip") else zip_name + ".zip")
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                for _, f in done:
                    z.write(f, f.name)
            files = [(None, zp)]
        else:
            files = done
    finally:
        if zip_name:
            shutil.rmtree(work, ignore_errors=True)
    for e, f in files:
        print("FILE  %s  (%.1f KB)%s" % (f.resolve(), f.stat().st_size / 1024, "  [%s]" % e["id"] if e else "  [zip of %d]" % len(done)))
    cautions = {}
    for e in items:
        if e.get("caution"):
            cautions.setdefault(e["caution"], []).append(e["id"])
    for msg, ids in cautions.items():
        print("NOTE [%s%s]: %s" % (", ".join(ids[:3]), " …+%d" % (len(ids) - 3) if len(ids) > 3 else "", msg))
    for e in items:
        if e.get("status") == "draft":
            print("DRAFT [%s]: not final — say so when sending" % e["id"])
        if e["kind"] == "portrait":
            s = e["_speaker"]
            print("ROLE  %s — %s" % (s["display"], s["role"]))
    for n in notes:
        print("NOTE: " + n)
    return 0


# ----------------------------------------------------------------------------- check

def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def cmd_check(args, cat, entries):
    problems = 0
    listed = {f for e in entries for f in e["files"]}
    for f in sorted(listed):
        if not (LIB / f).is_file():
            print("MISSING in library: %s" % f)
            problems += 1
    on_disk = {str(p.relative_to(LIB)) for p in LIB.rglob("*") if p.is_file() and p.name != ".DS_Store"}
    for f in sorted(on_disk - listed):
        print("UNCATALOGUED file: %s (add it to references/catalog.json or delete it)" % f)
        problems += 1
    print("library: %d files, %d catalogue entries (%d speakers), %.1f MB" % (
        len(on_disk), len(entries), sum(1 for e in entries if e["kind"] == "portrait"),
        sum((LIB / f).stat().st_size for f in on_disk) / 1e6))
    if args.site:
        site = Path(args.site)
        if not site.is_dir():
            sys.exit("site repo not found: %s" % site)
        drift = 0
        for rel, srel in cat["site_map"].items():
            s, l = site / srel, LIB / rel
            if not s.is_file():
                print("GONE from site: %s (library has %s)" % (srel, rel))
                drift += 1
            elif _md5(s) != _md5(l):
                print("DRIFT: %s differs from the site's %s" % (rel, srel))
                drift += 1
                if args.update:
                    shutil.copy2(s, l)
                    print("   updated from site")
        known = set(cat["site_map"].values()) | set(cat["site_ignore"])
        for sub in ("assets/img", "assets/docs"):
            for p in sorted((site / sub).glob("*")):
                r = str(p.relative_to(site))
                if p.is_file() and p.name != ".DS_Store" and r not in known:
                    print("NEW on site, not in library: %s" % r)
                    drift += 1
        ids = {e["id"] for e in entries}
        for p in sorted((site / "assets/img/speakers").glob("*.webp")):
            if "speaker." + p.stem not in ids:
                print("NEW speaker portrait on site: %s" % p.name)
                drift += 1
        print("site: %s" % ("no drift" if not drift else "%d difference(s) — decide per item; add new files by hand to assets/ and the catalogue" % drift))
        problems += drift if not args.update else 0
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("list"); p.add_argument("--group")
    p = sp.add_parser("find"); p.add_argument("words", nargs="+")
    p = sp.add_parser("speaker"); p.add_argument("name", nargs="+")
    p = sp.add_parser("get")
    p.add_argument("ids", nargs="+")
    p.add_argument("--dest")
    p.add_argument("--format", choices=["auto", "keep", "png", "jpg"], default="auto")
    p.add_argument("--width", type=int)
    p.add_argument("--bg", default="#FFFFFF", help="background for a transparent image saved as JPG")
    p.add_argument("--zip")
    p = sp.add_parser("check"); p.add_argument("--site"); p.add_argument("--update", action="store_true")
    args = ap.parse_args()
    cat, entries = load()
    sys.exit({"list": cmd_list, "find": cmd_find, "speaker": cmd_speaker, "get": cmd_get, "check": cmd_check}[args.cmd](args, cat, entries) or 0)


if __name__ == "__main__":
    main()
