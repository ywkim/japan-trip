# 2026-05-26 — 조식 참조를 사이트 내 페이지로 (Vercel 화면 GitHub 링크 금지)

## Status

Accepted (`2026-05-26-itinerary-doc-link-clickable.md`의 조식 링크 대상 결정을 일부 Superseded — GitHub blob URL → 사이트 내 HTML 페이지)

## Context (왜)

- 직전 결정(`2026-05-26-itinerary-doc-link-clickable.md`)에서 조식 슬롯의 `link.url`을 **GitHub blob URL**(`.../blob/main/docs/breakfast-near-lodging.md`)로 두어 화면에서 탭 가능하게 했다.
- 사용자 지시(2026-05-26): "Vercel 화면에서 GitHub 링크 금지." 비기술 동반자(시부모·소연)에게 운영 화면에서 GitHub로 튕기는 동선은 부적절.
- 제약: Vercel(호스트)은 `.md`를 raw text로 서빙 → 상대 경로 `.md` 링크는 깨지고, GitHub blob 링크는 사이트를 벗어난다. 두 방식 모두 사용자 요구에 부적합.
- 사용자 선택(범위·방식): "조식 링크만 먼저" + "사이트 내 HTML 페이지".

## Decision (무엇)

조식 옵션을 `data/breakfast.json` 단일 출처로 구조화하고, `build_index.py`가 사이트 내 페이지 `viz/breakfast.html`로 렌더한다. 일정의 조식 `doc-link`는 이 on-site 페이지를 상대 경로로 가리킨다.

- `data/breakfast.json` 신설 — 아침 3회 표·숙소별 가게(거리/영업/휴무/메모)·아침별 권장·주의·출처. `docs/breakfast-near-lodging.md`는 사람용 사본으로 보존.
- `scripts/build_index.py`: `build_breakfast(d)` + `OUTPUTS`에 `viz/breakfast.html` 추가(총 7 HTML). `doc_link_html()`은 url이 사이트 내 경로면 같은 탭(`target` 없음), 외부(http)면 새 탭으로 렌더.
- `data/itinerary.json` 조식 3항목 `link.url`: GitHub blob → `breakfast.html`. pending 항목의 평문 `docs/...md` 참조도 제거.
- TDD: `ItineraryDocLinkTests`(github 금지·`.md` 금지·on-site `.html`·대상 페이지 실존) + `BreakfastPageTests`(핵심 콘텐츠·GitHub 링크 0·standalone).
- 미채택: (a) `.md`를 빌드 시 HTML로 파싱 — 외부 의존성/파서 부담, 데이터 단일 출처 원칙과 어긋남. (b) 인라인 fold — 콘텐츠 길어 일정 카드 과밀. (c) GitHub blob 전면 유지 — 사용자 지시 위반.
- 범위 한정: 이번엔 **조식 링크만**. 다른 GitHub blob 링크(최종보고서·결정일지·예약리서치·교통패스)는 유지 — 별도 판단.

## Consequences (그래서)

- 긍정: 조식 정보를 Vercel 사이트 안에서 완결적으로 열람(외부 이탈 없음). 데이터 단일 출처 + 빌드 렌더 패턴 일관. 출처 링크(ekiten·타베로그 등 외부, GitHub 아님)는 그대로 노출.
- 부정·트레이드오프: `breakfast.json`↔`breakfast-near-lodging.md` 이중 관리(둘 다 갱신 필요). 빌드 산출물 1개 증가(7 HTML). 사이트 내 다른 GitHub 링크와 정책 비대칭(조식만 on-site).
- 후속: 나머지 GitHub blob 링크도 on-site로 옮길지 별도 결정. `breakfast.json` 스키마 검증을 `validate.py`에 추가할지 검토(현재 미적용).
- 영향 파일: `data/breakfast.json`(신규), `data/itinerary.json`, `scripts/build_index.py`, `tests/test_build_index.py`, 빌드 산출물(`viz/breakfast.html` 신규·`viz/itinerary*.html`), `CLAUDE.md`, `README.md`.
