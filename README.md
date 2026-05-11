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
- 브라우저로 `viz/dashboard.html` 더블클릭 → 가중치 슬라이더로 민감도 확인
- 또는 터미널에서 `python scripts/score.py` 실행

### 3-1. 예산 (3M 하드캡) 통과 여부 확인
- `data/cost-options.json`에 항공·숙박·고정비·일회성 단가와 시나리오 입력
- `python scripts/budget.py` 실행 → 시나리오별 확정 합계·여유·TBD 항목 출력
- 상세: `docs/budget-options.md`

### 4. 결정 기록
- `docs/decision-log.md`에 합의 사항·보류 사항 기록
- 최종 결정 후 `reports/final-report.md` 작성 → `bash scripts/render-pdf.sh`로 PDF

### 5. 보조 데이터 활용
- `data/weather.json` — 후보지 × 시기 기후 데이터 (JMA 평년값)
- `docs/weather.md` — 시기별 쾌적도 순위, `seasonality`/`physical_burden` 점수 제안

### 6. 모바일에서 결정 보기
- `index.html` — 모바일-퍼스트 최종 결정 요약 (목적지·시기·예산·왜·일정 한눈에). 카드 단을 세로로 쌓아 작은 화면에서 읽기 쉽도록 구성. 더블클릭 또는 GitHub Pages URL로 접근

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

도쿄, 오사카, 교토, 홋카이도(삿포로), 오키나와, 후쿠오카

## 디렉토리

```
data/        # 의사결정 데이터 (decision.json: 정본, weather.json: 보조)
docs/        # 비교표, 날씨 분석, 의사결정 일지
viz/         # 인터랙티브 대시보드 (HTML)
scripts/     # 계산·PDF 변환 스크립트
reports/     # 최종 보고서
```

## 환경 요구

- Python 3 (점수 계산)
- pandoc 또는 Chrome (PDF 변환, 선택)
- 브라우저 (대시보드)

## 변경 규칙 (모든 PR 공통)

이 레포는 **누적되는 의사결정 자산**을 목표로 하므로, 어떤 변경이든 다음 메타 문서를 함께 갱신한다.

| 갱신 대상 | 무엇을 적나 |
|---|---|
| `docs/decision-log.md` | 날짜·주제·산출물·합의/보류/다음 단계 |
| `README.md` (이 파일) | 새 산출물의 사용법·디렉토리 1줄 이상 |
| `CLAUDE.md` | 디렉토리 트리·작업 규칙·데이터 동기화 규칙 |

데이터 산출물(예: `data/weather.json`)을 추가할 땐 출처·갱신 주기·점수 기준도 `docs/`에 함께 기록한다.
상세 규칙은 `CLAUDE.md` 의 **메타 문서화 규칙** 섹션 참조.
