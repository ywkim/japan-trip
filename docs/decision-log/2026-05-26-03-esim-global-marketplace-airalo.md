# 2026-05-26 — eSIM 사업자 확정: 글로벌 마켓형 Airalo (영욱 라인)

## Status

Accepted (구매·개통은 출국 전 잔여 — 결제 완료 시 `confirmed_booking` 승격)

## Context (왜)

- PR #52에서 영욱 1회선(데이터) + 가족 3명 핫스팟 안으로 right-size(실사용 합계 ~4GB·영욱 88%). 영욱 라인 후보 3택1: (a) SKT baro 6GB ₩39,000 (b) Airalo Moshi Moshi 5GB/7일 ₩13,800 (c) Klook 1GB/일 ~₩11,000.
- 일본 eSIM 시장 분석(2026-05-26): 망은 4개(도코모·KDDI/au·소프트뱅크·라쿠텐)뿐이고 모든 eSIM은 이를 재판매. 사업자는 ① 글로벌 마켓(Airalo·Nomad·Ubigi·Holafly 등) ② OTA 리셀러(Klook·KKday·도시락 등) ③ 현지 MVNO(Sakura·Mobal·povo) ④ 본국 로밍(SKT baro·KT)의 4유형. 본 여행 프로필(총 ~4GB·1인 집중·핫스팟·도심·4일)의 스위트스팟은 "소량 GB 버킷 + 테더링 허용 + 도심망" → 글로벌 마켓형 / OTA 버킷.
- 일본 4G/5G 분석: 일본 5G는 転用5G(4G 재포장) 비중이 커 관광 eSIM은 체감 4G. 4G 실속도 40~80Mbps로 지도·메신저·검색·영상통화·FHD에 충분. 따라서 Airalo의 4G(KDDI/SB)도 교토·오사카 도심 일정에 충분하고 Klook "5G"의 실익은 미미.
- 검증 비대칭: Airalo는 가격·핫스팟을 Playwright MCP로 직접 확인(스크린샷 보존), Klook은 Akamai 봇 차단으로 가격 미검증·저가형은 1GB/일 한도.
- 사용자 지시(2026-05-26): "글로벌 마켓 확정".

## Decision (무엇)

- 영욱 라인 eSIM을 **글로벌 마켓형 Airalo Moshi Moshi 5GB/7일 ($10 ≈ ₩13,800)** 으로 확정한다.
- 근거: ① 가격·핫스팟 1차 검증(불확실성 제거) ② 5GB 통합형이라 핫스팟 공유에도 일일 한도 없음(Klook 1GB/일 대비 유연) ③ KDDI/소프트뱅크 4G가 교토·오사카 도심에 충분.
- 소연·시부모는 영욱 핫스팟(₩0) 유지 → 4인 데이터 합계 **₩13,800**.
- 채택하지 않은 대안:
  - **Klook**(OTA 버킷, ~₩11,000): 원화·한국어·QR 편의·소액 저렴하나 가격 미검증·일일 1GB 한도. 차순위 대안으로 보존.
  - **SKT baro**(본국 로밍, ₩39,000): 번호 native·baro 통화·Club T 혜택이나 GB당 고가. 핫스팟 단일 회선엔 과지출.
  - **Ubigi / Holafly / 현지 MVNO**: 대용량·무제한·장기체류향으로 본 프로필엔 오버사이즈(Holafly는 핫스팟 500MB/일 제한). 단 도코모 시골 커버리지가 필요했다면 Ubigi가 정답.

## Consequences (그래서)

- 긍정: 영욱 라인 비용 ₩13,800 확정선. 핫스팟 가족 공유 가정이 검증된 사업자로 안전. 4인 데이터 합계 ₩13,800 — 이전 4인 각자 플랜(₩44~95K) 대비 대폭 절감.
- 부정·트레이드오프: Airalo는 4G LTE(5G 미지원)·도코모 미연결(도심 일정엔 무영향). 영어 앱·USD 결제. 데이터 전용이라 영욱 SKT는 통화·SMS(OTP)용 이중유심 유지 필요.
- 후속 행동: 출국 전 영욱 본인 Airalo 앱에서 Moshi Moshi 5GB 구매·eSIM 설치, 도착 후 데이터 ON + 핫스팟. 결제·개통 완료 시 `data/booking-checklist.json` esim 항목을 `확정`(`confirmed_booking`) 승격 + `2026-05-XX-esim-confirmed.md` 일지.
- 영향 받은 파일: `data/booking-checklist.json`(esim 항목 status/amount/action/note), `docs/booking-research-2026-05-24.md`(§3 권장·요약 표·다음 행동), `viz/checklist.html`(빌드 산출물).
