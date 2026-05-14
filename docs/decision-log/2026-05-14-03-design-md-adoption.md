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
  - `viz/dashboard.html`을 `index.html`처럼 전체 빌드 대상으로 승격 (현재는 토큰 블록만 generated, 나머지는 수기). 별 PR.
  - status 색은 의미 전용이므로 `var(--ok/--warn/--danger)` 사용처 외에 텍스트로 노출되는 곳을 주기 점검 (예: 신규 카드 추가 시).
