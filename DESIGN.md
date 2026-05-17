# DESIGN.md — Quiet Ledger

> `voltagent/awesome-design-md` 컨벤션. AI 에이전트가 UI 변경 시 본 문서를 1차 출처로 읽고, 정확한 토큰 값은 `data/design-tokens.json`을 참조한다. 두 문서의 drift는 `scripts/validate.py` (G)가 차단한다.

**Theme**: Quiet Ledger · **Version**: 1.0.0

## 1. Visual Theme & Atmosphere

**의도**: "정량 의사결정 협업 공간"의 시각화. 회계 장부·필드 노트의 차분한 분위기. 두 사람이 데스크에 앉아 데이터를 검토하는 시간을 존중하는 미감.

- 자극보다 가독, 장식보다 정보.
- 일본 모티브(torii red, sakura pink) 회피. 본 레포는 "Japan-themed"가 아니라 "Japan-trip decision-making".
- 빨강 accent 폐기 → **slate-indigo** 단일 accent. 빨강은 오직 danger status에만.
- 라이트 모드는 따뜻한 종이톤(`#F7F6F2`), 다크 모드는 진청색 잉크톤(`#161821`).
- 한국어 본문이 1차. macOS·iOS 시스템 폰트를 우선하고 Pretendard로 fallback.

## 2. Color Palette & Roles

| 역할 | Light | Dark | 비고 |
|---|---|---|---|
| `bg` | `#F7F6F2` | `#161821` | 페이지 배경 |
| `surface` | `#FFFFFF` | `#1F222C` | 카드 표면 |
| `surface_sunken` | `#EFEDE6` | `#13151D` | 서브카드·표 스트라이프 |
| `ink` | `#1B1D24` | `#E8E6DE` | 본문 텍스트 |
| `ink_muted` | `#5B6070` | `#9A9DA8` | 보조 텍스트·라벨 |
| `border` | `#D9D6CC` | `#2E3140` | 보더·디바이더 |
| `accent` | `#3E5C76` | `#8AA8C7` | 단일 강조 (slate-indigo). 링크 hover·강조 테두리·진행 바 |
| `accent_soft` | `#E3EAF3` | `#262E3A` | accent 배경 (hover surface, bar track) |
| `ok` | `#2F7D5B` | `#6FB58E` | status "ok" (예산 통과·확정) |
| `warn` | `#B5811F` | `#D4B36A` | status "near"·"예약중"·조기 입림 |
| `danger` | `#9A3B3B` | `#D08585` | status "over"·"미정"·예산 초과 |
| `table_stripe` | `#EFEDE6` | `#262E3A` | 표 짝수 행 |
| `bar_track` | `#E3EAF3` | `#262E3A` | 진행 바 트랙 |

**규칙**:
- `accent`는 한 번에 한 컴포넌트만 강조. 페이지 안에서 5회 이상 노출되면 시각 노이즈.
- status 3색(`ok`/`warn`/`danger`)은 의미적으로만 사용. 미감적 색상으로 전용 금지.
- accent와 status 색은 본문 텍스트로 쓰지 않음 (대비 미달 위험). 텍스트 색상은 `ink`/`ink_muted`만.

## 3. Typography Rules

- **본문**: `-apple-system, "Apple SD Gothic Neo", "Pretendard Variable", BlinkMacSystemFont, "Segoe UI", sans-serif`
- **숫자·코드**: `"SF Mono", "JetBrains Mono", ui-monospace, monospace` + `font-variant-numeric: tabular-nums`
- **스케일(rem)**: xs 0.75 · sm 0.8125 · base 0.9375 · md 1.0625 · lg 1.375 · xl 1.75
- **line-height**: body 1.5, display 1.25
- **weight**: regular 400, medium 500, semibold 600
- 본문 기본 폰트 크기는 `base` (rem 0.9375 ≈ 15px). 모바일 가독성을 위해 viewport meta는 `width=device-width, initial-scale=1.0` 고정.
- h1: `xl` · h2: `lg` · h3·subtitle: `md` · 보조 텍스트: `sm`. 캡션·각주: `xs`.
- **단위**: 모든 수치(가격·점수·거리)에 `tabular-nums` 적용 → 표·열 정렬.

## 4. Component Stylings

### Card
- `background: surface`, `border: 1px solid border`, `radius: 8px (md)`, `padding: 1rem (base)`.
- 다크 모드에서만 `box-shadow: 0 1px 0 rgba(0,0,0,0.25)`.
- 카드 내부 첫 요소는 `h2` (섹션 제목, `ink_muted` 색 + medium weight).

### Subcard (카드 내부)
- `background: surface_sunken`, `border: 1px solid border`, `radius: 4px (sm)`, `padding: 0.75rem (md)`.
- 카드 안에서 그룹화 용도. 그림자 없음.

### Row (key-value 라인)
- `display: flex; justify-content: space-between`.
- `padding: 0.35rem 0` + `border-bottom: 1px solid border` (마지막은 없음).
- `.k`: `ink_muted`, `.v`: `ink` + `tabular-nums`.

### Navigation pill
- `padding: 0.4rem 0.7rem`, `border: 1px solid border`, `radius: 999px`.
- `background: surface`. hover 시 `border-color: accent`.

### Progress bar
- `height: 6px`, `background: bar_track`, `radius: 3px`.
- fill: `background: accent`.

### Buttons / Links footer
- 보더만 있는 ghost 스타일. `background: transparent`, `border: 1px solid border`, `radius: 4px`.
- hover 시 `border-color: accent`. 텍스트 색은 `ink`.

### Badge (status pill)
- `display: inline-block`, `padding: 0.1rem 0.45rem`, `border: 1px solid currentColor`, `radius: 4px (sm)`.
- 텍스트 색이 곧 보더 색 (`currentColor`). 사용처: `viz/checklist.html`의 상태 라벨.

## 5. Layout Principles

- **Mobile-first**. 4개 산출물(`index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/checklist.html`) 모두 단일 컬럼 기본 (`itinerary-table`은 600px+ 가로 4열 시간표).
- 모든 요소는 `box-sizing: border-box`.
- 세로 리듬: 카드 간 `0.75rem (md)`, 서브카드 간 `0.5rem (sm)`.
- 좌우 여백: 본문 `padding: 1rem (base)`.
- 카드는 풀-너비. 다중 컬럼 레이아웃은 도입하지 않음 (모바일 우선).

## 6. Depth & Elevation

- **거의 평면**. 그림자는 dark 모드 카드에 1px 라이너만.
- 강조는 그림자 대신 `accent` 보더로. 선택된 시나리오 카드는 `border-color: accent` (1px → 시각적 무게 증가).
- 반경 스케일: `sm 4px` (input·button·subcard) · `md 8px` (card) · `lg 12px` (예약 — modal 등 후속).

## 7. Do's and Don'ts

**Do**
- 새 색이 필요하면 먼저 `data/design-tokens.json`에 추가 + 본 문서 §2에 행 추가.
- status 표현은 `ok`/`warn`/`danger` 셋만. 신호등 의미가 명확하지 않으면 `ink_muted`.
- 숫자는 tabular-nums. 가격·점수·날짜 모두.
- 한국어 줄바꿈은 `word-break: keep-all`로 단어 단위.

**Don't**
- 레거시 빨강 accent(이전 `#d3`+`3` 톤) 재도입 금지. danger 외 모든 강조는 slate-indigo accent.
- 인라인 hex code 금지. 반드시 CSS 변수(`var(--accent)`, `var(--ok)`)로.
- 그림자 남용 금지. 평면 우선.
- Web font 추가 금지 (HTML 더블클릭 자체완결 보장 — 4개 산출물 공통 제약).
- 일본 모티브 장식(torii·sakura·후지산) 금지. 본 레포는 의사결정 도구.

## 8. Responsive Behavior

- 단일 컬럼. 미디어 쿼리는 다크 모드 전환(`prefers-color-scheme`)에만 사용.
- breakpoint 토큰(`mobile_max: 640px`, `tablet_max: 960px`)은 후속 컴포넌트 대비 보유. 현재 layout은 flex/grid wrap으로 자연 적응.
- 표가 필요하면 `overflow-x: auto` 컨테이너로 감싸 좁은 화면 가로 스크롤 보장.
- 모든 hover 효과는 데스크탑용. 모바일은 tap 즉시 반응 (transition ≤ 0.2s).

## 9. Agent Prompt Guide

> AI 에이전트가 UI 변경 작업을 시작할 때 본 섹션을 그대로 프롬프트에 인용한다.

**작업 전 점검**
1. 색이 필요한가? → `data/design-tokens.json` `color.light`·`color.dark` 키를 그대로 사용. 새 hex를 그대로 박지 말 것.
2. 텍스트 강조가 필요한가? → `ink` / `ink_muted` 두 단계만. accent로 텍스트 색 지정 금지.
3. status 표시인가? → `ok` / `warn` / `danger` 셋 중 정확히 하나 매핑.
4. 새 컴포넌트인가? → §4의 기존 컴포넌트(Card·Subcard·Row·Pill·Bar·Button)로 조합 가능한지 먼저 확인.

**구현 규칙**
- `index.html`·`viz/itinerary.html`·`viz/itinerary-table.html`·`viz/checklist.html`은 모두 `scripts/build_index.py` 산출물. 직접 편집 금지. CSS는 공통 `render_css(tokens)` 함수가 design-tokens.json에서 생성 → `html_doc(title, body, tokens)`이 주입.
- 새 색·간격·반경을 도입할 때: (1) tokens.json에 키 추가 → (2) DESIGN.md §2~§6 갱신 → (3) `render_css`가 var()로 노출 → (4) 사용처에서 `var(--키)` 참조.

**금지 패턴 (자동 거부)**
- 인라인 `style="color:#XXXXXX"`로 새 hex 도입 → CSS 변수로 교체.
- 레거시 팔레트 잔재(이전 빨강·미색 톤) → 즉시 토큰으로 치환.
- Web font import (`@font-face`, Google Fonts) → 시스템 폰트 스택 유지.

**검증**
- 변경 후 `python scripts/build_index.py && python scripts/validate.py` 실행. exit 0 이어야 함.
- 다크 모드 전환(OS 토글)으로 두 팔레트 시각 확인.
