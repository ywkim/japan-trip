#!/usr/bin/env bash
# reports/final-report.md → reports/final-report.pdf
#
# 우선 pandoc 시도, 실패 시 Chrome headless 시도.

set -euo pipefail

BASE="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$BASE/reports/final-report.md"
OUT="$BASE/reports/final-report.pdf"

if [ ! -f "$SRC" ]; then
  echo "❌ $SRC 파일이 없습니다." >&2
  exit 1
fi

if command -v pandoc >/dev/null 2>&1; then
  echo "→ pandoc으로 변환"
  pandoc "$SRC" -o "$OUT" \
    --pdf-engine=xelatex \
    -V mainfont="AppleGothic" \
    -V geometry:margin=2cm \
    2>/dev/null || pandoc "$SRC" -o "$OUT"
  echo "✓ $OUT 생성 완료"
  exit 0
fi

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ -x "$CHROME" ]; then
  echo "→ Chrome headless로 변환 (pandoc 미설치)"
  TMPHTML="$(mktemp -t final-report).html"
  if command -v markdown >/dev/null 2>&1; then
    markdown "$SRC" > "$TMPHTML"
  else
    # markdown 명령 없으면 단순 변환
    {
      echo '<html><head><meta charset="utf-8"><style>body{font-family:AppleGothic,sans-serif;max-width:800px;margin:2em auto;padding:1em;}</style></head><body><pre>'
      cat "$SRC"
      echo '</pre></body></html>'
    } > "$TMPHTML"
  fi
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$OUT" "file://$TMPHTML"
  echo "✓ $OUT 생성 완료"
  exit 0
fi

echo "❌ pandoc 또는 Google Chrome이 필요합니다." >&2
echo "   pandoc: brew install pandoc" >&2
exit 1
