# 2026-05-09 — 3M 예산 하드캡 정책 + 비용 비교 도구 도입

- 합의: **₩3,000,000 (4인 합계) 을 하드캡** — 어느 도시·기간이든 초과 불가
- 합의: 비용 계산은 MCDA 가중치(0.20)와 별개의 **선행 필터**로 작동
  - 3M 통과 시나리오만 MCDA 평가 후보로 인정
- 합의: 단가 입력은 `data_quality` 라벨로 구분
  - `confirmed_booking` / `official_fare` / `researched_market_rate`
  - 추측치 입력 금지
- 도입: `data/cost-options.json` (카탈로그) + `scripts/budget.py` (평가)
