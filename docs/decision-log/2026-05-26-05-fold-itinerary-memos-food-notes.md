# 2026-05-26 — 일정 탭 fold 확장: 긴 장소 메모·맛집 상세 노트 접기

## Status

Accepted

## Context (왜)

- 같은 날 일지 `2026-05-26-04`로 checklist·lodging에 fold를 확장해 "모든 화면 접기"를 진행 중이었으나, **일정 탭(itinerary·itinerary-table)은 이동 경로(`transit_line`)·교통패스(`pass_block`)·ICOCA 플레이북만 접혀 있고** 각 장소의 메모(`note`)와 맛집 상세 노트(`food_quality.note`)는 항상 펼쳐진 장문으로 남아 있었다(PR #45가 transit/pass만 다룸).
- 실제 산출물 스캔 결과 50~180자 메모가 다수(예: MACCHA HOUSE 135자, 사이호지 182자, 中華 大鵬 맛집 노트 102자)였고, 모바일 카드를 압도했다.
- 사용자 지시: "나머지 예를 들어 일정 탭은?" → 일정 카드·시간표에도 fold 확장. 단 일정 메모는 "여행 중 보고 싶은 본문"이라 접는 범위를 사용자 확인(택1: **긴 메모 + 맛집 상세 접기, 평점·첫 문장은 유지**).

## Decision (무엇)

- `scripts/build_index.py`에 `memo_block(note, *, style, cls)` + `_lead_split(text)` 추가:
  - 50자 이하 → 기존 평문(`<div class="{cls}">`) 유지.
  - 50자 초과 → 첫 문장(`". "`) 또는 첫 토막(`" · "`, 단 60자 미만일 때만)을 요약으로, 나머지를 `<details class="leg">`로 접음. 구분자가 없으면 `상세 보기` 요약으로 통째 접기(정보 손실 없음).
  - note_block(예약 메모의 `·` 2항목 요약)과 달리 **문장 단위 요약** — 일정 메모에 자연스러움.
- 적용: 일정 카드(`build_itinerary`)·route_candidates·시간표(`build_itinerary_table`) 데스크탑 td(`t-note`)·모바일 카드의 `note`, 그리고 공용 `food_quality_html`의 `note`.
- **맛집 평점 줄(`🍽️ 타베로그 3.x · 출처: …`)은 접지 않고 항상 노출** — 식당 검증 신호 유지(food_quality 무결성 규칙과 정합).
- 기각: (a) note_block 재사용 — `·` 없는 문장형 메모는 `상세 보기`로 전부 숨겨 첫 토막 미노출, (b) 메모 전체 접기 — 본문 과다 은닉, (c) 일정 탭 미적용 — "모든 화면" 미완.

## Consequences (그래서)

- 긍정: 일정 카드가 시간·장소·이동요약·평점·메모 첫 문장만 먼저 보여 모바일 스캔성↑. 상세 팁·맛집 설명은 탭으로 펼침. 6개 산출물 전부 동일 fold 패턴 완료.
- 부정·트레이드오프: 긴 메모 전문 확인에 탭 1회. 50자/60자 임계값은 휴리스틱. 데스크탑 시간표 td의 `t-note`도 짧으면 `<div class="t-note">`(이전 `<span>`)로 바뀜 — 표시상 차이 미미.
- 후속: 신규 메모·맛집 노트는 데이터만 추가하면 자동 적용. index(운영 모드)는 일정 메모를 임베드하되 food_quality는 미노출 — 변경 영향 없음.
- 영향 파일: `scripts/build_index.py`(`memo_block`·`_lead_split` 신규, `food_quality_html`·`build_itinerary`·`build_itinerary_table`), `tests/test_build_index.py`(`ItineraryMemoFoldTests` 신규 7건), 재빌드 `viz/itinerary.html`·`viz/itinerary-table.html`, `README.md`, `CLAUDE.md`.

## Test plan

- [x] `python -m unittest discover -s tests` → 116개 통과(신규 `ItineraryMemoFoldTests` 7건 포함)
- [x] `python scripts/build_index.py --check` → All outputs in sync
- [x] `python scripts/validate.py` → 0 errors, 0 warnings
- [ ] 모바일 폭에서 viz/itinerary.html·itinerary-table.html 육안 확인 (긴 메모·맛집 노트 접힘, 평점·짧은 메모 노출)
