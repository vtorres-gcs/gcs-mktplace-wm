---
name: Wealth and Migration Summit 2026
description: A navy night city where amber light marks the hours that matter.
colors:
  navy: "#121B31"
  navy-deep: "#0A101F"
  navy-wash: "#12192D"
  dawn-blue: "#232F52"
  gold: "#C2A358"
  gold-bright: "#DCC08B"
  dawn-low: "#1B2643"
  mist: "#C8CCD7"
  white: "#FFFFFF"
typography:
  display:
    fontFamily: "Caladea, Georgia, Times New Roman, serif"
    fontSize: "clamp(2.9rem, 7.6vw, 6rem)"
    fontWeight: 400
    lineHeight: 0.9
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Caladea, Georgia, Times New Roman, serif"
    fontSize: "clamp(2rem, 4.4vw, 3.4rem)"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Caladea, Georgia, Times New Roman, serif"
    fontSize: "clamp(1.6rem, 2.6vw, 2.25rem)"
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: "-0.005em"
  subtitle:
    fontFamily: "Caladea, Georgia, Times New Roman, serif"
    fontSize: "clamp(1.5rem, 1.8vw, 1.75rem)"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "0.005em"
  lead:
    fontFamily: "Archivo, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.62
    letterSpacing: "0.005em"
  body:
    fontFamily: "Archivo, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "0.005em"
  label:
    fontFamily: "Archivo, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "0.16em"
  label-sm:
    fontFamily: "Archivo, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "0.16em"
  session:
    fontFamily: "Caladea, Georgia, Times New Roman, serif"
    fontSize: "1.3rem"
    fontWeight: 400
    lineHeight: 1.22
    letterSpacing: "0"
  datum:
    fontFamily: "Archivo, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: "0.02em"
    fontFeature: "tnum 1"
rounded:
  none: "0"
  dot: "50%"
  tile: "5px"
spacing:
  s1: "0.5rem"
  s2: "1rem"
  s3: "1.5rem"
  s4: "2rem"
  s5: "3rem"
  s6: "4.5rem"
  s7: "7rem"
  s8: "10rem"
components:
  button-lit:
    backgroundColor: "{colors.gold}"
    textColor: "{colors.navy}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.95rem 1.5rem"
  button-lit-hover:
    backgroundColor: "{colors.gold-bright}"
    textColor: "{colors.navy}"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.mist}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.95rem 1.5rem"
  button-quiet-hover:
    textColor: "{colors.white}"
  button-on-light:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0.95rem 1.5rem"
  panel-lit:
    backgroundColor: "{colors.white}"
    textColor: "{colors.navy}"
    rounded: "{rounded.none}"
    padding: "clamp(2.25rem, 4.5vw, 4rem)"
  station-dot:
    backgroundColor: "{colors.navy-deep}"
    rounded: "{rounded.dot}"
    size: "0.5rem"
---

# Design System: Wealth and Migration Summit 2026

## Overview

**Creative North Star: "Lisbon Nocturne"**

The system is a night city, not a document. A single navy ground runs edge to edge from the first viewport to the last line of the footer, and the page's only warm light is amber — spent on the one thing worth looking at in each screen. Photography is the material: blue-hour river, wet street, still water. Nothing is bevelled, embossed, or given a fake surface; where the design needs texture it ships a real photograph and lets it sit dark.

The page reads as one continuous hour. It opens at the last minute of blue hour, deepens toward the middle where the two-day programme runs, and lifts to a first silver dawn behind the footer. That arc is a real gradient across the page's own paints, not a decoration: the programme sits at the darkest point because that is where attention should be, and the closing sections lighten because the visitor is on the way out.

Restraint is structural, not decorative. Structure comes from hairline rules, ruled columns, and a single amber line down the timed programme. The page's few boxes are accepted from the Figma redesign and each carries real content: the four countdown tiles (the only rounded boxes, 5px), the four audience entries under "Who's in the room", and the rates panel. The register section is the only white surface on the page, and it earns that by being the only thing the visitor is asked to do.

**Key Characteristics:**
- One navy ground, unbroken; sections differ by tone, not by container
- Amber is light, not colour: it marks the active thing and nothing else
- Real photographic material; no simulated surfaces or textures
- A quiet serif for every heading against a wide-aperture grotesk for reading
- Square corners throughout, except the countdown tiles; hairlines instead of boxes
- One authored motion — the amber programme line drawing itself in

## Colors

Four brand values, extended only by tonal steps of the same navy: the palette is a night, so its range is light level rather than hue.

### Primary
- **Transit Gold** (`{colors.gold}`): the page's only warm light. Reserved for the lit action, the service line, the day marker, the programme's line and its station dots, the footer's figures, and the input's focus. Never a body-text colour, never on white.
- **Lit Gold** (`{colors.gold-bright}`): the hover and focus state of anything gold, and the colour of a deep-linked session's title.

### Neutral
- **Night Navy** (`{colors.navy}`): the base ground of the page and the text colour on the one white panel.
- **Deep Night** (`{colors.navy-deep}`): the darkest tone, used for the programme band and the middle of the page's hour.
- **Wash Navy** (`{colors.navy-wash}`): the hero photograph's left wash, a gradient stop and never a surface.
- **First Dawn** (`{colors.dawn-blue}`): the footer's lightest navy, the end of the hour arc.
- **Dawn Mist** (`{colors.mist}`): secondary text, hairlines at low alpha, signage labels, and photo captions.
- **Sharp White** (`{colors.white}`): headlines and primary body text on navy; the register panel's ground.
- **Dawn Low** (`{colors.dawn-low}`): the midpoint of the footer's rise from night to dawn; a gradient stop, never a surface on its own.

Every alpha derivative of these values is a named role token, not an inline `rgba()`: `--scrim-nav`, `--scrim-drawer`, `--scrim-chip`, `--scrim-modal`, `--scrim-clear` for navy laid over content; `--wash-photo` and `--wash-photo-narrow` for the navy wash over the rooftop photograph; `--gold-edge`, `--gold-veil`, `--gold-fade` for gold below full strength; `--ink-dark-soft`, `--rule-dark` for the white surfaces; `--rule-on-panel`, `--rule-on-photo`, `--ink-on-photo` for white laid over navy or photography; `--veil-top`, `--veil-bottom` for the two lights of the hour; `--rule`, `--rule-strong`, `--mist-dim` for hairlines and quiet text. Multi-stop scrim ramps stay inline because each is authored once for one surface. Undocumented earlier and now named: `--grey-200` and `--grey-400` (secondary text on the countdown card and on white) and `--navy-wash` (the hero's left wash).

### Named Rules
**The Named Alpha Rule.** A colour below full opacity gets a role token that says what it is for. `rgba(18,27,49,.66)` typed into a rule is drift; `var(--ink-dark-label)` is the system. The only literals left in the stylesheet are the token definitions themselves, single-use gradient stops, and `#000` inside `mask-image`, where it is the opaque alpha channel rather than a colour.

**The One Light Rule.** One lit gold block per viewport. The masthead's register button stays outlined until the page has scrolled, so the hero's primary action is the only lit thing on arrival.

**The Gold Never Touches Paper Rule.** Gold on navy passes AA (7.1:1); gold on white does not. On any light surface gold appears only as a rule, a mark, or a focus ring — never as text.

**The Hour Rule.** Sections get darker toward the programme and lighter toward the footer. A new section inherits the tone of its position in that arc; it does not pick a background for contrast.

## Typography

**Display Font:** Caladea (with Georgia, Times New Roman)
**Body Font:** Archivo (with the system sans stack)

**Character:** A quiet serif — Caladea's low contrast and open counters read as institutional rather than editorial — carries every heading, set against a wide-aperture grotesk that stays calm at long measure. The contrast is voice, not width: nothing script, nothing condensed, nothing decorative.

### Hierarchy
Every step lives in a `--t-*` custom property; nothing in the stylesheet sets a literal `font-size`. Archivo is loaded at 400, 500 and 600 only, so 600 is the heaviest weight it is set in.

- **Display** (`--t-display`, 400, `clamp(2.9rem, 7.6vw, 6rem)`, 0.9): the page's one headline, set as a destination line, three lines at most. Below 900px it switches to `--t-display-narrow` (`clamp(2.4rem, 7.6vw, 4rem)`), which meets the desktop step exactly at the breakpoint — a responsive variant of one role, not a second step.
- **Headline** (`--t-headline`, 400, `clamp(2rem, 4.4vw, 3.4rem)`, 1.0): every section heading, including the register panel and the partner beacon. Capped at 30–34ch so they break where they should.
- **Title** (`--t-title`, 400, `clamp(1.6rem, 2.6vw, 2.25rem)`, 1.05): a programme day's theme.
- **Subtitle** (`--t-subtitle`, 400, `clamp(1.5rem, 1.8vw, 1.75rem)`, 1.0): a signal plate's value, the footer's name, a ledger figure. One step for all three; they are the same weight of statement.
- **Lead** (`--t-lead`, 400, 1.125rem, 1.62): the hero's subhead and the first paragraph of a section, in white where the rest of the section is mist.
- **Body** (`--t-body`, 400, 1.0625rem, 1.65): paragraphs and list items, held to a 65–75ch measure.
- **Label** (`--t-label`, 500, 0.8125rem, 0.16em, uppercase): service line, day marker, nav items, actions, the footer's base line.
- **Session** (`--t-session`, 400, 1.3rem, 1.4rem from 1080px, 1.22): a programme session's title on the agenda page. The tenth step, added because a session title is longer than a subtitle and shorter than a day theme.
- **Label small** (`--t-label-sm`, 500, 0.75rem, 0.16em, uppercase): a plate's key, a field's label, a photo caption — labels attached to something rather than standing alone.
- **Datum** (`--t-datum`, 400, 0.9375rem, tabular figures): session times, evening lines, the unpublished note, ledger descriptions. Tabular numerals are mandatory wherever times stack in a column.

### Named Rules
**The Times Line Up Rule.** Any column of times, dates or figures uses `font-variant-numeric: tabular-nums`. A ragged time column breaks the whole conceit.

**The Ramp Is Closed Rule.** Ten steps, all tokenised, and the smallest is 12px: the audience skews older, so nothing is set below it. A new element takes the nearest existing step; it does not introduce a tenth. If a step is genuinely missing, it is added here first and to `:root` second.

**The Sentence Stays A Sentence Rule.** Display and headline type is set in sentence case, exactly as the copy is written. Uppercase belongs to labels only, and always with 0.16em tracking.

## Layout

A single column of full-width sections on one shared gutter (`clamp(1.25rem, 5vw, 5.5rem)`), no page-level max width: the ground is meant to run to the edge. Inside a section, content splits into asymmetric two-column pairs — text against image, text against index, day against day — never into a row of equal cards.

Vertical rhythm is one scale (0.5rem to 10rem, in the `spacing` steps above). Sections take `clamp(5rem, 11vw, 10rem)` of vertical padding; a heading always has more space above it than below. Lists and tabular rows are separated by hairlines at `rgba(200,204,215,.16)`, strengthened to `.32` where a rule ends a group.

Every anchor destination carries its own clearance: `scroll-margin-top: 5rem` on sections, days and the footer, `6.5rem` on the 17 programme stations, against a masthead measured at 64px. The page is navigated almost entirely by anchor — five nav items, two hero actions and seventeen deep-linkable sessions — so clearance is a layout invariant, not a per-link fix.

Responsive behaviour has three moves. At 1080px the two-column pairs unstack to one column and the two programme days go from side by side to sequential. At 1200px the nav collapses to a drawer. At 900px the hero's plates stack into a ruled list, actions go full width, the display step drops to `clamp(2.4rem, 7.6vw, 4rem)`, and the heading reflection is dropped rather than shrunk. The page never scrolls horizontally at any width; `overflow-x: clip` on `html, body` is deliberate and must not become `hidden`, which would break scroll-driven behaviour.

## Elevation & Depth

Tonal, atmospheric, and photographic — not shadowed. The scroll-driven hour is a childless fixed `.veil` element whose two lights fade by opacity; its `--hour` is written there and nowhere higher, so a scroll frame restyles one node. Depth comes from three devices: the tone arc of the hour, full-bleed photography behind a layered scrim, and a mirrored reflection under a heading. Only two elements cast a shadow, and both are light sources rather than objects: the lit gold action and the white register panel.

### Shadow Vocabulary
- **Lamp glow** (`box-shadow: 0 6px 26px -10px rgba(194,163,88,.6)`; hover `0 10px 34px -10px rgba(194,163,88,.8)`): under a lit gold action, so it reads as emitting rather than floating.
- **Night lift** (`box-shadow: 0 40px 90px -50px rgba(0,0,0,.85), 0 0 0 1px rgba(194,163,88,.35)`): the register panel, seated in the dark with a gold hairline edge.
- **Signal halo** (`box-shadow: 0 0 12px rgba(194,163,88,.35)` on the line, `0 0 14px 2px rgba(194,163,88,.55)` on an active dot): the programme's own light.

### Named Rules
**The Scrim Is Layered Rule.** Text over photography sits on two stacked gradients — one rising from the page ground, one crossing from the text side — tuned so the measured ground under the text stays under 0.04 relative luminance. A single flat overlay always ends up either too dark for the image or too light for the text.

**Light Sources Are Tokens Rule.** The six shadows on this page are `--glow-lamp`, `--glow-lamp-hi`, `--glow-signal`, `--glow-line`, `--glow-mark`, `--lift-night` and `--lift-dark`. Nothing writes a `box-shadow` inline; nothing else casts anything.

**The Reflection Is A Sliver Rule.** The wet-street echo under a heading is a mirrored copy clipped to 0.44em at 20% opacity with a 1.2px blur. It is a reflection, never a second headline; below 900px it is removed.

## Shapes

Square. Radius is `0` everywhere except the programme's station dots, which are circles because they are lamps on a line. Borders are 1px hairlines in mist at low alpha; there are no boxes drawn around content, no pills, no chips, no coloured left borders. Images are un-inset rectangles, cropped by aspect ratio (8:5 hero, 3:2 plates) and faded with a `mask-image` gradient where they must dissolve into the ground rather than end on an edge.

## Components

### Buttons
- **Shape:** square (`0` radius), 1px border, uppercase label at 0.1em tracking.
- **Lit (primary):** gold ground, navy text, `0.95rem 1.5rem` padding, lamp-glow shadow. Rises 1px on hover to Lit Gold.
- **Quiet (secondary):** transparent with a mist hairline and mist text; goes white-on-mist on hover. No fill, ever.
- **On the white panel:** the primary inverts to navy ground with white text and no glow; the disabled state is navy at 35% with the label still legible.
- **In the masthead:** the register button uses the quiet treatment until the masthead is stuck, then becomes lit.

### Inputs / Fields

There are no inputs in this stylesheet. The register form is a HubSpot embed (portal 147203473, form `e00734ac-26f4-46f6-ad44-464bdc45843e`, region eu1) that renders inside a cross-origin iframe, so its fields, labels, validation and button are outside this system's reach and cannot be styled from here. The panel around it is ours; everything inside it is themed in HubSpot's form editor.

The values that form must be set to, so the embed reads as part of this page rather than a widget dropped into it, are recorded in `HUBSPOT.md`. Treat that file as the input specification: underline-only fields, square corners, Archivo, navy on white, gold focus, no grey card. If a future surface needs a form this page controls, restore the underline field from `.impeccable/pre-hubspot/site.css` rather than inventing a new one.

### Navigation
- **Style:** fixed, transparent on arrival; once scrolled it takes a `rgba(10,16,31,.86)` ground with a blur and a hairline bottom edge.
- **Items:** uppercase mist labels at 0.1em; a gold underline wipes in from the left on hover, focus, or when the section is in view.
- **Mark:** the wordmark carries a small gold square with a soft halo — the lamp that starts the page.
- **Order:** the items follow the order of the sections on the page, so the in-view underline moves left to right as the visitor scrolls.
- **Narrow:** below 1200px (the width the lockup, five routes and the action need side by side) the items collapse into a full-width drawer under the masthead, closed by Escape or by choosing a destination.

### Photographic Plate
- **Style:** a full-width or column-width image with no border and no radius, either scrimmed with layered gradients (hero) or dissolved with a mask gradient (column plate).
- **Caption:** uppercase mist label on a `rgba(10,16,31,.72)` chip, bottom-left inside the image.

### The Timed Line (signature)
- **Style:** an ordered list indented 1.75rem, with a 2px amber gradient line down the gutter and an 8px circle on the line at each entry.
- **Row:** a two-column plain row (`.station__row`) — tabular time, then session title — separated by hairlines. It is not a link and has no hover: the rows have no destination, so they do not borrow the look of one.
- **State:** a session reached by its `#id` fills its dot gold with a halo and warms its title to Lit Gold.
- **Motion:** on first approach the line draws top to bottom over 1.5s and the dots resolve in a 55ms stagger. The drawn state is the CSS default and the animation is applied by removing it, so the programme is fully visible if the script or the observer never runs.

### Reduced motion

`prefers-reduced-motion: reduce` removes travel and keeps feedback. The scroll-coupled hour veil is switched off, the programme line and its dots are already drawn, buttons stop lifting, and the heading reflection is dropped. Every colour and border transition survives at 90ms, because a state change the user cannot perceive is a worse outcome than a state change that arrives quickly. A blanket `transition-duration: 0.01ms` on `*` is the wrong answer and is banned here.

## Do's and Don'ts

### Do:
- **Do** keep one navy ground running through every section and change only its tone.
- **Do** spend gold on the single active thing per viewport, following The One Light Rule.
- **Do** set every column of times with tabular figures.
- **Do** ship a real photograph where the design wants material, and grade it into the navy.
- **Do** hold body text to a 65–75ch measure and give a heading more space above than below.
- **Do** make animated states the removal of a class, so content is visible when nothing runs.
- **Do** give every anchor destination a `scroll-margin-top` that clears the fixed masthead.
- **Do** give every interactive element a box of at least 44px on its short side, `min-height` on the element rather than padding guessed per case.
- **Do** name every alpha and every shadow as a role token before using it.
- **Do** give anything that moves on its own a pause: the partner strip stops on hover, on focus and from its button, and becomes a static wrapped grid under `prefers-reduced-motion`.
- **Do** hold third-party tags until the consent banner reports consent (`assets/js/tags.js`).

### Don't:
- **Don't** put gold text on a white or light surface.
- **Don't** introduce further rounded corners, cards, chips, icon tiles, or glass panels. The countdown tiles and the audience entries are the whole container vocabulary.
- **Don't** set a coloured `border-left` stripe on a list or block; a speaker group on the agenda page takes a gold hairline above it instead.
- **Don't** give a row a hover, a colour change or a cursor unless it goes somewhere.
- **Don't** simulate material — no bevels, embossing, inner shadows, or gradient "textures" standing in for a photograph.
- **Don't** add a second white surface; the register section is the only paper on the page (the standalone claim-your-seat card and the legal pages keep their own).
- **Don't** set an eyebrow label above a heading. The date-and-place service line is a datum with a lamp, placed above the headline as its own element, not a caption for it.
- **Don't** replace `overflow-x: clip` with `hidden`; it turns the body into a scroll container and breaks the page's scroll-driven hour.
- **Don't** scatter hover animations. The page has one authored motion, and it belongs to the programme.
- **Don't** kill all motion under `prefers-reduced-motion`. Remove travel, keep feedback at 90ms.
- **Don't** animate a layout property. `transform` and `opacity` carry every transition on this page, including the skip link's entrance.
- **Don't** write a literal `font-size`, `rgba()` or `box-shadow` in a rule. Ten type steps, the named alphas and the seven light sources are the whole vocabulary.
