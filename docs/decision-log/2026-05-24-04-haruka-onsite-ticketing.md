# 2026-05-24 — 하루카 발권 채널: KIX 현장 발권 채택 (소연 결정)

## Status

Accepted (Supersedes PR #43 초기 권장 "온라인 WEST QR 사전 구매")

## Context (왜)

- PR #43에서 하루카 외국인 할인 편도권(¥2,200/인)의 발권 채널로 **JR West 온라인 2026 WEST QR e-티켓 사전 구매**(지정석 사전 예약·KIX 교환 대기 회피)를 권장했다.
- 여행 의사결정자 소연이 PR #43 코멘트(2026-05-24)에서 **현장 결제(KIX 도착 후 현장 발권)**로 진행하겠다고 결정하고, 온라인 사전 구매 권장안은 보류를 요청했다. 참고 블로그를 함께 제시(https://blog.naver.com/bomnarigom/223024559486).
- 운임(¥2,200/인, 외국인 단기체재 할인 편도)과 구성(하루카 + 시내 ICOCA 단권)은 변동 없음 — **발권 채널만** 변경.

## Decision (무엇)

- 하루카 할인 편도권 발권을 **KIX 도착 후 현장 발권**으로 확정한다. KIX 1F JR 매표소/간사이 관광정보센터에서 여권 제시 후 4인분(왕복분) 구매.
- 온라인 WEST QR e-티켓 사전 구매안은 삭제하지 않고 **보류(대안)**로 문서에 보존(향후 재검토 대비).
- 운임·`data_quality`(official_fare, ¥2,200)는 유지.

## Consequences (그래서)

- 긍정: 사전 결제·앱/QR 관리 불요. 소연 의사 반영. 블로그 절차 참고 가능.
- 부정·트레이드오프: 시부모 동반 상태에서 KIX 도착 직후 매표소 대기 가능성(혼잡 시). 지정석은 현장 구매 시 가능 여부·잔여석에 따라 결정.
- 영향 받은 파일·데이터: `data/booking-checklist.json`(transit_pass action·note), `data/cost-options.json`(haruka_rt_4pax notes), `docs/booking-research-2026-05-24.md`(§2 권장 → 현장 발권), 빌드 산출물 `viz/checklist.html` 재생성.
