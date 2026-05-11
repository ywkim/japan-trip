# 2026-05-09 — 동반 인원 확정 (4인)

- 합의: **부부 2인 + 시부모 2인 = 4인**을 기본 전제로 확정. 이전 일지의 "보류: 동반자(부부만 vs +시부모)" 항목 해소
- 변경:
  - `data/decision.json`: `travelers`를 4인으로 갱신, `optional_companions` 제거, `travelers_composition` 필드 추가
  - `data/decision.json`: `family_fit` 설명을 "시부모 동반 4인 여행 적합성(보행·식사·언어·동선)"으로 갱신
  - `viz/dashboard.html`: 인라인 데이터 동기화 (CLAUDE.md 동기화 규칙)
  - `docs/candidates.md`: 상단 전제 명시 + 6개 도시 각각에 "시부모 적합성" 1줄 추가
  - `reports/final-report.md`: 동반자란 채움
- 제안 (보류, 합의 필요):
  - **`family_fit` 가중치 0.10 → 0.15 증액 검토**. 동반이 옵션이 아닌 확정 전제가 되었으므로 가족 적합성 비중을 높이는 것이 합리적. 단 가중치 합 1.0 유지 위해 다른 기준(`experience` 또는 `cost`)에서 0.05 차감 필요
- 보류: 가중치 재배분 합의
- 다음 단계:
  - 가중치 재배분 합의 후 `decision.json`·`viz/dashboard.html`·`reports/final-report.md` 동시 갱신
  - 시기·도시 후보 좁히기 → 점수 입력 → 종합 점수 산출
