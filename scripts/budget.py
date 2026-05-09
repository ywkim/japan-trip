#!/usr/bin/env python3
"""3M 예산 시나리오 비교 분석.

data/cost-options.json을 읽어 각 시나리오의 비용을 분해하고
- 확정 항목 합계
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

    # 항공
    flight = find(options["flights"], scenario["flight"])
    confirmed.append((f"항공: {flight['label']}", flight["total_krw"]))

    # 숙박
    for plan in scenario["lodging_plan"]:
        lodge = find(options["lodging"], plan["lodging"])
        nights = plan["nights"]
        per_night = lodge["per_night_krw"]
        line = f"숙박: {lodge['name']} × {nights}박"
        if per_night is None:
            tbd.append((line, "박당 ?원", None))
        else:
            confirmed.append((line, per_night * nights))

    # 일별 고정비
    pax = options["trip_pax"]
    for daily in scenario.get("fixed_days", []):
        df = find(options["daily_fixed"], daily["daily_fixed"])
        days = daily["days"]
        per = df["krw_per_pax_per_day"]
        line = f"고정비: {df['label']} × {pax}인 × {days}일"
        if per is None:
            tbd.append((line, "1인1일 ?원", None))
        else:
            confirmed.append((line, per * pax * days))

    # 일회성
    for ot_id in scenario.get("one_time", []):
        ot = find(options["one_time"], ot_id)
        line = f"일회성: {ot['label']}"
        if ot["krw"] is None:
            tbd.append((line, "?원", None))
        else:
            confirmed.append((line, ot["krw"]))

    return confirmed, tbd


def render_scenario(scn, options, cap):
    confirmed, tbd = evaluate(scn, options)
    print(f"━━ [{scn['id']}] {scn['label']} ━━")
    for label, amt in confirmed:
        print(f"  ✓ {label:<55}{fmt_won(amt)}")
    confirmed_total = sum(a for _, a in confirmed)
    print(f"  {'─' * 75}")
    print(f"  {'확정 소계':<57}{fmt_won(confirmed_total)}")

    headroom = cap - confirmed_total
    if headroom < 0:
        print(f"  ❌ 확정만으로 이미 3M 초과: {fmt_won(-headroom)} (TBD 채우기 전부터 불가)")
    else:
        print(f"  ✅ 확정 후 남은 여유: {fmt_won(headroom)} (이 안에서 TBD를 모두 채워야 함)")

    if tbd:
        print(f"  미확정 (TBD) 항목 {len(tbd)}개:")
        for label, hint, _ in tbd:
            print(f"    · {label:<55}{hint:>15}")
        if headroom >= 0:
            print(f"  → 위 {len(tbd)}개 항목 합계가 {fmt_won(headroom)} 이하이면 3M 통과")
    else:
        print(f"  TBD 없음 — 확정 합계 = 최종 비용")

    print()


def main() -> int:
    options = json.loads(DATA.read_text(encoding="utf-8"))
    cap = options["budget_cap_krw"]
    pax = options["trip_pax"]

    print(f"예산 상한: {fmt_won(cap)}  ·  여행자 수: {pax}명")
    print(f"카탈로그: 항공 {len(options['flights'])} / 숙박 {len(options['lodging'])} / "
          f"일별고정 {len(options['daily_fixed'])} / 일회성 {len(options['one_time'])} / "
          f"시나리오 {len(options['scenarios'])}")
    print()

    for scn in options["scenarios"]:
        render_scenario(scn, options, cap)

    return 0


if __name__ == "__main__":
    sys.exit(main())
