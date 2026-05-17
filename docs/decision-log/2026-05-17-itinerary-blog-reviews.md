# 2026-05-17 — 일정 뷰에 사진·블로그 코멘트 추가

## 주제
`viz/itinerary.html` 상세 일정 화면에 각 명소별 여행 블로그 스타일 사진 스트립과 후기 코멘트 추가

## 산출물
- `data/itinerary.json`: 주요 명소 10곳에 `blog_reviews` 배열 추가 (각 항목: `photos` URL 배열 + `comment` 한국어 후기 텍스트)
- `scripts/build_index.py`: `_render_blog_reviews()` 헬퍼 + CSS `.photo-strip` / `.blog-comment` 추가 → `viz/itinerary.html` 자동 반영
- `viz/itinerary.html` / `index.html` / `viz/checklist.html`: 빌드 산출물 갱신

## 사진 출처
- Unsplash 공개 CDN (`source.unsplash.com/{slug}/1200x800`) — 검색 결과에서 확인된 슬러그 사용
- 적용 명소: 키요미즈데라 · 산넨자카/기온 · 폰토초 · 죽림길 · 텐류지 · 금각사 · 료안지 · 후시미이나리 · 토후쿠지 · 카덴쇼 료칸
- 사용자가 네이버·핀터레스트 실제 사진으로 교체하려면 `itinerary.json`의 `blog_reviews[].photos` URL만 수정 후 `python scripts/build_index.py` 재실행

## 합의
- `blog_reviews` 필드는 선택적 (없으면 아무것도 렌더링하지 않음) — 기존 transit/식사 항목에는 미적용
- `.photo-strip`: 가로 스크롤 스냅, 160px 고정 높이, `loading="lazy"` → 모바일 성능 유지
- `.blog-comment`: 왼쪽 accent 보더 스타일로 블로그 인용문 느낌

## 다음 단계
- 사용자가 네이버 블로그/핀터레스트에서 선호하는 사진 URL 발견 시 `photos` 배열 교체
- 필요 시 명소별 코멘트 내용 조정
