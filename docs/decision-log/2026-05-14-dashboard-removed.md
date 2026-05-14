# 2026-05-14 — 민감도 대시보드 제거 (의사결정 확정 후 sync debt 청산)

- 트리거: 의사결정이 확정(교토 5/31~6/3, 시오 + 카덴쇼)됨에 따라 MCDA 민감도 분석 화면(`viz/dashboard.html`)이 더 이상 의사결정 도구로 작동하지 않음. `data/decision.json` 수정 시 인라인 데이터를 수동 동기화해야 하는 viz 레이어가 누적 sync debt만 발생시키는 구조 → 청산.
- 합의:
  - `viz/dashboard.html` 파일 자체 삭제. `data/decision.json`의 single source of truth는 유지.
  - `viz/` 디렉토리는 보존 — 후속 unit이 신규 화면(`viz/itinerary.html`·`viz/checklist.html` 등)을 추가할 예정.
  - 의사결정 자체는 변경 없음. 단지 viz 레이어만 제거.
- 산출물:
  - **DELETE** `viz/dashboard.html`
  - **EDIT** `scripts/build_index.py` — 모듈 docstring의 `# TODO: viz/dashboard.html도 동일 스크립트로 generate (별 PR)` 주석 제거, FOOTER의 `<a href="viz/dashboard.html">민감도 대시보드</a>` 앵커 제거
  - **REGEN** `index.html` — footer 링크에서 민감도 대시보드 항목 사라짐 (`build_index.py --check` 통과)
  - **EDIT** `README.md` — "결과 보기"에서 대시보드 더블클릭 안내 제거, 디렉토리 트리의 `viz/` 코멘트를 "(신규 화면 추가 예정)"으로 교체, 환경 요구의 "브라우저 (대시보드)" → "브라우저 (`index.html` 모바일 8섹션 카드 열기)"로 갱신
  - **EDIT** `CLAUDE.md` — 작성 규칙의 시각화 항목 제거, MCDA 워크플로우 5단계 제거 후 단계 번호 재조정 (5→삭제, 6→5, 7→6), 디렉토리 트리의 `dashboard.html` 라인을 placeholder 주석으로 교체, 데이터 동기화 규칙 섹션의 dashboard 항목 제거
  - **EDIT** `.github/PULL_REQUEST_TEMPLATE.md` — scope 예시에서 `, dashboard` 제거, 관련 문서 체크리스트의 viz/dashboard.html 인라인 동기화 항목 제거
- 핵심 관찰:
  - dashboard.html이 viz 레이어로 sync debt를 발생시키던 구조 종료. 이제 `data/decision.json` 수정 시 수동으로 HTML 인라인 데이터를 따라 갱신해야 했던 부담 사라짐.
  - 데이터 단일출처(`data/decision.json`·`data/cost-options.json` 등) 무결성은 손대지 않음 — 점수 계산(`scripts/score.py`)·예산 평가(`scripts/budget.py`) 동작 동일.
  - CI 게이트(`build_index.py --check`·`validate.py`·unittest)는 모두 통과 유지. SYNC 주석에 dashboard 참조가 없었으므로 `validate.py` 동작에 영향 없음.
- 보류: `docs/jejuair-icn-kobe-june-2026.md` §5.4("민감도 검토: `viz/dashboard.html`...")의 잔존 참조는 본 unit의 변경 파일 목록 밖이라 보존. 고베 후보 자체가 교토 확정으로 obsolete이므로 별도 정리 PR(고베 분석 문서 archive 또는 §5 다듬기)에서 함께 처리할 것.
- 다음 단계: 후속 unit이 `viz/itinerary.html`·`viz/checklist.html` 등 신규 화면을 추가 (별 PR). 추가 시점에 `CLAUDE.md`·`README.md`의 `viz/` placeholder 주석을 실제 파일 설명으로 교체.
