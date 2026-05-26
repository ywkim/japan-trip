# 2026-05-25 — 하루카 편도권 Trip.com 온라인 e티켓 실제 예약 (발권 채널 변경)

## Status

Accepted — Supersedes `2026-05-24-04-haruka-onsite-ticketing.md` (KIX 현장 발권)

## Context (왜)

- 2026-05-24 ADR(`-04-haruka-onsite-ticketing`)은 하루카 편도권을 **KIX 현장 발권**으로 결정했다.
- 2026-05-25 소연이 실제로는 **Trip.com 온라인 e티켓**으로 예약을 진행했다(PR #43 코멘트 보고). 발권 채널 결정의 후속 변경이다.
- 예약 시점에 운임·구성(하루카 편도 + 시내 ICOCA 단권)은 유지되나, **채널·단가·범위(편도 only)**가 본 PR 데이터와 달라 정합화가 필요하다.

## Decision (무엇)

- 하루카 편도권 발권을 **Trip.com 온라인 e티켓**으로 확정(실제 예약 완료). KIX 현장 발권(ADR 04)·JR West 온라인 WEST QR 직접 구매는 대안으로 보존.
- 예약 내역(실측):
  - 사이트: Trip.com / 상품: [공식] JR 하루카 간사이공항 특급 승차권(전자·실물 선택)
  - 구간·인원: 간사이공항 → 교토역 · **편도** · 성인 ×4
  - 결제: **₩70,300**(기본 ₩74,000 = ₩18,500×4, 일본 액티비티 5% 할인 −3,700, TossPay)
  - 예약자: LEE/SOYEON · 예약번호: **1400827143412439**(PIN 별도)
  - 유효: 2025/03/17~2027/03/31, 예약 후 90일 이내 1회 · 상태: **확인 중**(2026-05-25 17:43 확정 예정)
  - 사용: WEST QR 계정 등록 → 전자티켓 바인딩 → 편명·좌석 예약 → 당일 QR 활성화 · 취소: 조건부 가능
- 본 PR 반영 범위: `booking-checklist.json` transit_pass(status `예약중`·실측 reference·귀국편 TODO), `cost-options.json` haruka_rt_4pax notes 주석, 리서치 문서 §2. **정확 단가(krw)·`confirmed_booking` 승격은 확정 통보 후** 별도 갱신.

## Consequences (그래서)

- 긍정: 실제 예약이 단일 출처(booking-checklist)에 기록됨. 채널 변경 이력이 ADR로 추적됨.
- 부정·트레이드오프: 본 예약은 **편도 only** — 6/3 교토→KIX 귀국편 미예약. 단가가 계획 추정(₩167,200 왕복)과 달라(편도 실측 ₩70,300) cost-options krw는 아직 미갱신(확정·귀국편 발권 대기).
- 후속 행동:
  1. **6/3 귀국편 발권**(Trip.com 동일 상품 또는 현장) — 후속.
  2. 확정 통보 후 `cost-options.json` haruka_rt_4pax를 `confirmed_booking`으로 승격 + krw 갱신.
  3. WEST QR 계정 등록·전자티켓 바인딩(4인) 출국 전 완료.
- 영향 파일: `data/booking-checklist.json`, `data/cost-options.json`, `docs/booking-research-2026-05-24.md`, 빌드 산출물 `viz/checklist.html`.
