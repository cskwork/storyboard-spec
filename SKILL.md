---
name: storyboard-spec
description: Generate side-by-side storyboard-style screen design docs (스토리보드식 화면설계서) — left = pixel-faithful replica of the real screen with numbered callouts, right = per-element annotation table (action/data/exception), plus a thumbnail board index. Reusable across any domain.
when_to_use: User asks for a 화면설계서 / 화면 설계서 / 스토리보드 / screen design doc / screen spec / storyboard, or wants to document app screens for non-developers AND API/frontend devs together (기획 산출물). Also when they say "이런 화면설계 만들어줘" referencing the storyboard format.
allowed-tools: Read Write Edit Bash(*) Agent
---

Produce **storyboard-style screen design documents** that non-technical planners/QA and API developers read together. One screen (or one state) = one page:

- **LEFT — 실제 화면**: a pixel-faithful replica of the real UI (reuse the target app's own CSS), overlaid with numbered callout circles.
- **RIGHT — 화면 설명**: an annotation table, one row per callout — element/DOM-id, action/event, data contract, exception, state.
- **BOARD (index.html)**: thumbnail cards (screen previews) linking to each storyboard page.

The format is domain-agnostic: only the *content* (screens, elements) is project-specific. Deep guide + gotchas live in `reference/playbook.md` — read it before building.

## Files in this skill

- `templates/storyboard.css` — chrome (callouts + annotation table). Themeable via `:root --sb-*`. Link AFTER the target app's CSS.
- `templates/storyboard-page.html` — one-screen page skeleton ({{placeholders}} + inline guidance).
- `templates/board-index.html` — thumbnail board skeleton.
- `scripts/shoot.sh` — headless-Chrome thumbnail + verification screenshots (macOS/Linux/Git Bash/WSL). Windows-native: `scripts/shoot.ps1`.
- `reference/playbook.md` — full process, element-extraction checklist, gotchas, cross-domain porting.

## Workflow

1. **Scope** — list the screens/states (flow order) and find the target UI + its real stylesheet. Output usually goes in `<app>/design-specs/`. If scope/format is ambiguous, confirm with AskUserQuestion first.
2. **Extract** — per screen, pull every interactive element: DOM id/selector, action→event, data contract (fields/payload/endpoint), state, exception. For big codebases, fan out fact-extraction to subagents (return distilled facts, not file dumps).
3. **Copy CSS** — copy `templates/storyboard.css` into the output dir (theme `:root` to match the app if wanted).
4. **Build pages** — from `storyboard-page.html`: LEFT = real markup + real CSS link + `sb-mark`/`sb-cue` callouts; RIGHT = `sb-notes` table, one row per cue.
5. **Build board** — from `board-index.html`, one `.sb-card` per screen.
6. **Thumbnails** — `bash scripts/shoot.sh <design-specs-dir>` → `thumbs/` (Windows-native PowerShell: `scripts\shoot.ps1 <dir>`).
7. **Verify** — Read the generated PNGs: callouts must be white-bordered red circles with centered numbers; left must match the real app; links/images resolve. Fix and re-shoot.

## Non-negotiable rules (see playbook §5)

- Link order: **target app CSS first, then storyboard.css**.
- **Do not weaken the `.sb-cue { ... !important }` block** — it stops the target app's `span{}` rules from breaking the callouts (centered number, round red circle).
- **Never put `<span class="sb-cue">` as a direct child of `<table>/<thead>/<tbody>/<tr>`** — wrap the table in `<div class="sb-mark">` and put the cue there (foster-parenting breaks position).
- Verify with a real screenshot before claiming done.

## Defaults

Korean labels (화면/설명/구역/No) by default — swap template strings for English if needed. No emojis in output unless asked.
