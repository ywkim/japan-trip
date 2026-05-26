# 2026-05-26 — eSIM 실가격·핫스팟 정책 교차검증 (Airalo 직접 확인, Klook 봇 차단)

## Status

Accepted

## Context (왜)

- 2026-05-26 PR #52에서 영욱 1회선(데이터) + 가족 3명 핫스팟 공유 안을 잠정 결정. 영욱 라인 후보는 (a) SKT baro 6GB(프로모션 8GB) ₩39,000 (b) eSIM ~₩11,000 두 가지.
- 잠정 가격 ₩11,000은 기존 리서치 시점의 시세였고, **실제 핫스팟/테더링 허용 여부가 사이트별로 명시 확인되지 않은 상태**였다. 일부 "무제한" eSIM이 테더링을 차단해 우리 사용 시나리오(영욱 → 가족 3명 핫스팟)를 무력화할 위험이 있었다.
- Klook 페이지가 WebFetch에 403, Tokyo Cheapo/Airalo Help Center도 일부 차단 → Playwright MCP로 직접 페이지 채취가 필요했다.

## Decision (무엇)

eSIM 후보를 다음과 같이 정리한다.

- **검증 가격 후보**: Airalo Moshi Moshi 5GB/7일 **$10 ≈ ₩13,800** (2026-05-26 Playwright MCP로 airalo.com/japan-esim 직접 채취, 스크린샷 `docs/screenshots/airalo-japan-2026-05-26.png`). KDDI/Softbank, 4G LTE. 핫스팟 공식 허용(Airalo Help Center + esimsavvy Moshi Moshi 리뷰 교차확인).
- **추정 가격 후보 보존**: Klook eSIM 4일 1GB/일 **~₩11,000** (klook.com/en-US 및 /ko 모두 Akamai 봇 차단으로 KRW 직접 미검증). Docomo/Softbank 5G, 핫스팟 지원은 Holafly Klook 리뷰(`esim.holafly.com/reviews/klook-esim-review`) "Both options support hotspot sharing"로 확인. 결제 직전 영욱 본인 브라우저에서 KRW 재확인 후 `confirmed_booking` 승격 조건.
- **비교 제외**: Saily(`saily.com/destinations/japan-esim`), Nomad(`nomadesim.com/en/destination/japan`)는 2026-05-26 모두 404로 일본 페이지 경로 확인 실패. 가격 비교에서 제외.
- 합계 가격대를 `₩11,000~13,800(eSIM) ~ ₩39,000(baro)`로 갱신.

채택하지 않은 대안:
- Klook 가격 ₩11,000을 검증 가격으로 격상 → 봇 차단으로 직접 미확인. `researched_market_rate` 유지.
- Airalo만 단일 후보로 압축 → Klook이 1GB/일 단가는 더 저렴할 가능성. 본인 결제 시점 재확인 후 결정.

## Consequences (그래서)

- 긍정: 핫스팟 공유 가능 여부가 두 후보 모두 명시적으로 확인됨 → "영욱 1회선 + 가족 핫스팟" 안의 핵심 가정이 무너지지 않는다. Airalo는 가격·통신사·테더링 모두 1차 출처로 확보.
- 부정·트레이드오프: Klook KRW는 직접 미검증 → 결제 직전 영욱이 본인 브라우저로 재확인하는 운영 단계가 추가됨. Airalo는 4G LTE만 지원(5G 미지원) — 교토 시내는 큰 문제 없으나 속도 민감 시 Klook(5G) 우위.
- 후속 행동: 영욱이 (a)/(b)/(c) 중 택1 후 결제 → `data/booking-checklist.json` esim 항목을 `confirmed_booking`으로 승격하고 `2026-05-XX-esim-confirmed.md` 일지 추가.
- 영향 받은 파일: `data/booking-checklist.json`(esim 항목 amount/action/note), `docs/booking-research-2026-05-24.md`(§3 시세 표·권장·출처), `docs/screenshots/airalo-japan-2026-05-26.png`(신규).
