# 의사결정 일지

여행 결정 과정에서의 합의·보류·변경 사항을 시간순으로 기록.

## 파일 규칙

- **항목 1개 = 파일 1개.** 같은 파일에 여러 PR이 append하지 않는다 (충돌 폭발 방지).
- 파일명: `YYYY-MM-DD-slug.md`
  - 예: `2026-05-09-kyoto-itinerary.md`
  - 같은 날 여러 항목이면 `slug` 알파벳 순으로 정렬됨. 강한 순서가 필요하면 `YYYY-MM-DD-NN-slug.md`로 NN 부여.
- **새 PR은 이 디렉토리에 새 파일만 추가**. 다른 일지 파일을 편집하지 않는다.
- 디렉토리 자체가 인덱스. 별도 인덱스 파일을 두지 않는다 (인덱스도 append 충돌의 원인).

## 항목 형식 — ADR(Nygard)

2026-05-20 이후 신규 일지는 **ADR(Architecture Decision Record, Nygard 2011) 5섹션** 형식. 정본 정의는 `CLAUDE.md` "ADR(Nygard) 형식 — decision-log 항목·PR 본문 (필수)" 절. 본 README는 운영 메모로 템플릿만 재게시.

```markdown
# YYYY-MM-DD — 한 줄 명사구 (Title)

## Status

Accepted | Proposed | Deprecated | Superseded by `<YYYY-MM-DD-slug.md>`

## Context (왜)

- 이 결정을 강제한 힘·문제·제약 (사실 위주)
- 시점·환경·외부 사건 (예: 채팅 업로드, 가격 변동, 사용자 지시)
- 알려진 대안과 그 한계 (필요 시)

## Decision (무엇)

- 능동태로 명시한 채택 행동 1개
- 채택하지 않은 대안은 한 줄씩 사유와 함께 (선택)

## Consequences (그래서)

- 긍정 영향
- 부정·트레이드오프
- 후속 행동·별도 PR 필요 항목
- 영향 받은 파일·데이터 (해당 시)
```

기존 일지(2026-05-20 이전 + 같은 날 `2026-05-20-kakaotalk-sync-kadensho-booking.md`)는 시점 스냅샷으로 **보존하며 retroactive 변환 금지**. 자세한 cutover 규칙은 CLAUDE.md 참조.

## 조회

```bash
ls docs/decision-log/         # 파일명 = 날짜순
```

또는 GitHub 웹에서 디렉토리 열기.
