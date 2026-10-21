# Ad copy playbook — what an ad may say, and a bank to start from

Everything below is built from `FACTS.md` and `references/data/`. `ads.py lint` rejects anything that isn't. The programme is the argument: a fact beats an adjective, and a fact that is specific ("Limited to 200 attendees", "Ten workshops") beats a claim about quality.

## What an ad may state

| Fact | Say it as | Source |
|---|---|---|
| Name | Wealth & Migration Summit 2026 (text assets use "&"; the lockup says "and") | site |
| Dates, place | 5–6 November 2026 · Lisbon; venue **EPIC SANA Marques Hotel** (the site also writes *Marquês* — one spelling per pack, and tell the user) | `FACTS.md` |
| Format | Two days · ten workshops · 26 speakers · limited to 200 attendees | `FACTS.md` |
| Day themes | Day One *The New Geography of Wealth & Mobility* · Day Two *Global Wealth & the International Family* | `programme.json` |
| Included | Both days of sessions and workshops · networking lunch on both days · cocktail reception on the evening of Day Two | `rates.json` |
| Sessions | A title verbatim from `programme.json` — never a time that isn't there, never an end time | `facts` |
| Rate | Only the tier in force for the **whole flight**, with its end date (below) | `rates.json` |
| Call to action | "Secure your place" in the copy; the platform button is set in the UI | site |

**Never in an ad:** a speaker paired with a session (the site's two programme pages disagree; the user must confirm each pairing) or anyone outside the 26-speaker roster — portraits and names come only from `assets/speakers/`; a partner or sponsor logo other than the GCS + CNN Portugal pair unless the user names it for that ad; past-edition figures or "returns"; testimonials; urgency ("last chance", "only 10 seats", "book now"); a day count ("12 days to go"); a price that isn't a published tier; anything that reads as selling a visa, passport or citizenship; the sanctions / restricted-nationals workshop; "immigration" wording on Meta; a second-person claim about the viewer's wealth.

## Not in `FACTS.md` yet (site repo read 2026-10-21, after the commit `FACTS.md` was built from)

- **Partner landing pages** — `/gfpi`, `/redbridge`, `/trustedadvisor`, `/imglobalwealth` (all `noindex`): same programme, partner-only prices (e.g. €249, €374 against the €499 Advance Rate) and promo codes. A partner channel is not a public offer: never show those prices or codes in a public ad, and send public traffic to `/` or `/claim-your-seat`.
- **`/claim-your-seat` shows the Advance Rate as "NOW" in static HTML.** An ad that says €599 and lands there on 31 Oct disagrees with its page until someone edits it. `ads.py preflight --pack` warns; the user's web team switches the page on the day.
- **The hero line** *Your residency, your citizenship, your Plan B.* is second person but asserts nothing about the viewer's status, and it is the site's own headline, so it stays verbatim. If Meta flags it as a personal attribute, fall back to *Global Plan B, C and D* or *Global mobility, in one room*.

## The rate calendar decides which ads exist

| Tier | Price | Window | An ad that shows this price must end |
|---|---|---|---|
| Early bird | €399 | 1 Sep – 3 Oct | 3 Oct |
| Advance Rate | €499 | 4 Oct – 30 Oct | 30 Oct |
| Final Rate | €599 | 31 Oct – 4 Nov | 4 Nov |

- Nothing is published for 5–6 Nov, and every ad ends before the Summit opens (5 Nov, 09:00 Lisbon).
- A flight that crosses a boundary needs **two ad versions** (or no price). `lint` errors on a price that is wrong on any day of the flight. Say the date, never the pressure: "Advance Rate €499 until 30 October" is a fact; "Price rises soon" is not on file.
- A price line belongs to the warm funnel (people who have seen the programme). Cold ads lead with the programme and the cap.

## Angles by audience

The site names four rooms: global individuals and families · legal and tax counsel · private banking · industry and government. Its lede adds advisors and family offices. Pick **one** slice per ad group or ad set; "everyone" is not an audience.

| Slice | The thing they weigh | Copy that stays in the facts |
|---|---|---|
| **Global families** | A Plan B that holds up, tax and banking included | "Your residency, your citizenship, your Plan B." · "Global Plan B, C and D" (session: *Building a Global Plan B, C and D: Contingency Planning for Global Families*) · "Growing Up Global" (session title) |
| **Legal and tax counsel** | Country-specific detail from specialists | "Ten workshops: Portugal, Italy, Greece, Spain, Malta, the Caribbean, Panama" (the timed list; the site's intro sentence also says Turkey but no Turkey workshop is timed — flag it) · "Plan Smart: Combining Residency and Tax Benefits in Portugal" (workshop title) |
| **Private banking and wealth managers** | How international families structure and move capital | *Inside the Private Bank: How International Families Structure Their Wealth* · *Asset Location vs. Asset Allocation* · *Money Without Borders: Diversification and Wealth Management for the Global Citizen in 2026* |
| **Family offices, industry, government** | Who is in the room, and how many | "Limited to 200 attendees" · "Global mobility, in one room" · "26 speakers" (count only — no names) |

## Copy bank — lint-clean, to adapt

**Google RSA headlines (≤ 30)** — Wealth & Migration Summit · Lisbon · 5–6 November 2026 · Two days in Lisbon · Ten workshops, 26 speakers · Limited to 200 attendees · Your residency, your Plan B · Global mobility, in one room · For advisors, family offices · Global Plan B, C and D · Secure your place · EPIC SANA Marques Hotel · *(Final Rate)* Final Rate €599 to 4 Nov · *(Advance)* Advance Rate €499 to 30 Oct

**Google descriptions (≤ 90)** — Two days of main-stage sessions and specialist workshops on global mobility. · Residency and citizenship planning as part of a broader wealth strategy. · Lisbon, 5–6 November 2026. Limited to 200 attendees. · Advance Rate €499 until 30 October. Both days, networking lunches, cocktail reception.

**Meta primary text (first ~125 characters carry it)**
- *Programme:* Residency and citizenship planning is part of a wider wealth strategy. Two days in Lisbon, 5–6 November 2026.
- *Room:* Plan B, C and D, tax, banking and mobility, in one room for two days. Limited to 200 attendees.
- *Rate (warm):* Advance Rate €499 until 30 October. Two days, ten workshops, 26 speakers. Secure your place.

**Meta headlines (≤ 27)** — Wealth & Migration Summit · Lisbon · 5–6 November · Limited to 200 attendees

**On the graphic** (sentence case, words for numbers): *Your residency, your citizenship, your Plan B.* + support *Don't let the world decide for you.* · *Two days. Ten workshops. Twenty-six speakers.* + support *Limited to 200 attendees* · *Global mobility, in one room.* + the service line.

## Voice

Restrained, factual, institutional. British spelling in authored copy (*programme*, *organised*). No emoji, no exclamation marks, no superlatives, no hype; sentence case; capitals only for the acronyms the site uses (IFICI, CNN). Never *relocation firm*, *passport shop*, *borderless living*, *dream lifestyle*, *fallback option*; say *citizenship programme* / *residency programme*, never *passport programme*. English by default; Portuguese or Spanish only on request, with a line that the translation is not client-approved copy (the limits count the same; accents are one character).

## Naming and tracking

- Pack `name` → file prefix: `wms26-<angle>-<tier>` (e.g. `wms26-plan-b-advance`).
- UTMs: `utm_source` google | meta · `utm_medium` cpc | paid-social · `utm_campaign` = the pack's campaign slug · `utm_content` = creative id or ad group. `ads.py export` prints both strings.
- One landing page per audience temperature: home for cold, `/claim-your-seat` for warm. Confirm the URL and whether the staging gate is lifted before printing it anywhere.
