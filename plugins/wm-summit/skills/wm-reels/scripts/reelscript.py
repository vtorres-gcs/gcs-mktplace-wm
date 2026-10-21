"""Parser for output/<slug>/script.md (structure in references/script-template.md).

    import reelscript
    s = reelscript.parse(Path("output/x/script.md").read_text(encoding="utf-8"))
    s["length"], s["keyword"], s["beats"][0]["spoken"], s["caption"]

Standard library only (Python 3.9+).
"""

import re

QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')
DASH = {"", "-", "—", "–", "n/a", "none"}


def _section(md, heading):
    m = re.search(r"^##\s+" + re.escape(heading) + r"\s*$", md, re.M)
    if not m:
        return ""
    rest = md[m.end():]
    n = re.search(r"^##\s+", rest, re.M)
    return (rest[:n.start()] if n else rest).strip()


def _header(md, field):
    m = re.search(r"^" + re.escape(field) + r":\s*(.+)$", md, re.M)
    return m.group(1).strip() if m else ""


def _clean(cell):
    return cell.strip()


def _is_dash(s):
    return s.strip().lower() in DASH


def _spoken_lines(cell):
    """Quoted lines in a Spoken cell; an unquoted non-dash cell counts as one line."""
    if _is_dash(cell):
        return []
    found = [a or b for a, b in QUOTED.findall(cell)]
    return found or [cell.strip()]


def parse(md):
    out = {"raw": md}
    out["title"] = (re.search(r"^#\s+(.+)$", md, re.M) or [None, ""])[1].strip() if re.search(r"^#\s+(.+)$", md, re.M) else ""
    for f in ("Facts as of", "Platform", "Language", "Goal", "Length", "Post date", "Presenter"):
        out[f.lower().replace(" ", "_")] = _header(md, f)
    concept = _section(md, "Concept")
    out["concept"] = concept
    km = re.search(r"^Keyword:\s*(.+)$", concept, re.M)
    out["keyword"] = km.group(1).strip() if km else ""
    out["sends"] = (re.search(r"^Sends test:\s*(.+)$", concept, re.M) or [None, ""])[1].strip() if re.search(r"^Sends test:\s*(.+)$", concept, re.M) else ""

    lm = re.search(r"(\d+(?:\.\d+)?)\s*s", out["length"])
    out["length_s"] = float(lm.group(1)) if lm else None

    beats = []
    for line in _section(md, "Beats").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c for c in line.strip("|").split("|")]
        if len(cells) < 6:
            continue
        if cells[0].strip().lower() in ("#", "") or set(cells[0].strip()) <= set("-: "):
            continue
        sec = re.match(r"\s*(\d+(?:\.\d+)?)\s*[–—-]\s*(\d+(?:\.\d+)?)", cells[1])
        if not sec:
            continue
        beats.append({
            "n": cells[0].strip(),
            "start": float(sec.group(1)),
            "end": float(sec.group(2)),
            "shot": _clean(cells[2]),
            "onscreen": "" if _is_dash(cells[3]) else _clean(cells[3]),
            "spoken_cell": _clean(cells[4]),
            "spoken": _spoken_lines(cells[4]),
            "audio": _clean(cells[5]),
        })
    out["beats"] = beats

    out["cover"] = _section(md, "Cover")
    cap = _section(md, "Caption")
    hm = re.search(r"^Hashtags:\s*(.*)$", cap, re.M)
    out["hashtags_line"] = hm.group(1).strip() if hm else ""
    out["caption"] = re.sub(r"^Hashtags:.*$", "", cap, flags=re.M).strip()
    out["hashtags"] = re.findall(r"(?<!\w)#\w+", out["hashtags_line"])
    out["alt"] = re.findall(r"^\s*(?:Frame|Slide)\s*\d+\s*[—–-]\s*(\S.*)$", _section(md, "Alt text"), re.M)
    out["before_publishing"] = _section(md, "Before publishing")
    return out


def words(text):
    return re.findall(r"[\w'’À-ɏ%€.,-]+", text)
