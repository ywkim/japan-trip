# 2026-05-30 — 첫날(5/31) enen 저녁 예약 준비(채널·파라미터) 정비

## Status

Accepted

## Context (왜)

- 사용자 지시: "예약 원하면 첫째날 저녁 할 수 있게 준비만." → 예약을 **대행하지 말고**, 사용자가 원할 때 바로 실행할 수 있도록 채널·필요 정보만 정비.
- 5/31 저녁은 폰토초 enen 야끼니꾸로 확정(`2026-05-30-day1-dinner-enen-yakiniku.md`). 인기점이라 사전 예약이 사실상 필요.
- 리서치(2026-05-30, WebSearch 교차 확인): 전화 075-286-7479(owst 공식·gnavi·hotpepper 일치), 영어 즉시예약 가능 — Tabelog EN(영어 메뉴·응대, 가입 불필요 즉시예약)·Hot Pepper(24시간 넷예약). 영어 메뉴·영어 응대 가능.

## Decision (무엇)

- 5/31 enen 항목에 **예약 실행에 필요한 모든 정보**를 정비(실행은 보류, 사용자 확인 후):
  - 예약 파라미터: 5/31(일) 18:30·4인(시부모 2 포함)·테이블석 요청(고령자 좌식 부담 회피).
  - 채널: Tabelog EN(영어 즉시예약)·Hot Pepper(넷예약)·전화 075-286-7479(일본어). `note`에 tel/markdown 링크로 탭 가능하게, `link` 필드에 Tabelog EN 예약 CTA 추가.
  - 사람용 사본·핸드오프 노트 동기화.
- 대안: ① 예약을 직접 대행 — 사용자가 "준비만" 요청했고 개인정보·결제·외부 사이트 행위라 보류. ② `booking-checklist.json`에 항목 추가 — 그 체크리스트는 숙박·교통 등 7개 예약 상태 전용이라 식당 예약은 운영 화면(itinerary 항목)에 두는 것이 스코프에 맞음 — 기각.

## Consequences (그래서)

- 긍정: 운영 화면(viz/itinerary)·사람용 사본에서 예약 채널을 바로 탭해 실행 가능. 영어 채널 우선이라 언어 장벽 최소.
- 부정·트레이드오프: 예약 미실행 상태 — 인기점 특성상 가까운 날짜에 자리 확보 필요. note에 "실행은 사용자 확인 후" 명시. 전화는 일본어 필요(영어 채널로 회피 가능).
- 후속 행동: 사용자가 예약 실행을 지시하면 채널 선택 후 예약번호·시간을 항목에 반영하고 일지 추가.
- 영향 받은 파일: `data/itinerary.json`(5/31 enen note·link·핸드오프 노트), `docs/kyoto-itinerary-may31-jun3-2026.md`.

## Test plan

- [ ] `uv run python scripts/validate.py` — 검사 G·I·J·K·L 통과(링크·노트·place ref)
- [ ] `uv run python scripts/build_index.py` — 빌드 무오류(예약 링크·tel 렌더, GitHub 링크 0)
- [ ] `uv run python -m unittest discover -s tests` — 회귀 가드 통과
