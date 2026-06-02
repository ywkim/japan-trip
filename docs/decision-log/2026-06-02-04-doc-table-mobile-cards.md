# 2026-06-02 — 문서 페이지 표를 모바일에서 카드형(라벨:값)으로 스택

## Status

Accepted

## Context (왜)

- 새로 추가한 `viz/isetan-porta-shopping.html`을 사용자가 아이폰(LTE)에서 열어 캡처 제보: **4컬럼 표가 화면 폭을 넘겨 가로 스크롤**되고 "위치"·"가격" 컬럼이 잘려 보였다("가로 스크롤 등 UI가 아름답지 않아").
- 기존 `DOC_CSS`의 `.doc table`은 `display:block; overflow-x:auto`라 **표 자체가 가로 스크롤**되는 구조 — 데스크톱엔 무난하나 모바일에선 우측 컬럼이 가려진다. 교토역 쇼핑 페이지뿐 아니라 라멘코지·말차·날씨·후보 비교 등 표가 많은 23개 문서 페이지 공통 문제.
- python-markdown `tables` 확장은 단순 `<table>`만 출력 — 셀에 컬럼명 정보가 없어 CSS만으로 'label: value' 카드를 만들 수 없다.

## Decision (무엇)

- **`build_index.add_table_data_labels(html)` 신설** — 마크다운 렌더 후 각 표의 `<thead>` 헤더 텍스트를 본문 각 `<td>`의 `data-label` 속성으로 주입(`render_markdown_body`에서 호출). 기존 td 속성·data-label은 보존, thead/tbody 없는 표·표 없는 HTML은 무변경.
- **`DOC_CSS`에 `@media (max-width: 560px)` 카드 규칙 추가** — 좁은 화면에서 `thead` 숨김, 각 `tr`을 테두리 카드로, 각 `td`를 `td[data-label]::before { content: attr(data-label) }` 로 'label : value' flex 행으로 스택. 가로 스크롤 제거. 데스크톱(>560px)은 기존 `overflow-x:auto` 유지.
- 기존 토큰 변수(`--card`·`--border`·`--muted`)만 사용 — 신규 hex 없음(검사 H·DESIGN 무영향).
- **검토 후 기각**: 페이지별 표를 잘게 쪼개 수기 재작성(23페이지 반복·휴먼드리프트), 표를 ul 리스트로 변환(탭형 정보 가독성 저하), `white-space:nowrap`로 가로 스크롤 유지(원인 미해결).

## Consequences (그래서)

- 긍정: 23개 문서 페이지의 모든 표가 모바일에서 가로 스크롤 없이 카드로 읽힌다(위치·가격 등 잘림 해소). 데스크톱 표 형태는 그대로. 새 문서에도 자동 적용(추가 작업 0).
- 부정·트레이드오프: 매우 넓은 표도 카드로 세로 길어짐(컬럼 많으면 행당 카드가 길다 — 본 레포 표는 2~4컬럼이라 무리 없음). 라벨 길이는 `flex: 0 0 5rem` 고정.
- 후속: 표 렌더 변경이므로 TDD — 단위(`add_table_data_labels`)·렌더·CSS·프로덕션 회귀 테스트 6건 선작성 후 구현.
- 영향 받은 파일: `scripts/build_index.py`(`add_table_data_labels`·`render_markdown_body`·`DOC_CSS`), `tests/test_build_index.py`(DocTableResponsiveTests 6건).

## Test plan

- [x] `DocTableResponsiveTests` 6건 — 라벨 주입(단위·td속성·tableless)·렌더 통합·CSS 존재·프로덕션 페이지
- [x] `unittest` 218/218 PASS (212 → +6)
- [x] `build_index.py` 빌드 + `--check` 재현성 통과
- [x] `validate.py` 0 errors (검사 J·H 무영향)
