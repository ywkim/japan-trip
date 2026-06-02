# ICOCA 아이폰(Apple Wallet) 셋업 가이드 (2026-05-25 리서치)

> 트리거: 사용자가 공유한 한국 여행자 블로그 글
> `https://blog.naver.com/bomnarigom/223033114916` (네이버 — 본 세션에서
> 직접 접근 차단됨, 주제만 사용자 확인). 그리고 직전 ICOCA 모바일 운영
> playbook(`docs/decision-log/2026-05-18-06-icoca-playbook-mobile.md`)의
> Step 1 "출국 전(5/30 이전) 4인 iPhone Wallet ICOCA 추가·¥3,000/인 초기
> 충전"이 한 줄로만 존재 — 실제 따라할 단계가 없어 4인 가족(특히 시부모
> iPhone) 셋업 직전에 막힐 위험을 제거한다.
>
> 범위: **출국 전(5/30 이전)** 4인 셋업과 **현지 운영 시 충전·환불** 한정.
> 일자별 사용 패턴·요금은 `docs/transit-pass-jr-kansai-2026.md`와
> `data/itinerary.json`의 `trip.transit_pass_playbook`에 이미 있음.

## 1. 사전 요건 (셋업 전 확인)

### 1.1 기기 요건

| 항목 | 기준 | 출처 |
|---|---|---|
| iPhone 모델 | iPhone 8 이상 | JR 서일본 공식 (westjr.co.jp/global) 2026-05-25 |
| iOS | 16.0 이상 | JR 서일본 공식 2026-05-25 |
| Apple Watch (선택) | Series 3 이상, watchOS 8.7.1 이상 | JR 서일본 공식 2026-05-25 |
| Apple 계정 | 2단계 인증 활성화 | Apple Support (108772) 2026-05-25 |
| 결제 수단 | Wallet에 신용/체크카드 1장 등록 | JR 서일본 공식 2026-05-25 |

### 1.2 4인 가족 사전 확인 사항

직전 playbook 일지(`2026-05-18-06`)의 보류 항목 — **시부모 iPhone 모델·iOS 버전
사전 확인**. 본 가이드 적용 전 4인 모두 위 1.1 표를 통과하는지 확인.

| 인원 | 확인 항목 | 상태 |
|---|---|---|
| 영욱 | 아이폰·iOS | (셋업 시 본인 확인) |
| 소연 | 아이폰·iOS | (셋업 시 본인 확인) |
| 시아버지 | 아이폰 모델·iOS 16.0+ 여부 | **미확인 — 출국 전 본인 확인 필수** |
| 시어머니 | 아이폰 모델·iOS 16.0+ 여부 | **미확인 — 출국 전 본인 확인 필수** |

미충족 시 대안: 종이 ICOCA 카드(공항 미도리노마도구치) + 현금 충전. 본 가이드의
경로 B(아래 §3.3) 참조.

### 1.3 한국 결제수단 호환성

ICOCA 충전은 Wallet에 등록된 카드의 국제 브랜드(VISA·Mastercard·JCB·Amex)로
진행. 한국 카드별 동작은 다음과 같다 (출처: 한국 여행 블로그 2026 리서치
교차 검증 — Triple guide 2026-05-25, 자유로운 인생 2026-05-25).

| 카드 종류 | Wallet 직접 추가 | ICOCA 충전 |
|---|---|---|
| 현대카드 Mastercard/Amex | ✅ | ✅ |
| 트래블월렛·트래블로그 (Mastercard) | ✅ | ✅ |
| 그 외 한국 카드 (BC·국민·신한 등) | 카드사별 상이 | 카드사 정책에 따라 차단 사례 있음 — 실패 시 현지 현금 충전(§3.3) |

권장: **각자 트래블월렛/트래블로그 1장씩 Wallet에 미리 등록 + 본인 주거래
카드 1장 보조 등록**. 현지 충전이 차단되는 사고를 줄인다.

Wallet에 등록할 Mastercard·Amex 카드가 아예 없다면(예: 시부모) → ICOCA 대신
**§3.4 경로 C(PASMO 앱 무기명)**를 쓴다. 카드 한 장 없이 현금만으로 모바일 IC를
운용하는 유일한 경로다.

## 2. 셋업 단계 (경로 A — 아이폰에 신규 ICOCA 발급)

§1을 통과하면 다음 순서대로 4인 각자 진행. 5/30(토)까지 완료.

1. **Wallet 앱 열기** → 우측 상단 `+` (추가) 버튼 탭
2. `교통 카드(Transit Card)` 선택
3. `일본 / Japan` 지역 → `ICOCA` 선택
   - 메뉴에 ICOCA가 안 보이면 §4 트러블슈팅 참조
4. `새 카드 추가(Add New Card)` 선택
   - 기명·무기명 선택 화면이 나오면 **무기명(Unregistered)** 권장. 본 여행은
     단기 체재라 분실 시 재발급 수속(¥510)이 비효율적
5. **초기 충전 금액 입력 — ¥3,000 권장**
   - playbook(`2026-05-18-06`)의 4인 ¥3,000/인 기준과 동일
   - 최소 충전은 발급 화면에서 표기되는 값을 따름 (JR 서일본은 최소액 비공개,
     실측: ¥1,000~¥3,000 선택지로 표시)
6. Apple Pay로 결제 확정 (등록된 카드 선택)
7. 약관 동의 → `완료` — 카드가 Wallet에 추가됨

### 2.1 Express Card(익스프레스 카드) 설정 — 필수

기본값으로 켜져 있으나 확인 권장. 켜지면 잠금해제·Face ID·Touch ID 없이 IC
리더에 탭하는 즉시 결제. 끄면 시버스·개찰구 통과 시간이 길어져 4인 가족
이동에 부담.

- 설정 → 지갑 및 Apple Pay → `Express Transit Card` → ICOCA 지정

### 2.2 가족 등록 시 주의 (1카드 = 1기기)

JR 서일본 정책: **ICOCA 1장은 1개 기기에만 등록**. 4인이 각자 별도 카드를
발급받아야 하며, 1장을 4명이 공유 불가. Wallet에 4인이 각자 본인 Apple
계정으로 등록.

## 3. 충전·환불 (현지 운영)

### 3.1 Apple Pay 충전 (Wallet 앱 내)

- Wallet 앱 → ICOCA 카드 선택 → `금액 추가(Add Money)` → 금액 입력 → 결제
- 등록된 한국 카드가 거절되면 §1.3 표의 대안 카드로 전환

### 3.2 잔액 확인

- Wallet 앱 → ICOCA 카드 화면 상단에 잔액 표시
- 익스프레스 카드 모드라 IC 리더에 탭하면 사용 후 잔액이 잠금화면에 알림으로
  표시됨

### 3.3 경로 B — 현지 현금 충전 (Wallet 충전 실패 시 백업)

- **편의점**: 세븐일레븐·로손·패밀리마트 카운터에서 ICOCA 카드(또는 카드가
  띄워진 아이폰)를 내밀고 "이코카 챠지 오네가이시마스(ICOCAチャージお願いします)"
  → 충전액 현금 지불 → 카드/아이폰을 리더에 탭. ¥1,000 단위 충전
- **JR 발권기**: 교토역·우메코지·니조 등 JR 역사 내 자동발권기에서 현금
  충전 가능
- **차내 충전 불가**: 시버스 차내·JR 차내에서는 충전 안 됨. 잔액 부족 사고
  방지를 위해 ¥1,000 미만일 때 미리 충전

### 3.4 경로 C — PASMO 앱 무기명 ¥0 (카드 없이 모바일 IC 운용)

Wallet에 등록할 Mastercard·Amex가 없을 때, ICOCA 대신 PASMO 앱으로 모바일 IC를
발급·운용하는 경로다. 충전은 100% 현금으로 진행하므로 신용카드가 필요 없다.

- ICOCA·Suica는 Wallet `+`에서 직접 추가되지만 **발급 시 Mastercard/Amex가 필요**
  (초기 충전을 Apple Pay로 결제해야 함)
- PASMO는 Wallet `+`에서 직접 추가되지 않고 **PASMO 앱**을 거쳐야 하는 대신,
  잔액 **¥0 무기명**으로 카드 등록 없이 발급할 수 있다
- 발급 후 역 발권기·편의점에서 현금 충전(§3.3과 동일 방식)
- ICOCA·Suica·PASMO는 간사이 전역(교토 시버스·JR·지하철)에서 **상호 호환**되므로
  기능상 차이가 없다

**발급 절차:**

1. App Store에서 **PASMO 앱** 설치
2. 새 카드 → **무기명(無記名 / Anonymous)** 선택 → 잔액 **¥0**으로 진행
3. Apple 지갑에 추가됨
4. 역 발권기 또는 편의점에서 현금 ¥1,000 단위 충전
5. 설정 → 지갑 및 Apple Pay → `Express Transit Card` → PASMO 지정

**주의:**

- 무기명 = 분실 시 잔액 소멸 (기명은 수수료 내고 재발급 가능하나 등록 정보 입력 필요)
- 무기명 PASMO 발매는 2023-06-08 중단 후 **2025-03-01 재개** — 우리 여행 시점에는
  정상 발급된다

근거 링크는 문서 하단 §출처 참조.

### 3.5 환불 (귀국 후)

- 무기명 카드: 미도리노마도구치(JR 서일본 매표소)에서 ¥220 수수료 차감 후
  잔액 환불
- 권장: 환불 안 하고 **다음 일본 방문 시 재사용**. 잔액은 10년간 유효
  (Triple guide 2026-05-25)
- Wallet에 들어 있는 카드는 Wallet 앱에서 `카드 제거` 시 jr-west.co.jp의 별도
  환불 절차 안내가 뜸 (현장 환불보다 복잡 — 그냥 카드를 Wallet에 두고
  방치하는 게 단순)

## 4. 트러블슈팅

### 4.1 ICOCA가 메뉴에 없음

증상: Wallet `+` → 교통 카드에서 ICOCA가 표시되지 않음.

원인 후보:
- 기기 지역 설정이 Apple Pay 미지원 국가
- iOS 16.0 미만

해결:
- 설정 → 일반 → 언어 및 지역 → `지역` — Apple Pay 지원 국가(대한민국 포함)
  여부 확인
- iOS 업데이트
- 그래도 안 되면 경로 B(종이 카드 + 현지 충전)로 전환

### 4.2 충전 결제 거절

증상: Wallet에서 ICOCA 충전 시 카드 결제 실패.

해결:
1. 다른 등록 카드로 전환 (§1.3 표 — 트래블월렛/트래블로그가 가장 안정적)
2. 본인 명의 카드인지 확인 (가족 명의 카드는 Apple Pay에 추가는 되어도
   해외 결제에서 거절되는 사례 보고)
3. 카드사 앱에서 해외 결제 차단 해제
4. 위 모두 실패 시 현지 편의점 현금 충전(§3.3)

### 4.3 시부모 폰이 iPhone 8 미만 / iOS 16 미만

해결: 종이 ICOCA 카드 발급. 5/31 KIX 도착 후 JR 서일본 매표소(미도리노마도구치)
또는 발권기에서 ¥2,000(보증금 ¥500 포함) + 초기 충전 ¥1,500 = 총 ¥3,500
구매. 사용·충전 방식은 아이폰판과 동일하며, 환불 시 미도리노마도구치에서
보증금 ¥500 반환 + 잔액 환불(¥220 수수료).

## 5. 셋업 체크리스트 (5/30 토 마감)

- [ ] 4인 iPhone 모델·iOS 버전 확인 (시부모 포함)
- [ ] 4인 Apple 계정 2단계 인증 확인
- [ ] 4인 Wallet에 결제 카드 1장 이상 등록 (트래블월렛/트래블로그 권장)
- [ ] (카드 미등록자) PASMO 앱 설치 → 무기명 ¥0 발급 → Wallet 추가 (§3.4)
- [ ] 4인 각자 ICOCA Wallet 추가 + ¥3,000 초기 충전
- [ ] 4인 Express Card 설정 — ICOCA로 지정
- [ ] (미충족자) 종이 ICOCA 백업 계획 공유 — KIX 도착 즉시 발권 동선 추가

## 출처 (2026-05-25 WebSearch/WebFetch 검증)

- [JR West Official — ICOCA on Apple Pay](https://www.westjr.co.jp/global/en/howto/icoca/applepay/) — 기기 요건·결제 카드 브랜드 정책
- [Apple Support 108772 — Add a transit card to Apple Wallet in Japan](https://support.apple.com/en-us/108772) — 신규 ICOCA 추가 절차
- [Apple Support 120474 — Use transit cards on your iPhone or Apple Watch in Japan](https://support.apple.com/en-us/120474) — 운영·Express Card 설정
- [Apple Support 120475 — If you can't transfer transit cards to your iPhone or Apple Watch in Japan](https://support.apple.com/en-us/120475) — 트러블슈팅
- [Triple Guide — 아이폰에 일본 교통 카드 등록하는 방법](https://triple.guide/articles/65141a03-0f4a-4df9-aac8-5b0953c872de) — 한국 카드 호환·기명/무기명 차이
- [자유로운 인생 — 2026 일본여행 이코카카드 구입 충전 가이드](https://freedom.greatsisyphus.com/2026-japan-icoca-guide/) — 한국 여행자 실전 충전·편의점 충전 멘트
- [Inside Kyoto — How to import an IC card into your iPhone](https://www.insidekyoto.com/how-to-import-an-ic-card-icoca-pasmo-or-suica-into-your-iphone) — 신규 발급 vs 기존 카드 이전 구분
- 사용자 공유 — 네이버 블로그 `bomnarigom/223033114916` (본 세션에서 직접
  접근 차단됨, 사용자가 주제·취지만 확인). 본 PR의 트리거 자료

### §3.4 PASMO 앱 무기명 경로 근거 (2026-05-31 WebSearch/WebFetch 검증)

- [AtaDistance — Apple Pay Suica/PASMO Guide](https://atadistance.net/apple-pay-suica/) — PASMO 앱 ¥0 무기명·현금 충전, Suica/ICOCA는 카드 필요
- [Get Around Japan — Mobile Suica & PASMO on iPhone](https://www.getaroundjapan.jp/archives/9443) — Anonymous PASMO 선택 단계
- [PASMO — 나무위키](https://namu.wiki/w/PASMO) — 무기명 발매 2023-06-08 중단 → 2025-03-01 재개
