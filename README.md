# 일본 여행 협업

영욱·소연이 함께 일본 여행을 정량적으로 결정하기 위한 공간.

## 사용법

### 1. 후보·기준 함께 정하기
- `data/decision.json` 열기
- `candidates`에 후보지 추가/삭제
- `criteria`의 가중치 함께 조정 (합계 1.0)

### 2. 점수 매기기
- 각자 후보별로 1~10 점수 입력
- 의견이 다르면 `notes`에 이유 적기

### 3. 결과 보기
- 터미널에서 `python scripts/score.py` 실행 (의사결정 확정 후 회귀 가드)

### 3-1. 예산 (3M 하드캡) 통과 여부 확인
- `data/cost-options.json`에 항공·숙박·고정비·일회성 단가와 시나리오 입력
- `python scripts/budget.py` 실행 → 시나리오별 확정 합계·여유·TBD 항목 출력
- 상세: `docs/budget-options.md`

### 4. 결정 기록
- `docs/decision-log/` 디렉토리에 **새 파일** 추가 (`YYYY-MM-DD-slug.md`). 기존 파일은 편집하지 않음.
- 컨벤션: `docs/decision-log/README.md`
- 최종 결정 후 `reports/final-report.md` 작성 → `bash scripts/render-pdf.sh`로 PDF

### 5. 보조 데이터 활용
- `data/weather.json` — 후보지 × 시기 기후 데이터 (JMA 평년값) + `tsuyu_normals`(긴키 매우입·매우명 평년 + 최근 8년 실적 + `sokuhou_2026` 2026 속보 스냅샷) + `cities.kyoto.sub_monthly_precip`(순계열 강수)·`trip_window_daily_precip`(5/31~6/3 일별 평년)
- `docs/weather.md` — 시기별 쾌적도 순위, `seasonality`/`physical_burden` 점수 제안. §5에 교토 5/31~6/3 장마 정량 분석 (평년 입림 6/6, 여행 4일 합계 ~16mm, 최근 8년 기준 조기 입림 확률 ~25%, 2026-05-14 시점 긴키 미발표)
- `docs/screenshots/jma-sokuhou-2026-05-14-*.png` — JMA 2026 매우 속보 페이지 검증 캡처 (Playwright)
- `data/flights.json` — 후보지 × 출발지(ICN/GMP) 항공권 시세 스냅샷
- `docs/flights.md` — 4인 총액 비교, GMP 가용성, `cost` 점수 환산 가이드
- **`seasonality` 점수는 현재 2026-05 시기 고정** — 각 후보의 `weather.json` 2026-05 `comfort_score`를 `decision.json`에 그대로 입력. 다른 시기로 비교하려면 `weather.json`에서 해당 월 `comfort_score`로 수동 교체 (스키마 확장은 미실시). 상세: `docs/decision-log/2026-05-11-seasonality-scoring.md`

### 6. 모바일에서 결정 보기
- `index.html` — 모바일-퍼스트 8섹션 카드 (요약·에어비앤비·카덴쇼·항공·예산·일정·체크리스트·점수). 인라인 데이터로 자기완결, 더블클릭 동작
- `viz/itinerary.html` — 일자별 상세 일정 카드 뷰 (시간대·동선·메모·도보거리·보류 사항). `data/itinerary.json` 단일 출처
- `viz/itinerary-table.html` — 3박4일 **시간표 뷰** (4일 열 × 시간대 행). 한 화면에서 전체 일정 비교. `data/itinerary.json` 단일 출처
- `viz/checklist.html` — 예약 진행 상태 (기한 이른 순 정렬, 상태별 카운트). `data/booking-checklist.json` 단일 출처
- **4개 모두 `scripts/build_index.py` 빌드 산출물 — 직접 편집 금지**. 데이터(`data/*.json`)·스크립트 변경 후 `python scripts/build_index.py` 실행. CI(`build_index.py --check`)가 모든 산출물의 drift를 차단
- 각 섹션 위 `<!-- SYNC: ... -->` 주석이 데이터 출처를 명시. CI(`scripts/validate.py`)가 경로 유효성과 §N 절 번호를 검증

### 7. 검증 (CI)
- `python -m unittest discover tests` — 단위 테스트 (validate·build_index·design_tokens·score·budget)
- `python scripts/validate.py` — 가격 필드 무결성(source·data_quality), 30/60일 묵은 가격 경고/실패, SYNC 주석 경로·절 번호 검증, `docs/weather.md`↔`data/weather.json`, `docs/flights.md`↔`data/flights.json`, `DESIGN.md`↔`data/design-tokens.json` 동기화 검증
- `python scripts/build_index.py --check` — `index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/checklist.html` 4개 산출물이 데이터·토큰과 동기화 상태인지 (drift 시 exit 1)
- `.github/workflows/validate.yml`이 PR마다 unittest + 위 4개 실행

### 8. 시각 디자인 출처
- `DESIGN.md` — 시각 디자인 컨벤션 (`voltagent/awesome-design-md` 9섹션). Quiet Ledger 테마: paper-white + slate-indigo accent. AI 에이전트가 UI 변경 작업 시 본 파일을 1차 참조
- `data/design-tokens.json` — 색·타이포·간격·반경 단일 출처. `scripts/build_index.py`의 `render_css(tokens)`가 4개 산출물(`index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/checklist.html`)의 인라인 CSS를 공통 생성
- 동기화 게이트: `scripts/validate.py` (G)가 DESIGN.md ↔ tokens의 drift를 PR 단계에서 차단

## 평가 기준 (초안 — 함께 조정)

| 기준 | 의미 | 초기 가중치 |
|---|---|---|
| cost | 비용 부담 (낮을수록 좋음) | 0.20 |
| schedule_fit | 일정 적합성 | 0.15 |
| physical_burden | 신체 부담 (낮을수록 좋음) | 0.15 |
| experience | 경험 가치 | 0.20 |
| family_fit | 가족 동반 적합성 | 0.10 |
| medical_access | 의료 접근성 | 0.10 |
| seasonality | 계절성 | 0.10 |

## 후보지 (초안 — 함께 추가/삭제)

도쿄, 오사카, 교토, 홋카이도(삿포로), 오키나와, 후쿠오카, 고베

> **고베**: 2026-06-11 제주항공(7C) 인천-고베(ICN-UKB) 직항 신규 취항 + 취항 기념 프로모션을 계기로 후보 추가. 노선·가격·날씨 상세는 `docs/jejuair-icn-kobe-june-2026.md`

## 디렉토리

```
DESIGN.md    # 시각 디자인 컨벤션 (awesome-design-md 9섹션, Quiet Ledger)
data/        # decision·cost-options·weather·flights·itinerary·booking-checklist·design-tokens (단일 출처 JSON)
docs/        # 비교표, 날씨·항공권 분석, 의사결정 일지(decision-log/)
viz/         # itinerary.html·itinerary-table.html·checklist.html (build_index.py 산출물)
scripts/     # score·budget·build_index·validate·render-pdf
tests/       # unittest (validate·build_index·design_tokens·score·budget)
reports/     # 최종 보고서
index.html   # 모바일 8섹션 카드 (build_index.py 산출물)
```

## 환경 요구

- Python 3 (점수 계산·빌드)
- pandoc 또는 Chrome (PDF 변환, 선택)
- 브라우저 (index.html·viz/itinerary.html·viz/checklist.html 더블클릭)

## 변경 규칙 (모든 PR 공통)

이 레포는 **누적되는 의사결정 자산**을 목표로 하므로, 어떤 변경이든 다음 메타 문서를 함께 갱신한다.

| 갱신 대상 | 무엇을 적나 |
|---|---|
| `docs/decision-log/YYYY-MM-DD-slug.md` (새 파일) | 날짜·주제·산출물·합의/보류/다음 단계 |
| `README.md` (이 파일) | 새 산출물의 사용법·디렉토리 1줄 이상 |
| `CLAUDE.md` | 디렉토리 트리·작업 규칙·데이터 동기화 규칙 |

데이터 산출물(예: `data/weather.json`)을 추가할 땐 출처·갱신 주기·점수 기준도 `docs/`에 함께 기록한다.
상세 규칙은 `CLAUDE.md` 의 **메타 문서화 규칙** 섹션 참조.
