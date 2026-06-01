# 2026-05-31 — 카페 blog_reviews 카드 "있다가 없다가" 회귀 포스트모템

## Status

Accepted

## Context (왜)

eX cafe(6/1 12:00) blog_reviews 카드가 배포 사이트에서 **반복적으로 사라졌다 나타났다** 한다는 사용자 지적(2026-05-31, "또 없어졌어 계속 있다가 없다가"). git 히스토리를 추적해 근본 원인을 규명했다.

### 증상의 실제 원인 (regression의 메커니즘)

1. **미매핑 외부 이미지의 mixed-content/404 실패**: 6/1 12:00 `blog_reviews` 15장 중 **6장이 `http://blogthumb.pstatic.net/...`(Naver 썸네일)** 였고, 이들은 `data/local-image-map.json`에 **매핑되지 않아 자가호스팅되지 않았다**. 따라서 `build_index.py`의 `local_src()`가 외부 URL을 그대로 렌더했다.
   - 라이브 사이트는 **HTTPS**(`nihon-trip.vercel.app`)인데 `http://` 이미지는 브라우저가 **mixed-content로 차단**한다.
   - 추가로 6장 중 **3장은 원본이 이미 404(영구 사망)**, 3장은 200(자가호스팅 가능)이었다(2026-05-31 curl 검증).
2. **`onerror`가 카드를 통째로 숨김**: `blog_reviews_html()`의 `<img onerror="this.closest('.blog-card').style.display='none'">` 가 이미지 로드 실패 시 **카드 전체(댓글·후기 링크 포함)를 `display:none`** 처리했다. 그래서 위 6장의 이미지 실패 → 6개 카드가 라이브에서 **조용히 사라졌다**. 로컬 프리뷰(자가호스팅된 9장만 보이거나, 빌드 시점 상태에 따라)와 라이브가 달라 "있다가 없다가"로 보였다.

### 직전 포스트모템의 오진 (재발의 진짜 이유)

`docs/decision-log/2026-05-31-04-excafe-manzaratei-fabrication-postmortem.md`는 같은 증상을 다루며 다음과 같이 **오진하고 종결**했다:

> **오해였던 항목 (실제로는 정상)**: "origin/main 카드 블로그를 계속 대체하는가?" — `blog_reviews`(15장)는 origin/main과 **바이트 동일**. 두 배포는 같은 가로 카드 스트립을 **다른 위치로 스크롤한 화면**이었음. 데이터 변경 없음.

데이터가 origin/main과 동일하다는 사실은 맞았으나, **그 15장 중 6장이 라이브에서 실패해 숨겨진다는 점**을 놓쳤다. "스크롤 위치 착시"로 결론지어 **근본 원인(미자가호스팅 http:// + onerror 카드숨김)을 고치지 않았고**, 그래서 재발했다.

### 데이터 처닝 타임라인 (git 히스토리)

| 커밋 | blog_reviews | http:// | 비고 |
|---|---|---|---|
| `4b75831` (PR #88 확장) | 2 | 2 | Naver 썸네일 도입 |
| `b05f7eb` | 1 | 0 | Wikimedia로 교체·자가호스팅 |
| `9d14c85` | 12 | 0 | "restore" — img 전부 빈 문자열 |
| `e9b5a4a` | 12 | 2 | "restore original Naver images" — http 부활 |
| `30c28f2` | 15 | 6 | "원상복구" — **15장·http 6장 유입, fetch_assets 미실행** |
| `56b7a03`(HEAD) | 15 | 6 | 동일 상태 유지 |

여러 차례의 "restore/원상복구" 커밋이 이미지를 빈값↔Wikimedia↔Naver-http로 오갔고, **매번 `fetch_assets.py`를 재실행하지 않아** `local-image-map.json`이 데이터와 어긋났다.

### 구조적 공백

- `scripts/fetch_assets.py --check`는 누락 매핑(8개)을 **정확히 감지**하지만 **CI 게이트(`.github/workflows/validate.yml` / unittest)가 아니다**. 그래서 미자가호스팅 드리프트가 PR 단계에서 **보이지 않게 통과**했다.
- 기존 `SelfHostedImageTests`는 "매핑된 URL이 HTML에 누출 안 되는지"만 검사하고, **"모든 blog_reviews 이미지가 매핑됐는지"(역명제)는 검사하지 않았다** — 미매핑 URL은 트리비얼하게 통과.
- `test_blog_reviews_have_images`는 오히려 **HTML에 `pstatic.net`이 있기를 기대**해, 자가호스팅(외부 URL→로컬 치환) 목표와 모순됐다(미매핑 이미지가 있어야 통과하는 역설).

## Decision (무엇)

"카드가 조용히 사라지는" 결함을 **구조적으로 봉쇄**한다.

1. **살릴 수 있는 이미지 자가호스팅**: `fetch_assets.py` 재실행 → eX cafe 3장(200) + 금각사 니시키시장 1장(Wikimedia) 등 4장 신규 다운로드(`assets/place-images/` + `local-image-map.json` 갱신). 결과: `--check` 48/48, 0 missing.
2. **죽은(404) 이미지는 `img`를 빈 문자열로**: eX cafe 3장 + 금각사 1장(원본 404). **리뷰 자체(댓글·"후기 읽기" 링크)는 보존**하고 깨진 썸네일 참조만 제거 — 카드는 텍스트 전용으로 렌더(사라지지 않음). 리뷰 삭제 아님.
3. **`onerror` 강화 — 카드가 아니라 이미지만 숨김**: `this.closest('.blog-card').style.display='none'` → `this.style.display='none'`. 향후 어떤 이미지 실패도 카드(댓글·링크)를 통째로 사라지게 하지 않는다(2차 방어). 1차 보증은 전수 자가호스팅.
4. **CI 게이트 신설 — `BlogImageSelfHostGateTests`**: 비어있지 않은 모든 `blog_reviews.img`는 `local-image-map.json`에 매핑 + 로컬 파일 존재해야 한다. 위반 시 unittest(=CI 게이트) 실패. 미자가호스팅 드리프트를 머지 단계에서 차단. route_candidates도 순회.
5. **취약 테스트 수정**: `test_blog_reviews_have_images`가 `pstatic.net` 대신 `/assets/place-images/`(로컬 치환)를 기대하도록 정정.

채택하지 않은 대안:
- **죽은 카드 4개 완전 삭제**: 사진 스트립이 균일해지나, 사용자가 추가한 리뷰 링크를 잃음. 비파괴적인 `img=""`(텍스트 카드 유지)를 우선. 사용자가 균일 스트립을 원하면 후속 제거 가능.
- **`fetch_assets.py --check`를 validate.yml에 추가**: 유효하나 네트워크 의존(다운로드 시도). unittest 게이트는 **네트워크 비의존**(로컬 매핑·파일만 확인)이라 결정론적 — 더 우월.
- **eX cafe(카페)에 일본어 Tabelog 사진으로 재소싱**: 출처 정책(2026-05-31-06)상 카페는 일본어 1차 출처지만, blog_reviews는 사용자가 명시적으로 원한 한국 여행자 후기 카드 — 재소싱은 별도 결정. 본 PR은 "사라짐" 버그 해소에 한정.

## Consequences (그래서)

**긍정**:
- 15개 카드가 라이브에서 더 이상 사라지지 않음(12 사진 + 3 텍스트, 외부 URL 누출 0).
- `BlogImageSelfHostGateTests`가 미자가호스팅 이미지를 **머지 차단** — 같은 회귀의 재발을 구조적으로 봉쇄(이번이 3번째 처닝).
- `onerror` 강화로 이미지 실패가 카드를 삭제하지 않음 — "조용한 사라짐" 클래스 제거.
- 직전 포스트모템의 오진(스크롤 착시)을 정정·기록 — 후속 세션이 같은 함정에 빠지지 않음.

**부정·트레이드오프**:
- eX cafe 3장 + 금각사 1장이 텍스트 전용 카드(썸네일 없음)로 남음 — 사진 스트립에 섞이면 시각적 비균일. 원본이 404라 자가호스팅 불가가 근본 제약. 균일 스트립을 원하면 카드 제거가 후속 옵션.
- 3,189B(100×67) 저화질 썸네일 1장 포함 — 유효한 실사진이나 업스케일 시 흐림.

**후속 행동**:
- 신규 `blog_reviews` 추가 시 **반드시 `uv run python scripts/fetch_assets.py` 실행 후 `assets/place-images/`·`local-image-map.json` 재커밋**(게이트가 강제).
- "restore/원상복구"성 데이터 되돌림 후에도 동일 — 이미지 매핑 동기화는 게이트가 감시.
- (선택) 텍스트 전용 4장을 완전 제거하거나 검증된 새 이미지로 교체 — 사용자 판단.

**영향 받은 파일**:
- `data/itinerary.json` (죽은 이미지 4장 `img=""`, 리뷰·링크 보존)
- `data/local-image-map.json` + `assets/place-images/` (4장 신규 자가호스팅)
- `scripts/build_index.py` (`blog_reviews_html` onerror 강화)
- `tests/test_build_index.py` (`BlogImageSelfHostGateTests` 신설 + `test_blog_reviews_have_images` 정정)
- `CLAUDE.md`·`README.md` (게이트·규칙 반영)
- 본 일지
