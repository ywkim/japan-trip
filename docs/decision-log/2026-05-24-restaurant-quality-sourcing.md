# 2026-05-24 — 일정 식당 품질 검증·출처화 (맛집 vs 마케팅)

## Status

Accepted

## Context (왜)

- `data/itinerary.json`의 식사 항목은 **음식 품질 근거가 0건**이었다. 확정 일정의 명시 식당 3곳(쇼라이안·교토역 라멘코지·카덴쇼)은 이름·메모만 있고 평점·출처가 없었고, 라멘코지는 "동선"으로·카덴쇼는 "료칸 끼워팔기"로 선정돼 맛 검증이 아니었다. 라멘코지는 단일 맛집이 아니라 푸드코트다.
- 5/31 도착 점심, 가와라마치·폰토초·니시키 시장 저녁은 식당이 아니라 **동네**("거기서 알아서") 수준으로 구체 점포가 없었다.
- 항목에 붙은 유일한 후기(`blog_reviews`)는 **관광지에만** 있고 전부 네이버 블로그 — 협찬·광고에 취약하고 맛 평가가 아닌 사진·동선 글이다. 타베로그·구글·미쉐린 등 객관 지표는 레포에 전무했다.
- CLAUDE.md "실시간 가격/시세 리서치 우선" 규칙(가격엔 `source`+`data_quality` 강제)이 **식당 선정 품질에는 적용돼 있지 않았다.**
- 사용자 지시(2026-05-24): (1) 지정 식당 3곳 + 동네 끼니까지 구체 점포로 검증, (2) 평판이 약한 곳은 더 검증된 대안으로 교체.

## Decision (무엇)

식사 항목에 `food_quality` 객체(`rating`·`source`·`source_fetched_at`·`data_quality`·`note`)를 신설하고, 실시간 리서치(타베로그·구글·미쉐린·여행 예약 사이트 교차검증)로 6개 끼니를 검증/교체했다.

| 끼니 | 결정 | 근거 (2026-05-24 검색) |
|---|---|---|
| 5/31 점심 | **大鵬 (二条, 쓰촨 중식)** 으로 구체화 | 타베로그 3.76 · 미쉐린 빕구르망 2024 · 中国料理WEST百名店. 니조역 도보 5분(시오 인접) |
| 5/31 저녁 | "가와라마치 저녁(동네)" → **豆八 (폰토초)** | 타베로그 3.43(246). 4인 호리고타쓰 완전개실(시부모 좌식) |
| 6/1 점심 | **쇼라이안(松籟庵)** 유지 + 출처화 | 타베로그 3.59(353)·점심 ¥3,800~. 강변 두부 가이세키 |
| 6/1 저녁 | "가와라마치+니시키(동네)" → **まんざら亭 (폰토초)** | 타베로그 3.30(92)·130년 마치야. 니시키 시장은 17시 마감→주간 |
| 6/2 점심 | "라멘코지(푸드코트)" → **中村商店 (金の塩)** | 타베로그 3.56(603) — 라멘코지 최고점(라멘은 3.5+면 최상급) |
| 6/2 저녁 | **카덴쇼 가이세키** 유지 + 출처화 | 야후트래블 4.50/5(148)·一休 4.51(147). 예약 료칸 포함 석식(교체 불가) |

검증 인프라도 확장했다.
- `scripts/validate.py`: 검사 **H**(`check_itinerary_food_quality`) 신설 — food_quality가 있는 항목에 한해 필수 필드·`data_quality` 화이트리스트·60일 staleness 검사. `route_candidates`도 순회. (검사 G 미러링)
- `scripts/build_index.py`: `food_quality_html()` 헬퍼로 `viz/itinerary.html`·`viz/itinerary-table.html`에 평점 배지 렌더. 운영 요약 `index.html`은 제외.
- 채택하지 않은 대안: 동네 끼니를 그대로 두기 → 사용자 지시(교체)로 기각. 라멘코지를 푸드코트 통칭 유지 → 최고점 점포(中村商店) 지정으로 대체.

## Consequences (그래서)

- 긍정: 6개 끼니 전부 객관 평점+출처로 검증됨. "전부 맛집인가 마케팅인가"에 데이터로 답 가능. 가격 규율과 동일한 품질 규율이 식사에도 확립(검사 H가 출처 없는 식당 머지 차단).
- 부정·트레이드오프: 확정 코스의 4개 끼니가 교체/구체화됨(5/31·6/1 저녁, 5/31 점심 식당 지정, 6/2 라멘 점포 지정). `food_quality`는 60일 staleness 적용 → 예약 시점 재검색 필요. 大鵬·豆八 등은 예약·웨이팅 부담이 있어 도착편 지연 시 대안을 note에 병기.
- 후속: 예약 확정 시 평점 재검색. `route_candidates`(미식형 등)에는 아직 food_quality 미부여 — 필요 시 별도 PR.
- 영향 파일: `data/itinerary.json`, `scripts/validate.py`, `scripts/build_index.py`, `tests/test_validate.py`, `tests/test_build_index.py`, 빌드 산출물 12개(`index.html`·`viz/*.html`·`assets/og-*.svg`), `docs/kyoto-itinerary-may31-jun3-2026.md`, `README.md`, `CLAUDE.md`.

## Test plan

- [x] `python -m unittest discover -s tests` — FoodQualityTests(검사 H)·FoodQualityRenderTests 포함 전부 통과
- [x] `python scripts/validate.py` — 검사 H 포함 exit 0
- [x] `python scripts/build_index.py` 재빌드 후 `--check` drift 0
- [x] `viz/itinerary.html` 식사 카드에 평점·출처 배지 노출 확인
- [x] 마크다운 사본 식당명·평점 동기화(시그라쿠 토후→쇼라이안 불일치 해소)
