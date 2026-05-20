# 2026-05-20 — decision-log·PR 본문 ADR(Nygard) 형식 강제

## Status

Accepted

## Context (왜)

- 현재 `docs/decision-log/`와 PR 본문은 형식 일관성이 없다:
  - `docs/decision-log/README.md`(기존)는 단순 bullet 가이드 (`합의·보류·변경·산출물·핵심 관찰·다음 단계`).
  - 실제 파일은 스타일 제각각 — bullet 일색(예: 2026-05-19-haruka-discount-oneway-selected.md), 헤더 구조(예: 2026-05-18-04-transit-pass-correction-icoca.md, 2026-05-20-kakaotalk-sync-kadensho-booking.md) 혼재.
  - PR 본문은 Claude Code 기본 `## Summary / ## Test plan` 템플릿만 강제 → **"왜 이 결정을 했는가"가 누락**되기 쉬움 (예: PR #39는 어긋남 표·변경 파일·테스트 체크리스트는 있으나 "왜 booking-checklist는 5/13 시점에 동기화되지 않았는가" 같은 Context가 부족).
- 사용자 지시(2026-05-20 세션): "PR 본문과 docs/decision-log/는 '왜'를 ADR(Nygard) 형식으로 문서화하도록 CLAUDE.md 문서화".
- 알려진 대안:
  1. **현행 bullet 형식 유지** — 가볍지만 Context 누락 위험 지속. 채택 안 함.
  2. **MADR(Markdown ADR) 등 확장 ADR** — 섹션이 더 많아 짧은 PR에 과부하. 채택 안 함.
  3. **Nygard 5섹션(Title/Status/Context/Decision/Consequences)** — 1세대 ADR 표준, 4~5섹션으로 최소·충분. **채택**.

## Decision (무엇)

- `CLAUDE.md`의 "메타 문서화 규칙 (모든 PR 공통)" 섹션에 **"ADR(Nygard) 형식 — decision-log 항목·PR 본문 (필수)"** 절을 신설하여 5섹션 표준·공용 템플릿·PR Test plan 결합 규칙을 강제 규정으로 명시.
- `docs/decision-log/README.md`의 "항목 형식" 절을 ADR 템플릿으로 교체하고 정본을 CLAUDE.md로 명시.
- 본 일지(2026-05-20-02-adr-format-mandate.md)를 **ADR 형식으로 작성**하여 첫 적용 예시로 사용.
- Cutover: 본 PR 머지 이후 모든 신규 PR/일지에 적용.
- 채택하지 않은 대안:
  - 기존 일지 retroactive 변환: **불가** — 일지는 시점 스냅샷, 편집 시 충돌·이력 손실(`reports/final-report.md`의 사후 메모 방식과 동일 원칙).
  - PR #39 본문 retroactive 수정: 보류 — 본 PR 머지 후 별도 판단.

## Consequences (그래서)

**긍정**
- 모든 신규 PR/일지에 "왜(Context)"가 명시적으로 들어감 → 후속 세션이 결정 의도를 빠르게 복원.
- decision-log·PR 본문 형식 통일 → 자동화·검색·diff 친화적.
- `Status: Superseded by <slug.md>` 필드로 결정 이력 그래프 추적 가능 → 묵은 일지 vs 활성 일지 구분 명확.

**부정·트레이드오프**
- 짧은 PR(오타 수정 등)에도 5섹션 강제 시 과부하 → CLAUDE.md "메타 문서를 갱신하지 않는 경우"의 `META: skip` 예외를 그대로 유지하여 완화.
- 기존 일지(bullet/혼재)와 신규 일지(ADR) 형식이 혼재 → README와 CLAUDE.md에 cutover 일자(2026-05-20) 명시로 혼선 최소화.

**후속 행동**
- 본 PR 머지 직후 다음 PR부터 ADR 적용.
- (선택) 핵심 일지(예: 2026-05-11-may31-jun3-kyoto-update, 2026-05-12-04-airbnb-shio-selected, 2026-05-20-kakaotalk-sync-kadensho-booking)의 ADR 변환은 별도 PR로 분리 결정.
- PR #39 본문 ADR 재작성 여부는 본 PR 머지 후 사용자 판단.

**영향 받은 파일**
- `CLAUDE.md` — 메타 문서화 규칙 섹션에 새 ADR 절 추가, 기존 "1. docs/decision-log/" 항목의 형식 안내 1줄을 ADR 절 링크로 교체.
- `docs/decision-log/README.md` — 항목 형식 코드 블록 교체, 정본을 CLAUDE.md로 위임.
- `docs/decision-log/2026-05-20-02-adr-format-mandate.md` (본 일지, 신규) — 첫 ADR-형식 일지 = 자기 적용 예시.
