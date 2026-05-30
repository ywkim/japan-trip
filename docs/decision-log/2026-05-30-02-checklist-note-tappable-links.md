# 2026-05-30 — 체크리스트 note에 탭 가능한 마크다운·전화 링크 지원

## Status

Accepted

## Context (왜)

- 사용자가 모바일(Vercel 예약 탭)에서 `dining_reservations` 카드의 "자세히"를 열어보니 예약 채널(AutoReserve·楽天ぐるなび)·전화번호가 **일반 텍스트라 탭/클릭이 안 됨**("클릭이 안 돼").
- 원인: `build_index.py`의 `linkify`가 **벌거벗은 http(s) URL만** `<a>`로 변환하고, ① 라벨링을 못 해 긴 원문 URL이 그대로 노출되고 ② `tel:`(전화 탭)을 지원하지 않음. 기존 note는 채널을 이름으로만, 전화를 `☎075-…` 텍스트로만 적어 링크가 하나도 생성되지 않았음.

## Decision (무엇)

- `linkify`를 확장해 **마크다운 `[라벨](url)` 문법**을 지원한다. url 화이트리스트는 `http(s)`(새 탭)·`tel:`(전화 탭, 새 탭 아님)만 — `javascript:` 등은 무시(XSS 방지). 벌거벗은 http(s) 자동 링크 동작은 `_autolink` 헬퍼로 분리해 그대로 유지(하위호환).
- `dining_reservations.note`의 예약 채널·전화번호를 `[라벨](url)`·`[☎번호](tel:+81…)` 형식으로 교체해 모바일에서 바로 탭/통화 가능하게 한다.
- 채택하지 않은 대안:
  - 카드 `link` 필드(단일 버튼) 사용 — 식당 2곳·채널 다수라 1개 버튼으로 부족.
  - 전화번호 정규식 자동 인식 — 오탐 위험(가격·날짜 숫자), 명시적 `[](tel:)`가 안전.

## Consequences (그래서)

- 긍정: 예약 채널·전화가 라벨로 깔끔하게 탭/통화 가능. 모든 체크리스트 note(향후 항목 포함)에 재사용되는 일반 기능.
- 부정·트레이드오프: note 작성 시 채널은 `[라벨](url)` 규칙을 따라야 함(데이터 `_doc`·CLAUDE에 명문화).
- TDD: `tests/test_build_index.py::test_checklist_note_urls_rendered_as_links`에 마크다운·tel 단위 단언 추가, production note URL 추출 정규식을 `[^\s)]+`로 보정(마크다운 닫는 괄호 제외). build·validate·unittest 통과.
- 영향 받은 파일: `scripts/build_index.py`(linkify·_autolink)·`tests/test_build_index.py`·`data/booking-checklist.json`(note·_doc)·`CLAUDE.md`.
