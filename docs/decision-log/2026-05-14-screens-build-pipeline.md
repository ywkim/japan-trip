# 2026-05-14 — 화면·빌드 파이프라인 일원화 (대시보드 제거 + 신규 화면 2종 + 단일 출처 보강)

## 주제

`viz/dashboard.html` (MCDA 가중치 슬라이더)을 제거하고, `scripts/build_index.py`를 단일 빌드 파이프라인으로 확장하여 `index.html`·`viz/itinerary.html`·`viz/checklist.html` 3개 정적 HTML을 모두 `data/*.json`에서 생성하도록 일원화.

## 배경

- 의사결정이 교토 5/31~6/3 + 시오 + 카덴쇼로 확정되어 가중치 민감도 분석은 회귀 가드용으로만 필요. 대시보드는 manual sync 부채만 발생시키는 무용 화면이 됨.
- 1차 batch (PR #19/#20/#21)에서 신규 화면 2종을 추가했으나 각각 인라인 데이터 + manual sync 구조라 같은 sync debt 패턴 재발. `build_index.py`는 내부 하드코드 `ITINERARY` 리스트로 일정 카드를 만들어 사실상 4중 출처 (`build_index.py` 하드코드 / `data/itinerary.json` / `docs/kyoto-itinerary-may31-jun3-2026.md` / `viz/itinerary.html` 인라인)였음.
- 소연 리뷰 전에 부실한 4 PR을 머지하지 않고 1개 통합 PR로 재구성 (사용자 결정).

## 산출물

- **삭제**: `viz/dashboard.html` (331 lines)
- **신규**: `data/itinerary.json` — 교토 3박4일 일정 단일 출처 (일자×시간대×동선×메모×도보거리×보류, hour-level 평탄화 스키마)
- **신규**: `viz/itinerary.html` — `build_index.py` 산출물. `data/itinerary.json`을 인라인 임베드한 standalone HTML (외부 fetch 없음, 더블클릭 동작)
- **신규**: `viz/checklist.html` — `build_index.py` 산출물. `data/booking-checklist.json`을 인라인 임베드, 기한 이른 순 정렬 + 상태별 카운트 요약
- **리팩터**: `scripts/build_index.py` — 내부 하드코드 `ITINERARY` 제거. 3개 산출물을 모두 `data/*.json`에서 생성. `--check` 모드가 3개 모두 검사
- **테스트 확장**: `tests/test_build_index.py` — `viz/itinerary.html`·`viz/checklist.html` drift 검출 + 외부 fetch 부재 + SYNC 주석 회귀 가드 (24→26 tests)
- **정리**: `README.md` (대시보드 안내 제거 → 신규 화면 2종 안내 + `viz/`는 빌드 산출물 명시), `CLAUDE.md` (작성 규칙·MCDA 워크플로우·디렉토리 트리·데이터 동기화 규칙·CI 검증 표 5개 섹션), `.github/PULL_REQUEST_TEMPLATE.md` (scope 예시·체크리스트), `docs/jejuair-icn-kobe-june-2026.md` §5.4 (dashboard.html 잔존 참조 + 후속 메모)

## 합의

- **단일 출처 = 빌드 = 뷰**: 모든 화면 데이터는 `data/*.json`이 정본이며 `build_index.py`만 산출물을 생성. 인라인 사본은 빌드 결과의 부산물이지 수동 동기화 대상이 아님
- `build_index.py --check` 하나가 3개 산출물의 drift를 모두 차단 → 별도 G/H 게이트 불필요
- 5/24~27 구버전 일정(`docs/kyoto-itinerary-may-2026.md`)·탐색기 비교표(`docs/candidates.md`)는 의도적으로 유지 (역사적 기록)
- `MCDA` 용어는 방법론 자체 명칭이므로 `CLAUDE.md`의 워크플로우 섹션 제목에 유지하되 "확정 이후 회귀 가드용" 단서 추가

## 보류·후속

- `scripts/validate.py`의 `docs/weather.md`·`docs/flights.md` ↔ JSON 동기화 게이트 (E·F)는 별도 PR로 진행 중 (구조적으로 독립)
- `reports/final-report.md:60`의 "MCDA 비교 종료 시점 결정" 라인은 의사결정 히스토리이므로 그대로 유지
- 1차 batch의 PR #19·#20·#21은 본 PR로 대체되어 close 예정

## 핵심 관찰

1. 대시보드를 단순히 삭제하면 단일 출처 문제가 풀리지 않는다. 신규 화면이 같은 manual sync 패턴을 재현하면 부채 위치만 옮기는 셈
2. "단일 출처" 라벨만 붙이는 것과 "단일 출처에서 모든 view가 빌드되는 구조"는 다르다. 후자만 CI 게이트로 자동 보장 가능
3. `build_index.py` 내부의 하드코드된 `ITINERARY`는 외부 JSON과 내용이 거의 같았지만 별도 출처로 존재했음 — 코드 안의 데이터도 동일한 sync debt 원인
4. 의사결정이 확정된 후에는 화면이 "분석 도구"가 아닌 "참조 도구"로 변한다. 인터랙티브 슬라이더보다 빠른 정적 카드가 사용성이 좋음
5. 4개 사이드-바이-사이드 PR보다 1개 구조적 PR이 리뷰·머지·재작업 모든 측면에서 비용이 낮다 — sync debt 같은 cross-cutting 변경은 통합이 자연스럽다
