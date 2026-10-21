# Banner design — the site's system on a web banner

`DESIGN.md` describes the site's navy night page, and the banners follow it: **blue first**. A banner is a small surface carrying the same system — one navy ground, white type, gold as the single light. This file says how it scales down, and what `scripts/banner.py` does.

> History: the first version of this skill used a white ground on the user's request. On 2026-10-20 the user asked for the blue-first design "as on the site" and for the GCS and CNN logos on every banner; the white variant was removed. If white is wanted again it is a new decision, not a flag — the logo files, contrast table and palette lock all assume navy. House rule for any white ground (all Summit skills except `wm-letterhead`, which carries only the GCS Secondary Blue, by the user's decision): the pair is the **GCS Primary Blue** (`GCS-Primary-Blue.png`) and the **red CNN Portugal** (`Logo CNN PORTUGAL Float Final.png`), both shipped in the sibling `wm-social-media` skill's `assets/logos/` — never the white marks.

## The system on a banner

| `DESIGN.md` | On a banner |
|---|---|
| One navy ground, unbroken (`#121B31`) | The whole banner is navy; a 1px hairline (`--rule`, mist at 16%) marks the edge so it reads as a banner on any page |
| Sharp White headlines, Dawn Mist secondary text | Headline white; the date / sub line in mist `#C8CCD7` (10:1 on navy) |
| Gold is the page's only warm light | **One lit thing:** the button — gold ground, navy label, square. Plus the 32×2px gold rule that draws under the headline, and the gold inside the W&M symbol. Never gold body text |
| Caladea for headings, Archivo for reading and labels | Same: Caladea 400 headline, sentence case; Archivo 500 uppercase 0.16em for the date; button label 0.1em |
| No boxes, chips, glass; square corners | Same. No shadows either (the site's lamp-glow under the button costs GIF bytes and clips at a banner's edge) |
| Motion on `transform` and `opacity` only | Same |
| Nothing below 12px | Same — the checker errors under it |

The 44px minimum for interactive elements does **not** apply to the drawn button: a banner is an image whose whole area is the click target. The button is a signpost, kept at least 30px high.

## The three marks — always

Every banner carries, with no switch to turn them off:

1. **Wealth & Migration Summit** — the lockup (`w&m-*-white.svg`, white type + gold symbol). Left on every layout except 320x50-class banners.
2. **Global Citizen Solutions** — symbol + wordmark side by side, white (`hero-gcs-symbol.svg` + `hero-gcs-text.svg`).
3. **CNN Portugal** — white (`cnn-portugal-white.png`, from the client's own "Float BRANCO" file).

(2) and (3) are the pair the site's hero shows beside the title, at the same height as each other (64px on the site, 92x64 for CNN). On a banner they are set in one group, equal height, with a gap of 0.6× their height. Below 80px tall the GCS mark drops to the symbol alone; the wordmark is too small to read there. Neither mark is ever recoloured, and no wording gives either a role.

## Layouts

`banner.py` picks one from the aspect ratio (`layout_for`). The group of marks sits where the layout has room:

| Layout | When | Arrangement |
|---|---|---|
| **row** | width ÷ height ≥ 2.6 — 728x90, 970x90, 900x200, 970x250, 468x60, 320x50, 320x100 | Summit lockup · copy (vertically centred, left-aligned) · GCS + CNN (stacked from 80px tall, side by side below) · button |
| **box** | 0.75 ≤ ratio < 2.6 — 300x250, 336x280, 250x250, 1080x1080, 1200x627 | header: Summit lockup left, GCS + CNN right · copy centred in the space between · button bottom (full width at ≤ 420px wide). From a ratio of 1.5 the copy is held to 72% of the width |
| **tall** | ratio < 0.75 — 160x600, 300x600, 120x600 | Summit lockup (full width) · copy · button (full width, label may wrap) · GCS + CNN row at the foot |

Row Summit lockups: the stacked "default" lockup at 62% of the height for 60–120px banners, the symbol alone under 60px, 36% of the height above. Box and tall banners use the "vertical" lockup. `"logo"` overrides it (`horizontal | vertical | default | symbol`). `build` notes anything dropped (the lockup on 320x50, the sub line under 80px tall) or small (marks under 18px high).

## Type

- **Headline:** Caladea 400, line-height 1.06, `text-wrap: balance`. The fit loop starts at a layout-specific maximum (row: 30% of the height, capped 64px; box: 10% of the shorter side, capped 88px; tall: 17% of the width, capped 64px) and steps down by half a pixel until no scene overflows its box, then applies the **smallest** size to every scene so a sequence does not jump.
- **Date / sub line:** Archivo 500, 0.16em tracking, uppercase, 12–22px by size.
- **Button label:** Archivo 500, 0.1em tracking, uppercase, 12–22px.
- **Floor:** 12px for everything. If the headline cannot fit at 12px the checker errors — the fix is copy, not type.

## Motion (GIF, and the HTML preview)

One authored sequence per scene, in this order and no other: **headline** rises 8px while fading in (0.55s) → the **gold rule** draws left to right (0.5s) → the **date line** fades in (0.5s) → on the last scene the **button** fades in (0.5s). Between scenes the old one fades out over 0.4s as the next begins. Easing `cubic-bezier(.2,.7,.2,1)`. The first frame is the logo alone; the final state holds (default 3s) and the GIF stops there after its last play.

Why so little: a banner is seen for two seconds in the corner of the eye. Movement that is not the message is noise, and every extra moving pixel is file size.

## GIF size — how the encoder lands under the limit

Dimensions are never traded. In order:

1. Capture at 20 fps by seeking the page's own animations to each instant (deterministic — no timing jitter).
2. **Merge identical frames**: the marks-only start, every hold and the final hold collapse to single frames with long delays — they cost nothing. Most of the file is the ~1.2 seconds of movement per scene.
3. One **shared palette** for all frames (median cut over a montage of the distinct frames), no dithering — flat colour and type do not need it, and it keeps text edges clean. Three entries are **locked** to the brand's exact navy `#121B31`, white `#FFFFFF` and gold `#C2A358`, and pixels that are exactly those colours are pinned to them: plain median cut turns the navy ground into `#10182D` and white into `#FCFCFC`, which a brand banner must not do. `render` reads the finished GIF back and warns if the ground is not exact navy.
4. Try, in order: 256 → 128 → 64 → 32 colours at full frame rate; then 64 / 32 / 16 colours at half rate; then a third, a quarter. Stop at the first file under the limit.

Typical results: a 300x250 two-scene banner ~110–140 KB at 32–64 colours / 20 fps, ~30 KB at 16 colours / 5 fps. Flat grounds compress far better than photographic banners, but a navy ground costs more than white did (a 900x200 two-scene GIF lands near 147 KB at 32 colours) — against a 150 KB ceiling, prefer one scene or a shorter hold.

Loop count: `--plays 3` writes the GIF's repeat field as 2 (the field counts repeats after the first play). `--plays 0` loops forever; `--plays 1` plays once. Duration is reported per play.

The static companion (`_static.png`) exists because Outlook desktop and some ad placements show only the first frame, and this banner's first frame shows the three marks and no message.

## Copy length by size

Measured at the 12px floor, with the usual headline "Your residency, your citizenship, your Plan B." (46 characters):

| Size | Fits? |
|---|---|
| 300x250, 970x250, 1080x1080, 1200x627, 300x600, 160x600 | yes, with room |
| 728x90 | yes — two to three lines at ~20px between the Summit lockup and the marks + button |
| 320x50 | only with two to four words ("Your Plan B."): the GCS + CNN marks and the button leave ~75px for text; the Summit lockup is left out, so name the event in the headline |

## Accessibility

- Contrast: white on navy 17:1; mist on navy 10:1; navy on the gold button 7:1. The checker computes every text element and fails under 4.5:1 (3:1 at 24px and above).
- Every banner ships **alt text** in the hand-off — the image itself carries the words, so a placement without alt text is unreadable to a screen reader.
- GIF: nothing flashes (no frame-to-frame luminance jumps beyond the fades); it plays at most 3 times by default and rests on the final frame, which is also the static fallback.
- `prefers-reduced-motion` in the HTML preview: only the last scene is shown, no animation.
