# 2026-05-31 — docs/ 미등록 12개 파일 DOC_PAGES 등록 + archive.html 참고 문서 카드 추가

## Status

Accepted

## Context (왜)

- `docs/` 최상위에는 총 12개 마크다운 파일이 존재했으나 `DOC_PAGES`에 등록되지 않아 사이트 내 렌더 페이지가 없었다.
- 등록되지 않은 파일은 URL로 직접 접근할 방법이 없어 가족 공유 사이트에서 사실상 불가시 상태였다.
- `viz/archive.html`에는 이미 의사결정 분석 자료(장마·예산·후보지 점수)가 있으나, 연관 리서치 문서(후보지 비교·날씨 분석·항공권 분석·에어비앤비 비교 등)로의 진입점이 없었다.
- 운영 문서(이동 경로 가이드·사이호지 예약 리서치·구글맵 목록·조식 상세)도 일정·예약 화면에서 연결되지 않은 채 방치돼 있었다.
- 기존 7개 DOC_PAGES 패턴과 `build_doc_page()` 인프라가 완비돼 있어 추가 비용 없이 확장 가능했다.

## Decision (무엇)

- 미등록 12개 `docs/` 파일을 전부 `DOC_PAGES`에 등록해 `viz/*.html` 렌더 페이지를 생성한다.
  - 아카이브 문서 8개(candidates·weather·flights·budget-options·airbnb-comparison·jejuair·itinerary-may·transit-mcp-handoff): `tab="home"`, `back_href="archive.html"`
  - 운영 문서 4개(transit-guide·saihoji·soyeon-maps·breakfast-doc): `tab="itinerary"`, `back_href` 각 관련 페이지
- `viz/archive.html`에 `card_docs_archive()` 섹션을 추가해 12개 문서를 "운영" / "아카이브" 두 그룹의 카드 그리드로 노출한다.
- 채택하지 않은 대안: 별도 docs 인덱스 페이지 신설 — archive.html이 이미 아카이브 허브 역할을 하므로 기존 페이지 확장이 더 응집적이라 기각.

## Consequences (그래서)

- 긍정: 12개 문서 모두 사이트 내 URL로 접근 가능해짐. `viz/archive.html` 카드 섹션에서 한눈에 탐색 가능.
- 긍정: 검사 J(GitHub 링크 금지) 자동 적용 — OUTPUTS 자동 등록으로 별도 조치 불필요.
- 트레이드오프: archive.html이 다소 길어짐. "참고 문서" 섹션은 맨 하단에 배치해 기존 분석 자료 접근성에 영향 없음.
- 후속: 운영 문서(transit-guide·saihoji·soyeon-maps)를 일정·예약 화면의 관련 카드에서 `doc-link`로 직접 연결하려면 별도 PR 필요.
- 영향 받은 파일: `scripts/build_index.py`, `tests/test_build_index.py`, `CLAUDE.md`
