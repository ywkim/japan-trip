# 2026-05-09 — 실시간 가격 리서치 환경 한계 발견

- 사용자 요청: "실시간!!!!! 으로 직접 찾아서 2026-05-09 기준 가격 알아보기"
- 결과: 본 환경에서 **WebFetch는 모든 부킹 사이트에서 403 Forbidden**
  - 차단 사이트: Klook, Booking, KAYAK, Trip.com, Tripadvisor, HTB 공식, JR Kyushu, japancheapo, woomi-trip 등
  - WebSearch는 동작 (스니펫만 추출 가능)
- 검증된 정보:
  - 군함도 Marbella ¥3,600 + ¥310 견학료 (4인 ₩148,580) — gunkanjima-cruise.jp 공식 명시
  - 마츠바야 료칸 시작가 ₩75,129/실 (booked.net)
  - JR Kyushu Hotel Nagasaki from $35/실, Forest Villa from $107/villa (KAYAK)
- 카탈로그 반영: 군함도 가격을 ₩150K → ₩148,580 (정확값)으로 수정, source/data_quality 갱신
- 한계 명시: 부킹 사이트 페이지 직접 가져오기는 환경 제약. 정확한 5월 평일가는 사용자가 직접 검색해 갱신 필요
- 상세: `docs/budget-options.md` 환경 한계 섹션
