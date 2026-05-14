#!/usr/bin/env python3
"""데이터 무결성 + SYNC 무결성 검사 (CI 게이트).

검사 항목:
  B. 가격 필드 무결성: cost-options.json 모든 가격 항목에 source·data_quality
     존재. data_quality는 화이트리스트(confirmed_booking|official_fare|
     researched_market_rate)에 속함.
  C. 묵은 가격 경고: source 문자열에서 ISO 일자 추출, today - date > 30d 이고
     data_quality == researched_market_rate 면 stderr 경고. 60d 초과 시 fail.
  D. SYNC 주석 무결성: index.html의 <!-- SYNC: <path> --> 주석에서 추출한
     path가 실제 파일에 존재. §N 절 번호는 final-report.md 헤더 카운트로 검증.
  E. weather MD↔JSON 동기화: data/weather.json의 각 도시·각 월 comfort_score가
     docs/weather.md 본문에 등장하는지 검증 (도시당 1개 이상 row가 일치해야 함).
  F. flights MD↔JSON 동기화: data/flights.json의 snapshot_date·version이
     docs/flights.md 본문에 등장하고, 핵심 시세(4인 median 천만원 표기) 중
     적어도 1개가 일치하는지 검증.

exit 0 = 모두 통과 또는 경고만, exit 1 = 실패.

용법:
  python scripts/validate.py
  python scripts/validate.py --base <path>      # 테스트용 루트 오버라이드
  python scripts/validate.py --today YYYY-MM-DD # 테스트용 기준일 오버라이드
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ALLOWED_QUALITY = {"confirmed_booking", "official_fare", "researched_market_rate"}
PRICE_SECTIONS = ("flights", "lodging", "daily_fixed", "one_time")
DATE_RE = re.compile(r"(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})")
SYNC_RE = re.compile(r"<!--\s*SYNC:\s*(.+?)\s*-->")
SECTION_RE = re.compile(r"§(\d+)")
PATH_RE = re.compile(r"([\w./\-]+\.(?:md|json|py|html))")


def extract_date(text: str):
    m = DATE_RE.search(text)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def check_price_fields(base: Path, today: date) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    cost = json.loads((base / "data" / "cost-options.json").read_text(encoding="utf-8"))
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

            src = item.get("source", "")
            qual = item.get("data_quality", "")
            d = extract_date(src)
            if d and qual == "researched_market_rate":
                age = (today - d).days
                if age > 60:
                    errors.append(f"[C] {loc}: researched_market_rate stale {age}d (source: {src!r}) — re-research required")
                elif age > 30:
                    warnings.append(f"[C] {loc}: researched_market_rate aging {age}d (source: {src!r})")
    return errors, warnings


def check_sync_comments(base: Path) -> list[str]:
    errors = []
    index_path = base / "index.html"
    final_report = base / "reports" / "final-report.md"
    if not index_path.exists():
        return ["[D] index.html missing — run scripts/build_index.py"]
    text = index_path.read_text(encoding="utf-8")

    fr_text = final_report.read_text(encoding="utf-8") if final_report.exists() else ""
    fr_sections = len(re.findall(r"^## ", fr_text, re.MULTILINE))

    for m in SYNC_RE.finditer(text):
        body = m.group(1)
        for p in PATH_RE.findall(body):
            target = base / p
            if not target.exists():
                errors.append(f"[D] SYNC path missing: {p!r} (in '{body}')")
        if "final-report.md" in body:
            for snum in SECTION_RE.findall(body):
                if int(snum) > fr_sections:
                    errors.append(f"[D] SYNC §{snum} out of range — final-report.md has {fr_sections} sections")
    return errors


def check_weather_sync(base: Path) -> list[str]:
    """검사 E: 각 도시·월 comfort_score sequence가 weather.md의 도시 행에 등장해야 함."""
    errors: list[str] = []
    weather_json = base / "data" / "weather.json"
    weather_md = base / "docs" / "weather.md"
    # 격리된 테스트 fixture에는 weather 파일이 없을 수 있으므로 silent-skip.
    if not weather_json.exists() or not weather_md.exists():
        return errors
    data = json.loads(weather_json.read_text(encoding="utf-8"))
    md = weather_md.read_text(encoding="utf-8")
    cities = data.get("cities", {})
    months = data.get("months", [])
    for city_id, city in cities.items():
        name = city.get("name", city_id)
        # weather.json은 정식 표기 ("오키나와(나하)")를 쓰지만 weather.md는 가독성을 위해
        # 짧은 표기 ("오키나와")를 쓰는 경우가 있어, 괄호 앞 형태도 매칭 후보로 인정.
        short_name = name.split("(")[0].strip()
        name_candidates = {name, short_name}
        if not any(cand in md for cand in name_candidates):
            errors.append(
                f"[E] weather.md: city {name!r} (id={city_id}) not found in markdown body"
            )
            continue
        # weather.md 표 구조: '| 도쿄 | 8 | 5 | 6 | 8 |' — 도시명을 포함한 라인 하나가
        # 모든 월별 score sequence를 그대로 담아야 row-level 동기화가 성립.
        scores = [city[m]["comfort_score"] for m in months if "comfort_score" in city.get(m, {})]
        if not scores:
            continue
        score_seq = " | ".join(str(s) for s in scores)
        row_found = any(
            any(cand in line for cand in name_candidates) and score_seq in line
            for line in md.splitlines()
        )
        if not row_found:
            errors.append(
                f"[E] weather.md: {name} comfort_score sequence '{score_seq}' "
                f"not found in any line containing the city name"
            )
    return errors


def check_flights_sync(base: Path) -> list[str]:
    """검사 F: snapshot_date·version 메타와 4인 median 시세 표기가 flights.md에 등장해야 함."""
    errors: list[str] = []
    flights_json = base / "data" / "flights.json"
    flights_md = base / "docs" / "flights.md"
    # 격리된 테스트 fixture에는 flights 파일이 없을 수 있으므로 silent-skip.
    if not flights_json.exists() or not flights_md.exists():
        return errors
    data = json.loads(flights_json.read_text(encoding="utf-8"))
    md = flights_md.read_text(encoding="utf-8")

    snapshot = data.get("snapshot_date")
    if snapshot and snapshot not in md:
        errors.append(f"[F] flights.md: snapshot_date {snapshot!r} not found in markdown body")

    version = data.get("version")
    if version and version not in md:
        errors.append(f"[F] flights.md: version {version!r} not found in markdown body")

    ranking = data.get("ranking_4pax_median_5night_2026_05", {}).get("by_total_low_to_high", [])
    # 만 단위 변환: KRW 정수를 ÷10000으로 줄여 "63만" 같은 사람용 표기와 매칭.
    tokens = [
        (row.get("city"), f"{row['median_4pax_krw'] // 10000}만")
        for row in ranking
        if isinstance(row.get("median_4pax_krw"), int)
    ]
    if tokens and not any(token in md for _, token in tokens):
        details = ", ".join(f"{city}={token}" for city, token in tokens)
        errors.append(f"[F] flights.md: no median_4pax_krw value matches (checked: {details})")
    return errors


def run(base: Path, today: date) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    e, w = check_price_fields(base, today)
    errors.extend(e)
    warnings.extend(w)
    errors.extend(check_sync_comments(base))
    errors.extend(check_weather_sync(base))
    errors.extend(check_flights_sync(base))
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="레포 루트 (테스트용 오버라이드)")
    parser.add_argument("--today", type=lambda s: date.fromisoformat(s), default=date.today(),
                        help="기준일 (테스트용 오버라이드, YYYY-MM-DD)")
    args = parser.parse_args()

    errors, warnings = run(args.base, args.today)
    for warn in warnings:
        print(f"WARN  {warn}", file=sys.stderr)
    for err in errors:
        print(f"ERROR {err}", file=sys.stderr)
    if errors:
        print(f"\nFAIL — {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"OK — 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
