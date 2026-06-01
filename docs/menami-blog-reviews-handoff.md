# 후속 세션 위임 — 御料理めなみ(메나미) blog_reviews 실제 네이버 후기·사진 수집 (Playwright MCP)

> 이 문서는 **자기완결**입니다. 본 레포 `CLAUDE.md`만 읽으면 작업을 시작할 수 있습니다.
> 다른 대화 컨텍스트·세션 메모리 의존 없음.

## 1. 작업 목적

`data/itinerary.json`의 **6/1 17:30 御料理めなみ(메나미)** 항목에 `blog_reviews`(실제 네이버 블로그 후기 카드 — 가게 외관·내부·오반자이 음식 사진 + 실제 발췌)를 추가한다. 현재 메나미 항목은 **사진 카드가 0장**이라, 다른 외식 페이지(eX cafe·카네요·권타로)처럼 시각적으로 풍부하게 만드는 것이 목표.

### 왜 이 작업이 후속 세션으로 위임됐나

작성 세션(2026-06-01)의 실행 환경은 **네트워크 정책이 `*.naver.com` egress를 차단**해, 네이버 블로그 **특정 포스트(작성자ID/글번호)** 와 그 글의 이미지를 **찾을 수도 검증할 수도 없었다**(eX cafe 위임 때와 동일 — `docs/excafe-blog-reviews-handoff.md` 참조).

- `WebSearch`(US 색인)는 네이버 포스트를 거의 색인하지 않아, 메나미 검색 시 자체 매거진(`bricksmagazine.co.kr`)·영문 가이드만 반환
- 확인된 한국어 후기(메나미 포함)는 **bricksmagazine.co.kr**(매거진 사이트, 네이버 블로그 아님)에 있고 이미지도 `cdn.imweb.me`에 있으나, **CLAUDE.md `blog_reviews` 정책은 "네이버 특정 포스트가 정석"** 이라 그대로 쓰기 부적합 → 보류

**Playwright MCP(또는 naver egress 허용)가 있는 세션**은 네이버 검색·블로그 본문을 직접 열 수 있으므로 이 작업이 가능하다.

근거 일지: `docs/decision-log/2026-06-01-10-dinner-manzaratei-to-menami.md` (메나미 선정), `docs/decision-log/2026-05-31-09-blog-reviews-url-quality-policy-axis.md` (URL 품질 축)

## 2. 사전 요구사항

- 본 레포(`japan-trip`) 작업 트리. 작업 브랜치는 새로 파거나 지정받은 브랜치 사용.
- **Playwright MCP** 활성(`/mcp`로 확인). `browser_navigate`·`browser_snapshot`·`browser_click` 사용 가능해야 함. (대안: 환경 네트워크 정책이 `naver.com` egress를 허용해 `WebFetch`로 본문 도달 가능하면 그것도 가능.)
- Python 3 + `uv`(CI 동일). 클론 직후 `uv sync` 1회.

## 3. 절대 규칙 (위반 시 머지 차단 — 반드시 준수)

> **이 작업의 본질은 "날조 금지"다.** 과거 PR #89에서 카페 blog_reviews 다수가 날조(검색 페이지·블로거 홈 URL + 합성 댓글)로 머지됐다가 적발·제거됐다. 같은 실수를 반복하면 안 된다.

근거: `CLAUDE.md` "출처 종류 정책" 절(두 축 분리), `docs/decision-log/2026-05-31-08·09·10`.

### 3-1. URL은 반드시 **특정 포스트**
- ✅ 허용: `https://m.blog.naver.com/<작성자ID>/<글번호>` (글번호 = 숫자)
- ❌ **금지**: `search.naver.com/...?query=...`(검색 결과 페이지), `blog.naver.com/<id>`(글번호 없는 블로거 홈)
- **게이트**: `tests/test_build_index.py::BlogImageSelfHostGateTests::test_naver_blog_reviews_link_to_specific_posts`가 위 금지 URL을 자동 차단.

### 3-2. 댓글은 **그 글의 실제 내용** (합성 설명문 금지)
- ✅ 허용: 글 제목 또는 본문 첫 문장의 실제 발췌
- ❌ 금지: `[메나미] 오반자이 정식 실식 후기. 80년 노포…` 같은 **AI가 지어낸 가게 요약문**(과거 날조 시그니처)
- Playwright로 글을 **실제로 열어 본문을 읽고** 발췌하라. 안 읽었으면 댓글을 쓰지 마라.

### 3-3. 이미지는 **그 글의 사진** + 자가호스팅
- 글 본문의 실제 이미지 URL(`*.pstatic.net`·`blogfiles.naver.net` 등)을 `img`에 넣는다. URL·이미지 작성자가 일치해야 한다(조립 금지).
- `img`를 채운 뒤 **반드시** `uv run python scripts/fetch_assets.py` 실행 → `assets/place-images/`·`data/local-image-map.json` 갱신 → 재커밋.
- **게이트**: `test_every_blog_image_is_self_hosted`가 모든 비어있지 않은 `img`의 자가호스팅(매핑+파일)을 강제.
- 글에 쓸 만한 이미지가 없으면 `img: ""`(빈 문자열)로 — 텍스트 카드로 렌더(사라지지 않음).

### 3-4. 정책 축 — 식당에 한국어 blog_reviews는 **허용**
- 한국어 네이버 블로그 후기 카드는 **식당에도 OK**(정책 위반 아님). 일본어 1차 출처 제한은 **사실**(가격·영업·휴무·`food_quality`·번역 문서)에만 적용된다.
- 즉 이 작업(메나미 후기 카드 추가)은 정책상 정당하다. 단 3-1~3-3의 **품질**을 지켜야 한다.
- **메뉴·가격·영업·휴무 등 사실은 절대 한국어 블로그에서 인용하지 말 것** — 그건 `docs/menami-review-translation.md`가 일본어 1차 출처(menami.jp·Tabelog 26001266)로 이미 채웠다. blog_reviews는 "경험 공유 링크"만.

## 4. 처리 대상 (메나미 1곳)

| 가게 | 일본어 정식명 | 검색 키워드(네이버) | Tabelog(참고) |
|---|---|---|---|
| **御料理めなみ** | 御料理めなみ (키야마치 산조, 1939년 오반자이 노포) | `교토 메나미 오반자이`, `메나미 키야마치 맛집`, `御料理めなみ 후기`, `교토 메나미 저녁` | 26001266 |

> 카드 2~4장 목표(전량 실제·검증). 가게 외관·카운터에 늘어놓은 오반자이·생선구이/오리구이 등 **음식 사진**이 있는 글 우선.

## 5. 실행 절차

### 5-1. 네이버에서 실제 후기 글 찾기 (Playwright)
```
browser_navigate → https://m.search.naver.com/search.naver?where=m_blog&query=교토 메나미 오반자이
browser_snapshot → 블로그 글 목록에서 실제 포스트 링크(m.blog.naver.com/<id>/<글번호>) 식별
browser_click → 후보 글 진입 → 본문이 진짜 메나미 방문기인지 확인(사진·날짜·내용)
```
확인 사항(각 글):
- URL이 `m.blog.naver.com/<id>/<숫자글번호>` 형식인가?
- 본문이 **메나미(御料理めなみ)** 방문기가 맞는가? (제목·사진·텍스트로 확인 — 동명이인 가게/지점 주의)
- 6월/여름·시부모 동반·술 없이 식사·오반자이 추천 메뉴 등 **이 여행에 유용한 실용 정보**가 있으면 우선.
- 본문 첫 문장(또는 핵심 한 줄)을 댓글용으로 메모.
- 대표 사진 1장(같은 글의 사진)의 이미지 URL을 메모.

### 5-2. data/itinerary.json 갱신
6/1 17:30 메나미 항목에 `blog_reviews` 배열을 추가(현재 없음). 스키마(정확히 이 3개 키):
```json
"blog_reviews": [
  {
    "url": "https://m.blog.naver.com/<id>/<글번호>",
    "img": "<그 글의 실제 이미지 URL, 없으면 빈 문자열>",
    "comment": "<그 글 제목/본문의 실제 발췌, 50자 내외>"
  }
]
```
- 삽입 위치: 메나미 항목의 `link` 앞(또는 `food_quality` 뒤) — 다른 항목(eX cafe 등)의 `blog_reviews` 위치를 참고.
- `data/itinerary.json`은 파일 끝 **트레일링 개행 없음**(레포 컨벤션). 편집 후 확인.

### 5-3. 이미지 자가호스팅
```bash
uv run python scripts/fetch_assets.py         # img URL 다운로드 + 매핑 기록
uv run python scripts/fetch_assets.py --check # "N/N cached locally, 0 missing" 확인
```
`assets/place-images/`(새 .jpg)와 `data/local-image-map.json`을 함께 커밋.

### 5-4. 빌드·검증·테스트 (전부 통과해야 머지)
```bash
uv run python scripts/build_index.py          # 빌드 무오류
uv run python scripts/validate.py             # OK — 0 errors
uv run python -m unittest discover tests       # 전부 PASS (게이트 2종 포함)
```
육안 확인: `viz/itinerary.html`·`index.html`의 6/1 메나미 카드에 사진 strip이 뜨고, "후기 읽기 →"가 실제 네이버 글로 가는지. 외부 URL 누출(`search.naver`·미자가호스팅 이미지) 0개.

## 6. 산출물 (PR)
- `data/itinerary.json` (메나미 `blog_reviews` 실제 후기 N장)
- `data/local-image-map.json` + `assets/place-images/` (새 이미지 자가호스팅)
- `docs/decision-log/YYYY-MM-DD-menami-blog-reviews-collected.md` (ADR — 어느 글을 왜 골랐는지, Playwright로 본문 확인했음을 명시)
- 본 핸드오프 문서는 작업 완료 후 "완료" 표기하거나 제거.
- **메타**: `CLAUDE.md`·`README.md`에 변경 반영(메타 문서화 규칙).

## 7. 완료 정의 (Definition of Done)
- [ ] 메나미 `blog_reviews`의 모든 URL이 `m.blog.naver.com/<id>/<글번호>` 형식(검색/홈 0개)
- [ ] 모든 댓글이 Playwright로 **실제 읽은** 글의 발췌(합성 요약 0개)
- [ ] 모든 `img`가 자가호스팅(`--check` 0 missing) 또는 의도적 빈 문자열
- [ ] URL·이미지 출처 일치(조립 카드 0개)
- [ ] `build_index` + `validate` + `unittest` 전부 통과
- [ ] decision-log + 메타 문서 갱신
- [ ] **검증 못 한 글은 추가하지 않음**(빈칸이 날조보다 낫다)

## 8. 범위 명확화 — 이 작업은 "일정 카드 blog_reviews"만

> **번역 페이지(`docs/menami-review-translation.md`)의 본문 사진은 이미 공식 menami.jp 갤러리로 채워졌다**(CLAUDE.md 출처정책 "축 3" — 번역 페이지 이미지는 네이버 불필요·게이트 비대상). 따라서 본 handoff의 대상은 **`data/itinerary.json`의 일정 카드 `blog_reviews`**(축 2 — 네이버 특정 포스트 강제·자가호스팅 게이트)뿐이다.

- 비-네이버 후보(`bricksmagazine.co.kr` 등)는 **일정 카드 `blog_reviews`엔 부적합**(네이버 특정 포스트가 아니므로). blog_reviews는 반드시 §3-1의 `m.blog.naver.com/<id>/<글번호>` 형식 + 그 글의 실제 이미지로.
- 만약 일정 카드 blog_reviews를 끝내 못 채우면, 번역 페이지 사진(공식 갤러리)으로 시각 정보는 이미 충분하므로 **빈 채로 두어도 무방**(빈칸이 날조보다 낫다).
