# 2026-05-30 — arrive_from from/to 병기를 places 레지스트리 참조로 전환 (Work 4.1)

## Status

Accepted

## Context (왜)

- Work 4 스키마 마이그레이션(`scripts/migrate_schema.py`)이 `arrive_from.route` 문자열을
  정규식으로 파싱해 `steps[].from`·`to`를 `{ko, ja}` dict로 생성했으나, **26개 transit leg
  중 7개가 오염**됐다:
  - `¥230`·`206`·`케이한`을 도착지로 (요금·노선번호·회사명을 장소로 오인)
  - `으로 니조역`(조사 혼입)·`/아라시야마`·`'코케데라`(구두점 혼입)
  - `{{kadensho}}/{{kyoto_station}}` 미확장, 다수 `ja` 빈 문자열
- 게다가 `render_transit_line_steps()`가 `from["ko"]`만 출력하고 `ja`를 무시 →
  화면에 역·정류장 한자 병기가 아예 나오지 않음(가족 공유 페이지 스크린샷에서
  "니조역 → 교토역"처럼 병기 누락 확인).
- 근본 원인: from/to가 **구조화 dict라 `places` 레지스트리 확장(`expand_refs_in_obj`)과
  검사 K 대상에서 제외**되어, 사찰·지역명과 달리 병기 드리프트·오염이 구조적으로 방치됨.
- 대안: ① 각 from/to에 깨끗한 `{ko, ja}`를 inline으로 수기 입력(자족적이나 같은 역이
  인접 leg에 중복 입력되어 드리프트 여지) — 기각. ② 레지스트리 참조 단일 출처(채택).

## Decision (무엇)

- 모든 교통 노드(역·버스정류장·환승점)를 `data/itinerary.json` 최상위 `places`
  레지스트리에 1회 등록하고, `arrive_from.steps[].from`·`to`는 **`"{{place_id}}"` 단일
  참조 문자열**로 작성한다. 로드 시 `expand_refs_in_obj`가 `ko(ja)`로 자동 확장 → 별도
  해석 코드 불필요. (신규 11개 노드: `sagaarashiyama_station`·`inari_station`·
  `tofukuji_station`·`arashiyama_tenryuji_stop`·`kokedera_stop`·`kinkakujimichi_stop`·
  `ryoanjimae_stop`·`shijo_kawaramachi_stop`·`gion_shijo_stop`·`gojozaka_stop`·
  `yamagoe_nakamachi_stop`)
- 알려진 환승 2건(금각사 시버스 11→59 @야마고에나카마치, 후시미이나리 산인본선→나라선
  @교토역)은 `steps`를 2개로 분리해 모델링 → `render_transit_line_steps()`가 step 사이에
  "↓ 환승 ↓"를 자동 삽입.
- 운행 경고·대안은 소실된 `route` 문자열 정규식 추출 대신 `arrive_from.advisory`
  (선택 문자열)에 적고 ⚠️로 렌더. Stage 5의 route 정규식 경고 추출 로직 폐기.
- `scripts/build_index.py`: `render_transit_line_steps()`가 from/to를 확장된 문자열로 직접
  사용(`_station_label` 헬퍼, 구 dict 안전망 포함). `.get("ko")` 제거.
- `scripts/validate.py`: `_iter_prose_fields`에 from/to 문자열 포함(검사 K1이 미정의 참조
  커버) + **신규 검사 L**(from/to는 `^{{place_id}}$` 형식 & 레지스트리 정의 강제,
  inline dict·요금·노선번호·생문자열 차단).
- `scripts/migrate_schema.py`: 오염 원천이던 from/to 정규식 파서(`extract_station_from_text`
  및 from/to 추출 블록) 제거. 마이그레이션은 mode/duration/distance/fare/operator/
  number/line만 생성하고 from/to는 데이터에서 ref로 수기 작성.

## Consequences (그래서)

- **긍정**: 교통 노드 병기가 사찰과 동일한 단일 출처 메커니즘으로 통일 → 드리프트 불가.
  화면에 역·정류장 한자 병기 표시("니조역(二条駅) → 교토역(京都駅)"). 환승 2건 시각화.
  검사 L이 오염·회귀를 머지 단계에서 차단.
- **부정·트레이드오프**: `places`에 ~11개 노드 추가로 검사 K2(생 장소명) 스캔 대상 증가 —
  산문에 생 노드명이 있으면 신규 실패 가능(이번 작업에선 미발생, 빌드·검증으로 확인).
  from/to가 dict→문자열로 ko/ja 분리는 잃지만 렌더는 항상 병기라 무관.
- **후속**: 향후 leg 추가 시 노드를 `places`에 1줄 등록 후 `{{ref}}`로 참조.
- **영향 파일**: `data/itinerary.json`, `scripts/build_index.py`, `scripts/validate.py`,
  `scripts/migrate_schema.py`, `tests/test_build_index.py`·`test_validate.py`·
  `test_migrate_schema.py`, `CLAUDE.md`.
