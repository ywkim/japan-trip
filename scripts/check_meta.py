#!/usr/bin/env python3
"""메타 데이터 무결성 검사 (CI 게이트).

검사 항목:
  B. 가격 필드 무결성: cost-options.json 모든 가격 항목에 source·data_quality
     존재. data_quality는 화이트리스트(confirmed_booking|official_fare|
     researched_market_rate)에 속함.
  C. 묵은 가격 경고: source 문자열에서 ISO 일자 추출, today - date > 30d 이고
     data_quality == researched_market_rate 면 stderr 경고. 60d 초과 시 fail.
  D. SYNC 주석 무결성: index.html의 <!-- SYNC: <path> --> 주석에서 추출한
     path가 실제 파일에 존재. §N 절 번호는 final-report.md 헤더 카운트로 검증.

exit 0 = 모두 통과 또는 경고만, exit 1 = 실패.

용법:
  python scripts/check_meta.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
COST = BASE / "data" / "cost-options.json"
INDEX = BASE / "index.html"
FINAL_REPORT = BASE / "reports" / "final-report.md"

ALLOWED_QUALITY = {"confirmed_booking", "official_fare", "researched_market_rate"}
PRICE_SECTIONS = ("flights", "lodging", "daily_fixed", "one_time")
DATE_RE = re.compile(r"(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})")
SYNC_RE = re.compile(r"<!--\s*SYNC:\s*(.+?)\s*-->")
SECTION_RE = re.compile(r"§(\d+)")
PATH_RE = re.compile(r"([\w./\-]+\.(?:md|json|py|html))")
TODAY = date.today()


def extract_date(text: str):
    m = DATE_RE.search(text)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def check_price_fields() -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    cost = json.loads(COST.read_text(encoding="utf-8"))
    for section in PRICE_SECTIONS:
        for item in cost.get(section, []):
            iid = item.get("id", "<no-id>")
            loc = f"{section}.{iid}"
            if "source" not in item or not item["source"]:
                errors.append(f"[B] {loc}: missing 'source'")
            if "data_quality" not in item:
                errors.append(f"[B] {loc}: missing 'data_quality'")
            elif item["data_quality"] not in ALLOWED_QUALITY:
                errors.append(f"[B] {loc}: data_quality '{item['data_quality']}' not in {sorted(ALLOWED_QUALITY)}")

            # C. 묵은 가격
            src = item.get("source", "")
            qual = item.get("data_quality", "")
            d = extract_date(src)
            if d and qual == "researched_market_rate":
                age = (TODAY - d).days
                if age > 60:
                    errors.append(f"[C] {loc}: researched_market_rate stale {age}d (source: {src!r}) — re-research required")
                elif age > 30:
                    warnings.append(f"[C] {loc}: researched_market_rate aging {age}d (source: {src!r})")
    return errors, warnings


def check_sync_comments() -> list[str]:
    errors = []
    if not INDEX.exists():
        return ["[D] index.html missing — run scripts/build_index.py"]
    text = INDEX.read_text(encoding="utf-8")

    # final-report.md 헤더 카운트 (## …)
    fr_text = FINAL_REPORT.read_text(encoding="utf-8") if FINAL_REPORT.exists() else ""
    fr_sections = len(re.findall(r"^## ", fr_text, re.MULTILINE))

    for m in SYNC_RE.finditer(text):
        body = m.group(1)
        # 경로 검증
        for p in PATH_RE.findall(body):
            target = BASE / p
            if not target.exists():
                errors.append(f"[D] SYNC path missing: {p!r} (in '{body}')")
        # 절 번호 검증 (final-report.md를 가리킬 때만)
        if "final-report.md" in body:
            for snum in SECTION_RE.findall(body):
                if int(snum) > fr_sections:
                    errors.append(f"[D] SYNC §{snum} out of range — final-report.md has {fr_sections} sections")
    return errors


def main() -> int:
    all_errors: list[str] = []
    all_warnings: list[str] = []

    e, w = check_price_fields()
    all_errors.extend(e)
    all_warnings.extend(w)

    all_errors.extend(check_sync_comments())

    for warn in all_warnings:
        print(f"WARN  {warn}", file=sys.stderr)
    for err in all_errors:
        print(f"ERROR {err}", file=sys.stderr)

    if all_errors:
        print(f"\nFAIL — {len(all_errors)} error(s), {len(all_warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"OK — 0 errors, {len(all_warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
