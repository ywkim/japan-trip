# 2026-05-11 — index.html 모바일 페이지 소연 리뷰 후속 (PR #9 follow-up)

- 트리거: PR #9 머지 후 소연 리뷰 — 예산 표기·stale 날짜·코드 정리·링크 호환 항목.
- 산출물:
  - `index.html` 갱신 — 예산 옵션 표기에 3M 하드캡 정책 맥락 추가("3M 옵션 실패 → 5M 적용"), stale 일자 문구 제거, body margin 중복 통합, 카드 블록 위 `SYNC:` 주석으로 동기화 출처 명시, `.md` 링크는 GitHub blob URL로 변경(Pages에서 raw md 렌더 안 됨 대응).
- 변경:
  - PR #8(decision-log 디렉토리 분할) 머지에 맞춰 본 일지를 신규 파일(`docs/decision-log/2026-05-11-index-mobile-review.md`)로 기록. `index.html` footer는 main에서 이미 `docs/decision-log.md` 표기가 사라졌으므로 본 PR에서 별도 링크 갱신 없음.
- 핵심 관찰:
  - PR #5 머지(3M 하드캡) 이후 모바일 페이지의 "5M 내 수렴" 표기가 정책과 충돌하는 것처럼 보였음 → 충돌이 아니라 "3M 통과 실패 시 5M 옵션 적용" 맥락이 누락된 것. 본문에 명시해 오해 차단.
  - `index.html`에 인라인 하드코딩된 점수·비용·일정 블록은 충돌·동기화 위험. 본 PR은 SYNC 주석으로 추적성만 확보 — 인라인 JSON 렌더 패턴 도입은 별도 PR.
- 보류:
  - GitHub Pages 활성화는 자동 불가 — 사용자가 Settings → Pages에서 직접 활성화 필요.
- 다음 단계:
  - 영욱·소연: 모바일에서 갱신된 `index.html` 확인.
  - Pages 활성화 의사 결정.
