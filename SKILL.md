---
name: storyboard-spec
description: Side-by-side storyboard 화면설계서. Left = screen (wireframe to design up front, OR replica of a built/Figma UI) with numbered callouts; right = per-element table (action/data/exception); plus thumbnail board. Domain-agnostic.
when_to_use: User wants a 화면설계서 / 스토리보드 / screen design doc / spec / storyboard — to plan screens up front (no UI yet) or to document existing/built/Figma screens for planners and API/frontend devs together.
allowed-tools: Read Write Edit Bash(*) Agent
---

Produce **storyboard-style screen design documents** that non-technical planners/QA and API developers read together. One screen (or one state) = one page:

- **LEFT — 화면 (image)**: the screen shown as an **image** — a screenshot / Figma export, or a wireframe/live render captured as the picture — with numbered callout circles on top. This is the canonical storyboard form: left = the visual screen.
- **RIGHT — 화면 설명 (real HTML text)**: an annotation table rendered as **real, selectable HTML text — never a baked image** (must stay searchable/copyable/accessible), one row per callout — element/DOM-id, action/event, data contract, exception, state.
- **BOARD (index.html)**: thumbnail cards (screen previews) linking to each storyboard page.

This is a **planning/spec deliverable**, not a Figma importer. It works in two equally-supported modes — pick by whether the UI exists yet:

- **Mode B — 기획 (design up front, no UI yet)**: draw the screen as a **wireframe** using `storyboard.css` `sb-` boxes/fields/buttons. The doc IS the design. Elements come from the planning intent, not from code.
- **Mode A — 문서화 (an existing/built/Figma screen exists)**: **replica** — reuse the target app's real markup + real CSS so the left pane matches the real screen pixel-for-pixel. Elements are extracted from the code/design. For a **Figma** source, pull it via the Figma MCP if available, else the bundled `figma-cli` route (`inspect --json` for elements/coords, `export` for the left image) — see `reference/playbook.md` §8.

Both modes share the same right-pane table, board, and verification. Default to asking which mode if it isn't obvious. The format is domain-agnostic: only the *content* (screens, elements) is project-specific. Deep guide + gotchas live in `reference/playbook.md` — read it before building.

## Files in this skill

- `templates/storyboard.css` — chrome (callouts + annotation table). Themeable via `:root --sb-*`. Link AFTER the target app's CSS.
- `templates/storyboard-page.html` — one-screen page skeleton ({{placeholders}} + inline guidance).
- `templates/board-index.html` — thumbnail board skeleton.
- `scripts/shoot.sh` — headless-Chrome thumbnail + verification screenshots (macOS/Linux/Git Bash/WSL). Windows-native: `scripts/shoot.ps1`.
- `reference/playbook.md` — full process, element-extraction checklist, gotchas, cross-domain porting.

## Workflow

1. **Scope + mode** — list the screens/states (flow order). Decide the mode: **B (기획)** if no UI exists yet → you'll wireframe; **A (문서화)** if a built/Figma screen exists → find the target UI + its real stylesheet (or export image). Output usually goes in `<app>/design-specs/`. If scope/format/mode is ambiguous, confirm with AskUserQuestion first.
2. **Define elements** — per screen, list every interactive element: name/DOM-id (or selector), action→event, data contract (fields/payload/endpoint), state, exception. **Mode B**: derive these from the planning intent (what each control should do). **Mode A**: extract them from the code/design — for big codebases, fan out fact-extraction to subagents (return distilled facts, not file dumps).
3. **Copy CSS** — copy `templates/storyboard.css` into the output dir (theme `:root` to match the brand if wanted).
4. **Build pages** — from `storyboard-page.html`: RIGHT = `sb-notes` table, one row per cue. LEFT depends on mode — **B**: a wireframe from `sb-` boxes/fields/buttons; **A**: real markup + real CSS link (or export `<img>`). Both add `sb-mark`/`sb-cue` callouts.
5. **Build board** — from `board-index.html`, one `.sb-card` per screen.
6. **Thumbnails** — `bash scripts/shoot.sh <design-specs-dir>` → `thumbs/` (Windows-native PowerShell: `scripts\shoot.ps1 <dir>`).
7. **Verify** — Read the generated PNGs: callouts must be white-bordered red circles with centered numbers; left renders cleanly (Mode A: matches the real app); panes align, links/images resolve. Fix and re-shoot.

## Non-negotiable rules (see playbook §5)

- Link order: **target app CSS first, then storyboard.css**.
- **Do not weaken the `.sb-cue { ... !important }` block** — it stops the target app's `span{}` rules from breaking the callouts (centered number, round red circle).
- **Never put `<span class="sb-cue">` as a direct child of `<table>/<thead>/<tbody>/<tr>`** — wrap the table in `<div class="sb-mark">` and put the cue there (foster-parenting breaks position).
- Verify with a real screenshot before claiming done.

## Defaults

Korean labels (화면/설명/구역/No) by default — swap template strings for English if needed. No emojis in output unless asked.
