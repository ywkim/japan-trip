# 2026-05-26 — Vercel 산출물에서 GitHub 링크 제거 + CI 가드

## Status

Accepted (이전 정책 Superseded: "외부 문서 링크는 GitHub blob URL 사용")

## Context (왜)

- 본 레포는 Vercel(`nihon-trip.vercel.app`)로 호스팅되며, 메인·일정·예약·아카이브 페이지를 가족(시부모 포함)과 공유한다.
- 기존 정책은 외부 문서를 GitHub blob URL(`https://github.com/ywkim/japan-trip/blob/main/...`)로 링크했다. 사유는 Vercel이 `.md`를 렌더하지 않고 raw text로 서빙해 상대 경로가 깨진다는 것.
- 그 결과 산출물 곳곳(메인 footer 최종 보고서, 아카이브 footer 보고서·결정 일지, 아카이브 점수 카드 결정 일지, 일정 "마크다운", 예약 탭 "리서치 상세" 버튼 4개 + note 내 인라인 URL)에 GitHub 링크가 노출됐다.
- 가족 공유 페이지에서 링크를 누르면 운영용 화면이 아니라 소스 레포(코드·미렌더 마크다운)로 빠져나가, 받는 사람에게 혼란을 주고 레포 내부를 불필요하게 노출한다.
- 사용자 지시: "Vercel 화면에서 GitHub 링크 금지." 후속 합의: 텍스트로 남기되 사이트 내 HTML 페이지가 있으면 그쪽으로 연결, CLAUDE.md 정책도 갱신.

## Decision (무엇)

- Vercel이 서빙하는 HTML 6종(`index.html` + `viz/*.html`)에서 모든 GitHub 링크를 제거한다.
  - `scripts/build_index.py`: `GH_BLOB` 상수와 그 사용처 4곳(메인 footer·아카이브 footer·아카이브 점수 카드·일정 마크다운 링크)을 삭제. 사이트 내 HTML 페이지(`viz/archive.html`)로 연결되는 링크는 유지하고, 그 외는 일반 텍스트로 레포 경로(`reports/`, `docs/decision-log/`)만 표기.
  - `data/booking-checklist.json`: GitHub를 가리키던 `link`(리서치 상세 버튼) 4개 제거, `note` 내 인라인 GitHub URL을 일반 텍스트 레포 경로(`docs/...`)로 치환.
- `scripts/validate.py`에 **검사 J** 신설: Vercel 산출물 HTML에 `github.com` 문자열(링크·raw URL 모두)이 남으면 CI 차단. 미래에 GitHub 링크가 다시 새어 들어오는 것을 방지.
- 검토했으나 채택하지 않은 대안:
  - *렌더 레이어에서 GitHub 링크만 정규식으로 스트립*: 데이터에 URL이 그대로 남아 `github.com` raw 텍스트가 산출물에 노출 → 검사 J가 잡으므로 무의미. 데이터에서 제거하는 편이 단일 출처 정합에 맞음.
  - *CI 가드 없이 링크만 제거*: 미래 PR에서 재유입을 막지 못함. 본 레포의 검증 문화(B~I)와 불일치.

## Consequences (그래서)

- 긍정: 가족 공유 페이지가 운영 화면 안에서 닫힌다. 받는 사람이 소스 레포로 이탈하지 않는다. 검사 J가 회귀를 자동 차단.
- 부정·트레이드오프: 최종 보고서·결정 일지·리서치 상세 문서로 가는 클릭 동선이 사라진다. 이 문서들은 사이트 내 렌더본이 없어 텍스트 경로(레포 위치)로만 안내한다. 운영자(개발자)는 레포에서 직접 열어야 한다.
- 후속 행동: 향후 외부 문서를 산출물에서 참조할 땐 ① 사이트 내 HTML 페이지로 연결하거나 ② 일반 텍스트 경로로 표기. GitHub blob URL은 금지.
- 영향 받은 파일: `scripts/build_index.py`, `scripts/validate.py`, `data/booking-checklist.json`, 빌드 산출물 6 HTML(재생성), `tests/test_validate.py`(검사 J 테스트), `tests/test_build_index.py`(note linkify 가드 격리화), `CLAUDE.md`, `README.md`.

## Test plan

- [x] `python -m unittest discover tests` — 107 통과 (검사 J 신규 테스트 3건 + 기존 linkify 가드 격리 후 통과)
- [x] `python scripts/validate.py` — 0 errors (검사 J 포함)
- [x] `python scripts/build_index.py --check` — drift 없음
- [x] `grep github.com index.html viz/*.html` — 매치 없음
