# 2026-06-02 — 교토역 실내 쇼핑 4개 시설 일본어 후기 번역 페이지 추가

## Status

Accepted

## Context (왜)

- 6/2(화) 폭우 우천 실내 코스의 12:30 "이세탄·포르타 실내 구경" 항목은 **선물 봉인팩(돈키호테 아반티→요도바시) 동선**까지 메모로 들어가 있으나, 가족이 현장에서 참고할 **시설별 안내·후기**는 없었다.
- 사용자 지시: "이세탄·포르타 실내 구경 일본어 후기 찾고 번역해서 페이지 추가해 — 돈키호테·요도바시 등."
- PR #89 패턴(레포 마크다운 → 사이트 내 HTML 렌더 + 일정 카드 link)을 그대로 적용하면 GitHub 노출 없이(검사 J) 가족 공유 사이트에서 열람 가능.

## Decision (무엇)

- **`docs/isetan-porta-shopping-translation.md` 신규 작성** — 교토역 직결 4개 시설(JR교토 이세탄·교토 포르타·돈키호테 아반티점·요도바시 카메라 교토)의 일본어 가이드·블로그·공식 안내를 한국어로 번역·재구성.
  - 이세탄: 데파치카 손꾸러미 6선(ことりっぷ·FOODIE) + 영업·동선
  - 포르타: 현지 방문기(京暮らし 블로그) — 비 안 맞는 지하상가·깨끗한 화장실·동/서 에리어
  - 돈키호테: 오픈 리포트(京都ピ) — 2F 전체·면세·다언어 POP·봉인팩
  - 요도바시: 공식 층 구성 + 포켓몬 카드 **공식 취급점**(정가·재고 안정) + 6F 다이닝
  - 말미에 6/2 동선 활용법 + 출처 표(2026-06 조회).
- `build_index.py` `DOC_PAGES`에 `viz/isetan-porta-shopping.html` 1줄 등록(og_slug=itinerary 재사용 — 신규 SVG 불필요).
- 6/2 12:30 항목에 `link`(`isetan-porta-shopping.html`) 추가 + 사람용 사본 §1.3에 동일 링크.
- **검토 후 기각**: 식당 평점(food_quality) 부여 — 본 항목은 식사가 아닌 쇼핑·구경이라 평점 대상 아님(검사 I 면제). 외부 이미지 blog_reviews — 자가호스팅 이미지 없이 텍스트 번역으로 충분.

## Consequences (그래서)

- 긍정: 12:30 실내 구경 카드에서 4개 시설 후기를 탭 한 번에 열람, 봉인팩 조달처(돈키호테·요도바시) 성격·층·면세를 현장에서 확인. 우천 실내 동선의 정보 밀도 보강.
- 부정·트레이드오프: 돈키호테 영업시간(공식 9:00~24:00 / 안내처별 10:00 표기)·요도바시 완구 재고 등 현장 변동 요소는 "방문 전 확인"으로 명시. 시세·평점은 추후 묵으면 재조회 필요.
- 후속: 6/2 아침 예보 호전 시 원안 복귀하면 본 페이지는 참고용으로 보존(링크만 비활성 가능).
- 영향 받은 파일: `docs/isetan-porta-shopping-translation.md`(신규), `scripts/build_index.py`(DOC_PAGES), `data/itinerary.json`(6/2 items[3].link), `docs/kyoto-itinerary-may31-jun3-2026.md`(§1.3 12:30 링크), `CLAUDE.md`(트리·DOC_PAGES 24·후기 5), `README.md`.

## Test plan

- [x] `validate.py` 0 errors (검사 J — 렌더 산출물 github.com 없음 포함)
- [x] `unittest` 212/212 PASS
- [x] `build_index.py` 빌드(viz/isetan-porta-shopping.html 생성) + `--check` 재현성 통과
- [x] 4개 시설 위치·영업시간·면세·포켓몬 취급 공식/블로그 교차 확인(2026-06 WebSearch·WebFetch)
