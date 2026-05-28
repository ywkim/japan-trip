# 2026-05-26 — 외부 참조 문서를 사이트 내 HTML 페이지로 렌더 (GitHub 링크 대체)

## Status

Accepted (2026-05-26-vercel-no-github-links.md 보완 — GitHub 링크 금지는 유지, 링크 대상만 사이트 내부로 복원)

## Context (왜)

- 같은 날 앞선 결정(`2026-05-26-vercel-no-github-links.md`)으로 Vercel 산출물(`index.html` + `viz/*.html`)에서 GitHub 링크를 모두 제거하고, `github.com` 문자열을 차단하는 CI 검사 J를 도입했다. 근거: 가족(시부모 포함) 공유 페이지에서 레포(소스·미렌더 `.md`)로 빠져나가는 노출을 막는다.
- 부작용: 제거된 링크가 가리키던 문서(최종 보고서·일정 마크다운·예약 리서치·교통패스 비교·교토 결정 일지)를 사이트 안에서 더 이상 열람할 수 없게 됐다. 푸터·아카이브·체크리스트의 "상세/출처"가 평문 레포 경로로만 남아 클릭 동선이 끊겼다.
- 사용자 지시: "제거하지 말고 HTML 페이지로." 외부 문서를 없애지 말고 레포 마크다운을 사이트 내부 HTML로 렌더해 그 페이지로 연결하라.
- 사용자 확인 사항: ① 범위 = 실제로 참조되는 5개 문서 + 결정 일지 인덱스(텍스트), ② 변환 = stdlib 미니 변환기 대신 검증된 마크다운 의존성 추가.
- 제약: 레포는 그동안 의존성 0(stdlib only). `build_index.py --check`(CI drift 가드)가 결정적이어야 하므로 변환기 버전을 고정해야 한다.

## Decision (무엇)

- `scripts/build_index.py`에 `DOC_PAGES` 레지스트리를 추가하고, Python-Markdown(`Markdown==3.7`, `tables`·`sane_lists` 확장)으로 5개 레포 문서를 사이트 내 HTML 페이지로 렌더한다.
  - `reports/final-report.md` → `viz/report.html`
  - `docs/kyoto-itinerary-may31-jun3-2026.md` → `viz/itinerary-doc.html`
  - `docs/booking-research-2026-05-24.md` → `viz/research.html`
  - `docs/transit-pass-jr-kansai-2026.md` → `viz/transit-pass.html`
  - `docs/decision-log/2026-05-11-may31-jun3-kyoto-update.md` → `viz/decision-kyoto.html`
- `viz/decision-log.html`(결정 일지 인덱스)을 추가한다. `docs/decision-log/*.md`를 최신순 텍스트 목록(날짜 + 첫 제목)으로 렌더하되, 교토 변경 결정만 `decision-kyoto.html`로 연결하고 나머지는 제목만 표기(본문 미게시).
- 제거됐던 링크를 사이트 내 페이지로 재배선: index 푸터→`report.html`, archive 푸터→`report.html`·`decision-log.html`, archive 점수 카드→`decision-kyoto.html`, itinerary→`itinerary-doc.html`.
- `data/booking-checklist.json`의 4개 항목에 `link` 복원. `link.url`에 레포 마크다운 경로를 넣으면 `DOC_SOURCE_TO_OUT`가 사이트 내 페이지(`research.html`·`transit-pass.html`)로 치환.
- 검사 J(`scripts/validate.py`)를 고정 튜플 대신 `index.html` + `viz/*.html` glob 스캔으로 변경 — 신규 문서 페이지도 자동 포함.
- `requirements.txt` 신설 + CI에 `pip install -r requirements.txt` 단계 추가.
- 대안 — stdlib 미니 마크다운 변환기 자체 구현: 표·blockquote·중첩 리스트 엣지케이스 유지보수 부담이 커 기각. 검증된 라이브러리 + 버전 핀이 결정성·정확성에서 우월.
- 대안 — 모든 decision-log 63개를 개별 페이지로 렌더: 범위 과다(가족이 볼 필요 없는 내부 일지 다수). 인덱스 + 교토 결정 1개만 노출로 한정.

## Consequences (그래서)

- 긍정: 가족 공유 페이지에서 레포 노출 없이 핵심 문서를 열람 가능. GitHub 링크 금지(검사 J)는 유지·강화(glob으로 신규 페이지 자동 커버). 단일 출처는 여전히 레포 `.md`(원본이 정본, HTML은 빌드 산출물).
- 부정·트레이드오프: 레포에 첫 외부 의존성(Python-Markdown) 도입. 버전 핀과 커밋된 HTML이 일치해야 `--check` 통과 → CI도 동일 버전 설치 필요. 향후 렌더 대상 문서에 `github.com`이 들어가면 검사 J가 차단(현 5개 문서는 0건).
- Vercel 산출물이 HTML 6종 → 12종으로 증가(문서 5 + 결정 일지 인덱스 1).
- 후속: 다른 docs 문서를 추가로 노출하려면 `DOC_PAGES`에 1줄 등록 후 재빌드.
- 영향 받은 파일: `scripts/build_index.py`, `scripts/validate.py`, `data/booking-checklist.json`, `.github/workflows/validate.yml`, `requirements.txt`, `tests/test_build_index.py`, `tests/test_validate.py`, `CLAUDE.md`, `README.md`, 그리고 신규 `viz/report.html`·`viz/itinerary-doc.html`·`viz/research.html`·`viz/transit-pass.html`·`viz/decision-kyoto.html`·`viz/decision-log.html`(빌드 산출물).

## Test plan

- [x] `pip install -r requirements.txt` → `python scripts/build_index.py` → 12개 HTML + 6 SVG 생성
- [x] `grep -rn github.com index.html viz/*.html` → 매치 없음
- [x] `python scripts/validate.py` → 0 errors (검사 J가 12개 HTML glob 스캔)
- [x] `python scripts/build_index.py --check` → drift 없음
- [x] `python -m unittest discover -s tests` → 전부 통과 (문서 렌더·검사 J glob 테스트 포함)
- [ ] 브라우저로 `viz/report.html` 등 열어 표·제목·blockquote·뒤로가기 링크 확인
