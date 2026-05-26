# 2026-05-25 — ICOCA 아이폰(Apple Wallet) 셋업 가이드 신설

## Status

Accepted

## Context (왜)

- 사용자(소연)가 한국 여행자 블로그 글(`https://blog.naver.com/bomnarigom/223033114916`)을
  공유하며 "아이폰으로 (교통카드) 찍는 방법 리서치해서 japan-trip에 PR 올려"
  요청. 본 세션에서는 네이버 블로그 직접 접근이 차단되어 사용자에게 주제(관서
  ICOCA)를 확인받음.
- 직전 ICOCA 모바일 운영 playbook(`docs/decision-log/2026-05-18-06-icoca-playbook-mobile.md`)의
  Step 1 "출국 전(5/30 이전) 4인 iPhone Wallet ICOCA 추가·¥3,000/인 초기
  충전"이 한 줄 헤더로만 존재 — **4인이 따라할 실제 셋업 단계(요건 확인,
  Wallet 추가 절차, 한국 카드 호환성, Express Card 설정, 충전·환불, 트러블슈팅)가
  레포에 부재**. 같은 일지의 "보류" 항목에 "시부모(아버지·어머니) iPhone
  모델·iOS 버전 사전 확인 → step 1 사양 요건 충족 여부. 미충족 시 종이/현금
  대안 단계 추가"가 명시되어 있었으나 후속 산출물이 없는 상태.
- 출국까지 6일(5/25 → 5/31) — 4인 동시 셋업 + 시부모 폰 사양 확인 + 미충족
  시 백업 경로(종이 ICOCA)까지 처리할 시간이 짧다. 현지 도착 후 막히면
  4인 전체 동선이 영향.
- 알려진 대안:
  1. **`transit-pass-jr-kansai-2026.md`에 단계 보강** — 해당 문서는 패스 비교가
     주제, 셋업 매뉴얼이 섞이면 단일 책임 깨짐. 채택 안 함.
  2. **`data/itinerary.json`의 `transit_pass_playbook` step 1을 다단계로 확장** —
     모바일 카드 UI가 길어지고 일자별 카드 위 ICOCA 셋업이 4인 가족의 무게중심을
     흔듦(직전 playbook 일지의 "운영 가능 모바일 화면 정의" 관찰). 채택 안 함.
  3. **별도 `docs/icoca-iphone-setup.md` 신설 + playbook step 1에서 참조** —
     단일 책임, 모바일 카드 사이즈 영향 없음, 출국 전 일회성 셋업 문서로 분리.
     **채택**.

## Decision (무엇)

- `docs/icoca-iphone-setup.md` 신설 — 5섹션 구조:
  1. 사전 요건 (기기·계정·결제수단) + 4인 가족 체크 (시부모 폰 사양 보류
     항목을 표 형식으로 가시화)
  2. 셋업 단계 (Wallet 추가 + Express Card 설정 + 1카드=1기기 정책)
  3. 충전·환불 (Apple Pay·현지 현금·귀국 후 환불)
  4. 트러블슈팅 (메뉴 부재·결제 거절·구형 폰)
  5. 5/30 마감 체크리스트 6항목
- `README.md` "사용법" 절의 docs 목록에 본 문서 한 줄 추가.
- `CLAUDE.md` "디렉토리 구조" 트리에 본 문서 한 줄 추가.
- **transit_pass_playbook step 1과 본 가이드 간의 cross-link은 본 PR에서 처리하지
  않음** — `data/itinerary.json` 변경은 별도 PR 단위로 격리(직전 일지에서도
  데이터 변경과 메타 변경은 분리). 본 PR은 가이드 문서 신설 + 메타 갱신만.
- 채택하지 않은 대안:
  - 한국 카드사별 상세 호환성 매트릭스 (BC·국민·신한 등 카드사별 정책) →
    카드사 정책이 자주 변하고 본 여행 4인의 실제 카드와 무관한 정보가 부풀어남.
    "트래블월렛/트래블로그 권장 + 차단 시 현지 현금" 원칙만 유지.

## Consequences (그래서)

**긍정**
- 4인이 5/30 토요일까지 셋업 완료할 수 있는 단일 진입점 문서 확보.
- 시부모 폰 사양 미확인이 표로 가시화 → 영욱·소연이 시부모께 확인 요청을
  바로 트리거 가능 (직전 playbook 일지의 보류 항목 후속 행동 착수).
- 한국 카드 결제 거절 사고에 대한 백업 경로(트래블월렛 + 현지 편의점 현금)가
  미리 정의되어 현지에서 막힐 경우 즉시 전환 가능.
- ICOCA 메뉴 부재·iOS 미달 케이스의 백업(종이 ICOCA + KIX 매표소 발권)이
  비용·동선과 함께 명시 → 시부모 폰이 미충족이어도 5/31 도착 즉시 대응 가능.

**부정·트레이드오프**
- 셋업 가이드는 출국 전 일회성 문서 — 귀국 후 가치 소실. 본 레포의 다른
  운영 문서(weather, flights, transit-pass)와 달리 시계열 갱신이 없는 일회성
  자산.
- 외부 출처 7건(JR West·Apple Support 3건·Triple·자유로운 인생·Inside Kyoto)에
  의존 — 본 가이드의 데이터 품질은 `researched_market_rate` 수준. 단, 운임이
  아닌 절차·UI 정보라 60일 묵음 규칙은 비적용.

**후속 행동**
- (시급, 별도 행동) 시부모 iPhone 모델·iOS 확인 → 영욱·소연이 카톡으로 요청.
  미충족 결과 시 `data/booking-checklist.json`에 "종이 ICOCA KIX 발권" 항목
  추가 + 본 가이드 §4.3 동선 활성화.
- (선택, 별도 PR) `data/itinerary.json`의 `transit_pass_playbook` step 1에서
  본 가이드를 참조하는 한 줄 추가 (`see docs/icoca-iphone-setup.md`).
- (선택, 별도 PR) 4인 셋업 완료 후 결과를 `data/booking-checklist.json`의
  새 항목 또는 메모로 기록 → 출국 전 마지막 검증.

**영향 받은 파일·데이터**
- `docs/icoca-iphone-setup.md` (신설)
- `docs/decision-log/2026-05-25-02-icoca-iphone-setup-guide.md` (본 일지)
- `README.md` (docs 목록 1줄 추가)
- `CLAUDE.md` (디렉토리 구조 트리 1줄 추가)
