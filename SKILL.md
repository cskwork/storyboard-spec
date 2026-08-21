---
name: storyboard-spec
description: Side-by-side storyboard 화면설계서. Left = screen (wireframe to design up front, OR replica of a built/Figma UI) with numbered callouts; right = per-element table (action/data/exception); plus thumbnail board. Domain-agnostic.
when_to_use: User wants a 화면설계서 / 스토리보드 / screen design doc / spec / storyboard — to plan screens up front (no UI yet) or to document existing/built/Figma screens for planners and API/frontend devs together.
allowed-tools: Read Write Edit Bash(*) Agent AskUserQuestion
---

Produce **storyboard-style screen design documents** that non-technical planners/QA and API developers read together. One screen (or one state) = one page:

- **LEFT — 화면 (image)**: the screen shown as an **image** — a screenshot / Figma export, or a wireframe/live render captured as the picture — with numbered callout circles on top. This is the canonical storyboard form: left = the visual screen.
- **RIGHT — 화면 설명 (real HTML text)**: an annotation table rendered as **real, selectable HTML text — never a baked image** (must stay searchable/copyable/accessible), one row per callout — element/DOM-id, action/event, data contract, exception, state.
- **BOARD (index.html)**: thumbnail cards (screen previews) linking to each storyboard page.

This is a **planning/spec deliverable**, not a Figma importer. It works in two equally-supported modes — pick by whether the UI exists yet:

- **Mode B — 기획 (design up front, no UI yet)**: draw the screen as a **wireframe** using `storyboard.css` `sb-` boxes/fields/buttons. The doc IS the design. Elements come from the planning intent, not from code.
- **Mode A — 문서화 (an existing/built/Figma screen exists)**: **replica** — reuse the target app's real markup + real CSS so the left pane matches the real screen pixel-for-pixel. Elements are extracted from the code/design. For a **Figma** source with a `FIGMA_TOKEN`, `scripts/figma_storyboard.py` builds the whole page set in one command — read `reference/figma-extract.md` before running it. Without a token, pull nodes via the Figma MCP if available, else the `figma-cli` route (`inspect --json` for elements/coords, `export` for the left image; cloned separately, see `reference/playbook.md` §8).

Both modes share the same right-pane table, board, and verification. The format is domain-agnostic: only the *content* (screens, elements) is project-specific. Deep guide + gotchas live in `reference/playbook.md` — read it before building.

## Files in this skill

- `templates/storyboard.css` — chrome (callouts + annotation table). Themeable via `:root --sb-*`. Link AFTER the target app's CSS.
- `templates/storyboard-page.html` — one-screen page skeleton ({{placeholders}} + inline guidance).
- `templates/board-index.html` — thumbnail board skeleton.
- `scripts/shoot.sh` — headless-Chrome thumbnail + verification screenshots (macOS/Linux/Git Bash/WSL). Windows-native: `scripts/shoot.ps1`.
- `reference/playbook.md` — full process, element-extraction checklist, gotchas, cross-domain porting.
- `scripts/figma_storyboard.py` — **automated Mode A for Figma**: one Figma file → a full storyboard site (screen image + crisp HTML callouts left, real description text right, real policy text bottom, board, shared controls). See `reference/figma-extract.md`.
- `reference/figma-extract.md` — the Figma REST extraction playbook (DescriptionPanel or right TEXT column → HTML, marker/group heuristics → callout overlay, panel/policy split, render-timeout gotcha).
- `templates/storyboard-figma-page.html`, `templates/board-figma-index.html` — page/board skeletons used by `figma_storyboard.py`.
- `templates/settings-control.html` + `.js`, `zoom-control.js`, `lightbox.html` + `.js` — shared page chrome loaded by `figma_storyboard.py`: top-right 글자 크기 + 콜아웃 진하기 slider persisted in `localStorage` (a change on one page applies to all), screen wheel/drag zoom, 원본 보기 in-page viewer.

## Workflow

1. **Scope + mode** — list the screens/states (flow order). Decide the mode: **B (기획)** if no UI exists yet → you'll wireframe; **A (문서화)** if a built/Figma screen exists → find the target UI + its real stylesheet (or export image). Output usually goes in `<app>/design-specs/`. If scope/format/mode is ambiguous, confirm with AskUserQuestion first.
2. **Define elements** — per screen, list every interactive element: name/DOM-id (or selector), action→event, data contract (fields/payload/endpoint), state, exception. **Mode B**: derive these from the planning intent (what each control should do). **Mode A**: extract them from the code/design — for big codebases, fan out fact-extraction to subagents (return distilled facts, not file dumps).
3. **Copy CSS** — copy `templates/storyboard.css` into the output dir (theme `:root` to match the brand if wanted).
4. **Build pages** — from `storyboard-page.html`: RIGHT = `sb-notes` table as **real HTML text**, one row per cue. LEFT = the screen as the picture + `sb-mark`/`sb-cue` callouts — **mode A**: a Figma/screenshot `<img>` (canonical), or a live real-markup+CSS render; **mode B**: a wireframe from `sb-` boxes/fields/buttons.
5. **Build board** — from `board-index.html`, one `.sb-card` per screen.
6. **Thumbnails** — `bash scripts/shoot.sh <design-specs-dir>` → `thumbs/` (Windows-native PowerShell: `scripts\shoot.ps1 <dir>`).
7. **Verify** — Read the generated PNGs: callouts must be white-bordered red circles with centered numbers; left renders cleanly (Mode A: matches the real app); panes align, links/images resolve. Fix and re-shoot.

## Non-negotiable rules (see playbook §5)

- **Left = image, right = real HTML text** (canonical storyboard form). Screen goes left as a picture (screenshot / Figma export / render); the annotation table goes right as real selectable HTML text — never bake the right pane into an image.
- Link order: **target app CSS first, then storyboard.css**.
- **Do not weaken the `.sb-cue { ... !important }` block** — it stops the target app's `span{}` rules from breaking the callouts (centered number, round red circle).
- **Wrap a table in `<div class="sb-mark">` and put the cue on that div** — a `<span class="sb-cue">` placed directly under `<table>/<thead>/<tbody>/<tr>` is foster-parented out and loses its position.
- Verify with a real screenshot before claiming done.

## Defaults

Korean labels (화면/설명/구역/No) by default — swap template strings for English if needed. No emojis in output unless asked.
