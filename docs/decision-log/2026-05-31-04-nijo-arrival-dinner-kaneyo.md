# 2026-05-31 — 5/31 도착날 저녁 폰토초 엔엔 → 교고쿠 카네요(우나기 킨시동)

## Status

Accepted

## Context (왜)

- 5/31(일)은 에어서울 KIX 15:15 도착·17:45 시오 체크인이라 **첫날은 체크인+저녁만** 가능한 빠듯한 날이고, 피곤한 시부모 2인을 동반한다.
- 기존 `data/itinerary.json` 5/31 저녁은 **폰토초 야끼니꾸 엔엔(京都焼肉 enen)** + **가모강·폰토초 야경 산책**으로 구성. 문제점:
  - 1인 ¥5,000~6,000으로 고가.
  - 이동 출처(`arrive_from`)가 `tbd_needs_browser_mcp`(미검증)로 남아 있었다.
- 이 브랜치(`pontocho-restaurant-efficiency`)의 동기는 도착날 저녁 동선·비용을 시부모 친화적으로 재검토하는 것.
- 사용자가 실시간 리서치(2026-05-31)를 거쳐 후보를 비교한 뒤 **교고쿠 카네요(京極かねよ)** — 우나기 명물 **킨시동(きんし丼)** 을 최종 선택.
- 검증 사실(2026-05-31): 타베로그 3.49(리뷰 1,399), 킨시동 並¥3,000/上¥4,000/特¥6,100, 일요일 17:00~20:30(L.O.20:00)·수요일 휴무, 中京区 新京極通六角. 이동은 지하철 도자이선 **二条→京都市役所前 6분·¥220·환승 없음**(에키탄·교토시 교통국) + 도보 7분.

## Decision (무엇)

- 5/31 저녁(items[4])을 **교고쿠 카네요**로 교체하고, 식후 20:00 슬롯(items[5])은 카네요 바로 옆 **신쿄고쿠(新京極) 상점가 지붕 아케이드 산책**으로 교체한다.
- `arrive_from` 동선 출처를 `tbd_needs_browser_mcp` → `researched_market_rate`(에키탄·교토시 교통국, ¥220·6분)로 갱신.
- 비채택 대안:
  - **엔엔(폰토초 야끼니꾸)**: 1인 ¥5~6k로 고가 — 도착날 비용·부담 큼.
  - **나카나카(니조역 도보권 오코노미야키)**: 시오 도보권이라 동선은 최단이나 평점·명물성이 낮아 미채택.
  - **가모강·폰토초 야경 산책**: 식후 동선상 카네요에서는 신쿄고쿠/데라마치 아케이드가 더 가깝고 우천 대비도 되어 대체.

## Consequences (그래서)

- 긍정:
  - 1인 비용이 약 절반(¥3,000~4,000)으로 감소, 단일 명물 메뉴(킨시동)라 시부모 주문이 단순.
  - 운임이 ¥220·6분(공식 운임 확인)으로 확정 — 기존 미검증(`tbd`) 동선 출처 1건 해소.
  - 식당 바로 옆이 지붕 아케이드라 식후 산책·우천 대비가 자연스럽다.
- 부정·트레이드오프:
  - 카네요는 다운타운(新京極)이라 **시오 도보권이 아니다** — 엔엔과 마찬가지로 지하철 이동이 필요(동선 단축은 아님).
  - 일요 L.O.20:00이라 18:30 착석을 권장(여유 시간 감소).
- 후속 행동: 예약은 사용자 확인 후 넷예약(핫페퍼 strJ000903290·타베로그 26001330) 또는 전화로 실행.
- 영향 받은 파일: `data/itinerary.json`(places 3개 추가 + items[4]/[5] + day 메타), `docs/kyoto-itinerary-may31-jun3-2026.md`(§1.1·§3 사본 동기화), `tests/test_build_index.py`(food-note 폴딩 회귀 가드 production 문자열 갱신). `cost-options.json`은 5/31 지하철이 기존에도 미계상이라 변경 불필요.

### 후속 보강 (같은 PR) — 카네요 후기·메뉴 추가

- **Context**: 가족이 화면에서 카네요 후기·메뉴를 바로 보도록 보강 요청.
- **Decision**: 카네요 항목(items[4])에 ① `food_quality.note` 메뉴를 전체 메뉴(킨시동/우나기동 並·上·特, 키모야키 ¥1,500·키모스이 ¥500·우나기 카이세키 코스 ¥15,000·포장 +¥100)로 확장, ② `blog_reviews` 2장 추가(실제 한국어 후기 블로그 flywithmoxie의 자체 호스팅 이미지 2장 — HTTP 200·referer-less 검증, `fetch_assets.py`로 자가호스팅). 후기 문구는 flywithmoxie·타베로그 일본어 口コミ·검색 요약의 실제 평가를 자연스러운 한국어로 옮긴 것(추측 금지). 출처 주의: `かね正`(기온)는 동명이점이라 제외, `京極かねよ`만 사용.
### 후속 보강 2 (같은 PR) — 일본어 후기 번역 페이지 + 후기 카드 in-site 링크 경로 버그픽스

- **Context**: 후기를 일본어 원문(unagiudou.com 2025-05-27) 한국어 전문 번역 페이지로 추가 요청. 추가 후 Vercel에서 `/kaneyo-review.html` 404 발생.
- **Decision**: ① `docs/kaneyo-review-translation.md`(전문 번역) 추가 + `build_index.py` `DOC_PAGES`에 `viz/kaneyo-review.html` 등록, ② `itinerary.json` blog_reviews url을 외부 URL → 사이트 내 `kaneyo-review.html`로 변경. ③ **버그픽스**: `blog_reviews_html`이 url을 무보정으로 출력해 동일 카드가 루트(`index.html`)·viz(`viz/itinerary.html`) 양쪽에 렌더될 때 루트에서 bare 상대경로가 `/kaneyo-review.html`(404)로 깨졌다. `doc_link_html`과 동일 규칙(`_blog_card_href`)으로 in_viz에 따라 `viz/` 접두어를 보정하고, 내부 링크는 같은 탭·외부는 새 탭으로 분기.
- **Consequences (2)**: `blog_reviews_html(reviews, in_viz)` 시그니처 변경(viz 호출 2곳 `in_viz=True`). TDD로 테스트 2건 선행 추가(루트 viz/ 접두어·viz bare·외부 새 탭). 검사 J(github 링크)·K 무관(blog_reviews 미스캔). 외부 URL 후기는 기존대로 새 탭 동작 유지.

- **Consequences**: 메뉴·후기 출처는 공식 사이트(kyogoku-kaneyo.co.jp)·flywithmoxie·Tabelog(26001330)·공식 메뉴 2026-05-31. `data/local-image-map.json`에 매핑 4건 추가(flywithmoxie 2 + 부수적으로 기존 외부였던 아라시야마 죽림 후기 pstatic 썸네일 2장도 자가호스팅 — 오프라인 커버리지 개선). `test_build_index`의 food-note 폴딩 회귀 가드 detail-tail 문자열을 새 메뉴(우나기동 並¥3,200…)로 갱신. `validate.py` 검사 K는 `blog_reviews.comment`를 스캔하지 않아 후기 문구는 무관, `food_quality.note`(스캔 대상)에는 생(生) 레지스트리 장소명을 넣지 않음.

### 후속 보강 3 (같은 PR) — 신쿄고쿠 상점가 후기 번역 페이지 + blog_reviews + UI 개선 + 메타 문서화

- **Context**: 사용자 요청: ① 신쿄고쿠 야경 산책(items[5])에도 일본어 후기 번역 추가, ② UI 아름답게, ③ 메타 문서화(README·CLAUDE.md 갱신).
- **Decision**:
  1. `docs/shinkyogoku-review-translation.md` 신규 — 신쿄고쿠 상점가 진흥조합 공식 자료·note.com 복수 방문기 번역·재구성. Wikimedia Commons CC 이미지 2장 사용(Shinkyogoku_Shotengai.jpg·LondonYaki.jpg).
  2. `build_index.py` `DOC_PAGES`에 `viz/shinkyogoku-review.html` 등록.
  3. `data/itinerary.json` items[5]에 `blog_reviews` 2장 추가(url: `shinkyogoku-review.html`, Wikimedia 이미지).
  4. `scripts/fetch_assets.py`로 Wikimedia 이미지 자가호스팅 → `data/local-image-map.json` 갱신.
  5. **UI 개선**: 블로그 카드 너비 140→156px·이미지 높이 100→112px·`border-radius` 6→8px·scroll-snap·`-webkit-scrollbar: none`·`:active` opacity·`.blog-read "후기 읽기 →"` 라벨 추가. TDD: `test_blog_reviews_read_more_label`·`test_blog_reviews_css_present`(blog-read 클래스) 선행 추가.
  6. **메타 문서화**: `README.md`에 `viz/kaneyo-review.html`·`viz/shinkyogoku-review.html` 1줄씩 추가. `CLAUDE.md` DOC_PAGES "현재 8 페이지"로 갱신 + 디렉토리 트리에 신규 파일 4개 추가.
- **Consequences**:
  - 긍정: 5/31 저녁·야경 산책 두 슬롯 모두 blog_reviews 카드를 통해 상세 후기 페이지로 이동 가능. 카드 UI가 더 세련되고 탭 목적이 명확해짐.
  - 이미지 출처: Wikimedia Commons (CC-BY-SA), referer 없이 접근 가능 — `fetch_assets.py`로 자가호스팅 확인.
  - 영향 받은 파일: `docs/shinkyogoku-review-translation.md`(신규), `data/itinerary.json`(items[5] blog_reviews), `scripts/build_index.py`(DOC_PAGES·CSS·blog_reviews_html), `data/local-image-map.json`(2건 추가), `README.md`, `CLAUDE.md`, `tests/test_build_index.py`(2개 테스트 추가).
