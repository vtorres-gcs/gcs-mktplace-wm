"""Refresh the skill's fact files from the Summit site repo.

The skill is self-contained at run time: it reads references/data/*.json, never the site.
This script is the maintenance step that keeps those files honest. It only READS the site repo.

    python3 sync_site_facts.py sync  <site-repo>     # rewrite references/data/*.json
    python3 sync_site_facts.py check <site-repo>     # report drift, write nothing (exit 1 on drift)

Sources (decided by the user on 20 Oct 2026):
  programme.json        programme/build.py (the DAYS table that also feeds agenda.html): every session with
                        start/end time, format and its speakers, every workshop with its leaders
  programme_index.json  the programme as index.html publishes it — kept only so `check` can report how the
                        two still differ; nothing reads it at deck-build time
  speakers, rates, site index.html

`check` compares, against the bundled copies:
  - speakers (names, roles, order), programme (days, themes, times, titles), rate tiers, hero facts
  - PRODUCT.md / DESIGN.md (verbatim copies that must be replaced when the site changes them)
  - speaker portraits present in the site but missing from assets/speakers/

Standard library only. The site's own programme/THEMES.md calls the index.html / agenda mismatch an open editorial
question (see references/FACTS.md, "Sources disagree").
"""

from datetime import date
from pathlib import Path
import ast
import html
import json
import re
import subprocess
import sys

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA = SKILL_DIR / "references" / "data"
REFS = SKILL_DIR / "references"
SPEAKER_DIR = SKILL_DIR / "assets" / "speakers"


def _text(fragment: str) -> str:
    """Visible text of an HTML fragment: tags dropped, entities decoded, whitespace collapsed."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def _git(site: Path, *args) -> str:
    try:
        return subprocess.run(["git", "-C", str(site), *args], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _meta(site: Path, source: str) -> dict:
    return {
        "source": source,
        "site_commit": _git(site, "rev-parse", "--short", "HEAD") or None,
        "site_dirty": bool(_git(site, "status", "--porcelain", "--", source)),
        "extracted_on": date.today().isoformat(),
    }


# ----------------------------------------------------------------------------
# Extractors — each returns plain data, so `check` can diff it against the bundled JSON
# ----------------------------------------------------------------------------

def extract_speakers(src: str) -> list:
    out = []
    for n, m in enumerate(re.finditer(r'<button class="speaker"(.*?)>', src, re.S), 1):
        a = {k: html.unescape(v) for k, v in re.findall(r'(data-[a-z\-]+)="([^"]*)"', m.group(1))}
        name = a["data-name"].strip()
        display = re.sub(r",\s*PhD$", "", name) if name.startswith("Dr.") else name
        slug = Path(a.get("data-photo", "")).stem
        out.append({
            "order": n,
            "name": name,
            "display": display,
            "role": a["data-role"].strip(),
            "bio": a["data-bio"].strip(),
            "slug": slug,
            "photo_bundled": (SPEAKER_DIR / f"{slug}.webp").is_file(),
        })
    return out


def extract_programme(src: str) -> list:
    days = []
    for sec in re.finditer(r'<section class="day" id="(day-[a-z]+)"[\s\S]*?</section>', src):
        block = sec.group(0)
        when = _text(re.search(r'class="day__when">(.*?)</span>', block).group(1))
        theme = _text(re.search(r'class="day__name">(.*?)</span>', block).group(1))
        label, short = [p.strip() for p in when.split("·")]
        tracks = {"main": [], "workshops": []}
        for label_html, ol in re.findall(r'<h4 class="stations__label">(.*?)</h4>\s*<ol class="stations">([\s\S]*?)</ol>', block):
            track = "workshops" if "Workshop" in label_html else "main"
            for li in re.finditer(r'<li class="station( station--break)?" id="([^"]+)">([\s\S]*?)</li>', ol):
                row = li.group(3)
                t = re.search(r'<time datetime="([^"]+)">([^<]+)</time>', row)
                sub = re.search(r'<span class="station__sub">([\s\S]*?)</span>', row)
                head = re.sub(r'<span class="station__sub">[\s\S]*?</span>', "", re.search(r"</time><span>([\s\S]*)</span></div>", row).group(1))
                title = _text(head)
                tail = _text(sub.group(1)) if sub else None
                tracks[track].append({
                    "id": li.group(2),
                    "time": t.group(2),
                    "iso": t.group(1),
                    "kind": "break" if li.group(1) else ("workshop" if track == "workshops" else "session"),
                    "title": title,
                    "subtitle": tail,
                    "full": f"{title} {tail}" if tail else title,
                })
        days.append({"day": label, "date": short, "iso": tracks["main"][0]["iso"][:10], "theme": theme, **tracks})
    return days


def extract_agenda(site: Path) -> dict:
    """The programme as programme/build.py defines it. The DAYS literal is read with ast and evaluated with
    no builtins — build.py itself is never imported (it pulls in playwright/pymupdf and writes files)."""
    tree = ast.parse((site / "programme" / "build.py").read_text(encoding="utf-8"))
    gcs, days_node = None, None
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == "GCS":
                gcs = ast.literal_eval(node.value)
            elif node.targets[0].id == "DAYS":
                days_node = node.value
    if days_node is None:
        raise SystemExit("programme/build.py has no DAYS table — the site changed shape; update extract_agenda")
    raw = eval(compile(ast.Expression(days_node), "<DAYS>", "eval"), {"__builtins__": {}}, {"GCS": gcs, "dict": dict})
    days = []
    for n, d in enumerate(raw, 1):
        seen, main, workshops = set(), [], []
        for start, end, fmt, title, spk in d["main"]:
            rid = f"d{n}-{start.replace(':', '')}"
            while rid in seen:
                rid += "b"
            seen.add(rid)
            main.append({
                "id": rid, "time": start, "end": end, "iso": f"{d['iso']}T{start}",
                "kind": "break" if fmt is None else "session", "format": fmt,
                "title": title, "subtitle": None, "full": title,
                "speakers": [{"name": nm, "org": org, "role": role} for nm, org, role in spk],
            })
        for start, title, names in d["breakout"]:
            workshops.append({
                "id": f"d{n}-w{start.replace(':', '')}", "time": start, "iso": f"{d['iso']}T{start}",
                "kind": "workshop", "title": title, "subtitle": None, "full": title, "speakers": list(names),
            })
        days.append({"day": d["label"], "date": d["short"].split(" ", 1)[1], "iso": d["iso"], "theme": d["theme"],
                     "main": main, "workshops": workshops})
    note = re.search(r'class="prog-intro__note">([\s\S]*?)</p>', (site / "agenda.html").read_text(encoding="utf-8"))
    return {"days": days, "disclaimer": _text(note.group(1)) if note else None}


def extract_rates(src: str) -> dict:
    tiers = []
    for li in re.finditer(r'<li class="tier[^"]*" data-tier-start="([^"]+)" data-tier-end="([^"]+)"[^>]*>([\s\S]*?)</li>', src):
        name = re.search(r'class="tier__name">([\s\S]*?)(?:<span class="tier__flag"|</span>)', li.group(3)).group(1)
        price = _text(re.search(r'class="tier__price">(.*?)</span>', li.group(3)).group(1))
        when = _text(re.search(r'class="tier__when">(.*?)</span>', li.group(3)).group(1))
        tiers.append({"name": _text(name), "price": price, "eur": int(re.sub(r"\D", "", price)),
                      "start": li.group(1), "end": li.group(2), "when": when})
    included = [_text(x) for x in re.findall(r"<li>([\s\S]*?)</li>", re.search(r'class="reg__list">([\s\S]*?)</ul>', src).group(1))]
    limit = _text(re.search(r'class="reg__limit">([\s\S]*?)</p>', src).group(1))
    cta = _text(re.search(r'class="reg__cta"[^>]*>([\s\S]*?)</a>', src).group(1))
    cta_href = re.search(r'class="reg__cta" href="([^"]+)"', src).group(1)
    return {"tiers": tiers, "included": included, "limit": limit, "cta": cta, "cta_href": cta_href}


def extract_site(src: str, site: Path) -> dict:
    og_image = re.search(r'<meta property="og:image" content="([^"]+)"', src).group(1)
    domain = re.match(r"https?://[^/]+", og_image).group(0)
    facts = re.findall(r'<div class="plate"><dt>(.*?)</dt><dd>(.*?)</dd></div>', src)
    room = re.search(r'class="room room--cards">([\s\S]*?)</ul>', src).group(1)
    return {
        "domain": domain,
        "booking_page": (site / "claim-your-seat.html").is_file() and "claim-your-seat" or None,
        "service_line": _text(re.search(r'<p class="service">(.*?)</p>', src).group(1)),
        "headline": _text(re.search(r'<h1 class="destination"[^>]*>([\s\S]*?)</h1>', src).group(1)),
        "lede": _text(re.search(r'<p class="lede">([\s\S]*?)</p>', src).group(1)),
        "hero_facts": {_text(k): _text(v) for k, v in facts},
        "who_is_in_the_room": [_text(x) for x in re.findall(r"<span>([\s\S]*?)</span>", room)],
        "about_heading": _text(re.search(r'id="canyon-h"[^>]*>([\s\S]*?)</h2>', src).group(1)),
        "programme_heading": _text(re.search(r'id="line-h"[^>]*>([\s\S]*?)</h2>', src).group(1)),
        "workshop_countries_sentence": _text(re.search(r'class="line__disclaimer">([\s\S]*?)</p>', src).group(1)),
        "setting_heading": _text(re.search(r'id="mirror-h"[^>]*>([\s\S]*?)</h2>', src).group(1)),
        "venue_names_on_site": sorted(set(re.findall(r"EPIC SANA Marqu[eê]s(?: Hotel)?", src + (site / "claim-your-seat.html").read_text(encoding="utf-8")))),
        "partner_enquiries": "events@globalcitizensolutions.com",
        "partner_cta": _text(re.search(r'id="beacon-h"[^>]*>([\s\S]*?)</h2>', src).group(1)),
        "partner_logos_on_site": [html.unescape(a) for a in re.findall(r'<li><img src="assets/img/[^"]+" alt="([^"]+)"', re.search(r'class="beacon__logos">([\s\S]*?)</ul>', src).group(1))],
        "hero_partner_marks": re.findall(r'class="partner__logo[^"]*">[\s\S]*?alt="([^"]+)"', src),
    }


def extract_all(site: Path) -> dict:
    src = (site / "index.html").read_text(encoding="utf-8")
    return {
        "speakers": extract_speakers(src),
        "programme_index": extract_programme(src),
        "agenda": extract_agenda(site),
        "rates": extract_rates(src),
        "site": extract_site(src, site),
    }


# ----------------------------------------------------------------------------
# sync / check
# ----------------------------------------------------------------------------

def _wrap(site: Path, key: str, payload):
    return {"_meta": _meta(site, "index.html"), key: payload}


def sync(site: Path):
    got = extract_all(site)
    DATA.mkdir(parents=True, exist_ok=True)
    files = {
        "speakers.json": _wrap(site, "speakers", got["speakers"]),
        "programme.json": {"_meta": _meta(site, "programme/build.py"), **got["agenda"]},
        "programme_index.json": _wrap(site, "days", got["programme_index"]),
        "rates.json": {"_meta": _meta(site, "index.html"), **got["rates"]},
        "site.json": {"_meta": _meta(site, "index.html"), **got["site"]},
    }
    for name, payload in files.items():
        (DATA / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote references/data/{name}")
    days = got["agenda"]["days"]
    n_sp, n_main = len(got["speakers"]), sum(len(d["main"]) for d in days)
    n_ws = sum(len(d["workshops"]) for d in days)
    print(f"{n_sp} speakers · {len(days)} days · {n_main} main-stage rows · {n_ws} workshops · {len(got['rates']['tiers'])} rate tiers")
    missing = [s["slug"] for s in got["speakers"] if not s["photo_bundled"]]
    if missing:
        print("WARN  portraits not bundled in assets/speakers/:", ", ".join(missing))
    print("Now re-read references/FACTS.md: it is hand-written and may no longer match.")


def _load(name):
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def _diff_list(label, old, new, key):
    drift = []
    old_k, new_k = {key(x): x for x in old}, {key(x): x for x in new}
    for k in new_k.keys() - old_k.keys():
        drift.append(f"{label}: new on site — {k}")
    for k in old_k.keys() - new_k.keys():
        drift.append(f"{label}: gone from site — {k}")
    for k in old_k.keys() & new_k.keys():
        if old_k[k] != new_k[k]:
            changed = [f for f in new_k[k] if f != "photo_bundled" and old_k[k].get(f) != new_k[k][f]]
            if changed:
                drift.append(f"{label}: changed — {k} ({', '.join(changed)})")
    return drift


def check(site: Path) -> bool:
    got = extract_all(site)
    drift = []
    stored = {n: _load(f"{n}.json") for n in ("speakers", "programme", "programme_index", "rates", "site")}
    if not all(stored.values()):
        print("DRIFT references/data/*.json missing — run `sync` first")
        return False

    drift += _diff_list("speakers", stored["speakers"]["speakers"], got["speakers"], lambda s: s["name"])
    old_order = [s["name"] for s in stored["speakers"]["speakers"]]
    if old_order != [s["name"] for s in got["speakers"]] and set(old_order) == {s["name"] for s in got["speakers"]}:
        drift.append("speakers: same people, new order (roster order decides card order)")
    for label, old_days, new_days in (("programme", stored["programme"]["days"], got["agenda"]["days"]),
                                      ("programme (index.html copy)", stored["programme_index"]["days"], got["programme_index"])):
        for old, new in zip(old_days, new_days):
            if old["theme"] != new["theme"]:
                drift.append(f"{label}: {new['day']} theme changed — {old['theme']!r} -> {new['theme']!r}")
            for track in ("main", "workshops"):
                drift += _diff_list(f"{label} {new['day']} {track}", old[track], new[track], lambda r: r["id"])
        if len(old_days) != len(new_days):
            drift.append(f"{label}: number of days changed")
    if stored["programme"].get("disclaimer") != got["agenda"]["disclaimer"]:
        drift.append(f"programme: disclaimer changed — {stored['programme'].get('disclaimer')!r} -> {got['agenda']['disclaimer']!r}")
    if stored["rates"]["tiers"] != got["rates"]["tiers"]:
        drift.append("rates: tiers changed (prices or dates)")
    for k in ("included", "limit", "cta", "cta_href"):
        if stored["rates"][k] != got["rates"][k]:
            drift.append(f"rates: {k} changed — {stored['rates'][k]!r} -> {got['rates'][k]!r}")
    for k, v in got["site"].items():
        if stored["site"].get(k) != v:
            drift.append(f"site: {k} changed — {stored['site'].get(k)!r} -> {v!r}")

    for name in ("PRODUCT.md", "DESIGN.md"):
        theirs = site / name
        if theirs.is_file() and theirs.read_bytes() != (REFS / name).read_bytes():
            drift.append(f"{name}: differs from the site's copy — replace references/{name} (DESIGN.md feeds the palette)")

    missing = [s["slug"] for s in got["speakers"] if not (SPEAKER_DIR / f"{s['slug']}.webp").is_file()]
    if missing:
        drift.append("portraits missing from assets/speakers/: " + ", ".join(missing))

    # The two programme sources still disagree. That is the site's open editorial question, not drift in this skill.
    a_titles = {r["full"] for d in got["agenda"]["days"] for t in ("main", "workshops") for r in d[t] if r["kind"] != "break"}
    i_titles = {r["full"] for d in got["programme_index"] for t in ("main", "workshops") for r in d[t] if r["kind"] != "break"}
    print(f"NOTE  programme: this skill follows programme/build.py; index.html shows the other version "
          f"({len(a_titles - i_titles)} titles only in build.py, {len(i_titles - a_titles)} only on the home page)")

    print(f"bundled facts extracted {stored['site']['_meta']['extracted_on']} from site commit {stored['site']['_meta']['site_commit']}; "
          f"site is now at {_git(site, 'rev-parse', '--short', 'HEAD') or 'unknown'}")
    if site and _git(site, "status", "--porcelain", "--", "index.html"):
        print("NOTE  the site's index.html has uncommitted changes")
    for d in drift:
        print("DRIFT", d)
    print("in sync" if not drift else f"\n{len(drift)} difference(s) — run `sync`, then re-read references/FACTS.md")
    return not drift


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("sync", "check"):
        print(__doc__)
        sys.exit(2)
    repo = Path(sys.argv[2]).expanduser()
    if not (repo / "index.html").is_file():
        print(f"no index.html in {repo} — pass the Summit site repo root")
        sys.exit(2)
    if sys.argv[1] == "sync":
        sync(repo)
    else:
        sys.exit(0 if check(repo) else 1)
