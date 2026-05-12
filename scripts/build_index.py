#!/usr/bin/env python3
"""index.html 빌드 스크립트.

data/decision.json·data/cost-options.json·data/weather.json·data/booking-checklist.json
을 읽고 scripts/score.py·scripts/budget.py를 --json으로 호출해 인라인 데이터로
모바일 친화 8섹션 카드를 생성. CLAUDE.md "더블클릭 동작" 규칙 보존을 위해
단일 HTML 자기완결 (외부 fetch 없음).

용법:
  python scripts/build_index.py            # index.html 갱신
  python scripts/build_index.py --check    # 빌드 결과와 디스크 diff (CI용, exit 1 if drift)

# TODO: viz/dashboard.html도 동일 스크립트로 generate (별 PR)
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
OUT = BASE / "index.html"

GH_BLOB = "https://github.com/ywkim/japan-trip/blob/main"
SCENARIO_ID = "kyoto_may31_kadensho_early_bird"


def esc(s) -> str:
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def won(n: int) -> str:
    return f"₩{n:,}"


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
        "checklist": json.loads((DATA / "booking-checklist.json").read_text(encoding="utf-8")),
        "score": run_json("score.py"),
        "budget": run_json("budget.py"),
    }


# ─── 섹션 빌더 ─────────────────────────────────────────────────────────────

def card_summary(d) -> str:
    decision = d["decision"]
    cost = d["cost"]
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


def card_airbnb(d) -> str:
    items = [l for l in d["cost"]["lodging"] if l["id"].startswith("airbnb_") and l["id"] != "kyoto_airbnb_4pax"]
    cards = []
    for l in items:
        # 매물 ID에서 airbnb 링크 추출
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


# 일자별 일정 (정적 — 5/31~6/3 평행 이동)
ITINERARY = [
    {"date": "5/31 (일) — 도착", "items": [
        ("09:05", "간사이공항 도착 → JR 하루카 → 교토역", "Kansai International Airport"),
        ("11:30", "에어비앤비 짐 보관 + 점심", "Kyoto Station"),
        ("13:30", "키요미즈데라 (清水寺)", "Kiyomizu-dera"),
        ("16:30", "산넨자카 → 야사카 신사 → 기온", "Gion Kyoto"),
        ("18:30", "가와라마치 저녁", "Kawaramachi"),
    ], "walk": "도보 약 5km", "lodge": "에어비앤비"},
    {"date": "6/1 (월) — 아라시야마", "items": [
        ("09:00", "죽림길 (지쿠린)", "Arashiyama Bamboo Grove"),
        ("09:45", "텐류지 정원", "Tenryu-ji Temple"),
        ("12:00", "두부 가이세키 점심", "Arashiyama"),
        ("14:00", "금각사 (鹿苑寺)", "Kinkaku-ji"),
        ("15:30", "료안지 석정원", "Ryoan-ji"),
        ("18:30", "폰토초 저녁", "Pontocho Alley"),
    ], "walk": "도보 약 7km", "lodge": "에어비앤비 (2박째)"},
    {"date": "6/2 (화) — 후시미 + 료칸", "items": [
        ("07:30", "후시미 이나리 신사 (이른 시간 인파 회피)", "Fushimi Inari Taisha"),
        ("09:30", "토후쿠지 정원", "Tofuku-ji"),
        ("13:30", "우메코지 카덴쇼 체크인", "Umekoji Kadensho"),
        ("17:00", "료칸 대욕장 (천연식 온천)", "Umekoji Kadensho"),
        ("18:30", "가이세키 저녁", "Umekoji Kadensho"),
    ], "walk": "도보 약 4km", "lodge": "우메코지 카덴쇼 (2명×2실)"},
    {"date": "6/3 (수) — 출국", "items": [
        ("07:30", "료칸 조식 (포함)", "Umekoji Kadensho"),
        ("10:00", "토지 (東寺) 5중탑", "To-ji Temple"),
        ("14:00", "JR 하루카 → 간사이공항", "Kansai International Airport"),
        ("18:00", "출국", "Kansai International Airport"),
    ], "walk": "도보 약 3km", "lodge": "—"},
]


def card_itinerary(d) -> str:
    days = []
    for day in ITINERARY:
        items_html = []
        for time, name, query in day["items"]:
            map_url = f"https://maps.google.com/?q={esc(query.replace(' ', '+'))}"
            items_html.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(time)}</span> <a href="{map_url}" target="_blank" rel="noopener">{esc(name)}</a></div>
    </div>""")
        days.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['date'])}</div>
    {''.join(items_html)}
    <div class="sub" style="margin-top:0.4rem;">{esc(day['walk'])} · 숙박: {esc(day['lodge'])}</div>
  </div>""")
    return f"""
<!-- SYNC: docs/kyoto-itinerary-may-2026.md (5/24~27 → 5/31~6/3 평행 이동) · scripts/build_index.py ITINERARY -->
<section id="itinerary" class="card">
  <h2>일자별 일정</h2>
  <div class="sub" style="margin-bottom:0.5rem;">장소 탭 → 구글맵.</div>
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
  {''.join(rows)}
</section>
"""


def card_score(d) -> str:
    score = d["score"]
    rows = []
    max_score = max((s["score"] for s in score["scored"]), default=10)
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


# ─── 메인 ──────────────────────────────────────────────────────────────────

HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#fafafa" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1a1a1a" media="(prefers-color-scheme: dark)">
<title>일본 여행 최종 결정</title>
<style>
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
  footer { color: var(--muted); font-size: 0.75rem; margin-top: 1.5rem; text-align: center; }
</style>
</head>
<body>

<h1>일본 여행 최종 결정</h1>
<div class="status">교토 5/31~6/3 시나리오 (시부모 4인 확정). 본 페이지는 <code>scripts/build_index.py</code> 산출물 — 직접 편집 금지.</div>

<nav>
  <a href="#summary">요약</a>
  <a href="#airbnb">에어비앤비</a>
  <a href="#kadensho">카덴쇼</a>
  <a href="#flights">항공</a>
  <a href="#budget">예산</a>
  <a href="#itinerary">일정</a>
  <a href="#checklist">체크리스트</a>
  <a href="#score">점수</a>
</nav>
"""

FOOTER = f"""
<div class="links">
  <a href="{GH_BLOB}/reports/final-report.md" target="_blank" rel="noopener">최종 보고서</a>
  <a href="{GH_BLOB}/docs/airbnb-kyoto-may31-jun2-2026.md" target="_blank" rel="noopener">에어비앤비 비교 상세</a>
  <a href="{GH_BLOB}/docs/kyoto-itinerary-may-2026.md" target="_blank" rel="noopener">상세 일정</a>
  <a href="viz/dashboard.html">민감도 대시보드</a>
</div>

<footer>data/decision.json · data/cost-options.json · data/booking-checklist.json 단일 출처 · scripts/build_index.py 산출</footer>

</body>
</html>
"""


def build() -> str:
    d = load_data()
    sections = [
        card_summary(d),
        card_airbnb(d),
        card_kadensho(d),
        card_flights(d),
        card_budget(d),
        card_itinerary(d),
        card_checklist(d),
        card_score(d),
    ]
    return HEAD + "\n".join(sections) + FOOTER


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="빌드 결과와 디스크 diff (drift 시 exit 1)")
    args = parser.parse_args()

    rendered = build()
    if args.check:
        existing = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if existing != rendered:
            print("DRIFT: index.html out of sync. Run `python scripts/build_index.py` and commit.", file=sys.stderr)
            return 1
        print("index.html in sync.")
        return 0

    OUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(BASE)} ({len(rendered):,} bytes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
