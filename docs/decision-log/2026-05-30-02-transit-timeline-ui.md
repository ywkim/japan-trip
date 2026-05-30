# 2026-05-30 — 이동 경로를 '역 타임라인' 컴포넌트로 재설계 (ONE LONG STRING 해소)

## Status

Accepted

## Context (왜)

- Work 4.1로 `arrive_from.steps`의 from/to가 `ko(ja)` 병기로 확장됐으나,
  `render_transit_line_steps()`가 이를 **한 줄짜리 문자열**
  ("니조역(二条駅) → 사가아라시야마역(嵯峨嵐山駅) (12분, 8.5km, ¥200)")로 이어 붙여
  모바일에서 좁은 화면을 넘치거나 폰트가 작아지는 ONE LONG STRING 문제가 남았다.
- 1차 시도(인라인 flexbox 여러 줄)는 ① 시각적으로 "그냥 줄바꿈"이라 인상이 같고
  ("동일한데?" 피드백) ② **운영사 브랜드색(`#E94B3C` 빨강·`#0066CC` 파랑·`#003DA5`
  네이비)과 `#999`·`#666`·`#FF6B6B`·`#d9534f`·`#ddd`를 인라인 스타일로 박아**
  `DESIGN.md` §1·§7의 핵심 규칙("빨강 accent 폐기 → slate-indigo 단일 accent,
  빨강은 danger만", "인라인 hex 금지")을 정면으로 위반했다.
- 즉 ONE LONG STRING은 "줄바꿈"이 아니라 **정보 구조를 가진 컴포넌트 부재**가 원인이며,
  해법은 디자인 토큰을 따르는 전용 시각 컴포넌트여야 한다.

## Decision (무엇)

- 이동 경로 상세를 **세로 레일 타임라인 컴포넌트(`.tl*`)**로 재설계한다.
  - 각 `step.from`을 레일 위 도트 노드로(첫 step=출발, 이후 step.from=환승점),
    마지막 `step.to`를 도착 노드로 렌더 → 노드 사이를 `.tl-line` 레일이 잇는다.
  - 환승점은 `.tl-dot.transfer`(warn 색 도트) + `.tl-tag`('환승' pill)로 강조.
    과거 본문 가운데 삽입하던 "↓ 환승 ↓" 텍스트 폐기.
  - 운영사·노선은 **색이 아니라 아이콘 + `.tl-mode` pill**(시버스 11번 / JR 산인본선 /
    공항특급)로 구분. 분·거리·요금은 `.tl-meta`(tabular-nums)로 도트 옆에 첨부.
  - 역 정보가 없는 leg(도보 등)는 `.tl-simple` 간결 pill 줄로 폴백.
  - `advisory`는 `.tl-advisory`(warn 좌측 보더 박스)로 노출.
- 접힘 요약은 늘어지지 않게 **모드 동사 + 총 소요시간(+환승 횟수)**만:
  "🚌 버스로 환승 1회 · 약 38분". 펼치면 타임라인.
- 모든 색·간격은 **기존 토큰만**(`--accent`·`--accent-soft`·`--warn`·`--border`·
  `--muted`·`--subcard`) 사용 → 새 hex 도입 없음(검사 H 무변경). 인라인 hex 전면 제거.
- 대안 ① 운영사 브랜드색 배지(채택 안 함 — Quiet Gray 단일 accent 철학 위반,
  시부모 포함 가족 화면에 시각 노이즈). ② 단순 줄바꿈(채택 안 함 — 구조 부재로
  인상·가독성 개선 미미).

## Consequences (그래서)

- **긍정**: 역명 병기가 각자 한 줄에 놓여 어떤 길이도 넘치지 않음. 환승이 도트·태그로
  한눈에. 운영사 구분은 아이콘·pill로 정갈. `DESIGN.md` 규칙(단일 accent·인라인 hex 금지)
  준수. CSS가 토큰 기반이라 다크모드 자동 적응.
- **부정·트레이드오프**: 상세 HTML이 노드당 div로 늘어 산출물 크기 소폭 증가.
  요약에서 노선 번호·역명은 펼쳐야 보임(요약은 의도적으로 간결).
- **후속**: 신규 교통 leg는 `places` ref만 채우면 타임라인이 자동 렌더.
  `tests/test_build_index.py`가 환승 태그·인라인 hex 부재를 회귀 가드.
- **영향 파일**: `scripts/build_index.py`(`render_transit_line_steps` 재작성 +
  `_render_transit_timeline`·`_render_transit_simple`·`_segment_pill`·`_segment_meta`
  헬퍼 + `render_css` `.tl*` 추가), `tests/test_build_index.py`, `DESIGN.md`(§4
  컴포넌트), `CLAUDE.md`.
