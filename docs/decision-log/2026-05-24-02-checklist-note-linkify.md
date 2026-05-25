# 2026-05-24 — 예약 체크리스트 노트 URL 자동 링크화 (linkify)

## Status

Accepted

## Context (왜)

- PR #43에서 `data/booking-checklist.json` 미정 4항목 노트에 출처·상세 문서 URL을 추가했으나, 모바일 예약 탭(`viz/checklist.html`)에서 **URL이 클릭되지 않는다**는 피드백을 받았다.
- 원인: `scripts/build_index.py`의 `card_checklist`·`build_checklist`가 노트를 `esc()`(HTML escape)로만 출력해, URL이 앵커(`<a href>`) 없이 일반 텍스트로 렌더됐다. 기존 `transit_pass` 노트의 URL(transit-pass 문서·Apple Support)도 동일하게 클릭 불가였다.
- itinerary 쪽은 이미 구조화 데이터(label·url)로 링크를 렌더(`test_transit_pass_sources_rendered_as_links`)하지만, 체크리스트 노트는 자유 텍스트라 별도 처리가 필요했다.

## Decision (무엇)

- `scripts/build_index.py`에 `linkify()` 헬퍼를 추가: 자유 텍스트를 HTML escape하되 `http(s)://` URL은 `<a href target="_blank" rel="noopener">`로 변환. `card_checklist`·`build_checklist`의 노트 렌더링을 `esc()` → `linkify()`로 교체.
- TDD: 회귀 가드 `test_checklist_note_urls_rendered_as_links`를 먼저 추가(노트 내 모든 http URL이 `viz/checklist.html`에서 `<a href>`로 렌더되는지 검증) → red 확인 후 구현 → green.
- 대안 기각: 노트를 구조화(label·url 배열)로 스키마 변경 — 변경 범위가 크고 기존 단일출처 노트 자유 텍스트 관례를 깨므로 미채택. 자유 텍스트 + linkify가 최소 변경.

## Consequences (그래서)

- 긍정: 예약 탭 노트의 출처·상세 문서 URL이 모바일에서 탭으로 바로 열린다. transit_pass 기존 URL도 자동 링크화됨. URL escape 유지로 XSS 안전.
- 부정·트레이드오프: linkify는 `http(s)` URL만 인식(상대경로·이메일 제외) — 현 노트 용례에 충분.
- 영향 받은 파일: `scripts/build_index.py`(linkify 추가·노트 렌더 2곳), `tests/test_build_index.py`(테스트 1개 추가), 빌드 산출물 `viz/checklist.html` 재생성. (`index.html`은 운영 모드로 체크리스트 카드를 렌더하지 않아 변경 없음.)
