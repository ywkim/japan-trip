#!/usr/bin/env python3
"""3M 예산 시나리오 비교 분석.

data/cost-options.json을 읽어 각 시나리오의 비용을 분해하고
- 확정 항목 합계
- 카테고리별 합계 + 가이드 비율 대비 격차
- 미확정(TBD) 항목 목록
- 3M 예산 통과 가능 여부 (확정만 기준)
- 통과를 위한 미확정 항목 합계 상한
을 출력한다.
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "cost-options.json"

CATEGORY_DEFAULT = {
    "flights": "flight",
    "lodging": "lodging",
    "daily_fixed": "food",
    "one_time": "other",
}


def find(items, item_id):
    for it in items:
        if it["id"] == item_id:
            return it
    raise KeyError(f"id 없음: {item_id}")


def fmt_won(n):
    return f"₩{n:>10,}"


def evaluate(scenario, options):
    confirmed = []
    tbd = []
    by_category = {}

    def add(category, label, amt):
        confirmed.append((label, amt))
        by_category[category] = by_category.get(category, 0) + amt

    flight = find(options["flights"], scenario["flight"])
    cat = flight.get("category", CATEGORY_DEFAULT["flights"])
    add(cat, f"항공: {flight['label']}", flight["total_krw"])

    for plan in scenario["lodging_plan"]:
        lodge = find(options["lodging"], plan["lodging"])
        nights = plan["nights"]
        per_night = lodge["per_night_krw"]
        line = f"숙박: {lodge['name']} × {nights}박"
        if per_night is None:
            tbd.append((line, "박당 ?원"))
            continue
        cat = lodge.get("category", CATEGORY_DEFAULT["lodging"])
        add(cat, line, per_night * nights)

    pax = options["trip_pax"]
    for daily in scenario.get("fixed_days", []):
        df = find(options["daily_fixed"], daily["daily_fixed"])
        days = daily["days"]
        per = df["krw_per_pax_per_day"]
        line = f"고정비: {df['label']} × {pax}인 × {days}일"
        if per is None:
            tbd.append((line, "1인1일 ?원"))
            continue
        cat = df.get("category", CATEGORY_DEFAULT["daily_fixed"])
        add(cat, line, per * pax * days)

    for ot_id in scenario.get("one_time", []):
        ot = find(options["one_time"], ot_id)
        line = f"일회성: {ot['label']}"
        if ot["krw"] is None:
            tbd.append((line, "?원"))
            continue
        cat = ot.get("category", CATEGORY_DEFAULT["one_time"])
        add(cat, line, ot["krw"])

    return confirmed, tbd, by_category


def render_scenario(scn, options, cap, targets_index):
    confirmed, tbd, by_cat = evaluate(scn, options)
    print(f"━━ [{scn['id']}] {scn['label']} ━━")
    for label, amt in confirmed:
        print(f"  ✓ {label:<55}{fmt_won(amt)}")
    confirmed_total = sum(a for _, a in confirmed)
    print(f"  {'─' * 75}")
    print(f"  {'확정 소계':<57}{fmt_won(confirmed_total)}")

    headroom = cap - confirmed_total
    if headroom < 0:
        print(f"  ❌ 확정만으로 이미 3M 초과: {fmt_won(-headroom)}")
    else:
        print(f"  ✅ 3M 안 여유: {fmt_won(headroom)}")

    if tbd:
        print(f"  미확정 (TBD) 항목 {len(tbd)}개:")
        for label, hint in tbd:
            print(f"    · {label:<55}{hint:>15}")

    if targets_index and by_cat:
        print(f"\n  카테고리 비율 (실제 vs 가이드, 3M 기준):")
        print(f"  {'카테고리':<10} {'금액':>12}  {'실제 %':>7}  {'가이드 %':>9}  {'가이드 한도':>13}  상태")
        for cat_id, target in targets_index.items():
            actual = by_cat.get(cat_id, 0)
            actual_pct = actual / cap * 100
            target_pct = target["pct"] * 100
            limit = target["max_krw"]
            if actual <= limit:
                marker = "✅"
            elif actual <= limit * 1.1:
                marker = "⚠️  약간 초과"
            else:
                marker = "❌ 큰 폭 초과"
            print(f"  {target['label']:<10} {fmt_won(actual):>12}  {actual_pct:>6.1f}%  {target_pct:>8.1f}%  {fmt_won(limit):>13}  {marker}")

    print()


def main() -> int:
    options = json.loads(DATA.read_text(encoding="utf-8"))
    cap = options["budget_cap_krw"]
    pax = options["trip_pax"]

    targets = options.get("budget_allocation_targets", {}).get("categories", [])
    targets_index = {t["id"]: t for t in targets}

    print(f"예산 상한: {fmt_won(cap)}  ·  여행자 수: {pax}명")
    print(f"카탈로그: 항공 {len(options['flights'])} / 숙박 {len(options['lodging'])} / "
          f"일별고정 {len(options['daily_fixed'])} / 일회성 {len(options['one_time'])} / "
          f"시나리오 {len(options['scenarios'])}")
    if targets:
        print(f"\n예산 가이드 비율 (3M = ₩{cap:,} 기준):")
        for t in targets:
            print(f"  · {t['label']:<10} {t['pct']*100:>5.1f}%  ≤ {fmt_won(t['max_krw'])}  — {t['rationale']}")
    print()

    for scn in options["scenarios"]:
        render_scenario(scn, options, cap, targets_index)

    return 0


if __name__ == "__main__":
    sys.exit(main())
