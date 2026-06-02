# 2026-06-02 — 교토역 회전초밥 비교·번역 페이지 추가 (大起水産 vs 寿しのむさし)

## Status

Accepted

## Context (왜)

- 6/2 저녁 회전초밥을 다이키수산으로 잡은 뒤(`2026-06-02-08`), 사용자가 **스시노 무사시(寿しのむさし) 하치조구치점**과의 비교를 요청.
- 무사시 일본어 후기 검증 결과: ① 진짜 레인 회전 ✓(1977 교토 노포·장인이 쥠), ② 타베로그 **3.42/255건**(다이키수산 3.07/89건보다 높고 표본 많음), ③ 그러나 **카운터 34석뿐(테이블 없음)·상시 줄·관광객 많음**(하치조구치). 다이키수산은 카운터 54석·¥110~·가라스마구치라 4인+시부모 동선엔 더 무난.
- 사용자 지시: **"둘 다 (말차 디저트·라멘코지·쇼핑 가이드와) 같은 패턴으로 번역 페이지 추가."** → head-to-head 비교·번역 페이지를 만들어 일정에서 연결.

## Decision (무엇)

- **`docs/kyoto-station-kaiten-sushi-translation.md` 신규** — 大起水産 vs 寿しのむさし 일본어 후기 번역·비교(한눈에 표 + 점포별 방문기 인용·번역 + がんこ 제외 사유 + 권장). `isetan-matcha-dessert`(2곳 head-to-head) 패턴 준용.
- **`build_index.py` DOC_PAGES 등록** — `viz/kaiten-sushi-review.html`(og_slug `itinerary`, tab `itinerary`).
- **일정 연결** — `data/itinerary.json` 6/2 18:00 항목에 `link`(회전초밥 비교 페이지) 추가 + note에 무사시 대안 명시. `places`에 `musashi_hachijo` 등록.
- **기본값 유지** — 일정의 18:00 1순위는 다이키수산(좌석 54석·동선·가격), 무사시는 "맛·평판 우위 대안"으로 비교 페이지에서 안내.
- **검토 후 기각**: 무사시로 교체(카운터 34석·상시 줄이 4인+시부모 폭우 저녁에 부담), 간코 재등판(터치패널·안 도는 회전).

## Consequences (그래서)

- 긍정: 가족이 6/2 저녁을 현장에서 둘 중 골라잡을 수 있도록 근거(번역·평점·좌석·동선) 제공. 기존 후기 페이지 패턴 일관.
- 부정·트레이드오프: 회전초밥 비교 페이지가 늘며 유지 대상 +1. 두 곳 모두 카운터석·역 안 관광지대라 "현지 숨은 맛집"은 아님(페이지에 명시).
- 영향 받은 파일: `docs/kyoto-station-kaiten-sushi-translation.md`(신규), `scripts/build_index.py`(DOC_PAGES), `data/itinerary.json`(places `musashi_hachijo`·6/2 18:00 link·note), `docs/kyoto-itinerary-may31-jun3-2026.md`(§1.3 링크), `CLAUDE.md`(트리·DOC_PAGES 카운트 25/26 정정), `README.md`.

## Test plan

- [x] `validate.py` 0 errors
- [x] `build_index.py` 빌드 + `--check` 재현성 통과 (viz/kaiten-sushi-review.html 생성)
- [x] `unittest` 223/223 PASS
