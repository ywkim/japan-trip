# 2026-05-30 — 야경 코스 PR(#73)에 main 병합·충돌 해소

## Status

Accepted

## Context (왜)

- PR #73(첫날 5/31 저녁을 기온 야사카 야경 + 가모강 산책 코스로 교체)이 분기된 뒤, main에 #71(발음 표시·장문 구조화·장소 레지스트리 검사 K/L 도입)과 #74(저녁 식당 사전 넷예약 — 大鵬 5/31 19:00·まんざら亭 6/1)가 머지되어 `data/itinerary.json`·`docs/kyoto-itinerary-may31-jun3-2026.md`에서 충돌(`mergeable_state: dirty`).
- 핵심 충돌은 "5/31 저녁을 무엇으로 둘지": PR은 기온 야사카 원정(교토가츠규 → 야경 → 가모강), main #74는 시오 도보권 大鵬을 5/31 19:00 4인 넷예약으로 확정.
- 사용자 결정(2026-05-30): "교토가츠규는 예약 안 하고, 식당은 별도 세션에서 enen으로 바꾸는 새 PR을 올리는 중. 이 PR엔 야경 코스를 반영." → 5/31 저녁은 **야경 코스 유지**, 식당 교체는 별도 PR 범위.
- PR이 #71(검사 K/L) 도입 전 브랜치라, PR의 새 항목들이 산문 필드에 레지스트리 장소명(니조역·교토역·산인본선·기온·아라시야마·기온시조)을 '생으로' 담고 있어 병합 후 검사 K가 차단.

## Decision (무엇)

- 충돌 두 파일 모두 **HEAD(PR 야경 코스)를 채택**하고 main의 5/31 大鵬 단일 저녁 재구조화는 버린다(大鵬은 PR note의 폴백으로 보존).
- 17:45 체크인 note는 main의 장소 참조 표기(`{{kyoto_station}}`·`{{sanin_line}}`·`{{nijo_station}}`)와 PR의 "짐 풀고 기온 야경 원정" 의미를 **병합**.
- 검사 K 통과를 위해 day1 산문 필드의 생 장소명을 레지스트리 참조로 정규화: 니조역→`{{nijo_station}}`, 교토역→`{{kyoto_station}}`, 시오→`{{shio_machiya}}`, 기온→`{{gion}}`, 아라시야마→`{{arashiyama}}`, 기온시조역→`{{gion_shijo_stop}}역`.
- `tests/test_build_index.py` 2건 갱신:
  - `test_long_food_note_folded_but_rating_kept`: 大鵬 day-item이 사라져 fold 회귀 대상을 6/1 まんざら亭로 이동 — 실제 렌더 출력에 맞춰 단언을 `130년 된 교마치야(전통 목조 가옥)</summary>`·`1인당 ¥6,000~8,000`로 정정.
  - `test_verified_source_shows_tick`: main에서 유일하게 `source_verified_at`를 갖던 5/31 大鵬 leg을 야경 코스(researched_market_rate·미검증)로 교체하면서 day-item 전제가 깨짐. 검증 ✓는 production 산출물에 여전히 `trip.transit_pass_sources`(4개 검증 출처)로 렌더되므로, 전제를 day-item + `trip.transit_pass_sources`까지 넓혀 산출물 정합을 그대로 가드.
- 채택하지 않은 대안: ① 야경 leg에 `source_verified_at` 부여(Playwright 미검증이라 출처 정직성 위반) ② 大鵬 day-item 유지(사용자 결정과 배치).

## Consequences (그래서)

- 긍정: PR #73 충돌 해소(`dirty`→머지 가능). 야경 코스가 main의 레지스트리·구조화 스키마와 정합(검사 K/L·G/I 0 error). 검증 ✓ 가드는 출처 위치를 정직하게 반영해 유지.
- 부정·트레이드오프: 5/31 저녁 식당(교토가츠규)은 별도 enen PR로 다시 바뀔 예정이라 본 머지는 잠정. booking-checklist의 大鵬 5/31 예약 항목은 이 PR 범위 밖(enen PR에서 정리).
- 후속 행동: enen 식당 교체 PR(별도 세션). 야경 leg의 Playwright 도달성 검증은 추후 세션.
- 영향 받은 파일: `data/itinerary.json`, `docs/kyoto-itinerary-may31-jun3-2026.md`, `tests/test_build_index.py`.
