# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/JS, no build step (user's answer). Single page at `index.html` with `assets/css`, `assets/js`, `assets/img`. Must stay portable to WordPress/Elementor later, so no framework and no runtime dependency beyond Google Fonts.

## Users

Primary: high-net-worth individuals and families evaluating where to live, invest and hold residency or citizenship across borders. Alongside them, the professionals who advise or transact with them — family offices, legal and tax counsel, private banking, fund managers, industry players, and international specialists (the seven segments named in the approved copy).

Situation: they are considering an international residency or citizenship strategy and are currently assembling that decision from fragmented, one-specialist-at-a-time advice. On this page the job is narrower: decide whether this Summit is worth two days of their time, and register interest.

Secondary audience: prospective partners and sponsors, who need a route to `events@globalcitizensolutions.com`.

## Product Purpose

The Wealth and Migration Summit 2026 — a private two-day gathering in Lisbon, Portugal, 5–6 November 2026, at EPIC SANA Marques Hotel, convened by Global Citizen Solutions and chaired by Patricia Casaburi (Founder & CEO). Attendance is intentionally limited to approximately 150–200 curated delegates, by registration.

The page exists to make the Summit intelligible and desirable to a qualified stranger and to capture registrations of interest, which the GCS team then follows up to confirm a place and share the full programme. Success = a qualified visitor understands what it is, why it matters now, and submits the register-interest form.

## Positioning

Residency and citizenship planning is treated here as part of a broader wealth strategy rather than an isolated legal decision. The mechanism a neighbouring event could not truthfully copy: the specialisms that a cross-border decision normally requires one at a time — investment selection, legal structuring, tax planning, banking relationships, long-term mobility — are put in one room, in a fixed sequence, over two days. The two-day programme itself is the proof; it is the only asset on the page that is specific rather than assertable.

## Operating Context

Two days, split by theme. Day One (5 Nov) — "The Golden Visa Pathway": EU golden visa state of play, qualifying funds and due diligence, wealth management for foreigners, cultural donation projects, the Portugal/Italy/Greece/Malta landscape, IFICI tax planning, the path to citizenship, masterclass breakout rooms, private networking dinner. Day Two (6 Nov) — "Structuring, Context & Experience": global residence and citizenship comparatives, family office and multi-generational planning, healthcare and longevity, banking/AML/cross-border capital, moving money and forex timing, living in Portugal as a foreign resident, integration and lifestyle, parallel breakout discussions, closing remarks, closing reception.

Lisbon is framed as a European capital with a global outlook — from Web Summit to major international business, cultural and sporting events — and therefore a fitting setting for a Summit about the movement of people, capital and opportunity.

## Capabilities and Constraints

- **Hero copy follows the Figma hero (node 14398:6051)**: the lede, "Two days • 5 and 6 Nov" and "EPIC SANA Marques Hotel - Lisbon" come from the design, not the original copy deck; the rest of the page still follows the deck.
- **Copy is locked and final.** Every visible string comes verbatim from `content/Wealth and Migration Summit Landing page copy.docx`. No rewriting, reordering into new prose, correcting, or adding claims.
- Sections, in the copy's own order: nav, hero, 01 why this matters / who's in the room, 02 the programme, 03 speakers, 04 the setting, 05 register, 06 partner with the Summit, footer, bottom bar.
- Registration form fields: full name, work email, company / family office, "I am registering as". **No form endpoint exists yet** — undecided; must not be faked.
- Full session timings beyond the published programme are not confirmed. Never invent sponsor logos, prices, or delegate names.
- **Speaker line-up is confirmed** (14 named speakers, supplied by the client as `content/speaker.docx`): name, role and bio for each, shown in a gallery section after the programme, opening a modal with the full bio on click. Headshots live in `assets/img/speakers/` (optimised WebP, generated from the client-supplied originals in `assets/img/`); one speaker (Duarte Calheiros Menezes) has no supplied photo and shows an initials placeholder instead. Never invent a speaker not in that source list.
- Partner enquiries go to `events@globalcitizensolutions.com`.
- Open client editorial question, not ours to resolve: a comment in the source document asks whether the Day One Golden Visa session should split into a European residency landscape session plus a Portugal-specific one. Ships as written until GCS decides.

## Brand Commitments

- Name and lockup: "Wealth & Migration Summit" in navigation; "Wealth and Migration Summit 2026" as the page title. Convened by Global Citizen Solutions; GCS descriptor and stats appear in the footer.
- **Pinned palette (binding):** primary `#121B31`, secondary `#C2A358`, support `#FFFFFF` and `#C8CCD7`.
- Visual reference supplied at `references/c97b78d0bd8b9dbfc21ef57bb80ef115.webp` is binding as a **craft/finish bar only** — the user explicitly ruled out its layout and its lime palette.
- Voice: restrained, factual, institutional. British spelling in the source copy ("organised", "programme") is preserved.

## Evidence on Hand

- Approved copy deck: `content/Wealth and Migration Summit Landing page copy.docx` (single source of truth for all strings).
- Craft-bar reference: `references/c97b78d0bd8b9dbfc21ef57bb80ef115.webp`.
- Speaker roster: `content/speaker.docx` (client-supplied), 14 named speakers with role and bio, in the order they must appear; headshots supplied alongside it in `assets/img/`.
- Real facts available: dates, city, venue name, convener, chair, delegate cap, two-day session list, confirmed speaker roster, GCS footer stats (10+ years advising international clients, 100+ professionals across legal, immigration and advisory teams, global network spanning multiple jurisdictions).
- **Absent, must not be fabricated:** photography of Lisbon or EPIC SANA Marques owned by GCS, sponsor or partner logos, delegate testimonials, ticket pricing, past-edition figures. Page imagery is generated (Freepik/Magnific MCP) and is on the client's replacement list.

## Product Principles

1. The programme is the argument. Specificity of the two-day agenda outranks any adjective about exclusivity.
2. Scarcity is factual, not theatrical: ~150–200 curated delegates, by registration. State it; never dress it as urgency mechanics.
3. Registration is an expression of interest followed by a human conversation, not a checkout. The form must read as the start of a vetted process.
4. Nothing on the page may outrun what is confirmed. Unpublished detail is disclosed as unpublished.
5. This is a Global Citizen Solutions surface: institutional trust is the baseline the design must not spend.

## Accessibility & Inclusion

International audience, mixed devices, older HNW readers likely. WCAG 2.1 AA contrast is required on every text/ground pair — note that `#C2A358` on white fails AA for body text, so gold is used on dark ground, as rule, or as mark, never as small text on white. Full keyboard operability of nav and form; `prefers-reduced-motion` honoured.
