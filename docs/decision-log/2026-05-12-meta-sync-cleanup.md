# 2026-05-12 — 메타 동기화 부채 청산 (5/31~6/3 + 시부모 확정)

- 트리거: PR #13(일정 5/31~6/3 + 카덴쇼 2명×2실 6/2 1박)·#14(에어비앤비 5개 후보)와 시부모 동반 확정이 합쳐졌으나 정본(`data/decision.json`)·보고서(`reports/final-report.md`)·모바일 페이지(`index.html`)는 옛 5/24~27/4인 1실/시부모 옵션 표기 그대로 → 단일 출처 원칙 위반.
- 합의:
  - 시부모 동반은 **확정**. `trip.optional_companions` 필드 자체 폐기.
  - 일정·구조: 5/31(일)~6/3(수) 항공 3박4일, 1·2박 에어비앤비(5/31~6/2), 3박 카덴쇼 6/2~6/3 2명×2실 조기할인 조식.
  - 시나리오 ID `kyoto_may31_kadensho_early_bird` 신설.
- 산출물:
  - `data/decision.json` — `optional_companions` → `companions`, `kyoto.notes` 일정·구조 갱신
  - `data/cost-options.json` — 카덴쇼 6/2 4 플랜(early_bird/hwajeoncho/standard/gaosung) 정식 등록, scenario `kyoto_may31_kadensho_early_bird` 추가, 기존 항공 2건에 `data_quality: researched_market_rate` 보강
  - `reports/final-report.md` — §1 결정 요약·§5 보류·§6 일정 개요 5/31~6/3로 일괄 갱신
- 핵심 관찰:
  - 새 시나리오 `budget.py` 합계 **₩3,050,150 (3M ₩50,150 초과)** — 에어비앤비 placeholder ₩180K/박 가정. 매물 #4 세이 히가시야마(₩275K/박)·#5 반노천탕(₩292K/박) 사용 시 placeholder 대비 절감 가능
  - 카테고리 비율: 숙박 36.2%(가이드 27% 대비 큰 폭 초과 — 료칸 1박이 견인), 항공 33.7%(가이드 40% 안)
  - 에어비앤비 매물 1개 선정은 별 PR (영욱·소연 합의 필요)
- 다음 단계: 에어비앤비 매물 결정 → scenario 분기 `kyoto_may31_*_pick` 생성 → `budget.py` 재실행으로 3M 통과 여부 확정.
