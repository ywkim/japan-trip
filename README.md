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

### 4. 결정 기록
- `docs/decision-log.md`에 합의 사항·보류 사항 기록
- 최종 결정 후 `reports/final-report.md` 작성 → `bash scripts/render-pdf.sh`로 PDF

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
data/        # 의사결정 데이터 (JSON 단일 출처)
docs/        # 비교표, 의사결정 일지
viz/         # 인터랙티브 대시보드 (HTML)
scripts/     # 계산·PDF 변환 스크립트
reports/     # 최종 보고서
```

## 환경 요구

- Python 3 (점수 계산)
- pandoc 또는 Chrome (PDF 변환, 선택)
- 브라우저 (대시보드)
