# 2026-05-31 — DOC_PAGES 누락 등록 빌드 오류 해결

## Status

Accepted

## Context (왜)

PR #89(6/1 eX cafe·만자라테이 일본어 리뷰 한국어 번역)를 제출 후 GitHub Actions CI에서 `validate` 잡이 실패했으나, 로컬에서는 모든 검증이 통과하는 불일치 현상 발생.

**초기 현상**:
- 로컬 validation: ✅ 모두 통과 (build_index.py, unittest 212/212, validate.py 0 errors)
- GitHub Actions: ❌ unittest 단계에서 2개 테스트 실패
- mergeable_state: `blocked`

**실제 오류**(GitHub Actions 로그에서 발견):
```
FAIL: test_index_checklist_doc_link_target_exists
AssertionError: index.html checklist doc-link target not built: 'viz/excafe-review.html'

FAIL: test_breakfast_link_resolves_to_built_page
AssertionError: onsite doc-link target 'manzaratei-review.html' is not a built page
```

**근본 원인**:
- `docs/excafe-review-translation.md` 신규 추가 후 `scripts/build_index.py`의 `DOC_PAGES` 튜플에 등록하지 않음
- `docs/manzaratei-review-translation.md`도 동일 상황
- `data/itinerary.json`의 링크 필드가 `excafe-review.html`, `manzaratei-review.html` 등을 참조하나, 빌드 아웃풋에 페이지가 생성되지 않아 테스트 실패

## Decision (무엇)

`scripts/build_index.py` 줄 122~134에 신규 DocPage 2개 추가:

```python
DocPage(
    "docs/excafe-review-translation.md", "viz/excafe-review.html",
    "eX cafe — 당고 직화구이와 100년 목조 가옥",
    "일본어 후기 한국어 번역 — 당고 직화구이·여름 말차 빙수·아라시야마 카페 비교",
    "itinerary", "itinerary", "itinerary.html", "← 일정",
),
DocPage(
    "docs/manzaratei-review-translation.md", "viz/manzaratei-review.html",
    "만자라테이 — 130년 전통 교마치야의 창작 교토요리",
    "일본어 후기 한국어 번역 — 130년 전통·오반자이·강변 야외석(川床)",
    "itinerary", "itinerary", "itinerary.html", "← 일정",
),
```

채택하지 않은 대안:
- 테스트 수정: 테스트가 맞고, 빌드 구성이 잘못된 것이 근본 원인이므로 미채택
- 사후 이미지 추가: DOC_PAGES에 등록 후에야 빌드 산출물이 생성되므로 미필수

## Consequences (그래서)

**긍정 영향**:
- CI 실패 원인 규명 (로컬 재현 불가능한 환경 차이 해결)
- unittest 212/212 PASS로 복귀
- PR #89 mergeable_state 정상화 (CI 차단 해소)
- 향후 신규 문서 페이지 추가 시 패턴 명확화

**부정·트레이드오프**:
- None — 순수 누락 수정

**후속 행동**:
- CLAUDE.md TDD 규칙 재확인: 데이터 구조(data/itinerary.json) 변경 시, 관련 빌드 구성(DOC_PAGES) 변경도 동시에 수행 필수
- 신규 문서 페이지 추가 체크리스트:
  1. `docs/*.md` 파일 생성/수정
  2. `data/itinerary.json`의 link.url 참조 확인
  3. `scripts/build_index.py`의 DOC_PAGES 등록 확인 (생략 시 테스트 실패)
  4. 로컬 `build_index.py` + `unittest` 재실행으로 검증

**영향 받은 파일**:
- `scripts/build_index.py` (DOC_PAGES 2줄 추가)
- commit: fb87a5c

## 근본 원인 분석

**왜 로컬에서는 통과했나?**
- 로컬은 기존 산출물(`viz/excafe-review.html` 등)이 이전 빌드에서 이미 생성되어 있었음
- gitignore 때문에 산출물이 커밋되지 않으므로 CI 환경에서는 빌드 첫 실행 시 DOC_PAGES 미등록 → 산출물 미생성 → 테스트 실패

**테스트가 작동한 이유**:
- `test_index_checklist_doc_link_target_exists`: 빌드된 모든 viz HTML을 OUTPUTS 에서 검색하는 회귀 테스트
- DOC_PAGES에 없으면 빌드되지 않으므로 OUTPUTS에서 찾을 수 없어 실패 — **의도대로 작동**

## 학습

1. **gitignore 산출물의 함정**: 로컬은 산출물이 캐시되어 있어 빌드 누락이 드러나지 않음 → CI(깨끗한 환경)에서만 발견
2. **회귀 테스트의 가치**: build_index.py의 구성 오류를 자동으로 검출
3. **메타 동기화**: 데이터 구조 + 빌드 구성 + 테스트는 일원화되어야 함 (한쪽만 변경하면 불일치)

---

출처: GitHub Actions 로그 (2026-05-31T14:17:19Z)
