# 2026-05-24 — 예약 탭 카드 재설계 (구조화 필드 + 상태 색상 + D-day)

## Status

Accepted

## Context (왜)

- PR #43에서 미정 항목 노트에 리서치 내용을 추가한 뒤, "예약 탭 화면이 텍스트라 이해하기 불편하다"는 피드백을 받았다. 각 항목이 `제목 + 상태 + 기한 + 긴 노트 문단`이라 핵심(금액·마감·권장)이 긴 텍스트에 묻혀 모바일에서 스캔이 어려웠다.
- 사용자는 "구조화(스키마 변경) + 시각 개선" 둘 다를 선택했다.

## Decision (무엇)

- `data/booking-checklist.json` 항목에 선택 필드를 추가: `amount`(금액 한 줄)·`reference`(예약/확정 정보, 확정 항목)·`action`(권장 다음 행동, 미정 항목)·`link`({label,url} 출처/상세). `note`는 전체 상세로 유지.
- `scripts/build_index.py`에 공용 `checklist_card()` 렌더러 도입(`card_checklist`·`build_checklist` 공유):
  - 제목 옆 상태 배지 + 카드 좌측 색상 띠 (확정=초록 `--ok` / 미정=주황 `--warn` / 예약중=파랑 `--info`).
  - 금액·마감·예약번호·권장을 라벨 행으로 렌더, 긴 `note`는 `<details>`(자세히)로 접음.
  - 출처 문서는 `.doc-link` 버튼으로 노출.
  - 마감일은 `data-due` 속성 + 클라이언트 인라인 스크립트로 **D-day**를 계산(빌드 시각 비의존 → `--check` 결정성 유지). D-2 이내는 `--urgent`(빨강) 강조.
  - 정렬: 처리 필요(미정·예약중) 먼저, 그다음 마감 이른 순.
- 상태 색상은 CSS 변수(`--ok/--warn/--info/--urgent`)로 정의하고 다크모드 대비값을 함께 추가.
- TDD: `test_checklist_status_is_color_coded`·`test_checklist_renders_structured_fields`·`test_checklist_long_note_is_collapsible`·`test_checklist_pending_due_has_dday` 4개를 먼저 추가(red) → 구현 → green.
- 대안 기각: 빌드 시각으로 D-day를 서버측 렌더 — `--check` drift를 유발(매일 출력이 바뀜)하므로 미채택, 클라이언트 계산 채택.

## Consequences (그래서)

- 긍정: 예약 탭이 한눈에 스캔 가능(상태 색상·금액·마감 D-day·권장 한 줄). 긴 리서치 노트는 접혀 기본 화면이 간결. 출처는 탭 가능한 버튼.
- 부정·트레이드오프: 요약 필드(amount 등)와 note에 동일 수치가 일부 중복(요약 vs 상세 의도). D-day는 JS 비활성 시 미표시(날짜 텍스트는 그대로 보임 — 점진적 향상).
- 영향 받은 파일: `scripts/build_index.py`(CSS 변수·체크리스트 클래스, `checklist_card`/`checklist_sort_key`/D-day 스크립트, `card_checklist`·`build_checklist` 재작성), `data/booking-checklist.json`(선택 필드 추가), `tests/test_build_index.py`(테스트 4개), 빌드 산출물 `viz/checklist.html` 재생성. (`index.html`은 운영 모드로 체크리스트 미렌더 → 변경 없음.)
