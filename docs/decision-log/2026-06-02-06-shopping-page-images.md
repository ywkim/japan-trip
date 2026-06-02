# 2026-06-02 — 쇼핑 가이드 페이지 시설 사진 추가 (위키미디어 Commons 자가호스팅)

## Status

Accepted

## Context (왜)

- 사용자 지적(2026-06-02): `viz/isetan-porta-shopping.html` 에 이미지가 없어 텍스트만 나온다.
- `DOC_PAGES` 마크다운→HTML 렌더(`render_markdown_body()`)가 `local_src()` 자가호스팅 치환을 거치지 않아, 마크다운에 `![alt](url)` 를 넣어도 외부 URL 그대로 노출된다.
- `fetch_assets.py`의 `collect_urls()`가 `itinerary.json`만 스캔해 `docs/*.md` 이미지를 다운받지 못한다.
- 4개 시설(JR이세탄·포르타·아반티·요도바시) 외관 사진은 Wikimedia Commons에서 CC 라이선스(BY 4.0 / BY-SA 3.0)로 제공된다.

## Decision (무엇)

- **`docs/isetan-porta-shopping-translation.md`** 각 시설 절(`##`)에 Wikimedia Commons 960px thumb 이미지 4장 추가.
  - JR교토 이세탄 2층 입구: `JR_Kyoto_Isetan_Level_2_Entrance_2025.JPG` (CC BY 4.0)
  - 교토 포르타 아트리움: `Kyoto_Porta_Atrium_2025.JPG` (CC BY 4.0)
  - 교토 아반티 빌딩: `Kyoto_Avanti_(Redevelopment_building)_Kyoto,_JAPAN.jpg` (CC BY-SA 3.0)
  - 요도바시 카메라 교토 빌딩: `Kyoto_Yodobashi_Bldg_20101106-001.jpg` (CC BY-SA 3.0)
- **`scripts/fetch_assets.py`**: `collect_doc_urls()` 함수 추가 — `docs/*.md` 마크다운 이미지 URL(`![](http...)`)을 수집. `main()`에서 `collect_urls()`(itinerary) + `collect_doc_urls()`(docs) 병합.
- **`scripts/build_index.py`**: `_IMG_SRC_RE` 추가 + `render_markdown_body()`에서 `<img src>` 를 `local_src()`로 치환 → DOC_PAGES 페이지도 자가호스팅 이미지로 서빙.
- **`DOC_CSS`**: `.doc img { max-width: 100%; height: auto; border-radius: 8px; ... }` 추가.
- **자가호스팅 실행**: `uv run python scripts/fetch_assets.py` → 4장 + 이전 미다운로드 이미지 다운로드, `data/local-image-map.json` 갱신, `assets/place-images/` 커밋.
- **검토 후 기각**: 외부 URL 그대로 렌더 — 자가호스팅 없이는 비행기 모드에서 깨지고, SW best-effort가 위키미디어를 잡지 못할 수 있다.

## Consequences (그래서)

- 긍정: 쇼핑 가이드 페이지에 각 시설 외관 사진이 노출되어 한눈에 파악 가능. 모든 DOC_PAGES 마크다운에서 이미지 자가호스팅이 동작하는 공통 인프라 완성.
- 부정·트레이드오프: `docs/*.md` 이미지를 추가할 때 `fetch_assets.py`를 재실행해야 한다.
- 영향 받은 파일: `docs/isetan-porta-shopping-translation.md`(이미지 4장), `scripts/fetch_assets.py`(`collect_doc_urls`), `scripts/build_index.py`(`_IMG_SRC_RE`·`render_markdown_body`·`DOC_CSS`), `data/local-image-map.json`, `assets/place-images/`(13장 신규), `tests/test_build_index.py`(+1), `tests/test_scripts_json.py`(+3).

## Test plan

- [x] `test_render_markdown_body_applies_local_src` PASS
- [x] `FetchAssetsDocUrlTests` 3건 PASS
- [x] `unittest` 223/223 PASS
- [x] `build_index.py` 빌드 + `--check` 재현성 통과
- [x] `validate.py` 0 errors
