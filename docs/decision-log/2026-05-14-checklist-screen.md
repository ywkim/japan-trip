# 2026-05-14 — 예약 체크리스트 시각화 화면 추가

- 주제: 예약 진행 상태(`data/booking-checklist.json`)를 한눈에 보여주는 사용자 화면 신설
- 산출물:
  - `viz/checklist.html` (인라인 데이터, 더블클릭 동작, 외부 CDN/CSS 의존성 없음)
  - `README.md` 사용법 1줄 추가 (viz/checklist.html 더블클릭 안내)
  - `CLAUDE.md` 디렉토리 트리 + 데이터 동기화 규칙에 `viz/checklist.html` 1줄 추가
- 합의:
  - 단일 출처는 `data/booking-checklist.json` 그대로 유지. 화면은 인라인 사본.
  - 상태/메모 변경은 브라우저 localStorage에만 저장 → JSON 내보내기 후 파일에 반영해야 영구화.
  - `viz/dashboard.html`과 동일한 디자인 토큰(다크모드·뱃지·카드)을 따라 일관된 룩앤필 유지.
- 보류:
  - build 통합(`scripts/build_index.py`가 `viz/checklist.html`도 산출하도록) — `viz/dashboard.html`과 함께 추후 일괄 정리.
- 다음 단계:
  - 예약이 진행되면 `data/booking-checklist.json`의 `status`를 갱신 → `viz/checklist.html` 인라인 데이터도 함께 갱신 (manual sync).
  - `python scripts/build_index.py` 재실행으로 `index.html` §7 카드도 동기화.

## 핵심 관찰

- 현 시점(2026-05-14) 기준 8개 항목 전부 `미정`. 어느 것도 아직 예약 단계에 진입하지 않음.
- 가장 이른 마감(`due_date`)은 2026-05-18로 항공·에어비앤비 시오·우메코지 카덴쇼 3건이 동시 — D-4. 우선순위 1순위 클러스터.
- 보험·교통패스는 2026-05-25 (D-11), eSIM·환전은 2026-05-28 (D-14)로 2주 내 모두 처리 필요.
- 시각화 도입 후 영욱이 모바일에서도 `미정/예약중/확정` 진행 상태와 D-day를 한눈에 파악 가능 → 임박 항목을 놓칠 위험 감소.
- 단일 출처(`data/booking-checklist.json`) 원칙은 그대로 유지하고, 화면은 인라인 사본 + localStorage 임시 메모만 허용 → JSON 일치성은 PR 단계에서 grep으로 확인.
