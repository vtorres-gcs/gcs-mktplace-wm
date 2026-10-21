# Creative design — the site's system on an ad image

`DESIGN.md` is the Summit's system ("Lisbon Nocturne": one navy ground, gold as the one light, Caladea over Archivo, square corners, no simulated surfaces). `scripts/ads.py render` applies it to ad canvases. This file says what that means and where it deliberately differs from the web banners and the organic social skill.

## What every ad image is

- **Navy `#121B31`** ground, edge to edge: flat by default, or a photograph from `assets/imagery/` under a layered navy scrim (`"photo"` in the creative; the `plate-*-dark` files are already graded dark). No gradient "texture" standing in for a picture, and no new generated image. The user confirmed on 2026-10-21 that the images are licensed stock with paid-use rights, not AI; the hand-off repeats that it is their statement.
- **Type:** the headline in Caladea 400, white, sentence case, the biggest thing on the canvas (96–112px on a 1080 canvas, fitted down to a floor of 60px; 68px → 38px on 1200x628). The service line `5–6 NOVEMBER 2026 · LISBON` in Archivo 500, uppercase, 0.16em, **gold** — gold is text only on navy and it is the one warm light. An optional support line in Archivo 400, mist `#C8CCD7`.
- **Marks (Meta formats):** the Summit lockup top-left; the Global Citizen Solutions mark and CNN Portugal (white, equal height, gap 0.6× height) at the foot — the pair the site hero shows beside the title. Nothing is written above, beside or over the GCS mark; no wording gives either a role. `"marks": "summit-only"` drops the pair.
- **Plates (Google formats):** Google's responsive-image guidance says not to overlay logos or repeat the text assets on a picture. Google formats therefore render the gold service line and the headline only — no lockup, no marks, no support line — and the logo goes in the separate logo asset. `"style": "full"` on a creative puts the Meta treatment on a Google format; `"style": "plate"` the other way.
- **No button, no "Learn more" chip, no play icon.** Both platforms draw their own call to action; a drawn one is a fake control (a policy problem on both) and also steals the one-light rule. Uploaded IAB banners are different — they are one clickable image — and belong to `wm-web-banners`.
- **Words:** one headline (≤ 12 words) and at most one support line. If it does not fit at the floor, `render` errors; shorten the copy, do not shrink the type.

## Formats and safe zones

| Format | Canvas | Margins | Why |
|---|---|---|---|
| Meta feed 4:5 | design 1080x1350, output 1440x1800 | 7.5% | Instagram's profile grid shows the middle 3:4 |
| Square 1:1 (Meta and Google) | 1080x1080 / 1200x1200 | 7.5% | carousel cards are cropped to 1:1 |
| Stories + Reels 9:16 (and Google vertical) | 1080x1920 | **top 14%, bottom 35%**, 7.5% sides | profile bar on top; Reels caption and buttons below (Stories needs only 20%) |
| Landscape 1.91:1 (Meta link, Google) | 1200x628 | 8% top/bottom, 6% sides | Google crops for some placements |
| Google portrait 4:5 | 960x1200 | 7.5% | PMax, Demand Gen |
| Google logo 1:1 / 4:1 | 1200x1200 / 1200x300 | — | the stacked lockup on solid navy; Google advises against mostly-white logos on a transparent ground |

`render` measures the copy block, the lockup and the marks against the safe rectangle after fitting and errors if any leaves it. The headline is placed in the lower part of the safe area on tall canvases (the foot-block of the site's hero) and centred on square and landscape ones.

## Sentences

A full stop after a lowercase word ends a line: *Two days. / Ten workshops. / Twenty-six speakers.* sits one sentence per line, and each line is unbreakable — the fit loop shrinks the type until every line fits, and errors at the floor. Put `\n` in a headline to force a break anywhere else. A hyphenated word never splits. A different headline for one format: `"by_format": {"meta_story_9x16": {"headline": "…"}}`.

## Extending

A new layout is a change to `layout_params()` and `PAGE` in `ads.py` plus an entry in `specs.json`; keep the rules above (tokens, floors, safe zones) and add a test pack. Do not hand-edit the rendered HTML — rebuild from the pack JSON so the result is reproducible.

## Photography

No new image is generated. The pictures in `assets/imagery/` (cleared by the user) go in a creative with `"photo"`: Meta formats get the scrim and the text; Google formats get a clean crop. Any other picture the user supplies is cropped with `ads.py photo` to each format's pixels and left clean — the words come from the text assets. The command warns when a source needs an upscale above x1.15 (soft images are flagged by Google). Never caption a stock picture as the venue or as a real event of this Summit.

## Assumption to confirm with the user

The decision to carry **GCS + CNN Portugal** on every banner was made on 2026-10-20 for web banners (and the hero pair on organic covers). It was not stated for paid Meta and Google ads. This skill applies it by default; the hand-off says so, and `"marks": "summit-only"` is the way out if a paid placement should not carry the CNN mark.
