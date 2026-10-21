# Confirmed facts — Wealth & Migration Summit 2026

**As of 21 Oct 2026**, read from the site repo `gcs-wealth-migration-summit` at commit `6725cff` (`index.html` last changed 21 Oct via `ef8ec1a`). Machine-readable copies: `references/data/{speakers,programme,rates,site}.json`, read through `scripts/facts.py`. Refresh with `scripts/sync_site_facts.py` (see "Keeping this current").

## Precedence

| For | The authority is |
|---|---|
| Facts — dates, prices, programme, speakers, capacity, what's included, how to book | **This file and `references/data/`** |
| Voice, positioning, audience, what must never be invented, accessibility floor | `PRODUCT.md` |
| Palette, type, components, rules | `DESIGN.md` |

`PRODUCT.md` is a verbatim copy of the site's file; its fact sections have been overtaken by the site (checked against `index.html` at the commit above). Do not edit it (it is replaced wholesale when the site updates it); this file overrides it where they conflict.

## What `PRODUCT.md` still says that is no longer true

| `PRODUCT.md` / older skill | Live site | So |
|---|---|---|
| Day One "The Golden Visa Pathway", Day Two "Structuring, Context & Experience" | Day One **"The New Geography of Wealth & Mobility"**, Day Two **"Global Wealth & the International Family"** | Use the new themes. The old ones are a lint error |
| Programme = nine + ten approved entries; "timings not confirmed" | 15 main-stage rows + 5 workshops per day, **every one timed**, published on the site | Times may be used — only from `data/programme.json` |
| Open client question: split the Day One Golden Visa session | The programme was restructured; there is no such session any more | Drop the question. Nothing to resolve or avoid |
| "Approximately 150–200 curated delegates" | **"Limited to 200"** / "Attendance is limited to 200 attendees" | Say 200. Never "150" |
| Seven audience segments | Four: *Global individuals & families · Legal & tax counsel · Private banking · Industry and Government* | Use the four on the site. The seven are in the older copy deck only |
| 14 named speakers; ask the user for the roster | **28 speakers** on the site, each with role, bio and portrait | Roster is bundled. Nobody else is named |
| Duarte Calheiros Menezes has no portrait (initials) | Portrait exists and is bundled | Use the portrait |
| Ticket pricing absent; "never invent prices" | Three rate tiers published (below) | Prices are allowed — only the published ones, only the tier in force on the post date |
| Registration = register interest, "the start of a vetted process", "not a checkout" | **"Secure your place"** → a booking page with payment ("Your place is confirmed once payment is received") | CTA is booking, not enquiry. Follow-up-by-a-human framing is gone |
| Private networking dinner (Day One evening), closing reception | **Cocktail reception on the evening of Day Two**, networking lunches both days, a guided wine experience (Day Two 16:50) | No dinner, ever |
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

- **Source of truth for titles, times and speakers: `agenda.html`** (generated from `programme/build.py`) → `data/programme.json`. The homepage (`index.html`) carries the same sessions, titles and times. `agenda-tracks.html` is a thematic-filter view of the same programme with four tracks (see below). Inspect with `python3 scripts/facts.py programme [1|2]`.
- **Day One · 5 Nov — The New Geography of Wealth & Mobility.** Registration from 08:30; Opening Remarks 09:00 (Mehdi Kadiri); The Future of Investment Migration 09:15 (Patricia Casaburi, Mehdi Kadiri); Where Wealth Is Moving 10:00 (João Pacheco Gonçalves moderator); What's in It for Governments? 11:10 (H.E. Calvin St Juste, Alex Muscat, Joe Rice moderator); Portugal's Investment Fund Landscape 11:55 (Pedro Lino, Duarte Calheiros Menezes, Nuno Serafim, Lourenço Alvares moderator); Europe Mobility 2027 14:00 (Adalberto Pucca, Luca Calabrese Q&A, Yanimar Hernandez Q&A, Thanos Tsoukalas Q&A); USA Immigration Policy 14:40 (speaker TBA, Adalberto Pucca Q&A moderator); Asset Location vs. Asset Allocation 15:35 (speaker TBA); The Global Citizen's Checklist 16:10 (Maggie Williams, Grazi Fulchiron); Closing Remarks 16:50 (Mehdi Kadiri). Workshops: Portugal/IFICI (11:00, Diogo Pedro, Joana M.), Italy (12:00, Luca Calabrese), Portugal Real Estate (14:00, Gonçalo Peixoto), Beyond Sanctions (15:00, Joe Rice), Greece (16:00, Thanos Tsoukalas).
- **Day Two · 6 Nov — Global Wealth & the International Family.** Registration from 08:30; Day Two Welcome 09:15 (Mehdi Kadiri); Where Is Capital Going? 09:30 (Pedro Lino); Family Wealth & Succession 10:15 (Bernardo Meyrelles + TBA); The Global Wealth Playbook: Tax & Jurisdiction 11:00 (Albert Morgenstern, Dr. Laura Madrid moderator); Are You Really Ready for a 100-Year Life? 11:10 (Dr. Nina Patrick); Longevity Is the New Luxury 11:30 (Cintia Mano, Dr. Nina Patrick, Dr. Joana Costa); Building a Global Plan B, C and D 11:50 (João Pacheco Gonçalves, Joe Rice, Dr. Laura Madrid, Mehdi Kadiri); The Regulatory Horizon 14:00 (Bruno L'ecuyer, Joana M. moderator); Beyond the Golden Visa: Integration and Contribution 14:30 (Ruth Shaber, Sheree M. Mitchell); Raising Global Children 15:25 (Nathalie Willis-Davis, Diane Bidna, Gizane Campos moderator); Beyond Equities and Property 16:00 (Marc Jancou, Adrien Bridge); Closing Remarks 16:40 (Mehdi Kadiri); Wine Tasting & Farewell Networking 16:50–17:30. Workshops: US taxes for Americans abroad (11:00, Albert Morgenstern), Spain (12:00, Yanimar Hernandez), Caribbean (14:00, Joe Rice), Panama (15:00, TBA), Malta (16:00, Ayoub Rebroub).
- **Speaker↔session pairings are now published.** `agenda.html` (generated from `programme/build.py`) lists every session with its speakers, roles and moderators. The homepage (`index.html`) does **not** pair speakers with sessions. A post may use speaker↔session pairings from `agenda.html` / `data/programme.json` — they are now the same source of truth.
- **Thematic tracks** (from `agenda-tracks.html` and the `data-themes` attributes on `index.html`): four tracks — **Wealth & Investment**, **International Residency**, **Citizenship Planning**, **Family & Future**. Each session carries one or more themes. Shared opening/closing activities have no theme. A post may classify sessions by theme; the theme assignments come from `data/programme.json`.
- **Rules**
  1. A session title goes on a slide verbatim from `programme.json` (`full`, or `title` alone when it is the lead-in). Check with `facts.find_session("…")`.
  2. A time goes on a slide only if it is in `facts.known_times()`. Don't compute, round or infer end times — the site publishes start times; `agenda.html` also has end times from `build.py`.
  3. Speaker↔session pairings from `agenda.html` / `data/programme.json` may be used. The pairings are generated from `programme/build.py`.
  4. A post that names sessions carries "Programme subject to change" in the caption (the agenda page says it).
  5. Count only what is unambiguous: **2 days · 10 workshops · 28 speakers**. Don't state a "session" count — the main-stage rows include coffee, lunch and registration, and nothing on the site defines "session".
- **Workshop countries.** The intro sentence on the site names *Italy, Spain, Portugal, Greece, the Caribbean, Panama, and Turkey*; the timed list has **Malta** and **no Turkey**. For a workshop post use the timed list; do not mention Turkey or leave out Malta without telling the user.

## Speakers

28, in the site's order (`python3 scripts/facts.py speakers`). Name, role and bio come from `data/speakers.json` (the site's own cards); portraits from `assets/speakers/<slug>.webp` — all 28 bundled. A person not in the roster is not named, drawn or implied.

**Agenda-only names** (appear in `agenda.html` as session participants but have no speaker card on the site): Maggie Williams, Grazi Fulchiron, Sheree M. Mitchell, Adrien Bridge, Dr. Joana Costa, Diogo Pedro, Joana M., Gonçalo Peixoto, Lourenço Alvares, Gizane Campos. These are **not** in the speaker roster — they have no card, no portrait, no bio. A post may name them as session participants (from `programme.json`) but must not present them as "speakers" with a portrait.

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
| Athanassios (Thanos) Tsoukalas | Card: "Legal Manager, Greece at AT Legal"; agenda: "Legal Manager, Greece at Global Citizen Solutions" | Card |

**New speakers since 20 Oct 2026:**
- **Francisca van Dijken** — EMEA Head of Global Client Solutions at Citigroup Private Bank. Portrait: `francisca-van-dijken.webp`
- **José Carlos Reis** — Executive Director & Senior Investment Adviser at Julius Baer. Portrait: `jose-carlos-reis.jpg`
- **John McNertney** — CEO at Green Ocean Global Advisors. Portrait: `john-mcnertney.jpg`

Bios are long and copied verbatim from the site; a speaker card carries name, role and portrait, no bio — a spotlight caption may quote ≤ 40 words of it, whole sentences only.

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

## Partner booking pages

Five partner-specific booking pages exist, each with its own discount or form. These are `noindex` — they are shared privately via partner channels, not from the public site.

| Page | Partner | Discount | Promo code | Form |
|---|---|---|---|---|
| `/americanclub` | The American Club of Lisbon | 50% | `AMERICANCLUBWEALTH50` | Main HubSpot form |
| `/gfpi` | Global Financial Planning Institute (GFPI) | 50% | *(applied via dedicated form)* | GFPI-specific HubSpot form |
| `/redbridge` | RedBridge | 50% | *(applied via dedicated form)* | RedBridge-specific HubSpot form |
| `/trustedadvisor` | Trusted Advisor | 50% | *(applied via dedicated form)* | Trusted Advisor-specific HubSpot form |
| `/imglobalwealth` | IMGlobalWealth | 25% | `WMSIMGLOBALWEALTH25` | Main HubSpot form |

**Rule:** partner booking pages and their promo codes are private distribution channels. A social post must **not** publish a promo code or a partner page URL unless the user explicitly clears it for that post.

## Partners and media

- The hero shows two marks next to the title: **Global Citizen Solutions** and **CNN Portugal**.
- The partner strip under "Interested in partnering with the Summit?" shows ten logos: Goldcrest Portugal Real Estate, Optimize Investment Partners, CapitalPartners (a member of Gaw Capital), Blue Crow, Lisboa 2030, Portuguese Chamber of Commerce, CNN Portugal, Atlântico Europa, João M. Barbosa, Cascais Ventures. **The site does not say what each one is** (sponsor, partner, media, venue-side). The skill does not say either.
- Five additional partners have their own booking pages (see "Partner booking pages" above): The American Club of Lisbon, GFPI, RedBridge, Trusted Advisor, IMGlobalWealth. Their logos are in `assets/img/` (`americanclub-logo.png`, `gfpi-logo.png`, `redbridge-logo.svg`, `trustedadvisor-logo.png`, `imglobalwealth-logo.png`).
- **Rule:** no partner or sponsor logo on a social creative unless the user names it for this post and confirms it is cleared for social use. **Exception (user instruction, 20 Oct 2026):** the two marks the hero shows beside the title — Global Citizen Solutions and CNN Portugal — close the cover and the final slide by default. Nothing is written above, beside or over the GCS mark. No tiers, no "official partner of…" wording, no thank-you posts that imply a role. Logos live in `assets/img/` (`summit_assets` keys `partner.*`); several speakers' companies appear there too (Optimize, Blue Crow, Cascais Ventures) — a speaker card is not a partnership statement.
- **Partner enquiries:** the site now opens a form ("Explore partnership"); it does not print an address. `events@globalcitizensolutions.com` is in `PRODUCT.md` and the copy deck. Use it only after the user confirms it is still the route; otherwise "Link in bio".

## Spelling and verbatim copy

- Authored copy: **British English** (programme, organised, colour).
- The live site itself mixes in US forms ("organized", "specializing" in a bio) and spells the venue both **"EPIC SANA Marques Hotel"** (hero, venue section) and **"EPIC SANA Marquês"** (what's-included, booking page, agenda).
- Mode B (verbatim) keeps the source's spelling. Mode A writes British. For the venue, default to the hero's **"EPIC SANA Marques Hotel"** and tell the user the site uses both — it is a client call, not ours.

## Still absent — must not be fabricated

Delegate or client testimonials · past-edition figures (attendance, countries, sessions) · GCS-owned photography of Lisbon or the venue (the site's imagery is generated and on the client's replacement list; the venue photo on the site is not evidence for a claim) · sponsor tiers or sponsor roles · session end times on `index.html` (though `agenda.html` now has them from `build.py`) · who "Maggie Williams", "Grazi Fulchiron" and the other agenda-only names are beyond their session participation · any statement about attendance numbers so far.

## Sources — now aligned

As of commit `6725cff`, `index.html` and `agenda.html` are generated from the same `programme/build.py` source and agree on session titles, times and speakers. The earlier mismatch between the two pages (documented in the 20 Oct version of this file) has been resolved. `agenda-tracks.html` is a filtered view of the same data with thematic tags.

**Residual differences:**
- `index.html` does not show speaker↔session pairings; `agenda.html` does.
- `index.html` does not show session end times; `agenda.html` does.
- `agenda.html` uses "L'Ecuyer"; speaker card says "L'ecuyer". Use card spelling.
- The Day Two overlap (`10:55–11:10` coffee, `11:00–11:15` tax panel, `11:10–11:30` longevity) persists in the programme data and needs organiser confirmation.

## Keeping this current

```bash
python3 scripts/sync_site_facts.py check "/Volumes/GCS - DISK 1T/GCS 2026/Github/gcs-wealth-migration-summit"   # drift report, writes nothing
python3 scripts/sync_site_facts.py sync  "/Volumes/GCS - DISK 1T/GCS 2026/Github/gcs-wealth-migration-summit"   # refresh references/data/*.json
```

After a `sync`: re-read the tables above (they are hand-written), replace `references/PRODUCT.md` / `DESIGN.md` with the site's copies if `check` says they differ, update the "As of" line. The site repo is read-only for this purpose. Everything here expires after **6 Nov 2026**.
