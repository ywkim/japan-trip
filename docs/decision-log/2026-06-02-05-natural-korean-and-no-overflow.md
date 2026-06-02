# 2026-06-02 — 일본어 직역투 한국어 자연화 + 모바일 가로 폭 넘침 제거

## Status

Accepted

## Context (왜)

- 사용자 모바일 캡처·지적(2026-06-02): ① "직결·손꾸러미·물판" 등 일본어 직역투가 자연스럽지 않다, ② 페이지가 **가로로 밀려**(폭 넘침) 제목·본문 좌우가 잘린다.
- 원인 ②: `DOC_CSS`의 `.doc`가 `word-break: keep-all`(한글 단어 안 끊기) 단독이라, **공백 없는 긴 일본어 원문 인용**(예: "京都駅構内にあるので新幹線乗車前の最後の買い物にぴったり")이 줄바꿈되지 않아 컨테이너 폭을 넘겨 페이지 가로 스크롤을 유발. 모바일 카드 표의 flex 셀(값)도 `min-width:auto`라 긴 값이 넘칠 여지.

## Decision (무엇)

- **자연스러운 한국어로 교체** (data/MD): `직결`→`역과 바로 연결/이어진`, `손꾸러미`→`선물`, `물판`→`매장`, `에리어`→`구역`, `디스카운트`→`할인점`, `모닝`→`아침 영업`, `리모델`→`새단장`, 중복어 `폭우 우천`→`폭우`. 대상: `docs/isetan-porta-shopping-translation.md`(전면), `data/itinerary.json`(6/2 note 2건·day_label), `docs/kyoto-itinerary-may31-jun3-2026.md`(§1.3), `docs/isetan-matcha-dessert-translation.md`·`docs/nakamura-shoten-review-translation.md`(역 직결 표현), `build_index.py` DocPage 설명.
- **모바일 폭 넘침 제거** (`DOC_CSS`):
  - `.doc`에 `overflow-wrap: anywhere` 추가 — 공백 없는 긴 CJK 문자열도 폭에 맞춰 줄바꿈(한글 `keep-all`은 유지).
  - 좁은 화면(≤560px) 카드 셀을 flex → **블록(라벨 위·값 아래)**으로 변경 + `overflow-wrap: anywhere` — 긴 값도 절대 폭을 넘기지 않음.
- **검토 후 기각**: `body { overflow-x: hidden }`로 잘라내기(증상만 가림·원문 잘림 유지), 일본어 원문 인용 제거(번역 근거 약화).

## Consequences (그래서)

- 긍정: 가족이 읽는 문장이 자연스러워지고, 모든 문서 페이지가 모바일에서 가로 스크롤 없이 폭 안에 들어온다(긴 일본어 인용·긴 표 값 포함). 카드 셀은 '라벨(작은 muted) 위 / 값 아래'로 안정적.
- 부정·트레이드오프: 카드 셀이 2줄(라벨+값)이라 세로로 약간 길어짐. `overflow-wrap: anywhere`는 긴 일본어를 임의 지점에서 끊을 수 있음(일본어엔 자연스러움).
- 영향 받은 파일: `scripts/build_index.py`(`DOC_CSS` `.doc`·카드 셀, DocPage 설명), `tests/test_build_index.py`(overflow-wrap 잠금 테스트 +1), `docs/*translation.md` 3건, `data/itinerary.json`, `docs/kyoto-itinerary-may31-jun3-2026.md`.

## Test plan

- [x] `DocTableResponsiveTests` 7건(overflow-wrap 잠금 포함) PASS
- [x] `unittest` 219/219 PASS
- [x] `build_index.py` 빌드 + `--check` 재현성 통과
- [x] `validate.py` 0 errors
