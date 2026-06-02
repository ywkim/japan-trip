# 2026-05-31 — 루트 index.html 임베드 섹션의 사이트 내 링크 viz/ 접두사 수정 (404 버그)

## Status

Accepted

## Context (왜)

- 사용자가 모바일에서 교통패스 카드의 "ICOCA·PASMO 셋업" 링크를 탭하니
  `…/icoca-setup.html`(루트)로 풀려 **404 NOT_FOUND**가 떴다(스크린샷 2장).
- 원인: `checklist_card`(체크리스트 카드)와 `doc_link_html`(일정 조식 링크)이 만든 사이트 내
  링크는 viz-상대(예: `icoca-setup.html`, `breakfast.html`)였다. 이 두 렌더러는
  **viz/checklist.html·viz/itinerary.html** 뿐 아니라 **루트 index.html**(`card_checklist`·
  `card_itinerary`로 임베드)에서도 호출된다. 루트(`/`)에서 viz-상대 링크는 `/<page>`로
  풀려 404 — `viz/<page>`가 돼야 한다.
- `checklist_card`는 `in_viz=True`를 **하드코딩**했고, `doc_link_html`은 url을 그대로 출력해
  둘 다 페이지 컨텍스트를 무시했다. viz 출력은 우연히 맞았고(같은 디렉토리) 루트만 깨졌다.
  잠재 버그였으나 이번에 추가한 교통패스 셋업 링크가 홈 화면 상단에서 노출되며 드러났다.
- 동일 클래스 버그가 루트의 다른 체크리스트 링크(transit-pass·research·essential-iphone-apps)와
  일정 조식 링크(breakfast)에도 있었다.

## Decision (무엇)

- `checklist_card(it, in_viz=True)`·`doc_link_html(link, in_viz=True)`에 `in_viz` 매개변수를
  추가한다. `in_viz=True`(viz/*.html)는 기존과 동일하게 접두사 없이, `in_viz=False`(루트
  index.html 임베드)는 사이트 내 상대 링크에 `viz/` 접두사를 붙인다(외부 http·절대경로·이미
  `viz/`로 시작하면 그대로).
- 루트 렌더러 `card_itinerary`·`card_checklist`만 `in_viz=False`로 호출. viz 렌더러
  (`build_itinerary`·`build_itinerary_table`·`build_checklist`)는 기본값 유지 → **viz 출력
  바이트 불변**.
- 대안 미채택: ① itinerary.json의 `breakfast.html`을 절대경로로 바꾸기(데이터에 배포 구조를
  하드코딩, viz 페이지에서 깨짐), ② 루트에서 체크리스트·일정 임베드 제거(요약 UX 손실).

## Consequences (그래서)

- 긍정: 홈 화면(루트)에서 모든 사이트 내 문서 링크가 정상 작동(404 제거). 링크 렌더가
  페이지 컨텍스트를 인지하는 일반 패턴 확보.
- 부정·트레이드오프: 두 렌더러 호출부가 컨텍스트(in_viz)를 넘겨야 함(루트 2곳).
- 후속: 없음(이번 PR 범위 내 완결).
- 영향 받은 파일: `scripts/build_index.py`(checklist_card·doc_link_html·card_itinerary·
  card_checklist), `tests/test_build_index.py`(RootPageInternalLinkTests 신규 + ChecklistMultiLink in_viz 명시).

## Test plan

- [x] `RootPageInternalLinkTests` 신규 — 루트 viz/ 접두사·viz 페이지 bare·외부 링크 불변·프로덕션 index.html/viz 회귀
- [x] `uv run python -m unittest discover -s tests` — 210 tests OK
- [x] `scripts/build_index.py` + `--check` 재현성, `scripts/validate.py` 0 errors
- [x] 빌드 산출물 확인: 루트 index.html `viz/icoca-setup.html`, viz/checklist.html `icoca-setup.html`
