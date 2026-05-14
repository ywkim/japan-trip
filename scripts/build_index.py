#!/usr/bin/env python3
"""index.html + viz/itinerary.html + viz/checklist.html 빌드.

data/decision.json·data/cost-options.json·data/weather.json·data/itinerary.json
·data/booking-checklist.json을 읽고 scripts/score.py·scripts/budget.py를
--json으로 호출해 인라인 데이터로 3개 정적 HTML을 생성한다. 모든 산출물은
"브라우저 더블클릭 동작"을 위해 외부 fetch 없음.

용법:
  python scripts/build_index.py            # 3개 파일 갱신
  python scripts/build_index.py --check    # 빌드 결과와 디스크 diff (CI용, exit 1 if drift)
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SCRIPTS = BASE / "scripts"
DATA = BASE / "data"
DOCS = BASE / "docs"
OUT_INDEX = BASE / "index.html"
OUT_ITINERARY = BASE / "viz" / "itinerary.html"
OUT_CHECKLIST = BASE / "viz" / "checklist.html"

GH_BLOB = "https://github.com/ywkim/japan-trip/blob/main"
SCENARIO_ID = "kyoto_may31_kadensho_early_bird"


def esc(s) -> str:
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def won(n: int) -> str:
    return f"₩{n:,}"


def maps_link(query: str, label: str) -> str:
    q = esc(query.replace(" ", "+"))
    return f'<a href="https://maps.google.com/?q={q}" target="_blank" rel="noopener">{esc(label)}</a>'


def run_json(script: str) -> dict:
    res = subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--json"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(res.stdout)


def load_data():
    return {
        "decision": json.loads((DATA / "decision.json").read_text(encoding="utf-8")),
        "cost": json.loads((DATA / "cost-options.json").read_text(encoding="utf-8")),
        "weather": json.loads((DATA / "weather.json").read_text(encoding="utf-8")),
        "itinerary": json.loads((DATA / "itinerary.json").read_text(encoding="utf-8")),
        "checklist": json.loads((DATA / "booking-checklist.json").read_text(encoding="utf-8")),
        "score": run_json("score.py"),
        "budget": run_json("budget.py"),
    }


# ─── 공통 스타일 ───────────────────────────────────────────────────────────

CSS = """
  :root {
    --bg: #fafafa; --fg: #222; --muted: #666; --border: #ddd;
    --accent: #d33; --card: #fff; --subcard: #fafafa;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1a1a1a; --fg: #eee; --muted: #999; --border: #333;
      --accent: #ff6464; --card: #232323; --subcard: #1e1e1e;
    }
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "AppleGothic", sans-serif;
    background: var(--bg); color: var(--fg);
    margin: 0 auto; padding: 1rem; max-width: 640px;
    line-height: 1.5; font-size: 16px;
  }
  h1 { font-size: 1.4rem; margin: 0.5rem 0 0.25rem; }
  h2 { font-size: 1rem; margin: 0 0 0.5rem; color: var(--muted); font-weight: 500; }
  .status { color: var(--muted); font-size: 0.85rem; margin-bottom: 1rem; }
  nav { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 1rem 0; }
  nav a {
    padding: 0.4rem 0.7rem; border: 1px solid var(--border); border-radius: 999px;
    text-decoration: none; color: var(--fg); font-size: 0.8rem; background: var(--card);
  }
  nav a:hover { border-color: var(--accent); }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 8px;
    padding: 1rem; margin: 0.75rem 0;
  }
  .subcard {
    background: var(--subcard); border: 1px solid var(--border); border-radius: 6px;
    padding: 0.75rem; margin: 0.5rem 0;
  }
  .subtitle { font-weight: 600; margin-bottom: 0.4rem; font-size: 0.95rem; }
  .big { font-size: 1.6rem; font-weight: 600; line-height: 1.2; }
  .sub { color: var(--muted); font-size: 0.85rem; margin-top: 0.25rem; }
  .row {
    display: flex; justify-content: space-between; gap: 0.5rem;
    padding: 0.35rem 0; border-bottom: 1px solid var(--border);
  }
  .row:last-child { border-bottom: none; }
  .row .k { color: var(--muted); flex-shrink: 0; }
  .row .v { font-variant-numeric: tabular-nums; text-align: right; word-break: keep-all; }
  ul { padding-left: 1.2rem; margin: 0.3rem 0; }
  li { margin: 0.2rem 0; }
  .day { padding: 0.35rem 0; border-bottom: 1px solid var(--border); }
  .day:last-child { border-bottom: none; }
  .day .date { font-size: 0.9rem; }
  .day .date .k { display: inline-block; min-width: 3.2rem; color: var(--muted); }
  .day a { color: var(--fg); text-decoration: underline; text-decoration-color: var(--border); }
  .bar { height: 6px; background: var(--border); border-radius: 3px; margin: 0.2rem 0 0.5rem; overflow: hidden; }
  .bar-fill { height: 100%; background: var(--accent); }
  .links { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.6rem; }
  .links a {
    flex: 1 1 auto; text-align: center; padding: 0.5rem 0.7rem;
    background: transparent; color: var(--fg); border: 1px solid var(--border);
    border-radius: 6px; text-decoration: none; font-size: 0.85rem;
  }
  .links a:hover { border-color: var(--accent); }
  .badge {
    display: inline-block; padding: 0.1rem 0.45rem; border-radius: 4px;
    font-size: 0.75rem; border: 1px solid currentColor;
  }
  footer { color: var(--muted); font-size: 0.75rem; margin-top: 1.5rem; text-align: center; }
"""


def html_doc(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#fafafa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1a1a1a" media="(prefers-color-scheme: dark)">
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


# ─── index.html 섹션 ──────────────────────────────────────────────────────

def card_summary(d) -> str:
    decision = d["decision"]
    score = d["score"]
    budget = d["budget"]
    kyoto = next(c for c in decision["candidates"] if c["id"] == "kyoto")
    kyoto_score = next((s for s in score["scored"] if s["id"] == "kyoto"), None)
    scn = next((s for s in budget["scenarios"] if s["id"] == SCENARIO_ID), None)
    pass_marker = "✅ 통과" if scn and scn["passes_cap"] else f"❌ {won(-scn['headroom_krw'])} 초과" if scn else "—"
    score_str = f"{kyoto_score['score']:.2f} / 10" if kyoto_score else "N/A"
    total_str = won(scn["confirmed_total_krw"]) if scn else "—"

    return f"""
<!-- SYNC: reports/final-report.md §1 (결정 요약) · data/decision.json (companions·점수) · data/cost-options.json (scenario {SCENARIO_ID}) -->
<section id="summary" class="card">
  <h2>요약</h2>
  <div class="big">교토 · 5/31~6/3</div>
  <div class="sub">관서 · 시부모 동반 4인 (확정) · 3박 4일</div>
  <div class="row"><span class="k">시기</span><span class="v">2026-05-31 (일) ~ 06-03 (수)</span></div>
  <div class="row"><span class="k">동반</span><span class="v">영욱·소연 + 시부모 (4인)</span></div>
  <div class="row"><span class="k">숙박</span><span class="v">에어비앤비 2박 + 카덴쇼 료칸 1박 (2명×2실)</span></div>
  <div class="row"><span class="k">예상 비용</span><span class="v">{esc(total_str)}</span></div>
  <div class="row"><span class="k">3M 캡</span><span class="v">{esc(pass_marker)}</span></div>
  <div class="row"><span class="k">종합 점수</span><span class="v">{esc(score_str)}</span></div>
  <div class="sub" style="margin-top:0.5rem;">{esc(kyoto.get('notes', ''))}</div>
</section>
"""


def card_tsuyu(d) -> str:
    weather = d["weather"]
    tn = weather.get("tsuyu_normals", {})
    kyoto = weather["cities"]["kyoto"]
    trip = kyoto.get("trip_window_daily_precip", {})
    sokuhou = tn.get("sokuhou_2026", {})

    daily_rows = []
    for d_key in ("2026-05-31", "2026-06-01", "2026-06-02", "2026-06-03"):
        if d_key in trip:
            mm, dd = d_key[5:7], d_key[8:10]
            label = f"{int(mm)}/{int(dd)}"
            daily_rows.append(f'<div class="row"><span class="k">{esc(label)}</span><span class="v">{trip[d_key]}mm</span></div>')
    trip_total = trip.get("trip_total_mm")
    if trip_total is not None:
        daily_rows.append(f'<div class="row"><span class="k">4일 합계</span><span class="v">{trip_total}mm</span></div>')
    sokuhou_status = sokuhou.get("kinki_iri_status", "—")
    snap_date = sokuhou.get("snapshot_date", "—")
    okinawa = sokuhou.get("okinawa_iri_2026", "—")
    amami = sokuhou.get("amami_iri_2026", "—")
    rechecks = sokuhou.get("rechecks_planned", "")

    return f"""
<!-- SYNC: data/weather.json (tsuyu_normals · cities.kyoto.trip_window_daily_precip) · docs/weather.md §5 -->
<section id="tsuyu" class="card">
  <h2>장마(쓰유) 진입 확률</h2>
  <div class="sub" style="margin-bottom:0.5rem;">긴키 매우입 평년 {esc(tn.get('iri_normal', '—'))}. 여행 5/31~6/3은 평년상 입림 직전 진입기.</div>

  <div class="subcard">
    <div class="subtitle">교토 평년 일별 강수 (1991–2020)</div>
    {''.join(daily_rows)}
  </div>

  <div class="subcard">
    <div class="subtitle">최근 8년 시나리오 확률</div>
    <div class="row"><span class="k">평년형 (6/4~6/10)</span><span class="v">50%</span></div>
    <div class="row"><span class="k">조기 입림 (6/3 이전)</span><span class="v" style="color:#c80">25%</span></div>
    <div class="row"><span class="k">6/10 이전 입림</span><span class="v">50%</span></div>
    <div class="sub">조기 입림 사례: 2023(5/29) · 2025(5/17). 평년 직전 평탄 구간 — 본격 강수 상승은 6월 둘째 주부터.</div>
  </div>

  <div class="subcard">
    <div class="subtitle">2026 속보 (스냅샷 {esc(snap_date)})</div>
    <div class="row"><span class="k">긴키</span><span class="v" style="color:var(--muted)">{esc(sokuhou_status)}</span></div>
    <div class="row"><span class="k">沖縄</span><span class="v">{esc(okinawa)} 발표</span></div>
    <div class="row"><span class="k">奄美</span><span class="v">{esc(amami)} 발표</span></div>
    <div class="sub">출처: JMA 속보 (Playwright 검증). {esc(rechecks)}</div>
  </div>
</section>
"""


def card_airbnb(d) -> str:
    items = [l for l in d["cost"]["lodging"] if l["id"].startswith("airbnb_") and l["id"] != "kyoto_airbnb_4pax"]
    cards = []
    for l in items:
        src = l.get("source", "")
        airbnb_id = ""
        for tok in src.split():
            if tok.isdigit() and len(tok) > 6:
                airbnb_id = tok.rstrip(",")
                break
        link = f"https://www.airbnb.co.kr/rooms/{airbnb_id}" if airbnb_id else ""
        per_night = l["per_night_krw"]
        two_night = per_night * 2
        link_html = f'<a href="{esc(link)}" target="_blank" rel="noopener">매물 열기 ↗</a>' if link else ""
        cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(l['name'])}</div>
    <div class="row"><span class="k">2박 총액</span><span class="v">{esc(won(two_night))}</span></div>
    <div class="row"><span class="k">1인 1박</span><span class="v">{esc(won(per_night // 4))}</span></div>
    <div class="sub">{esc(l.get('notes', ''))}</div>
    <div class="links">{link_html}</div>
  </div>""")
    return f"""
<!-- SYNC: data/cost-options.json (lodging.airbnb_*) · docs/airbnb-kyoto-may31-jun2-2026.md -->
<section id="airbnb" class="card">
  <h2>에어비앤비 5개 후보 (5/31~6/2 2박)</h2>
  <div class="sub" style="margin-bottom:0.5rem;">매물 결정 후 시나리오 분기 추가 예정. 가격은 4명 직접 조회 2026-05-11.</div>
  {''.join(cards)}
</section>
"""


def card_kadensho(d) -> str:
    items = [l for l in d["cost"]["lodging"] if "kadensho" in l["id"] and "2026jun2" in l["id"]]
    cards = []
    for l in items:
        cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(l['name'])}</div>
    <div class="row"><span class="k">1박 (4인)</span><span class="v">{esc(won(l['per_night_krw']))}</span></div>
    <div class="row"><span class="k">출처</span><span class="v">{esc(l.get('data_quality', ''))}</span></div>
    <div class="sub">{esc(l.get('notes', ''))}</div>
  </div>""")
    return f"""
<!-- SYNC: data/cost-options.json (lodging.kadensho_*_2026jun2) · docs/decision-log/2026-05-11-may31-jun3-kyoto-update.md -->
<section id="kadensho" class="card">
  <h2>우메코지 카덴쇼 4 플랜 (6/2 1박, 2명×2실)</h2>
  <div class="sub" style="margin-bottom:0.5rem;">dormy-hotels.com 공식 검색 2026-05-11. 환불 정책 사전 확인 후 결제.</div>
  {''.join(cards)}
</section>
"""


def card_flights(d) -> str:
    items = d["cost"]["flights"]
    cards = []
    for f in items:
        cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(f['label'])}</div>
    <div class="row"><span class="k">일자</span><span class="v">{esc(f['depart_date'])} → {esc(f['return_date'])}</span></div>
    <div class="row"><span class="k">4인 총액</span><span class="v">{esc(won(f['total_krw']))}</span></div>
    <div class="row"><span class="k">출처</span><span class="v">{esc(f.get('source', ''))}</span></div>
    <div class="sub">{esc(f.get('notes', ''))}</div>
  </div>""")
    return f"""
<!-- SYNC: data/cost-options.json (flights) -->
<section id="flights" class="card">
  <h2>항공 옵션</h2>
  {''.join(cards)}
</section>
"""


def card_budget(d) -> str:
    budget = d["budget"]
    rows = []
    for s in budget["scenarios"]:
        marker = "✅" if s["passes_cap"] else "❌"
        head = won(s["headroom_krw"]) if s["headroom_krw"] >= 0 else f"−{won(-s['headroom_krw'])}"
        highlight = ' style="border-color: var(--accent);"' if s["id"] == SCENARIO_ID else ""
        cats = []
        for c in s["categories"]:
            color = {"ok": "#2a7", "near": "#c80", "over": "#c33"}[c["status"]]
            cats.append(f'<div class="row"><span class="k">{esc(c["label"])}</span><span class="v" style="color:{color}">{esc(won(c["actual_krw"]))} ({c["actual_pct"]}%)</span></div>')
        rows.append(f"""
  <div class="subcard"{highlight}>
    <div class="subtitle">{marker} {esc(s['label'])}</div>
    <div class="row"><span class="k">확정 합계</span><span class="v">{esc(won(s['confirmed_total_krw']))}</span></div>
    <div class="row"><span class="k">3M 여유</span><span class="v">{esc(head)}</span></div>
    {''.join(cats)}
  </div>""")
    return f"""
<!-- SYNC: scripts/budget.py --json · data/cost-options.json (scenarios) -->
<section id="budget" class="card">
  <h2>예산 시뮬 (3M 캡 = {esc(won(budget['cap_krw']))})</h2>
  <div class="sub" style="margin-bottom:0.5rem;">확정 항목만 기준. 굵은 테두리 = 현재 선택 시나리오.</div>
  {''.join(rows)}
</section>
"""


def card_itinerary(d) -> str:
    itin = d["itinerary"]
    days = []
    for day in itin["days"]:
        items_html = []
        for it in day["items"]:
            link = maps_link(it["maps_query"], it["title"]) if it.get("maps_query") else esc(it["title"])
            items_html.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
    </div>""")
        days.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['day_label'])}</div>
    {''.join(items_html)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day['walking_km']}km · 숙박: {esc(day['lodging'])}</div>
  </div>""")
    return f"""
<!-- SYNC: data/itinerary.json · docs/kyoto-itinerary-may31-jun3-2026.md -->
<section id="itinerary" class="card">
  <h2>일자별 일정</h2>
  <div class="sub" style="margin-bottom:0.5rem;">장소 탭 → 구글맵. 상세: <a href="viz/itinerary.html">전체 일정 화면 ↗</a></div>
  {''.join(days)}
</section>
"""


def card_checklist(d) -> str:
    items = d["checklist"]["items"]
    rows = []
    color_map = {"확정": "#2a7", "예약중": "#c80", "미정": "#c33"}
    for it in items:
        color = color_map.get(it["status"], "#666")
        rows.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(it['label'])}</div>
    <div class="row"><span class="k">상태</span><span class="v" style="color:{color}">{esc(it['status'])}</span></div>
    <div class="row"><span class="k">기한</span><span class="v">{esc(it['due_date'])}</span></div>
    <div class="sub">{esc(it.get('note', ''))}</div>
  </div>""")
    return f"""
<!-- SYNC: data/booking-checklist.json -->
<section id="checklist" class="card">
  <h2>예약 체크리스트 ({len(items)}개)</h2>
  <div class="sub" style="margin-bottom:0.5rem;">상세: <a href="viz/checklist.html">전체 체크리스트 화면 ↗</a></div>
  {''.join(rows)}
</section>
"""


def card_score(d) -> str:
    score = d["score"]
    rows = []
    for s in score["scored"]:
        pct = (s["score"] / 10) * 100
        rows.append(f"""
  <div class="row">
    <span class="k">{esc(s['name'])}</span>
    <span class="v">{s['score']:.2f}</span>
  </div>
  <div class="bar"><div class="bar-fill" style="width:{pct:.1f}%"></div></div>""")
    for s in score["unscored"]:
        rows.append(f"""
  <div class="row"><span class="k">{esc(s['name'])}</span><span class="v" style="color:var(--muted)">N/A · {esc(s['note'])}</span></div>""")
    return f"""
<!-- SYNC: scripts/score.py --json · data/decision.json (criteria·candidates) -->
<section id="score" class="card">
  <h2>후보지 종합 점수</h2>
  <div class="sub" style="margin-bottom:0.5rem;">교토만 7기준 모두 입력. 나머지는 seasonality(2026-05)만.</div>
  {''.join(rows)}
</section>
"""


INDEX_HEAD = """<h1>일본 여행 최종 결정</h1>
<div class="status">교토 5/31~6/3 시나리오 (시부모 4인 확정). 본 페이지는 <code>scripts/build_index.py</code> 산출물 — 직접 편집 금지.</div>

<nav>
  <a href="#summary">요약</a>
  <a href="#tsuyu">장마</a>
  <a href="#airbnb">에어비앤비</a>
  <a href="#kadensho">카덴쇼</a>
  <a href="#flights">항공</a>
  <a href="#budget">예산</a>
  <a href="#itinerary">일정</a>
  <a href="#checklist">체크리스트</a>
  <a href="#score">점수</a>
</nav>
"""

INDEX_FOOTER = f"""
<div class="links">
  <a href="{GH_BLOB}/reports/final-report.md" target="_blank" rel="noopener">최종 보고서</a>
  <a href="{GH_BLOB}/docs/airbnb-kyoto-may31-jun2-2026.md" target="_blank" rel="noopener">에어비앤비 비교</a>
  <a href="viz/itinerary.html">일자별 일정</a>
  <a href="viz/checklist.html">예약 체크리스트</a>
</div>

<footer>data/decision.json · data/cost-options.json · data/itinerary.json · data/booking-checklist.json 단일 출처 · scripts/build_index.py 산출</footer>
"""


def build_index(d) -> str:
    sections = [
        card_summary(d),
        card_tsuyu(d),
        card_airbnb(d),
        card_kadensho(d),
        card_flights(d),
        card_budget(d),
        card_itinerary(d),
        card_checklist(d),
        card_score(d),
    ]
    body = INDEX_HEAD + "\n".join(sections) + INDEX_FOOTER
    return html_doc("일본 여행 최종 결정", body)


# ─── viz/itinerary.html ────────────────────────────────────────────────────

def build_itinerary(d) -> str:
    itin = d["itinerary"]
    trip = itin["trip"]
    lodging_rows = "".join(
        f"""<div class="row"><span class="k">{esc(l['name'])} ({l['nights']}박)</span><span class="v">{esc(l.get('location',''))}</span></div>
  <div class="sub">{esc(l.get('note',''))}</div>"""
        for l in trip.get("lodging", [])
    )

    day_cards = []
    for day in itin["days"]:
        item_rows = []
        for it in day["items"]:
            link = maps_link(it["maps_query"], it["title"]) if it.get("maps_query") else esc(it["title"])
            note_html = f'<div class="sub">{esc(it["note"])}</div>' if it.get("note") else ""
            item_rows.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
      {note_html}
    </div>""")
        day_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['day_label'])}</div>
    {''.join(item_rows)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day['walking_km']}km · 숙박: {esc(day['lodging'])}</div>
  </div>""")

    pending_items = "".join(f"<li>{esc(p)}</li>" for p in itin.get("pending", []))

    body = f"""<h1>교토 3박4일 일정</h1>
<div class="status">{esc(trip['dates'])} · {trip['nights']}박 · {trip['travelers']}인 · {esc(trip.get('composition',''))}</div>

<!-- SYNC: data/itinerary.json -->
<section class="card">
  <h2>여행 메타</h2>
  <div class="row"><span class="k">목적지</span><span class="v">{esc(trip['destination'])}</span></div>
  <div class="row"><span class="k">강도</span><span class="v">{esc(trip.get('intensity',''))}</span></div>
  <div class="row"><span class="k">총 도보</span><span class="v">약 {trip.get('walking_km_total','—')}km</span></div>
  {lodging_rows}
</section>

<section class="card">
  <h2>일자별 코스</h2>
  {''.join(day_cards)}
</section>

<section class="card">
  <h2>보류·확인 필요</h2>
  <ul>{pending_items}</ul>
</section>

<div class="links">
  <a href="../index.html">← 결정 요약으로</a>
  <a href="{GH_BLOB}/{esc(itin.get('source_doc',''))}" target="_blank" rel="noopener">사람용 마크다운</a>
  <a href="checklist.html">예약 체크리스트</a>
</div>

<footer>data/itinerary.json 단일 출처 · scripts/build_index.py 산출 — 직접 편집 금지</footer>
"""
    return html_doc("교토 3박4일 일정", body)


# ─── viz/checklist.html ────────────────────────────────────────────────────

def build_checklist(d) -> str:
    cl = d["checklist"]
    items = cl["items"]
    color_map = {"확정": "#2a7", "예약중": "#c80", "미정": "#c33"}
    counts = {"확정": 0, "예약중": 0, "미정": 0}
    for it in items:
        counts[it.get("status", "미정")] = counts.get(it.get("status", "미정"), 0) + 1

    summary_rows = "".join(
        f'<div class="row"><span class="k" style="color:{color_map[k]}">● {k}</span><span class="v">{counts[k]}개</span></div>'
        for k in ("확정", "예약중", "미정")
    )

    sorted_items = sorted(items, key=lambda it: it.get("due_date", "9999-99-99"))
    item_cards = []
    for it in sorted_items:
        color = color_map.get(it["status"], "#666")
        item_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(it['label'])}</div>
    <div class="row"><span class="k">상태</span><span class="v"><span class="badge" style="color:{color}">{esc(it['status'])}</span></span></div>
    <div class="row"><span class="k">기한</span><span class="v">{esc(it.get('due_date',''))}</span></div>
    <div class="sub">{esc(it.get('note',''))}</div>
  </div>""")

    body = f"""<h1>예약 체크리스트</h1>
<div class="status">시나리오: {esc(cl.get('scenario',''))} · {len(items)}개 항목</div>

<!-- SYNC: data/booking-checklist.json -->
<section class="card">
  <h2>상태 요약</h2>
  {summary_rows}
</section>

<section class="card">
  <h2>항목 (기한 이른 순)</h2>
  {''.join(item_cards)}
</section>

<div class="links">
  <a href="../index.html">← 결정 요약으로</a>
  <a href="itinerary.html">일자별 일정</a>
</div>

<footer>data/booking-checklist.json 단일 출처 · scripts/build_index.py 산출 — 직접 편집 금지</footer>
"""
    return html_doc("예약 체크리스트", body)


# ─── 메인 ──────────────────────────────────────────────────────────────────

OUTPUTS = (
    ("index.html", lambda p: p / "index.html", build_index),
    ("viz/itinerary.html", lambda p: p / "viz" / "itinerary.html", build_itinerary),
    ("viz/checklist.html", lambda p: p / "viz" / "checklist.html", build_checklist),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="빌드 결과와 디스크 diff (drift 시 exit 1)")
    args = parser.parse_args()

    d = load_data()
    rendered = [(label, path_fn(BASE), build_fn(d)) for label, path_fn, build_fn in OUTPUTS]

    if args.check:
        drift = []
        for label, path, content in rendered:
            existing = path.read_text(encoding="utf-8") if path.exists() else ""
            if existing != content:
                drift.append(label)
        if drift:
            print(f"DRIFT: {', '.join(drift)} out of sync. Run `python scripts/build_index.py` and commit.", file=sys.stderr)
            return 1
        print("All outputs in sync.")
        return 0

    for label, path, content in rendered:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {label} ({len(content):,} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
