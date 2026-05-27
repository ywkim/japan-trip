# 2026-05-26 — 조식 누락 가게 메뉴·가격 실시간 리서치

## Status

Accepted (`2026-05-26-05-breakfast-readability-menu-visible.md` 후속 — 빈 `menu` 채움)

## Context (왜)

- 직전 작업에서 `menu` 필드를 도입했으나, 2026-05-23 리서치에 구체 메뉴/가격이 없던 가게는 비워 두었다.
- 사용자 지시(2026-05-26): "없으면 리서치를 해." → 누락 가게의 모닝 메뉴·가격을 실시간 웹 리서치로 조사.
- CLAUDE.md "실시간 가격 리서치 우선": 추측 금지, 출처·검색일자·신뢰도 라벨 필수. 각 가격은 작성 전 `WebFetch`로 출처 페이지를 직접 재확인했다(미확인은 미작성).

## Decision (무엇)

출처가 확인된 가게만 `data/breakfast.json`의 `menu`를 채우고, 확인 불가/충돌/출처 없음은 정직하게 비우거나 주의를 표기한다.

**채움 (WebFetch 재확인 완료):**
- 홀리스(Holly's) 二条駅前店 — 모닝 토스트+삶은달걀 단품 ¥340 / 드링크 세트 ¥500 (Holly's 공식, official_fare).
- 스타벅스 — 고정 모닝세트 없음, 페이스트리·샌드위치 ¥310~660 (Fun Japan, researched_market_rate).
- 小川珈琲 京都駅 — 모닝세트 ¥680 (Kyotopi, official_fare).
- 월드커피 콜로라도 八条口 — 콜로라도 모닝 플레이트 ¥800 (RocketNews24, official_fare).
- 鈴屋 — 가격 총액은 출처 간 충돌(커피 ¥380 vs ¥450)이라 **금액 미기재**, 단품 조합 구조만 기술 + 영업 07:00~14:00 (japanhomeycafes, researched_market_rate).

**미채움 (출처 부재·미확인 — 추측 금지):**
- CAFFE CIAO PRESSO — 공식 페이지에 모닝 가격 미게시 → "가격 미공개, 현장 확인"으로 표기.
- Koto 카페 — 신뢰 출처 없음 → `menu` 미입력.
- 喫茶パル — 출처 없음 + 영업 여부 불확실 → `note`에 "출발 전 재확인" 주의.

부수: `researched_at` 2026-05-23 → 2026-05-26 갱신. `sources[]` 5건 추가(8→13). 사람용 사본 `docs/breakfast-near-lodging.md` 동기화.

## Consequences (그래서)

- 긍정: 조식 페이지에서 가게별 가격대(¥340~¥1,660)를 바로 비교 가능. 모든 가격에 출처·검색일자·신뢰도 라벨 부착.
- 부정·트레이드오프: 鈴屋·CIAO·Koto·喫茶パル는 가격 미확정으로 남음(현장 확인 필요). 출처 페이지는 시세성 — §4 주의(출발 전 Google Maps 재확인) 유효.
- 후속: 현지/예약 시점에 미확정 항목 재조회. 가격이 60일 이상 묵으면 재검색.
- 영향 파일: `data/breakfast.json`, `docs/breakfast-near-lodging.md`, 빌드 산출물 `viz/breakfast.html`.
