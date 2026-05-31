#!/usr/bin/env bash
# install.sh — 이 레포를 Claude Code / Codex 스킬 디렉토리로 설치.
# 사용법:
#   ./install.sh            # 설치된 런타임 모두에 (~/.claude/skills, ~/.codex/skills)
#   ./install.sh claude     # Claude Code 만
#   ./install.sh codex      # Codex 만
#   ./install.sh <path>     # 임의 경로로
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="storyboard-spec"

copy_to() { # <dest-skill-dir>
  local dest="$1"
  if [ "$SRC" = "$dest" ]; then
    echo "건너뜀 (이미 그 위치에서 실행 중): $dest"
    chmod +x "$SRC/scripts/shoot.sh" 2>/dev/null || true
    return
  fi
  mkdir -p "$(dirname "$dest")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude '.git' "$SRC/" "$dest/"
  else
    mkdir -p "$dest"; cp -R "$SRC/." "$dest/"; rm -rf "$dest/.git" 2>/dev/null || true
  fi
  chmod +x "$dest/scripts/shoot.sh" 2>/dev/null || true
  echo "설치 완료 → $dest"
}

case "${1:-both}" in
  claude) copy_to "$HOME/.claude/skills/$NAME" ;;
  codex)  copy_to "$HOME/.codex/skills/$NAME" ;;
  both)
    installed=0
    if [ -d "$HOME/.claude" ]; then copy_to "$HOME/.claude/skills/$NAME"; installed=1; fi
    if [ -d "$HOME/.codex"  ]; then copy_to "$HOME/.codex/skills/$NAME";  installed=1; fi
    [ "$installed" -eq 0 ] && { echo "Claude/Codex 디렉토리를 못 찾음. 경로를 직접 지정: ./install.sh <path>"; exit 1; }
    ;;
  *) copy_to "$1" ;;   # 임의 경로
esac

echo "사용: '화면설계서 만들어줘' / '스토리보드' 라고 요청하거나 /storyboard-spec"
