# 2026-05-20 — 모바일 운영 화면 정체성 정렬: 비교 잔재 제거

## Status

Accepted

## Context (왜)

- 사용자 우선순위(2026-05-20 세션): "모바일 화면이 가장 중요". 가족 수신자(시부모 포함)가 휴대폰으로 처음 보는 4개 운영 탭(홈·일정·숙박·예약)이 레포 정체성을 결정한다.
- 카톡 채팅(2025-05-31~2026-05-20)이 보여주는 현실: 2026-05-12~13 항공·1·2박 에어비앤비·3박 카덴쇼 모두 확정, 실재 시나리오는 **1개**만 존재. 11일 뒤 출국.
- PR #36이 메인 페이지 골격을 정리했으나 카드 내부에 의사결정 시점의 비교 잔재가 남아 있었다:
  - `index.html` 요약 카드(`card_summary`) — `data/decision.json` kyoto.notes의 분석가 블롭(`seasonality=9`·`comfort_score=9`·`docs/...` 파일 경로 4개)이 직접 노출.
  - `viz/checklist.html` 헤더 — "시나리오: **kyoto_may31_kadensho_early_bird** · 7개 항목" — 내부 코드명이 가족 화면에.
  - `viz/lodging.html` `card_kadensho` — 카덴쇼 4 플랜(트립닷컴 확정 + 꽃전초·스탠다드·가오슝 미선택 3개) 동시 노출, 제목도 "4 플랜".
  - `viz/lodging.html` `card_flights` — 항공 3 옵션(5/24~27·5/12~16 미예약 + 5/31~6/3 확정) 동시 노출.
  - `viz/lodging.html` header — "에어서울 옵션" 어휘로 미확정 인상.
  - `card_kadensho` sub 줄이 "dormy-hotels.com 공식 검색"으로 표시되나 실제는 **트립닷컴 예약 완료**.
- 알려진 대안:
  1. data/decision.json kyoto.notes를 편집 — 아카이브 보존 원칙 위반(시점 스냅샷). 채택 안 함.
  2. 비교 카드를 운영 탭에서 숨기지 않고 "원안 비교 (아카이브)" 접기 섹션으로 — 모바일 real estate 낭비, 운영 페이지 부담. 채택 안 함.
  3. **build_index.py에서 운영 페이지 렌더링 시 확정 시나리오만 필터링**, 비교는 archive.html에 위임. **채택**.

## Decision (무엇)

- `scripts/build_index.py` 5개 함수 미세 조정 — 운영 페이지에서 확정 1건만 렌더, 미확정·비교 항목은 archive.html에 위임:
  - `card_summary` line 284 — kyoto.notes 블롭을 운영 한 줄로 대체("발권·예약 완료 (항공 A8YW58 · 시오 마치야 · 카덴쇼 트립닷컴). 출국 전 점검은 ☑ 예약 탭.").
  - `card_kadensho` — 필터를 `id == "kadensho_tripcom_no_meal_2026jun2"`로 좁히고, 제목 "4 플랜" → "(6/2 1박)", sub를 dormy-hotels.com → 트립닷컴 예약번호로 교체.
  - `card_flights` — 필터를 `id == "rs_kix_may31_jun3"`로 좁히고, sub를 에어서울 RS 예약번호 A8YW58 + 시간으로 교체.
  - `build_lodging` status — "항공 옵션" → "에어서울 4인 발권 완료".
  - `build_checklist` status — "시나리오: kyoto_may31_kadensho_early_bird · 7개 항목" → "{확정} 확정 · {미정} 미정 · 총 N개 항목".
- `data/cost-options.json` 비확정 시나리오 7건에 `[아카이브·...]` prefix 추가 — archive.html에서도 일관 표시.
- `data/decision.json` 최상위에 `_archive_status: "decision_ended_2026_05_12"` + `_archive_note` 필드 추가.
- 채택하지 않은 대안:
  - `docs/` MCDA 입력 .md 6종에 아카이브 배너 추가 — mobile-first 우선순위 외, 별도 PR로 분리.
  - `_TABS` 4탭 유지 (아카이브 nav 미추가) — 운영 모드 전환 원칙 충실.

## Consequences (그래서)

**긍정**
- 가족 수신자가 4개 운영 탭에서 보는 모든 텍스트가 "이미 발권/예약 완료된 단일 여행"으로 일관 표시.
- index.html 첫 카드에서 "발권·예약 완료 (A8YW58·시오·트립닷컴)" 노출 → 첫 시선에 운영 모드 인지.
- 카덴쇼 4 플랜 비교가 archive.html로만 노출되어 운영 화면 부담 감소.
- 내부 시나리오 id(`kyoto_may31_kadensho_early_bird`) 같은 개발자 jargon이 가족 화면에서 사라짐.

**부정·트레이드오프**
- `card_kadensho`·`card_flights` sub 줄에 booking-checklist의 예약번호를 하드코드 — cost-options↔booking-checklist 데이터 결합 미적용, 향후 예약번호 변경 시 build_index.py 직접 수정 필요(가능성 낮음).
- 비확정 카덴쇼 3 플랜(꽃전초·스탠다드·가오슝)이 운영 탭에서 사라짐 → 가이세키 비교 검토 시 archive.html로 이동 필요. 의도된 분리.

**후속 행동**
- Vercel preview에서 휴대폰 사이즈로 4탭 직접 점검 (홈·일정·숙박·예약).
- `docs/` MCDA 입력 .md 6종 아카이브 배너는 별도 PR.
- 카덴쇼 4 플랜 비교를 archive.html에 별도 섹션으로 추가하는 PR 검토 (현재 archive.html에는 시나리오 단위 비교만 있고 lodging 단위 비교는 없음).

**영향 받은 파일**
- `scripts/build_index.py` — card_summary·card_kadensho·card_flights·build_lodging·build_checklist 5개 함수 미세 조정.
- `data/cost-options.json` — 비확정 시나리오 7건 라벨 prefix.
- `data/decision.json` — `_archive_status`·`_archive_note` 최상위 키 추가.
- `docs/decision-log/2026-05-20-03-mobile-operational-mode-cleanup.md` (본 일지, 신규) — ADR 5섹션 자기 적용.
- 자동 재생성: `index.html`·`viz/lodging.html`·`viz/checklist.html`·`viz/archive.html`·`assets/og-*.svg`.
