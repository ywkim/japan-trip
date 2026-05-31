# 2026-05-31 — eX cafe blog_reviews 미복원 확정 (환경 제약상 검증 불가)

## Status

Accepted. `2026-05-31-09-blog-reviews-url-quality-policy-axis.md`의 후속 행동("실제 포스트 확보 후 복원")을 **이번 세션에서는 미수행으로 종결**.

## Context (왜)

09에서 "eX cafe 카드는 정책 위반이 아니므로 실제 포스트 URL을 확보하면 복원이 정답(빈칸 방치 금지)"이라 했다. 사용자가 "WebSearch로 실제 네이버 후기 글을 찾아 curl로 검증해 복원하라"고 지시. 그러나 **본 실행 환경의 도구로는 실제 네이버 글을 찾거나 검증할 수 없음**이 확인됐다(2026-05-31 실측):

| 경로 | 결과 |
|---|---|
| `curl https://blog.naver.com` · `rss.blog.naver.com/<id>.xml` · `api.blog.naver.com` | **403 "Blocked by egress policy"** |
| `WebFetch search.naver.com` · `m.blog.naver.com/<post>` | 차단(unable to fetch) |
| WebSearch (도메인 제한·일반) | 네이버 포스트 미색인 (triple.guide·tripadvisor·영문 블로그만 반환) |
| `curl pstatic.net` (이미지 CDN) | 200 (이미지 자가호스팅만 가능) |
| `curl google.com` · `tabelog.com` | 200 (네이버만 선별 차단) |

즉 이 환경의 네트워크 정책이 `*.naver.com` 전체를 egress 차단하고, WebSearch(US 색인)는 네이버 글을 띄우지 못한다. 검증 불가능한 URL·댓글을 지어 복원하면 레포 절대 규칙(날조 금지·검증 불가 시 보류, `CLAUDE.md`)을 다시 위반한다.

제시한 선택지 A(사용자가 실제 포스트 URL 제공)·B(환경 정책에서 naver 허용)·C(카드 없이 두기) 중 **사용자가 C를 선택**.

## Decision (무엇)

**eX cafe(6/1 12:00)는 `blog_reviews` 없이 둔다.** 카페 정보는 일본어 1차 출처로 작성된 상세 페이지(`viz/excafe-review.html` ← `docs/excafe-review-translation.md`, Tabelog)가 `link`("eX cafe 상세 정보")로 연결돼 있어 정보 손실이 없다.

- 데이터는 이미 08에서 제거된 상태 — 본 결정은 "복원하지 않음"을 확정(추가 변경 없음).
- 게이트 `test_naver_blog_reviews_link_to_specific_posts` **유지** — 향후 누가 카드를 추가하면 실제 특정 포스트(작성자ID/글번호)만 통과, 검색 페이지·블로거 홈(날조 시그니처) 차단. 종류 무관.
- 사찰·관광지(죽림길·텐류지·사이호지·금각사) blog_reviews는 실제 포스트라 **보존**.

채택하지 않은 대안:
- **A(사용자 URL 제공)**: 유효하나 이번엔 미진행. 추후 사용자가 실제 후기 URL을 주면 경로 A로 복원 가능(이미지는 pstatic CDN에서 자가호스팅 가능).
- **B(naver egress 허용)**: 환경 재구성 필요, 이번엔 미진행.
- **검증 없이 origin/main 카드 복원**: 검색/홈 URL + 합성 댓글 = 날조 재현. 미채택.

## Consequences (그래서)

**긍정**:
- 날조 카드 영구 제거 + 검증 불가 콘텐츠 미생성(레포 규칙 준수). 카페 정보는 일본어 출처로 일원화.
- 게이트가 향후 동일 날조를 차단.

**부정·트레이드오프**:
- eX cafe 가로 후기 스트립 없음 — 일정 카드가 단출. 추후 실제 후기 확보 시 경로 A로 복원 가능.

**후속 행동(선택)**:
- 사용자가 실제 eX cafe·% Arabica·사가노유·파인투에스프레소·쿠모노차 네이버 포스트 URL을 제공하면 → 이미지 자가호스팅 + 정직한 발췌/요약으로 카드 복원.

**영향 받은 파일**:
- 없음(데이터는 08에서 이미 제거). 본 일지가 결정만 확정.
