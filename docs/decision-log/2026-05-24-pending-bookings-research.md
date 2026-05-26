# 2026-05-24 — 미정 예약 4항목 실시간 리서치 + 하루카 운임 정합화

## Status

Accepted

## Context (왜)

- 오늘 2026-05-24 기준 `data/booking-checklist.json` 7항목 중 4항목이 `미정`이고 마감이 임박: 여행자보험·교통패스(발권)·5/25, eSIM·환전/트래블카드·5/28.
- 항공·숙박(에어비앤비 시오·카덴쇼)은 이미 `확정`. 남은 미정 항목은 마감 전 발권/가입이 필요하나, 현재가·발권 채널 정보가 노트에 정리돼 있지 않았다.
- CLAUDE.md 강제 규칙: 가격·운임은 실시간 리서치(WebSearch/WebFetch)로만 입력, `source`+`data_quality`+검색일자 필수, 기억 기반 추측 금지.
- 리서치 중 내부 불일치 발견: `data/cost-options.json`의 `haruka_rt_4pax`가 ¥2,400×4×2=₩192,000("JR 공식")으로, 2026-05-19 채택 결정(하루카 외국인 할인 편도 ¥2,200/인)·`booking-checklist.json` transit_pass 노트(₩167K)와 어긋나 있었다.
- 본 작업은 발권·결제 자체(사용자만 가능)가 아니라, 사용자가 마감 전 즉시 발권할 수 있도록 리서치·권장안·채널을 정리하는 범위다.

## Decision (무엇)

- 미정 4항목을 실시간 리서치(2026-05-24)하여 `docs/booking-research-2026-05-24.md`에 비교표·권장안·발권 채널·출처·`data_quality`로 정리하고, `data/booking-checklist.json` 4항목 `note`에 요약 권장 + 문서 링크를 추가한다. **status는 `미정` 유지** — 실제 결제 전이며 임의 `확정` 처리는 출처 없는 입력 금지 원칙 위반.
- `data/cost-options.json`의 `haruka_rt_4pax`를 채택 운임(¥2,200/인 × 4 × 2 = ₩167,200, `official_fare`, japan-guide.com 2026-05-24 교차검증)으로 정합화하여 단일출처 불일치를 해소한다.
- 채택하지 않은 대안:
  - eSIM·여행자보험을 `cost-options.json` 예산 시나리오에 신규 항목으로 추가 — 예산 시나리오는 아카이브 비교 모델이라 개인별 부대비용 추가는 범위 밖. 필요 시 별도 PR.
  - status를 `예약중`으로 변경 — 실제 발권 진행 상태가 아니므로 부정확.

## Consequences (그래서)

- 긍정: 마감 임박 4항목이 출처·`data_quality` 라벨이 붙은 현재 시세 + 명확한 발권 채널·절차로 정리되어 사용자가 5/25·5/28 마감 전 즉시 결제 가능. 하루카 운임 단일출처 불일치 해소(budget 총액 ₩24,800 감소).
- 부정·트레이드오프: 가격은 모두 `researched_market_rate`(보험·eSIM·카드)로 실제 결제가와 다를 수 있음. 정확 보험료는 시부모 실제 생년 입력 후 산출 필요.
- 후속 행동: 사용자 결제 시 해당 항목 `확정`(`reference`·`confirmed_at`·`confirmed_booking`) 승격 + `cost-options.json` 반영 + 확정 일지. eSIM·보험의 예산 모델 포함은 별도 PR.
- 영향 받은 파일·데이터:
  - 신규: `docs/booking-research-2026-05-24.md`, `docs/decision-log/2026-05-24-pending-bookings-research.md`
  - 수정: `data/booking-checklist.json`(insurance·transit_pass·esim·fx note), `data/cost-options.json`(haruka_rt_4pax), `README.md`, `CLAUDE.md`
  - 빌드 산출물 재생성: `index.html`, `viz/checklist.html`
