# 2026-06-02 — 회전초밥 비교 페이지 이미지·링크·메뉴 가격 보강

## Status

Accepted

## Context (왜)

- `2026-06-02-09`에서 만든 `docs/kyoto-station-kaiten-sushi-translation.md`가 다른 비교 페이지(말차 디저트·쇼핑 가이드)에 비해 이미지·인라인 링크·메뉴 가격이 없다는 사용자 지적.
- 쇼핑 가이드(`isetan-porta-shopping-translation.md`)는 각 시설 섹션 상단에 Wikimedia Commons 이미지 + 시설별 가격 표 + 출처 링크를 갖춤; 회전초밥 페이지는 이 세 요소 모두 부재.

## Decision (무엇)

- **이미지 2장 추가**: Wikimedia Commons CC BY-SA 4.0 이미지
  - 大起水産 섹션: 교토타워 주변 전경(2019, Another Believer) — KYOTO TOWER SANDO가 탑 기슭에 위치함을 시각화
  - 寿しのむさし 섹션: 교토역 하치조구치 입구(Hide1228) — ASTY 상업 시설 구역
  - `scripts/fetch_assets.py`로 자가호스팅 (`220c9476a703b275.jpg`·`9c5d31bad1adcec5.jpg`)
- **인라인 링크 추가**: 비교 표의 타베로그 점수를 클릭 가능 링크로, 각 섹션 상단에 공식·타베로그·방문기 링크, 권장 섹션의 타베로그 점수도 링크화
- **메뉴 가격 표 추가**: 공식 그랜드메뉴(`sushi.daiki-suisan.co.jp/grandmenu/`)·공식 홈페이지(`sushinomusashi.com`) 실시간 조회
  - 大起水産: 접시별 가격 체계 ¥110~¥649 + 카이센동 ¥980 + 세트류
  - 寿しのむさし: 7단계 접시 색깔 가격제 ¥161(表準)~¥977(朱金の鶴)
- **영업 시간 수정**: 이전 11:00~22:00 → 공식 11:00~23:00 (L.O. 22:30)로 정정

## Consequences (그래서)

- 긍정: 가족이 현장에서 가격대·메뉴를 직접 확인할 수 있어 의사결정 지원 강화; 다른 비교 페이지와 패턴 일관.
- 부정·트레이드오프: 메뉴 가격은 공식 그랜드메뉴 기준이나 교토타워산도 지점의 지점별 차이 가능성 있음(주석 없음).
- 영향 받은 파일: `docs/kyoto-station-kaiten-sushi-translation.md`(이미지·링크·메뉴 표), `data/local-image-map.json`(+2개), `assets/place-images/`(+2장)

## Test plan

- [x] `validate.py` 0 errors
- [x] `build_index.py --check` 재현성 통과
- [x] `unittest` 223/223 PASS
