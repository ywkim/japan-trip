#!/usr/bin/env python3
"""일본 여행 후보지 종합 점수 계산.

data/decision.json을 읽어 각 후보의 가중평균 점수를 계산하고
순위와 함께 출력한다.
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "decision.json"


def main() -> int:
    decision = json.loads(DATA.read_text(encoding="utf-8"))
    criteria = decision["criteria"]
    candidates = decision["candidates"]

    weight_sum = sum(c["weight"] for c in criteria)
    if abs(weight_sum - 1.0) > 0.001:
        print(f"⚠️  가중치 합계가 1.0이 아닙니다: {weight_sum:.3f}", file=sys.stderr)

    results = []
    for cand in candidates:
        scores = cand.get("scores", {})
        if not scores:
            results.append((cand["name"], None, "점수 미입력"))
            continue
        total = 0.0
        used_weight = 0.0
        for crit in criteria:
            cid = crit["id"]
            if cid in scores and scores[cid] is not None:
                total += scores[cid] * crit["weight"]
                used_weight += crit["weight"]
        if used_weight == 0:
            results.append((cand["name"], None, "유효 점수 없음"))
        else:
            normalized = total / used_weight
            results.append((cand["name"], normalized, f"적용 가중치 {used_weight:.2f}"))

    scored = [r for r in results if r[1] is not None]
    unscored = [r for r in results if r[1] is None]
    scored.sort(key=lambda x: -x[1])

    print(f"{'순위':<4} {'후보':<20} {'점수':>6}  비고")
    print("-" * 60)
    for i, (name, score, note) in enumerate(scored, 1):
        print(f"{i:<4} {name:<20} {score:>6.2f}  {note}")
    for name, _, note in unscored:
        print(f"{'-':<4} {name:<20} {'N/A':>6}  {note}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
