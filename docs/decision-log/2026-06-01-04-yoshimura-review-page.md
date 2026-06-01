# 2026-06-01 — 아라시야마 요시무라 번역 페이지 추가

## Status

Accepted

## Context (왜)

6/1 점심으로 아라시야마 요시무라(嵐山よしむら)가 확정됨(사가노유 → 요시무라 교체, 사용자 선택: 음식·경치 우선). eX cafe(`viz/excafe-review.html`), 만자라테이(`viz/manzaratei-review.html`)와 동일한 패턴으로 일본어 정보를 한국어로 번역한 참고 페이지가 필요하다.

## Decision (무엇)

`docs/yoshimura-review-translation.md`를 작성하고 `viz/yoshimura-review.html`로 렌더하도록 DOC_PAGES에 등록한다.

**수집 출처**:
- 嵐山よしむら 공식사이트(yoshimura-gr.com) — 소바 철학(산지·석구제분·수타), 역사, 이용 안내
- Tabelog(ID 26000403) — 평점 3.53(1,003 리뷰), 영업시간, 예산
- 공식 메뉴 페이지(yoshimura-gr.com/arashiyama/menu/) — 전 메뉴 항목·가격

**번역 페이지 구성**:
- 건물 역사 (가와무라 만슈 구저택, 기타오지 로산진 연고)
- 소바 3원칙 (산지 직매입·석구 제분·전원 수타)
- 도게쓰교 창가석 (2층 유리창 파노라마)
- 세트(膳) 4종 + 단품 소바 8종 + 사이드·스위츠 가격표
- 4인 가족 추천 조합 (도게쓰젠·텐자루젠 기준 ¥9,160)
- 이용 팁 (예약 불가 대응, 창가석 요청법, 주와리소바 품절 주의)

itinerary.json 요시무라 항목에 `link.url: "yoshimura-review.html"` 추가.

채택하지 않은 대안:
- **itinerary.json 메모만으로 처리**: 메뉴 전체·역사·팁을 일정 카드에 담기 어려움. 별도 페이지가 낫다.

## Consequences (그래서)

**긍정**:
- 일정 화면에서 "아라시야마 요시무라 상세 정보" 링크로 바로 연결
- 메뉴·가격·팁 정보를 현지에서 화면으로 참조 가능 (오프라인 PWA 캐시 포함)
- eX cafe·만자라테이 패턴과 일관성 유지

**부정·트레이드오프**:
- 예약 불가 식당이라 페이지에서 예약 링크 없음 — 방문 당일 대기 대응만 가능

**후속 행동**:
- 없음 (자기완결)

**영향 받은 파일**:
- `docs/yoshimura-review-translation.md` (신규 번역 페이지)
- `scripts/build_index.py` (DOC_PAGES 1줄 추가)
- `data/itinerary.json` (요시무라 항목 link 추가)
- `CLAUDE.md` (디렉토리 트리·DOC_PAGES 수 갱신 22→23)
- 본 일지
