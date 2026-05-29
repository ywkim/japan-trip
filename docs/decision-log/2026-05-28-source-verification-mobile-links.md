# 2026-05-28 — Playwright 출처 검증 + 모바일 출처 클릭 가능화

## Status

Accepted

## Context (왜)

- `data/*.json` 5개 파일의 근거 `source`에 URL·텍스트가 혼재. 출국 D-3(5/31) 직전, 출처가 살아있는지 마지막으로 검증할 시점.
- 모바일 화면(`viz/itinerary.html` 등)에서 출처 링크의 터치 타깃이 44px 미만이라 시부모 동반 운영 시 조작성 리스크.
- `scripts/list_sources.py`(신규)로 인벤토리: 근거 URL 37개(unique) + 텍스트 전용 source 53개.

## Decision (무엇)

- Playwright MCP로 근거 URL을 직접 방문 검증. 도달 결과:
  - 정상(200·콘텐츠 일치): JMA 매우 평년/속보(2), tictivity IC카드, 교토시 공식 1일권, SoraNews24, Apple Support, Inside Kyoto, kyotostation(나라선·사가노선), kyoto.travel, japan-guide, kinukake, en.kyotokk, en.activityjapan, Google Maps Directions(패턴), Naver 블로그 후기(패턴).
  - **사망(404)**: `livejapan.com/.../to-ji-temple/spot-lj0091598/` — 게다가 교토역↔카덴쇼 도보 leg에 토픽 불일치(To-ji 페이지)였음. → Google Maps Directions URL로 교체(교토역↔카덴쇼), `source_fetched_at`·`source_verified_at` 2026-05-28 갱신.
  - 차단(봇 챌린지, 판정 보류): tripadvisor ShowTopic — kinukake가 1차 출처라 영향 없음.
- 스키마: arrive_from·weather·pass source에 옵션 필드 `source_verified_at`(검증일), `source_url`(텍스트 source의 URL 보완용) 도입. `scripts/validate.py` G가 `source_url`=http(s) prefix, `source_verified_at`=ISO date 형식 검증.
- `scripts/build_index.py`: 출처를 `.source-link` 칩(min-height 44px)으로 렌더, 검증된 항목은 ✓ 표시. transit leg·교통 패스 출처에 적용.
- 채택하지 않은 대안: 텍스트 전용 source 53개 전체에 `source_url` 보완 — 대부분 미채택 대안 숙소(여행 미사용)라 비용 대비 가치 낮음. 확정 일정에 쓰이는 근거만 검증·태깅.

## Consequences (그래서)

- 긍정: 죽은 출처 1건 제거, 근거 URL 살아있음 확인. 모바일 출처 탭 영역 44px 보장 + ✓로 검증 신뢰도 가시화.
- 부정·트레이드오프: `source_verified_at`은 시점 스냅샷 — 시간이 지나면 재검증 필요. 텍스트 전용 source는 이번 범위에서 제외.
- 후속: 텍스트 전용 source(특히 cost-options 확정 항목)의 URL 보완은 별도 PR 여지.
- 영향 받은 파일: `scripts/list_sources.py`(신규), `scripts/validate.py`, `scripts/build_index.py`, `data/itinerary.json`, `data/weather.json`, `tests/test_validate.py`, `tests/test_build_index.py`, 빌드 산출물(`index.html`·`viz/*.html`).

## Test plan

- [x] `python -m unittest discover -s tests` — 72 tests OK
- [x] `python scripts/validate.py` — 0 errors
- [x] `python scripts/build_index.py --check` — drift 0
- [x] Playwright 375px 뷰: `.source-link` 19개, 높이 44px, ✓ 렌더 확인
