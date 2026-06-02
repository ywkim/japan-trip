# 2026-05-31 — 체크리스트 항목 다중 링크(links) + 교통패스 카드에 PASMO 셋업 연결

## Status

Accepted

## Context (왜)

- 같은 날 추가한 PASMO 앱 무기명 ¥0 경로(`2026-05-31-pasmo-mobile-ic-no-creditcard.md`)는
  가이드 문서(`docs/icoca-iphone-setup.md` §3.4)에만 존재했다. 모바일 운영 화면
  (`viz/checklist.html`)의 **교통패스 카드**는 여전히 "Apple Wallet ICOCA 단권"만 안내해,
  카드 없는 인원(시부모)이 PASMO 대안을 화면에서 찾을 길이 없었다 (사용자 모바일 스크린샷 확인).
- `booking-checklist.json` 항목은 참조 문서를 **단일 `link`(dict)**만 가질 수 있었다.
  교통패스 카드의 link 슬롯은 이미 "패스 비교"가 점유 → ICOCA·PASMO 셋업 가이드를 추가로
  연결할 자리가 없었다.
- 제약: Vercel 산출물은 GitHub·raw `.md` 링크 금지(검사 J). 링크 대상은 `DOC_PAGES`에 등록된
  사이트 내 렌더 페이지여야 한다 — `docs/icoca-iphone-setup.md`는 이미 `viz/icoca-setup.html`로
  등록돼 있어 연결 가능.

## Decision (무엇)

- `checklist_card`(`scripts/build_index.py`)가 항목당 **`links`(list) 또는 `link`(dict)**를 모두
  렌더하도록 확장한다(단일 `link`은 하위 호환 유지). 각 url은 기존대로 `DOC_SOURCE_TO_OUT`로
  사이트 내 페이지 치환.
- `data/booking-checklist.json`의 `transit_pass` 항목을 `links` 배열로 바꿔 **"패스 비교"** +
  **"ICOCA·PASMO 셋업"**(→ `viz/icoca-setup.html`) 두 링크를 노출하고, note에 카드 없는 인원의
  PASMO 대체 경로를 한 줄 추가한다.
- 대안으로 검토했으나 미채택: ① `iphone_apps` 항목 link 교체(앱 가이드를 밀어냄), ② 카드에
  인라인 텍스트만 추가(사용자 요청은 "안내 링크" — 탭 가능한 연결).

## Consequences (그래서)

- 긍정: 카드 없는 인원이 운영 화면의 교통패스 카드에서 바로 PASMO 셋업 가이드로 이동 가능.
  체크리스트 항목이 복수 문서를 참조하는 일반 패턴 확보.
- 부정·트레이드오프: 카드에 링크가 2개 노출돼 약간 길어짐. `links`/`link` 두 형식이 공존.
- 후속: 없음(이번 PR 범위 내 완결).
- 영향 받은 파일: `scripts/build_index.py`(checklist_card), `data/booking-checklist.json`
  (transit_pass·_doc 스키마 노트), `tests/test_build_index.py`(ChecklistMultiLinkTests 신규).

## Test plan

- [x] `tests.test_build_index.ChecklistMultiLinkTests` 3종 통과 (단일 link 하위호환·links 배열·프로덕션 교토패스 카드)
- [x] `uv run python -m unittest discover -s tests` — 203 tests OK
- [x] `scripts/build_index.py` + `--check` 재현성, `scripts/validate.py` 0 errors
