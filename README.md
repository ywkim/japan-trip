# 일본 여행 협업

영욱·소연 부부의 **2026-05-31(일)~06-03(수) 교토 4인 가족 여행 (부부 + 시부모) 실행** 협업 공간.

> 정량 비교를 통한 목적지·시기·동반 의사결정은 2026-05-12에 종료. 본 레포는 이제 발권·예약·일정·체크리스트·현지 운영 정보를 누적·갱신한다. 과거 의사결정 자료(MCDA·후보 비교·시기 비교)는 보존되며 `docs/decision-log/`·`data/`에서 그대로 조회 가능.

## 확정 사항

| 항목 | 확정 내용 |
|---|---|
| 목적지 | 교토 (관서) |
| 시기 | 2026-05-31(일) ~ 06-03(수) 3박 4일 |
| 동반 | 부부 2인 + 시부모 2인 (4인) |
| 항공 | 에어서울 인천↔간사이 4인 발권 |
| 1·2박 (5/31·6/1) | 시오(Shio) 100년 마치야 에어비앤비 |
| 3박 (6/2) | 우메코지 카덴쇼 트립닷컴 (객실 2개, 식사 불포함) |

상세는 `docs/kyoto-itinerary-may31-jun3-2026.md` (사람용 일정), `docs/decision-log/` (의사결정 시계열).

## 사용법

### 1. 확정 정보 보기 (모바일·웹)

- 배포: https://nihon-trip.vercel.app (Vercel, main 브랜치 자동 배포). 산출물(HTML·SVG)은 레포에 커밋하지 않고 배포 시점에 `vercel.json`의 `buildCommand`(`uv run python scripts/build_index.py`)로 빌드
- `index.html` — 🏠 홈 탭 (운영 모드): 요약 + 일자별 일정. 하단 고정 4탭 내비게이션. 인라인 데이터로 자기완결, 더블클릭 동작
- `viz/itinerary.html` — 📅 일정 탭: 일자별 상세 일정 카드 뷰 (시간대·동선·메모·이미지). `data/itinerary.json` 단일 출처. 이동 설명은 평이 요약(예: "🚌 버스로 35분") + 접기(상세 경로·링크)로 표시. 긴 장소 메모·맛집 상세 노트도 첫 문장 요약 + 접기(맛집 평점 줄은 항상 노출) — 모바일에서 시간·장소가 먼저 읽히도록
- `viz/itinerary-table.html` — 📅 일정 탭: 3박4일 **시간표 뷰** (4일 열 × 시간대 행, 모바일 카드/데스크탑 테이블 자동 전환). `data/itinerary.json` 단일 출처
- `viz/lodging.html` — ✈️ 숙박·항공 탭: 에어비앤비·카덴쇼·항공편 확정 예약 내역. `data/cost-options.json` 단일 출처
- `viz/checklist.html` — ✅ 예약 탭: 예약 진행 상태 (기한 이른 순 정렬, 상태별 카운트). `data/booking-checklist.json` 단일 출처. 긴 메모·예약번호·권장(예약번호·PIN·취소정책 등)은 식별 요약 + 접기로 표시 — 짧은 값은 k/v 행, 44자 초과 값만 접어 모바일 셀 오버플로 방지
- `viz/archive.html` — 📦 의사결정 아카이브 (장마 확률·9 예산 시나리오·7 후보지 점수). 메인 페이지의 무게중심을 운영 정보로 유지하기 위해 분석·결정 자료는 이곳으로 분리
- `viz/breakfast.html` — 🍞 숙소 인근 조식 옵션 (아침 3회·숙소별 가게·영업시간·아침별 권장). `data/breakfast.json` 단일 출처. 일정 카드의 조식 슬롯에서 탭해 이동 (Vercel 화면은 외부 GitHub 링크 대신 사이트 내 페이지로 연결). 가게명은 모바일에서 탭하면 구글 지도가 열린다
- `viz/report.html`·`viz/itinerary-doc.html`·`viz/research.html`·`viz/transit-pass.html`·`viz/decision-kyoto.html` — 레포 마크다운 문서(최종 보고서·일정 문서·예약 리서치·교통패스 비교·교토 변경 결정)를 사이트 내 HTML로 렌더한 페이지. 가족 공유 시 GitHub 노출 없이 열람 (검사 J: `github.com` 링크 금지)
- `viz/kaneyo-review.html` — 교고쿠 카네요(京極かねよ) 일본어 방문기 한국어 번역 페이지. `docs/kaneyo-review-translation.md` 정본. 5/31 저녁 식당 후기 카드에서 탭 진입
- `viz/shinkyogoku-review.html` — 신쿄고쿠 상점가(新京極商店街) 안내·방문기 번역 페이지. `docs/shinkyogoku-review-translation.md` 정본. 5/31 20:00 야경 산책 카드에서 탭 진입
- `viz/decision-log.html` — 결정 일지 인덱스 (`docs/decision-log/*.md` 최신순 제목 목록, 교토 변경 결정만 링크)
- `assets/og-*.svg` — 6장의 OG/Twitter 카드 이미지 (1200×630). 카톡·Slack·X 공유 시 페이지별 썸네일·제목·설명 노출
- `sw.js`·`manifest.json`·`assets/icon.svg` — **오프라인(PWA) 산출물**. 서비스 워커가 전 페이지·로컬 자산을 사전 캐시해 **비행기 모드에서도 모든 페이지가 다시 열린다**(HTTPS 한 번 방문 후). PWA 매니페스트로 홈 화면 추가(앱 모드) 가능. 근거: `docs/decision-log/2026-05-31-offline-service-worker.md`
- `assets/place-images/`(커밋) + `data/local-image-map.json` — **외부 일정 이미지 자가호스팅**. `scripts/fetch_assets.py`가 위키미디어·네이버·타베로그 이미지를 referer 없이 내려받아 로컬 저장 → 빌드 시 외부 URL을 로컬 경로로 치환 → **오프라인에서 장소 사진·블로그 썸네일까지 표시**. 이미지 추가/교체 시 `uv run python scripts/fetch_assets.py` 재실행 후 재커밋(`--check`로 누락 감시). 근거: `docs/decision-log/2026-05-31-02-offline-image-selfhosting.md`
- **HTML 13개·SVG 6장 모두 `scripts/build_index.py` 빌드 산출물 — 직접 편집 금지**. **레포에 커밋하지 않는다(`.gitignore`)** — 배포(CD)와 소스를 분리해 PR 머지 충돌을 줄인다. 클론 직후 로컬에서 보려면 `uv run python scripts/build_index.py`를 1회 실행(`markdown` 의존 — uv가 자동 설치). 실제 배포는 Vercel이 매번 빌드(`buildCommand`가 `uv run`으로 lockfile에서 markdown 설치), CI도 검증 전에 빌드한다(재현성·콘텐츠 검사는 `tests/test_build_index.py`)
- 각 섹션 위 `<!-- SYNC: ... -->` 주석이 데이터 출처를 명시. CI(`scripts/validate.py`)가 경로 유효성과 §N 절 번호를 검증

### 2. 발권·예약 갱신

- `data/booking-checklist.json`의 항목별 `status`·`reference`(예약번호)·`confirmed_at`(확정일) 갱신
- 확정 금액은 `data/cost-options.json`에 반영 — `researched_market_rate` 라벨을 `confirmed_booking`으로 승격하고 `source`에 예약 사이트·확정일 기록
- 변경 사유는 `docs/decision-log/`에 새 파일 추가 (`YYYY-MM-DD-slug.md`)
- 점검: `uv run python scripts/build_index.py` (산출물 생성) + `uv run python -m unittest discover tests` + `uv run python scripts/validate.py`

### 3. 일정 갱신

- `data/itinerary.json`의 해당 day(`days[*]`)에 시간대·동선·메모 갱신
- 식사 항목은 `food_quality`(타베로그·구글·미쉐린 등 평점 + `source`·`data_quality`)로 맛집 근거 명시 — 추측 금지, 출처 없으면 머지 차단(검사 H)
- 장소명 한자 병기는 `data/itinerary.json`의 `places` 레지스트리가 단일 출처. 산문 필드에서 `{{place_id}}`로 참조하면 빌드 시 `ko(ja)`로 확장된다(신규 장소는 `places`에 1줄 추가). 참조·병기 없는 생 장소명은 검사 K가 머지 차단 — 병기 드리프트 방지
- `docs/kyoto-itinerary-may31-jun3-2026.md`(사람용 사본) 함께 갱신
- `uv run python scripts/build_index.py` 재빌드 → `viz/itinerary.html`·`viz/itinerary-table.html`·`index.html` 재생성

### 4. 현지 운영 (예정)

- 출국 전·현지·귀국 체크리스트, 한국어 가능 병원·영사관·교통 패스 등은 별도 산출물로 추가 예정 (`docs/checklist.md`·`docs/local-info.md` — 별도 PR)

### 5. 결정 기록 (모든 변경 공통)

- `docs/decision-log/` 디렉토리에 **새 파일** 추가 (`YYYY-MM-DD-slug.md`). 기존 파일은 편집하지 않음
- 컨벤션: `docs/decision-log/README.md`

### 6. 검증 (CI)

- `uv run python scripts/build_index.py` — 산출물(13 HTML + 6 OG SVG)은 gitignore이므로 검증 전에 빌드(빌드 무오류 자체가 가드). 재현성(idempotent)·콘텐츠 검사는 단위 테스트 `tests/test_build_index.py`가 담당. 로컬 재현성 확인은 `uv run python scripts/build_index.py --check`(drift 시 exit 1)
- `uv run python -m unittest discover tests` — 단위 테스트 (validate·build_index·design_tokens·score·budget)
- `uv run python scripts/validate.py` — 가격 필드 무결성(source·data_quality), 30/60일 묵은 가격 경고/실패, SYNC 주석 경로·절 번호 검증, `docs/weather.md`↔`data/weather.json`, `docs/flights.md`↔`data/flights.json`, `DESIGN.md`↔`data/design-tokens.json` 동기화 검증, Vercel 산출물 GitHub 링크 금지(검사 J — `index.html`·`viz/*.html`에 `github.com` 없음), 장소명 병기 무결성(검사 K — `places` 미정의 참조·생 장소명 무병기 차단)
- `.github/workflows/validate.yml`이 PR마다 위를 실행 (`uv sync --locked` 선행, `astral-sh/setup-uv`)

### 7. 시각 디자인 출처

- `DESIGN.md` — 시각 디자인 컨벤션 (`voltagent/awesome-design-md` 9섹션). Quiet Ledger 테마: paper-white + slate-indigo accent. AI 에이전트가 UI 변경 작업 시 본 파일을 1차 참조
- `data/design-tokens.json` — 색·타이포·간격·반경 단일 출처. `scripts/build_index.py`의 `render_css(tokens)`가 7개 산출물(`index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/lodging.html`·`viz/checklist.html`·`viz/archive.html`·`viz/breakfast.html`)의 인라인 CSS를 공통 생성
- 동기화 게이트: `scripts/validate.py` (H)가 DESIGN.md ↔ tokens의 drift를 PR 단계에서 차단

## 아카이브 (참조용)

> 2026-05-12에 종료된 정량 의사결정의 입력·산출물. 다음 여행이나 시기 변경 시 재참조 가능하도록 보존.

- `data/decision.json` — MCDA criteria·candidates·scores (입력)
- `data/weather.json` — 후보지×시기 기후 + 긴키 매우(梅雨) 평년·실적 + 교토 5/31~6/3 일별 강수 평년
- `data/flights.json` — 후보지×출발지 항공권 시세 스냅샷
- `docs/candidates.md` — 후보지 상세 비교
- `docs/weather.md` — 시기별 쾌적도 순위, `seasonality`/`physical_burden` 점수 제안 + §5 교토 5/31~6/3 장마 정량 분석
- `docs/flights.md` — 4인 총액 비교, GMP 가용성
- `docs/transit-pass-jr-kansai-2026.md` — JR 간사이 에어리어 패스 1/2/3/4일권 비교·권장 (예약 탭 `transit_pass` 근거)
- `docs/breakfast-near-lodging.md` — 숙소(시오·카덴쇼) 인근 조식 옵션 사람용 사본 (단일 출처는 `data/breakfast.json` → `viz/breakfast.html`)
- `docs/booking-research-2026-05-24.md` — 미정 예약 4항목(여행자보험·하루카 발권·eSIM·환전/트래블카드) 실시간 리서치·권장 발권 채널 (예약 탭 미정 항목 근거)
- `docs/icoca-iphone-setup.md` — ICOCA 아이폰(Apple Wallet) 셋업 가이드 (4인 사전 요건·등록 단계·충전·트러블슈팅·5/30 체크리스트)
- `docs/soyeon-maps-list.md` — 소연 구글맵 저장 목록 41개 장소 (카페·식사·명소·쇼핑 카테고리별 정리, 일정 참고용)
- `docs/saihoji-reservation-2026-06.md` — 사이호지(苔寺) 참배 예약 가능성 리서치 (예약 방법·7일 전 선착순·참배료·사경 면제·시부모 적합성·6월 이끼)
- `docs/screenshots/` — 리서치 근거 스크린샷 (예: `airalo-japan-2026-05-26.png` — eSIM 실가격·핫스팟 정책 1차 출처)
- `reports/final-report.md` — 최종 권고 (교토·5/31~6/3·4인)
- `scripts/score.py`·`scripts/budget.py` — 회귀 가드용

> 평가 기준(cost·schedule_fit·physical_burden·experience·family_fit·medical_access·seasonality·가중치)과 후보지 목록(도쿄·오사카·교토·삿포로·오키나와·후쿠오카·고베)의 상세는 `data/decision.json` + `docs/candidates.md`.

## 디렉토리

```
DESIGN.md    # 시각 디자인 컨벤션 (awesome-design-md 9섹션, Quiet Ledger)
vercel.json  # Vercel 배포 설정 (buildCommand로 배포 시점 빌드)
data/        # itinerary·booking-checklist·cost-options·design-tokens (실행 단일 출처) + decision·weather·flights (아카이브)
docs/        # 일정·후보·날씨·항공 분석, 의사결정 일지(decision-log/)
viz/         # itinerary·itinerary-table·lodging·checklist·archive·breakfast + 문서 렌더(report·itinerary-doc·research·transit-pass·decision-kyoto·decision-log) (build_index.py 산출물 — gitignore)
assets/      # og-*.svg (OG 카드 6장) + icon.svg (PWA 앱 아이콘) + lodging/·place-images/ (사진, 커밋) — og-*.svg·icon.svg는 build_index.py 산출물(gitignore)
sw.js + manifest.json  # 오프라인(PWA) 산출물 — 서비스 워커 사전 캐시 + 웹 앱 매니페스트 (build_index.py 산출물 — gitignore)
pyproject.toml + uv.lock  # 빌드 의존성 (markdown==3.7 — 문서 렌더용, uv virtual project)
scripts/     # build_index·validate·score·budget·list_sources·fetch_assets·render-pdf
tests/       # unittest (validate·build_index·design_tokens·score·budget)
reports/     # 최종 보고서 (아카이브)
index.html   # 운영 페이지 — 요약·일자별 일정 (build_index.py 산출물 — gitignore)
```

## 환경 요구

- [uv](https://docs.astral.sh/uv/) (Python·의존성 관리). `uv sync` → `uv run python ...`
- Python 3.11+ (uv가 관리)
- pandoc 또는 Chrome (PDF 변환, 선택)
- 브라우저 (`index.html`·`viz/*.html` 더블클릭)

## 변경 규칙 (모든 PR 공통)

이 레포는 **누적되는 여행 실행 자산**을 목표로 하므로, 어떤 변경이든 다음 메타 문서를 함께 갱신한다.

| 갱신 대상 | 무엇을 적나 |
|---|---|
| `docs/decision-log/YYYY-MM-DD-slug.md` (새 파일) | 날짜·주제·산출물·합의/보류/다음 단계 |
| `README.md` (이 파일) | 새 산출물의 사용법·디렉토리 1줄 이상 |
| `CLAUDE.md` | 디렉토리 트리·작업 규칙·데이터 동기화 규칙 |

데이터 산출물(예: `data/weather.json`)을 추가할 땐 출처·갱신 주기·점수 기준도 `docs/`에 함께 기록한다.
상세 규칙은 `CLAUDE.md` 의 **메타 문서화 규칙** 섹션 참조.
