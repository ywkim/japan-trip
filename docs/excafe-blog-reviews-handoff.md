# 후속 세션 위임 — eX cafe·아라시야마 카페 blog_reviews 실제 네이버 후기 수집 (Playwright MCP)

> 이 문서는 **자기완결**입니다. 본 레포 `CLAUDE.md`만 읽으면 작업을 시작할 수 있습니다.
> 다른 대화 컨텍스트·세션 메모리 의존 없음.

## 1. 작업 목적

`data/itinerary.json`의 6/1 12:00 **eX cafe** 항목 `blog_reviews`에, 아라시야마 카페들의 **실제 네이버 블로그 후기 카드**를 추가한다. 현재 1장(0번, `ramu0527/223959935624`)만 있고, 그조차 URL(ramu0527)과 이미지(m0846)의 출처가 다른 조립 카드다. **검증된 실제 후기 글**로 채우는 것이 목표.

### 왜 이 작업이 후속 세션으로 위임됐나

작성 세션(2026-06-01)의 실행 환경은 **네트워크 정책이 `*.naver.com` 전체를 egress 차단**했다(실측):
- `curl https://blog.naver.com` · `rss.blog.naver.com` · `search.naver.com` → **403 "Blocked by egress policy"**
- `WebFetch` 네이버 도메인 → 차단
- `WebSearch`(US 색인) → 네이버 포스트 미색인(triple.guide·tripadvisor·영문 블로그만 반환)
- `pstatic.net` 이미지 CDN만 200(이미지 자가호스팅은 가능)

따라서 실제 네이버 글을 **찾을 수도 검증할 수도 없어** 보류됐다. **Playwright MCP(또는 naver egress 허용)가 있는 세션**은 네이버 검색·블로그 본문을 직접 열 수 있으므로 이 작업이 가능하다.

근거 일지: `docs/decision-log/2026-05-31-10-excafe-blog-reviews-not-restored-env-block.md`, `docs/decision-log/2026-06-01-excafe-blog-review-restore-one.md`

## 2. 사전 요구사항

- 본 레포(`japan-trip`) 작업 트리. 작업 브랜치는 새로 파거나 지정받은 브랜치 사용.
- **Playwright MCP** 활성(`/mcp`로 확인). `browser_navigate`·`browser_snapshot`·`browser_click` 사용 가능해야 함. (대안: 환경 네트워크 정책이 `naver.com` egress를 허용해 `WebFetch`로 본문 도달 가능하면 그것도 가능.)
- Python 3 + `uv`(CI 동일). 클론 직후 `uv sync` 1회.

## 3. 절대 규칙 (위반 시 머지 차단 — 반드시 준수)

> **이 작업의 본질은 "날조 금지"다.** 과거 PR #89에서 카페 blog_reviews 14/15장이 날조(검색 페이지·블로거 홈 URL + 합성 댓글)로 머지됐다가 적발·제거됐다. 같은 실수를 반복하면 안 된다.

근거: `CLAUDE.md` "출처 종류 정책" 절(두 축 분리), `docs/decision-log/2026-05-31-08·09·10`.

### 3-1. URL은 반드시 **특정 포스트**

- ✅ 허용: `https://m.blog.naver.com/<작성자ID>/<글번호>` (글번호 = 숫자). 예: `https://m.blog.naver.com/ramu0527/223959935624`
- ❌ **금지**: `search.naver.com/...?query=...`(검색 결과 페이지) — "후기 읽기 →"가 검색창으로 떨어짐
- ❌ **금지**: `blog.naver.com/<id>`(글번호 없는 블로거 홈) — 특정 글 미지정
- **게이트**: `tests/test_build_index.py::BlogImageSelfHostGateTests::test_naver_blog_reviews_link_to_specific_posts`가 위 금지 URL을 자동 차단한다. CI 통과 = 형식 검증 통과.

### 3-2. 댓글은 **그 글의 실제 내용** (합성 설명문 금지)

- ✅ 허용: 글 제목 또는 본문 첫 문장의 실제 발췌. 예: "여행 계획 부터 그 날 비가 오기를 바랐던 건 처음이다…"
- ❌ 금지: `[가게명] 당고 세트+말차 파르페 실식 후기. 미니 화로 직화구이…` 같은 **AI가 지어낸 가게 요약문**(과거 날조 시그니처).
- Playwright로 글을 **실제로 열어 본문을 읽고** 발췌하라. 안 읽었으면 댓글을 쓰지 마라.

### 3-3. 이미지는 **그 글의 사진** + 자가호스팅

- 글 본문의 실제 이미지 URL(`*.pstatic.net`·`blogfiles.naver.net` 등)을 `img`에 넣는다. URL·이미지 작성자가 일치해야 한다(0번처럼 URL≠이미지 출처 조립 금지).
- `img`를 채운 뒤 **반드시** `uv run python scripts/fetch_assets.py` 실행 → `assets/place-images/`·`data/local-image-map.json` 갱신 → 재커밋.
- **게이트**: `test_every_blog_image_is_self_hosted`가 모든 비어있지 않은 `img`의 자가호스팅(매핑+파일)을 강제. 미자가호스팅 = 라이브에서 mixed-content/404로 카드 사라짐 → 머지 차단.
- 글에 쓸 만한 이미지가 없으면 `img: ""`(빈 문자열)로 두라 — 텍스트 카드로 렌더(사라지지 않음). 댓글·URL은 유지.

### 3-4. 정책 축 — 카페에 한국어 blog_reviews는 **허용**

- 한국어 네이버 블로그 후기 카드는 **카페·식당에도 OK**(정책 위반 아님). 일본어 1차 출처 제한은 **사실**(가격·영업·휴무·`food_quality`·번역 문서)에만 적용된다.
- 즉 이 작업(카페 후기 카드 추가)은 정책상 정당하다. 단 3-1~3-3의 **품질**을 지켜야 한다.

## 4. 처리 대상 (아라시야마 카페 5곳)

eX cafe 항목 카드에 아래 카페들의 실제 후기를 모은다(과거 origin/main도 한 항목에 여러 카페를 섞어 담았음). 카페당 1~3장 권장, 총 8~12장 목표(전량 실제·검증).

| 가게 | 일본어 정식명 | 검색 키워드(네이버) | Tabelog(참고) |
|---|---|---|---|
| **eX cafe** | eX cafe(イクスカフェ) 京都嵐山本店 | `eX카페 아라시야마`, `이쿠스카페 교토 당고` | 26005251 |
| **% ARABICA** | % ARABICA 京都 嵐山 | `아라비카 아라시야마 카페`, `% arabica 교토 강변` | 26025913 |
| **嵯峨野湯** | 嵯峨野湯(사가노유) | `사가노유 교토 카페`, `사가노유 팬케이크` | 26005250 |
| **パンとエスプレッソと** | パンとエスプレッソと嵐山庭園 | `파앤에스 아라시야마`, `파인투에스프레소토 교토 정원` | 26032681 |
| **雲ノ茶** | 雲ノ茶(쿠모노차) 嵐山店 | `쿠모노차 아라시야마`, `雲ノ茶 교토 말차` | 26038471 |

> Tabelog ID는 가게 식별·교차 확인용 참고일 뿐 — 후기는 **네이버 글**에서 가져온다.

## 5. 실행 절차

### 5-1. 네이버에서 실제 후기 글 찾기 (Playwright)

```
browser_navigate → https://m.search.naver.com/search.naver?where=m_blog&query=<위 검색 키워드>
browser_snapshot → 블로그 글 목록에서 실제 포스트 링크(m.blog.naver.com/<id>/<글번호>) 식별
browser_click → 후보 글 진입 → 본문이 진짜 그 카페 방문기인지 확인(사진·날짜·내용)
```

확인 사항(각 글):
- URL이 `m.blog.naver.com/<id>/<숫자글번호>` 형식인가?
- 본문이 **그 카페**(eX cafe 등) 방문기가 맞는가? (제목·사진·텍스트로 확인)
- 6월/여름·시부모 동반·아라시야마 동선 등 **이 여행에 유용한 실용 정보**가 있으면 우선.
- 본문 첫 문장(또는 핵심 한 줄)을 댓글용으로 메모.
- 대표 사진 1장의 이미지 URL을 메모(같은 글의 사진).

### 5-2. data/itinerary.json 갱신

6/1 12:00 eX cafe 항목의 `blog_reviews` 배열에 카드 추가. 스키마(정확히 이 3개 키):

```json
{
  "url": "https://m.blog.naver.com/<id>/<글번호>",
  "img": "<그 글의 실제 이미지 URL, 없으면 빈 문자열>",
  "comment": "<그 글 제목/본문의 실제 발췌, 50자 내외>"
}
```

- 기존 0번 카드(`ramu0527/223959935624`)는 URL≠이미지 출처라 **검증되면 교체 권장**(같은 글의 이미지로 바꾸거나, 그 글이 실제 eX cafe 후기면 댓글을 실제 발췌로 교정). 검증 못 하면 그대로 둬도 게이트는 통과.
- `data/itinerary.json`은 파일 끝에 **트레일링 개행 없음**(레포 컨벤션). 편집 후 `tail -c 4 data/itinerary.json | od -c`로 `} \n }`로 끝나는지 확인.

### 5-3. 이미지 자가호스팅

```bash
uv run python scripts/fetch_assets.py        # img URL 다운로드 + 매핑 기록
uv run python scripts/fetch_assets.py --check # "N/N cached locally, 0 missing" 확인
```

`assets/place-images/`(새 .jpg)와 `data/local-image-map.json`을 함께 커밋.

### 5-4. 빌드·검증·테스트 (전부 통과해야 머지)

```bash
uv run python scripts/build_index.py          # 빌드 무오류
uv run python scripts/validate.py             # OK — 0 errors
uv run python -m unittest discover tests       # 전부 PASS (게이트 2종 포함)
```

육안 확인:
```bash
# eX cafe 섹션에 카드 N개·자가호스팅 경로·외부 URL 누출 0 확인
python3 -c "
html=open('viz/itinerary.html').read()
i=html.find('당고 직화구이'); s=html[i:i+12000]; n=s.find('금각사')
if n>0: s=s[:n]
print('카드:', s.count('class=\"blog-card\"'))
print('자가호스팅:', '/assets/place-images/' in s)
print('외부 누출:', 'blogthumb.pstatic' in s or 'search.naver' in s)
"
```

## 6. 산출물 (PR)

- `data/itinerary.json` (eX cafe `blog_reviews` 실제 후기 N장)
- `data/local-image-map.json` + `assets/place-images/` (새 이미지 자가호스팅)
- `docs/decision-log/YYYY-MM-DD-excafe-blog-reviews-collected.md` (ADR — 어느 글을 왜 골랐는지, 검증 방법, Playwright로 본문 확인했음을 명시)
- 본 핸드오프 문서는 작업 완료 후 "완료" 표기하거나 제거.
- **메타**: `CLAUDE.md`·`README.md`에 변경 반영(메타 문서화 규칙).

## 7. 완료 정의 (Definition of Done)

- [ ] eX cafe `blog_reviews`의 모든 URL이 `m.blog.naver.com/<id>/<글번호>` 형식(검색/홈 0개)
- [ ] 모든 댓글이 Playwright로 **실제 읽은** 글의 발췌(합성 요약 0개)
- [ ] 모든 `img`가 자가호스팅(`--check` 0 missing) 또는 의도적 빈 문자열
- [ ] URL·이미지 출처 일치(조립 카드 0개)
- [ ] `build_index` + `validate` + `unittest` 전부 통과
- [ ] decision-log + 메타 문서 갱신
- [ ] **검증 못 한 글은 추가하지 않음**(빈칸이 날조보다 낫다)
