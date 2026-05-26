# 2026-05-26 — 사이호지(苔寺) 입장 예약 확정 (6/1 10:30, 4인)

## Status

Accepted

## Context (왜)

- 같은 날 일지 `2026-05-26-02-saihoji-reservation-feasibility.md`에서 사이호지 예약을 "가능성 확인"까지만 진행했다(실제 예약·일정 편입은 사용자 결정으로 보류).
- 소연이 2026-05-25 **Trip.com '사이호지 입장권' 상품**으로 실제 예약을 완료했고, 영욱이 예약 스크린샷(3장)을 업로드하며 4인·2건·총 ₩188,216·체크리스트+일정+비용 전부 반영을 지시했다.
- 사이호지는 예약당 2명 제한 → 4인은 2건으로 분할 예약됨.

## Decision (무엇)

- 사이호지 입장을 **6/1(월) 10:30, 성인 4인** 예약 확정으로 데이터에 반영:
  - 예약 ① `1400827143416024`(성인2, ₩94,108) · ② `1400827143410570`(성인2, PIN 2362) · 4인 총 **₩188,216** · 조건부 취소(건당 예상 수수료 ₩18,822).
  - `booking-checklist.json` saihoji_research: status `미정`→`확정`, reference·amount·confirmed_at 갱신.
  - `cost-options.json`: `saihoji_admission_4pax`(₩188,216, `confirmed_booking`) 추가 + 확정 시나리오 `kyoto_may31_kadensho_early_bird` one_time에 편입.
  - `itinerary.json` 6/1: 텐류지 09:45→09:30로 당기고 **10:30 사이호지** 삽입(교토버스 73계통), 점심(쇼라이안) 도착 경로를 사이호지발로 갱신, walking_km 4→5.
- 채택하지 않은 대안: intosaihoji.com 공식 온라인 예약 — 실제로는 Trip.com 상품으로 예약됨(플랫폼 일원화).

## Consequences (그래서)

- 긍정: 사이호지가 확정 예약으로 단일 출처에 기록되고 6/1 동선에 편입됨. 6월=이끼 최성수기로 관람 적기.
- 부정·트레이드오프: 6/1 오전이 빡빡해짐(죽림길→텐류지→10:30 사이호지→아라시야마 복귀 점심). 텐류지~사이호지·사이호지~점심 이동시간은 `tbd_needs_browser_mcp`(정확 측정 후속). 휠체어 불가·사경 면제는 당일 현장 상담. Trip.com 마크업으로 공식(¥4,000+¥110/인)보다 비쌈.
- 후속: ① 텐류지~사이호지 버스 정확 시각 측정 ② 사경 면제 가족 사전 합의 ③ 6/1 잔여 오후(금각사 등) 시간 여유 재점검.
- 영향 파일: `data/booking-checklist.json`, `data/cost-options.json`, `data/itinerary.json`, `docs/saihoji-reservation-2026-06.md`, `docs/kyoto-itinerary-may31-jun3-2026.md`, 빌드 산출물(`viz/checklist.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`index.html`).
