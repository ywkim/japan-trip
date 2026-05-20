# 2026-05-19 — 수신자 관점 리뷰: 정체성 어긋남 일괄 수정

## 배경

`nihon-trip.vercel.app` 를 가족·시부모에게 카톡으로 공유했을 때 받는 사람이
보는 신호와 사이트의 실제 목적(이미 종료된 의사결정 결과를 운영하는 실행
페이지) 사이에 강한 어긋남이 관찰됨. 핵심 6가지:

1. 카톡·Slack에 URL만 떴을 때 썸네일·설명 없음 (OG/Twitter 메타 부재).
2. 메인 페이지 `<title>` 이 "일본 여행 최종 결정" — CLAUDE.md 의 "이제 실행·운영" 과 정면 충돌.
3. 메인의 `#tsuyu`·`#budget`(9 시나리오)·`#score`(7 후보지) 가 받는 사람에게 "아직 결정 중" 으로 읽힘.
4. `#score` 는 교토 6위로 보여 선택 정당성을 의심하게 만듦.
5. 상단 5 anchor + 하단 4 탭 = 9 라벨, "일정" 중복.
6. 푸터 텍스트가 `scripts/build_index.py 산출` 로 개발자 자료 인상.

## 합의 (사용자 결정 via AskUserQuestion)

- 범위: 리뷰 전체를 **1 개 PR** 로 (병렬 fan-out 안 함).
- 메인 title/H1: `교토 5/31~6/3 · 4인 가족 여행`.
- `og:image`: 페이지별 **6장 SVG** 를 `build_index.py` 가 자동 생성 (assets/og-*.svg).
- 분석/아카이브 섹션: 메인에서 제거 → `viz/archive.html` 로 이동.

## 산출물

### 새 파일

- `viz/archive.html` — 의사결정 아카이브 (장마 확률 · 9 예산 시나리오 · 7 후보지 점수)
- `assets/og-{home,itinerary,itinerary-table,lodging,checklist,archive}.svg` — 1200×630 OG 카드 6장
- `docs/decision-log/2026-05-19-recipient-perspective-fix.md` (본 일지)

### 수정 파일

- `scripts/build_index.py`
  - `html_doc(title, body, *, description, og_slug, page_path, extra_css)` 시그니처 확장
  - `og_meta()` 헬퍼 추가 — 페이지별 og:/twitter: 13개 메타 일괄 주입
  - `build_og_svg()` + `OG_CARDS` 테이블 — SVG 6장 자동 생성
  - 메인 페이지: `INDEX_HEAD` 재구성, `card_summary` 에서 종합 점수 줄 제거, `card_tsuyu`·`card_budget`·`card_score` 를 메인에서 제외
  - 신규 `build_archive()` — 아카이브 3 섹션 + "← 운영 페이지로" 링크
  - `card_score` 상단에 "교토는 1위가 아니지만 …" 사유 + decision-log 링크 1줄 추가
  - 푸터 정리: "scripts/build_index.py 산출" 같은 개발자 표현 제거
- `tests/test_build_index.py`
  - `test_all_sections_rendered` — 메인은 summary·itinerary만, archive에 tsuyu·budget·score
  - `test_index_title_is_operational`·`test_index_summary_has_no_score_line` 신설
  - `test_og_meta_present_on_all_pages`·`test_og_titles_are_unique_per_page`·`test_og_image_points_to_assets_svg`·`test_og_assets_generated`·`test_check_detects_drift_in_og_svg` 신설
  - `ALL_OUTPUTS = ALL_HTML_OUTPUTS + ALL_OG_SVGS` 로 분리
- `CLAUDE.md`·`README.md` — 디렉토리 트리에 `viz/archive.html`·`assets/og-*.svg` 추가, 메인 페이지 설명을 "운영 모드" 로 갱신

## 핵심 관찰

- 받는 사람의 1차 인지 경로는 **탭 제목 → 첫 화면 → 푸터**. 이 셋에 분석·결정 모드 단어가
  하나라도 있으면 "운영용 일정표" 라는 신호가 모두 무력화된다.
- OG 메타의 1차 수신자는 카카오톡·iMessage·Slack·X. 모두 SVG OG image 를 수용함. Facebook 일부 크롤러는 PNG/JPG 만 지원하지만 본 사이트 1차 수신자가 아니므로 PNG 변환은 후속 PR 로 미룸.
- 메인에서 `#score` 를 단순 제거하면 archive 에서 "교토 6위" 가 그대로 노출돼 다른 경로(공유 URL 의 anchor 등)로 진입하는 사람이 의심하게 된다. 따라서 archive 의 `#score` 카드 상단에 사유 + decision-log 링크 1줄을 명시.
- `_TABS` 는 4탭 유지. archive 페이지는 탭에 없는 "5번째 페이지" 로, 메인 nav·푸터·archive 자체의 "← 운영 페이지로" 링크로만 접근. 받는 사람의 무게중심을 운영 4탭에 묶어두기 위함.
- 빌드 산출물이 6 HTML + 6 SVG = 12개로 늘었지만 `--check` drift 가드는 그대로 동작.

## 검증

- `python scripts/build_index.py` → 12 산출물 생성 (HTML 6 + SVG 6)
- `python scripts/build_index.py --check` → exit 0
- `python -m unittest discover -s tests` → 59 tests pass
- `python scripts/validate.py` → 0 errors, 0 warnings
- 페이지별 og:title 유일성 검증 → 6 페이지 6 고유 title

## 한계 (후속 PR 후보)

- SVG OG image 가 Facebook OG 크롤러 일부에서 미지원 → PNG 변환 (Pillow 또는 외부 렌더).
- 메인 요약 카드의 "3M 캡 ₩392,522 초과" 표기 — "초과" 단어가 "예산 안 맞는 중" 인상 유발. 라벨 문구 재검토 PR.

## 다음 단계

- 머지 후 카카오톡에 URL 공유해 카드 미리보기·썸네일·설명 노출 실측.
- LinkedIn Post Inspector / opengraph.xyz 로 OG 파싱 검증 (선택).
