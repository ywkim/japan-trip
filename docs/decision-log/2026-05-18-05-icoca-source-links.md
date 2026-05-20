# 2026-05-18 — ICOCA Apple Wallet 출처 링크 보강 (PR #29 머지 후속)

## 트리거

PR #29 머지 직후 영욱 지시: "iPhone Apple Wallet ICOCA 단권도 링크 필요". 직전 PR(`2026-05-18-04-transit-pass-correction-icoca`)에서 ICOCA Apple Wallet 통일 결론은 박았으나 출처 URL이 cost-options.json source 필드와 decision-log 본문 어디에도 인용되지 않은 채 머지됨 — CLAUDE.md "메타 문서화 규칙: 데이터 산출물 PR은 데이터 출처 명시" 규칙 미흡 보강.

## 산출물

- `data/cost-options.json` `kyoto_local_transit_4pax.source`: ICOCA Apple Wallet 통일 근거 3건(Apple Support / Inside Kyoto / Tictivity) + ¥700 폐지 근거 2건(SoraNews24 / 교토시 공식) URL 인라인 인용.
- `docs/decision-log/2026-05-18-04-transit-pass-correction-icoca.md`: 본문 끝에 "## 출처 (2026-05-18 WebSearch/WebFetch 검증)" 섹션 신설 — Apple Support·Inside Kyoto·Tictivity·SoraNews24·Mothership·교토시 공식·KKday 7건 마크다운 하이퍼링크.
- `docs/kyoto-itinerary-may31-jun3-2026.md` §2.5: 결제 채널 한 줄 아래 출처 링크 5건 추가.

## 핵심 관찰

- 직전 PR 본문엔 출처가 있었지만(채팅 응답에 박혀있던 Sources 섹션) 정작 **레포 데이터에는 누락** — 채팅 컨텍스트와 레포 메타가 분리되어 시간이 지나면 출처 추적 불가. 메타 문서화 규칙 적용 누락 사례로 기록.
- 별도 PR 분리 사유: 머지된 PR #29을 다시 열거나 동일 변경의 새 PR 금지(자동 unsubscribe 가이드). 메타 누락 보강은 별개 단일 목적 커밋.

## 보류 / 다음 단계

- (검토) `arrive_from`에 `fare_yen`·`ic_card_eligible` 필드 추가 — 직전 04 일지에서도 제안. 본 보강과 묶지 않음.
- 6/2 JR 나라선 3 leg 정확 운임 측정 (Browser MCP) — 직전 04 일지 보류 항목 유지.
