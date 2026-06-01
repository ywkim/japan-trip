# 2026-06-01 — 메나미 페이지 보강: 오반자이 설명 + 번역페이지 이미지 정책(축 3) + 공식 갤러리 사진 + blog_reviews 위임

## Status

Accepted

(`docs/decision-log/2026-06-01-10-dinner-manzaratei-to-menami.md` 메나미 확정의 후속 보강)

## Context (왜)

배포된 메나미 페이지(`viz/menami-review.html`)를 확인한 사용자 피드백:

1. **오반자이 한국어 설명 부재** — "오반자이"가 무엇인지 모르는 가족(시부모 포함)을 위한 설명이 없었다.
2. **가게·메뉴 후기 사진 부재** — 다른 외식 페이지(eX cafe·카네요·권타로)는 사진이 있는데 메나미는 0장.

사진 출처를 두고 정책 혼동이 있었다. 작성자가 처음엔 모든 사진을 `blog_reviews`(네이버 특정 포스트 강제) 기준으로 보고 후속 세션에 위임하려 했으나, **사용자가 "번역 페이지의 이미지는 네이버일 필요 없다"고 정책을 정정**했다.

- `CLAUDE.md` 기존 정책은 `blog_reviews`(일정 카드) 이미지만 다뤘고(축 2: 네이버 특정 포스트 + 자가호스팅 게이트), **번역 페이지(`docs/*-review-translation.md`) 본문 이미지**에 대한 규정이 없어 모호했다.
- 선례: `docs/kaneyo-review-translation.md`는 일본 블로그(unagiudou.com) 이미지를 외부 https hotlink로 이미 사용 중 — 번역 페이지 이미지는 네이버가 아니어도 됨이 사실상 관행이었다.
- 본 세션 환경은 `*.naver.com` egress 차단이라 네이버 특정 포스트는 여전히 확보 불가.

## Decision (무엇)

**① 오반자이 한국어 설명을 추가하고, ② 번역 페이지 이미지 정책(축 3)을 명문화한 뒤 메나미 페이지에 공식 갤러리 사진을 추가하고, ③ 일정 카드 `blog_reviews`(네이버)만 후속 세션에 위임한다.**

- `docs/menami-review-translation.md`:
  - "오반자이(おばんざい)란?" 섹션 신설 — 교토 가정식 반찬 문화·담백한 집밥·큰 사발에 골라 먹는 스타일·제철.
  - **공식 사이트 menami.jp 점내 갤러리 사진 5장** 추가(외관·카운터 오반자이·제철 교야채·테이블석·다다미 개실). 전부 다운로드해 **실제 메나미 이미지임을 시각 확인**, https·200 확인, 출처를 문서에 명기.
- `CLAUDE.md` 출처정책에 **"축 3 — 번역 페이지 본문 이미지"** 추가: 번역 페이지 `.md` 이미지는 `blog_reviews`의 네이버 제약(축 2)·자가호스팅 게이트 **대상 아님**. ① 그 가게 실제 이미지 ② https ③ 출처 명기면 출처 무관(공식·Tabelog·블로그 등). 외부 hotlink 허용(`fetch_assets.py`는 `itinerary.json`만 자가호스팅).
- `docs/menami-blog-reviews-handoff.md`: 대상을 **일정 카드 `blog_reviews`(네이버 특정 포스트)** 로 한정 명확화. 번역 페이지 사진은 이미 충족.
- **채택하지 않은 대안**: bricksmagazine 후기·이미지를 blog_reviews에 사용 — 네이버 특정 포스트 아님(축 2 위반). 검증 없이 사진 날조 — 절대 금지.

## Consequences (그래서)

**긍정**:
- 가족이 "오반자이" 의미와 가게 분위기(외관·카운터·좌석)·제철 재료를 페이지에서 바로 확인.
- 번역 페이지 이미지 정책이 명문화돼 향후 외식 페이지 사진 추가가 일관됨(축 3).
- 날조 위험 0 — 공식 사이트 검증 이미지만 사용.

**부정·트레이드오프**:
- 번역 페이지 사진은 외부 https hotlink라 오프라인(PWA)에선 best-effort(라이브에선 정상). 자가호스팅이 필요해지면 별도 작업.
- 일정 카드 `blog_reviews`(네이버 후기 strip)는 여전히 후속 세션 대기.

**후속 행동**:
- Playwright MCP(또는 naver egress 허용) 세션이 `docs/menami-blog-reviews-handoff.md`로 일정 카드 `blog_reviews` 2~4장 추가.

**영향 받은 파일**:
- `docs/menami-review-translation.md` — "오반자이란?" 섹션 + 공식 갤러리 사진 5장
- `CLAUDE.md` — 출처정책 "축 3" 추가, 디렉토리 트리에 handoff 1줄
- `docs/menami-blog-reviews-handoff.md` — 신규(범위: 일정 카드 blog_reviews만)
- 본 일지
