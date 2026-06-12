# Figma → storyboard 화면설계서 (automated Mode A)

When the "real screen" lives in a **Figma** design file (not a running app), generate the
storyboard from the Figma REST API. The Figma frames are usually *already* storyboards
(left wireframe + right description). The job: keep the screen as an **image**, but lift every
annotation out as **real HTML text** — so it stays selectable, searchable, and crisp.

One command does the whole pipeline:

```bash
export FIGMA_TOKEN=figd_...        # or put it in the skill's .env (gitignored)
export FIGMA_FILE_KEY=xxxxxxxx     # the /design/<KEY>/ segment of the file URL
python3 scripts/figma_storyboard.py --out ./design-specs --pages 9:2,60:2 --title "My CMS"
#   --pages  comma canvas-page node ids (URL node-id 9-2 == api id 9:2); omit = all pages
```

Output: `design-specs/<page>-NN.html` per frame, `index.html` board, `assets/` (full + `-screen` crop),
`thumbs/`, and a copy of `storyboard.css`.

## What each page contains

| Region | Source | Rendered as |
|---|---|---|
| LEFT screen | frame image, cropped to exclude right panel + bottom policy | `<img>` in `.sb-stage` |
| callout ①②③ | Figma marker nodes (ELLIPSE + digit TEXT), or styled marker TEXT groups | crisp HTML `.sb-cue.pin` overlay, positioned by % |
| RIGHT description | `DescriptionPanel` TEXT nodes, or a right-side TEXT column | real HTML text (`.sb-desc`, numbered `.sb-num` badges) |
| BOTTOM policy/rules | `PolicyBox` TEXT nodes | real HTML text (`.sb-policy`) |

**Never bake annotation text into the image.** The whole point is selectable/searchable text and
sharp callouts at any zoom.

## How the pipeline works (and the traps)

1. **Map** — `GET /v1/files/{KEY}?depth=2` → canvas pages → `FRAME` children. Sort `SB-*` first.
2. **Per-frame extract** (`GET /v1/files/{KEY}/nodes?ids=...&depth=14`):
   - **Description panel** = a child `FRAME` named `*Description*`, else the right-side tall narrow
     column (relx > 45 % of width, 480–900 px wide). Its left edge = the screen's **right crop X**.
     If there is no panel frame, fall back to a right-side TEXT column: first use a `Description`
     label's x position, else use the left edge of repeated right-side text blocks. Filter out
     metadata (`Date`, `Ver`, `Writer`, `Description`, version/date strings) and standalone marker
     numbers before rendering description HTML.
   - **Policy box** = a child named `*policy*`, else a wide frame low in the canvas (relY > 50 %,
     width > 40 %), left of the description panel. Its top = the screen's **bottom crop Y**.
   - **Callout markers** = small ELLIPSE (20–36 px) with a marker TEXT centered on it (≤ 8 px).
     Marker text may be `1`, `10`, `4-4`, or `*`. Keep only those inside the screen region
     (left of panel, above policy) — this drops right-panel section numbers and table-data digits.
   - **Text-only marker fallback** = accept marker-looking TEXT only when its layer path looks like a
     marker group (`description_`, `point`, `marker`, `callout`, `pin`, `annotation`) **and** the text
     style looks like a marker (white bold text or red marker fill). Do not promote arbitrary numeric
     UI data such as counts, table values, page numbers, scores, or dates.
   - **Text** = every `TEXT` node's `characters`, sorted by (y, x) to recover reading order.
3. **Export** — `GET /v1/images/{KEY}?ids=<one id>&format=png&scale=3`.
   - **Render-timeout trap:** batching many large frames returns `400 "Render timeout, try requesting
     fewer or smaller images"`. Export **one frame id per request** (a few worker threads is fine).
     Fall back to a smaller scale if `maxdim * scale` is too big.
   - Crop the screen with PIL to `(0, 0, cropX*scale, cropY*scale)`.
4. **Render** — text → HTML: a standalone marker number (`1`, `10`, `4-4`, `*`) or a circled digit
   (①…㉚) starts a numbered section (`.sb-num` badge = the on-screen callout number); `•`/`-` lines
   become `<li>`. Callout overlay left/top % = `marker.center ÷ crop size`. Multi-character marker
   labels get `--sb-cue-size` / `--sb-cue-font` so they stay centered inside one red circle.

## Marker extraction checklist

When adapting the extractor for a new Figma source, verify these in the generated HTML and a screenshot:

- Right-side description text is real HTML, not part of the exported image.
- A screen with no real on-screen marker does not invent a fallback marker.
- Numeric UI data in lists, tables, badges, dates, or counters does not become `data-cue="..."`.
- Compound marker labels such as `4-4` remain unbroken inside the red marker and the right-side `.sb-num`.
- The original full frame is still reachable through the 원본 보기/lightbox link.

## Shared controls (top-right, common to all pages)

`templates/settings-control.html` + `.js`, styled in `storyboard.css`:
- **글자 크기** (가−/가/가+) → sets `--sb-fz`; reading text uses `calc(<px> * var(--sb-fz))`.
- **콜아웃 진하기** slider → sets `--sb-cue-op`; `.sb-cue.pin { opacity: var(--sb-cue-op) }` (default 0.6
  so numbers don't obscure the screen; hover the screen for full strength).
- Both persist in `localStorage` (`sbFz`, `sbCueOp`) and apply **before paint** (no flash). A change on
  one storyboard applies to **all** on next load, and live across open tabs via the `storage` event.

## Per-page interactions

- **Left TOC** (`.sb-toc`, built by `build_toc`) lists every screen grouped by page with the current one
  highlighted — jump between screens without going back to the board. It fills the otherwise-empty centered
  margin, so content shifts right and no space is wasted (`templates/*`'s `.sb-layout` grid).
- **Screen zoom/pan** (`templates/zoom-control.js`): wheel-zoom on the screen (centered on the cursor),
  −/+/맞춤 buttons in the screen caption, drag-to-pan, double-click reset. Callouts live inside `.sb-stage`
  so they zoom/pan with the screen.
- **원본 viewer** (`templates/lightbox.html` + `lightbox.js`): the 원본 보기 button opens the full-res frame
  in an **in-page popup** (not a new tab), fit-to-screen, with the same wheel/buttons/drag zoom; Esc / ✕ /
  backdrop close.

## CSS gotcha that bit us

In `.sb-split` (CSS grid), grid items default to `min-width: auto` (= min-content), so a wide screen
image blows the track out to its natural pixel width. Keep `.sb-split > * { min-width: 0 }` and make the
image's wrapping `<a>` `display:block` so `width:100%` resolves against the column.
