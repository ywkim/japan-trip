# 2026-05-09 — "실시간 가격 리서치 우선" 정책 도입 (CLAUDE.md)

- 합의: 모든 클로드 세션은 가격·운임·시세를 **실시간 웹 리서치**로 입력
- 합의: 학습 데이터 기반 추측치 입력 금지, `source` + `data_quality` 필드 필수
- 합의: `data_quality` 3단 분류 — `confirmed_booking` / `official_fare` / `researched_market_rate`
- 합의: 30일 이상 묵은 리서치 가격은 신뢰하지 않고 재조회
- 산출물:
  - `CLAUDE.md`에 "실시간 가격 리서치 우선" 섹션 추가
  - 메타 문서화 규칙에 가격 데이터 검증 의무 추가
- 다음 단계: 기존 `data/cost-options.json` 항목들도 `data_quality` 라벨 부여 (#5에서 적용 중)
