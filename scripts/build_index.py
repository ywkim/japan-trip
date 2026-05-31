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
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path
from urllib.parse import quote

import markdown

BASE = Path(__file__).resolve().parent.parent
SCRIPTS = BASE / "scripts"
DATA = BASE / "data"
DOCS = BASE / "docs"
OUT_INDEX = BASE / "index.html"
OUT_ITINERARY = BASE / "viz" / "itinerary.html"
OUT_CHECKLIST = BASE / "viz" / "checklist.html"

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


# ─── 문서 렌더 페이지 (레포 마크다운 → 사이트 내 HTML) ───────────────────────
# Vercel 산출물에는 GitHub 링크 금지(검사 J). 외부 참조 문서는 레포로 빠져나가는
# 대신 여기 등록한 마크다운을 사이트 내부 HTML로 렌더해 그 페이지로 연결한다.
DocPage = namedtuple("DocPage", "source out title description og_slug tab back_href back_label")

DOC_PAGES = (
    DocPage(
        "reports/final-report.md", "viz/report.html",
        "최종 보고서 · 교토 가족여행 2026",
        "2026-05-12 의사결정 종료 시점 최종 보고서 (아카이브)",
        "archive", "home", "archive.html", "← 아카이브",
    ),
    DocPage(
        "docs/kyoto-itinerary-may31-jun3-2026.md", "viz/itinerary-doc.html",
        "교토 일정 문서 · 5/31~6/3",
        "교토 3박 4일 일자별 시나리오 (사람용 문서)",
        "itinerary", "itinerary", "itinerary.html", "← 일정",
    ),
    DocPage(
        "docs/booking-research-2026-05-24.md", "viz/research.html",
        "예약 리서치 · 보험·eSIM·환전",
        "미정 예약 4항목 실시간 리서치 (2026-05-24)",
        "checklist", "checklist", "checklist.html", "← 예약",
    ),
    DocPage(
        "docs/transit-pass-jr-kansai-2026.md", "viz/transit-pass.html",
        "JR 간사이 패스 비교",
        "JR 간사이 에어리어 패스 1/2/3/4일권 비교·권장",
        "checklist", "checklist", "checklist.html", "← 예약",
    ),
    DocPage(
        "docs/decision-log/2026-05-11-may31-jun3-kyoto-update.md", "viz/decision-kyoto.html",
        "교토 일정 변경 결정 (2026-05-11)",
        "5/24~27 → 5/31~6/3 변경 + 카덴쇼 가용 재확인",
        "archive", "home", "decision-log.html", "← 결정 일지",
    ),
    DocPage(
        "docs/icoca-iphone-setup.md", "viz/icoca-setup.html",
        "ICOCA 아이폰(Apple Wallet) 셋업 가이드",
        "출국 전 4인 ICOCA 설정 및 초기 충전 가이드 (2026-05-25)",
        "checklist", "checklist", "checklist.html", "← 예약",
    ),
    DocPage(
        "docs/essential-iphone-apps.md", "viz/essential-iphone-apps.html",
        "필수 아이폰 앱 가이드",
        "교토 여행 필수 앱 5개 설치·설정·운영 가이드 (2026-05-28)",
        "checklist", "checklist", "checklist.html", "← 예약",
    ),
)

DOC_SOURCE_TO_OUT = {p.source: p.out for p in DOC_PAGES}
DECISION_LOG_OUT = "viz/decision-log.html"


def doc_href(out_rel: str, in_viz: bool) -> str:
    """문서 페이지(viz/*.html)로의 상대 링크. 루트(index.html)면 그대로, viz/ 페이지면 prefix 제거."""
    return out_rel.split("/", 1)[1] if in_viz else out_rel


def esc(s) -> str:
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


_URL_RE = re.compile(r"(https?://[^\s)]+)")
# 마크다운 [라벨](url) — url은 http(s) 또는 tel: 만 허용 (javascript: 등 차단)
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((tel:[^)\s]+|https?://[^)\s]+)\)")


def _autolink(s) -> str:
    """벌거벗은 http(s) URL을 새 탭 <a>로, 나머지는 HTML escape."""
    parts = _URL_RE.split(s)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # 캡처된 URL
            url = esc(part)
            out.append(f'<a href="{url}" target="_blank" rel="noopener">{url}</a>')
        else:
            out.append(esc(part))
    return "".join(out)


def linkify(s) -> str:
    """자유 텍스트를 HTML escape하되 클릭 가능한 링크로 변환.

    - 마크다운 `[라벨](url)`: url이 http(s)면 새 탭, `tel:`이면 전화 탭(라벨 표시).
    - 벌거벗은 http(s) URL: 원문을 라벨로 한 새 탭 링크.
    체크리스트 노트 등 예약 채널·전화·출처가 모바일에서 탭으로 열리도록 한다.
    """
    if s is None:
        return ""
    s = str(s)
    out = []
    pos = 0
    for m in _MD_LINK_RE.finditer(s):
        out.append(_autolink(s[pos:m.start()]))
        label = esc(m.group(1))
        href = esc(m.group(2))
        if m.group(2).startswith("tel:"):
            out.append(f'<a href="{href}">{label}</a>')
        else:
            out.append(f'<a href="{href}" target="_blank" rel="noopener">{label}</a>')
        pos = m.end()
    out.append(_autolink(s[pos:]))
    return "".join(out)


def won(n: int) -> str:
    return f"₩{n:,}"


def maps_link(query: str, label: str) -> str:
    q = esc(query.replace(" ", "+"))
    return f'<a href="https://maps.google.com/?q={q}" target="_blank" rel="noopener">{esc(label)}</a>'


# ─── 장소 레지스트리 (병기 단일 출처) ────────────────────────────────────────
# data/itinerary.json의 "places"가 장소명 ko/ja 병기의 유일한 출처.
# 산문 필드(note·food_quality·pass_recommendation·route)는 {{place_id}}로 참조하고,
# 빌드 시 'ko(ja)'로 확장한다 — 같은 장소가 문서 전체에서 동일하게 병기된다.
# validate.py 검사 K가 (1) 미정의 참조, (2) 참조/병기 없는 생(生) 장소명을 차단한다.
PLACE_REGISTRY: dict = {}
PLACE_REF_RE = re.compile(r"\{\{([a-z0-9_]+)\}\}")
# 확장된 'ko(ja)' 라벨 → reading(일본어 발음 한글표기) 역방향 맵.
# 교통 타임라인이 역·정류장 발음을 노출하기 위해 load_data에서 채운다.
PLACE_LABEL_TO_READING: dict = {}


def build_place_reading_map() -> dict:
    """PLACE_REGISTRY에서 확장 라벨('ko(ja)' 또는 'ko') → reading 맵을 만든다."""
    m = {}
    for p in PLACE_REGISTRY.values():
        reading = (p.get("reading") or "").strip()
        if not reading:
            continue
        ko, ja = p.get("ko", ""), p.get("ja", "")
        label = f"{ko}({ja})" if ja else ko
        m[label] = reading
    return m


def expand_place_refs(text: str) -> str:
    """문자열 내 {{place_id}}를 레지스트리의 'ko(ja)' 병기로 확장.

    미정의 id는 원문({{id}})을 그대로 남겨 validate.py 검사 K가 잡도록 한다.
    """
    if not text or "{{" not in text:
        return text

    def sub(m):
        pid = m.group(1)
        p = PLACE_REGISTRY.get(pid)
        if not p:
            return m.group(0)
        ko, ja = p.get("ko", ""), p.get("ja", "")
        return f"{ko}({ja})" if ja else ko

    return PLACE_REF_RE.sub(sub, text)


def expand_refs_in_obj(obj):
    """중첩 dict/list의 모든 문자열 값에서 {{place_id}}를 확장 (재귀)."""
    if isinstance(obj, dict):
        return {k: expand_refs_in_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_refs_in_obj(v) for v in obj]
    if isinstance(obj, str):
        return expand_place_refs(obj)
    return obj


# ─── New schema (Work 4) helper functions ───────────────────────────────────

def is_new_schema_title(title) -> bool:
    """Check if title is in new schema (dict with ko_name, ja_name, etc)."""
    return isinstance(title, dict) and "ko_name" in title


def is_new_schema_arrive_from(af) -> bool:
    """Check if arrive_from is in new schema (has steps array)."""
    return isinstance(af, dict) and isinstance(af.get("steps"), list)


def render_title_display(title) -> str:
    """Render title for display, supporting both old and new schema.

    New schema: {type, ko_name, ja_name, ja_reading_ko, en_name}
    Old schema: string

    Returns plain text (no HTML escaping here - caller handles <a> wrapping).
    """
    if isinstance(title, str):
        return title

    if not is_new_schema_title(title):
        return str(title)

    # New schema: build display string from components
    ko_name = title.get("ko_name", "").strip()
    ja_name = title.get("ja_name", "").strip()
    ja_reading = title.get("ja_reading_ko", "").strip()

    # Render as: "ko_name (ja_name)" or "ko_name (ja_reading)" if ja_name missing
    parts = [ko_name]
    if ja_name:
        parts.append(f"({ja_name})")
    elif ja_reading:
        parts.append(f"({ja_reading})")

    return " ".join(parts)


def title_reading_html(title) -> str:
    """발음 줄 렌더 (🗣️ {ja_reading_ko}). title이 dict이고 ja_reading_ko가 있으면 HTML, 없으면 빈 문자열."""
    if not isinstance(title, dict):
        return ""
    reading = title.get("ja_reading_ko", "").strip()
    if not reading:
        return ""
    return f'<div class="pron">🗣️ {esc(reading)}</div>'


def _station_label(value) -> str:
    """from/to 값에서 화면용 라벨을 얻는다.

    신스키마: from/to는 '{{place_id}}' 문자열이 expand_refs_in_obj로 이미
    'ko(ja)'로 확장된 상태(예: '니조역(二条駅)'). 그대로 사용.
    """
    if isinstance(value, str):
        return value.strip()
    # 안전망: 구 dict 형태가 남아 있으면 ko(ja)로 합성
    if isinstance(value, dict):
        ko, ja = value.get("ko", ""), value.get("ja", "")
        return f"{ko}({ja})" if ko and ja else (ko or "")
    return ""


def _segment_pill(step: dict) -> str:
    """이동 수단 pill 라벨 (아이콘 + 운영사·노선). 색이 아니라 아이콘·텍스트로 구분.

    Quiet Gray 테마: 운영사별 브랜드색(빨강·파랑) 도입 금지 — 단일 accent 유지.
    """
    mode = step.get("mode")
    operator = step.get("operator") or {}
    op_ko = operator.get("ko") if isinstance(operator, dict) else ""
    icon = MODE_ICONS.get(mode, "·")
    if mode == "bus":
        text = op_ko or "버스"
        number = step.get("number")
        if number:
            text += f" {number}번"
    elif mode == "jr":
        jr_line = step.get("line")
        text = f"JR {jr_line}" if jr_line else "JR"
    elif mode == "airport_express":
        text = op_ko or "공항특급"
    elif mode == "walk":
        text = "도보"
    else:
        text = MODE_VERBS.get(mode, "이동")
    return f'<span class="tl-mode">{icon} {esc(text)}</span>'


def _segment_meta(step: dict) -> str:
    """분·거리·요금 메타 (tabular-nums). 없으면 빈 문자열."""
    parts = []
    if step.get("duration_min"):
        parts.append(f'{step["duration_min"]}분')
    if step.get("distance_km"):
        parts.append(f'{step["distance_km"]}km')
    if step.get("fare_jpy"):
        parts.append(f'¥{step["fare_jpy"]}')
    if not parts:
        return ""
    return f'<span class="tl-meta">{esc(" · ".join(parts))}</span>'


def _render_transit_timeline(steps: list) -> str:
    """역·정류장 from/to가 있는 steps를 세로 레일 타임라인으로 렌더.

    - 각 step.from을 도트 노드로(첫 step은 출발, 이후 step의 from은 환승점),
      마지막 step.to를 도착 노드로 렌더 → 노드 사이를 레일 선이 잇는다.
    - 환승점은 강조 도트 + '환승' 태그. 운영사/소요/요금은 도트 옆 pill·메타.
    인접 step이 to[i]==from[i+1]로 이어진다는 전제(우리 데이터의 환승 모델).
    """
    parts = ['<div class="tl">']
    for i, step in enumerate(steps):
        from_label = _station_label(step.get("from"))
        is_transfer = i > 0
        dot_cls = "tl-dot transfer" if is_transfer else "tl-dot start"
        rail = f'<span class="{dot_cls}"></span><span class="tl-line"></span>'
        station = f'<div class="tl-station">{esc(from_label)}'
        if is_transfer:
            station += '<span class="tl-tag">환승</span>'
        station += '</div>'
        station += _station_reading_html(from_label)
        seg = f'<div class="tl-seg">{_segment_pill(step)}{_segment_meta(step)}</div>'
        parts.append(
            f'<div class="tl-node"><div class="tl-rail">{rail}</div>'
            f'<div class="tl-content">{station}{seg}</div></div>'
        )
    to_label = _station_label(steps[-1].get("to"))
    parts.append(
        f'<div class="tl-node"><div class="tl-rail"><span class="tl-dot end"></span></div>'
        f'<div class="tl-content"><div class="tl-station">{esc(to_label)}</div>'
        f'{_station_reading_html(to_label)}</div></div>'
    )
    parts.append('</div>')
    return ''.join(parts)


def _station_reading_html(label: str) -> str:
    """확장 라벨('ko(ja)')에 대응하는 역·정류장 발음 줄. 없으면 빈 문자열."""
    reading = PLACE_LABEL_TO_READING.get(label.strip())
    if not reading:
        return ""
    return f'<div class="tl-reading">🗣️ {esc(reading)}</div>'


def _render_transit_simple(steps: list) -> str:
    """역 정보가 없는 steps(도보 등)를 간결한 pill 줄로 렌더."""
    rows = []
    for step in steps:
        rows.append(f'<div class="tl-simple">{_segment_pill(step)}{_segment_meta(step)}</div>')
    return ''.join(rows)


def render_transit_line_steps(steps: list, af_dict: dict) -> str:
    """새 스키마 arrive_from를 '역 타임라인'으로 렌더 (모바일 ONE LONG STRING 해소).

    - 접힘 요약: 모드별 한국어 동사 + 총 소요시간(+환승 횟수). 길게 늘어지지 않음.
    - 펼침 상세: 세로 레일 + 역·정류장 도트 타임라인(역 기반 leg) 또는 간결 pill(도보).
    - 운영사/노선은 색이 아니라 아이콘+pill로 구분 (Quiet Gray: 단일 accent 유지).
    - af_dict.advisory(선택)는 warn 보더 안내 박스.
    """
    if not steps:
        return ""

    ride_modes = ("bus", "jr", "subway", "train", "airport_express")
    rides = [s for s in steps if s.get("mode") in ride_modes]
    transfers = max(0, len(rides) - 1)
    total_dur = sum(s.get("duration_min") or 0 for s in steps)
    primary = rides[0] if rides else steps[0]
    icon = MODE_ICONS.get(primary.get("mode"), "·")
    verb = MODE_VERBS.get(primary.get("mode"), "이동")
    if transfers >= 1:
        summary = f"{icon} {verb} 환승 {transfers}회 · 약 {total_dur}분"
    elif total_dur:
        summary = f"{icon} {verb} {total_dur}분"
    else:
        summary = f"{icon} {verb}"

    # 지도 버튼
    maps_url = (af_dict.get("maps_url") or "").strip()
    src = (af_dict.get("source") or "").strip()
    first_token = src.split()[0] if src else ""
    src_href = first_token if first_token.startswith(("http://", "https://")) else ""
    href = maps_url or src_href
    if href:
        summary += f' <a href="{esc(href)}" target="_blank" rel="noopener" class="maps-btn">지도 ↗</a>'

    station_based = all(
        _station_label(s.get("from")) and _station_label(s.get("to")) for s in steps
    )
    detail = _render_transit_timeline(steps) if station_based else _render_transit_simple(steps)

    advisory = (af_dict.get("advisory") or "").strip()
    if advisory:
        detail += f'<div class="tl-advisory">⚠️ {esc(advisory)}</div>'

    return fold(summary, detail)


_PLACE_MARKUP_RE = re.compile(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")
_PLACEHOLDER_RE = re.compile(r"__PLACE_LINK_\d+__")


def strip_place_markup(text: str) -> str:
    """note 텍스트에서 wiki 마크업 [[label|query]]을 제거하고 label만 남긴다.

    memo_block의 길이 판정용 — 보이는 텍스트 길이로 계산하도록.
    """
    if not text:
        return text
    return _PLACE_MARKUP_RE.sub(r"\1", text)


def link_places(text: str) -> str:
    """note 텍스트의 위키식 마크육 [[label|query]]을 Google Maps 링크로 변환.

    - [[label|query]]: label을 query로 검색
    - [[label]]: label을 query로 사용
    나머지 텍스트는 linkify()로 처리해 URL도 링크화하고 HTML escape.

    double-escape 방지: markup을 먼저 처리해 placeholder로 치환, 나머지 텍스트를 escape+linkify,
    마지막에 placeholder를 실제 HTML로 복구.
    """
    if not text:
        return text

    placeholders = {}
    counter = [0]

    def store_markup(m):
        label = m.group(1)
        query = m.group(2) or label
        placeholder = f"__PLACE_LINK_{counter[0]}__"
        placeholders[placeholder] = maps_link(query, label)
        counter[0] += 1
        return placeholder

    text = _PLACE_MARKUP_RE.sub(store_markup, text)
    text = linkify(text)

    for placeholder, html in placeholders.items():
        text = text.replace(esc(placeholder), html)

    return text


def lodging_photo_strip(photos: list, img_prefix: str = "") -> str:
    """photos: list of (filename, alt) — renders a horizontal scroll strip."""
    if not photos:
        return ""
    imgs = "".join(
        f'<img src="{esc(img_prefix + "assets/lodging/" + fname)}" alt="{esc(alt)}" class="lodging-thumb" loading="lazy">'
        for fname, alt in photos
    )
    return f'<div class="lodging-strip">{imgs}</div>'


def blog_reviews_html(reviews: list) -> str:
    """Render a scrollable photo strip of Naver blog reviews."""
    if not reviews:
        return ""
    cards = "".join(
        f'<a href="{esc(r["url"])}" target="_blank" rel="noopener" class="blog-card">'
        f'<img src="{esc(r["img"])}" class="blog-thumb" loading="lazy" alt="" referrerpolicy="no-referrer">'
        f'<p class="blog-comment">{esc(r["comment"])}</p>'
        f'</a>'
        for r in reviews
    )
    return f'<div class="blog-reviews"><div class="blog-strip">{cards}</div></div>'


def food_quality_html(fq) -> str:
    """식사 항목 평점·출처 배지 (data/itinerary.json food_quality).

    url(평점 출처 페이지)이 있으면 평점을 탭 가능한 링크로 감싼다 — 모바일에서
    "타베로그 3.x"를 눌러 실제 리뷰 페이지를 확인할 수 있게(검증 가능성).
    """
    if not fq:
        return ""
    rating = esc(fq.get("rating", ""))
    body = f"🍽️ {rating}"
    url = (fq.get("url") or "").strip()
    if url.startswith(("http://", "https://")):
        body = f'<a href="{esc(url)}" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline;">{body}</a>'
    michelin_url = (fq.get("michelin_url") or "").strip()
    if michelin_url.startswith(("http://", "https://")):
        body += (
            f' · <a href="{esc(michelin_url)}" target="_blank" rel="noopener" '
            f'style="color:inherit;text-decoration:underline;">미쉐린 가이드</a>'
        )
    src = esc((fq.get("source") or "").strip())
    src_html = f' <span style="opacity:0.65;">· 출처: {src}</span>' if src else ""
    note_html = memo_block(fq.get("note"), style="font-size:0.8em;opacity:0.7;margin-top:0.1rem;")
    return (
        f'<div class="food-quality" style="font-size:0.85em;margin-top:0.25rem;color:var(--muted);">'
        f'{body}{src_html}</div>{note_html}'
    )


def doc_link_html(link, in_viz: bool = False) -> str:
    """일정 항목 참조 문서 링크 (data/itinerary.json item.link = {url, label}).

    조식 슬롯 등이 가리키는 문서를 화면에서 바로 탭해 열 수 있는 <a>로 렌더.
    url이 사이트 내 상대 경로면 같은 탭 내비게이션, 외부(http)면 새 탭으로 연다.
    Vercel은 .md를 raw로 서빙하므로 운영 화면 링크는 사이트 내 HTML 페이지를
    가리킨다(예: 조식 슬롯 → breakfast.html). 외부 GitHub blob 링크 금지.
    in_viz=False(루트 index.html)일 때 viz-상대 경로에 viz/ 접두어 추가.
    """
    link = link or {}
    url = (link.get("url") or "").strip()
    if not url:
        return ""
    # viz-상대 경로(breakfast.html 등)를 루트에서 렌더할 때 viz/ 접두어 보정
    if not in_viz and url.endswith(".html") and not url.startswith(("http://", "https://", "viz/", "/", "#")):
        url = "viz/" + url
    label = esc(link.get("label", "상세"))
    external = url.startswith(("http://", "https://"))
    attr = ' target="_blank" rel="noopener"' if external else ""
    return f'<a class="doc-link" href="{esc(url)}"{attr}>{label} ↗</a>'


def run_json(script: str) -> dict:
    res = subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--json"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(res.stdout)


def load_data():
    itinerary = json.loads((DATA / "itinerary.json").read_text(encoding="utf-8"))
    # 장소 레지스트리를 모듈 전역에 적재 후 {{place_id}} 참조를 'ko(ja)'로 확장.
    global PLACE_REGISTRY, PLACE_LABEL_TO_READING
    PLACE_REGISTRY = itinerary.get("places", {})
    PLACE_LABEL_TO_READING = build_place_reading_map()
    itinerary = expand_refs_in_obj(itinerary)
    return {
        "decision": json.loads((DATA / "decision.json").read_text(encoding="utf-8")),
        "cost": json.loads((DATA / "cost-options.json").read_text(encoding="utf-8")),
        "weather": json.loads((DATA / "weather.json").read_text(encoding="utf-8")),
        "itinerary": itinerary,
        "checklist": json.loads((DATA / "booking-checklist.json").read_text(encoding="utf-8")),
        "breakfast": json.loads((DATA / "breakfast.json").read_text(encoding="utf-8")),
        "tokens": json.loads((DATA / "design-tokens.json").read_text(encoding="utf-8")),
        "score": run_json("score.py"),
        "budget": run_json("budget.py"),
    }


# ─── 공통 스타일 ───────────────────────────────────────────────────────────

def render_css(tokens: dict) -> str:
    """data/design-tokens.json → <style> 본문. 6개 산출물(index·itinerary·itinerary-table·lodging·checklist·archive) 공통."""
    cl = tokens["color"]["light"]
    cd = tokens["color"]["dark"]
    fs = tokens["typography"]["font_family_sans"]
    return f"""
  :root {{
    --bg: {cl['bg']}; --fg: {cl['ink']}; --muted: {cl['ink_muted']}; --border: {cl['border']};
    --accent: {cl['accent']}; --accent-soft: {cl['accent_soft']};
    --card: {cl['surface']}; --subcard: {cl['surface_sunken']};
    --ok: {cl['ok']}; --warn: {cl['warn']}; --danger: {cl['danger']};
    --bar-track: {cl['bar_track']};
    --font-sans: {fs};
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: {cd['bg']}; --fg: {cd['ink']}; --muted: {cd['ink_muted']}; --border: {cd['border']};
      --accent: {cd['accent']}; --accent-soft: {cd['accent_soft']};
      --card: {cd['surface']}; --subcard: {cd['surface_sunken']};
      --ok: {cd['ok']}; --warn: {cd['warn']}; --danger: {cd['danger']};
      --bar-track: {cd['bar_track']};
    }}
  }}
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }}
  body {{
    font-family: var(--font-sans);
    background: var(--bg); color: var(--fg);
    margin: 0 auto; padding: 1rem; max-width: 640px;
    line-height: 1.5; font-size: 16px;
  }}
  h1 {{ font-size: 1.4rem; margin: 0.5rem 0 0.25rem; }}
  h2 {{ font-size: 1rem; margin: 0 0 0.5rem; color: var(--muted); font-weight: 500; }}
  .status {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 1rem; }}
  nav {{ display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 1rem 0; }}
  nav a {{
    padding: 0.4rem 0.7rem; border: 1px solid var(--border); border-radius: 999px;
    text-decoration: none; color: var(--fg); font-size: 0.8rem; background: var(--card);
  }}
  nav a:hover {{ border-color: var(--accent); }}
  .card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 8px;
    padding: 1rem; margin: 0.75rem 0;
  }}
  @media (prefers-color-scheme: dark) {{
    .card {{ box-shadow: 0 1px 0 rgba(0,0,0,0.25); }}
  }}
  .subcard {{
    background: var(--subcard); border: 1px solid var(--border); border-radius: 6px;
    padding: 0.75rem; margin: 0.5rem 0;
  }}
  .subtitle {{ font-weight: 600; margin-bottom: 0.4rem; font-size: 0.95rem; }}
  .big {{ font-size: 1.6rem; font-weight: 600; line-height: 1.2; }}
  .sub {{ color: var(--muted); font-size: 0.85rem; margin-top: 0.25rem; word-break: keep-all; }}
  .row {{
    display: flex; justify-content: space-between; gap: 0.5rem;
    padding: 0.35rem 0; border-bottom: 1px solid var(--border);
  }}
  .row:last-child {{ border-bottom: none; }}
  .row .k {{ color: var(--muted); flex-shrink: 0; }}
  .row .v {{ font-variant-numeric: tabular-nums; text-align: right; word-break: keep-all; min-width: 0; overflow-wrap: anywhere; }}
  .bf-item {{ padding: 0.5rem 0; border-bottom: 1px solid var(--border); }}
  .bf-item:last-child {{ border-bottom: none; }}
  .bf-label {{ font-weight: 600; margin-bottom: 0.2rem; }}
  .bf-body {{ line-height: 1.5; word-break: keep-all; }}
  .bf-menu {{ margin-top: 0.3rem; font-size: 0.9rem; color: var(--fg); }}
  .bf-store {{ padding: 0.55rem 0; border-bottom: 1px solid var(--border); }}
  .bf-store:last-child {{ border-bottom: none; }}
  ul {{ padding-left: 1.2rem; margin: 0.3rem 0; }}
  li {{ margin: 0.2rem 0; }}
  .day {{ padding: 0.35rem 0; border-bottom: 1px solid var(--border); }}
  .day:last-child {{ border-bottom: none; }}
  .day .date {{ font-size: 0.9rem; }}
  .day .date .k {{ display: inline-block; min-width: 3.2rem; color: var(--fg); font-weight: 600; font-variant-numeric: tabular-nums; }}
  .pron {{ color: var(--muted); font-size: 0.8em; margin-top: 0.1rem; }}
  /* ── 접기(쉬운 설명 + 펼침 상세) ── */
  details.leg {{ margin: 0.15rem 0 0.35rem; }}
  details.leg > summary {{
    cursor: pointer; list-style: none; color: var(--muted);
    font-size: 0.82rem; padding: 0.1rem 0; -webkit-tap-highlight-color: transparent;
  }}
  details.leg > summary::-webkit-details-marker {{ display: none; }}
  details.leg > summary::before {{ content: '▸ '; color: var(--muted); }}
  details.leg[open] > summary::before {{ content: '▾ '; }}
  .leg-detail {{
    color: var(--muted); font-size: 0.8rem; line-height: 1.35;
    padding: 0.2rem 0 0.1rem 0.9rem; margin-top: 0.2rem;
    border-left: 2px solid var(--border);
  }}
  .leg-detail a {{ color: var(--fg); }}
  .day a {{ color: var(--fg); text-decoration: underline; text-decoration-color: var(--border); }}
  details.leg summary a.maps-btn {{
    display: inline-block; padding: 0.05em 0.35em; margin-left: 0.3em;
    border: 1px solid var(--accent); border-radius: 3px;
    font-size: 0.78em; text-decoration: none; color: var(--accent);
    vertical-align: middle; white-space: nowrap;
  }}
  .bar {{ height: 6px; background: var(--bar-track); border-radius: 3px; margin: 0.2rem 0 0.5rem; overflow: hidden; }}
  .bar-fill {{ height: 100%; background: var(--accent); }}
  .links {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.6rem; }}
  .links a {{
    flex: 1 1 auto; text-align: center; padding: 0.5rem 0.7rem;
    background: transparent; color: var(--fg); border: 1px solid var(--border);
    border-radius: 6px; text-decoration: none; font-size: 0.85rem;
  }}
  .links a:hover {{ border-color: var(--accent); }}
  .links a {{ min-height: 44px; display: inline-flex; align-items: center; justify-content: center; }}
  /* ── 출처 칩 (모바일 터치 타깃 ≥44px) ── */
  .source-row {{ display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; margin-top: 0.3rem; }}
  .source-link {{
    display: inline-flex; align-items: center; gap: 0.3rem;
    min-height: 44px; padding: 0.5rem 0.8rem; border-radius: 8px;
    background: var(--subcard); border: 1px solid var(--border);
    color: var(--fg); text-decoration: none; font-size: 0.78rem; line-height: 1.2;
    -webkit-tap-highlight-color: transparent;
  }}
  .source-link:hover {{ border-color: var(--accent); }}
  .source-link:active {{ opacity: 0.6; }}
  .source-tick {{ color: #2e9e5b; font-weight: 700; }}
  .source-label {{ color: var(--muted); font-size: 0.72rem; margin-right: 0.1rem; }}
  .badge {{
    display: inline-block; padding: 0.1rem 0.45rem; border-radius: 4px;
    font-size: 0.75rem; border: 1px solid currentColor;
    white-space: nowrap; flex-shrink: 0;
  }}
  /* ── 예약 체크리스트 ── */
  .ck-head {{ display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }}
  .ck-head .subtitle {{ margin: 0; }}
  .badge-done {{ color: var(--ok); border-color: var(--ok); }}
  .badge-pending {{ color: var(--warn); border-color: var(--warn); }}
  .badge-progress {{ color: var(--accent); border-color: var(--accent); }}
  .subcard.status-done {{ border-left: 3px solid var(--ok); }}
  .subcard.status-pending {{ border-left: 3px solid var(--warn); }}
  .subcard.status-progress {{ border-left: 3px solid var(--accent); }}
  .dday {{ font-size: 0.78rem; color: var(--muted); margin-left: 0.3rem; }}
  .dday.urgent {{ color: var(--danger); font-weight: 600; }}
  .dday.over {{ color: var(--muted); }}
  .doc-link {{
    display: inline-block; margin-top: 0.5rem; padding: 0.4rem 0.7rem;
    border: 1px solid var(--border); border-radius: 6px;
    text-decoration: none; color: var(--fg); font-size: 0.8rem;
  }}
  .doc-link:hover {{ border-color: var(--accent); }}
  .map-link {{ color: var(--accent); text-decoration: none; }}
  .map-link:hover {{ text-decoration: underline; }}
  footer {{ color: var(--muted); font-size: 0.75rem; margin-top: 1.5rem; text-align: center; }}
  /* ── 하단 탭바 ── */
  body {{ padding-bottom: calc(4.5rem + env(safe-area-inset-bottom, 0px)); }}
  .tab-bar {{
    position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 100%; max-width: 640px;
    display: flex; background: var(--card); border-top: 1px solid var(--border);
    z-index: 200; padding-bottom: env(safe-area-inset-bottom, 0px);
  }}
  .tab-bar::after {{
    content: ''; position: absolute; top: 100%; left: 0; right: 0;
    height: 80px; background: var(--card);
  }}
  .tab-bar a {{
    flex: 1; display: flex; flex-direction: column; align-items: center;
    padding: 0.6rem 0.25rem 0.45rem; text-decoration: none;
    color: var(--muted); font-size: 0.68rem; gap: 0.2rem; line-height: 1.2;
    -webkit-tap-highlight-color: transparent;
  }}
  .tab-bar a.active {{
    color: var(--fg); font-weight: 600;
  }}
  .tab-bar a:active {{ opacity: 0.6; }}
  .tab-bar .tab-icon {{ font-size: 1.25rem; line-height: 1; }}
  /* ── 이미지 ── */
  .place-img {{
    width: 100%; aspect-ratio: 16/9; object-fit: cover;
    border-radius: 4px; display: block; margin-top: 0.35rem;
    max-height: 200px;
  }}
  .img-credit {{ color: var(--muted); font-size: 0.65rem; text-align: right; }}
  .blog-reviews {{ margin-top: 0.5rem; }}
  .blog-strip {{ display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 0.3rem; -webkit-overflow-scrolling: touch; }}
  .blog-card {{ flex: 0 0 140px; text-decoration: none; color: var(--fg); border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }}
  .blog-thumb {{ width: 140px; height: 100px; object-fit: cover; display: block; }}
  .blog-comment {{ font-size: 0.7rem; padding: 0.3rem; margin: 0; color: var(--muted); line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
  /* ── 숙소 사진 스트립 ── */
  .lodging-strip {{ display: flex; gap: 0.5rem; overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; padding-bottom: 0.25rem; margin: 0.6rem 0 0.4rem; }}
  .lodging-strip::-webkit-scrollbar {{ display: none; }}
  .lodging-thumb {{ flex: 0 0 200px; height: 134px; object-fit: cover; border-radius: 8px; display: block; }}
  /* ── 이동 경로 타임라인 (역·정류장 노드 + 환승) ── */
  .tl {{ margin: 0.1rem 0 0.05rem; }}
  .tl-node {{ display: flex; gap: 0.55rem; align-items: stretch; }}
  .tl-rail {{ display: flex; flex-direction: column; align-items: center; flex-shrink: 0; width: 11px; }}
  .tl-dot {{
    width: 9px; height: 9px; border-radius: 50%; margin-top: 3px; flex-shrink: 0;
    background: var(--accent); box-shadow: 0 0 0 2px var(--card), 0 0 0 3px var(--accent);
  }}
  .tl-dot.transfer {{ background: var(--warn); box-shadow: 0 0 0 2px var(--card), 0 0 0 3px var(--warn); }}
  .tl-line {{ width: 2px; flex: 1 0 auto; min-height: 1.3rem; background: var(--border); margin: 2px 0; }}
  .tl-content {{ flex: 1; min-width: 0; padding-bottom: 0.5rem; }}
  .tl-node:last-child .tl-content {{ padding-bottom: 0; }}
  .tl-station {{ color: var(--fg); font-weight: 500; font-size: 0.92em; line-height: 1.35; word-break: keep-all; }}
  .tl-reading {{ color: var(--muted); font-size: 0.78em; line-height: 1.3; margin-top: 0.05rem; }}
  .tl-tag {{
    display: inline-block; margin-left: 0.35rem; padding: 0 0.4rem;
    font-size: 0.72em; font-weight: 600; color: var(--warn);
    border: 1px solid var(--warn); border-radius: 999px; vertical-align: middle; white-space: nowrap;
  }}
  .tl-seg {{ display: flex; align-items: center; flex-wrap: wrap; gap: 0.3rem 0.4rem; margin-top: 0.25rem; }}
  .tl-mode {{
    display: inline-flex; align-items: center; gap: 0.25rem; white-space: nowrap;
    padding: 0.1rem 0.5rem; border-radius: 999px;
    background: var(--accent-soft); color: var(--accent);
    font-size: 0.78em; font-weight: 600;
  }}
  .tl-meta {{ color: var(--muted); font-size: 0.78em; font-variant-numeric: tabular-nums; }}
  .tl-simple {{ display: flex; align-items: center; flex-wrap: wrap; gap: 0.3rem 0.4rem; padding: 0.1rem 0; }}
  .tl-advisory {{
    margin-top: 0.45rem; padding: 0.4rem 0.55rem;
    border-left: 2px solid var(--warn); background: var(--subcard);
    border-radius: 0 4px 4px 0; color: var(--fg);
    font-size: 0.82em; line-height: 1.4; word-break: keep-all;
  }}
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
    tokens: dict,
    description: str,
    og_slug: str,
    page_path: str,
    extra_css: str = "",
) -> str:
    css = render_css(tokens) + extra_css
    meta = og_meta(title=title, description=description, slug=og_slug, page_path=page_path)
    bg_light = tokens["color"]["light"]["bg"]
    bg_dark = tokens["color"]["dark"]["bg"]
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="{bg_light}" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="{bg_dark}" media="(prefers-color-scheme: dark)">
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
  <div class="sub" style="margin-top:0.5rem;">발권·예약 완료 (항공 A8YW58 · 시오 마치야 · 카덴쇼 트립닷컴). 출국 전 점검은 ☑ 예약 탭.</div>
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


def card_airbnb(d, img_prefix: str = "") -> str:
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
    photos = lodging_photo_strip([
        ("shio-exterior.jpg", "외관 · 汐 노렌"),
        ("shio-room-1.jpg", "다다미방 · 정원 뷰"),
        ("shio-room-2.jpg", "다다미방 · 달창"),
    ], img_prefix=img_prefix)
    return f"""
<!-- SYNC: data/cost-options.json (lodging.airbnb_shio_machiya) · docs/airbnb-kyoto-may31-jun2-2026.md -->
<section id="airbnb" class="card">
  <h2>에어비앤비 · 시오(Shio) 100년 마치야 <span class="badge badge-done">확정</span></h2>
  {photos}
  <div class="row"><span class="k">일정</span><span class="v">5/31~6/2 · 2박</span></div>
  <div class="row"><span class="k">위치</span><span class="v">중교구 · 니조역 도보 7분</span></div>
  <div class="row"><span class="k">2박 총액</span><span class="v">{esc(won(two_night))}</span></div>
  <div class="row"><span class="k">1인 1박</span><span class="v">{esc(won(l['per_night_krw'] // 4))}</span></div>
  {note_block(l.get('notes', ''), style='margin-top:0.4rem;')}
  <div class="links">{link_html}</div>
</section>
"""


def card_kadensho(d, img_prefix: str = "") -> str:
    items = [l for l in d["cost"]["lodging"] if l["id"] == "kadensho_tripcom_no_meal_2026jun2"]
    cards = []
    for l in items:
        cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(l['name'])}</div>
    <div class="row"><span class="k">1박 (4인, 객실 2개)</span><span class="v">{esc(won(l['per_night_krw']))}</span></div>
    {note_block(l.get('notes', ''))}
  </div>""")
    photos = lodging_photo_strip([
        ("kadensho-exterior.jpg", "외관 · 花伝抄"),
        ("kadensho-bath-hinoki.jpg", "히노키 욕조"),
        ("kadensho-bath-outdoor.jpg", "노천탕 · 대나무 정원"),
        ("kadensho-bath-rock.jpg", "암반탕"),
    ], img_prefix=img_prefix)
    return f"""
<!-- SYNC: data/cost-options.json (lodging.kadensho_tripcom_no_meal_2026jun2) · data/booking-checklist.json (ryokan) -->
<section id="kadensho" class="card">
  <h2>우메코지 카덴쇼 (6/2 1박) <span class="badge badge-done">확정</span></h2>
  {photos}
  {note_block("트립닷컴 예약번호 1400825991981904 · 2026-05-13 확정 · 숙소 현지결제.", style="margin-bottom:0.5rem;")}
  {''.join(cards)}
</section>
"""


def card_flights(d) -> str:
    items = [f for f in d["cost"]["flights"] if f["id"] == "rs_kix_may31_jun3"]
    cards = []
    for f in items:
        cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(f['label'])}</div>
    <div class="row"><span class="k">일자</span><span class="v">{esc(f['depart_date'])} → {esc(f['return_date'])}</span></div>
    <div class="row"><span class="k">4인 총액</span><span class="v">{esc(won(f['total_krw']))}</span></div>
    {note_block("에어서울 RS · 예약번호 A8YW58 · 2026-05-12 확정 (시부 결제). ICN 13:15→KIX 15:15 / KIX 10:05→ICN 12:05.")}
  </div>""")
    return f"""
<!-- SYNC: data/cost-options.json (flights.rs_kix_may31_jun3) · data/booking-checklist.json (flight) -->
<section id="flights" class="card">
  <h2>항공 (확정)</h2>
  {''.join(cards)}
</section>
"""


def card_budget(d) -> str:
    budget = d["budget"]
    selected_html = ""
    others = []
    for s in budget["scenarios"]:
        marker = "통과" if s["passes_cap"] else "초과"
        head = won(s["headroom_krw"]) if s["headroom_krw"] >= 0 else f"−{won(-s['headroom_krw'])}"
        is_selected = s["id"] == SCENARIO_ID
        highlight = ' style="border-color: var(--accent); border-width: 2px;"' if is_selected else ""
        cats = []
        for c in s["categories"]:
            dim = ' style="color:var(--muted)"' if c["status"] == "ok" else (' style="font-weight:600"' if c["status"] == "over" else "")
            cats.append(f'<div class="row"><span class="k">{esc(c["label"])}</span><span class="v"{dim}>{esc(won(c["actual_krw"]))} ({c["actual_pct"]}%)</span></div>')
        subcard = f"""
  <div class="subcard"{highlight}>
    <div class="subtitle">{marker} {esc(s['label'])}</div>
    <div class="row"><span class="k">확정 합계</span><span class="v">{esc(won(s['confirmed_total_krw']))}</span></div>
    <div class="row"><span class="k">3M 여유</span><span class="v">{esc(head)}</span></div>
    {''.join(cats)}
  </div>"""
        if is_selected:
            selected_html = subcard
        else:
            others.append(subcard)

    others_html = ""
    if others:
        others_html = fold(f"다른 예산 시나리오 {len(others)}개 보기", "".join(others))
    return f"""
<!-- SYNC: scripts/budget.py --json · data/cost-options.json (scenarios) -->
<section id="budget" class="card">
  <h2>예산 시뮬 (3M 캡 = {esc(won(budget['cap_krw']))})</h2>
  <div class="sub" style="margin-bottom:0.5rem;">확정 항목만 기준. 굵은 테두리 = 현재 선택 시나리오.</div>
  {selected_html}
  {others_html}
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

MODE_VERBS = {
    "walk": "걸어서",
    "bus": "버스로",
    "subway": "지하철로",
    "train": "전철로",
    "jr": "전철로",
    "airport_express": "공항특급으로",
    "taxi": "택시로",
}


def fold(summary_html: str, detail_html: str, *, open: bool = False) -> str:
    """평이 요약(summary) + 펼침 상세(details)로 감싸는 재사용 헬퍼."""
    open_attr = " open" if open else ""
    return (
        f'<details class="leg"{open_attr}><summary>{summary_html}</summary>'
        f'<div class="leg-detail">{detail_html}</div></details>'
    )


def note_block(note: str, *, style: str = "") -> str:
    """예약·숙박 메모를 짧으면 평문, 길면 '앞 항목 요약 + 접기'로 렌더.

    ' · '로 구분된 장문 운영 메모(예약번호·PIN·탑승객·체크인시각 등)가
    카드를 압도하지 않도록, 식별용 앞 2개 항목만 보이고 나머지는 접는다.
    """
    note = (note or "").strip()
    if not note:
        return ""
    style_attr = f' style="{style}"' if style else ""
    if len(note) <= 60:
        return f'<div class="sub"{style_attr}>{esc(note)}</div>'
    segs = [s for s in note.split(" · ") if s.strip()]
    if len(segs) >= 2:
        summary = esc(" · ".join(segs[:2]))
        # 3개 이상 항목이면 나머지를 다중 줄로 렌더
        if len(segs) >= 3:
            rest_lines = "".join(f'<div>{esc(s)}</div>' for s in segs[2:])
            return fold(summary, rest_lines)
        # 2개 항목: 그대로 접기
        return fold(summary, esc(" · ".join(segs[1:])))
    # 구분자 없으면 첫 50자 + "…" 요약 후 다중 줄로 분해
    break_idx = note.find(" ", 0, 50)
    if break_idx > 0:
        first_phrase = note[:break_idx].strip() + "…"
    else:
        first_phrase = note[:50].strip() + "…"
    detail_lines = "".join(f'<div>{esc(line)}</div>' for line in [note])
    return fold(esc(first_phrase), detail_lines)


def pass_block(text: str) -> str:
    """일자별 교통패스 추천(🎫)을 '추천 요약 + 근거 접기'로 렌더.

    '{추천} — {근거}' 형식의 장문은 추천만 보이고 비용 계산·근거를 접는다.
    """
    text = (text or "").strip()
    if not text:
        return ""
    if len(text) <= 60 or " — " not in text:
        return f'<div class="sub" style="margin-top:0.25rem;">🎫 {esc(text)}</div>'
    head, _, rest = text.partition(" — ")
    # rest를 ` + ` 또는 ` · ` 기준으로 여러 줄로 분해
    import re
    lines = re.split(r'\s+\+\s+|\s·\s', rest)
    lines = [line.strip() for line in lines if line.strip()]
    if lines:
        detail_html = "".join(f'<div>{esc(line)}</div>' for line in lines)
    else:
        detail_html = esc(rest.strip())
    return f'<div style="margin-top:0.25rem;">{fold("🎫 " + esc(head.strip()), detail_html)}</div>'


def detail_row(label: str, value: str) -> str:
    """예약번호·권장처럼 길어지는 k/v 값을 짧으면 행, 길면 'label + 앞 토막 + 접기'로 렌더.

    16자리 예약번호·PIN·취소정책 등 장문 운영값이 우측 정렬 셀(.row .v)을 넘쳐
    모바일 레이아웃을 깨뜨리지 않도록, 식별용 앞 토막만 요약에 두고 나머지를 접는다.
    """
    value = (value or "").strip()
    if not value:
        return ""
    if len(value) <= 44:
        return f'<div class="row"><span class="k">{esc(label)}</span><span class="v">{esc(value)}</span></div>'
    segs = [s for s in value.split(" · ") if s.strip()]
    if len(segs) >= 2:
        summary = esc(f"{label} · {segs[0]}")
        detail = esc(" · ".join(segs[1:]))
    else:
        summary = esc(label)
        detail = esc(value)
    return "\n    " + fold(summary, detail)


def _lead_split(text: str):
    """첫 문장 또는 첫 토막을 요약 head로, 나머지를 detail로 분리.

    구분자 우선순위: 위치(earlier is better) + 타입(문장 > 항목).
    1. 60자 이내에서 가장 먼저 나타나는 구분자 찾기: ". " · "다. " · "요. " · "음. " · " — " · " · "
    2. 구분자 없으면 첫 어절 또는 60자 추출 + "…"

    의도: 항상 의미있는 요약을 생성.
    """
    separators = [". ", "다. ", "요. ", "음. ", " — ", " · "]
    # 60자 이내에서 가장 먼저 나타나는 구분자 찾기
    best_sep = None
    best_idx = float('inf')
    for sep in separators:
        idx = text.find(sep)
        if 0 < idx < 60 and idx < best_idx:
            best_idx = idx
            best_sep = sep

    if best_sep:
        return text[:best_idx].strip(), text[best_idx + len(best_sep):].strip()

    # 구분자 없으면 첫 어절 또는 60자까지 추출 + "…"
    if len(text) <= 60:
        return None, None
    # 첫 띄어쓰기 찾기 (최대 60자 내)
    break_idx = text.find(" ", 0, 60)
    if break_idx > 0:
        head = text[:break_idx].strip() + "…"
        return head, text[break_idx + 1:].strip()
    # 띄어쓰기 없으면 60자 한계
    return text[:60].strip() + "…", text[60:].strip()


def _detail_lines(text: str) -> str:
    """상세 텍스트를 여러 줄로 분해하여 HTML 렌더링.

    구분자(`. `·`다. `·`요. `·`음. `·` · `)로 항목화하고, 각 항목을 `<div>` 줄로 렌더.
    마크업([[]]) 변환도 함께.
    """
    import re
    # 구분자 패턴: ". " · "다. " · "요. " · "음. " · " · "
    sep_pattern = r'(?:\.(?:\s+|$)|다\.\s+|요\.\s+|음\.\s+|\s·\s)'
    lines = re.split(sep_pattern, text)
    # 빈 항목과 도미노 공백 제거
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        return ""
    return "".join(f'<div>{link_places(line)}</div>' for line in lines)


def memo_block(note: str, *, style: str = "", cls: str = "sub") -> str:
    """일정 메모·맛집 상세 노트를 짧으면 평문, 길면 '첫 문장 요약 + 접기'로 렌더.

    장소 팁·맛집 설명이 카드를 압도하지 않도록 첫 문장만 보이고 나머지를 접는다.
    예약·숙박 메모용 note_block(' · ' 2항목 요약)과 달리 문장 단위 요약이 자연스럽다.

    [[label|query]] 형식의 place markup을 Google Maps 링크로 변환.
    길이 판정은 strip_place_markup(note)의 display text로 수행.
    """
    note = (note or "").strip()
    if not note:
        return ""
    style_attr = f' style="{style}"' if style else ""
    display_text = strip_place_markup(note)
    if len(display_text) <= 50:
        return f'<div class="{cls}"{style_attr}>{link_places(note)}</div>'
    head, rest = _lead_split(note)
    if head and rest:
        detail_html = _detail_lines(rest)
        return fold(link_places(head), detail_html)
    # 구분자를 찾지 못하면 첫 어절 + "…" 추출 + 상세를 여러 줄로
    if len(display_text) > 60:
        # 50~60자: 구분자가 없으면 평문 그대로
        # 60자 초과: 첫 50자 추출 + "…"로 요약, 나머지 다중 줄
        import re
        break_idx = note.find(" ", 0, 50)
        if break_idx > 0:
            first_phrase = note[:break_idx].strip() + "…"
        else:
            first_phrase = note[:50].strip() + "…"
        detail_html = _detail_lines(note)
        return fold(link_places(first_phrase), detail_html)
    # 50~60자: 평문
    return f'<div class="{cls}"{style_attr}>{link_places(note)}</div>'


def source_url_of(text: str) -> str:
    """source 문자열의 첫 http(s) 토큰을 반환 (없으면 빈 문자열)."""
    for tok in (text or "").split():
        if tok.startswith(("http://", "https://")):
            return tok
    return ""


def source_chip(href: str, label: str, *, verified: bool = False) -> str:
    """모바일 터치 타깃 ≥44px 출처 칩. verified면 ✓ 표시."""
    tick = '<span class="source-tick" title="Playwright 검증">✓</span>' if verified else ""
    return (
        f'<a class="source-link" href="{esc(href)}" target="_blank" rel="noopener">'
        f'{tick}<span>{esc(label)} ↗</span></a>'
    )


def transit_line(af) -> str:
    """도착 경로를 '아이콘 + 평이 요약(소요시간)' summary와 장문 route 상세로 렌더.

    Supports both old schema (mode, route, ...) and new schema (steps array, ...).
    maps_url이 있으면 summary 줄에 '지도 ↗' 버튼 인라인 표시 — 탭하면 구글맵 앱 오픈.
    """
    if not af:
        return ""

    # New schema: has steps array
    if is_new_schema_arrive_from(af):
        return render_transit_line_steps(af.get("steps"), af)

    # Old schema: flat structure with mode, route, etc
    mode = af.get("mode")
    icon = MODE_ICONS.get(mode, "·")
    verb = MODE_VERBS.get(mode, "이동")
    dur = af.get("duration_min")
    tbd = af.get("data_quality") == "tbd_needs_browser_mcp"

    if dur:
        time_part = f"약 {dur}분 (현지 확인)" if tbd else f"{dur}분"
    else:
        time_part = "이동 (Maps 확인)" if tbd else "이동"
    summary = f"{icon} {verb} {time_part}"
    dist = af.get("distance_km")
    if mode == "walk" and isinstance(dist, (int, float)) and dist < 2:
        summary += f" ({dist}km)"

    # maps_url 우선, 없으면 source_url, 없으면 source 첫 토큰 URL fallback
    maps_url = (af.get("maps_url") or "").strip()
    src_url = (af.get("source_url") or "").strip()
    src = (af.get("source") or "").strip()
    first_token = src.split()[0] if src else ""
    src_href = first_token if first_token.startswith(("http://", "https://")) else ""
    href = maps_url or src_url or src_href

    # summary 줄에 지도 버튼 인라인 (항상 노출)
    if href:
        summary += f' <a href="{esc(href)}" target="_blank" rel="noopener" class="maps-btn">지도 ↗</a>'

    route = af.get("route") or ""
    detail = esc(route) if route else f"{esc(verb)} {esc(time_part)}"

    # 출처 칩 — source_url이 있고 maps_url이 없을 때만 (지도 버튼과 중복 방지)
    source_chip_html = ""
    if src_url and not maps_url:
        verified = bool(af.get("source_verified_at"))
        source_chip_html = f'<div class="source-row">{source_chip(src_url, "경로 출처", verified=verified)}</div>'

    return fold(summary, detail) + source_chip_html


def card_itinerary(d) -> str:
    itin = d["itinerary"]
    trip = itin.get("trip", {})
    day_cards = []
    for day in itin["days"]:
        item_rows = []
        for it in day["items"]:
            title_text = render_title_display(it["title"])
            link = maps_link(it["maps_query"], title_text) if it.get("maps_query") else esc(title_text)
            pronunciation_html = title_reading_html(it["title"])
            note_html = memo_block(it.get("note"))
            transit = transit_line(it.get("arrive_from"))
            if it.get("image_url"):
                img_html = (
                    f'<img src="{esc(it["image_url"])}" alt="{esc(title_text)}" '
                    f'class="place-img" loading="lazy">'
                    f'<div class="img-credit">{esc(it.get("image_credit",""))}</div>'
                )
            else:
                img_html = ""
            reviews_html = blog_reviews_html(it.get("blog_reviews", []))
            link_html = doc_link_html(it.get("link"))
            item_rows.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
      {pronunciation_html}
      {transit}
      {note_html}{link_html}{img_html}{reviews_html}
    </div>""")
        day_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['day_label'])}</div>
    {''.join(item_rows)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day['walking_km']}km · 숙박: {esc(day['lodging'])}</div>
    {pass_block(day.get("pass_recommendation"))}
  </div>""")

    pass_sources = trip.get("transit_pass_sources", [])
    pass_sources_html = ""
    if pass_sources:
        chips = "".join(
            source_chip(s["url"], s["label"], verified=bool(s.get("source_verified_at")))
            for s in pass_sources
        )
        pass_sources_html = (
            '<div class="sub" style="margin-top:0.6rem;">📚 교통 출처</div>'
            f'<div class="source-row">{chips}</div>'
        )

    playbook = trip.get("transit_pass_playbook", [])
    playbook_html = ""
    if playbook:
        rows = "".join(
            f'<li style="margin-bottom:0.35rem;"><b>{esc(s["when"])}</b> — {esc(s["action"])}</li>'
            for s in playbook
        )
        playbook_html = (
            f'<div class="subcard" style="margin-top:0.6rem;">'
            + fold(
                "🧭 ICOCA 실행 단계 (탭하면 펼침)",
                f'<ol style="margin:0.3rem 0 0 1.1rem;padding:0;">{rows}</ol>',
            )
            + "</div>"
        )

    return f"""
<!-- SYNC: data/itinerary.json · docs/kyoto-itinerary-may31-jun3-2026.md -->
<section id="itinerary" class="card">
  <h2>일자별 일정</h2>
  <div class="sub" style="margin-bottom:0.5rem;">장소 탭 → 구글맵 · 이동 경로 ▸ 탭하면 펼침</div>
  {''.join(day_cards)}
  {playbook_html}
  {pass_sources_html}
</section>
"""




_STATE_CLASS = {"확정": "done", "예약중": "progress", "미정": "pending"}


def checklist_card(it, in_viz: bool = False) -> str:
    """예약 항목 1개를 구조화 카드로 렌더.

    제목+상태 배지 / 금액·마감(D-day)·예약번호·권장 행 / 출처 링크 / 접히는 상세 노트.
    마감 D-day는 빌드 결정성을 위해 클라이언트 스크립트가 data-due에서 계산한다.
    in_viz=True: viz/checklist.html에서 렌더 (viz/ 접두어 불요).
    in_viz=False: index.html(루트)에서 렌더 (viz/ 접두어 필요).
    """
    st = it.get("status", "미정")
    state = _STATE_CLASS.get(st, "pending")
    rows = []
    if it.get("amount"):
        rows.append(f'<div class="row"><span class="k">금액</span><span class="v">{esc(it["amount"])}</span></div>')
    due = it.get("due_date", "")
    if state != "done" and due:
        rows.append(
            f'<div class="row"><span class="k">마감</span>'
            f'<span class="v">{esc(due)}<span class="dday" data-due="{esc(due)}"></span></span></div>'
        )
    if it.get("reference"):
        rows.append(detail_row("예약번호", it["reference"]))
    if it.get("action"):
        rows.append(detail_row("권장", it["action"]))
    link = it.get("link") or {}
    link_html = ""
    if link.get("url"):
        url = link["url"]
        # 레포 문서 경로는 사이트 내 렌더 페이지로 치환 (GitHub 링크 금지·검사 J).
        if url in DOC_SOURCE_TO_OUT:
            url = doc_href(DOC_SOURCE_TO_OUT[url], in_viz=in_viz)
        link_html = (
            f'\n    <a class="doc-link" href="{esc(url)}" target="_blank" '
            f'rel="noopener">{esc(link.get("label", "상세"))} ↗</a>'
        )
    note = it.get("note", "")
    note_html = ""
    if note:
        note_html = "\n    " + fold("자세히", linkify(note))
    return f"""
  <div class="subcard status-{state}">
    <div class="ck-head"><span class="subtitle">{esc(it['label'])}</span><span class="badge badge-{state}">{esc(st)}</span></div>
    {''.join(rows)}{link_html}{note_html}
  </div>"""


def checklist_sort_key(it):
    """처리 필요(미정·예약중)를 먼저, 그다음 마감일 이른 순."""
    done = 1 if it.get("status") == "확정" else 0
    return (done, it.get("due_date", "9999-99-99"))


CHECKLIST_DDAY_SCRIPT = """
<script>
(function () {
  var now = new Date(); now.setHours(0, 0, 0, 0);
  document.querySelectorAll('.dday[data-due]').forEach(function (el) {
    var due = new Date(el.getAttribute('data-due') + 'T00:00:00');
    if (isNaN(due.getTime())) return;
    var diff = Math.round((due - now) / 86400000);
    el.textContent = diff < 0 ? '지남' : diff === 0 ? 'D-day' : 'D-' + diff;
    if (diff < 0) el.classList.add('over');
    else if (diff <= 2) el.classList.add('urgent');
  });
})();
</script>"""


def card_checklist(d) -> str:
    items = sorted(d["checklist"]["items"], key=checklist_sort_key)
    cards = "".join(checklist_card(it) for it in items)
    return f"""
<!-- SYNC: data/booking-checklist.json -->
<section id="checklist" class="card">
  <h2>예약 체크리스트 ({len(items)}개)</h2>
  <div class="sub" style="margin-bottom:0.5rem;">상세: <a href="viz/checklist.html">전체 체크리스트 화면 ↗</a></div>
  {cards}
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
  <div class="sub" style="margin-bottom:0.5rem;">교토는 1위(오사카·고베 9.0) 후보가 아니지만 시부모 동반·비용·이동 부담을 종합한 별도 의사결정. 사유: <a href="decision-kyoto.html" style="color:inherit;text-decoration:underline;">2026-05-11 결정 일지</a>.</div>
  {''.join(rows)}
</section>
"""


INDEX_TITLE = "교토 5/31~6/3 · 4인 가족 여행"
INDEX_DESCRIPTION = "교토 5/31~6/3 · 4인 가족(부부+시부모) · 3박 4일 · 확정 일정·예약 현황"

INDEX_HEAD = f"""
<header class="lp-hero">
  <h1>{esc(INDEX_TITLE)}</h1>
  <p class="lp-tagline">시부모 동반 · 3박 4일 · 시오 마치야 2박 + 카덴쇼 료칸 1박</p>
  <nav class="lp-nav">
    <a href="#itinerary">일정</a>
    <a href="#airbnb">에어비앤비</a>
    <a href="#kadensho">카덴쇼</a>
    <a href="#flights">항공</a>
    <a href="#checklist">예약</a>
    <a href="#summary">요약</a>
  </nav>
</header>
"""

INDEX_FOOTER = """
<footer class="lp-footer">
  2026-05-12 의사결정 종료 ·
  <a href="viz/archive.html">아카이브</a> ·
  <a href="viz/report.html">최종 보고서</a>
</footer>
"""


LANDING_CSS = """
  /* ── Apple-style landing page ── */
  body { padding: 0; overflow-x: hidden; }

  .lp-hero {
    padding: 3.5rem 1.5rem 2.5rem;
    text-align: center;
    background: var(--subcard);
    border-bottom: 1px solid var(--border);
  }
  .lp-hero h1 {
    font-size: clamp(1.9rem, 7vw, 2.8rem);
    font-weight: 700; letter-spacing: -0.03em;
    line-height: 1.1; margin: 0 0 0.5rem;
  }
  .lp-tagline {
    color: var(--muted); font-size: 0.95rem;
    margin: 0 0 1.5rem; line-height: 1.5;
  }
  .lp-nav {
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 0.4rem; margin: 0; border: none; padding: 0;
  }
  .lp-nav a {
    padding: 0.4rem 0.9rem; border-radius: 999px;
    background: var(--card); color: var(--fg); text-decoration: none;
    font-size: 0.78rem; font-weight: 500; border: 1px solid var(--border);
  }
  .lp-nav a:active { background: var(--accent-soft); }

  main > section.card {
    border: none; border-radius: 0; box-shadow: none;
    padding: 1.75rem 1.5rem; margin: 0;
    border-bottom: 1px solid var(--border);
  }
  main > section.card:last-child { border-bottom: none; }
  main > section.card > h2 {
    font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em;
    color: var(--fg); margin: 0 0 1rem;
  }
  main > section.card .subcard {
    border-radius: 12px; border: none;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.05);
    padding: 0.9rem; margin: 0.5rem 0;
  }
  @media (prefers-color-scheme: dark) {
    main > section.card .subcard {
      box-shadow: 0 0 0 1px rgba(255,255,255,0.1);
    }
  }
  main > section.card .lodging-strip {
    margin: 0.75rem -1.5rem 0.6rem;
    padding: 0 1.5rem;
  }
  main > section.card .lodging-thumb {
    flex: 0 0 220px; height: 148px; border-radius: 10px;
  }
  footer.lp-footer {
    padding: 2rem 1.5rem; text-align: center;
    font-size: 0.8rem; margin: 0;
    border-top: 1px solid var(--border);
  }
  footer.lp-footer a { color: var(--muted); }
"""


def build_index(d) -> str:
    sections = [
        card_itinerary(d),
        card_airbnb(d),
        card_kadensho(d),
        card_flights(d),
        card_checklist(d),
        card_summary(d),
    ]
    body = INDEX_HEAD + "<main>\n" + "\n".join(sections) + "\n</main>" + INDEX_FOOTER
    return html_doc(
        INDEX_TITLE,
        body,
        tokens=d["tokens"],
        description=INDEX_DESCRIPTION,
        og_slug="home",
        page_path="",
        extra_css=LANDING_CSS,
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
    footer = """
<footer><a href="report.html" style="color:inherit;">최종 보고서</a> · <a href="decision-log.html" style="color:inherit;">결정 일지</a> · data/decision.json · data/cost-options.json · data/weather.json 단일 출처</footer>
"""
    body = head + "\n".join(sections) + footer + tab_bar("home", in_viz=True)
    return html_doc(
        ARCHIVE_TITLE,
        body,
        tokens=d["tokens"],
        description=ARCHIVE_DESCRIPTION,
        og_slug="archive",
        page_path="viz/archive.html",
    )


# ─── viz/lodging.html ──────────────────────────────────────────────────────

def build_lodging(d) -> str:
    body = f"""<h1>숙박 · 항공</h1>
<div class="status">에어비앤비 2박 + 카덴쇼 료칸 1박 · 에어서울 4인 발권 완료</div>
{card_airbnb(d, img_prefix="../")}
{card_kadensho(d, img_prefix="../")}
{card_flights(d)}
<footer>data/cost-options.json 단일 출처</footer>
{tab_bar("lodging", in_viz=True)}
"""
    return html_doc(
        "숙박·항공 · 교토 5/31~6/3",
        body,
        tokens=d["tokens"],
        description="시오 마치야 2박 + 카덴쇼 료칸 1박 · 에어서울 4인 발권",
        og_slug="lodging",
        page_path="viz/lodging.html",
    )


# ─── viz/breakfast.html ────────────────────────────────────────────────────

BREAKFAST_TITLE = "숙소 인근 조식 옵션 · 교토 5/31~6/3"


def maps_search_url(query: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + quote(query)


def _breakfast_store(store, map_area: str) -> str:
    rows = "".join(
        f'<div class="row"><span class="k">{esc(k)}</span><span class="v">{esc(v)}</span></div>'
        for k, v in store.get("rows", [])
    )
    menu = store.get("menu", "")
    menu_html = f'<div class="bf-menu">🍽 {esc(menu)}</div>' if menu else ""
    note = store.get("note", "")
    note_html = f'<div class="sub">{esc(note)}</div>' if note else ""
    query = store.get("map_query") or " ".join(p for p in (store["name"], map_area) if p)
    name_link = (
        f'<a class="map-link" href="{esc(maps_search_url(query))}" target="_blank" '
        f'rel="noopener">{esc(store["name"])} 🗺</a>'
    )
    return (
        f'<div class="bf-store">'
        f'<div class="subtitle">{name_link}</div>{rows}{menu_html}{note_html}</div>'
    )


def _breakfast_group(g, map_area: str, *, open: bool = False) -> str:
    """가게 그룹을 '라벨 + 개수' 요약 + 접힌 상세로 렌더 (모바일 가독성)."""
    label = esc(g["label"])
    if g.get("stores"):
        inner = "".join(_breakfast_store(s, map_area) for s in g["stores"])
        summary = f'{label} · {len(g["stores"])}곳'
    else:
        items = g.get("items", [])
        lis = "".join(f"<li>{esc(x)}</li>" for x in items)
        inner = f'<ul style="margin:0.3rem 0 0 1.1rem;padding:0;">{lis}</ul>'
        summary = f'{label} · {len(items)}항목'
    return fold(summary, inner, open=open)


def build_breakfast(d) -> str:
    bf = d["breakfast"]

    morning_items = "".join(
        f'<div class="bf-item"><div class="bf-label">{esc(m["morning"])} · {esc(m["lodging"])}</div>'
        f'<div class="bf-body">{esc(m["first_plan"])}</div>'
        f'<div class="sub">여유: {esc(m["leeway"])}</div></div>'
        for m in bf.get("mornings", [])
    )
    mornings_card = (
        f'<div class="subcard"><div class="subtitle">조식이 필요한 아침 3회</div>{morning_items}'
        f'<div class="sub" style="margin-top:0.4rem;">출발 시각이 옵션을 결정 — 카덴쇼는 조식 미포함(6/3 새벽 출국).</div></div>'
    )

    lodging_cards = []
    for lg in bf.get("lodgings", []):
        map_area = lg.get("map_area", "")
        groups_html = "".join(
            _breakfast_group(g, map_area, open=(i == 0))
            for i, g in enumerate(lg.get("groups", []))
        )
        lodging_cards.append(
            f'<div class="subcard"><div class="subtitle">{esc(lg["name"])}</div>'
            f'<div class="sub">{esc(lg["access"])}</div>'
            f'<div class="sub">{esc(lg.get("note",""))}</div>'
            f'{groups_html}</div>'
        )

    reco_items = "".join(
        f'<div class="bf-item"><div class="bf-label">{esc(r["morning"])}</div>'
        f'<div class="bf-body">{esc(r["text"])}</div></div>'
        for r in bf.get("recommendations", [])
    )
    reco_card = f'<div class="subcard"><div class="subtitle">아침별 권장</div>{reco_items}</div>'

    caution = bf.get("caution", [])
    caution_card = ""
    if caution:
        caution_items = "".join(f"<li>{esc(c)}</li>" for c in caution)
        caution_detail = f'<ul style="margin:0.3rem 0 0 1.1rem;padding:0;">{caution_items}</ul>'
        caution_card = (
            f'<div class="subcard">'
            f'{fold("⚠ 영업시간은 변동 — 출발 전 Google Maps 재확인", caution_detail)}</div>'
        )

    sources = bf.get("sources", [])
    sources_card = ""
    if sources:
        source_links = " · ".join(
            f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a>'
            for s in sources
        )
        researched = esc(bf.get("researched_at", ""))
        summary = f"📚 출처 {len(sources)}건 (리서치 {researched})"
        sources_card = f'<div class="subcard">{fold(summary, source_links)}</div>'

    head = f"""<h1>{esc(bf["title"])}</h1>
<div class="status">{esc(bf.get("intro",""))}</div>

<nav>
  <a href="itinerary.html">← 일정으로</a>
</nav>
"""
    body = (
        head
        + mornings_card
        + "\n".join(lodging_cards)
        + reco_card
        + caution_card
        + sources_card
        + f'\n<footer>data/breakfast.json 단일 출처 · 사람용 사본 docs/breakfast-near-lodging.md</footer>\n'
        + tab_bar("itinerary", in_viz=True)
    )
    return html_doc(
        BREAKFAST_TITLE,
        body,
        tokens=d["tokens"],
        description="시오·카덴쇼 인근 조식 — 거리·영업시간·아침별 권장 (4인 가족)",
        og_slug="itinerary",
        page_path="viz/breakfast.html",
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
            title_text = render_title_display(it["title"])
            link = maps_link(it["maps_query"], title_text) if it.get("maps_query") else esc(title_text)
            pronunciation_html = title_reading_html(it["title"])
            note_html = memo_block(it.get("note"))
            transit = transit_line(it.get("arrive_from"))
            if it.get("image_url"):
                img_html = (
                    f'<img src="{esc(it["image_url"])}" alt="{esc(title_text)}" '
                    f'class="place-img" loading="lazy">'
                    f'<div class="img-credit">{esc(it.get("image_credit",""))}</div>'
                )
            else:
                img_html = ""
            reviews_html = blog_reviews_html(it.get("blog_reviews", []))
            food_html = food_quality_html(it.get("food_quality"))
            link_html = doc_link_html(it.get("link"), in_viz=True)
            item_rows.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
      {pronunciation_html}
      {transit}
      {note_html}{food_html}{link_html}{img_html}{reviews_html}
    </div>""")
        day_cards.append(f"""
  <div class="subcard">
    <div class="subtitle">{esc(day['day_label'])}</div>
    {''.join(item_rows)}
    <div class="sub" style="margin-top:0.4rem;">도보 약 {day['walking_km']}km · 숙박: {esc(day['lodging'])}</div>
    {pass_block(day.get("pass_recommendation"))}
  </div>""")

    pending_items = "".join(f"<li>{esc(p)}</li>" for p in itin.get("pending", []))

    pass_sources = trip.get("transit_pass_sources", [])
    pass_sources_html = ""
    if pass_sources:
        chips = "".join(
            source_chip(s["url"], s["label"], verified=bool(s.get("source_verified_at")))
            for s in pass_sources
        )
        pass_sources_html = (
            '<div class="sub" style="margin-top:0.6rem;">📚 교통 출처</div>'
            f'<div class="source-row">{chips}</div>'
        )

    playbook = trip.get("transit_pass_playbook", [])
    playbook_html = ""
    if playbook:
        rows = "".join(
            f'<li style="margin-bottom:0.35rem;"><b>{esc(s["when"])}</b> — {esc(s["action"])}</li>'
            for s in playbook
        )
        playbook_html = (
            f'<div class="subcard" style="margin-top:0.6rem;">'
            + fold(
                "🧭 ICOCA 실행 단계 (탭하면 펼침)",
                f'<ol style="margin:0.3rem 0 0 1.1rem;padding:0;">{rows}</ol>',
            )
            + "</div>"
        )

    candidate_cards = []
    for cand in itin.get("route_candidates", []):
        cand_day_cards = []
        for day in cand["days"]:
            item_rows = []
            for it in day["items"]:
                title_text = render_title_display(it["title"])
                link = maps_link(it["maps_query"], title_text) if it.get("maps_query") else esc(title_text)
                pronunciation_html = title_reading_html(it["title"])
                note_html = memo_block(it.get("note"))
                food_html = food_quality_html(it.get("food_quality"))
                link_html = doc_link_html(it.get("link"), in_viz=True)
                item_rows.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(it['time'])}</span> {link}</div>
      {pronunciation_html}
      {note_html}{food_html}{link_html}
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

    candidates_section = ""  # 의사결정 완료 — 후보 코스 웹 노출 안 함

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
  <a href="itinerary-doc.html">문서 보기</a>
</div>

<footer>data/itinerary.json 단일 출처</footer>
{tab_bar("itinerary", in_viz=True)}
"""
    return html_doc(
        "교토 3박4일 일정 · 5/31~6/3 · 4인 가족",
        body,
        tokens=d["tokens"],
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

    badge_map = {"확정": "done", "예약중": "progress", "미정": "pending"}
    summary_rows = "".join(
        f'<div class="row"><span class="k">'
        f'<span class="badge badge-{badge_map[k]}">{k}</span></span>'
        f'<span class="v">{counts[k]}개</span></div>'
        for k in ("확정", "예약중", "미정")
    )

    sorted_items = sorted(items, key=checklist_sort_key)
    item_cards = [checklist_card(it, in_viz=True) for it in sorted_items]


    body = f"""<h1>예약 체크리스트</h1>
<div class="status">{counts.get('확정', 0)}개 확정 · {counts.get('미정', 0)}개 미정 · 총 {len(items)}개 항목</div>

<!-- SYNC: data/booking-checklist.json -->
<section class="card">
  <h2>상태 요약</h2>
  {summary_rows}
</section>

<section class="card">
  <h2>항목 (처리 필요 먼저 · 마감 이른 순)</h2>
  {''.join(item_cards)}
</section>

<footer>data/booking-checklist.json 단일 출처</footer>
{tab_bar("checklist", in_viz=True)}
{CHECKLIST_DDAY_SCRIPT}
"""
    return html_doc(
        "예약 체크리스트 · 교토 5/31~6/3",
        body,
        tokens=d["tokens"],
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
                title_text = render_title_display(it["title"])
                link = maps_link(it["maps_query"], title_text) if it.get("maps_query") else esc(title_text)
                pronunciation_html = title_reading_html(it["title"])
                note_html = memo_block(it.get("note"), cls="t-note")
                transit = transit_line(it.get("arrive_from"))
                if it.get("image_url"):
                    img_html = (
                        f'<img src="{esc(it["image_url"])}" alt="{esc(title_text)}" '
                        f'class="place-img" loading="lazy">'
                        f'<span class="img-credit">{esc(it.get("image_credit",""))}</span>'
                    )
                else:
                    img_html = ""
                food_html = food_quality_html(it.get("food_quality"))
                link_html = doc_link_html(it.get("link"), in_viz=True)
                cells.append(
                    f'<td><span class="t-time">{esc(it["time"])}</span>'
                    f'<span class="t-title">{link}</span>{pronunciation_html}{transit}{note_html}{food_html}{link_html}{img_html}</td>'
                )
            else:
                cells.append("<td></td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    # 모바일용 카드 뷰 (600px 미만)
    mobile_cards = []
    for day in days:
        item_rows = []
        for it in day["items"]:
            title_text = render_title_display(it["title"])
            link = maps_link(it["maps_query"], title_text) if it.get("maps_query") else esc(title_text)
            pronunciation_html = title_reading_html(it["title"])
            note_html = memo_block(it.get("note"))
            transit = transit_line(it.get("arrive_from"))
            if it.get("image_url"):
                img_html = (
                    f'<img src="{esc(it["image_url"])}" alt="{esc(title_text)}" '
                    f'class="place-img" loading="lazy">'
                    f'<div class="img-credit">{esc(it.get("image_credit",""))}</div>'
                )
            else:
                img_html = ""
            reviews_html = blog_reviews_html(it.get("blog_reviews", []))
            food_html = food_quality_html(it.get("food_quality"))
            link_html = doc_link_html(it.get("link"), in_viz=True)
            item_rows.append(f"""
    <div class="day">
      <div class="date"><span class="k">{esc(it["time"])}</span> {link}</div>
      {pronunciation_html}
      {transit}
      {note_html}{food_html}{link_html}{img_html}{reviews_html}
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
        tokens=d["tokens"],
        description="교토 3박 4일 시간표 · 4일 한눈에",
        og_slug="itinerary-table",
        page_path="viz/itinerary-table.html",
        extra_css=TABLE_CSS,
    )


# ─── 문서 페이지 렌더 (마크다운 → HTML) ─────────────────────────────────────

DOC_CSS = """
  .doc { line-height: 1.6; word-break: keep-all; }
  .doc h1 { font-size: 1.4rem; margin: 1rem 0 0.5rem; color: var(--fg); font-weight: 600; }
  .doc h2 { font-size: 1.1rem; margin: 1.3rem 0 0.4rem; color: var(--fg); font-weight: 600;
            border-bottom: 1px solid var(--border); padding-bottom: 0.2rem; }
  .doc h3 { font-size: 1rem; margin: 1rem 0 0.3rem; color: var(--fg); font-weight: 600; }
  .doc p { margin: 0.5rem 0; }
  .doc ul, .doc ol { padding-left: 1.3rem; margin: 0.5rem 0; }
  .doc li { margin: 0.25rem 0; }
  .doc a { color: var(--accent); }
  .doc strong { font-weight: 600; }
  .doc code {
    background: var(--subcard); border: 1px solid var(--border); border-radius: 4px;
    padding: 0.05rem 0.3rem; font-size: 0.85em; word-break: break-all;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }
  .doc blockquote {
    margin: 0.6rem 0; padding: 0.4rem 0.8rem; border-left: 3px solid var(--accent);
    background: var(--subcard); color: var(--muted); border-radius: 0 4px 4px 0;
  }
  .doc blockquote p { margin: 0.3rem 0; }
  .doc table {
    border-collapse: collapse; width: 100%; margin: 0.6rem 0; font-size: 0.85rem;
    display: block; overflow-x: auto; -webkit-overflow-scrolling: touch;
  }
  .doc th, .doc td { border: 1px solid var(--border); padding: 0.4rem 0.55rem; text-align: left; vertical-align: top; }
  .doc th { background: var(--subcard); font-weight: 600; white-space: nowrap; }
  .doc hr { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }
"""

_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    """선두 YAML frontmatter(---...---) 블록 제거. 없으면 원문 그대로."""
    return _FRONTMATTER_RE.sub("", text, count=1)


def render_markdown_body(md_text: str) -> str:
    html_body = markdown.markdown(
        strip_frontmatter(md_text),
        extensions=["tables", "sane_lists"],
        output_format="html",
    )
    return f'<div class="doc">\n{html_body}\n</div>'


def build_doc_page(d, page: DocPage) -> str:
    md_text = (BASE / page.source).read_text(encoding="utf-8")
    nav = (
        f'<nav><a href="{esc(page.back_href)}">{esc(page.back_label)}</a>'
        f'<a href="../index.html">🏠 홈</a></nav>'
    )
    body = (
        nav
        + render_markdown_body(md_text)
        + f"\n<footer>레포 {esc(page.source)} 의 사이트 내 사본 · 원본이 정본</footer>\n"
        + tab_bar(page.tab, in_viz=True)
    )
    return html_doc(
        page.title,
        body,
        tokens=d["tokens"],
        description=page.description,
        og_slug=page.og_slug,
        page_path=page.out,
        extra_css=DOC_CSS,
    )


def _first_heading(md_text: str) -> str:
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return ""


def build_decision_log_index(d) -> str:
    entries = sorted(
        (p for p in (DOCS / "decision-log").glob("*.md") if p.name != "README.md"),
        key=lambda p: p.name,
        reverse=True,
    )
    linked = {
        p.source.rsplit("/", 1)[-1]: p.out
        for p in DOC_PAGES
        if p.source.startswith("docs/decision-log/")
    }
    rows = []
    for p in entries:
        title = _first_heading(p.read_text(encoding="utf-8")) or p.stem
        if p.name in linked:
            href = doc_href(linked[p.name], in_viz=True)
            label = f'<a href="{esc(href)}">{esc(title)}</a>'
        else:
            label = esc(title)
        rows.append(
            f'<li><b style="font-variant-numeric:tabular-nums;">{esc(p.name[:10])}</b> — {label}</li>'
        )
    body = f"""<h1>의사결정 일지</h1>
<div class="status">{len(entries)}개 항목 · 최신순 · 본문은 레포 docs/decision-log/ 에 보관</div>

<nav>
  <a href="archive.html">← 아카이브</a>
  <a href="../index.html">🏠 홈</a>
</nav>

<section class="card">
  <h2>전체 일지 ({len(entries)}개)</h2>
  <div class="sub" style="margin-bottom:0.5rem;">교토 변경 결정만 사이트 내 문서로 연결 · 나머지는 제목만 표기 (원본은 레포 docs/decision-log/).</div>
  <div class="doc"><ul>{''.join(rows)}</ul></div>
</section>

<footer>docs/decision-log/ 단일 출처 · ADR(Nygard) 형식</footer>
{tab_bar("home", in_viz=True)}
"""
    return html_doc(
        "의사결정 일지 · 교토 가족여행 2026",
        body,
        tokens=d["tokens"],
        description="의사결정 일지 전체 목록 (최신순)",
        og_slug="archive",
        page_path=DECISION_LOG_OUT,
        extra_css=DOC_CSS,
    )


# ─── OG SVG 자산 (1200×630) ────────────────────────────────────────────────

OG_FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif"


def build_og_svg(*, tokens: dict, eyebrow: str, title: str, subtitle: str) -> str:
    """1200×630 SVG OG 카드. 좌측 액센트 바 + 큰 한글 제목 + 부제 + 도메인.
    배경은 dark surface, 텍스트는 dark ink, 액센트는 dark accent — 카톡·Slack 다크 미리보기 친화."""
    cd = tokens["color"]["dark"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="{cd['surface']}"/>
  <rect x="0" y="0" width="12" height="630" fill="{cd['accent']}"/>
  <g font-family="{OG_FONT_STACK}" fill="{cd['ink']}">
    <text x="80" y="170" font-size="34" font-weight="500" fill="{cd['ink_muted']}">{esc(eyebrow)}</text>
    <text x="80" y="290" font-size="84" font-weight="700">{esc(title)}</text>
    <text x="80" y="380" font-size="40" font-weight="400" fill="{cd['ink_muted']}">{esc(subtitle)}</text>
    <text x="80" y="560" font-size="26" font-weight="500" fill="{cd['ink_muted']}">nihon-trip.vercel.app</text>
    <text x="1120" y="560" font-size="26" font-weight="500" fill="{cd['ink_muted']}" text-anchor="end">교토 가족여행 2026</text>
  </g>
</svg>
"""


OG_CARDS = (
    ("home",              "교토 가족여행 · 2026",     "교토 5/31~6/3 · 4인 가족",     "부부 + 시부모 · 3박 4일 · 확정"),
    ("itinerary",         "일자별 코스",              "교토 3박 4일 일정",            "5/31~6/3 · 청수사·아라시야마·후시미"),
    ("itinerary-table",   "4일 시간표",               "교토 3박4일 시간표",           "5/31~6/3 · 4열 타임테이블"),
    ("lodging",           "숙박 · 항공",              "시오 2박 + 카덴쇼 1박",        "에어서울 인천↔간사이 4인 발권"),
    ("checklist",         "예약 체크리스트",          "예약 진행 상태",               "확정 3 · 미정 4 항목"),
    ("archive",           "의사결정 아카이브",        "장마·예산·후보지 점수",        "2026-05-12 결정 종료 · 회귀 가드"),
)


# ─── 메인 ──────────────────────────────────────────────────────────────────

OUTPUTS = (
    ("index.html",                    lambda p: p / "index.html",                        build_index),
    ("viz/itinerary.html",            lambda p: p / "viz" / "itinerary.html",            build_itinerary),
    ("viz/itinerary-table.html",      lambda p: p / "viz" / "itinerary-table.html",      build_itinerary_table),
    ("viz/checklist.html",            lambda p: p / "viz" / "checklist.html",            build_checklist),
    ("viz/lodging.html",              lambda p: p / "viz" / "lodging.html",              build_lodging),
    ("viz/archive.html",              lambda p: p / "viz" / "archive.html",              build_archive),
    ("viz/breakfast.html",            lambda p: p / "viz" / "breakfast.html",            build_breakfast),
) + tuple(
    (
        page.out,
        lambda p, rel=page.out: p / rel,
        lambda d, pg=page: build_doc_page(d, pg),
    )
    for page in DOC_PAGES
) + (
    (DECISION_LOG_OUT, lambda p: p / "viz" / "decision-log.html", build_decision_log_index),
) + tuple(
    (
        f"assets/og-{slug}.svg",
        lambda p, s=slug: p / "assets" / f"og-{s}.svg",
        lambda d, e=eyebrow, t=title, s=subtitle: build_og_svg(tokens=d["tokens"], eyebrow=e, title=t, subtitle=s),
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
