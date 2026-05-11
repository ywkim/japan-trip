# 2026-05-11 — auto-request-review config 스키마 수정

## 주제

`necojackarc/auto-request-review@v0.13.0` 액션이 모든 PR에서 리뷰어를 자동 할당하지 못하는 문제.

## 산출물

- `.github/auto_request_review.yml` 재작성

## 핵심 관찰

1. 도입 이후 분기된 PR(#11)에서도 워크플로우 로그가 `Matched no reviewers / No default reviewers are matched / terminating the process`로 종료됨. 즉 "도입 이전 분기" 가설로는 설명 불가.
2. v0.13.0 README 확인 결과 표준 스키마는 `files:`가 **매핑**(키=glob, 값=이름 리스트)이며, 최상위 `reviewers:` 키 아래 `defaults / groups / per_author`를 둠.
3. 기존 config는 `files:`를 리스트로 시작(`- '**':`)하고 값에 `reviewers:`/`required: 1` 객체를 중첩 → 액션이 어떤 glob도 매칭 키로 추출하지 못함. `reviewers.defaults`도 없어 fallback 실패.
4. 그동안 PR의 `reviewRequests`에 상대방이 들어 있던 것은 영욱님이 GitHub UI에서 수동 추가한 것 (`review_requested` 이벤트 actor = ywkim).

## 합의

- 스키마를 표준 형식으로 교체.
- `files: '**'` + `reviewers.defaults` 양쪽에 두 사람 등록 → 액션이 작성자를 자동 제외하므로 상대방만 할당됨.
- `required: 1` 같은 강제 승인 수는 액션 기능이 아니라 GitHub 브랜치 보호 규칙에서 별도 설정 (기존 주석 그대로 유지).

## 보류

- 기존 열린 PR(#6, #11, #12)의 head 브랜치에는 여전히 broken config가 들어 있음. 액션은 `pull_request.head.ref`에서 config를 fetch하므로 main만 고친다고 즉시 회복되지 않음 → 각 PR을 main으로 sync/rebase 해야 새 config가 head에 반영됨.
- PR #12는 워크플로우 실행 기록 자체가 0건이라 트리거 누락 원인이 별도로 존재할 가능성. 이번 수정 머지 후에도 미발화 시 별도 조사.

## 다음 단계

1. 이 PR을 main에 머지 (이 PR 자체는 자동 할당이 안 되므로 수동 지정).
2. 기존 열린 PR들의 head를 main으로 sync → 새 PR이나 sync 이벤트에서 액션이 정상 매칭하는지 확인.
3. 정상 매칭 확인 후 GitHub 브랜치 보호 규칙에서 "Require at least 1 approval" 설정 점검.
