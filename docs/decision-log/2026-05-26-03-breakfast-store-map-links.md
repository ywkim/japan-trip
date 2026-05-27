# 2026-05-26 — 조식 가게명을 모바일 탭 가능한 지도 링크로

## Status

Accepted (`2026-05-26-02-breakfast-onsite-page-no-github-link.md` 후속 — 같은 조식 페이지에 가게 지도 링크 추가)

## Context (왜)

- 사용자 지시(2026-05-26): "카페 등 모두 모바일에서 클릭 필요." `viz/breakfast.html`의 가게명이 평문이라 모바일에서 위치·길찾기로 바로 갈 수 없었다.
- 동반자(시부모·소연)는 현지에서 가게명을 보고 즉시 지도 앱으로 길찾기를 켜는 동선이 필요. 데스크톱이 아니라 모바일 운영 화면이 주 사용처.
- 제약: 좌표·place_id를 추측해 박으면 CLAUDE.md "출처 없는 데이터 금지"에 저촉. 가게별 공식 URL을 일일이 확보하기도 어렵다.

## Decision (무엇)

각 가게명을 **구글 지도 검색 링크**(`https://www.google.com/maps/search/?api=1&query=…`)로 렌더한다. 질의는 `store.map_query`가 있으면 그것을, 없으면 `가게명 + 숙소 map_area`로 생성한다.

- `data/breakfast.json`: 숙소에 `map_area`(시오 `京都 二条駅`, 카덴쇼 `京都駅`) 추가. 이름만으로 모호한 가게(스타벅스 (니조 인근))에 `map_query`(`スターバックス 二条駅 京都`) 명시.
- `scripts/build_index.py`: `maps_search_url()` + `_breakfast_store(store, map_area)`가 가게명을 `.map-link` 앵커(🗺, 새 탭)로 렌더. `.map-link` CSS는 기존 토큰(`var(--accent)`)만 참조 — 새 hex·토큰 없음(검사 H 영향 없음).
- 적용 범위: `stores`만 링크. `items`(편의점·마치야 주방·하루카 차내 등 비특정 장소)는 평문 유지.
- 미채택: (a) 좌표/place_id 매핑 — 추측 금지 규칙 위반·유지비용. (b) 가게별 공식 URL 수집 — 14곳 확보 부담·일관성 저하. (c) 타베로그 링크 — 길찾기엔 지도가 적합.

## Consequences (그래서)

- 긍정: 모바일에서 가게명 탭 → 지도 앱 길찾기. 좌표를 지어내지 않고 검색 질의만 생성해 데이터 무결성 규칙 준수. 데이터 단일 출처(`breakfast.json`)에서 링크가 파생.
- 부정·트레이드오프: 지도 검색이 동명 점포로 잘못 잡힐 가능성(→ `map_query`로 보정 가능). 외부 링크(google.com) 추가(단 GitHub 아님 → Vercel 규칙 위배 아님).
- 후속: 현지에서 핀이 틀린 가게가 있으면 해당 store에 `map_query` 보정. 필요 시 검사 규칙으로 "stores는 지도 링크 필수"를 `validate.py`에 추가 검토.
- 영향 파일: `data/breakfast.json`, `scripts/build_index.py`, `tests/test_build_index.py`, `viz/breakfast.html`(빌드), `CLAUDE.md`, `README.md`.
