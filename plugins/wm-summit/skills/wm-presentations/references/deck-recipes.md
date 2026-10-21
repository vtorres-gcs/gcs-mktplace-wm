# Deck recipes — what to build for which request

Pick the recipe by **what the deck is for and who sits in front of it**, then adjust length to the talk (≈ 1.5–2 minutes a slide; a pre-read can run longer because it has to carry the argument alone). Every recipe is a sequence of slide types from `deck-design.md`; `templates/` holds a ready spec for the first.

Before any recipe: read `FACTS.md`; run `python3 scripts/facts.py freshness`; know the **as-of date** (today unless the deck is for a later date — it picks the rate tier).

## 1. Summit overview — "present the Summit" (`templates/summit-overview.json`, 19 slides)

For a prospective delegate, an advisor, a journalist, a first call. Argument: *capital is mobile; the right decisions need the right people in one room; here is the room.*

`cover` (hero, GCS + CNN marks) → `split` (about + venue photo) → `ledger` (2 days · 10 workshops · 28 speakers · 200) → `entries` (@audience) → `days` (two themes, two picked sessions each) → `programme` ×4 (use `"columns": 2` on the main stage) (Day 1 main, Day 1 workshops, Day 2 main, Day 2 workshops) → `speakers` (all) → `rates` → `closing` (the dark-blue back cover). `meta.alternate: true` interleaves white slides (the template also fixes the roster on white and the rates on navy).

Short version (6–8 slides, a live pitch): `cover` → `statement` → `ledger` → `days` → `speakers` (4-up, five or six names the user picks) → `rates` → `closing`. Drop the full programme and roster; say they are on the site.

## 2. Programme deck — "send the agenda"

A pre-read for people deciding which sessions to attend. `cover` → `days` → `programme` for each day and track the user wants (`"columns": 2` fits more rows a slide; speakers are on by default — `"speakers": false` for a bare timetable; `"end_times": true` only after the organiser confirms the Day Two overlaps) → `closing` (`"cta": false` when the readers already hold a place — "Secure your place" is wrong for them). The last programme page carries the agenda's own "Programme subject to change."

## 3. Speaker line-up — "who is speaking"

`cover` → `speakers` (`all`, 8-up, or the chosen names, 4-up) → one `speaker` slide per featured name (full verbatim bio, never trimmed — if a bio does not fit, the build warns; split rather than cut) → `closing`. Roster order is the site's order; a user-chosen subset keeps the order the user gives. A new name the user mentions who is not on the roster is **not drawn** — ask whether the site has been updated, run `sync_site_facts.py check`.

## 4. Partner / sponsor briefing — "talk to a prospective partner"

The site publishes **no sponsor packages, tiers, prices or partner roles**, and no past-edition numbers. A partner deck therefore has two parts: the confirmed Summit (the 6-slide version of recipe 1, minus `rates` — delegate prices are not a partner conversation) and **whatever the user supplies** for the partnership offer.

`cover` → `statement` (why Lisbon, why now — the site's own lines) → `ledger` (days · workshops · speakers · 200) → `entries` (@audience: who the partner meets) → `days` → *user's offer, as `statement` / `entries` slides in the user's words* → `closing` (`headline` "Interested in partnering with the Summit?" via `@site.partner_cta`, `cta` = the route the user confirms; the enquiry address `events@globalcitizensolutions.com` goes in `contact` only after `confirmed: ["email"]`).

Ask once what the offer actually is. If the user has no package yet, say so on the slide plan ("offer slides pending") — do not invent tiers, reach, logos or "official partner" wording. The lint will fail it anyway.

## 5. Delegate welcome / on-site — "the first slide in the room"

For 5–6 Nov, shown by the host. `cover` → `programme` for the day being opened → `section` ("Coffee & networking") only if the user wants dividers → `closing`. Use `--as-of` the day itself; no rate tier is published for 5–6 Nov, so leave the rates slide out; the lint rejects both a price line and a rates slide on those dates.

## 6. Rate / booking announcement — "a deck about securing a place"

Short, because the call-to-action is the point: `cover` → `ledger` → `rates` → `closing`. The `rates` slide marks the **current rate** from `--as-of` and shows all three tiers with their published dates — a deadline is a date, never pressure ("Advance Rate until October 30"). State in the hand-off which tier is marked and the date it stops being true.

## 7. Internal team briefing — "brief the GCS team on the Summit"

Facts as in recipe 1, plus whatever internal content the user supplies (targets, owners, timelines). Internal figures the user gives are the user's — keep them verbatim, mark them in the notes, and tell the user that the lint cannot check them. Nothing internal goes on a slide that will be shared outside GCS.

## Storyline checks (all recipes)

- State the deck's purpose in one sentence before the first slide: a decision, a booking, a conversation opened. If the closing slide does not serve it, the deck is wrong, not the slide.
- Vary the weight: statement → ledger → ruled entries → timed line → portraits. Three identical slides in a row reads as generated.
- Every slide earns its place by a fact, a name or a time — not an adjective about exclusivity. Scarcity is stated as a number (200), never as urgency.
- Use the site's own sentences where they exist (`@site.*`). Writing new copy is allowed; every claim in it must trace to `FACTS.md` or text the user supplied.

## Which programme? — the site disagrees with itself

The site repo holds two versions of the schedule: `programme/build.py` / `agenda.html` (with end times, formats and speakers; updated 20 Oct in site PR #77) and the home page `index.html` (different titles and times). The site's own `programme/THEMES.md` calls the mismatch "pending editorial resolution before publication". **The user chose `programme/build.py` as this skill's source on 20 Oct 2026**, so `data/programme.json` is that version and `data/programme_index.json` is the home page's, kept only so `sync_site_facts.py check` can show how they differ.

Every deck that shows the programme must say in the hand-off: which version it used; that the home page differs; the **ten agenda-only names** (not on the 28-speaker roster) and the **five "to be announced" slots** it shows (`facts.py names`); and the **Day Two overlaps** (`facts.py overlaps`). The build prints all of these as deck-level warnings — carry them through.
