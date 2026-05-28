# 2026-05-27 — 빌드 산출물(CD)을 소스에서 분리해 PR 머지 충돌 제거

## Status

Accepted

## Context (왜)

- `scripts/build_index.py`가 생성하는 12개 산출물(`index.html`, `viz/*.html` 5개, `assets/og-*.svg` 6개)이 레포에 **커밋**되어 있었고, Vercel은 `vercel.json` 없이 커밋된 정적 파일을 그대로 서빙했다.
- CI 게이트 `build_index.py --check`가 커밋된 산출물과 소스의 drift를 차단하므로, `data/*.json` 한 줄만 바꿔도 합계 2000줄+의 기계 생성 HTML 6개를 재생성·커밋해야 했다.
- 그 결과 서로 다른 날짜·영역을 건드리는 PR들도 거대한 기계 생성 diff가 겹쳐 머지 충돌이 잦았다. 실증: PR #38("archive.html drift 충돌 해소"), 열린 PR들이 본문에 "⚠️ 충돌 가능 — 머지 순서 지정"을 명시.
- 충돌의 구조적 증폭 원인은 **배포 산출물(CD)이 소스와 분리되지 않은 것**이다. 표준 정적 사이트 관행(빌드 산출물 비커밋, 배포 시점 빌드)을 따르지 않았다.
- 대안: `.gitattributes` merge driver는 로컬 `.git/config` 의존이라 GitHub 웹 머지에 적용되지 않아 기각. GitHub Actions + Vercel CLI 배포는 VERCEL_TOKEN 시크릿·배포 워크플로우가 필요하고 PR preview 자동검증을 잃어 기각.

## Decision (무엇)

- 12개 산출물을 `git rm --cached`로 추적 해제하고 `.gitignore`에 `/index.html`, `/viz/*.html`, `/assets/og-*.svg` 추가.
- `vercel.json` 신설 — `buildCommand: "python3 scripts/build_index.py"`, `outputDirectory: "."`. Vercel이 매 배포 시점에 산출물을 빌드해 서빙. PR마다 생성되는 preview 배포가 buildCommand·python3 가용성을 머지 전에 검증.
- CI(`.github/workflows/validate.yml`)는 검증 단계 **앞에** `python scripts/build_index.py`를 실행해 산출물을 생성(빌드 무오류 자체가 가드). 커밋된 산출물이 없으므로 무의미해진 `build_index.py --check` 단계는 삭제. 재현성(idempotent)·drift·콘텐츠 검사는 기존 `tests/test_build_index.py`(unittest)가 계속 담당.
- `tests/test_validate.py`의 `ProductionDataTests`에 `setUpClass`를 추가해 `index.html` 부재 시 빌드 — 격리 실행에서도 검사 D가 자기완결적으로 통과.

## Consequences (그래서)

- 긍정: PR은 소스(`data/*.json`·`scripts/`·`docs/`)만 건드려 diff가 작아지고, 거대한 기계 생성 HTML/SVG 충돌이 사라진다. 머지 순서 조율 부담 감소.
- 부정·트레이드오프: 클론 직후 로컬에서 페이지를 보려면 `python scripts/build_index.py`를 1회 실행해야 한다(문서화함). Vercel 빌드가 python3에 의존(빌드 이미지 기본 제공). preview 빌드 실패 시 fallback은 산출물 재커밋 또는 Actions 빌드 전환.
- 남는 충돌: 두 PR이 `data/itinerary.json` 같은 단일 소스 동일 영역을 편집하면 충돌은 남으나, 작고 의미 단위라 해소가 쉽다.
- 영향 받은 파일·데이터: `.gitignore`, `vercel.json`(신규), `.github/workflows/validate.yml`, `tests/test_validate.py`, 추적 해제 12개 산출물, 문서 `CLAUDE.md`·`README.md`·`DESIGN.md`.

## Test plan

- [x] `python scripts/build_index.py` — 12개 산출물 무오류 생성
- [x] `python scripts/validate.py` — 0 errors (검사 D가 빌드된 index.html 발견)
- [x] `python -m unittest discover -s tests` — 104 tests OK
- [x] 격리 실행 `python -m unittest tests.test_validate`(산출물 삭제 후) — setUpClass 자기빌드로 통과
- [x] `git ls-files | grep -E '\.(html|svg)$'` — 매치 없음(추적 해제 확인), 산출물은 ignored
- [ ] PR preview 배포 — Vercel preview URL에서 메인·일정·체크리스트·숙박·아카이브 + OG 이미지 렌더 확인(머지 전)
