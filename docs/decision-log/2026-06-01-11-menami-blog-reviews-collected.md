# 2026-06-01 — 御料理めなみ blog_reviews 실제 네이버 후기 2장 수집

## Status

Accepted

## Context (왜)

- 6/1 17:30 메나미 일정 카드에 `blog_reviews`가 없어 다른 식당(eX cafe·카네요·권타로)과 달리 사진 strip이 비어있었음
- 이전 세션(`docs/menami-blog-reviews-handoff.md`)에서 `*.naver.com` egress 차단으로 작업 보류됨
- PR #89에서 날조(합성 URL·합성 댓글) 적발 이력이 있어 Playwright로 직접 본문 확인 후 발췌 의무화

## Decision (무엇)

- Playwright MCP로 네이버 블로그 검색 후 두 글 본문·사진 직접 확인 → `blog_reviews` 2장 추가
  1. `m.blog.naver.com/chochocho_o/223691590267` — 초쵸춉, 2024년도 실식 후기 (2025-02-10 게시), 오반자이 음식 사진 다수 확인
  2. `m.blog.naver.com/laputaa/221890693037` — 기억저편, 2020년 오반자이 원조 방문기, 오반자이 모리아와세 사진 확인
- 댓글은 각 글의 실제 본문 텍스트에서 발췌 (합성 요약 없음)
- `fetch_assets.py`로 이미지 2장 자가호스팅 완료

## Consequences (그래서)

- 메나미 일정 카드에 사진 strip 2장 표시됨 (다른 식당과 동등한 시각 정보)
- 두 게이트(`test_naver_blog_reviews_link_to_specific_posts`·`test_every_blog_image_is_self_hosted`) 통과
- 영향 파일: `data/itinerary.json`, `data/local-image-map.json`, `assets/place-images/` (2장 신규)
- `docs/menami-blog-reviews-handoff.md` 작업 완료
