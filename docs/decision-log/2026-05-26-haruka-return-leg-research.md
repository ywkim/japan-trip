# 2026-05-26 — 하루카 귀국편(6/3 교토→KIX) 발권 채널 리서치

## Status

Accepted

## Context (왜)

- PR #43에서 하루카 **왕로(편도)만** Trip.com 온라인으로 예약됨(₩70,300/4인, 확인 중). **귀국편(6/3 교토→KIX, 성인 4인)은 미예약**으로 남아 후속 과제였다.
- 실제 발권 전에 채널별 운임·예약 조건을 실시간으로 확인할 필요가 있었다(CLAUDE.md 실시간 가격 리서치 규칙).

## Decision (무엇)

- 귀국편 채널 비교를 리서치하여 `docs/booking-research-2026-05-24.md` §2-1에 기록하고, `booking-checklist.json` transit_pass `action`·`cost-options.json` haruka_rt_4pax `notes`에 권장안을 반영했다. **발권 자체는 미실행**(사용자/소연 실행 + 항공 시각 확정 필요).
- 권장: 왕로와 동일 **Trip.com 채널**로 통일(추정 ~₩70,300/4인, 발권 화면서 교토→KIX·6/3·성인4 실가 재확인). 대안: WEST QR 공식 외국인 할인 편도권 ¥2,200/인(지정석 포함)≈₩83,600/4인.
- 채택하지 않은 즉시 결정: 운임 단가(krw) `confirmed_booking` 승격 — 귀국편 미예약·왕로 "확인 중"이라 보류(소연 지정 순서).

## Consequences (그래서)

- 긍정: 귀국편 발권이 출처·data_quality 라벨과 함께 액션 가능한 상태로 정리됨. 왕복 실측 추정(≈₩140,600~153,900)이 기존 계획 추정(₩167,200)보다 낮음을 확인.
- 부정·트레이드오프: Trip.com 복로 실제 표시가는 발권 화면 재확인 전까지 추정값(`researched_market_rate`).
- 후속: ① 에어서울 KIX 출발 시각 확정 후 좌석시각 역산 ② 귀국편 4인 발권 ③ 확정 후 cost-options krw·data_quality 갱신.
- 영향 파일: `data/booking-checklist.json`, `data/cost-options.json`, `docs/booking-research-2026-05-24.md`, 빌드 산출물 `viz/checklist.html`.
