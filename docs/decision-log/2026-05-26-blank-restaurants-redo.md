# 2026-05-26 — #42 식당 픽 보류·재선정 (data 비우고 인프라는 유지)

## Status

Accepted (Partially supersedes `2026-05-24-restaurant-quality-sourcing.md` —
**구체 식당 6곳만 보류**, food_quality 스키마·검사 I·렌더링 인프라는 유지)

## Context (왜)

- PR #42(2026-05-25 머지, 5b71384)에서 6개 끼니에 `food_quality` 필드를 신설하고 구체 식당 6곳을 지정·출처화했다: 大鵬(5/31 점심)·豆八(5/31 저녁)·쇼라이안(6/1 점심)·まんざら亭(6/1 저녁)·中村商店(6/2 점심)·카덴쇼(6/2 저녁).
- 머지 직후 소연이 결정: "**식당은 다시 할테니깐 비워두자**" — #42의 구체 식당 픽은 보류, 직접 재선정 예정.
- 리뷰 시 짚었던 2건도 보류의 배경:
  - 5/31·6/1 저녁이 둘 다 폰토초(豆八 → まんざら亭) — 이틀 연속 같은 거리 분산 여부 미합의.
  - 大鵬·豆八 등 인기점 웨이팅·예약 부담이 note에만 있어 운영 리스크 미해소.
- 다만 #42가 도입한 인프라(`food_quality` 필드 스키마, `validate.py` 검사 I, `build_index.py`의 `food_quality_html()` 렌더러)는 향후 재선정 시 그대로 재사용 가능 — 코드를 다시 깔지 않는다.
- 알려진 대안:
  1. **#42 전체를 revert** — 인프라까지 함께 사라져 재선정 시 다시 구축해야 함. 채택 안 함.
  2. **그대로 두고 나중에 새 PR로 교체** — 머지된 main에 협찬·웨이팅 리스크 있는 식당 픽이 남아 다른 의사결정에 영향. 채택 안 함.
  3. **데이터(식당 6곳)만 비우고 인프라는 유지** — 머지된 인프라 보존, 데이터만 TBD 상태로 회귀. **채택**.

## Decision (무엇)

- `data/itinerary.json`의 6개 식사 항목을 #42 머지 직전 상태(commit `5b71384^1`)로 복원:
  - 5/31 12:45 점심: `니조 인근 점심 (시오 도보권)` 으로 환원, `food_quality` 제거
  - 5/31 18:30 저녁: `가와라마치 저녁 (시라카와·폰토초)` 으로 환원, `food_quality` 제거
  - 6/1 12:00 점심: 쇼라이안 제목 유지, `food_quality` 제거 (maps_query는 #42 변경 그대로)
  - 6/1 18:30 저녁: `가와라마치 + 니시키 시장 저녁` 으로 환원, `food_quality` 제거
  - 6/2 11:30 점심: `교토역 라멘코지 점심` 으로 환원, `food_quality` 제거
  - 6/2 18:00 저녁: 카덴쇼 제목 유지, `food_quality` 제거
- `docs/kyoto-itinerary-may31-jun3-2026.md`(사람용 마크다운 사본): JSON과 동일하게 복원.
- `scripts/build_index.py` 산출물(`index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`) 재빌드 — `food_quality_html()` 함수는 살아 있으나 데이터가 없어 dormant.
- `tests/test_build_index.py`의 `FoodQualityRenderTests` 클래스 제거 — production 데이터에 `food_quality` 존재를 단언하던 4개 테스트(렌더링 결과를 production data로 검증). CLAUDE.md "테스트가 production 데이터에 의존하는 케이스는 회귀 가드로만 사용. 새 규칙 검증은 tempfile 기반 fixture로 격리" 원칙에 따라, 인프라 검증은 `tests/test_validate.py`의 `FoodQualityTests`(tempfile fixture)가 이미 담당하므로 production-coupled 테스트는 정리.
- **유지(인프라)**:
  - `scripts/validate.py` 검사 I (`check_itinerary_food_quality`) — food_quality가 있는 항목에 한해 필수 필드·`data_quality` 화이트리스트·60일 staleness 검사
  - `scripts/build_index.py` `food_quality_html()` 헬퍼·CSS — 식당이 재지정되면 자동 렌더
  - `tests/test_validate.py` `FoodQualityTests` — tempfile fixture 기반 (production 데이터 비의존)
  - `CLAUDE.md`·`README.md`의 food_quality 스키마 문서 — 재선정 시 가이드로 작동
- 채택하지 않은 대안:
  - 식당 6곳 중 일부(쇼라이안·카덴쇼는 예약 이슈 없음)만 출처 유지: 일관성 위해 6곳 모두 비움 — 부분 유지는 재선정 시 혼선.

## Consequences (그래서)

**긍정**
- 머지된 운영 데이터에서 협찬 가능성·예약 부담이 있는 구체 식당 픽이 사라지고 TBD 상태로 회귀 — 다른 의사결정(시간 배분·동선)에 식당 선택이 더 이상 영향 미치지 않음.
- 인프라(검사 I + 렌더러 + 스키마 문서)는 보존 — 재선정 시 `food_quality` 객체만 추가하면 검증·렌더링 자동 작동.
- "비워두자" 결정의 시계열 근거가 ADR로 남아 후속 세션이 의도 복원 가능.

**부정·트레이드오프**
- 운영 데이터의 식사 항목이 다시 "동네 수준" 메모로 회귀 — 출국까지 6일(5/26 → 5/31) 안에 6곳 재선정 필요.
- `FoodQualityRenderTests` 제거 → 렌더링 회귀 가드 1단계 축소. 향후 재선정 PR에서 tempfile fixture 기반 렌더링 테스트를 추가하면 보강 가능.

**후속 행동**
- (시급) 소연이 6곳 재선정 — 평점·예약 가능성·동선 분산(폰토초 이틀 연속 회피) 기준 반영.
- (선택) 재선정 PR에서 `FoodQualityRenderTests`를 tempfile fixture 기반으로 재작성하여 인프라 회귀 가드 복원.

**영향 받은 파일·데이터**
- `data/itinerary.json` (6 끼니 환원)
- `docs/kyoto-itinerary-may31-jun3-2026.md` (마크다운 사본 동기화)
- `index.html`·`viz/itinerary.html`·`viz/itinerary-table.html` (재빌드)
- `tests/test_build_index.py` (`FoodQualityRenderTests` 클래스 제거)
- `docs/decision-log/2026-05-26-blank-restaurants-redo.md` (본 일지)
