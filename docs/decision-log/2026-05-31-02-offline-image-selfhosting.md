# 2026-05-31 — 외부 이미지 자가호스팅 + 서비스 워커 referer 보정 (오프라인 이미지 보장)

## Status

Accepted

## Context (왜)

- 직전 PR(#80, `2026-05-31-offline-service-worker.md`)로 비행기 모드에서 **모든 페이지 재오픈은 달성**했으나, Vercel 프리뷰 실측(비행기 모드 스크린샷)에서 **일부 외부 이미지가 깨졌다.**
- 포스트모템으로 호스트별 차이를 확인: `commons.wikimedia.org`·`search.pstatic.net`은 오프라인 표시 ✅, `blogthumb.pstatic.net`·`tblg.k-img.com`(타베로그)은 깨짐 ❌.
- 근본 원인: 서비스 워커의 install 사전 캐시 `fetch(url, {mode:"no-cors"})`는 **SW origin을 referer로 전송**한다. 반면 페이지의 `<img>`는 `referrerpolicy="no-referrer"`. 핫링크 보호(referer 검사) 호스트가 SW의 referer 붙은 요청을 거부(403)해 쓸모없는 응답이 캐시됐다.
- 실측 검증: referer 없이 받으면 **모든 호스트가 200**(`blogthumb`·`tblg` 포함) — 자가호스팅·no-referrer 둘 다 유효함을 확인.
- 사용자 지시: 포스트모템 후 "A + B 둘 다"(경량 SW 보정 + 빌드 자가호스팅) 선택.

## Decision (무엇)

- **B(자가호스팅, 진짜 보장)**: `scripts/fetch_assets.py`를 추가해 itinerary.json의 외부 이미지를 **referer 없이** 내려받아 `assets/place-images/<url-sha1>.<ext>`로 저장하고, `url → 로컬경로` 매핑을 `data/local-image-map.json`에 기록한다. 이미지·매핑을 **커밋**하고, `build_index.py`(`local_src()`)가 빌드 시 외부 URL을 로컬 경로로 치환한다 — **빌드는 네트워크 비의존·결정론**(다운로드는 작성자 측 1회). 서비스 워커는 `assets/place-images/`를 CORE 사전 캐시에 포함.
- **A(SW referer 보정, 스톱갭)**: install best-effort fetch에 `referrerPolicy: "no-referrer"` 추가(=`<img>`와 일치). 자가호스팅 안 된 소수 외부 이미지의 사전 캐시 적중률을 높인다.
- 다운로드 실패(dead URL·404)한 이미지는 외부 URL을 그대로 유지(graceful) — A의 best-effort로만 시도.
- 채택 안 한 대안: 빌드 시점(Vercel) 다운로드 — 산출물 결정성 훼손·빌드 네트워크 의존으로 기각.
- TDD: `SelfHostedImageTests` 4개(매핑 치환·HTML 외부 URL 누출 없음·SW place-images 사전 캐시·SW no-referrer) 선작성.

## Consequences (그래서)

- 긍정: 자가호스팅된 **42/48 이미지가 오프라인 100% 보장**(로컬 자산이라 install 사전 캐시 확정). dead URL 6개를 제외한 모든 장소 사진·블로그 썸네일이 비행기 모드에서 표시된다. referer 보정으로 잔여 외부 이미지 적중률도 개선.
- 부정·트레이드오프: 레포에 바이너리 이미지 ~2.7MB(42장) 추가. 외부 이미지가 갱신되면 `scripts/fetch_assets.py` 재실행 + 재커밋 필요(자동 아님). dead URL 6개는 원본이 사라져(404) 오프라인·온라인 모두 깨진 채 유지 — 복구 불가.
- 후속 행동: 일정 이미지 추가·교체 시 `uv run python scripts/fetch_assets.py` 실행 후 `assets/place-images/`·`data/local-image-map.json` 재커밋. `--check`로 누락 감시 가능.
- 영향 받은 파일: `scripts/fetch_assets.py`(신규), `data/local-image-map.json`(신규), `assets/place-images/*`(신규, 커밋), `scripts/build_index.py`(`local_src`·이미지 치환·SW CORE/EXTERNAL/no-referrer), `tests/test_build_index.py`(`SelfHostedImageTests`), `README.md`, `CLAUDE.md`.
