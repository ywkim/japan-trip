# 2026-05-14 — weather/flights MD↔JSON CI 동기화 게이트 추가

- 합의: `docs/weather.md` ↔ `data/weather.json`, `docs/flights.md` ↔ `data/flights.json`
  동기화를 manual sync에서 CI 게이트로 승격. drift 시 PR 머지 차단.
- 산출물:
  - `scripts/validate.py`에 검사 E·F 추가
    - E: weather.json `cities[*].name`이 weather.md에 등장하고, 각 도시의
      월별 `comfort_score` sequence가 도시명을 포함한 한 라인에서 일치해야 함
    - F: flights.json의 `snapshot_date`·`version` 문자열이 flights.md에 등장하고,
      `ranking_4pax_median_5night_2026_05.by_total_low_to_high`의 도시별
      `median_4pax_krw` 중 최소 1개가 "만" 단위 표기로 flights.md에 일치해야 함
  - `tests/test_validate.py`에 `WeatherSyncTests`·`FlightsSyncTests` 신설
    (in-sync/drift 케이스 각각 격리 fixture 기반 검증)
  - `CLAUDE.md` CI 게이트 표·동기화 규칙 행 갱신
- 핵심 관찰:
  1. 게이트 추가 전: CI는 cost-options(B/C)·SYNC 주석(D)·index drift만 차단.
     weather/flights의 manual sync 실수는 reviewer 눈에만 의존했음.
  2. 게이트 추가 후: `python scripts/validate.py`가 도시 5개 × 월 4개의
     comfort_score, snapshot_date "2026-05-11", version "v2.1", 7개 도시의
     median 만 단위 표기까지 자동 비교 → drift 자동 차단.
  3. 도시명 표기 차이 (예: weather.json "오키나와(나하)" vs weather.md "오키나와")는
     **괄호 앞 short_name**도 인정하여 사람 가독성을 깨지 않으면서 검증.
  4. flights.md에 "만" 단위 표기 (예: 63만)와 flights.json의 KRW 정수 (630000)
     사이 변환은 정수 나눗셈 ÷10000로 1:1 매칭. 천 단위 round 오차 우려는 현재
     데이터셋이 모두 만 단위 라운드라 없음.
  5. production 데이터에서 검사 E·F 모두 exit 0 (in sync 확인).
- 다음 단계:
  - `data/cost-options.json` ↔ `docs/budget-options.md` 등 다른 단일출처에도
    동일 패턴 (검사 G·H) 확장 검토. 현재는 cost는 SYNC 주석으로만 묶여있음.
  - 향후 `data/itinerary.json` 같은 신규 단일출처가 들어오면 같은 게이트 패턴
    템플릿으로 추가.
