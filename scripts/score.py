#!/usr/bin/env python3
"""일본 여행 후보지 종합 점수 계산.

data/decision.json을 읽어 각 후보의 가중평균 점수를 계산하고
순위와 함께 출력한다.
"""

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "decision.json"


def compute():
    decision = json.loads(DATA.read_text(encoding="utf-8"))
    criteria = decision["criteria"]
    candidates = decision["candidates"]

    weight_sum = sum(c["weight"] for c in criteria)
    weight_warning = None
    if abs(weight_sum - 1.0) > 0.001:
        weight_warning = f"가중치 합계가 1.0이 아닙니다: {weight_sum:.3f}"

    results = []
    for cand in candidates:
        scores = cand.get("scores", {})
        if not scores:
            results.append({"id": cand["id"], "name": cand["name"], "score": None, "used_weight": 0.0, "note": "점수 미입력"})
            continue
        total = 0.0
        used_weight = 0.0
        for crit in criteria:
            cid = crit["id"]
            if cid in scores and scores[cid] is not None:
                total += scores[cid] * crit["weight"]
                used_weight += crit["weight"]
        if used_weight == 0:
            results.append({"id": cand["id"], "name": cand["name"], "score": None, "used_weight": 0.0, "note": "유효 점수 없음"})
        else:
            normalized = total / used_weight
            results.append({"id": cand["id"], "name": cand["name"], "score": round(normalized, 2), "used_weight": round(used_weight, 2), "note": f"적용 가중치 {used_weight:.2f}"})

    scored = [r for r in results if r["score"] is not None]
    unscored = [r for r in results if r["score"] is None]
    scored.sort(key=lambda x: -x["score"])
    return {"weight_warning": weight_warning, "scored": scored, "unscored": unscored}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="JSON 출력 (build_index.py용)")
    args = parser.parse_args()

    res = compute()
    if args.json:
        json.dump(res, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    if res["weight_warning"]:
        print(f"⚠️  {res['weight_warning']}", file=sys.stderr)
    print(f"{'순위':<4} {'후보':<20} {'점수':>6}  비고")
    print("-" * 60)
    for i, r in enumerate(res["scored"], 1):
        print(f"{i:<4} {r['name']:<20} {r['score']:>6.2f}  {r['note']}")
    for r in res["unscored"]:
        print(f"{'-':<4} {r['name']:<20} {'N/A':>6}  {r['note']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
