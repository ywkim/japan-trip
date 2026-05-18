# 2026-05-17 — 장소 간 이동 메타 출처 추가 + 검사 G 신설

## 트리거

직전 세션 Q&A에서 "도보와 지역 교통의 근거와 출처는?" 진단 → 운임(JR 하루카·시영 1일권)은 `official_fare`로 라벨링 OK였지만, days[].`walking_km`(3/4/5/1)과 마크다운의 "버스 20~30분", "도보 15분", "두 곳 도보 권" 표현이 모두 출처 없음으로 확인. 브랜치명 `claude/add-transit-sources-McmoV`가 이 작업을 의도.

## 산출물

- `data/itinerary.json` 스키마 확장 — days[].items[]에 `arrive_from` 필드 추가 (mode·duration_min·distance_km·route·source·source_fetched_at·data_quality). days[]·trip에 `walking_km_source` 메타 추가.
- `scripts/validate.py` — 검사 **G** 신설 (arrive_from 무결성 + walking_km 정합성 + source_fetched_at 60d staleness).
- `scripts/build_index.py` — `transit_line()` 헬퍼로 카드/뷰에 이동 메타 한 줄(🚶/🚌/🚇/🚆/✈️/🚕 + 노선·분·km) 렌더. `tbd_needs_browser_mcp`는 "소요시간 미확정 — Maps 확인 필요" 회색 표기.
- `tests/test_validate.py` — `ItineraryTransitTests` 7 케이스(누락·잘못된 mode·잘못된 quality·tbd 면제·stale·walk 합 초과·정상 합).
- `docs/kyoto-itinerary-may31-jun3-2026.md` — "버스 20~30분"·"두 곳 도보 권"·"도보 15분" 표현을 노선·시간·거리·출처로 교체.
- `CLAUDE.md` — 데이터 동기화 규칙·CI 검증 표에 검사 G 행 추가.

## 데이터 출처 (확정 leg)

| 구간 | 모드 | 시간·거리 | 출처 |
|---|---|---|---|
| KIX ↔ 교토역 | airport_express | 75분 | JR 서일본 공식 (`haruka_rt_4pax` 인용) |
| 키요미즈 → 야사카 → 기온 | walk | 25분 · 1.3km | en.kyotokk.com · activityjapan.com |
| 니조역 → 사가아라시야마 | jr | 12분 · 8.5km | kyotostation.com (JR 산인본선) |
| 금각사 → 료안지 | bus | 4분 · 1.6km · 市バス 59 | kinukake.com · tripadvisor |
| 이나리 → 토후쿠지 → 교토역 | jr | 2분 + 5분 | kyotostation.com (JR 나라선) |
| 교토역 → 토지 | walk | 16분 · 1.2km | kyoto.travel · japan-guide.com |
| 교토역 ↔ 카덴쇼 | walk | 8분 · 0.6km | livejapan.com |

## tbd_needs_browser_mcp 후속 위임 (8 leg)

WebSearch/WebFetch로 분·거리·정확한 노선번호가 안 잡힌 구간 — Google Maps Directions URL을 `source`에 박아두었으므로, **Playwright MCP 보유 Claude Code 세션이 클릭 → 측정 → 라벨 승격**.

1. 시오(니조역) → 키요미즈데라
2. 기온 → 가와라마치/폰토초 (저녁 동선)
3. 죽림길 → 텐류지 (인접)
4. 텐류지 → 시그라쿠 토후 (아라시야마 본거리)
5. 시그라쿠 토후 → 금각사 (시버스 11 또는 12)
6. 료안지 → 가와라마치 (시버스 59 등)
7. 시오 → 후시미이나리 (지하철+JR or 택시)

## 핵심 관찰

- **walking_km 정의 명확화**: leg 단위 도보(arrive_from[mode=walk])는 declared walking_km의 **하한**. 사찰 경내·시장 산책은 별도로 추정 누적. 검사 G는 sum이 declared를 초과(+ 2km tolerance)할 때만 fail — 한 방향 검증.
- **tbd_needs_browser_mcp**: 신규 data_quality 라벨. WebFetch가 JS 렌더(Google Maps) 등으로 실패한 항목을 정직하게 "추측치 + 검증 URL" 형태로 남겨두는 패턴. 60d staleness 검사에서 면제.
- **빌드 산출물**: `card_itinerary()`와 `build_itinerary()` 모두 arrive_from을 렌더하므로 mobile #itinerary 카드 + viz/itinerary.html 상세 화면 양쪽에서 노선·소요시간이 보임.

## 보류

- tbd_needs_browser_mcp 8 leg — Playwright MCP 세션에서 처리.
- `validate.py`의 itinerary.json↔kyoto-itinerary-may31-jun3-2026.md 본문 동기화 검사(E/F 동급)는 별도 PR로 분리. 본 PR에서는 MD를 수기로 동기화.

## 다음 단계

1. 본 PR 머지 후 Playwright MCP 세션에서 tbd 라벨 8 leg 측정 → 별도 PR로 승격.
2. 항공편 시간 확정 시 5/31 첫 leg(KIX→교토역) duration_min 미세 조정.
