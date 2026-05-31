# 2026-05-31 — 서비스 워커 + PWA 매니페스트로 비행기 모드 완전 오프라인 보장

## Status

Accepted

## Context (왜)

- 가족 공유 운영 사이트(`index.html` + `viz/*.html`)는 현지(교토)에서 일정·예약·체크리스트를 확인하는 용도다. 시부모 동반 + eSIM/로밍 불안정(`docs/decision-log/2026-05-26-connectivity-mixed-carrier-roaming.md`) 상황에서 **네트워크가 끊겨도 모든 페이지를 다시 열 수 있어야** 한다.
- 기존 구조는 CSS·JS가 전부 인라인이고 시스템 폰트만 써서 **구조적으로는 오프라인 친화적**이었으나, ① 서비스 워커·PWA 매니페스트가 전혀 없어 비행기 모드에서 페이지 재오픈이 브라우저 캐시 운에 의존했고, ② 장소 사진(위키미디어)·블로그 썸네일이 외부 URL이라 오프라인에서 깨졌다.
- 사용자 지시: "비행기 모드에서 모든 페이지 다시 열 수 있게 완전 사전 캐시 오프라인 기능 보장".
- 대안과 한계:
  - 외부 이미지 빌드 시 자가호스팅(다운로드) — 빌드 시점 네트워크 의존·산출물 결정성 훼손(`tests/test_build_index.py` 재현성 검사와 충돌). 채택 안 함.
  - 아이콘 PNG 생성 — Pillow 등 추가 의존이 필요(레포는 `markdown`만 의존). SVG 아이콘으로 대체.

## Decision (무엇)

- `scripts/build_index.py`가 **서비스 워커(`sw.js`)·PWA 매니페스트(`manifest.json`)·앱 아이콘(`assets/icon.svg`)을 빌드 산출물로 생성**하고, `html_doc()`이 전 페이지에 매니페스트 링크 + 서비스 워커 등록 스크립트(`SW_REGISTER_SCRIPT`)를 주입한다.
- 서비스 워커 캐시 전략:
  - **install**: 전 HTML 페이지 + 로컬 자산(숙소 사진·아이콘·매니페스트)을 `cache.addAll`로 사전 캐시(반드시 성공). 외부 이미지(장소 사진·블로그 썸네일)는 `no-cors` best-effort(`Promise.allSettled`, 실패 무시).
  - **fetch**: cache-first. 캐시 미스 시 네트워크 응답을 런타임 캐시(한 번 본 자원은 오프라인에 남음). 오프라인 내비게이션은 캐시된 `/index.html`로 폴백.
  - **activate**: 이전 버전 캐시 정리.
- 캐시 버전(`CACHE` 상수)은 `compute_cache_version(d)` — 전 산출물 콘텐츠의 SHA-256 해시(앞 12자리). 콘텐츠가 바뀌면 캐시가 자동 무효화되고, 안 바뀌면 동일(결정론 → `--check`·idempotency 통과).
- 산출물 3종(`sw.js`·`manifest.json`·`assets/icon.svg`)은 기존 CD 분리 정책(`2026-05-27-cd-artifact-separation.md`)에 따라 `.gitignore` 처리 — 커밋하지 않고 CI·Vercel·로컬에서 빌드.
- TDD: `tests/test_build_index.py`에 `OfflineCapabilityTests` 7개 케이스를 먼저 추가(산출물 생성·등록 주입·전 페이지 사전 캐시·생명주기/오프라인 폴백·콘텐츠 해시 버전·매니페스트 유효성·GitHub 링크 부재).

## Consequences (그래서)

- 긍정:
  - HTTPS(Vercel)에서 한 번 방문하면 **비행기 모드로도 모든 페이지가 다시 열린다**. 외부 사진은 온라인에서 본 적 있으면 캐시되어 오프라인에서도 보인다.
  - PWA 매니페스트로 홈 화면 추가(standalone) 가능 — 현지에서 앱처럼 사용.
  - 캐시 버전이 콘텐츠 해시라 배포 시 자동 갱신, 결정론 유지.
- 부정·트레이드오프:
  - 외부 이미지는 **사전 방문하지 않으면** 오프라인에서 깨질 수 있다(빌드 시 자가호스팅을 택하지 않은 결과). best-effort 사전 캐시로 완화하나 100% 보장은 아님.
  - iOS는 SVG `apple-touch-icon`을 무시할 수 있어 홈 화면 아이콘이 스크린샷으로 폴백될 수 있다(오프라인 캐싱 자체는 동작).
  - 서비스 워커는 `file://` 더블클릭에서는 동작하지 않음(HTTPS/localhost 필요) — 로컬 미리보기는 기존대로 페이지만 열림.
- 후속 행동: 외부 사진까지 100% 보장이 필요해지면 별도 PR로 빌드 시 이미지 자가호스팅(결정성 확보 방안 포함) 검토.
- 영향 받은 파일: `scripts/build_index.py`(SW/매니페스트/아이콘 빌더·등록 주입·`compute_cache_version`·`OUTPUTS`), `tests/test_build_index.py`(`OfflineCapabilityTests`), `.gitignore`(신규 산출물 3종), `README.md`, `CLAUDE.md`.
