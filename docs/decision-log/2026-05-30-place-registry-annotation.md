# 2026-05-30 — 장소명 병기 단일 출처(레지스트리) + CI 게이트 강제

## Status

Accepted

## Context (왜)

- 모바일 일정 앱(viz/itinerary.html)에서 장소명 한자 병기(예: `교토역(京都駅)`)가
  **같은 문서 안에서 일관되지 않았다.** 실제 배포 화면 검수 결과:
  - `니시키 시장`·`우메코지`·`후시미` — 한자 병기가 **어디에도 없음**
  - `교토역` — 병기 6회 / 무병기 **10회** (절반 이상 생 장소명)
  - `가와라마치`·`텐류지`·`금각사`·`료안지`·`아라시야마`·`토후쿠지`·`키요미즈데라` — 곳곳 불일치
- 근본 원인: 같은 장소가 `note`·`food_quality.note`·`pass_recommendation`·
  `arrive_from.route` 등 **자유 텍스트에 occurrence마다 별개 문자열로 손으로**
  적혀 있었다. 단일 출처가 없으니 병기는 occurrence별 수기 관리 → 드리프트 필연.
- 이전 시도(Work 4 Phase B)는 `title`·`arrive_from`만 구조화했을 뿐, 화면에
  보이는 장소명 대부분이 사는 산문 필드는 손대지 않아 문제가 남아 있었다.
- 직전 작업에서 "렌더링 검증했다"고 했으나 실제로는 title 1건 grep에 불과했다.
  완전성·일관성을 기계적으로 보증하는 장치가 없던 것이 메타 실패의 핵심이었다.

## Decision (무엇)

- **장소명 ko/ja 병기의 단일 출처로 `data/itinerary.json`에 `places` 레지스트리**를
  도입한다. 각 장소는 `{"ko": "교토역", "ja": "京都駅"}` 1줄로 정의.
- 산문 필드는 `{{place_id}}`로 **참조**하고, `scripts/build_index.py`가 빌드 시
  `expand_place_refs()`로 `ko(ja)` 병기로 확장한다(`expand_refs_in_obj` 재귀 적용).
  같은 장소가 문서 전체에서 동일하게 병기된다.
- **CI 게이트(검사 K)를 `scripts/validate.py`에 추가**해 강제한다:
  - (K1) `{{place_id}}` 참조가 `places`에 정의돼 있어야 함 (미정의 → 머지 차단)
  - (K2) 레지스트리 장소의 ko명이 참조도 `ko(漢字)` 병기도 없이 산문에 '생으로'
    나타나면 머지 차단 — `금각사도(金閣寺道)` 같은 병기된 합성어는 lookahead로 통과
- 역명 합성어(`아라시야마역(嵐山駅)` 등)는 참조 대신 **리터럴 병기**로 둔다
  (`{{arashiyama}}역`은 한자 위치가 어색해지므로). 검사 K는 둘 다 허용.
- 채택하지 않은 대안:
  - 수기로 ~30곳 병기 채우기 → 드리프트를 만든 그 방식의 반복이라 기각
  - 정규식으로 산문 장소명 NLP 파싱 → false positive/negative 과다(감사 스크립트가
    `니시키`를 놓친 사례)로 신뢰 불가, 기각

## Consequences (그래서)

- 긍정:
  - 병기가 레지스트리 1곳에서 렌더 → 문서 전체 일관. 신규 occurrence도 참조만 하면 됨
  - 검사 K가 누락을 **기계적으로 차단** — "grep 1건"식 가짜 검증 불가능해짐
  - 21개 드리프트 지점을 전수 교정(5/31~6/3 note·food·pass·route)
- 부정·트레이드오프:
  - `{{ref}}`가 기존 괄호 안에 오면 중첩 괄호(`(니조역(二条駅) 도보 5분)`)가 생길 수
    있어 일부 문장은 rephrase로 회피했다
  - 레지스트리는 등록된 장소만 강제 — 미등록 약어는 미검출. 신규 장소는 레지스트리에
    1줄 추가 필요(README·CLAUDE.md에 명시)
- 후속 행동:
  - 구스키마 `route` 문자열은 Phase B steps로 점진 이관 예정(별도 작업). 이관 시
    from/to의 ko/ja 구조화로 route 내 장소명도 레지스트리화 가능
  - `docs/kyoto-itinerary-may31-jun3-2026.md`(사람용 사본)의 병기 동기화는 후속
- 영향 받은 파일·데이터:
  - `data/itinerary.json` — `places` 레지스트리 신설 + 산문 21곳 참조/병기 교정
  - `scripts/build_index.py` — `PLACE_REGISTRY`·`expand_place_refs`·`expand_refs_in_obj`
    + `load_data`에서 적재·확장
  - `scripts/validate.py` — 검사 K(`check_place_registry`) 추가
  - `tests/test_validate.py`·`tests/test_build_index.py` — K·확장 회귀 테스트 8건
