# 2026-05-30 — 첫날(5/31) 저녁을 시오 인근 다이호(중식)에서 폰토초 enen 야끼니꾸로 변경

## Status

Accepted

## Context (왜)

- 사용자(소연) 지시: "첫째날 시오 근처 다이호에서 저녁이 아니라 enen 에서 야끼니꾸 먹는걸로 바꿔줘" + 구글맵 링크(`https://maps.app.goo.gl/nywudw85RDR8YWmc8`).
- 기존 5/31 18:30 저녁은 **다이호(中華 大鵬·쓰촨 중식)** — {{shio_machiya}}·{{nijo_station}} 도보권의 "이동 없는 가까운 저녁"으로 설계됨(오후 도착·시부모 피로 최소화 의도).
- 링크 해소 결과 대상 매물은 **京都焼肉 enen 先斗町本店**(중京区鍋屋町209-13, 폰토초). 한큐 교토카와라마치역·게이한 기온시조역 도보 2분으로 **시오에서 도보권이 아님** → 첫날 동선이 "인근 저녁"에서 "지하철 이동 저녁"으로 바뀐다.
- 리서치(2026-05-30): Tabelog 3.44, A5 흑모와규 창작 야끼니꾸(프렌치 터치), 일요일 디너 17:00~22:00(L.O.21:30), 1인 ¥5,000~6,000(Tabelog 예산 ¥5,000~5,999). 5/31은 일요일이라 디너 영업 정상.
  - 출처: Tabelog(en) 26034057 · enen 공식사이트(주소·영업시간·접근) · Yahoo!地図(주소 확인).

## Decision (무엇)

- 5/31 18:30 식사 항목을 **다이호 → 京都焼肉 enen 先斗町本店**으로 교체(`data/itinerary.json` 정본 + 사람용 사본 `docs/kyoto-itinerary-may31-jun3-2026.md` 동기화).
  - `food_quality`: Tabelog 3.44 · researched_market_rate · source_fetched_at 2026-05-30. 미쉐린 빕구르망 배지·전화번호 등 다이호 잔여 필드 제거.
  - `arrive_from`: 도보 단일 leg → **지하철(도자이선) {{nijo_station}}→{{sanjo_keihan_station}} + 폰토초 도보** 2-step. 정밀 노선·요금은 브라우저 검증 대기로 `tbd_needs_browser_mcp` 유지.
  - `places` 레지스트리에 `sanjo_keihan_station`(三条京阪駅) 1줄 추가(transit from/to 참조용, 검사 L).
  - day_label·체크인 메모·`walking_km_source`·`pass_recommendation`을 "인근 저녁" → "폰토초 지하철 이동 저녁"으로 갱신.
- 대안 검토: 다이호 유지(사용자 지시에 반함 — 기각). enen 다른 지점(四条河原町店 등) — 사용자 링크가 先斗町本店을 지목하므로 본점 채택.

## Consequences (그래서)

- 긍정: 사용자가 원한 야끼니꾸로 첫날 저녁 확정. 폰토초 분위기 + A5 와규.
- 부정·트레이드오프: 오후 도착·시부모 동반 첫날에 **지하철 왕복 이동이 추가**됨(기존 "도보권 가까운 저녁" 의도 약화). 도착편 지연·피로 시 부담 — 메모에 "휴식 후 출발" 명시. 요금/정밀 환승은 `tbd_needs_browser_mcp`로 후속 검증 필요.
- 후속 행동: ① `cost-options.json kyoto_local_transit_4pax`에 5/31 지하철 왕복(니조↔삼조케이한) 반영 검토(별도 PR) ② 예약 채널·시간 확정 시 일지 추가 ③ Playwright MCP 세션에서 transit leg 요금·소요 확정.
- 영향 받은 파일: `data/itinerary.json`(places + 5/31 항목), `docs/kyoto-itinerary-may31-jun3-2026.md`.

## Test plan

- [ ] `uv run python scripts/validate.py` — 검사 G·I·K·L 통과(신규 station 참조·food_quality·transit from/to)
- [ ] `uv run python scripts/build_index.py` — 빌드 무오류(저녁 카드·역 타임라인 렌더)
- [ ] `uv run python -m unittest discover -s tests` — 회귀 가드 통과
