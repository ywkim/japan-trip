# 2026-05-27 — Vercel buildCommand를 `uv run`으로 (markdown 의존 + PEP 668)

## Status

Accepted (보완: `2026-05-27-cd-artifact-separation.md`의 `buildCommand: python3 scripts/build_index.py` + `2026-05-26-04-build-deps-uv.md`의 markdown 의존 도입이 Vercel에서 충돌한 지점 해소)

## Context (왜)

- #54(CD 분리)가 `vercel.json`에 `buildCommand: "python3 scripts/build_index.py"`를 도입했다. 당시 `build_index.py`는 의존성이 없어 시스템 python3로 충분했다.
- 본 PR이 문서 렌더(DOC_PAGES)를 위해 `markdown` 의존을 추가하면서 Vercel 빌드가 markdown을 필요로 하게 됐다. 1차 시도로 `python3 -m pip install markdown==3.7 && python3 scripts/build_index.py`로 바꿨으나 Vercel 배포가 실패했다.
- Vercel 빌드 로그(commit cf0e7a3): `error: externally-managed-environment` / "This Python installation is **managed by uv** and should not be modified" (PEP 668). 즉 **Vercel 빌드 이미지의 python3는 uv가 관리**하며 시스템 pip 설치가 차단된다.
- GitHub Actions(`validate`)는 통과했고 실패는 Vercel CD에 한정. 빌드 로그는 GitHub MCP로 접근 불가라 사용자가 로그를 공유해 원인을 특정했다.

## Decision (무엇)

- `vercel.json`의 `buildCommand`를 `uv run python scripts/build_index.py`로 변경한다.
  - Vercel 빌드 이미지에 이미 `uv`가 존재(로그가 입증)하므로, `uv run`이 `pyproject.toml`+`uv.lock`에서 venv를 만들어 `markdown==3.7`을 설치한 뒤 빌드한다. 시스템 python을 건드리지 않아 PEP 668 우회.
  - 로컬·CI·Vercel 모두 `uv run` 경로로 통일 — markdown 버전이 lockfile로 동일하게 고정.
- 기각한 대안: `--break-system-packages`(시스템 python 오염 위험·비권장), `pip install --user`(externally-managed에서 비신뢰), 산출물 재커밋(#54 CD 분리 취지 위배).

## Consequences (그래서)

- 긍정: Vercel 빌드가 lockfile 기반으로 재현성 있게 markdown을 설치. 3개 환경(로컬/CI/Vercel) 빌드 경로 일치.
- 부정·트레이드오프: Vercel 빌드가 빌드 이미지의 `uv` 가용성에 의존(현재 제공됨). 향후 Vercel이 uv를 빼면 buildCommand에 uv 설치 스텝(`curl … astral.sh/uv`) 추가 필요.
- 영향 파일: `vercel.json`, `CLAUDE.md`, `README.md`.
