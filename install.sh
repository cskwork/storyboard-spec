#!/usr/bin/env bash
# install.sh — 이 레포를 Claude Code 사용자 스킬 디렉토리로 설치.
# 사용법:  ./install.sh            # → ~/.claude/skills/storyboard-spec
#          ./install.sh <dest>     # 다른 경로로
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${1:-$HOME/.claude/skills/storyboard-spec}"

if [ "$SRC" = "$DEST" ]; then
  echo "이미 스킬 디렉토리에서 실행 중입니다: $DEST"
  echo "(별도 설치 불필요 — 이 위치가 곧 설치 위치)"
  chmod +x "$SRC/scripts/shoot.sh" 2>/dev/null || true
  exit 0
fi

mkdir -p "$(dirname "$DEST")"
# .git 등 제외하고 복사
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude '.git' "$SRC/" "$DEST/"
else
  mkdir -p "$DEST"
  cp -R "$SRC/." "$DEST/"
  rm -rf "$DEST/.git" 2>/dev/null || true
fi
chmod +x "$DEST/scripts/shoot.sh" 2>/dev/null || true

echo "설치 완료: $DEST"
echo "사용: Claude Code 에서 '화면설계서 만들어줘' / '스토리보드' 라고 요청하거나 /storyboard-spec"
