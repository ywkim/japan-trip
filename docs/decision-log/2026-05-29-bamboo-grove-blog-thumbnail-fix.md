# 2026-05-29 — 죽림길 블로그 후기 썸네일 깨짐 수정 (postfiles → mblogthumb 호스트 교체)

## Status

Accepted

## Context (왜)

- 운영 페이지(`viz/itinerary.html` 6/1 08:00 죽림길 카드)의 블로그 후기 사진 2장이 깨진 이미지(broken image "?" 박스)로 렌더된다는 제보(모바일 스크린샷).
- 원인 확인(curl): 두 이미지의 `img` URL이 `postfiles.pstatic.net` 호스트를 쓰는데, 외부/핫링크 요청에 대해 **HTTP 404**를 반환(referer 유무와 무관).
  - `data/itinerary.json` `days[1].items` 죽림길 항목 `blog_reviews[0].img`(`mathian97/223963483537`), `blog_reviews[1].img`(`muse_jigelle/224072195788`).
- 동일 일정 내 다른 후기 썸네일은 정상: `search.pstatic.net`(16장)·`phinf.pstatic.net`(2장)·`blogthumb.pstatic.net`(5장) 모두 HTTP 200. 즉 렌더링 코드(`blog_reviews_html`, `referrerpolicy="no-referrer"`)·정책 문제 아님, **데이터의 이미지 URL 2개만 문제**.
- 검증: 동일 이미지 경로를 표준 네이버 썸네일 CDN `mblogthumb-phinf.pstatic.net`으로 호스트만 바꾸면 두 장 모두 HTTP 200(149KB·262KB), 브라우저처럼 referer 없이 보내도 200. `blogthumb.pstatic.net`·`blogfiles.naver.net` 호스트 스왑은 404.

## Decision (무엇)

- 죽림길 항목의 깨진 후기 썸네일 2개 URL을 경로·쿼리 그대로 두고 호스트만 `postfiles.pstatic.net` → `mblogthumb-phinf.pstatic.net`으로 교체한다.
- 대안 — `search.pstatic.net/common/?src=…` 프록시 래핑: 작동하나(200) URL이 길고 인코딩이 번거로워 호스트 1토막 교체가 더 단순. 기각.
- 대안 — 블로그에서 새 사진 재수집: 캡션과 매칭된 동일 사진을 유지하는 게 맥락 보존에 유리해 호스트 스왑으로 충분. 기각.

## Consequences (그래서)

- 긍정: 6/1 죽림길 카드 후기 사진 2장이 정상 노출. 캡션·링크(`url`)는 그대로라 출처 추적성 유지.
- 부정·트레이드오프: 네이버 CDN 핫링크 정책 변동 시 재발 가능(외부 호스팅 의존). 향후 신규 `blog_reviews[].img`는 `mblogthumb-phinf`/`search.pstatic.net` 형식 권장, `postfiles.pstatic.net` 직링크는 외부에서 404이므로 지양.
- 후속: 없음(별도 PR 불필요).
- 영향 받은 파일: `data/itinerary.json`(죽림길 `blog_reviews` img 2건). 산출물 `viz/itinerary.html`·`viz/itinerary-table.html`은 빌드 시 자동 반영(gitignore).

## Test plan

- [x] curl로 신규 호스트 2장 HTTP 200 확인(referer 없이도 200)
- [x] `uv run python scripts/build_index.py` 빌드 무오류, 산출물에 `mblogthumb-phinf` 반영·`postfiles` 잔존 0
- [x] `uv run python scripts/validate.py` 통과
- [x] `uv run python -m unittest discover -s tests` 통과
