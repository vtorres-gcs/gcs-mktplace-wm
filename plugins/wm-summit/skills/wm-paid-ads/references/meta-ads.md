# Meta Ads — formats, limits and how the Summit uses them

Facebook + Instagram (+ Messenger, Audience Network) are bought together in Ads Manager. Sizes and text lengths are in `specs.json`; Meta's figures are **guidance, not hard caps** — the UI accepts longer text and cuts it, so `ads.py lint` warns where Google's lint errors. Meta's own Ads Guide (Feed image ad) was read on 2026-10-21; the other placements come from 2026 third-party tables — check the live Ads Manager preview before a large build.

## Placements and the file each one needs

| Placement | Ratio · size | Notes |
|---|---|---|
| **Feed** (Facebook, Instagram) | 4:5 · **1440x1800** (Meta's recommendation; 1080 wide is the floor) | The default. Instagram's profile grid shows the middle 3:4, so side margins matter |
| **Feed / carousel card / right column / Marketplace** | 1:1 · 1080x1080 | Carousel cards are cropped to 1:1 whatever you upload (2–10 cards) — never a 4:5 card |
| **Stories + Reels** | 9:16 · 1080x1920 | **Safe zone: nothing in the top 14% or the bottom 35%.** Stories only needs 20% at the bottom; Reels needs 35%. One file at 35% serves both |
| **Link ad / Audience Network** | 1.91:1 · 1200x628 | Older landscape card; still used |

JPG or PNG, up to 30 MB. Video is out of scope (none exists for the Summit). `render` writes each size at exactly these pixels, and `check` verifies them.

## Text — what shows, what is cut

| Field | Shows | Use it for |
|---|---|---|
| **Primary text** | ~125 characters, then "See more" (Meta's guide suggests 50–150) | The first sentence carries the whole message; what follows is detail, a rate line, what is included |
| **Headline** | ~27 characters in the feed, up to ~40 on some placements | The click line: the event name, the dates, or one hard fact |
| **Description** | ~30 characters, often not shown on mobile | Nothing essential |

Give **2–3 primary texts and 2–3 headlines** that genuinely differ (a fact angle, a topic angle, a rate-and-date angle). Meta tests them against each other, so near-duplicates waste the test; the lint errors on exact duplicates.

**Call-to-action button** is Meta's own label, set in the UI, never drawn in the image. For cold audiences use **Learn more** (the site argues the programme first). For people who already visited the site use **Book now** (the booking page takes payment). The button label is a platform setting, so it is not the "Secure your place" line — that phrase belongs in the copy.

## Objective and structure — suggestions, not Summit facts

- A two-week flight will not collect the ~50 optimisation events per week Meta wants to leave "learning". For a €499–599 ticket, expect **Learning limited** if you optimise for Purchase. A Traffic (landing-page views) campaign plus a retargeting ad set aimed at site visitors is the realistic shape; the user decides.
- Budgets, bids, audiences and lookalikes are not on file and not set by this skill. The audience slices on the site (global individuals and families · legal and tax counsel · private banking · industry and government) are a messaging brief, not a targeting export.
- Name things so results can be read later: campaign `WMS26 | <objective> | <tier>`, ad set `<audience> | <placement>`, ad `<creative id> | <primary-text #>`.

## Tracking and what Meta can see

- The Meta Pixel loads only after the HubSpot banner reports **advertising** consent (`tags.js`). Expect fewer attributed events than Stripe shows. The pixel fires `PageView` on load and `Purchase` (value and currency) on `/thank-you`.
- Put the URL parameters printed in `_copy.md` into the ad's URL parameters field (`utm_source=meta&utm_medium=paid-social&…`).

## Policy — check before publishing

1. **Social issues, elections or politics.** Meta's list of social issues includes **immigration**, and ads Meta classifies that way need the advertiser to complete authorization and carry a "Paid for by" disclaimer — and, per Meta's policy page, such ads are **not allowed to run in the European Union** (verified 2026-10-21 on transparency.meta.com; read the live page). The Summit is a commercial event about wealth and mobility, not advocacy, but the event name contains *Migration* and programme titles say *Immigration Workshop*. So: write copy about global mobility, cross-border strategy, planning and the programme; keep *immigration*, *migrants*, *border*, *refugee*, *asylum* and any policy language out of the ad (the lint warns on them); if an ad is flagged anyway, appeal it as ticket sales for a conference; tell the user early, because authorization takes days.
2. **Personal attributes.** Meta bars ads that assert or imply a viewer's financial status, nationality, status and the like ("Are you wealthy?", "As a high-net-worth individual…"). Speak about roles in the third person — advisors, family offices, global families.
3. **Deceptive practices / unacceptable business practices.** No guaranteed outcomes, no offers that read as selling a visa, passport or citizenship. The Summit sells a conference place. The lint errors on both.
4. **Financial products.** Meta's financial-services policy can require licences when an ad promotes a financial product or service. The Summit is not one: no returns, yields, investment recommendations or "invest in…" calls to action.
5. **Landing page.** It must load without a password. The site's own `CLAUDE.md` says it sits behind HTTP Basic Auth until launch; a preflight on 2026-10-21 returned 200, and the gate can come back. Run `ads.py preflight <url>` on the day of upload.
6. **Image text.** Meta no longer enforces a 20% text rule, but less is better. The creatives carry one headline and one support line. There is no drawn button, no fake play icon, no fake notification — Meta rejects those.
7. **Identity.** The ad runs from a Facebook Page and an Instagram account; the user chooses which (Global Citizen Solutions or a Summit Page). The marks in the image are the same pair the site hero shows (GCS, CNN Portugal); no wording gives either a role.
