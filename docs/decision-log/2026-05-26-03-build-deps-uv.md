# 2026-05-26 — 빌드 의존성 관리를 pyproject.toml + uv로 전환

## Status

Accepted (같은 날 `2026-05-26-02-vercel-docs-as-html-pages.md`에서 도입한 `requirements.txt` 방식을 Superseded)

## Context (왜)

- 직전 결정(`2026-05-26-02-...`)으로 문서 렌더용 첫 외부 의존성(`Markdown==3.7`)을 `requirements.txt` + `pip install`로 도입했다.
- 사용자 질의: "pip이 업계 권장인가." 사실관계 — pip + requirements.txt는 파이썬 기본·보편 방식이고 deprecated는 아니지만, 현재 표준의 방향은 프로젝트 메타데이터를 `pyproject.toml`(PEP 621)로 두고 재현성은 락파일 도구(uv·Poetry·pip-tools)로 고정하는 쪽이다. 특히 uv(Astral)가 사실상 표준처럼 빠르게 자리잡는 중.
- 본 레포의 핵심 제약은 `build_index.py --check`(커밋된 HTML vs 빌드 산출물 비교)의 **결정성**이다. requirements.txt의 `==3.7` 핀도 작동하지만 해시·전이 의존성까지 고정하지는 않는다. (현 의존성 `markdown`은 런타임 전이 의존성이 없어 차이는 작지만, 향후 확장 대비.)
- 사용자 지시: "pyproject.toml + uv."

## Decision (무엇)

- 빌드 의존성 관리를 `pyproject.toml` + `uv.lock`(uv)로 전환한다.
  - `pyproject.toml`: `[project]` 메타 + `dependencies = ["markdown==3.7"]`. 설치 가능한 패키지가 아니라 스크립트 모음이므로 `[tool.uv] package = false`(virtual project)로 둬 uv가 루트를 빌드하지 않고 의존성만 `.venv`로 관리.
  - `uv.lock`: `uv lock`으로 생성·커밋. markdown 정확 버전·해시 고정.
  - `requirements.txt` 제거. `.gitignore`에 `.venv/` 추가(`uv.lock`은 커밋).
- 로컬·CI 실행을 `uv run python ...`(자동 동기화) / `uv sync --locked`로 통일.
- CI(`.github/workflows/validate.yml`): `actions/setup-python` + `pip install` → `astral-sh/setup-uv@v8`(`python-version: 3.11`, `enable-cache: true`) + `uv sync --locked` + 각 스텝 `uv run python ...`. `--locked`로 lock↔pyproject 불일치 시 실패(재현성 가드).
- 대안 — requirements.txt 유지: 보편적이고 충분하나, 사용자가 명시적으로 uv 전환을 지시. 락파일 기반 재현성·향후 의존성 확장성에서 우월.
- 대안 — Poetry/pip-tools: uv가 설치 속도·단일 도구(파이썬 관리 포함)·최신 채택도에서 유리.

## Consequences (그래서)

- 긍정: 의존성·파이썬 버전·해시가 `uv.lock`으로 완전 고정 → `--check` 결정성 강화. 메타데이터가 표준 `pyproject.toml`에 모임. CI 캐시로 설치 빨라짐.
- 부정·트레이드오프: 로컬·CI에 uv 설치가 전제됨(이전엔 파이썬 기본 pip만으로 충분). 기여자가 `python scripts/...` 대신 `uv run python scripts/...`를 써야 함(직접 .venv 활성화도 가능).
- 빌드 산출물 영향 없음: markdown 버전이 동일(3.7)하므로 렌더 HTML 무변경 — `--check` drift 없음.
- 후속: 의존성 추가·갱신 시 `uv add`/`uv lock` → 빌드 재실행 → 일지화. 의존성 버전 변경은 커밋된 HTML과 동기화 필수.
- 영향 받은 파일: 신규 `pyproject.toml`·`uv.lock`, 삭제 `requirements.txt`, 수정 `.gitignore`·`.github/workflows/validate.yml`·`CLAUDE.md`·`README.md`.

## Test plan

- [x] `uv lock` → `uv sync --locked` (virtual project, markdown==3.7 설치)
- [x] `uv run python scripts/build_index.py --check` — drift 없음 (HTML 무변경)
- [x] `uv run python scripts/validate.py` — 0 errors
- [x] `uv run python -m unittest discover tests` — 전부 통과
- [ ] CI에서 `astral-sh/setup-uv@v8` + `uv sync --locked` 그린 확인
