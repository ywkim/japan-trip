# japan-trip

## 레포 목적

영욱·소연 부부의 일본 여행 정량 의사결정 협업 공간.

## 작업 범위

- **이 레포는 일본 여행 의사결정에만 사용**
- 그 외 모든 주제 (다른 일정, 개인 사정, 가족·업무 이슈 등)는 응답 거부
- 다른 디렉토리·레포·파일 읽기·참조·인용 금지
- 작업은 이 레포 디렉토리 내부 파일에만 한정

## 작성 규칙

- 한국어
- 의사결정 데이터는 `data/decision.json`에 단일 출처
- 사람이 읽는 비교표·일지는 `docs/*.md`
- 시각화는 `viz/dashboard.html` (인라인 데이터로 자체 완결, 더블클릭 동작)
- 보고서는 `reports/final-report.md` → PDF

## 정량 의사결정 워크플로우 (MCDA)

1. `data/decision.json`의 `criteria`에 평가 기준·가중치 정의 (가중치 합계 = 1.0)
2. `data/decision.json`의 `candidates`에 후보지 추가
3. 각 후보 × 각 기준 → 1~10 점수 입력 (`scores` 객체)
4. `python scripts/score.py` 실행 → 종합 점수 출력
5. `viz/dashboard.html`에서 가중치 슬라이더로 민감도 확인
6. `docs/decision-log/`에 항목 1개 = 파일 1개로 결정 근거 기록 (파일명 `YYYY-MM-DD-slug.md`)
7. `reports/final-report.md` 갱신 → `bash scripts/render-pdf.sh`로 PDF 생성

## 디렉토리 구조

```
japan-trip/
├── README.md            # 사람용 안내
├── CLAUDE.md            # AI 세션 지시
├── index.html           # 모바일 8섹션 카드 (build_index.py 산출물 — 직접 편집 금지)
├── data/
│   ├── decision.json          # 단일 출처 (criteria + candidates + scores)
│   ├── cost-options.json      # 단일 출처 (flights/lodging/daily_fixed/one_time/scenarios)
│   ├── weather.json           # 후보지 × 시기 기후 + 긴키 매우(梅雨) 평년·실적 + 교토 5/31~6/3 일별 강수 평년
│   ├── flights.json           # 후보지 × 출발지 항공권 시세 스냅샷 (메타사이트 근사)
│   └── booking-checklist.json # 단일 출처 (예약 진행 상태 8 항목)
├── docs/
│   ├── candidates.md                      # 후보지 상세 비교
│   ├── weather.md                         # 날씨 분석 (시기별 쾌적도 순위)
│   ├── flights.md                         # 항공권 분석 (4인 총액·GMP 가용성)
│   ├── decision-log/                      # 의사결정 일지 (항목 1개 = 파일 1개, README.md에 컨벤션)
│   ├── kyoto-itinerary-may-2026.md        # 교토 5월 시나리오 (4인 시부모 동반)
│   ├── airbnb-kyoto-may31-jun2-2026.md    # 에어비앤비 5개 매물 비교
│   └── jejuair-icn-kobe-june-2026.md      # 제주항공 인천-고베 신규 노선·가격 리서치
├── viz/
│   └── dashboard.html   # 인터랙티브 대시보드 (가중치 슬라이더)
├── scripts/
│   ├── score.py         # 종합 점수 계산 (--json 지원)
│   ├── budget.py        # 3M 예산 시나리오 평가 (--json 지원)
│   ├── build_index.py   # index.html 빌드 (--check 모드로 CI drift 검사)
│   ├── validate.py      # 가격 필드·묵은 가격·SYNC 주석 무결성 검사
│   └── render-pdf.sh    # PDF 생성
├── tests/               # unittest (validate·build_index·score·budget)
├── .github/workflows/
│   └── validate.yml     # PR 게이트: unittest + build_index --check + validate + score + budget
└── reports/
    └── final-report.md  # 최종 보고서 (PDF 변환 대상)
```

## 데이터 동기화 규칙

- 단일 출처(정본):
  - `data/decision.json` — criteria·candidates·scores
  - `data/cost-options.json` — 항공·숙박·고정비·일회성·시나리오
  - `data/weather.json` — 후보지×시기 기후 + `tsuyu_normals`(긴키 매우입·매우명 평년 + 최근 7년 실적) + `cities.kyoto.sub_monthly_precip`(순계열)·`trip_window_daily_precip`(5/31~6/3 일별). 원자료: JMA 매우 평년값·京都(47759) 일별 평년값 1991–2020. `docs/weather.md` §5와 동기화
  - `data/flights.json` — 후보지×출발지 항공권 시세 스냅샷 (시점 스냅샷, snapshot_date 명시)
  - `data/booking-checklist.json` — 예약 진행 상태
- **`index.html`은 `scripts/build_index.py` 산출물 — 직접 편집 금지**. 데이터·일정 표 변경 후 `python scripts/build_index.py` 실행. CI(`build_index.py --check`)가 PR 단계에서 drift를 차단
- `viz/dashboard.html`은 인라인 데이터 (브라우저 더블클릭 동작 보장). 본 파일은 아직 build_index 대상이 아니므로 `data/decision.json` 수정 시 수동 갱신 (TODO: build 통합)
- `docs/weather.md`·`docs/flights.md`의 표는 각각 `data/weather.json`·`data/flights.json`의 사람용 사본 — JSON 수정 시 함께 갱신
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
| index.html drift | `scripts/build_index.py --check` | 빌드 결과 ≠ 커밋된 index.html |

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

### 모든 PR이 반드시 갱신해야 하는 항목

1. **`docs/decision-log/`**
   - **새 파일을 추가**한다. 기존 파일을 편집하지 않는다 (충돌 방지).
   - 파일명 `YYYY-MM-DD-slug.md` (같은 날 여러 항목이면 슬러그로 구분, 강한 순서가 필요하면 `YYYY-MM-DD-NN-slug.md`)
   - 내용: 날짜·주제·산출물·합의·보류·다음 단계
   - 데이터/분석 PR은 **핵심 관찰 3~5줄**도 포함
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
