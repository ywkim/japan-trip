# 2026-05-14 — DESIGN.md(awesome-design-md) 도입 + 디자인 토큰 단일 출처화

- 합의:
  - `voltagent/awesome-design-md` 컨벤션 채택. `/DESIGN.md`를 시각 디자인 9섹션 단일 출처로 신설.
  - 시각 방향 **"Quiet Ledger"** 채택: paper-white 배경(`#F7F6F2`) + slate-indigo accent(`#3E5C76`).
    빨강 accent(`#d33`/`#ff6464`) 폐기. status 3색(`ok`/`warn`/`danger`)은 의미적 용도만 유지.
  - 디자인 토큰을 `data/design-tokens.json`으로 분리 → `scripts/build_index.py`가 `index.html` 인라인 CSS와
    `viz/dashboard.html`의 `/* TOKENS:START */`~`/* TOKENS:END */` 블록에 주입. 인라인 hex 직접 입력 금지.
  - `scripts/validate.py` 검사 (G) 추가: DESIGN.md ↔ design-tokens.json ↔ dashboard TOKENS 블록의 drift를 PR 단계에서 차단.
- 산출물:
  - `DESIGN.md` (9섹션: Visual Theme · Color · Typography · Components · Layout · Depth · Do/Don't · Responsive · Agent Prompt Guide)
  - `data/design-tokens.json` (theme_name `Quiet Ledger`, version `1.0.0`, light/dark 13색 × 2, 타이포·간격·반경·elevation·breakpoint)
  - `scripts/build_index.py` 리팩터: 하드코드 `<style>` 블록 → `_render_index_css(tokens)`; `render_dashboard(tokens)` 신설로 dashboard 토큰 블록 재생성; 인라인 `#2a7`/`#c80`/`#c33` → `var(--ok)`/`var(--warn)`/`var(--danger)`
  - `viz/dashboard.html`: `:root` + dark `:root`를 `/* TOKENS:START */`~`/* TOKENS:END */` 센티넬로 감쌈
  - `scripts/validate.py`: `check_design_sync` (G) 등록 — hex 양방향, theme_name·version, dashboard 센티넬 검증
  - `tests/test_design_tokens.py` (스키마·hex 포맷·레거시 회귀)
  - `tests/test_validate.py` `DesignSyncTests` 6개 (in-sync pass, MD-only hex fail, token-only hex fail, sentinel missing, dashboard unknown hex, theme_name drift)
  - `tests/test_build_index.py` `test_css_uses_token_palette`·`test_dashboard_tokens_block_in_sync`
  - `CLAUDE.md`·`README.md` 메타 문서: 디렉토리 트리, 단일 출처 목록, CI 게이트 표, "디자인 워크플로우" 신설
- 핵심 관찰:
  1. 도입 전 `index.html` CSS는 `build_index.py` 문자열에 하드코드, `viz/dashboard.html`은 손으로 같은 팔레트 복붙. 한쪽 수정 시 drift 위험.
  2. 토큰화 후 `python scripts/build_index.py` 한 번이면 두 surface가 동시 갱신. `--check` 모드가 두 파일 모두 검증.
  3. 검사 G의 양방향 hex 비교(MD↔JSON)는 "토큰만 추가하고 문서를 잊는" 케이스와 "문서만 고치고 토큰을 잊는" 케이스 둘 다 차단. theme_name·version 검증으로 버전 번호 누락도 방지.
  4. 빨강 accent 폐기는 단순 미감 변경이 아님: 빨강이 본문 강조에 쓰이던 위치가 모두 slate-indigo로 교체되면서 danger(`#9A3B3B`)의 의미적 신호가 비로소 또렷해짐. status 색은 의미 전용으로만.
  5. production 데이터에서 검사 G 통과 (44개 테스트 그린, validate exit 0, build_index --check OK).
- 다음 단계:
  - 토큰 활용 추가: 현재 `spacing_rem`·`radius_px`는 정의만 되어 있고 CSS에는 일부만 인젝션. 후속 PR에서 CSS 변수(`--space-md`, `--radius-md` 등)로 확장.
  - status 색은 의미 전용이므로 `var(--ok/--warn/--danger)` 사용처 외에 텍스트로 노출되는 곳을 주기 점검 (예: 신규 카드 추가 시).

## 2026-05-16 갱신 (PR #24와의 충돌 해소)

main에 PR #24(빌드 파이프라인 일원화)가 먼저 머지되면서 본 PR 구조가 크게 바뀌었다. `viz/dashboard.html`이 삭제되고 `viz/itinerary.html`·`viz/checklist.html` 두 화면이 신설, `scripts/build_index.py`는 3개 산출물을 공통 `CSS` 상수와 `html_doc()` 헬퍼로 생성하는 구조로 리팩터링됨.

- 합의: 본 PR의 token-injection을 **3개 산출물 공통 경로**(공유 `CSS` 상수)에 적용. 결과적으로 더 깨끗함 — 한 번의 `render_css(tokens)`가 3개 화면을 동시 갱신.
- 산출물 차이:
  - `viz/dashboard.html`·관련 sentinel 로직·dashboard sentinel 테스트 전부 삭제.
  - `CSS` 상수 → `render_css(tokens)` 함수.
  - `html_doc(title, body)` → `html_doc(title, body, tokens)` (3개 호출처 모두 갱신).
  - `card_budget`·`card_checklist`(index)·`build_checklist`(viz)의 status 색 `#2a7/#c80/#c33` → `var(--ok/--warn/--danger)`. `card_tsuyu`의 `#c80` 인라인도 `var(--warn)`로.
  - `scripts/validate.py` G의 dashboard sentinel 검사 제거 (파일이 없으므로). hex 양방향 + theme_name/version 검사만 유지.
  - `tests/test_validate.py` `DesignSyncTests` 6개 → 5개 (dashboard 케이스 2개 제거, `test_version_drift_fails` 1개 추가).
  - `tests/test_build_index.py`에 `test_all_outputs_use_token_palette` (3개 산출물 일괄 회귀) 추가.
- 검증: 44 tests pass, validate 0 errors, build_index --check OK.
- 메타: README.md·CLAUDE.md의 dashboard 언급을 모두 "3개 산출물" 표현으로 교체.
