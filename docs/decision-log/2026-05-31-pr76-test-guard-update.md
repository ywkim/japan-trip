# 2026-05-31 — PR #76 머지 차단 해소: 6/1 동선 재구성에 맞춰 빌드 회귀 가드 갱신

## Status

Accepted

## Context (왜)

- PR #76("6/1 둘째날 오후 재구성: 한낮 휴식 + 은각사·철학의 길 + 길 위 카페")이 `mergeable_state: blocked`로 머지되지 않음. GitHub 체크에서 `validate` 잡이 **failure**, Vercel·auto-review는 success.
- 원인 분석(2026-05-31): `validate` 잡은 `build_index → unittest → validate.py → score → budget` 순으로 도는데, `validate.py` 자체는 통과하나 **`tests/test_build_index.py`의 프로덕션 회귀 가드 3건이 실패**.
  - `test_multistep_leg_totals_match_sourced_aggregate` — 기대 leg `("2026-06-01","금각사",38,460)`이 6/1 코스에서 금각사가 제거되며 사라짐(`steps` 0개).
  - `test_production_fromto_annotated_in_itinerary` — 기대 병기 `아라시야마텐류지마에(嵐山天龍寺前)→야마고에나카마치(山越中町)`가 삭제된 텐류지→금각사 버스 환승점이라 렌더 HTML에 부재.
  - `test_production_transfer_and_advisory_rendered` — 기대 advisory `"놓치면 택시 22분 대안"`이 삭제된 금각사 leg의 문자열이라 부재.
- 즉 PR #76이 `data/itinerary.json`의 6/1 동선을 바꾸면서, 옛 동선을 하드코딩으로 단언하던 빌드 회귀 가드를 함께 갱신하지 않아 CI가 막힘(CLAUDE.md TDD 규칙: 데이터가 테스트 단언 대상이면 테스트도 같이 갱신).

## Decision (무엇)

- PR #76 변경분을 본 브랜치(`claude/pr-76-merge-issue-adxqd`)에 병합한 뒤, 세 회귀 가드를 **새 6/1 동선의 실제 데이터에 맞게 갱신**한다.
  - `test_multistep_leg_totals_match_sourced_aggregate`: 금각사 기대를 새 2-스텝 leg `("2026-06-01","철학의 길",23,260)`(니조→케아게 지하철 도자이선 ¥260 + 케아게→난젠지 도보)로 교체. 후시미이나리(JR 통표 ¥200·20분) 기대는 유지.
  - `test_production_fromto_annotated_in_itinerary`: 삭제된 `아라시야마텐류지마에→야마고에나카마치` 튜플을 새 지하철 leg `니조역(二条駅)→케아게역(蹴上駅)`으로 교체. 나머지 두 튜플(니조→교토역, 교토역→이나리역)은 6/2 동선이라 유지.
  - `test_production_transfer_and_advisory_rendered`: 사라진 `"놓치면 택시 22분 대안"` 단언을 새 폰토초 복귀 leg의 advisory `"먼저 오는 차 탑승"`(시버스 17/203)으로 교체. '환승' 태그·`tl-dot transfer` 단언은 후시미 JR 통표 환승이 여전히 렌더하므로 유지.
- 대안 "금각사 기대를 그냥 삭제"는 회귀 가드 커버리지가 줄어 채택하지 않음 — 동등한 새 2-스텝 leg로 교체해 가드 수를 보존.

## Consequences (그래서)

- 긍정: PR #76의 6/1 재구성이 빌드 회귀 가드와 정합하게 되어 `validate` 잡이 녹색이 되고 머지 차단이 해소됨. 가드는 옛 동선이 아닌 현재 동선을 검증.
- 부정·트레이드오프: 옛 금각사 leg의 "버스 2회 요금 합산(¥230×2)" 검증 케이스가 사라짐 — 새 동선에 이중 유료 환승 leg가 없어 불가피(후시미 JR 통표 케이스가 합산 검증을 계속 담당).
- 후속 행동: 향후 일정 변경 시 `data/itinerary.json`과 `tests/test_build_index.py`의 프로덕션 가드를 동시에 갱신(TDD 규칙 재확인).
- 영향 받은 파일: `tests/test_build_index.py`(가드 3건), 병합으로 들어온 `data/itinerary.json`·`docs/kyoto-itinerary-may31-jun3-2026.md`·`docs/decision-log/2026-05-30-03-...md`.
