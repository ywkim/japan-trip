# 2026-05-26 — 모든 화면에 접기 확장: 예약 체크리스트 긴 예약번호·권장 fold

## Status

Accepted

## Context (왜)

- PR #45(모바일 가독성 fold 도입)는 `fold(summary, detail)`/`note_block`/`pass_block`을 도입하면서, 적용 대상을 index·itinerary·itinerary-table·archive로 한정하고 **lodging·checklist는 "2~3줄 k/v 카드라 이미 스캔 가능"이라며 비대상**으로 두었다. 단 #45 원 피드백의 방향은 "대상은 모든 화면"이었다.
- 그 후 예약이 누적되며 `data/booking-checklist.json`의 `reference`(예약번호)·`action`(권장)이 길어졌다. 특히 사이호지(PR #51) 예약번호는 "Trip.com ① 1400827143416024 (성인2, ₩94,108) · ② 1400827143410570 (성인2, PIN 2362) · 6/1 10:30 · LEE/SOYEON · 조건부 취소(건당 수수료 ₩18,822)"로, `checklist_card`의 우측 정렬 셀(`.row .v`, `text-align:right`)에서 모바일 폭을 넘쳐 레이아웃을 깨뜨렸다.
- 사용자 지시: "PR #45 참고하여 모든 화면은 접기로" — #45가 미룬 화면에도 동일 fold 패턴을 확장.

## Decision (무엇)

- `scripts/build_index.py`에 재사용 헬퍼 `detail_row(label, value)`를 추가하고 `checklist_card`의 예약번호·권장 행에 적용:
  - 값이 44자 이하면 기존 k/v 행(`<div class="row">`) 그대로.
  - 44자 초과면 `fold`로 접되, `·` 앞 첫 토막을 `label · {앞토막}` 요약에 노출하고 나머지 세그먼트를 상세에 보존(정보 손실 없음). `·` 구분이 없으면 라벨만 요약.
  - 짧은 식별값(항공 `A8YW58`, 보험·환전 권장 등)은 행 유지 → 스캔성 보존.
- lodging 화면(`card_kadensho`)의 하드코딩 장문 라인("트립닷컴 예약번호 …")을 `note_block()` 경유로 변경 — 하드코딩 always-expanded 운영 라인 제거(현재 길이는 60자 이하라 펼침 유지, 길어지면 자동 접힘).
- 결과적으로 6개 산출물 전부가 동일 fold 패턴 적용.
- 기각 대안: (a) 행 안에서 truncate — 정보 손실, (b) 예약번호 셀만 좌측 정렬 CSS — 16자리 숫자 줄바꿈은 여전히 카드 압도, (c) 카드 전체 아코디언화 — #45의 블록 단위 접기와 결이 달라 "참고" 범위 초과.

## Consequences (그래서)

- 긍정: 체크리스트 화면이 모바일에서 넘치지 않고, 긴 예약번호·권장은 탭으로 펼침. 짧은 값은 즉시 스캔. #45가 미룬 "모든 화면" 완료.
- 부정·트레이드오프: 긴 예약번호 확인에 탭 1회. 44자 임계값은 휴리스틱(현 데이터 기준 항공·보험·환전은 행, 료칸·하루카·사이호지·eSIM은 접힘).
- 후속: 새 예약 항목도 동일하게 자동 적용(데이터만 추가하면 됨). index는 운영 모드라 체크리스트를 임베드하지 않음(링크만) — 변경 영향 없음.
- 영향 파일: `scripts/build_index.py`(`detail_row` 신규·`checklist_card`·`card_kadensho`), `tests/test_build_index.py`(`ChecklistDetailFoldTests` 신규), 재빌드 6 HTML, `README.md`, `CLAUDE.md`.

## Test plan

- [x] `python -m unittest discover -s tests` → 109개 통과(신규 `ChecklistDetailFoldTests` 5건 포함)
- [x] `python scripts/build_index.py --check` → All outputs in sync
- [x] `python scripts/validate.py` → 0 errors, 0 warnings
- [ ] 모바일 폭에서 viz/checklist.html 육안 확인 (사이호지·료칸·하루카 예약번호 접힘·짧은 값 행 유지)
