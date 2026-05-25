# 2026-05-24 — 모바일 일정 가독성: "쉬운 설명 + 접기" 렌더 패턴

## Status

Accepted

## Context (왜)

- 사용자 피드백: "모바일 화면이 이해하기 어려움". 확인 결과 대상은 모든 화면, 선호 방향은 "접기/링크로 쉬운 설명을 추가".
- 구체 원인: `data/itinerary.json`의 `arrive_from.route`가 다구간·장문(예: "JR 하루카 KIX→교토역 75분 + JR 산인본선 교토→니조 5분 + 도보 니조역→시오 7분 0.5km")인데, `scripts/build_index.py`의 `transit_line()`이 이 장문을 각 장소 위에 흐린 한 줄로 깔아, 정작 "몇 시·어디"가 한눈에 안 들어옴.
- ICOCA 실행 단계(번호 목록)·예산 9개 시나리오 등 항상 펼쳐진 장문 블록도 카드를 압도.
- 모든 HTML은 `build_index.py` 산출물(직접 편집 금지)이고 공통 `CSS`가 6개 HTML 전부에 인라인되므로, 빌더 함수 + CSS만 고치면 전 화면에 일괄 적용된다.
- 대안: (a) 장문을 단순 truncate — 정보 손실로 기각. (b) 별도 상세 페이지로 이동 — 자기완결(외부 fetch 없음) 원칙·탭 부담으로 기각.

## Decision (무엇)

`build_index.py`에 재사용 헬퍼 `fold(summary, detail)`(= `<details class="leg"><summary>…</summary><div class="leg-detail">…</div></details>`)와 공통 CSS를 추가하고, 장문 블록을 "평이 요약 + 접기 상세"로 렌더한다.

- `transit_line()` 재작성: 요약은 모드별 한국어 동사(`MODE_VERBS`: 걸어서·버스로·전철로·공항특급으로 등) + 소요시간(예: "🚌 버스로 35분", tbd는 "약 35분 (현지 확인)"), 상세는 원문 `route` + 기존 출처 URL(`경로 ↗` 링크).
- 타임라인 항목 순서를 "시간·장소 먼저 → 이동 접기 아래"로 재배치하고 시간(`.day .date .k`)을 굵게·tabular-nums로 강조.
- ICOCA 실행 단계·예산 비선택 시나리오를 `fold`로 접는다(선택 시나리오는 펼친 상태 유지).
- 적용: index·viz/itinerary·viz/itinerary-table·viz/archive. 비대상: lodging·checklist(2~3줄 k/v 카드라 이미 스캔 가능).

## Consequences (그래서)

- 긍정: 기본 화면이 "시간·장소·이동수단·소요시간"만 보여 한눈에 들어옴. 상세 경로·출처 링크는 손실 없이 접기 안에 보존. 표 셀도 짧아져 가독성 향상.
- 부정·트레이드오프: 상세 경로 확인에 탭 1회 필요. `<details>` 의존(구형 브라우저 일부 미지원이나 모바일 사파리·크롬 지원).
- 후속: 새 장문 정보도 `fold` 패턴을 따른다(CLAUDE.md 데이터 동기화 규칙에 명시).
- 영향 받은 파일: `scripts/build_index.py`(헬퍼·`transit_line`·`card_budget`·playbook·타임라인 순서·CSS), `tests/test_build_index.py`(`TransitFoldTests` 신규), 재빌드된 6 HTML, `README.md`, `CLAUDE.md`.

## Test plan

- [x] `python scripts/build_index.py` → 12개 산출물 재생성
- [x] `python -m unittest discover -s tests` → 71 통과(신규 `TransitFoldTests` 포함)
- [x] `python scripts/build_index.py --check` → All outputs in sync
- [x] `python scripts/validate.py` → 0 errors
- [ ] 모바일 폭에서 index·viz/itinerary 육안 확인(요약 우선·접기 동작)
