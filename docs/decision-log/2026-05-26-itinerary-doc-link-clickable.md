# 2026-05-26 — 일정 조식 슬롯의 참조 문서 링크를 화면에서 탭 가능하게

## Status

Accepted

## Context (왜)

- 조식 슬롯(6/1·6/2·6/3)이 `breakfast-near-lodging.md`를 참조하지만, `data/itinerary.json` 항목 note에 **상대 경로 평문**(`docs/breakfast-near-lodging.md`)으로만 적혀 있었다.
- `build_index.py`의 일정 카드·시간표 note 렌더는 `esc()`만 적용 → URL/경로가 클릭 불가 평문으로 출력. 빌드 산출물(`viz/itinerary.html`·`viz/itinerary-table.html`)에서 조식 문서를 화면에서 바로 열 수 없었다.
- 사용자 지시(2026-05-26): "화면에서 클릭이 가능해야."
- 추가 제약: 호스트(Vercel)는 `.md`를 raw text로 서빙 → 상대 경로 링크는 동작하지 않음. CLAUDE.md 규칙상 외부 문서 링크는 GitHub blob URL이어야 한다.
- 이미 존재하는 패턴: 예약 체크리스트 항목은 `link`(url/label)를 `doc-link` 앵커로 렌더(`card_checklist`).

## Decision (무엇)

일정 항목에 `link`(url/label) 필드를 도입하고, 체크리스트와 동일한 `doc-link` 앵커로 렌더한다.

- `data/itinerary.json` 조식 3항목에 `link: {url, label}` 추가. url은 `https://github.com/ywkim/japan-trip/blob/main/docs/breakfast-near-lodging.md`(GitHub blob), label은 "조식 옵션·영업시간". note에서 평문 경로(`docs/...md`) 제거.
- `scripts/build_index.py`에 `doc_link_html(link)` 헬퍼 신설 → `build_itinerary`(카드·route_candidates)·`build_itinerary_table`(데스크탑 셀·모바일 카드) 4개 렌더 지점에서 note 뒤에 앵커 출력. 운영 요약 `index.html`(`card_itinerary`)은 note 미렌더라 제외.
- TDD: `tests/test_build_index.py`에 `ItineraryDocLinkTests` 추가 — (1) link.url이 `viz/itinerary.html`·`itinerary-table.html`에 `<a href>`로 렌더, (2) `.md` 링크는 GitHub blob URL이어야 함.
- 미채택: note 전체를 `linkify()`로 바꾸는 안(평문 URL이 길게 노출돼 모바일 가독성 저하, 라벨 불가) → 구조화 `link` 필드 채택.

## Consequences (그래서)

- 긍정: 조식 슬롯에서 영업시간 문서를 모바일 화면에서 1탭으로 열람. 체크리스트와 동일 패턴으로 일관. 향후 다른 일정 항목도 `link`로 참조 문서 연결 가능.
- 부정·트레이드오프: 일정 항목 스키마에 선택 필드 1개 추가(검사 화이트리스트엔 영향 없음 — 검사 G/I는 arrive_from·food_quality만 검증).
- 후속: 필요 시 다른 항목(예: 료칸·예약 상세)도 `link` 부여 가능.
- 영향 파일: `data/itinerary.json`, `scripts/build_index.py`, `tests/test_build_index.py`, 빌드 산출물(`viz/itinerary.html`·`viz/itinerary-table.html`), `CLAUDE.md`.
