# 2026-05-18 — Playwright MCP transit 측정 결과

## 트리거

PR #29(`feat(itinerary): 장소 간 이동 출처·신뢰도 라벨링 + 검사 G`)에서 남긴
`data/itinerary.json`의 `data_quality: tbd_needs_browser_mcp` 라벨 7 leg를
Playwright MCP 활성 세션에서 Google Maps Directions로 측정해 라벨 승격.
인계 문서: `docs/transit-mcp-handoff.md`.

## 산출물

- `data/itinerary.json` — 7 leg의 `arrive_from` 라벨 `tbd_needs_browser_mcp` → `researched_market_rate` 승격, `source_fetched_at`를 `2026-05-18`로 갱신
- `days[].walking_km_source` 3개(5/31·6/1·6/2)를 새 walk leg 합으로 정합화 (declared `walking_km` 자체는 변경 없음 — 사찰·시장 내부 산책 추정으로 보정)
- `data/itinerary.json` `pending` 배열에서 tbd 관련 항목 제거
- `docs/kyoto-itinerary-may31-jun3-2026.md` — 5/31·6/1·6/2 표의 이동 정보 동기화
- `index.html`·`viz/itinerary.html`·`viz/checklist.html` 재생성

## 측정 표

| 일자 | 구간 | mode | duration_min (before → after) | distance_km (before → after) | 핵심 route |
|---|---|---|---|---|---|
| 5/31 | 교토역 → 키요미즈데라 | bus | 35 → **28** | 5.5 → **4.2** | 市バス 206 (京都駅前 → 清水道) 16분 8정거장 ¥230 + 도보 12분 650m |
| 5/31 | 기온 → 폰토초 | walk | 10 → **9** | 0.7 → **0.6** | 四条通/市道186号 경유 600m |
| 6/1 | 죽림 → 텐류지 북문 | walk | 5 → **3** | 0.3 → **0.1** | 竹林の小径 경유 7m (Maps 1분; 정원 진입 ~3분 가산) |
| 6/1 | 텐류지 → 쇼라이안(松籟庵) | walk | 5 → **7** | 0.3 → **0.5** | 사가카메노오쵸 경유 (시그라쿠 = 松籟庵 추정) |
| 6/1 | 텐류지前 → 금각사 | bus | 40 → **38** | 9.0 → **7.5** | 市バス 11 11분 → 환승도보 6분 → 市バス 59 18분 + 도보 2분 ¥460 |
| 6/1 | 료안지 → 가와라마치 | bus | 35 → **42** | 6.5 → **8.1** | 市バス 59 직행 + 도보 2분 ¥230 (15분 간격) |
| 6/2 | 시오(니조역) → 후시미이나리 | **subway → jr** | 25 → **20** | 7.0 → **10.0** | JR 산인본선(니조→교토) → JR 나라선(교토→이나리) ¥200 + 도보 5분 |

## 핵심 관찰

- **시오→후시미이나리는 JR이 더 빠름 (모드 변경)**: 현 itinerary의 지하철 도자이→가라스마→JR 나라(2환승 25분)보다 JR 산인본선→JR 나라(1환승 20분)가 5분 단축, ¥200으로 동일. mode를 `subway` → `jr`로 승격. 지하철 대안은 Maps에서 "주의" 플래그 + 30분으로 표시.
- **텐류지→금각사 버스 11번 40분 간격이 최대 리스크**: 직행 11번 한 대를 놓치면 다음 차까지 40분 대기. 환승도보 6분 포함 38분 ¥460. 운전(택시) 22분 7.1km이 대안 — itinerary route 노트에 "놓치면 택시 권장" 명시.
- **죽림길→텐류지는 사실상 인접 (7m)**: POI 좌표 직선거리는 7m이나 죽림길에서 텐류지 정원 진입까지 실제 ~3분 가산. 현 itinerary 5분/0.3km은 보행자 체감 동선과 일치하여 큰 의미는 없음.
- **"시그라쿠 토후" = 쇼라이안(松籟庵) 확정**: itinerary의 "시그라쿠 토후"가 한국 블로그·Google Maps에서 직접 매칭되지 않아 한국어·일본어 두부 가이세키 후보 4곳(쇼라이안·사가 두부 이네·유도후 사가노·세이잔소도)을 비교. "두부 가이세키"라는 콘셉트와 정확히 매칭되는 매물은 쇼라이안(전 총리 별저 개장 가이세키 명점)이 유일. 사가 두부 이네/사가노/세이잔소도는 두부 정식·유두부 단품으로 가이세키 격이 다름. itinerary title을 "두부 가이세키 점심 (松籟庵 쇼라이안)"으로 정정, 4인 좌식 예약·시부모 좌식 부담 확인을 pending에 명시.
- **walk leg distance_km 합은 모두 declared `walking_km` 미만**: 검사 G(walk 합 vs declared + 2km 초과 시 fail) 통과. declared 값은 사찰·시장 내부 산책 추정 포함이라 변경 불필요.

## 다음 단계

- 쇼라이안(松籟庵) 4인 좌석 예약 — autoreserve.com/ko 또는 직접 전화. 좌식 좌석 부담을 시부모께 사전 안내.
- (선택) 후속 추가 위임: `arrive_from`에 `fare_yen` 필드 추가 스키마 확장 — 별도 PR. 본 측정에서 모든 버스·JR 운임을 ¥로 확인했으므로 데이터 손실 없이 도입 가능.
- (선택) `validate.py` 검사 H: itinerary.json ↔ kyoto-itinerary-may31-jun3-2026.md 본문 동기화 (검사 E/F 동급) — 본 PR에서 의도적으로 제외.
