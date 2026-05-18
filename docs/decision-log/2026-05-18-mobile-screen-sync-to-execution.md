# 2026-05-18 — 모바일 8섹션 카드 메시지를 실행 모드로 동기화

## 배경

PR #31에서 CLAUDE.md·README.md를 "교토 5/31~6/3 4인 가족 여행 실행·운영 공간"으로 재정의했으나, **모바일 8섹션 카드(`index.html`)는 의사결정 시점의 어휘를 유지**하고 있었다. 헤더는 "일본 여행 최종 결정 / 교토 5/31~6/3 시나리오", §airbnb는 "5개 후보", §score는 "후보지 종합 점수" 등 결정 진행형 표현.

PR #31 머지 직후 후속 PR로 정적 문자열만 동기화한다. 데이터·뷰 3종(`viz/*.html` 빌드 소스의 정적 문자열)은 손대지 않아 다른 세션의 진행 PR과 충돌이 없다.

## 변경

`scripts/build_index.py` 정적 문자열 4곳:

| 위치 | before | after |
|---|---|---|
| `INDEX_HEAD` h1 | `일본 여행 최종 결정` | `교토 5/31~6/3 실행 (4인)` |
| `INDEX_HEAD` status | `교토 5/31~6/3 · 시부모 4인 확정` | `2026-05-12 의사결정 종료 · 발권·예약·일정 갱신 공간` |
| `card_score` h2 | `후보지 종합 점수` | `후보지 평가 점수 (아카이브 · 의사결정 종료)` |
| `card_score` sub | `교토만 7기준 모두 입력. 나머지는 seasonality(2026-05)만.` | `MCDA 2026-05-12 종료. 교토 7기준 입력, 나머지는 seasonality(2026-05)만. 회귀 가드용.` |
| `build_index` doc title | `일본 여행 최종 결정` | `교토 5/31~6/3 실행 (4인)` |

`python scripts/build_index.py` 실행으로 `index.html`도 함께 재빌드.

> §airbnb 카드는 PR #27 IA 개편에서 이미 시오(Shio) 단일 카드 + "확정" 배지로 재작성됨 → 본 PR에서는 손대지 않음. PR #27 머지 후 rebase 시 §airbnb 충돌은 PR #27 버전을 채택.

## 산출물

- `scripts/build_index.py` (정적 문자열 5개)
- `index.html` (재빌드 산출)
- 본 일지

## 핵심 관찰

- `viz/itinerary.html`·`viz/itinerary-table.html`·`viz/checklist.html`·`viz/lodging.html`은 이미 실행 어휘 — 손대지 않음. 빌드 차이는 5개 산출물 중 `index.html`에만 발생.
- §airbnb는 PR #27(IA 개편)에서 이미 실행 모드로 재작성되어 본 PR이 손댈 필요 없음. 본 PR이 PR #27 머지 후 만들어진 것이 아니라 그 전에 만들어져 rebase 시 충돌 → PR #27 버전 채택.
- `tests/test_build_index.py`는 section_id만 검사하고 h2 문자열 어서션은 없음 → 무영향.
- `scripts/validate.py` (B·C·D·E·F·G) → 데이터·SYNC 미변경, 무영향.
- 데이터(`data/*.json`) 변경 없음 → 다른 세션의 발권/일정 PR과 충돌 없음.
- 52 tests OK · validate 0 errors · build_index --check 통과.

## 다음 단계

- 본 PR 머지 후 추가 실행 트랙(`docs/checklist.md`·`docs/local-info.md`·`data/bookings.json`)은 별도 PR로 분리.
