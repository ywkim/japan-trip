# 2026-05-12 — meta → validate 리네이밍 + TDD 도입

- 트리거: 직전 PR에서 `check_meta.py`·`meta-check.yml` 네이밍이 모호하다는 지적 + 테스트 없이 작성됐다는 TDD 미준수 지적.
- 합의:
  - `meta`는 데이터 검증·SYNC 무결성·빌드 drift 셋이 섞여 있어 의미가 흐림 → `validate`로 통일.
  - CLAUDE.md "메타 문서화 규칙"(decision-log/README/CLAUDE 갱신)은 다른 개념이라 유지.
  - 스크립트·빌드 로직 변경 시 테스트 먼저 작성하는 TDD 원칙을 본 PR부터 강제.
- 산출물:
  - 리네이밍: `scripts/check_meta.py` → `scripts/validate.py`, `.github/workflows/meta-check.yml` → `.github/workflows/validate.yml`
  - `scripts/validate.py` — `run(base, today)` 함수형으로 리팩토링, `--base`·`--today` 플래그로 테스트 격리 가능
  - `tests/__init__.py`, `tests/test_validate.py`(12 케이스), `tests/test_build_index.py`(5 케이스), `tests/test_scripts_json.py`(7 케이스) — 총 24 테스트
  - workflow에 `python -m unittest discover tests` 추가
  - CLAUDE.md에 "테스트 작성 규칙 (TDD)" 섹션 신설
- 핵심 관찰:
  - 24/24 테스트 통과 (production 데이터 회귀 가드 포함)
  - `validate.py` 리팩토링 중 모듈 전역 상수(`BASE`, `TODAY`) 제거 → tempfile fixture 기반 격리 테스트 가능. 부수효과로 production 코드 품질도 개선
  - `test_check_detects_drift`: index.html 직접 편집 시 `--check` 실패를 보장 (회귀 가드)
  - `test_kyoto_full_weight`: 교토만 used_weight 1.0인 사실을 테스트로 박제 — 다른 후보 점수 추가 시 의도적 갱신 필요
- 다음 단계: 다른 후보 점수 입력 PR이 들어오면 `test_kyoto_full_weight`를 더 일반적인 형태로 갱신.
