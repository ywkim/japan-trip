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
  G. itinerary arrive_from 무결성: data/itinerary.json의 모든
     days[].items[].arrive_from 항목에 mode·source·source_fetched_at·
     data_quality 존재. data_quality는 ALLOWED_QUALITY ∪
     {'tbd_needs_browser_mcp'}. source_fetched_at > 60d 이고
     data_quality != tbd_needs_browser_mcp 면 stale fail. mode=walk leg의
     distance_km 합과 days[].walking_km 차이가 2km 초과면 fail (정수 반올림
     오차 + 시장·사찰 내부 산책 추정 여유 포함). 옵션 필드 source_url은
     http(s):// prefix, source_verified_at은 ISO date(YYYY-MM-DD)여야 함.
  H. DESIGN MD↔JSON 동기화: DESIGN.md의 모든 hex 색상이 data/design-tokens.json의
     color 트리에 존재하고, 그 반대(tokens의 모든 색이 DESIGN.md 본문에 등장)도
     성립. theme_name·version 일치. (4개 산출물(index·itinerary·itinerary-table·
     checklist)의 CSS는 scripts/build_index.py가 tokens에서 생성하므로 별도
     sentinel 검증 불필요 — build_index.py --check가 drift를 잡는다.)
  I. itinerary food_quality 무결성: data/itinerary.json의 식사 항목 food_quality에
     rating·source·source_fetched_at·data_quality 존재. data_quality는
     ITINERARY_QUALITY 화이트리스트. source_fetched_at > 60d 이고
     data_quality != tbd_needs_browser_mcp 면 stale fail. food_quality가 없는
     항목(동네 끼니 등)은 면제. route_candidates도 순회.
  J. Vercel 산출물 GitHub 링크 금지: Vercel이 서빙하는 HTML(index.html +
     viz/*.html 전체)에 'github.com' 문자열(링크·raw URL 모두)이 등장하면 fail.
     가족 공유 페이지에서 레포 노출 방지 — 외부 문서는 사이트 내 HTML로 연결하거나
     일반 텍스트(레포 경로)로만 표기.

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
ITINERARY_QUALITY = ALLOWED_QUALITY | {"tbd_needs_browser_mcp"}
ITINERARY_MODES = {"walk", "bus", "subway", "train", "jr", "airport_express", "taxi"}
WALKING_KM_TOLERANCE = 2.0
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


def check_itinerary_transit(base: Path, today: date) -> tuple[list[str], list[str]]:
    """검사 G: data/itinerary.json arrive_from 무결성 + walking_km 합 정합성."""
    errors: list[str] = []
    warnings: list[str] = []
    itin_path = base / "data" / "itinerary.json"
    if not itin_path.exists():
        return errors, warnings
    data = json.loads(itin_path.read_text(encoding="utf-8"))
    for day in data.get("days", []):
        day_label = day.get("date") or day.get("day_label", "?")
        walk_sum = 0.0
        for idx, item in enumerate(day.get("items", [])):
            af = item.get("arrive_from")
            if af is None:
                continue
            loc = f"{day_label}.items[{idx}].arrive_from ({item.get('title','?')})"
            for field in ("mode", "source", "source_fetched_at", "data_quality"):
                if not af.get(field):
                    errors.append(f"[G] {loc}: missing '{field}'")
            mode = af.get("mode")
            if mode and mode not in ITINERARY_MODES:
                errors.append(f"[G] {loc}: mode {mode!r} not in {sorted(ITINERARY_MODES)}")
            qual = af.get("data_quality")
            if qual and qual not in ITINERARY_QUALITY:
                errors.append(f"[G] {loc}: data_quality {qual!r} not in {sorted(ITINERARY_QUALITY)}")
            su = af.get("source_url")
            if su and not su.startswith(("http://", "https://")):
                errors.append(f"[G] {loc}: source_url {su!r} must start with http(s)://")
            sv = af.get("source_verified_at")
            if sv:
                try:
                    date.fromisoformat(sv)
                except ValueError:
                    errors.append(f"[G] {loc}: source_verified_at {sv!r} not ISO date (YYYY-MM-DD)")
            fetched = af.get("source_fetched_at")
            if fetched and qual and qual != "tbd_needs_browser_mcp":
                d = extract_date(fetched)
                if d:
                    age = (today - d).days
                    if age > 60:
                        errors.append(f"[G] {loc}: source_fetched_at stale {age}d — re-research required")
                    elif age > 30:
                        warnings.append(f"[G] {loc}: source_fetched_at aging {age}d")
            if mode == "walk":
                dist = af.get("distance_km")
                if isinstance(dist, (int, float)):
                    walk_sum += dist
        declared = day.get("walking_km")
        if isinstance(declared, (int, float)) and walk_sum > 0:
            # leg 합은 경내·시장 내부 산책 미포함이므로 declared의 하한.
            # leg 합이 declared를 초과(+ tolerance)할 때만 부정합으로 본다.
            if walk_sum - declared > WALKING_KM_TOLERANCE:
                errors.append(
                    f"[G] {day_label}: items[].arrive_from[mode=walk] sum {walk_sum:.1f}km "
                    f"exceeds declared walking_km {declared} + {WALKING_KM_TOLERANCE}km tolerance"
                )
    return errors, warnings


HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _flatten_color_hexes(color_tree: dict) -> set[str]:
    """{light: {bg: '#...', ...}, dark: {...}} → {'#...', ...} (대문자)."""
    out: set[str] = set()
    for variant in color_tree.values():
        if not isinstance(variant, dict):
            continue
        for v in variant.values():
            if isinstance(v, str) and HEX_RE.fullmatch(v):
                out.add(v.upper())
    return out


def check_design_sync(base: Path) -> list[str]:
    """검사 H: DESIGN.md ↔ data/design-tokens.json hex 양방향 + theme_name·version."""
    errors: list[str] = []
    design_md = base / "DESIGN.md"
    tokens_json = base / "data" / "design-tokens.json"
    # 격리된 fixture가 디자인 자산을 갖추지 않은 경우 silent-skip.
    if not design_md.exists() or not tokens_json.exists():
        return errors
    tokens = json.loads(tokens_json.read_text(encoding="utf-8"))
    md = design_md.read_text(encoding="utf-8")

    md_hexes = {h.upper() for h in HEX_RE.findall(md)}
    token_hexes = _flatten_color_hexes(tokens.get("color", {}))

    missing_in_tokens = md_hexes - token_hexes
    if missing_in_tokens:
        errors.append(
            f"[H] DESIGN.md hex(es) not in design-tokens.json color tree: "
            f"{sorted(missing_in_tokens)}"
        )
    missing_in_md = token_hexes - md_hexes
    if missing_in_md:
        errors.append(
            f"[H] design-tokens.json color(s) not documented in DESIGN.md: "
            f"{sorted(missing_in_md)}"
        )

    theme = tokens.get("theme_name")
    version = tokens.get("version")
    if theme and theme not in md:
        errors.append(f"[H] DESIGN.md missing theme_name {theme!r} from tokens")
    if version and version not in md:
        errors.append(f"[H] DESIGN.md missing version {version!r} from tokens")

    return errors


def check_itinerary_food_quality(base: Path, today: date) -> tuple[list[str], list[str]]:
    """검사 I: data/itinerary.json food_quality 무결성 (식사 항목 평점 출처).

    식사 항목에 food_quality가 있을 때만 검사한다(동네/비식사 항목은 면제 — G와 동일
    '있으면 검증' 패턴). rating·source·source_fetched_at·data_quality 필수.
    data_quality는 ITINERARY_QUALITY 화이트리스트. source_fetched_at > 60d 이고
    data_quality != tbd_needs_browser_mcp 면 stale fail. route_candidates도 순회.
    """
    errors: list[str] = []
    warnings: list[str] = []
    itin_path = base / "data" / "itinerary.json"
    if not itin_path.exists():
        return errors, warnings
    data = json.loads(itin_path.read_text(encoding="utf-8"))

    def scan(items, ctx):
        for idx, item in enumerate(items):
            fq = item.get("food_quality")
            if fq is None:
                continue
            loc = f"{ctx}.items[{idx}].food_quality ({item.get('title', '?')})"
            for field in ("rating", "source", "source_fetched_at", "data_quality"):
                if not fq.get(field):
                    errors.append(f"[I] {loc}: missing '{field}'")
            qual = fq.get("data_quality")
            if qual and qual not in ITINERARY_QUALITY:
                errors.append(f"[I] {loc}: data_quality {qual!r} not in {sorted(ITINERARY_QUALITY)}")
            fetched = fq.get("source_fetched_at")
            if fetched and qual and qual != "tbd_needs_browser_mcp":
                d = extract_date(fetched)
                if d:
                    age = (today - d).days
                    if age > 60:
                        errors.append(f"[I] {loc}: source_fetched_at stale {age}d — re-research required")
                    elif age > 30:
                        warnings.append(f"[I] {loc}: source_fetched_at aging {age}d")

    for day in data.get("days", []):
        scan(day.get("items", []), day.get("date") or day.get("day_label", "?"))
    for rc in data.get("route_candidates", []):
        rc_name = rc.get("id") or rc.get("name", "?")
        for day in rc.get("days", []):
            scan(day.get("items", []), f"{rc_name}/{day.get('date') or day.get('day_label', '?')}")
    return errors, warnings


def check_no_github_links(base: Path) -> list[str]:
    """검사 J: Vercel 산출물 HTML에 github.com 링크/URL이 없어야 함.

    가족과 공유하는 페이지에서 레포(소스·미렌더 .md)로 빠져나가는 링크를 막는다.
    index.html + viz/*.html 전체를 glob으로 스캔하므로 새 viz 페이지(문서 렌더
    페이지 등)도 자동 포함. 존재하지 않는 산출물은 silent-skip (격리 fixture 대응).
    """
    errors: list[str] = []
    targets: list[str] = []
    if (base / "index.html").exists():
        targets.append("index.html")
    targets.extend(
        sorted(str(p.relative_to(base).as_posix()) for p in (base / "viz").glob("*.html"))
    )
    for rel in targets:
        if "github.com" in (base / rel).read_text(encoding="utf-8"):
            errors.append(
                f"[J] {rel}: github.com 참조 발견 — Vercel 산출물에는 GitHub 링크 금지 "
                f"(사이트 내 HTML로 연결하거나 일반 텍스트로 표기)"
            )
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
    e, w = check_itinerary_transit(base, today)
    errors.extend(e)
    warnings.extend(w)
    errors.extend(check_design_sync(base))
    e, w = check_itinerary_food_quality(base, today)
    errors.extend(e)
    warnings.extend(w)
    errors.extend(check_no_github_links(base))
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
