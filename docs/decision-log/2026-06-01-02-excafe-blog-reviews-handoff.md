# 2026-06-01 — eX cafe 카페 후기 수집을 Playwright 세션에 위임

## Status

Accepted

## Context (왜)

`2026-06-01-excafe-blog-review-restore-one.md`에서 eX cafe `blog_reviews`를 검증 가능한 1장(0번)으로 복원했으나, 그 카드조차 URL(ramu0527)과 이미지(m0846) 출처가 다른 조립 카드이고 댓글은 합성 요약이다. 실제 후기로 제대로 채우려면 네이버 블로그 글을 직접 열어 검증해야 하는데, **본 세션 환경은 `*.naver.com` egress를 차단**(curl/WebFetch 403, WebSearch 미색인 — `2026-05-31-10` 참조)해 불가능하다.

사용자 지시: "실제 네이버 글 URL을 커밋(push)하도록 Playwright 가능한 세션에 넘길 메시지 작성해."

기존 위임 선례: `docs/transit-mcp-handoff.md`(tbd_needs_browser_mcp leg 측정) — 자기완결 핸드오프 문서로 후속 Playwright MCP 세션에 작업을 넘긴 패턴.

## Decision (무엇)

`docs/excafe-blog-reviews-handoff.md`를 **자기완결 위임 가이드**로 작성한다. Playwright MCP(또는 naver egress 허용) 세션이 본 레포 `CLAUDE.md` + 이 문서만으로 작업을 수행할 수 있게 한다.

문서 구성:
- **목적·위임 이유**: naver egress 차단 실측 결과 명시.
- **절대 규칙(머지 차단)**: ① URL은 특정 포스트(`/<id>/<글번호>`), 검색 페이지·블로거 홈 금지 ② 댓글은 실제 읽은 글 발췌, 합성 요약 금지 ③ 이미지는 그 글 사진 + 자가호스팅(URL·이미지 출처 일치) ④ 카페에 한국어 blog_reviews는 정책상 허용(품질만 지키면 됨).
- **대상 5곳**(eX cafe·% ARABICA·嵯峨野湯·パンとエスプレッソと·雲ノ茶) + 네이버 검색 키워드 + Tabelog ID(교차확인용).
- **실행 절차**: Playwright로 검색→글 진입→본문 확인→발췌, itinerary.json 스키마, fetch_assets 자가호스팅, build/validate/unittest 게이트.
- **완료 정의(DoD)**: 검증 못 한 글은 추가하지 않음(빈칸 > 날조).

게이트 2종(`test_naver_blog_reviews_link_to_specific_posts`·`test_every_blog_image_is_self_hosted`)이 날조 URL·미자가호스팅을 자동 차단하므로, 후속 세션이 규칙을 어기면 CI가 막는다.

채택하지 않은 대안:
- **본 세션에서 강행(검증 없이 origin/main 복원)**: 검색/홈 URL + 합성 댓글 날조 재현. 미채택(애초 이 사태의 원인).
- **위임 없이 영구 보류**: 사용자가 실제 후기를 원함. 위임이 정답.

## Consequences (그래서)

**긍정**:
- 환경 제약(naver 차단)이 풀린 세션이 즉시 작업 가능 — 컨텍스트 의존 없는 자기완결 문서.
- 절대 규칙·게이트·DoD가 명시돼 같은 날조(PR #89) 재발을 구조적으로 방지.

**부정·트레이드오프**:
- eX cafe 카드는 그때까지 1장(조립)으로 남음.
- 위임 문서가 실행되지 않으면 미완으로 잔존(별도 세션 필요).

**후속 행동**:
- Playwright MCP 세션이 `docs/excafe-blog-reviews-handoff.md` 따라 작업 → 실제 후기 카드 PR.
- 완료 시 핸드오프 문서 "완료" 표기 또는 제거.

**영향 받은 파일**:
- `docs/excafe-blog-reviews-handoff.md` (신규 위임 가이드)
- `CLAUDE.md` (디렉토리 트리에 핸드오프 문서 등록)
- 본 일지
