# 2026-06-01 — 6/2 일정 식당 정보 보강 (PR #89 패턴 적용)

## Status

Accepted

## Context (왜)

- PR #89가 6/1 일정에 외식 번역 페이지(eX cafe·권타로·메나미) + food_quality 강화를 적용한 것과 동일한 패턴을 6/2에도 적용하도록 요청됨
- 6/2 일정 점검 결과, 두 식사 항목에 누락 정보가 있음:
  - **11:00 나카무라쇼텐(中村商店, 교토역 라멘코지)**: food_quality ✓(Tabelog 3.55), blog_reviews ✗, 번역 페이지 ✗, link ✗
  - **14:30 맛차하우스(MACCHA HOUSE 抹茶館 산넨자카)**: blog_reviews 5개 ✓, food_quality ✗, ja_name 공란 ✗, 번역 페이지 ✗, link ✗
- 맛차하우스 note의 영업시간 오기("11:00~20:00") 발견 — Tabelog 실측 11:00~18:00(L.O.17:30)과 불일치

## Decision (무엇)

- **나카무라쇼텐 번역 가이드 페이지 신규 등록**: `docs/nakamura-shoten-review-translation.md` → `viz/nakamura-shoten-review.html` (Tabelog·공식 2026-06-01 기준, 닭파이탄 라멘 메뉴·발권기·4인 팁)
- **맛차하우스 번역 가이드 페이지 신규 등록**: `docs/maccha-house-review-translation.md` → `viz/maccha-house-review.html` (Tabelog·공식 2026-06-01 기준, 말차 티라미수·호지차 티라미수·방문 가이드)
- **itinerary.json 업데이트**:
  - 11:00 항목에 `link` 추가
  - 14:30 항목에 `food_quality` 추가, `title.ja_name`·`ja_reading_ko` 보완, `link` 추가, note 시간 수정
  - `places` 레지스트리에 `maccha_house` 추가
- **테스트 갱신**: "영업 11:00~20:00" → "영업 11:00~18:00(L.O.17:30, Tabelog 기준)"로 수정

## Consequences (그래서)

- 6/2 일정도 6/1(PR #89)과 동일하게 주요 식당·카페에 번역 페이지 + link가 연결됨
- 가족이 Vercel 운영 화면에서 14:30 항목 탭 시 맛차하우스 상세 안내(영업시간·메뉴·방문팁) 열람 가능
- 11:00 항목 탭 시 나카무라쇼텐 라멘 안내(메뉴·라멘코지 이용법·4인 팁) 열람 가능
- 맛차하우스 영업시간 오기(20:00 → 18:00) 수정 — 현장 확인 전 잘못된 정보 노출 방지
- DOC_PAGES: 후기·안내 2개 추가 (kaneyo·shinkyogoku 포함 총 4개로 증가)
- 영향 받은 파일: `data/itinerary.json`, `scripts/build_index.py`, `docs/nakamura-shoten-review-translation.md`(신규), `docs/maccha-house-review-translation.md`(신규), `tests/test_build_index.py`, `CLAUDE.md`, `README.md`
