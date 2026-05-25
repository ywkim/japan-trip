# 후속 세션 위임 — itinerary tbd_needs_browser_mcp 8 leg 측정 (Playwright MCP)

> 이 문서는 **자기완결**입니다. 본 레포 `CLAUDE.md`만 읽으면 작업을 시작할 수 있습니다.
> 다른 대화 컨텍스트·세션 메모리 의존 없음.

## 1. 작업 목적

PR #29(`feat(itinerary): 장소 간 이동 출처·신뢰도 라벨링 + 검사 G`)에서 `data/itinerary.json`의 일부 inter-item 이동 leg는 WebFetch가 Google Maps Directions의 JS 렌더를 처리하지 못해 `data_quality: tbd_needs_browser_mcp`로 표기되었다. 본 작업은 **Playwright MCP가 활성화된 Claude Code 세션**에서 해당 URL을 직접 열어 분·거리·노선을 측정하고 라벨을 `researched_market_rate`로 승격하는 것이다.

## 2. 사전 요구사항

- 본 레포(`japan-trip`) 작업 트리.
- **Playwright MCP** 설정 완료 (`/mcp` 명령으로 활성 확인). MCP 도구로 `browser_navigate`, `browser_snapshot`, `browser_click` 등이 사용 가능해야 함.
- Python 3 (CI 동일).

## 3. 처리 대상 (8 leg)

`data/itinerary.json`을 grep해 `"data_quality": "tbd_needs_browser_mcp"`로 찾을 수 있다. 각 leg의 `arrive_from.source`에 측정할 Google Maps URL이 박혀있다.

| # | 일자 | 출발 → 도착 | 현재 `route` 추정 | 측정 URL (source 필드) |
|---|---|---|---|---|
| 1 | 5/31 | 시오 마치야 → 키요미즈데라 | `市バス 206 (교토역前→五条坂) + 도보 10분` | `…/maps/dir/Kyoto+Station/Kiyomizu-dera` |
| 2 | 5/31 | 기온 → 가와라마치/폰토초 | `기온 → 시조대교 → 폰토초·가와라마치 (가모강 도보)` | `…/maps/dir/Gion/Pontocho` |
| 3 | 6/1 | 죽림길 → 텐류지 | `죽림길 남문 → 텐류지 북문 (인접)` | `…/maps/dir/Arashiyama+Bamboo+Grove/Tenryu-ji` |
| 4 | 6/1 | 텐류지 → 시그라쿠 토후 | `텐류지 정문 → 시그라쿠 토후 (아라시야마 본거리)` | `…/maps/dir/Tenryu-ji/Shoraku+Tofu` |
| 5 | 6/1 | 시그라쿠 토후 → 금각사 | `市バス 11 또는 택시 (天龍寺前 → 金閣寺道). 11번 약 40분` | 교토시 교통국 노선검색 URL (재측정 권장) |
| 6 | 6/1 | 료안지 → 가와라마치/니시키 | `市バス 59 (竜安寺前 → 四条河原町)` | 교토시 교통국 노선도 URL |
| 7 | 6/2 | 시오 → 후시미이나리 | `지하철 도자이선 → 가라스마선 → JR 나라선. 또는 택시 15분` | 교토시 교통국 경로검색 URL |
| 8 | 5/31 | 시오 → 키요미즈 같은 경우 ② (위 1번과 동일 라인 — 패스) | — | — |
| 9 | 5/31 | 시오 마치야 → 니조성 외정원 | `시오 → 니조성 동대수문 (堀川通 경유 700m, walk)` | `…/maps/dir/Shio+Machiya+Kyoto/Nijo+Castle` |
| 10 | 5/31 | 니조성 → 니조 인근 점심 | `니조성 → 시오 도보권 식당 (500m 내, walk)` | `…/maps/search/restaurants+near+Shio+Machiya+Kyoto` |
| 11 | 5/31 | 야사카 신사 → 철학의 길 남단 | `야사카 → 난젠지 정문 → 철학의 길 남단 (1.2km, walk)` | `…/maps/dir/Yasaka+Shrine/Philosopher's+Path+Kyoto` |
| 12 | 5/31 | 철학의 길 남단 → 가와라마치 | `市バス 46 또는 201 → 四条河原町 (도보 1km + 버스 15분, bus)` | `…/maps/dir/Philosopher's+Path+Kyoto/Kawaramachi` |

> 실제 leg는 본 표 기준 11개 (#1~7, #9~12). #8은 중복 표기로 패스. 정확한 위치는 grep으로 확인.

### 정확한 위치 grep

```bash
python -c "
import json, pathlib
data = json.loads(pathlib.Path('data/itinerary.json').read_text(encoding='utf-8'))
for d in data['days']:
    for i, it in enumerate(d['items']):
        af = it.get('arrive_from')
        if af and af.get('data_quality') == 'tbd_needs_browser_mcp':
            print(f\"{d['date']} items[{i}] '{it['title']}'  ← {af.get('route','')}\")
            print(f\"  source: {af.get('source','')}\")
"
```

## 4. 측정 절차 (leg 1개당)

1. **Playwright MCP로 URL 열기** — `source` 필드의 Google Maps Directions URL 또는 교토시 교통국 노선검색 URL.
2. **출발지/도착지 입력 확인** — URL의 `dir/A/B`가 의도한 두 장소인지 확인. 잘못됐으면 화면에서 다시 검색.
3. **이동 수단별 측정** — 도보(🚶), 대중교통(🚆/🚌) 모두 비교. itinerary의 현재 `mode`를 따르되, 더 합리적인 모드가 있으면 변경 + 비고로 기록.
4. **값 채취**:
   - `duration_min`: Maps에 표시되는 분.
   - `distance_km`: Maps에 표시되는 km (소수점 1자리).
   - `route`: 노선·정거장명을 자국어 표기 그대로 (예: `市バス 59 (竜安寺前→四条河原町)`). 도보면 경로 요약.
5. **출처 URL 갱신** — Maps의 영구 링크(URL 박스 그대로)로 source 갱신. `source_fetched_at`을 작업 당일로.
6. **라벨 승격** — `data_quality`를 `tbd_needs_browser_mcp` → `researched_market_rate`. 공식 운임 페이지(JR/교토 시영)에서 확인하면 `official_fare`로.

## 5. data/itinerary.json 편집 예시

before:
```json
"arrive_from": {
  "mode": "bus",
  "duration_min": 35,
  "distance_km": 5.5,
  "route": "市バス 206 (교토역前→五条坂) + 도보 10분",
  "source": "https://www.google.com/maps/dir/Kyoto+Station/Kiyomizu-dera",
  "source_fetched_at": "2026-05-17",
  "data_quality": "tbd_needs_browser_mcp"
}
```

after (예시):
```json
"arrive_from": {
  "mode": "bus",
  "duration_min": 28,
  "distance_km": 4.2,
  "route": "市バス 206 (京都駅前 → 五条坂) 18분 · 五条坂 정류장 → 도보 10분",
  "source": "https://www.google.com/maps/dir/Kyoto+Station/Kiyomizu-dera/@…",
  "source_fetched_at": "2026-XX-XX",
  "data_quality": "researched_market_rate"
}
```

## 6. 검증 (작업 후 반드시 실행)

```bash
python scripts/build_index.py          # 산출물 재생성
python scripts/build_index.py --check  # drift 0 확인
python scripts/validate.py             # 검사 G 포함 0 errors 기대
python -m unittest discover -s tests   # 40개 그린 유지
python scripts/score.py > /dev/null    # exit 0
python scripts/budget.py > /dev/null   # exit 0
```

**주의 사항**:

- `walking_km` 정합성 검사(G): 한 일자의 mode=walk leg distance_km 합이 declared `walking_km` + 2km을 초과하면 fail. 도보 leg를 크게 늘리면 `days[].walking_km`도 같이 올려야 한다.
- `source_fetched_at` 60일 staleness 검사: 작업 당일 날짜로 갱신하면 자동 통과.

## 7. 사람용 마크다운 사본 동기화

`docs/kyoto-itinerary-may31-jun3-2026.md`의 해당 일자 표·메모를 새 값으로 갱신. 본 PR(#29)에서는 핵심 3 leg만 동기화됐고 나머지는 정성 표현 그대로일 수 있음. arrive_from 값과 줄을 맞춰서 갱신.

## 8. 결정 일지 신설 (메타 문서화 규칙)

`docs/decision-log/`에 새 파일 추가 — 예: `docs/decision-log/YYYY-MM-DD-transit-mcp-measurements.md`.

템플릿:

```markdown
# YYYY-MM-DD — Playwright MCP transit 측정 결과

## 트리거

PR #29에서 남긴 tbd_needs_browser_mcp 8 leg를 Playwright MCP 세션에서 측정.
인계 문서: `docs/transit-mcp-handoff.md`.

## 산출물

- `data/itinerary.json` — N개 leg의 arrive_from 라벨 `tbd_needs_browser_mcp`
  → `researched_market_rate` 승격
- 도보 거리 변경 반영해 days[].walking_km 미세 조정 (필요 시)
- `docs/kyoto-itinerary-may31-jun3-2026.md` 동기화
- index.html·viz/itinerary.html 빌드 산출물 갱신

## 측정 표

| 일자 | 구간 | mode | duration_min | distance_km | route |
|---|---|---|---|---|---|
| ... |

## 핵심 관찰

- 3~5줄. 예상보다 빠른/느린 구간, 노선 변경 등.

## 다음 단계

- (있으면) 남은 tbd leg, 운임 추가 리서치 등.
```

## 9. 커밋·PR

- 본 PR(#29)이 머지된 후 별도 PR로 진행: `claude/transit-mcp-measurements` 등의 브랜치명.
- 커밋 메시지 예: `data(itinerary): Playwright MCP transit 측정 — tbd 7 leg 승격`
- PR 본문: 측정 결과 표 + 변경 전후 비교 + Test plan 체크박스.

## 10. 후속 추가 위임 (선택)

- 교토 시버스/지하철 **운임**도 `data/itinerary.json` arrive_from에 `fare_yen` 필드로 추가하는 스키마 확장 — 별도 PR.
- `validate.py` 검사 H 신설: itinerary.json ↔ kyoto-itinerary-may31-jun3-2026.md 본문 동기화(검사 E/F 동급) — 본 PR(#29)에서 의도적으로 제외된 항목.
