# Confirmed facts — Wealth & Migration Summit 2026

**As of 20 Oct 2026**, read from the site repo `gcs-wealth-migration-summit` at commit `ab1fe08`. **Programme source: `programme/build.py` (the table behind `agenda.html`) — the user's decision of 20 Oct 2026**; speakers, rates and site facts from `index.html`. This skill's copy differs from the sibling `wm-social-media` / `w&m-web-banners` skills, which still follow `index.html` for the programme. Machine-readable copies: `references/data/{speakers,programme,programme_index,rates,site}.json`, read through `scripts/facts.py`. Refresh with `scripts/sync_site_facts.py` (see "Keeping this current").

## Precedence

| For | The authority is |
|---|---|
| Facts — dates, prices, programme, speakers, capacity, what's included, how to book | **This file and `references/data/`** |
| Voice, positioning, audience, what must never be invented, accessibility floor | `PRODUCT.md` |
| Palette, type, components, rules | `DESIGN.md` |

`PRODUCT.md` is a verbatim copy of the site's file; its fact sections have been overtaken by the site (checked against `index.html` and `programme/build.py` at the commit above). Do not edit it (it is replaced wholesale when the site updates it); this file overrides it where they conflict.

## What `PRODUCT.md` still says that is no longer true

| `PRODUCT.md` / older skill | Live site | So |
|---|---|---|
| Day One "The Golden Visa Pathway", Day Two "Structuring, Context & Experience" | Day One **"The New Geography of Wealth & Mobility"**, Day Two **"Global Wealth & the International Family"** | Use the new themes. The old ones are a lint error |
| Programme = nine + ten approved entries; "timings not confirmed" | `programme/build.py`: Day One 14 main-stage rows (10 sessions, 4 breaks) + 5 workshops; Day Two 17 rows (12 sessions, 5 breaks) + 5 workshops — **every row has a start and an end time**, sessions carry a format and their speakers | Times and speaker lines may be used — only from `data/programme.json` |
| Open client question: split the Day One Golden Visa session | The programme was restructured; there is no such session any more | Drop the question. Nothing to resolve or avoid |
| "Approximately 150–200 curated delegates" | **"Limited to 200"** / "Attendance is limited to 200 attendees" | Say 200. Never "150" |
| Seven audience segments | Four: *Global individuals & families · Legal & tax counsel · Private banking · Industry and Government* | Use the four on the site. The seven are in the older copy deck only |
| 14 named speakers; ask the user for the roster | **26 speakers** on the site, each with role, bio and portrait | Roster is bundled. Nobody else is named |
| Duarte Calheiros Menezes has no portrait (initials) | Portrait exists and is bundled | Use the portrait |
| Ticket pricing absent; "never invent prices" | Three rate tiers published (below) | Prices are allowed — only the published ones, only the tier in force on the post date |
| Registration = register interest, "the start of a vetted process", "not a checkout" | **"Secure your place"** → a booking page with payment ("Your place is confirmed once payment is received") | CTA is booking, not enquiry. Follow-up-by-a-human framing is gone |
| Private networking dinner (Day One evening), closing reception | **Cocktail reception on the evening of Day Two**, networking lunches both days, a guided wine experience (Day Two 16:30) | No dinner, ever |
| Registration URL not known | Domain `wealthandmigrationsummit.com`; booking page `/claim-your-seat` (served `noindex`) | See "Booking" for the go-live caveat |
| Hero: "Where international wealth and global mobility meet." | **"Your residency, your citizenship, your Plan B. Don't let the world decide for you."** | Use as the site's own headline (verbatim) |

## The event

- **Dates:** 5–6 November 2026 (Thursday and Friday). **City:** Lisbon, Portugal.
- **Venue:** EPIC SANA Marques Hotel (see "Spelling" — the site also writes *Marquês*). Convened by Global Citizen Solutions. The Summit chair named in `PRODUCT.md` is Patricia Casaburi.
- **Format:** two days · main stage + parallel **workshops · breakout room** · networking lunches on both days · cocktail reception on the evening of Day Two (the venue section calls it "a rooftop cocktail evening overlooking the city").
- **Capacity:** limited to 200 attendees.
- **Site's own lines** (verbatim, usable in Mode B):
  - Service line: `5–6 November 2026 · Lisbon`
  - Lede: *The Summit gathering for global citizens, advisors, family offices and industry leaders building global mobility and cross-border strategies.*
  - About: *Capital is becoming mobile, and the right decisions need the right people in the room* — Residency and citizenship planning are increasingly treated as part of a broader wealth strategy, not an isolated legal decision.
  - Setting: *Lisbon, a European capital with a global outlook.*
  - Countdown label: "Summit opens in" (target 5 Nov 2026, 09:00 Lisbon time).
- **Convener's footer facts:** 10+ years advising international clients · 100+ professionals across legal, immigration and advisory teams · a global network spanning multiple jurisdictions. Descriptor now: *Global mobility advisory, helping global citizens turn cross-border planning into actionable mobility goals.* (`register-interest.html` still carries the older "Residency and citizenship planning advisory, helping high-net-worth families…" — use the `index.html` line.)

## Programme

- **Source: `programme/build.py`** (the `DAYS` table that also builds `agenda.html` and the PDFs) → `data/programme.json`. Inspect with `python3 scripts/facts.py programme [1|2]`; people and slots to confirm with `facts.py names` and `facts.py overlaps`. The home page (`index.html`) shows a **different** schedule — kept in `data/programme_index.json` for comparison only; nothing reads it when a deck is built. See "Sources disagree".
- **Day One · 5 Nov — The New Geography of Wealth & Mobility.** Registration 08:30; Keynote "Opening Remarks" 09:00 (Mehdi Kadiri); panel "The Future of Investment Migration" 09:15 (Patricia Casaburi, Mehdi Kadiri); "Where Wealth Is Moving: Global Outflows, Inflows & New Hubs" 10:00; governments panel 11:10; Portugal's investment-fund panel 11:55; lunch 12:40; "Europe Mobility 2027" 14:00; "USA Immigration Policy" 14:40; "Asset Location vs. Asset Allocation" 15:35; fireside chat "The Global Citizen's Checklist" 16:10; closing remarks 16:50–17:00. Workshops: Portugal NHR to IFICI (11:00), Italy (12:00), Portugal real estate (14:00), Beyond Sanctions (15:00), Greece (16:00).
- **Day Two · 6 Nov — Global Wealth & the International Family.** Day Two Welcome 09:15; "Where Is Capital Going?" 09:30; "Family Wealth & Succession" 10:15; "The Global Wealth Playbook: Tax & Jurisdiction" 11:00; longevity (11:10, 11:30); "Building a Global Plan B, C and D" 11:50; lunch 12:35; "The Regulatory Horizon" 14:00; "Beyond the Golden Visa: Integration and Contribution" 14:30; "Raising Global Children" 15:25; passion assets 16:00; closing remarks 16:40; "Wine Tasting & Farewell Networking" 16:50–17:30. Workshops: US taxes for Americans abroad (11:00), Spain (12:00), Caribbean (14:00), Panama (15:00), Malta (16:00).
- **Rules**
  1. A session title goes on a slide verbatim from `programme.json` (`full`). Check with `facts.find_session("…")`.
  2. A time goes on a slide only if it is in `facts.known_times()` — now **start and end** times. A deck shows start times by default; end times are opt-in (`end_times: true`) because the agenda's ranges overlap in two places (below).
  3. **Speaker lines come from the agenda, as written** (`facts.speaker_line`): `Name, Org (Role)`. A slot the agenda marks *To be announced* is drawn as "to be announced" — never a guessed name. Ten people on the agenda are **not** on the site's 26-speaker roster (no card, portrait or bio): Lourenço Alvares, Maggie Williams, Grazi Fulchiron, Diogo Pedro, Joana M., Gonçalo Peixoto, Dr. Joana Costa, Sheree M. Mitchell, Gizane Campos, Adrien Bridge. They may appear in a programme row exactly as the agenda writes them; they get no portrait, no bio slide, no "speakers" count, and the hand-off says they need confirming. Five slots are *to be announced* today (`facts.py names`).
  4. **Overlaps the organiser must confirm** (the site's own `THEMES.md`): Day Two coffee 10:55–11:10 runs into the 11:00 tax panel, which runs to 11:15 and into the 11:10 100-Year Life presentation. Start times are shown as published; the hand-off says so.
  5. A programme slide carries the agenda's own line, **"Programme subject to change."**, on its last page (a deck can override it with `note`).
  6. Count only what is unambiguous: **2 days · 10 workshops · 26 speakers**. Don't state a "session" count — the main-stage rows include coffee, lunch and registration, and nothing on the site defines "session".
- **Workshop countries.** The home page's intro sentence names *Italy, Spain, Portugal, Greece, the Caribbean, Panama, and Turkey*; the agenda's workshop list has **Malta** and **no Turkey**. Use the list; do not mention Turkey or leave out Malta without telling the user.

## Speakers

26, in the site's order (`python3 scripts/facts.py speakers`). Name, role and bio come from `data/speakers.json` (the site's own cards); portraits from `assets/speakers/<slug>.webp` — all 26 bundled. A person not in the roster gets no portrait, bio or speaker slide and is not counted in the 26. The agenda names ten such people (listed under Programme rule 3): they appear only as a speaker line in a programme row, exactly as the agenda writes them, and are flagged in the hand-off.

**Name and role as the card has them** (`display` in the JSON). Known inconsistencies — flag, don't resolve:

| Card | Issue | Do |
|---|---|---|
| Ayoub Rebroub — "Legal Manager, Malta at Endevio Group" | Bio says "the newly appointed CEO of Endevio Group" | Use the role line; don't repeat the CEO claim |
| Yanimar Hernandez — "Legal Manager, Spain at …" | Bio is written about "Yanimar **Rodriguez**", "Head of Legal Spain" | Use name + role from the card; don't quote the bio |
| Bruno L'ecuyer | Agenda: "L'Ecuyer"; card: "L'ecuyer" | Card spelling |
| Mehdi Kadiri | Client roster docx: "El-Kadiri" | Card spelling |
| H.E. Calvin St. Juste | Agenda: "St Juste" | Card spelling |
| Adalberto Pucca | Roster docx header "Head of Global Sales"; card "Head of Global Client Advisory" | Card |
| João Pacheco Gonçalves | docx "Head of Institutional Client Relations"; card "Head of Institutional Relations" | Card |
| Dr. Nina Patrick, PhD | "Dr." and "PhD" together | `display` drops the suffix |

Bios are long and copied verbatim from the site; a card gets **no bio** (`carousel-template.md`) — a spotlight caption may quote ≤ 40 words of it, whole sentences only.

## Rates and booking

`data/rates.json`; `facts.rate_on()` returns the tier in force.

| Tier | Price | Window |
|---|---|---|
| Early bird | €399 | 1 Sep – 3 Oct |
| Advance Rate | €499 | 4 Oct – 30 Oct |
| Final Rate | €599 | 31 Oct – 4 Nov |

- Nothing is published for 5–6 Nov. Before 1 Sep and after 4 Nov: say nothing about price.
- **A price is only ever the tier in force on the date the post goes live.** If it ends before the likely post date, either use the next tier or leave price out. `facts.freshness()` warns inside the last 7 days of a tier. The hand-off must say which tier was used and until when it is true.
- A deadline is a fact ("Advance Rate until 30 October"); "last chance", "only N seats", "book now" are not. Say the date, never the pressure.
- **Included:** full access to both days of conference sessions and specialist workshops · networking lunch on both days · cocktail reception on the evening of Day Two.
- **CTA verb:** "Secure your place" (site), "Book your place" (booking page title). Not "Register your interest" — that is the older page (`register-interest.html` still exists: "we will keep you updated on ticket availability").
- **Where:** domain `wealthandmigrationsummit.com` (from the site's share metadata); booking page `/claim-your-seat`. **Unverified:** whether the site's staging password gate has been lifted (`CLAUDE.md` of the site repo: "currently sits behind HTTP Basic Auth"). **Ask once before printing a URL on a graphic;** until confirmed, graphics say "Link in bio" / "Link in the comments" and the URL goes in a caption only after the user confirms.

## Partners and media

- The hero shows two marks next to the title: **Global Citizen Solutions** and **CNN Portugal**.
- The partner strip under "Interested in partnering with the Summit?" shows ten logos: Goldcrest Portugal Real Estate, Optimize Investment Partners, CapitalPartners (a member of Gaw Capital), Blue Crow, Lisboa 2030, Portuguese Chamber of Commerce, CNN Portugal, Atlântico Europa, João M. Barbosa, Cascais Ventures. **The site does not say what each one is** (sponsor, partner, media, venue-side). The skill does not say either.
- **Rule:** no partner or sponsor logo on a social creative unless the user names it for this post and confirms it is cleared for social use. No tiers, no "official partner of…" wording, no thank-you posts that imply a role. Logos live in `assets/img/` (`summit_assets` keys `partner.*`); several speakers' companies appear there too (Optimize, Blue Crow, Cascais Ventures) — a speaker card is not a partnership statement.
- **Partner enquiries:** the site now opens a form ("Explore partnership"); it does not print an address. `events@globalcitizensolutions.com` is in `PRODUCT.md` and the copy deck. Use it only after the user confirms it is still the route; otherwise "Link in bio".

## Spelling and verbatim copy

- Authored copy: **British English** (programme, organised, colour).
- The live site itself mixes in US forms ("organized", "specializing" in a bio) and spells the venue both **"EPIC SANA Marques Hotel"** (hero, venue section) and **"EPIC SANA Marquês"** (what's-included, booking page, agenda).
- Mode B (verbatim) keeps the source's spelling. Mode A writes British. For the venue, default to the hero's **"EPIC SANA Marques Hotel"** and tell the user the site uses both — it is a client call, not ours.

## Still absent — must not be fabricated

Delegate or client testimonials · past-edition figures (attendance, countries, sessions) · GCS-owned photography of Lisbon or the venue (the site's imagery is generated and on the client's replacement list; the venue photo on the site is not evidence for a claim) · sponsor tiers or sponsor roles · speaker↔session pairings beyond what the agenda prints · who "Joana M.", "Maggie Williams" and the other agenda-only names are · any statement about attendance numbers so far.

## Sources disagree

The site repo holds two schedules and its own `programme/THEMES.md` (19 Oct) calls the mismatch "pending editorial resolution before publication". **This skill follows `programme/build.py` (`agenda.html`) — decided by the user on 20 Oct 2026.** Every deck that shows the programme says so in the hand-off.

| Topic | `programme/build.py` / `agenda.html` (this skill) | `index.html` (the public home page) |
|---|---|---|
| Day One opening | 09:00 Keynote "Opening Remarks", 09:15 "The Future of Investment Migration" (Casaburi, Kadiri) | 09:00 Opening Remarks, 09:10 "The Future of Global Mobility: The Global Citizen in 2026 and Beyond" |
| Main-stage rows | 14 (Day One) and 17 (Day Two), with end times, format, speakers, moderators | 15 per day, start times only, no speakers |
| Day One Portugal workshop | "Portugal: From NHR to IFICI & Residence Planning" | "Plan Smart: Combining Residency and Tax Benefits in Portugal — The IFICI Opportunity" |
| Day Two evening | 16:50–17:30 "Wine Tasting & Farewell Networking" | 16:30 "A Taste of Portugal: A Guided Wine Experience" |
| Disclaimer | "Programme subject to change." | none |

If the client resolves it the other way, run `sync_site_facts.py sync` after changing `extract_agenda` / the source, and re-read this file. Until then: titles, times, formats and speaker lines are the agenda's; the home page's version is not mixed in.

## Keeping this current

```bash
python3 scripts/sync_site_facts.py check "/Volumes/GCS - DISK 1T/GCS 2026/Github/gcs-wealth-migration-summit"   # drift report, writes nothing
python3 scripts/sync_site_facts.py sync  "/Volumes/GCS - DISK 1T/GCS 2026/Github/gcs-wealth-migration-summit"   # refresh references/data/*.json
```

After a `sync`: re-read the tables above (they are hand-written), replace `references/PRODUCT.md` / `DESIGN.md` with the site's copies if `check` says they differ, update the "As of" line. The site repo is read-only for this purpose. Everything here expires after **6 Nov 2026**.
