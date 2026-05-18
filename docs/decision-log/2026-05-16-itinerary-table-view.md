# 2026-05-16 · 시간표 뷰 추가 + 5/31 동선 수정

## 산출물

- `viz/itinerary-table.html` (신규) — 4일 열 × 시간대 행 테이블
- `scripts/build_index.py` — `build_itinerary_table()` 추가, `OUTPUTS`에 4번째 항목 등록
- `viz/itinerary.html` — "시간표 뷰" 링크 추가
- `index.html` — 일정 카드에 "시간표 뷰 ↗" 링크 추가
- `tests/test_build_index.py` — `ItineraryTableTests` 6개 추가 (TDD)

## 데이터 수정

- `data/itinerary.json` 5/31 11:30 항목:
  - 변경 전: `"시오 짐 보관 + 점심"` (maps_query: Kyoto Station)
  - 변경 후: `"니조역 → 시오 짐 보관 후 점심"` (maps_query: Nijo Station Kyoto)
  - 사유: 교토역 코인락커 대신 에어비앤비(시오) 직접 방문해 짐 위탁
- `docs/kyoto-itinerary-may31-jun3-2026.md` 동기화

## 합의

- 5/31 도착 동선: KIX → 교토역 → 니조역 → 시오 짐 보관 → 동산 지구
- 코인락커 불필요 (마치야에 먼저 들러 짐 위탁)
- 시간표 뷰는 `viz/itinerary.html` (카드 뷰) + `index.html` 일정 카드에서 링크

## 다음 단계

- 항공편 시간 확정 후 5/31 오전·6/3 오후 일정 미세 조정
- 시그라쿠 토후 4인 예약 진행
