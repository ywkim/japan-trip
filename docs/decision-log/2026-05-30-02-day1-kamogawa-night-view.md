# 2026-05-30 — 첫날(5/31) 폰토초 저녁 후 가모강(鴨川) 야경 산책 추가

## Status

Accepted

## Context (왜)

- 직전 결정(`2026-05-30-day1-dinner-enen-yakiniku.md`)으로 5/31 저녁을 폰토초 enen 야끼니꾸로 변경하면서, 시오에서 도보권이 아닌 점을 "이동 부담"으로 메모했다.
- 사용자 후속 지시: "대중교통 이용할꺼야 야경 보러 폰토초 쪽 기모강(鴨川) 갈꺼니깐."
  - ① 이동 수단은 **대중교통(지하철)** 확정 — 기존 arrive_from(도자이선 二条↔三条京阪)이 의도와 일치.
  - ② 폰토초로 가는 목적이 단순 저녁이 아니라 **가모강 강변 야경**임이 드러남. 즉 cross-town 이동은 부담이 아니라 의도된 야경 코스.

## Decision (무엇)

- 5/31 저녁(enen) 뒤 20:00 항목으로 **가모강(鴨川) 강변·폰토초 야경 산책**을 추가(`data/itinerary.json` + 사람용 사본 동기화).
  - `places`에 `kamogawa`(鴨川) 등록(검사 K/L 참조용).
  - 산책 arrive_from은 enen→강변 도보 2분(~0.15km) 단일 walk leg, 정밀 동선은 `tbd_needs_browser_mcp`.
  - 복귀는 지하철 도자이선 {{sanjo_keihan_station}}→{{nijo_station}}(ICOCA) — note에 명시. day_label·체크인 메모·walking_km_source를 "야끼니꾸·가모강 야경"으로 갱신.
- 이동 수단은 대중교통으로 유지 — 직전 결정의 지하철 arrive_from을 그대로 두고 "이동 부담" 프레이밍을 야경 목적으로 갱신.

## Consequences (그래서)

- 긍정: 첫날 저녁 코스가 "이동 부담"이 아니라 폰토초 미식 + 가모강 야경으로 완결. 대중교통 동선 확정으로 택시 검토 불필요.
- 부정·트레이드오프: 도착일 야간 일정이 늘어 귀가가 늦어짐(시부모 동반) — note에 "무리 없이 짧게" 명시. 정밀 도보 동선·요금은 여전히 Playwright 후속 검증 대상.
- 후속 행동: ① 야경 산책 leg 도보 동선 브라우저 검증 ② `cost-options.json kyoto_local_transit_4pax`에 5/31 지하철 왕복 반영(별도 PR).
- 영향 받은 파일: `data/itinerary.json`(places + 5/31 항목), `docs/kyoto-itinerary-may31-jun3-2026.md`.

## Test plan

- [ ] `uv run python scripts/validate.py` — 검사 G·K·L 통과(kamogawa 참조·walk leg)
- [ ] `uv run python scripts/build_index.py` — 빌드 무오류(야경 카드 렌더)
- [ ] `uv run python -m unittest discover -s tests` — 회귀 가드 통과
