# 2026-05-30 — 장소 발음 + 장문 텍스트 자동 구조화

## Status

Accepted

## Context (왜)

모바일 공유 화면에서 세 부류의 텍스트가 장애를 만들었다.

### ① 장소 발음 누락 (발음 안 나오는 금각사)
`render_title_display()`가 `ja_name`이 있으면 `ja_reading_ko`를 버린다(`if ja_name … elif ja_reading`). 그래서 데이터에 발음이 있는 **금각사(킨카쿠지)·죽림길(치쿠린)조차** 화면엔 `금각사(金閣寺)`로만 나와 택시에서 발음 불가. 게다가 ~16개 사찰·신사·식당·주요 역은 `ja_reading_ko`가 빈칸이라 애초에 발음을 못 보여준다.

### ② 장문 상세 blob (iPhone Apple Wallet ICOCA 단권 …)
`day.pass_recommendation` 3건이 "iPhone Apple Wallet ICOCA 단권 — …"(130·219·241자)로, `pass_block`이 ` — ` 앞만 요약하고 **근거(시버스 3회 비용·1일권 비교)를 한 덩어리 문단**으로 접는다. 펼치면 ONE LONG STRING.

### ③ 의미 없는 "상세 보기" 폴드
`note_block`/`memo_block`이 구분자(` · `·`. `)를 못 찾으면 요약을 **"상세 보기"**로 떨궈 장문 전체를 통째 숨긴다. 확정 사례:
- 산넨자카 동선 note(143자), "전날 구매" note(295자)
- 카덴쇼 lodging note(153자: 확정번호·PIN), 시오 후기 note(65자)

## Decision (무엇)

### A. 발음 표시 (모든 장소 + 교통 노드)
- 신규 헬퍼 `title_reading_html(title)`: 장소 카드 제목 아래 🗣️ 발음 줄 렌더 (택시용)
  - 대상: 모든 `title` dict with `ja_reading_ko` (사찰·신사·역·식당 모두)
  - 5개 호출부(index/itinerary/table/candidates/mobile)에 `pronunciation_html` 삽입
  - `.pron` CSS: muted color, 0.8em size, 0.1rem margin
- 교통 타임라인 역·정류장에 발음 표시
  - 신규 헬퍼 `_station_reading_html(label)`: 역명 아래 🗣️ 발음 줄
  - `places` 레지스트리에 `reading` 필드 추가 (29개 역·정류장·랜드마크)
  - `.tl-reading` CSS: muted, 0.78em, margin-top 0.05rem
- **데이터**: `data/itinerary.json`에 ~16개 사찰·신사·식당 `ja_reading_ko` 백필 + `places` 29개 `reading` 추가

### B. 장문 상세 자동 구조화
- `_lead_split(text)` 재구현: 60자 이내 **가장 먼저 나타나는** 구분자 선택
  - 우선순위: `. ` > `다. ` > `요. ` > `음. ` > ` — ` > ` · `
  - 구분자 없으면 첫 60자 + "…" 추출 (의미있는 요약 항상 생성)
- 신규 헬퍼 `_detail_lines(text)`: 상세를 여러 `<div>` 줄로 분해
- `note_block` + `memo_block`: "상세 보기" 폴백 제거
- `pass_block`: rest를 ` + `·` · ` 기준 다중 줄로 렌더

### C. 테스트 + 검증
- TDD: 실패 테스트 5개 작성 후 구현 (신규 + 기존 수정 1개)
- 모든 113개 테스트 통과
- validate.py 0 errors
- 산출물 grep 검증:
  - `'상세 보기'` 0 instances (폴백 완전 제거)
  - place pronunciation 20개 줄 (`.pron` class)
  - station pronunciation 13개 줄 (`.tl-reading` class)

## Consequences (그래서)

- **긍정**: 
  - 택시·시부모가 발음 가능 (🗣️ 아이콘)
  - 장문 상세가 한 줄 blob 아닌 줄/리스트로 정돈
  - "상세 보기" 제네릭 폴백 소멸
  - 렌더러 개선 → 향후 모든 데이터에 자동 적용
  - 토큰 기반 (신규 hex 0)
- **부정·트레이드오프**:
  - `ja_reading_ko` ~16개 + `places.reading` 29개 수기 입력 (발음 정확도 책임)
  - 상세 HTML 노드 소폭 증가
  - 교통 타임라인 nodes 증가 (읽기 쉬움 ↔ 파일 크기)
- **후속**:
  - 신규 장소는 title에 `ja_reading_ko` 필수 (CLAUDE.md 컨벤션화)
  - 신규 역·정류장은 `places`에 `reading` 필수
- **영향 파일**:
  - `scripts/build_index.py` (헬퍼 3개 + CSS + 역맵)
  - `data/itinerary.json` (16개 title + 29개 place readings)
  - `tests/test_build_index.py` (5개 신규 + 1개 수정)
  - `CLAUDE.md` (컨벤션 추가)

## 검증 체크리스트

- [x] 113개 테스트 통과 (TDD)
- [x] validate.py 0 errors
- [x] `build_index.py --check` 멱등
- [x] "상세 보기" 0 instances
- [x] `.pron` 20개 줄 (장소 발음)
- [x] `.tl-reading` 13개 줄 (교통 노드 발음)
- [x] 타임라인 샘플: 간사이쿠코, 니조에키, 사가아라시야마에키 등 렌더
