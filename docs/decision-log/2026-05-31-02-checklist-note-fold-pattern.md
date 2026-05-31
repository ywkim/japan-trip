# 2026-05-31 — checklist_card note fold 패턴 개선 (PR #71 패턴 통일)

## Status

Accepted

## Context (왜)

- PR #71이 `note_block()`·`memo_block()`·`_lead_split()` 등 "의미있는 요약 + 접기" 헬퍼를 도입했으나, `checklist_card`의 note 렌더는 여전히 `fold("자세히", linkify(note))`를 직접 호출
- "자세히"는 내용에 대한 힌트 0% — 수십 줄의 예약번호·PIN·세부 정보를 예측 불가능하게 감춤
- 상세 내부도 한 덩어리(one long string) — `_detail_lines` 미적용
- `note_block()` 그대로 대체할 수 없는 이유: `dining_reservations.note`에 markdown `[text](url)` 링크 포함, `note_block`의 내부 `esc()` 적용 시 링크가 깨짐

## Decision (무엇)

- `note_block(note, *, style="", render_fn=None)` — `render_fn` 파라미터 추가 (기본 `esc`, backward compatible)
  - 내부 `esc(x)` 전부 → `render_fn(x)` 로 교체
- `checklist_card` note: `fold("자세히", linkify(note))` → `note_block(note, render_fn=linkify)`
  - ` · ` 구분자 있는 note: 앞 2항목 summary, 나머지 다중 줄 detail
  - ` · ` 구분자 없는 note: 첫 어절 + "…" summary (iphone_apps·dining_reservations)
- 미채택 대안: `note_block` 대신 `memo_block` 사용 → ` · `·`. ` 혼합 노트에서 일관성 저하

## Consequences (그래서)

**긍정**:
- 항공·숙박·료칸·eSIM·사이호지 등 ` · ` 구분 note → 의미있는 앞 2항목 요약 노출
- dining_reservations markdown 링크(`AutoReserve`, `tel:`) 유지
- 기존 `note_block` 호출부 모두 backward compatible (render_fn 기본값 = esc)

**트레이드오프**:
- ` · ` 구분자 없는 항목(iphone_apps·dining_reservations)은 "출국…"·"두…" 첫 어절 요약 — 이상적이지 않음. 데이터 정비(note를 ` · ` 구조로 재작성)는 별도 후속 작업

**영향 파일**:
- `scripts/build_index.py` (note_block 시그니처 + checklist_card note 렌더)
- `tests/test_build_index.py` (기존 test 1개 수정 + ChecklistCardNoteFoldTests 3개 신규)
- `docs/decision-log/2026-05-31-02-checklist-note-fold-pattern.md` (이 파일)
