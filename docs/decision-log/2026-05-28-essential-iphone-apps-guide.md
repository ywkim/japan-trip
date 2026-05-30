# 2026-05-28 — 필수 아이폰 앱 가이드 문서 작성 및 체크리스트 추가

## Status

Accepted

## Context

- **시간**: 출국까지 3일 (2026-05-31 KIX 출발)
- **발견**: 기존 ICOCA 아이폰 셋업 가이드(`docs/icoca-iphone-setup.md`)는 교통 카드 설정만 다루고, Google Maps·Tabelog·번역·Trip.com 등 여행 필수 앱은 따로 정리되지 않음
- **문제**: 시부모 4인의 앱 설치·사용법을 현지(5/31~6/3)에서 배우기에는 시간이 부족. 특히:
  - 시부모가 길 찾기(Google Maps)를 스스로 할 수 있어야 함
  - 메뉴판 번역(Papago)은 영욱·소연이 옆에서 보일 수 없는 경우도 발생
  - 호텔 예약번호 확인(Trip.com) 등 예약 정보는 미리 숙지 필수
- **근거**: CLAUDE.md의 "메타 문서를 갱신하는 경우" — 신규 산출물 추가 시 일지화 의무

## Decision

1. **필수 아이폰 앱 종합 가이드 신규 작성** (`docs/essential-iphone-apps.md`)
   - ICOCA 외 4개 앱(Google Maps, Tabelog, Papago, Trip.com)의 사전 설치·설정 방법
   - 현지 사용 흐름도
   - 4인 공통 + 영욱·소연 운영자 + 시부모 추가 체크리스트
   - 각 앱의 오프라인 기능(지도·번역팩) 사전 다운로드 강조

2. **체크리스트에 "앱 설치" 항목 추가** (`data/booking-checklist.json`)
   - `id: "iphone_apps"`, `due_date: "2026-05-30"`
   - 링크: `docs/essential-iphone-apps.md` (가이드 문서 참조)
   - 상태: "미정" (출국 전 설치 진행 중)

3. **불채택 대안**
   - ❌ ICOCA 문서에 통합: 교통 이상 범위가 넓어지면 문서 길이 과도 → 별도 문서 유지
   - ❌ 앱별 분리 가이드: 가족이 따라할 통합 단계가 필요 → 1개 문서로 통합

## Consequences

### 긍정
- 시부모가 출국 전 앱 설치·기본 기능(Google Maps 길 찾기, Papago 번역)을 미리 숙련 → 현지 운영 부담 감소
- 영욱·소연이 "5/30까지 4인 모두 설치 확인" 체크리스트로 관리 가능
- 사이트 내 HTML 렌더(GitHub 링크 금지 규칙 준수) → 가족 공유 페이지에서 모바일·원클릭 접근

### 후속 행동
- `python scripts/build_index.py` 실행 → `viz/checklist.html`(예약 탭) 자동 갱신
- PR 리뷰: `data/booking-checklist.json` 형식 검사 (필드명·링크 경로), `validate.py` (D: SYNC 주석, J: GitHub 링크 금지) 통과 확인

### 영향 받은 파일
- **신규**: `docs/essential-iphone-apps.md` (786줄)
- **수정**: `data/booking-checklist.json` (items[] 추가 1개)
- **자동 생성**: `viz/checklist.html` (build_index.py 재실행 시 갱신, gitignore)

## 참고

- 기존 ICOCA 가이드와의 연계: `docs/essential-iphone-apps.md` §1.1에서 ICOCA 세부 절차는 `docs/icoca-iphone-setup.md`로 참조 시킴
- 소연 저장 목록 활용: Google Maps §1.2에서 `docs/soyeon-maps-list.md` 언급
- 기기·iOS 버전 사전 확인: `docs/icoca-iphone-setup.md` §1.2의 시부모 미확인 사항과 연계
