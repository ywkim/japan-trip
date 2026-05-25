# japan-trip

## 레포 목적

영욱·소연 부부의 **2026-05-31(일)~06-03(수) 교토 4인 가족 여행 (부부 + 시부모) 실행·운영 공간**.

> 정량 비교를 통한 목적지·시기·동반 의사결정은 2026-05-12에 종료. 본 레포는 이제 발권·예약·일정·체크리스트·현지 운영 정보를 누적·갱신하는 공간이다. 과거 의사결정 자산(MCDA·후보 비교·시기 비교)은 그대로 보존하며 회귀 가드·재참조용으로만 사용한다.

### 확정 사항 (요약)

| 항목 | 확정 내용 | 출처 |
|---|---|---|
| 목적지 | 교토 (관서) | `docs/decision-log/2026-05-11-may31-jun3-kyoto-update.md` |
| 시기 | 2026-05-31(일) ~ 06-03(수) 3박 4일 | 같음 |
| 동반 | 부부 2인 + 시부모 2인 (4인) | 같음 |
| 항공 | 에어서울 인천↔간사이 4인 발권 | 별도 PR (발권 기록) |
| 1·2박 (5/31·6/1) | 시오(Shio) 100년 마치야 에어비앤비 | `docs/decision-log/2026-05-12-04-airbnb-shio-selected.md` |
| 3박 (6/2) | 우메코지 카덴쇼 트립닷컴 (객실 2개, 식사 불포함) | `data/booking-checklist.json` |

## 작업 범위

- **이 레포는 위 교토 여행 실행·운영에만 사용**
- 그 외 모든 주제 (다른 일정, 개인 사정, 가족·업무 이슈 등)는 응답 거부
- 다른 디렉토리·레포·파일 읽기·참조·인용 금지
- 작업은 이 레포 디렉토리 내부 파일에만 한정

## 작성 규칙

- 한국어
- 일정·예약 데이터는 `data/itinerary.json`·`data/booking-checklist.json`에 단일 출처
- 시각 디자인 토큰은 `data/design-tokens.json`에 단일 출처 (DESIGN.md §2~§6과 동기화)
- 사람이 읽는 일지·상세 시나리오는 `docs/*.md`
- 모바일/상세 화면은 `index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/lodging.html`·`viz/checklist.html`·`viz/archive.html` — 모두 `scripts/build_index.py` 산출물 (직접 편집 금지)
- 과거 의사결정 보고서는 `reports/final-report.md` → PDF (아카이브)

## 실행 워크플로우

> 의사결정이 끝났으므로 이제부터의 작업은 모두 "확정된 여행을 사고 없이 다녀오기 위한 실행"이다.

### 1. 발권·예약 기록

- 단일 출처: `data/booking-checklist.json` (예약 진행 상태 7 항목)
- 예약 확정 시: `status`·`reference`(예약번호)·`confirmed_at`(확정일) 갱신 + `docs/decision-log/`에 새 일지 (예약처·금액·취소 정책 요약)
- 발권/예약 영수증·바우처는 본 레포에 첨부하지 않음 (개인정보·메일/카카오톡 원본 보관)
- 발권·결제 금액은 `data/cost-options.json`의 시나리오 입력에도 반영 (확정값으로 `confirmed_booking` 라벨로 승격)

### 2. 일자별 일정

- 단일 출처: `data/itinerary.json` (`days`: 확정 코스, `route_candidates`: 대안 3개)
- 일정 변경 시 JSON 먼저 수정 → `python scripts/build_index.py` 재빌드 → `docs/kyoto-itinerary-may31-jun3-2026.md`(사람용 사본) 동기화
- 신규 일자별 메모(예: 짐 보관 동선·동반자 컨디션·식당 예약 시간) 도 itinerary.json의 해당 day에 추가
- 보기: `viz/itinerary.html`(일자별 카드)·`viz/itinerary-table.html`(4일 시간표)

### 3. 체크리스트 (출국 전·현지·귀국)

- 예약 진행 상태는 `data/booking-checklist.json` + `viz/checklist.html` (기존 자산 재사용)
- 출국 전 준비·현지 동선·귀국 정리 체크리스트는 별도 산출물로 추가 예정 (예: `docs/checklist.md` — 별도 PR)

### 4. 현지 정보 (예정)

- 한국어 가능 병원·영사관(오사카 총영사관)·긴급 연락처·교통 패스(JR Kansai Area Pass·관광패스 등)는 별도 산출물로 추가 (예: `docs/local-info.md` — 별도 PR)
- 시부모 동반이므로 의료 접근성·이동 부담을 사전에 정리

### 5. 모든 변경의 일지화

- 위 1~4의 어떤 변경이든 `docs/decision-log/`에 새 파일 1개 추가 (`YYYY-MM-DD-slug.md`). 컨벤션: `docs/decision-log/README.md`
- 메타 문서화 규칙(본 문서 하단) 동일 적용

## 과거 의사결정 기록 (아카이브)

> 6개 후보지 × 4개 시기 × 동반 옵션 MCDA(다기준 의사결정 분석)은 2026-05-12에 종료. 아래 워크플로우와 산출물은 이제 회귀 가드·재참조용으로만 사용. 신규 후보·기준 비교가 다시 필요해질 때만 재가동한다.

- 정량 비교 흐름: `data/decision.json`의 criteria·가중치 → candidates × criteria 1~10 점수 → `python scripts/score.py` → 종합 점수 → `docs/decision-log/` 일지화 → `reports/final-report.md` → PDF
- 결정의 시계열·근거: `docs/decision-log/` (특히 2026-05-11·2026-05-12 일자 일지)
- 결과물: `reports/final-report.md` (교토·5/31~6/3·4인 최종 권고)

## 디렉토리 구조

```
japan-trip/
├── README.md            # 사람용 안내
├── CLAUDE.md            # AI 세션 지시
├── DESIGN.md            # 시각 디자인 단일 출처 (awesome-design-md 9섹션, Quiet Ledger 테마)
├── index.html           # 메인 운영 페이지 — 요약·일자별 일정 (build_index.py 산출물 — 직접 편집 금지)
├── assets/
│   └── og-*.svg                 # OG/Twitter 카드 이미지 6장 (1200×630 SVG, build_index.py 산출물 — 직접 편집 금지)
├── data/
│   ├── decision.json          # 단일 출처 (criteria + candidates + scores)
│   ├── cost-options.json      # 단일 출처 (flights/lodging/daily_fixed/one_time/scenarios)
│   ├── weather.json           # 후보지 × 시기 기후 + 긴키 매우(梅雨) 평년·실적 + 교토 5/31~6/3 일별 강수 평년
│   ├── flights.json           # 후보지 × 출발지 항공권 시세 스냅샷 (메타사이트 근사)
│   ├── itinerary.json         # 단일 출처 (교토 3박4일 일정 — 일자·시간대·동선·메모 + route_candidates 대안 코스 3개)
│   ├── booking-checklist.json # 단일 출처 (예약 진행 상태 7 항목)
│   └── design-tokens.json     # 단일 출처 (색·타이포·간격·반경, DESIGN.md §2~§6과 동기화)
├── docs/
│   ├── candidates.md                      # 후보지 상세 비교
│   ├── weather.md                         # 날씨 분석 (시기별 쾌적도 순위)
│   ├── flights.md                         # 항공권 분석 (4인 총액·GMP 가용성)
│   ├── decision-log/                      # 의사결정 일지 (항목 1개 = 파일 1개, README.md에 컨벤션)
│   ├── kyoto-itinerary-may-2026.md        # 교토 5월 시나리오 (5/24~27 구버전 — 사람용 사본)
│   ├── kyoto-itinerary-may31-jun3-2026.md # 교토 5/31~6/3 확정 시나리오 (사람용 사본)
│   ├── airbnb-kyoto-may31-jun2-2026.md    # 에어비앤비 5개 매물 비교
│   ├── jejuair-icn-kobe-june-2026.md      # 제주항공 인천-고베 신규 노선·가격 리서치
│   ├── transit-pass-jr-kansai-2026.md     # JR 간사이 에어리어 패스 1/2/3/4일권 비교·권장 (booking-checklist transit_pass 근거)
│   └── transit-mcp-handoff.md             # 후속 세션(Playwright MCP) 위임 가이드 (tbd_needs_browser_mcp leg 측정)
├── viz/
│   ├── itinerary.html         # 일자별 카드 뷰 (build_index.py 산출물 — 직접 편집 금지)
│   ├── itinerary-table.html   # 4일 시간표 뷰 (build_index.py 산출물 — 직접 편집 금지)
│   ├── checklist.html         # 예약 체크리스트 화면 (build_index.py 산출물 — 직접 편집 금지)
│   ├── lodging.html           # 숙박·항공 탭 화면 (build_index.py 산출물 — 직접 편집 금지)
│   └── archive.html           # 의사결정 아카이브 (장마 확률·9 예산 시나리오·7 후보지 점수 — build_index.py 산출물 — 직접 편집 금지)
├── scripts/
│   ├── score.py         # 종합 점수 계산 (--json 지원)
│   ├── budget.py        # 3M 예산 시나리오 평가 (--json 지원)
│   ├── build_index.py   # index.html + viz/*.html(5개: itinerary·itinerary-table·lodging·checklist·archive) + assets/og-*.svg(6장) 빌드 (공통 토큰 주입, --check)
│   ├── validate.py      # 가격 필드·묵은 가격·SYNC 주석·MD↔JSON·DESIGN 동기화 검사
│   └── render-pdf.sh    # PDF 생성
├── tests/               # unittest (validate·build_index·design_tokens·score·budget)
├── .github/workflows/
│   └── validate.yml     # PR 게이트: unittest + build_index --check + validate + score + budget
└── reports/
    └── final-report.md  # 최종 보고서 (PDF 변환 대상)
```

## 데이터 동기화 규칙

- **실행 단일 출처(정본)** — 본 레포의 현재 1차 데이터:
  - `data/itinerary.json` — 교토 3박4일 일정. `days`: 확정 코스 (일자·시간대·동선·메모·도보거리·보류). `route_candidates`: 대안 코스 3개 (여유형·서북 사찰 집중형·미식+문화 체험형). days[].items[].`arrive_from`(mode/duration_min/distance_km/route/source/source_fetched_at/data_quality)으로 장소 간 이동 출처 명시. data_quality는 `official_fare`/`researched_market_rate`/`tbd_needs_browser_mcp`(Playwright MCP 후속 세션 위임). 식사 항목은 days[].items[].`food_quality`(rating/source/source_fetched_at/data_quality/note)로 맛집 근거(타베로그·구글·미쉐린 등 평점) 명시 — 추측 금지, 출처 없으면 검사 H가 머지 차단. 사람용 사본은 `docs/kyoto-itinerary-may31-jun3-2026.md`
  - `data/booking-checklist.json` — 예약 진행 상태
  - `data/cost-options.json` — 항공·숙박·고정비·일회성·시나리오 (확정 금액은 `confirmed_booking` 라벨로 승격)
  - `data/design-tokens.json` — 색·타이포·간격·반경 (DESIGN.md §2~§6과 동기화). `build_index.py`의 `render_css(tokens)`가 6개 산출물(`index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/lodging.html`·`viz/checklist.html`·`viz/archive.html`)의 인라인 CSS를 공통 생성
- **아카이브 단일 출처(참조용)** — 의사결정 종료(2026-05-12) 시점의 입력 데이터. 신규 비교가 필요해질 때만 갱신:
  - `data/decision.json` — criteria·candidates·scores (MCDA 입력. 교토 확정 후 회귀 가드)
  - `data/weather.json` — 후보지×시기 기후 + `tsuyu_normals`(긴키 매우입·매우명 평년 + 최근 7년 실적) + `cities.kyoto.sub_monthly_precip`(순계열)·`trip_window_daily_precip`(5/31~6/3 일별). 원자료: JMA 매우 평년값·京都(47759) 일별 평년값 1991–2020. `docs/weather.md` §5와 동기화. 5/31~6/3 실측 기상 추적이 필요해지면 본 파일의 `cities.kyoto`에 새 키로 추가
  - `data/flights.json` — 후보지×출발지 항공권 시세 스냅샷 (시점 스냅샷, snapshot_date 명시). 발권은 별도 PR로 `data/booking-checklist.json`·`data/cost-options.json`에 기록
- **`index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/checklist.html`·`viz/lodging.html`·`viz/archive.html`·`assets/og-*.svg`(6장)는 `scripts/build_index.py` 산출물 — 직접 편집 금지**. 데이터(`data/*.json`)·스크립트 변경 후 `python scripts/build_index.py` 실행. CI(`build_index.py --check`)가 6 HTML + 6 SVG = 12개 산출물의 drift를 PR 단계에서 차단
- 메인 페이지(`index.html`)는 **운영 모드** — 요약·일자별 일정만. 분석·결정 자료(장마 확률·9 예산 시나리오·7 후보지 점수)는 `viz/archive.html`로 분리. 받는 사람에게 "아직 결정 중"으로 읽히는 콘텐츠는 메인에서 제외
- `docs/weather.md`·`docs/flights.md`의 표는 각각 `data/weather.json`·`data/flights.json`의 사람용 사본 — JSON 수정 시 함께 갱신 (CI 게이트: `scripts/validate.py` E·F가 도시·시기 수치, snapshot_date, 시세 표기의 drift를 PR 단계에서 차단)
- `docs/kyoto-itinerary-may31-jun3-2026.md`는 `data/itinerary.json`의 사람용 마크다운 사본 (JSON이 정본). 일정 변경 시 JSON을 먼저 수정 → 마크다운 함께 갱신
- `data/flights.json`은 **시점 스냅샷**. 시세 재조회 시 새 스냅샷으로 덮어쓰지 말고 snapshot_date 갱신 + 변경 사유를 `docs/decision-log/`에 새 일지로 기록
- 카드 블록 위 `<!-- SYNC: <출처> -->` 주석으로 동기화 대상 명시 (예: `<!-- SYNC: reports/final-report.md §1 -->`). `scripts/validate.py`가 경로 유효성과 §N 절 번호를 검증
- 외부 문서 링크는 GitHub blob URL(`https://github.com/ywkim/japan-trip/blob/main/...`) 사용 — Vercel(본 레포의 호스트)이 `.md` 파일을 자동 렌더하지 않고 raw text로 서빙하므로 상대 경로(`reports/final-report.md`)는 금지

## CI 검증 (PR 게이트)

`.github/workflows/validate.yml`이 모든 PR에서 다음을 실행한다.

| 검사 | 스크립트 | 실패 조건 |
|---|---|---|
| 단위 테스트 | `python -m unittest discover tests` | 1개라도 실패 |
| 점수 계산 동작 | `scripts/score.py` | exit ≠ 0 |
| 예산 평가 동작 | `scripts/budget.py` | exit ≠ 0 |
| 가격 필드 무결성 | `scripts/validate.py` (B) | `cost-options.json`의 `flights`/`lodging`/`daily_fixed`/`one_time` 항목에 `source`·`data_quality` 누락, `data_quality` 값이 화이트리스트 외 |
| 묵은 가격 | `scripts/validate.py` (C) | `researched_market_rate` 항목 source 일자 > 60일 (30~60일은 경고만) |
| SYNC 주석 무결성 | `scripts/validate.py` (D) | `index.html`의 SYNC 주석에 명시된 path가 존재하지 않음, §N이 final-report 절 수보다 큼 |
| weather MD↔JSON 동기화 | `scripts/validate.py` (E) | `docs/weather.md`의 도시·시기 수치가 `data/weather.json`과 일치하지 않음 |
| flights MD↔JSON 동기화 | `scripts/validate.py` (F) | `docs/flights.md`의 snapshot_date·시세 수치가 `data/flights.json`과 일치하지 않음 |
| itinerary arrive_from 무결성 | `scripts/validate.py` (G) | `data/itinerary.json` arrive_from에 mode/source/source_fetched_at/data_quality 누락, mode·data_quality 화이트리스트 외, source_fetched_at > 60d(tbd_needs_browser_mcp 제외), days[].walking_km보다 도보 leg 합이 2km 이상 초과 |
| DESIGN MD↔JSON 동기화 | `scripts/validate.py` (H) | `DESIGN.md`의 hex가 `data/design-tokens.json`에 없거나 그 반대, theme_name·version drift |
| itinerary food_quality 무결성 | `scripts/validate.py` (I) | `data/itinerary.json` 식사 항목 food_quality에 rating/source/source_fetched_at/data_quality 누락, data_quality 화이트리스트 외, source_fetched_at > 60d. food_quality 없는 항목(동네 끼니)은 면제. route_candidates도 순회 |
| 빌드 산출물 drift | `scripts/build_index.py --check` | `index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/lodging.html`·`viz/checklist.html` 중 하나라도 빌드 결과와 다름 |

## 디자인 워크플로우

6개 산출물(`index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/lodging.html`·`viz/checklist.html`·`viz/archive.html`)의 시각 변경 시:

1. `DESIGN.md` 편집 (의도·규칙 먼저).
2. `data/design-tokens.json` 동기화 (DESIGN.md §2~§6의 모든 hex·치수가 토큰에 반영되어야 함).
3. `python scripts/build_index.py` 실행 → 6개 산출물이 공통 `render_css(tokens)`로 재생성.
4. `python scripts/validate.py` (H 통과) + `python scripts/build_index.py --check` (drift 없음) 확인.
5. `data/design-tokens.json`이 단일 출처. 인라인 hex 추가 금지 — 새 색은 반드시 토큰 키 추가 후 `var(--키)`로 참조.

상세 가이드: `DESIGN.md` §9 (Agent Prompt Guide).

## 테스트 작성 규칙 (TDD)

- **스크립트(`scripts/*.py`) 또는 빌드/검증 로직을 변경할 때는 `tests/`의 테스트를 먼저 작성/갱신**한 뒤 코드를 수정한다. 새 분기·새 검사 규칙·새 출력 필드는 실패하는 테스트가 먼저 들어와야 한다.
- 테스트는 `unittest` 표준 라이브러리만 사용. 외부 의존성 추가 금지 (CI 단순화).
- 데이터 변경(JSON·MD)은 테스트 작성 의무에서 제외 — 단, 데이터 스키마 변경(필드 추가/제거)은 `validate.py` 화이트리스트와 함께 테스트 갱신.
- 테스트가 production 데이터에 의존하는 케이스(`ProductionDataTests`)는 회귀 가드로만 사용. 새 규칙 검증은 `tempfile` 기반 fixture로 격리.
- 로컬 실행: `python -m unittest discover -s tests -v`. CI도 동일 명령으로 실행.

## 점수 입력 규칙

- 1~10 정수
- 각 기준의 `direction`이 `higher_is_better`/`lower_is_better` — 점수는 항상 "높을수록 좋게" 정규화하여 입력
  - 예: 비용은 `lower_is_better`이지만 점수는 "비용 부담이 적을수록 높은 점수"로 입력
- 점수 입력 시 `notes` 필드에 근거 짧게 기록

## 실시간 가격 리서치 우선 (모든 세션 공통, 강제 규칙)

> 여행 계획의 본질은 리서치다. 가격·운임·시세·운영 정보는 매일 바뀌므로
> AI 학습 데이터의 기억으로 대체할 수 없다. 모든 세션은 다음 규칙을 따른다.

### 절대 금지

- ❌ **학습 데이터 기반 가격 추측 금지** — "보통 그쯤" 같은 표현으로 숫자 입력 금지
- ❌ **출처 없는 숫자 입력 금지** — `source` 필드 비어 있으면 머지 불가
- ❌ **"적절한 추정값"으로 빈칸 채우기 금지** — 차라리 `null` + TBD 유지
- ❌ **사용자가 보여준 스크린샷 외 가격을 임의 추정해 비교 금지**

### 가격·시세 입력 시 의무 절차

1. **WebSearch/WebFetch로 실시간 검색** (Klook·Booking·Agoda·Trip.com·Airbnb·공식 사이트 등)
2. **여러 출처 교차 검증** — 단일 사이트 가격에 의존하지 않음
3. **`source` 필드에 사이트명·검색 일자 기록** (예: "Klook 2026-05-09")
4. **`data_quality` 라벨 부여** (아래 분류 사용)
5. 환율 가정 명시 (`fx_assumption` 필드 등) — 엔→원 환산 시 기준 환율 기록

### `data_quality` 분류

| 라벨 | 의미 | 예 |
|---|---|---|
| `confirmed_booking` | 사용자가 본 실제 예약 사이트 가격 (스크린샷·링크) | Skyscanner·Agoda 스크린샷 가격 |
| `official_fare` | 공식 운영자 발표 운임/요금 | JR 공식, 시 교통, 사찰 입장료 |
| `researched_market_rate` | 비교 사이트·블로그·여행 가이드 시세 | Klook 평균, 트립스토어 가이드 |

→ 시나리오 평가 출력 시에도 라벨별로 신뢰도가 다름을 사용자에게 표시.

### 사용자에게 제시할 때

- "약 30만원 정도 예상" 같은 모호한 표현 금지
- "Klook 2026-05-09 검색 기준 ₩300,000" 처럼 출처·시점 명시
- 리서치가 부족한 항목은 정직하게 "TBD — 리서치 필요" 표기

### 가격 데이터 갱신 정책

- 예약 시점에 모든 `researched_market_rate` 항목을 재검색 → `confirmed_booking`으로 승격
- 30일 이상 묵은 리서치 가격은 신뢰하지 않고 재조회

## 메타 문서화 규칙 (모든 PR 공통)

> 이후 모든 의사결정에 자료가 누적·재사용되도록, 어떤 PR이든 작업물뿐 아니라
> 메타 문서를 함께 갱신한다. 이는 강제 규칙이며 예외 없음.

### ADR(Nygard) 형식 — decision-log 항목·PR 본문 (필수)

**근거**: Michael Nygard, "Documenting Architecture Decisions" (2011). 결정의 "왜(Context)"를 명시적으로 남겨 후속 세션이 의도를 빠르게 복원할 수 있도록 한다.

**적용 대상**:
- `docs/decision-log/YYYY-MM-DD-slug.md` (모든 신규 일지)
- 모든 PR 본문 (Summary 영역)

**5섹션 표준 (Korean 매핑)**:

| ADR 섹션 | 한국어 의도 | 필수 | 설명 |
|---|---|---|---|
| Title | 한 줄 명사구 | ✓ | `# YYYY-MM-DD — 주제` 형태 |
| Status | 상태 | △ | `Accepted`(기본·자명할 시 PR 본문에서 생략 가능) / `Proposed` / `Deprecated` / `Superseded by <YYYY-MM-DD-slug.md>` |
| Context (왜) | 결정을 강제한 힘·사실 | ✓ | 사실 위주, 가치판단 배제. 시점·환경·외부 사건·알려진 대안과 한계 |
| Decision (무엇) | 채택한 행동 | ✓ | 능동태 1개. 채택하지 않은 대안은 한 줄씩 사유와 함께 |
| Consequences (그래서) | 결정의 결과 | ✓ | 긍정 / 부정·트레이드오프 / 후속 행동 / 영향 받은 파일·데이터 |

**공용 템플릿** (decision-log·PR 본문 동일):

```markdown
# YYYY-MM-DD — 한 줄 명사구 (Title)

## Status

Accepted | Proposed | Deprecated | Superseded by `<YYYY-MM-DD-slug.md>`

## Context (왜)

- 이 결정을 강제한 힘·문제·제약 (사실 위주)
- 시점·환경·외부 사건 (예: 채팅 업로드, 가격 변동, 사용자 지시)
- 알려진 대안과 그 한계 (필요 시)

## Decision (무엇)

- 능동태로 명시한 채택 행동 1개
- 채택하지 않은 대안은 한 줄씩 사유와 함께 (선택)

## Consequences (그래서)

- 긍정 영향
- 부정·트레이드오프
- 후속 행동·별도 PR 필요 항목
- 영향 받은 파일·데이터 (해당 시)
```

**PR 본문 추가 규칙**: 위 4섹션(Status 생략 가능) 다음에 기존 `## Test plan` 체크리스트를 그대로 유지. Test plan은 ADR 외 운영 항목으로 본문 하단에 둔다.

**Cutover**: 2026-05-20 ADR 도입 일지 (`docs/decision-log/2026-05-20-02-adr-format-mandate.md`) 머지 이후 모든 신규 PR/일지에 적용. **기존 일지는 시점 스냅샷으로 보존**(`reports/final-report.md` 동일 원칙) — retroactive 변환 금지.

**예외**: 본 문서 하단 "메타 문서를 갱신하지 않는 경우"의 `META: skip` 예외(오타 수정 등)에 해당하면 일지도 생략 가능.

### 모든 PR이 반드시 갱신해야 하는 항목

1. **`docs/decision-log/`**
   - **새 파일을 추가**한다. 기존 파일을 편집하지 않는다 (충돌 방지).
   - 파일명 `YYYY-MM-DD-slug.md` (같은 날 여러 항목이면 슬러그로 구분, 강한 순서가 필요하면 `YYYY-MM-DD-NN-slug.md`)
   - **형식**: 위 "ADR(Nygard) 형식" 절의 공용 템플릿을 따른다.
   - 컨벤션 상세: `docs/decision-log/README.md`

2. **`README.md`**
   - 새 산출물(데이터·문서·스크립트·뷰)이 추가되면 사용법·디렉토리 안내에 1줄 이상 반영
   - 사람이 처음 레포에 들어와도 해당 산출물의 존재·용도를 5초 안에 인지할 수 있어야 함

3. **`CLAUDE.md` (본 파일)**
   - 새 파일·디렉토리가 생기면 "디렉토리 구조" 트리에 추가
   - 새 작업 패턴/제약/데이터 출처가 생기면 해당 섹션 신설 또는 기존 섹션 보강
   - **새 데이터 파일을 만들면 "단일 출처는 무엇인가, 동기화 대상은 무엇인가"를 명시**

### 데이터 산출물 PR의 추가 의무

- 데이터 출처(예: JMA, 정부 통계, 공개 API) 명시
- 갱신 주기·평년값 vs 실측 구분 명시
- 점수화한 경우 점수 기준(1~10이 무엇을 의미하는지)을 `docs/`에 기록
- **가격·운임·시세 데이터는 "실시간 가격 리서치 우선" 섹션 규칙 따름**
  - 모든 가격 항목에 `source` + `data_quality` + 검색 일자
  - 추측치·기억 기반 가격 입력은 PR 머지 차단 사유

### 메타 문서를 갱신하지 않는 경우

- PR을 머지하지 않음. 누적 의사결정 자산이 깨지므로 예외 없음.
- 정말 메타 갱신이 불필요한 변경(오타 수정 등)이면 PR 본문에 "META: skip — 사유" 명시
