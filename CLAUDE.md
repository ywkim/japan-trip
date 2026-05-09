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
6. `docs/decision-log.md`에 결정 근거 기록
7. `reports/final-report.md` 갱신 → `bash scripts/render-pdf.sh`로 PDF 생성

## 디렉토리 구조

```
japan-trip/
├── README.md            # 사람용 안내
├── CLAUDE.md            # AI 세션 지시
├── data/
│   ├── decision.json    # 단일 출처 (criteria + candidates + scores)
│   └── weather.json     # 후보지 × 시기 기후 데이터 (JMA 평년값)
├── docs/
│   ├── candidates.md             # 후보지 상세 비교
│   ├── weather.md                # 날씨 분석 (시기별 쾌적도 순위)
│   ├── dashboard-alternatives.md # 대시보드 필요성·대안 검토
│   └── decision-log.md           # 의사결정 일지
├── viz/
│   └── dashboard.html   # 인터랙티브 대시보드 (가중치 슬라이더)
├── scripts/
│   ├── score.py         # 종합 점수 계산
│   └── render-pdf.sh    # PDF 생성
└── reports/
    └── final-report.md  # 최종 보고서 (PDF 변환 대상)
```

## 데이터 동기화 규칙

- `viz/dashboard.html`은 인라인 데이터 (브라우저 더블클릭 동작 보장)
- `data/decision.json` 수정 시 → HTML의 인라인 데이터도 동시 갱신 필요
- 단일 출처는 `data/decision.json` (정본)
- 단일 출처는 `data/weather.json`. `docs/weather.md`의 표는 사람용 사본 — JSON 수정 시 함께 갱신

## 점수 입력 규칙

- 1~10 정수
- 각 기준의 `direction`이 `higher_is_better`/`lower_is_better` — 점수는 항상 "높을수록 좋게" 정규화하여 입력
  - 예: 비용은 `lower_is_better`이지만 점수는 "비용 부담이 적을수록 높은 점수"로 입력
- 점수 입력 시 `notes` 필드에 근거 짧게 기록

## 메타 문서화 규칙 (모든 PR 공통)

> 이후 모든 의사결정에 자료가 누적·재사용되도록, 어떤 PR이든 작업물뿐 아니라
> 메타 문서를 함께 갱신한다. 이는 강제 규칙이며 예외 없음.

### 모든 PR이 반드시 갱신해야 하는 항목

1. **`docs/decision-log.md`**
   - 새 일지 항목 추가: 날짜, 주제, 산출물, 합의·보류·다음 단계
   - 데이터/분석 PR은 **핵심 관찰 3~5줄**도 포함

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

### 메타 문서를 갱신하지 않는 경우

- PR을 머지하지 않음. 누적 의사결정 자산이 깨지므로 예외 없음.
- 정말 메타 갱신이 불필요한 변경(오타 수정 등)이면 PR 본문에 "META: skip — 사유" 명시
