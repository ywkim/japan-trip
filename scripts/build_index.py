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
SITE_URL = "https://nihon-trip.vercel.app"
SITE_NAME = "교토 가족여행 2026"

# 탭바 정의: (탭 키, 아이콘, 레이블, 루트 기준 경로, viz/ 기준 경로)
_TABS = [
    ("home",      "🏠", "홈",      "index.html",         "../index.html"),
    ("itinerary", "📅", "일정",    "viz/itinerary.html",  "itinerary.html"),
    ("lodging",   "✈️", "숙박·항공","viz/lodging.html",    "lodging.html"),
    ("checklist", "☑", "예약",    "viz/checklist.html",  "checklist.html"),
]


def tab_bar(active: str, in_viz: bool = False) -> str:
    idx = 4 if in_viz else 3
    items = []
    for key, icon, label, root_href, viz_href in _TABS:
        href = viz_href if in_viz else root_href
        active_attr = f' class="active" data-tab="{key}"' if key == active else f' data-tab="{key}"'
        items.append(
            f'<a href="{esc(href)}"{active_attr}>'
            f'<span class="tab-icon">{icon}</span>'
            f'<span>{esc(label)}</span></a>'
        )
    return f'<nav class="tab-bar" aria-label="하단 탭">{"".join(items)}</nav>'


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
    --bg: #fff; --fg: #111; --muted: #888; --border: #eaeaea;
    --accent: #111; --card: #fff; --subcard: #fafafa;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #000; --fg: #ededed; --muted: #888; --border: #333;
      --accent: #ededed; --card: #0a0a0a; --subcard: #111;
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
  /* ── 하단 탭바 ── */
  body { padding-bottom: calc(4.5rem + env(safe-area-inset-bottom, 0px)); }
  .tab-bar {
    position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 100%; max-width: 640px;
    display: flex; background: var(--card); border-top: 1px solid var(--border);
    z-index: 200; padding-bottom: env(safe-area-inset-bottom, 0px);
  }
  .tab-bar::after {
    content: ''; position: absolute; top: 100%; left: 0; right: 0;
    height: 80px; background: var(--card);
  }
  .tab-bar a {
    flex: 1; display: flex; flex-direction: column; align-items: center;
    padding: 0.6rem 0.25rem 0.45rem; text-decoration: none;
    color: var(--muted); font-size: 0.68rem; gap: 0.2rem; line-height: 1.2;
    -webkit-tap-highlight-color: transparent;
  }
  .tab-bar a.active {
    color: var(--fg); font-weight: 600;
  }
  .tab-bar a:active { opacity: 0.6; }
  .tab-bar .tab-icon { font-size: 1.25rem; line-height: 1; }
  /* ── 이미지 ── */
  .place-img {
    width: 100%; aspect-ratio: 16/9; object-fit: cover;
    border-radius: 4px; display: block; margin-top: 0.35rem;
    max-height: 200px;
  }
  .img-credit { color: var(--muted); font-size: 0.65rem; text-align: right; }
"""


def og_meta(*, title: str, description: str, slug: str, page_path: str) -> str:
    url = f"{SITE_URL}/{page_path}" if page_path else f"{SITE_URL}/"
    image = f"{SITE_URL}/assets/og-{slug}.svg"
    return f"""<meta name="description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:locale" content="ko_KR">
<meta property="og:url" content="{esc(url)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(image)}">"""


def html_doc(
    title: str,
    body: str,
    *,
    description: str,
    og_slug: str,
    page_path: str,
    extra_css: str = "",
) -> str:
    css = CSS + extra_css
    meta = og_meta(title=title, description=description, slug=og_slug, page_path=page_path)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#fafafa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1a1a1a" media="(prefers-color-scheme: dark)">
<title>{esc(title)}</title>
{meta}
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


# ─── index.html 섹션 ──────────────────────────────────────────────────────

def card_summary(d) -> str:
    decision = d["decision"]
    budget = d["budget"]
    kyoto = next(c for c in decision["candidates"] if c["id"] == "kyoto")
    scn = next((s for s in budget["scenarios"] if s["id"] == SCENARIO_ID), None)
    pass_marker = "통과" if scn and scn["passes_cap"] else f"{won(-scn['headroom_krw'])} 초과" if scn else "—"
    total_str = won(scn["confirmed_total_krw"]) if scn else "—"

    return f"""
<!-- SYNC: reports/final-report.md §1 (결정 요약) · data/decision.json (companions) · data/cost-options.json (scenario {SCENARIO_ID}) -->
<section id="summary" class="card">
  <h2>요약</h2>
  <div class="big">교토 · 5/31~6/3</div>
  <div class="sub">관서 · 시부모 동반 4인 (확정) · 3박 4일</div>
  <div class="row"><span class="k">시기</span><span class="v">2026-05-31 (일) ~ 06-03 (수)</span></div>
  <div class="row"><span class="k">동반</span><span class="v">영욱·소연 + 시부모 (4인)</span></div>
  <div class="row"><span class="k">숙박</span><span class="v">에어비앤비 2박 + 카덴쇼 료칸 1박 (2명×2실)</span></div>
  <div class="row"><span class="k">예상 비용</span><span class="v">{esc(total_str)}</span></div>
  <div class="row"><span class="k">3M 캡</span><span class="v">{esc(pass_marker)}</span></div>
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
    <div class="row"><span class="k">조기 입림 (6/3 이전)</span><span class="v" style="font-weight:600">25%</span></div>
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
    l = next((x for x in d["cost"]["lodging"] if x["id"] == "airbnb_shio_machiya"), None)
    if not l:
        return ""
    src = l.get("source", "")
    airbnb_id = ""
    for tok in src.split():
        if tok.isdigit() and len(tok) > 6:
            airbnb_id = tok.rstrip(",")
            break
    link = f"https://www.airbnb.co.kr/rooms/{airbnb_id}" if airbnb_id else ""
    link_html = f'<a href="{esc(link)}" target="_blank" rel="noopener">매물 열기 ↗</a>' if link else ""
    two_night = l["per_night_krw"] * 2
    return f"""
<!-- SYNC: data/cost-options.json (lodging.airbnb_shio_machiya) · docs/airbnb-kyoto-may31-jun2-2026.md -->
<section id="airbnb" class="card">
  <h2>에어비앤비 · 시오(Shio) 100년 마치야 <span class="badge">확정</span></h2>
  <div class="row"><span class="k">일정</span><span class="v">5/31~6/2 · 2박</span></div>
  <div class="row"><span class="k">위치</span><span class="v">중교구 · 니조역 도보 7분</span></div>
  <div class="row"><span class="k">2박 총액</span><span class="v">{esc(won(two_night))}</span></div>
  <div class="row"><span class="k">1인 1박</span><span class="v">{esc(won(l['per_night_krw'] // 4))}</span></div>
  <div class="sub" style="margin-top:0.4rem;">{esc(l.get('notes', ''))}</div>
  <div class="links">{link_html}</div>
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
        marker = "통과" if s["passes_cap"] else "초과"
        head = won(s["headroom_krw"]) if s["headroom_krw"] >= 0 else f"−{won(-s['headroom_krw'])}"
        highlight = ' style="border-color: var(--accent); border-width: 2px;"' if s["id"] == SCENARIO_ID else ""
        cats = []
        for c in s["categories"]:
            dim = ' style="color:var(--muted)"' if c["status"] == "ok" else (' style="font-weight:600"' if c["status"] == "over" else "")
            cats.append(f'<div class="row"><span class="k">{esc(c["label"])}</span><span class="v"{dim}>{esc(won(c["actual_krw"]))} ({c["actual_pct"]}%)</span></div>')
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


MODE_ICONS = {
    "walk": "🚶",
    "bus": "🚌",
    "subway": "🚇",
    "train": "🚆",
    "jr": "🚆",
    "airport_express": "✈️",
    "taxi": "🚕",
}


def transit_line(af) -> str:
    if not af:
        return ""
    icon = MODE_ICONS.get(af.get("mode"), "·")
    # source 필드의 첫 토큰이 http(s) URL이면 클릭 가능 링크로 감싼다 (Maps Directions 등).
    src = (af.get("source") or "").strip()
    first_token = src.split()[0] if src else ""
    href = first_token if first_token.startswith(("http://", "https://")) else ""
    if af.get("data_quality") == "tbd_needs_browser_mcp":
        route = af.get("route") or af.get("mode", "")
        body = f"{icon} {esc(route)} · 소요시간 미확정 — Maps 확인 필요"
    else:
        bits = [icon]
        if af.get("route"):
            bits.append(esc(af["route"]))
        if af.get("duration_min"):
            bits.append(f"{af['duration_min']}분")
        dist = af.get("distance_km")
        if isinstance(dist, (int, float)) and dist < 50:
            bits.append(f"{dist}km")
        body = " · ".join(bits)
    if href:
        body = f'<a href="{esc(href)}" target="_blank" rel="noopener" style="color:inherit;">{body}</a>'
    return f'<div class="sub" style="opacity:0.75;font-size:0.85em;">{body}</div>'


def card_itinerary(d) -> str:
    itin = d["itinerary"]
    trip = itin.get("trip", {})
    days = []
    for day in itin["days"]:
        items_html = []
        for it in day["items"]:
            link = maps_link(it["maps_query"], it["title"]) if it.get("maps_query") else esc(it["title"])
            transit = transit_line(it.get("arrive_from"))
            items_html.append(f"""
    <div class="day">
      {transit}
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
    </div>""")
        days.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['day_label'])}</div>
    {''.join(items_html)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day['walking_km']}km · 숙박: {esc(day['lodging'])}</div>
    {f'<div class="sub" style="margin-top:0.25rem;">🎫 {esc(day["pass_recommendation"])}</div>' if day.get("pass_recommendation") else ""}
  </div>""")

    pass_sources = trip.get("transit_pass_sources", [])
    pass_sources_html = ""
    if pass_sources:
        links = " · ".join(
            f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a>'
            for s in pass_sources
        )
        pass_sources_html = f'<div class="sub" style="margin-top:0.6rem;">📚 교통 출처: {links}</div>'

    playbook = trip.get("transit_pass_playbook", [])
    playbook_html = ""
    if playbook:
        rows = "".join(
            f'<li style="margin-bottom:0.35rem;"><b>{esc(s["when"])}</b> — {esc(s["action"])}</li>'
            for s in playbook
        )
        playbook_html = (
            f'<div class="subcard" style="margin-top:0.6rem;">'
            f'<div class="subtitle">🧭 ICOCA 실행 단계</div>'
            f'<ol style="margin:0.3rem 0 0 1.1rem;padding:0;">{rows}</ol></div>'
        )

    return f"""
<!-- SYNC: data/itinerary.json · docs/kyoto-itinerary-may31-jun3-2026.md -->
<section id="itinerary" class="card">
  <h2>일자별 일정</h2>
  <div class="sub" style="margin-bottom:0.5rem;">장소 탭 → 구글맵. 상세: <a href="viz/itinerary.html">카드 뷰 ↗</a> · <a href="viz/itinerary-table.html">시간표 뷰 ↗</a></div>
  {''.join(days)}
  {playbook_html}
  {pass_sources_html}
</section>
"""


def card_checklist(d) -> str:
    items = d["checklist"]["items"]
    rows = []
    for it in items:
        st = it["status"]
        dim = "" if st == "확정" else ' style="color:var(--muted)"'
        rows.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(it['label'])}</div>
    <div class="row"><span class="k">상태</span><span class="v"{dim}>{esc(it['status'])}</span></div>
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
  <div class="sub" style="margin-bottom:0.3rem;">교토만 7기준 모두 입력. 나머지는 seasonality(2026-05)만.</div>
  <div class="sub" style="margin-bottom:0.5rem;">교토는 1위(오사카·고베 9.0) 후보가 아니지만 시부모 동반·비용·이동 부담을 종합한 별도 의사결정. 사유: <a href="{GH_BLOB}/docs/decision-log/2026-05-11-may31-jun3-kyoto-update.md" target="_blank" rel="noopener">2026-05-11 결정 일지 ↗</a></div>
  {''.join(rows)}
</section>
"""


INDEX_TITLE = "교토 5/31~6/3 · 4인 가족 여행"
INDEX_DESCRIPTION = "교토 5/31~6/3 · 4인 가족(부부+시부모) · 3박 4일 · 확정 일정·예약 현황"

INDEX_HEAD = f"""<h1>{esc(INDEX_TITLE)}</h1>
<div class="status">시부모 동반 · 3박 4일 · 시오 마치야 2박 + 카덴쇼 료칸 1박</div>

<nav>
  <a href="#summary">요약</a>
  <a href="#itinerary">일정</a>
  <a href="viz/lodging.html">숙박·항공</a>
  <a href="viz/checklist.html">예약</a>
  <a href="viz/archive.html">아카이브</a>
</nav>
"""

INDEX_FOOTER = f"""
<div class="links">
  <a href="viz/itinerary.html">일자별 일정 ↗</a>
  <a href="viz/checklist.html">예약 체크리스트 ↗</a>
  <a href="viz/archive.html">의사결정 아카이브 ↗</a>
</div>

<footer>2026-05-12 의사결정 종료 · 이 페이지는 확정 일정·예약 운영용. 결정 근거는 <a href="viz/archive.html" style="color:inherit;">아카이브</a>·<a href="{GH_BLOB}/reports/final-report.md" target="_blank" rel="noopener" style="color:inherit;">최종 보고서 ↗</a></footer>
"""


def build_index(d) -> str:
    sections = [
        card_summary(d),
        card_itinerary(d),
    ]
    body = INDEX_HEAD + "\n".join(sections) + INDEX_FOOTER + tab_bar("home", in_viz=False)
    return html_doc(
        INDEX_TITLE,
        body,
        description=INDEX_DESCRIPTION,
        og_slug="home",
        page_path="",
    )


# ─── viz/archive.html ──────────────────────────────────────────────────────

ARCHIVE_TITLE = "의사결정 아카이브 · 교토 가족여행 2026"
ARCHIVE_DESCRIPTION = "의사결정 아카이브 · 장마 확률·예산 시나리오·후보지 점수 (2026-05-12 종료)"


def build_archive(d) -> str:
    sections = [
        card_tsuyu(d),
        card_budget(d),
        card_score(d),
    ]
    head = f"""<h1>의사결정 아카이브</h1>
<div class="status">2026-05-12 의사결정 종료 · 회귀 가드·재참조용 분석 자료</div>

<nav>
  <a href="../index.html">← 운영 페이지로</a>
  <a href="#tsuyu">장마</a>
  <a href="#budget">예산 시나리오</a>
  <a href="#score">후보지 점수</a>
</nav>
"""
    footer = f"""
<div class="links">
  <a href="{GH_BLOB}/reports/final-report.md" target="_blank" rel="noopener">최종 보고서 ↗</a>
  <a href="{GH_BLOB}/docs/decision-log/" target="_blank" rel="noopener">결정 일지 ↗</a>
</div>

<footer>data/decision.json · data/cost-options.json · data/weather.json 단일 출처</footer>
"""
    body = head + "\n".join(sections) + footer + tab_bar("home", in_viz=True)
    return html_doc(
        ARCHIVE_TITLE,
        body,
        description=ARCHIVE_DESCRIPTION,
        og_slug="archive",
        page_path="viz/archive.html",
    )


# ─── viz/lodging.html ──────────────────────────────────────────────────────

def build_lodging(d) -> str:
    body = f"""<h1>숙박 · 항공</h1>
<div class="status">에어비앤비 2박 + 카덴쇼 료칸 1박 · 항공 옵션</div>
{card_airbnb(d)}
{card_kadensho(d)}
{card_flights(d)}
<footer>data/cost-options.json 단일 출처</footer>
{tab_bar("lodging", in_viz=True)}
"""
    return html_doc(
        "숙박·항공 · 교토 5/31~6/3",
        body,
        description="시오 마치야 2박 + 카덴쇼 료칸 1박 · 에어서울 4인 발권",
        og_slug="lodging",
        page_path="viz/lodging.html",
    )


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
            transit = transit_line(it.get("arrive_from"))
            if it.get("image_url"):
                img_html = (
                    f'<img src="{esc(it["image_url"])}" alt="{esc(it["title"])}" '
                    f'class="place-img" loading="lazy">'
                    f'<div class="img-credit">{esc(it.get("image_credit",""))}</div>'
                )
            else:
                img_html = ""
            item_rows.append(f"""
    <div class="day">
      {transit}
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
      {note_html}{img_html}
    </div>""")
        day_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['day_label'])}</div>
    {''.join(item_rows)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day['walking_km']}km · 숙박: {esc(day['lodging'])}</div>
    {f'<div class="sub" style="margin-top:0.25rem;">🎫 {esc(day["pass_recommendation"])}</div>' if day.get("pass_recommendation") else ""}
  </div>""")

    pending_items = "".join(f"<li>{esc(p)}</li>" for p in itin.get("pending", []))

    pass_sources = trip.get("transit_pass_sources", [])
    pass_sources_html = ""
    if pass_sources:
        links = " · ".join(
            f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a>'
            for s in pass_sources
        )
        pass_sources_html = f'<div class="sub" style="margin-top:0.6rem;">📚 교통 출처: {links}</div>'

    playbook = trip.get("transit_pass_playbook", [])
    playbook_html = ""
    if playbook:
        rows = "".join(
            f'<li style="margin-bottom:0.35rem;"><b>{esc(s["when"])}</b> — {esc(s["action"])}</li>'
            for s in playbook
        )
        playbook_html = (
            f'<div class="subcard" style="margin-top:0.6rem;">'
            f'<div class="subtitle">🧭 ICOCA 실행 단계</div>'
            f'<ol style="margin:0.3rem 0 0 1.1rem;padding:0;">{rows}</ol></div>'
        )

    candidate_cards = []
    for cand in itin.get("route_candidates", []):
        cand_day_cards = []
        for day in cand["days"]:
            item_rows = []
            for it in day["items"]:
                link = maps_link(it["maps_query"], it["title"]) if it.get("maps_query") else esc(it["title"])
                note_html = f'<div class="sub">{esc(it["note"])}</div>' if it.get("note") else ""
                item_rows.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
      {note_html}
    </div>""")
            cand_day_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['day_label'])}</div>
    {''.join(item_rows)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day['walking_km']}km · 숙박: {esc(day['lodging'])}</div>
  </div>""")
        candidate_cards.append(f"""
<details>
  <summary style="cursor:pointer;font-weight:600;padding:0.5rem 0;font-size:0.95rem;">{esc(cand['name'])}</summary>
  <div class="sub" style="margin:0.25rem 0 0.5rem;">{esc(cand.get('theme',''))} · 총 도보 약 {cand.get('walking_km_total','—')}km</div>
  {''.join(cand_day_cards)}
</details>""")

    candidates_section = ""
    if candidate_cards:
        candidates_section = f"""
<section class="card">
  <h2>후보 코스</h2>
  <div class="sub" style="margin-bottom:0.5rem;">숙소·날짜(5/31~6/3) 동일. 동선만 다른 대안 코스. 제목 탭하면 펼쳐짐.</div>
  {''.join(candidate_cards)}
</section>
"""

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
  {playbook_html}
  {pass_sources_html}
</section>
{candidates_section}
<section class="card">
  <h2>보류·확인 필요</h2>
  <ul>{pending_items}</ul>
</section>

<div class="links">
  <a href="itinerary-table.html">시간표 뷰</a>
  <a href="{GH_BLOB}/{esc(itin.get('source_doc',''))}" target="_blank" rel="noopener">마크다운</a>
</div>

<footer>data/itinerary.json 단일 출처</footer>
{tab_bar("itinerary", in_viz=True)}
"""
    return html_doc(
        "교토 3박4일 일정 · 5/31~6/3 · 4인 가족",
        body,
        description="교토 3박 4일 일자별 코스 · 5/31~6/3 · 4인 가족",
        og_slug="itinerary",
        page_path="viz/itinerary.html",
    )


# ─── viz/checklist.html ────────────────────────────────────────────────────

def build_checklist(d) -> str:
    cl = d["checklist"]
    items = cl["items"]
    counts = {"확정": 0, "예약중": 0, "미정": 0}
    for it in items:
        counts[it.get("status", "미정")] = counts.get(it.get("status", "미정"), 0) + 1

    summary_rows = "".join(
        f'<div class="row"><span class="k">{k}</span><span class="v">{counts[k]}개</span></div>'
        for k in ("확정", "예약중", "미정")
    )

    sorted_items = sorted(items, key=lambda it: it.get("due_date", "9999-99-99"))
    item_cards = []
    for it in sorted_items:
        st = it["status"]
        badge_style = "" if st == "확정" else ' style="color:var(--muted)"'
        item_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(it['label'])}</div>
    <div class="row"><span class="k">상태</span><span class="v"><span class="badge"{badge_style}>{esc(it['status'])}</span></span></div>
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

<footer>data/booking-checklist.json 단일 출처</footer>
{tab_bar("checklist", in_viz=True)}
"""
    return html_doc(
        "예약 체크리스트 · 교토 5/31~6/3",
        body,
        description="예약 진행 상태 7항목 (확정·미정)",
        og_slug="checklist",
        page_path="viz/checklist.html",
    )


# ─── viz/itinerary-table.html ─────────────────────────────────────────────

TABLE_CSS = """
  /* 모바일: 카드 뷰 표시, 테이블 숨김 */
  .tbl-wrap { display: none; }
  .mobile-days { display: block; }
  /* 데스크탑(600px+): 테이블 표시, 모바일 카드 숨김 */
  @media (min-width: 600px) {
    .tbl-wrap { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 0.5rem 0; }
    .mobile-days { display: none; }
  }
  table.timetable {
    border-collapse: collapse; width: 100%; min-width: 560px;
    font-size: 0.82rem; table-layout: fixed;
  }
  .timetable th {
    background: var(--subcard); border: 1px solid var(--border);
    padding: 0.45rem 0.5rem; text-align: center; font-weight: 600;
    font-size: 0.85rem; position: sticky; top: 0; z-index: 1;
  }
  .timetable th .day-meta {
    font-weight: 400; color: var(--muted); font-size: 0.75rem;
    display: block; margin-top: 0.15rem;
  }
  .timetable td {
    border: 1px solid var(--border); padding: 0.4rem 0.5rem;
    vertical-align: top; width: 25%;
  }
  .timetable td:empty { background: var(--subcard); }
  .timetable .t-time {
    color: var(--muted); font-size: 0.75rem; display: block;
    margin-bottom: 0.2rem; font-variant-numeric: tabular-nums;
  }
  .timetable .t-title { line-height: 1.35; }
  .timetable .t-title a { color: var(--fg); text-decoration: underline; text-decoration-color: var(--border); }
  .timetable .t-note {
    color: var(--muted); font-size: 0.75rem; margin-top: 0.2rem;
    display: block; line-height: 1.3;
  }
  .timetable tr:nth-child(even) td { background: var(--subcard); }
  .timetable tr:nth-child(even) td:empty { background: var(--bg); }
  .timetable .place-img {
    width: 100%; aspect-ratio: 16/9; object-fit: cover;
    border-radius: 3px; display: block; margin-top: 0.3rem; max-height: 160px;
  }
  .timetable .img-credit { color: var(--muted); font-size: 0.62rem; }
"""


def build_itinerary_table(d) -> str:
    itin = d["itinerary"]
    trip = itin["trip"]
    days = itin["days"]

    # 열 헤더 (4일)
    headers = []
    for day in days:
        label = day["day_label"]
        meta = f"도보 {day['walking_km']}km · {day['lodging']}"
        headers.append(f'<th>{esc(label)}<span class="day-meta">{esc(meta)}</span></th>')

    # 각 일자의 항목 목록 (최대 길이만큼 패딩)
    col_items = [day["items"] for day in days]
    max_rows = max(len(col) for col in col_items)

    rows_html = []
    for i in range(max_rows):
        cells = []
        for col in col_items:
            if i < len(col):
                it = col[i]
                link = maps_link(it["maps_query"], it["title"]) if it.get("maps_query") else esc(it["title"])
                note_html = f'<span class="t-note">{esc(it["note"])}</span>' if it.get("note") else ""
                transit = transit_line(it.get("arrive_from"))
                if it.get("image_url"):
                    img_html = (
                        f'<img src="{esc(it["image_url"])}" alt="{esc(it["title"])}" '
                        f'class="place-img" loading="lazy">'
                        f'<span class="img-credit">{esc(it.get("image_credit",""))}</span>'
                    )
                else:
                    img_html = ""
                cells.append(
                    f'<td>{transit}<span class="t-time">{esc(it["time"])}</span>'
                    f'<span class="t-title">{link}</span>{note_html}{img_html}</td>'
                )
            else:
                cells.append("<td></td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    # 모바일용 카드 뷰 (600px 미만)
    mobile_cards = []
    for day in days:
        item_rows = []
        for it in day["items"]:
            link = maps_link(it["maps_query"], it["title"]) if it.get("maps_query") else esc(it["title"])
            note_html = f'<div class="sub">{esc(it["note"])}</div>' if it.get("note") else ""
            transit = transit_line(it.get("arrive_from"))
            if it.get("image_url"):
                img_html = (
                    f'<img src="{esc(it["image_url"])}" alt="{esc(it["title"])}" '
                    f'class="place-img" loading="lazy">'
                    f'<div class="img-credit">{esc(it.get("image_credit",""))}</div>'
                )
            else:
                img_html = ""
            item_rows.append(f"""
    <div class="day">
      {transit}
      <div class="date"><span class="k">{esc(it["time"])}</span> {link}</div>
      {note_html}{img_html}
    </div>""")
        mobile_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day["day_label"])}</div>
    {''.join(item_rows)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day["walking_km"]}km · 숙박: {esc(day["lodging"])}</div>
  </div>""")

    pending_items = "".join(f"<li>{esc(p)}</li>" for p in itin.get("pending", []))

    body = f"""<h1>교토 3박4일 · 시간표 뷰</h1>
<div class="status">{esc(trip['dates'])} · {trip['nights']}박 · {trip['travelers']}인 · {esc(trip.get('composition',''))}</div>

<!-- SYNC: data/itinerary.json -->
<div class="card">
  <h2>4일 한눈에 보기 — 장소 탭 → 구글맵</h2>
  <div class="sub" style="margin-bottom:0.5rem;">모바일: 일자별 카드 뷰 · 데스크탑: 4열 시간표</div>

  <div class="mobile-days">{''.join(mobile_cards)}</div>

  <div class="tbl-wrap">
    <table class="timetable">
      <thead><tr>{''.join(headers)}</tr></thead>
      <tbody>{''.join(rows_html)}</tbody>
    </table>
  </div>
</div>

<section class="card">
  <h2>보류·확인 필요</h2>
  <ul>{pending_items}</ul>
</section>

<div class="links">
  <a href="itinerary.html">카드 뷰</a>
</div>

<footer>data/itinerary.json 단일 출처</footer>
{tab_bar("itinerary", in_viz=True)}
"""
    return html_doc(
        "교토 3박4일 시간표 · 5/31~6/3",
        body,
        description="교토 3박 4일 시간표 · 4일 한눈에",
        og_slug="itinerary-table",
        page_path="viz/itinerary-table.html",
        extra_css=TABLE_CSS,
    )


# ─── OG SVG 자산 (1200×630) ────────────────────────────────────────────────

OG_FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif"


def build_og_svg(*, eyebrow: str, title: str, subtitle: str) -> str:
    """1200×630 SVG OG 카드. 좌측 액센트 바 + 큰 한글 제목 + 부제 + 도메인."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#0a0a0a"/>
  <rect x="0" y="0" width="12" height="630" fill="#ededed"/>
  <g font-family="{OG_FONT_STACK}" fill="#ededed">
    <text x="80" y="170" font-size="34" font-weight="500" fill="#888">{esc(eyebrow)}</text>
    <text x="80" y="290" font-size="84" font-weight="700">{esc(title)}</text>
    <text x="80" y="380" font-size="40" font-weight="400" fill="#cfcfcf">{esc(subtitle)}</text>
    <text x="80" y="560" font-size="26" font-weight="500" fill="#888">nihon-trip.vercel.app</text>
    <text x="1120" y="560" font-size="26" font-weight="500" fill="#888" text-anchor="end">교토 가족여행 2026</text>
  </g>
</svg>
"""


OG_CARDS = (
    ("home",            "교토 가족여행 · 2026",     "교토 5/31~6/3 · 4인 가족",     "부부 + 시부모 · 3박 4일 · 확정"),
    ("itinerary",       "일자별 코스",              "교토 3박 4일 일정",            "5/31~6/3 · 청수사·아라시야마·후시미"),
    ("itinerary-table", "4일 시간표",               "교토 3박 4일 · 한눈에",        "5/31 일 · 6/1 월 · 6/2 화 · 6/3 수"),
    ("lodging",         "숙박 · 항공",              "시오 2박 + 카덴쇼 1박",        "에어서울 인천↔간사이 4인 발권"),
    ("checklist",       "예약 체크리스트",          "예약 진행 상태",               "확정 3 · 미정 4 항목"),
    ("archive",         "의사결정 아카이브",        "장마·예산·후보지 점수",        "2026-05-12 결정 종료 · 회귀 가드"),
)


# ─── 메인 ──────────────────────────────────────────────────────────────────

OUTPUTS = (
    ("index.html",               lambda p: p / "index.html",                   build_index),
    ("viz/itinerary.html",       lambda p: p / "viz" / "itinerary.html",       build_itinerary),
    ("viz/checklist.html",       lambda p: p / "viz" / "checklist.html",       build_checklist),
    ("viz/itinerary-table.html", lambda p: p / "viz" / "itinerary-table.html", build_itinerary_table),
    ("viz/lodging.html",         lambda p: p / "viz" / "lodging.html",         build_lodging),
    ("viz/archive.html",         lambda p: p / "viz" / "archive.html",         build_archive),
) + tuple(
    (
        f"assets/og-{slug}.svg",
        lambda p, s=slug: p / "assets" / f"og-{s}.svg",
        lambda _d, e=eyebrow, t=title, s=subtitle: build_og_svg(eyebrow=e, title=t, subtitle=s),
    )
    for slug, eyebrow, title, subtitle in OG_CARDS
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
