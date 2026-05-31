#!/usr/bin/env bash
# shoot.sh — 스토리보드 페이지를 헤드리스 크롬으로 캡처.
#   1) thumbs/<name>.png  : 보드 카드용 화면 위주 썸네일(좁은 폭=1열 레이아웃)
#   2) (옵션) 전체폭 검증샷 : 콜아웃 중앙정렬/레이아웃 확인용
#
# 사용법:
#   scripts/shoot.sh <design-specs-dir>                 # dir 안의 sb-*.html 전부 썸네일
#   scripts/shoot.sh <design-specs-dir> <one-file.html> # 한 파일 전체폭 검증샷(/tmp)
#   CHROME=/path/to/chrome scripts/shoot.sh ...         # 크롬 경로 직접 지정
#
# 검증 루프: 캡처 후 PNG를 Read 로 열어 콜아웃이 흰 테두리 빨강 원 + 중앙 숫자인지,
# 왼쪽 화면이 실제 앱과 같은지 눈으로 확인한다. (대상 앱 CSS가 상대경로로 링크돼 있어야 함)

set -euo pipefail

DIR="${1:?usage: shoot.sh <dir> [one-file.html]}"
ONE="${2:-}"

# file:// 는 절대경로여야 함 → DIR 을 절대경로로
case "$DIR" in /*) ;; *) DIR="$(cd "$DIR" && pwd)" ;; esac
THUMB_W="${THUMB_W:-1000}"     # 썸네일 폭(<=1040 이면 1열로 떨어져 화면이 큼)
THUMB_H="${THUMB_H:-820}"
FULL_W="${FULL_W:-1500}"
FULL_H="${FULL_H:-1500}"

# --- 크롬/크로미움 탐지 ---
if [ -z "${CHROME:-}" ]; then
  for c in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
    "$(command -v google-chrome 2>/dev/null || true)" \
    "$(command -v google-chrome-stable 2>/dev/null || true)" \
    "$(command -v chromium 2>/dev/null || true)" \
    "$(command -v chromium-browser 2>/dev/null || true)" \
    "$(command -v microsoft-edge 2>/dev/null || true)"; do
    if [ -n "$c" ] && [ -x "$c" ]; then CHROME="$c"; break; fi
  done
fi
if [ -z "${CHROME:-}" ]; then
  echo "ERROR: Chrome/Chromium not found. Set CHROME=/path/to/chrome" >&2
  exit 1
fi

shoot() { # <out.png> <w> <h> <file.html>
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --window-size="$2,$3" --screenshot="$1" "file://$4" >/dev/null 2>&1
}

if [ -n "$ONE" ]; then
  f="$DIR/$(basename "$ONE")"
  if [ ! -f "$f" ]; then
    case "$ONE" in /*) f="$ONE" ;; *) f="$(cd "$(dirname "$ONE")" && pwd)/$(basename "$ONE")" ;; esac
  fi
  out="/tmp/sb-verify-$(basename "$ONE" .html).png"
  shoot "$out" "$FULL_W" "$FULL_H" "$f"
  echo "verify shot: $out"
  exit 0
fi

mkdir -p "$DIR/thumbs"
shopt -s nullglob
count=0
for f in "$DIR"/sb-*.html; do
  base="$(basename "$f" .html)"
  shoot "$DIR/thumbs/${base}.png" "$THUMB_W" "$THUMB_H" "$f"
  echo "thumb: thumbs/${base}.png"
  count=$((count+1))
done
[ "$count" -eq 0 ] && echo "no sb-*.html found in $DIR" >&2
echo "done ($count thumbnails)"
