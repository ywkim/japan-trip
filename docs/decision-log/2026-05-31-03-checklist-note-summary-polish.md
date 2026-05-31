# 2026-05-31 — checklist note 요약 다듬기 (dangling word 제거 · eSIM 1줄)

## Status

Accepted

## Context (왜)

- 직전 작업(`2026-05-31-02`)이 `checklist_card` note를 `note_block(render_fn=linkify)`으로 전환해 ` · ` 구분 항목은 의미있는 요약을 얻었으나, 두 가지 잔여 결함이 모바일 화면에 노출:
  1. **`출국…`·`두…` — 의미 없는 첫 어절 잘림**: `iphone_apps`·`dining_reservations` note는 ` · ` 구분자가 없어(`. `·공백없는 `·` 사용) 폴백이 첫 띄어쓰기까지만 끊음. iphone_apps는 첫 공백이 "출국 |전"이라 한 글자 어절만 남아 "자세히"보다 더 고장 난 것처럼 보임
  2. **eSIM 요약이 3줄로 늘어짐**: ` · ` 앞 2세그먼트가 각 ~45자라 합산 ~95자 → 3줄 줄바꿈, 카드 압도
- 사용자 확인: 코드+데이터 수정 채택, eSIM 요약은 1줄로 단축 요청

## Decision (무엇)

### 코드 (`scripts/build_index.py`)
- `note_block` 요약을 **고정 2세그먼트 → 60자 예산 기반**으로 변경: seg0 항상, seg1은 합산 ≤60자일 때만. eSIM처럼 seg0이 길면 1개로 제한
- `note_block` "구분자 없음" 폴백을 **첫 어절 → 문장 인식(`_lead_split`)**으로 교체. dining이 첫 문장 "두 저녁 모두 워크인 대기 리스크 커 사전 넷예약 권장(전화 불요)"으로 자동 개선
- `_detail_lines(text, render_fn=None)` — `render_fn` 파라미터 추가(기본 `link_places`). 폴백 상세에 `linkify` 전달해 dining의 markdown 링크(`AutoReserve`·`tel:`) 유지

### 데이터 (`data/booking-checklist.json`)
- `iphone_apps` note: 앱 리스트 `·`(공백없음) → ` · ` 구분 + 선두 요약절 "출국 전 4인 모두 설치·설정 완료(5/30 마감)" 추가 (첫 공백 2번째 문제는 코드로 불가 → 데이터 정비 필수)
- `esim` note: 선두 오리엔팅 세그먼트 "데이터 = Airalo eSIM 부부 2라인 + 시부모 핫스팟 공유" 추가 → 60자 예산으로 요약 1줄. 기존 세그먼트는 전부 보존(접힌 상세로 이동)
- 두 note 모두 **내용·출처·가격 무삭제**, 순서·구분자만 정비

## Consequences (그래서)

**긍정**:
- 모든 checklist 카드 요약이 의미있는 한 줄: eSIM `데이터 = Airalo eSIM 부부 2라인…`, 앱 `출국 전 4인 모두 설치·설정 완료(5/30 마감)`, 식당 `두 저녁 모두 워크인 대기 리스크 커…`
- `출국…`·`두…` dangling word 완전 제거
- dining·eSIM 상세 markdown 링크·출처 URL 전부 유지

**트레이드오프**:
- eSIM·iphone_apps note에 선두 요약절이 일부 `금액`/`label`과 중복 (오리엔팅 목적상 허용)

**후속 행동**:
- 신규 checklist note는 ` · ` 구분 + 선두 요약절 컨벤션 권장 (검사로 강제하지는 않음)

**영향 파일**:
- `scripts/build_index.py` (`note_block` 요약 로직·폴백, `_detail_lines` render_fn)
- `data/booking-checklist.json` (`iphone_apps`·`esim` note)
- `tests/test_build_index.py` (ChecklistCardNoteFoldTests에 3개 추가)
- `docs/decision-log/2026-05-31-03-checklist-note-summary-polish.md` (이 파일)
