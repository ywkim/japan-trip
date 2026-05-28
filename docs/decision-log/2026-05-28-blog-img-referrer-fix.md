# 2026-05-28 — 블로그 후기 사진 hotlink 차단 수정

## Status

Accepted

## Context (왜)

- 일정 카드 (`viz/itinerary.html`) 의 블로그 후기 이미지가 깨져서 표시됨
- `img` 출처 대부분이 Naver 블로그 (`pstatic.net`)로, Naver는 외부 도메인에서 `Referer` 헤더를 보내면 hotlink 요청을 차단함
- `build_index.py` 의 `blog_reviews_html()` 가 `<img>` 에 `referrerpolicy` 속성 없이 렌더하므로 브라우저가 `Referer: https://nihon-trip.vercel.app` 를 전송 → 차단

## Decision (무엇)

- `blog_reviews_html()` 의 `<img class="blog-thumb">` 태그에 `referrerpolicy="no-referrer"` 추가
- 브라우저가 Referer 헤더를 전송하지 않아 Naver hotlink 차단 우회

## Consequences (그래서)

- 후기 썸네일이 정상 표시됨
- 영향 파일: `scripts/build_index.py` (1줄 수정)
- Wikimedia Commons (`image_url`) 는 hotlink 차단이 없어 별도 처리 불필요
