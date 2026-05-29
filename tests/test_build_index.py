"""build_index.py: 결정론(idempotent)·--check 동작·핵심 섹션 회귀 테스트."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
INDEX = BASE / "index.html"
ITINERARY = BASE / "viz" / "itinerary.html"
CHECKLIST = BASE / "viz" / "checklist.html"
TABLE = BASE / "viz" / "itinerary-table.html"
LODGING = BASE / "viz" / "lodging.html"
ARCHIVE = BASE / "viz" / "archive.html"
BREAKFAST = BASE / "viz" / "breakfast.html"
ALL_HTML_OUTPUTS = (INDEX, ITINERARY, CHECKLIST, TABLE, LODGING, ARCHIVE, BREAKFAST)
OG_SLUGS = ("home", "itinerary", "itinerary-table", "lodging", "checklist", "archive")
ALL_OG_SVGS = tuple(BASE / "assets" / f"og-{s}.svg" for s in OG_SLUGS)
ALL_OUTPUTS = ALL_HTML_OUTPUTS + ALL_OG_SVGS
SCRIPT = BASE / "scripts" / "build_index.py"

sys.path.insert(0, str(BASE / "scripts"))
import build_index  # noqa: E402


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=BASE)


class BuildIndexTests(unittest.TestCase):
    def test_build_then_check_passes(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stderr)
        r2 = run("--check")
        self.assertEqual(r2.returncode, 0, r2.stderr)

    def test_build_is_idempotent(self):
        run()
        first = [p.read_text(encoding="utf-8") for p in ALL_OUTPUTS]
        run()
        second = [p.read_text(encoding="utf-8") for p in ALL_OUTPUTS]
        self.assertEqual(first, second, "build_index.py is not idempotent")

    def test_og_assets_generated(self):
        """OG SVG 자산 6장이 모두 생성되어야 한다."""
        run()
        for path in ALL_OG_SVGS:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"{path.relative_to(BASE)} not generated")
                content = path.read_text(encoding="utf-8")
                self.assertIn("<svg", content)
                self.assertIn('width="1200"', content)
                self.assertIn('height="630"', content)

    def test_check_detects_drift_in_each_output(self):
        run()
        for path in ALL_HTML_OUTPUTS:
            with self.subTest(path=path.name):
                original = path.read_text(encoding="utf-8")
                try:
                    path.write_text(original + "<!-- drift -->", encoding="utf-8")
                    r = run("--check")
                    self.assertEqual(r.returncode, 1, f"expected --check to fail on drift in {path.name}")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_check_detects_drift_in_og_svg(self):
        run()
        for path in ALL_OG_SVGS:
            with self.subTest(path=path.name):
                original = path.read_text(encoding="utf-8")
                try:
                    path.write_text(original + "<!-- drift -->", encoding="utf-8")
                    r = run("--check")
                    self.assertEqual(r.returncode, 1, f"expected --check to fail on drift in {path.name}")
                finally:
                    path.write_text(original, encoding="utf-8")

    def test_all_sections_rendered(self):
        run()
        # 홈 탭: 운영 모드 — 요약·일정만 (장마·예산·점수는 archive로 분리)
        html = INDEX.read_text(encoding="utf-8")
        for section_id in ("summary", "itinerary"):
            self.assertIn(f'id="{section_id}"', html, f"index.html section #{section_id} missing")
        for section_id in ("tsuyu", "budget", "score"):
            self.assertNotIn(
                f'id="{section_id}"', html,
                f"index.html should not contain archive section #{section_id} (moved to viz/archive.html)",
            )
        # 아카이브 탭: 장마·예산(9 시나리오)·점수(7 후보지)
        archive = ARCHIVE.read_text(encoding="utf-8")
        for section_id in ("tsuyu", "budget", "score"):
            self.assertIn(f'id="{section_id}"', archive, f"archive.html section #{section_id} missing")
        # 숙박·항공 탭: lodging.html에 분리
        lodging = LODGING.read_text(encoding="utf-8")
        for section_id in ("airbnb", "kadensho", "flights"):
            self.assertIn(f'id="{section_id}"', lodging, f"lodging.html section #{section_id} missing")

    def test_index_title_is_operational(self):
        """리뷰 §8-1: 메인 <title>·H1은 '최종 결정'이 아니라 운영 모드 문구."""
        run()
        html = INDEX.read_text(encoding="utf-8")
        self.assertNotIn("일본 여행 최종 결정", html, "index.html still uses decision-mode title")
        self.assertIn("교토 5/31~6/3", html, "index.html title should include operational date range")
        self.assertIn("4인 가족", html, "index.html title should include 4인 가족")

    def test_index_summary_has_no_score_line(self):
        """리뷰 §8-4: 메인 요약에서 종합 점수 줄 제거 (교토 7.60/10이 의심 신호)."""
        run()
        html = INDEX.read_text(encoding="utf-8")
        self.assertNotIn("종합 점수", html, "index.html summary should not show 종합 점수 line")

    def test_sync_comments_present(self):
        run()
        total = sum(p.read_text(encoding="utf-8").count("<!-- SYNC:") for p in ALL_HTML_OUTPUTS)
        self.assertGreaterEqual(total, 9, "expected at least 9 SYNC comments across all HTML outputs (one per section)")

    def test_og_meta_present_on_all_pages(self):
        """리뷰 §1·§8-2: 모든 페이지에 og:/twitter: 메타가 있어야 한다."""
        run()
        required = (
            'property="og:title"',
            'property="og:description"',
            'property="og:image"',
            'property="og:url"',
            'property="og:type"',
            'name="twitter:card"',
            'name="twitter:title"',
            'name="twitter:image"',
            'name="description"',
        )
        for path in ALL_HTML_OUTPUTS:
            html = path.read_text(encoding="utf-8")
            for needle in required:
                with self.subTest(path=path.name, needle=needle):
                    self.assertIn(needle, html, f"{path.name} missing {needle}")

    def test_og_titles_are_unique_per_page(self):
        """각 페이지의 og:title은 페이지 정체성을 반영해 서로 달라야 한다."""
        import re
        run()
        og_title_re = re.compile(r'<meta\s+property="og:title"\s+content="([^"]+)"')
        titles = {}
        for path in ALL_HTML_OUTPUTS:
            html = path.read_text(encoding="utf-8")
            m = og_title_re.search(html)
            self.assertIsNotNone(m, f"{path.name} has no og:title")
            titles[path.name] = m.group(1)
        self.assertEqual(
            len(set(titles.values())),
            len(titles),
            f"og:title should be unique per page, got: {titles}",
        )

    def test_og_image_points_to_assets_svg(self):
        """og:image는 assets/og-*.svg를 참조해야 한다."""
        import re
        run()
        og_image_re = re.compile(r'<meta\s+property="og:image"\s+content="([^"]+)"')
        for path in ALL_HTML_OUTPUTS:
            html = path.read_text(encoding="utf-8")
            m = og_image_re.search(html)
            with self.subTest(path=path.name):
                self.assertIsNotNone(m, f"{path.name} has no og:image")
                self.assertIn("/assets/og-", m.group(1))
                self.assertTrue(m.group(1).endswith(".svg"), f"{path.name} og:image not SVG")

    def test_viz_outputs_have_no_external_fetch(self):
        run()
        for path in (ITINERARY, CHECKLIST):
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("fetch(", content, f"{path.name} must be standalone (no fetch)")
                self.assertNotIn("XMLHttpRequest", content, f"{path.name} must be standalone (no XHR)")

    def test_viz_outputs_reference_their_data_source(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertIn("data/itinerary.json", itin)
        cl = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("data/booking-checklist.json", cl)

    def test_all_html_outputs_use_token_palette(self):
        """HTML 6종: light(#F7F6F2/#3E5C76) + dark 토큰 모두 인라인 CSS에 등장."""
        run()
        for path in ALL_HTML_OUTPUTS:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("#F7F6F2", content, f"{path.name}: light bg token not injected")
                self.assertIn("#3E5C76", content, f"{path.name}: slate-indigo accent not injected")
                for legacy in ("#d33", "#fafafa", "#ff6464", "#c33", "#c80", "#2a7"):
                    self.assertNotIn(
                        legacy, content,
                        f"{path.name}: legacy color {legacy} still present",
                    )

    def test_og_svgs_use_dark_token_palette(self):
        """OG SVG 6장: dark surface(#1F222C) + dark accent(#8AA8C7) 토큰 인젝션. 다크 미리보기 친화."""
        run()
        for path in ALL_OG_SVGS:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("#1F222C", content, f"{path.name}: dark surface token not injected")
                self.assertIn("#8AA8C7", content, f"{path.name}: dark accent token not injected")
                for legacy in ("#0a0a0a", "#ededed", "#cfcfcf"):
                    self.assertNotIn(
                        legacy, content,
                        f"{path.name}: legacy SVG color {legacy} still present",
                    )

    def test_arrive_from_route_is_clickable_link_when_source_is_url(self):
        """모든 mode(bus·subway·jr·taxi·walk·airport_express)의 arrive_from에서
        maps_url(우선) 또는 source가 http URL이면 해당 URL이 HTML에 링크로 렌더돼야 한다.
        maps_url이 있으면 maps-btn 버튼으로, 없으면 source URL로 확인.
        """
        run()
        import json as _json
        data = _json.loads((BASE / "data" / "itinerary.json").read_text(encoding="utf-8"))
        url_legs = []
        for day in data["days"]:
            for it in day["items"]:
                af = it.get("arrive_from")
                if not af:
                    continue
                # maps_url 우선, 없으면 source 첫 토큰
                maps_url = (af.get("maps_url") or "").strip()
                src = af.get("source", "")
                first_src = src.split()[0] if src else ""
                url = maps_url or (first_src if first_src.startswith("http") else "")
                if url:
                    url_legs.append((af["mode"], url))
        self.assertGreater(len(url_legs), 0, "fixture must have at least one URL-sourced leg")
        import html as _html
        for path in (INDEX, ITINERARY):
            with self.subTest(path=path.name):
                page = path.read_text(encoding="utf-8")
                for mode, url in url_legs[:5]:
                    # HTML href 속성에서 & → &amp; 이스케이프 — 양쪽 형태 중 하나가 있으면 통과
                    escaped = _html.escape(url, quote=True)
                    found = url in page or escaped in page
                    self.assertTrue(found, f"{mode} leg URL {url!r} not linked in {path.name}")

    def test_transit_pass_playbook_rendered_as_steps(self):
        """data/itinerary.json trip.transit_pass_playbook(when·action 배열)이
        index.html·viz/itinerary.html 양쪽 카드에 번호 매김된 실행 단계로
        렌더돼야 한다. 모바일 현지 운영용 회귀 가드.
        """
        run()
        import json as _json
        data = _json.loads((BASE / "data" / "itinerary.json").read_text(encoding="utf-8"))
        steps = data.get("trip", {}).get("transit_pass_playbook") or []
        self.assertGreaterEqual(len(steps), 5, "playbook must have at least 5 steps")
        for s in steps:
            self.assertIn("when", s)
            self.assertIn("action", s)
        for path in (INDEX, ITINERARY):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn("실행 단계", html, f"playbook header missing in {path.name}")
                for s in steps:
                    self.assertIn(s["when"], html, f"step.when {s['when']!r} not in {path.name}")
                    self.assertIn(s["action"][:20], html, f"step.action prefix not in {path.name}")

    def test_transit_pass_sources_rendered_as_links(self):
        """data/itinerary.json trip.transit_pass_sources(label·url 배열)가
        index.html·viz/itinerary.html 양쪽 카드에 클릭 가능한 <a href> 링크로
        렌더돼야 한다. 모바일 운영용 출처 노출 회귀 가드.
        """
        run()
        import json as _json
        data = _json.loads((BASE / "data" / "itinerary.json").read_text(encoding="utf-8"))
        sources = data.get("trip", {}).get("transit_pass_sources") or []
        self.assertGreater(len(sources), 0, "trip.transit_pass_sources must be populated")
        for src in sources:
            self.assertIn("label", src)
            self.assertIn("url", src)
            self.assertTrue(src["url"].startswith("http"), f"non-http source url: {src['url']}")
        for path in (INDEX, ITINERARY):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                for src in sources:
                    self.assertIn(src["url"], html, f"source url {src['url']!r} not in {path.name}")
                    self.assertIn(src["label"], html, f"source label {src['label']!r} not in {path.name}")

    def test_route_candidates_rendered_in_itinerary(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertIn("후보 코스", itin, "route candidates section missing in itinerary.html")
        for candidate_name in ("여유형", "서북 사찰 집중형", "미식+문화 체험형"):
            self.assertIn(candidate_name, itin, f"candidate '{candidate_name}' missing in itinerary.html")

    def test_checklist_note_urls_rendered_as_links(self):
        """note에 포함된 http URL은 linkify가 클릭 가능한 <a href> 링크로 렌더해야 한다.
        모바일 예약 탭에서 외부 출처로 바로 이동하기 위한 회귀 가드. (GitHub 링크는
        검사 J가 별도 차단하므로 production note에는 URL이 없을 수 있어, linkify
        동작은 격리 입력으로 직접 검증하고 production note URL은 조건부로 확인한다.)
        """
        sys.path.insert(0, str(BASE / "scripts"))
        import build_index
        rendered = build_index.linkify("출처 https://example.com/doc 참고")
        self.assertIn('<a href="https://example.com/doc"', rendered)

        run()
        import json as _json
        import re as _re
        data = _json.loads((BASE / "data" / "booking-checklist.json").read_text(encoding="utf-8"))
        url_re = _re.compile(r"https?://[^\s]+")
        html = CHECKLIST.read_text(encoding="utf-8")
        for it in data["items"]:
            for url in url_re.findall(it.get("note", "")):
                with self.subTest(url=url):
                    self.assertIn(f'href="{url}"', html,
                                  f"note URL {url!r} not rendered as <a href> in checklist.html")

    def test_checklist_badge_does_not_wrap(self):
        """상태 배지(미정/확정)가 좁은 폭에서 글자 단위로 세로 줄바꿈되지 않도록
        nowrap·flex-shrink:0 규칙이 있어야 한다 (모바일 ck-head flex 압축 방지)."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        self.assertRegex(html, r"\.badge\s*\{[^}]*white-space:\s*nowrap")
        self.assertRegex(html, r"\.badge\s*\{[^}]*flex-shrink:\s*0")

    def test_checklist_value_cell_wraps_long_text(self):
        """금액·권장 등 긴 값(.row .v)이 모바일 폭에서 가로 오버플로/클리핑되지
        않도록 flex 자식이 줄어들 수 있어야 한다(min-width:0 + overflow-wrap).
        긴 amount가 카드 밖으로 잘리던 회귀 가드."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        self.assertRegex(html, r"\.row\s+\.v\s*\{[^}]*min-width:\s*0")
        self.assertRegex(html, r"\.row\s+\.v\s*\{[^}]*overflow-wrap:\s*anywhere")

    def test_checklist_status_is_color_coded(self):
        """예약 탭 항목은 상태별 색상 클래스(badge·subcard accent)로 구분돼야 한다.
        확정/미정을 한눈에 스캔하기 위한 시각 회귀 가드."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        for cls in ("badge-done", "badge-pending", "status-pending", "status-done"):
            with self.subTest(cls=cls):
                self.assertIn(cls, html, f"checklist.html missing status class {cls!r}")

    def test_checklist_renders_structured_fields(self):
        """긴 노트 대신 금액·예약번호·권장 등 구조화 필드가 라벨 행으로 렌더돼야 한다."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        for label in ("금액", "권장", "예약번호"):
            with self.subTest(label=label):
                self.assertIn(f">{label}<", html,
                              f"checklist.html missing structured field label {label!r}")

    def test_checklist_long_note_is_collapsible(self):
        """긴 리서치 노트는 <details>로 접혀 기본 화면이 간결해야 한다."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("<details", html, "checklist long note should be collapsible (<details>)")
        self.assertIn("자세히", html, "collapsible note should have a '자세히' summary")

    def test_checklist_pending_due_has_dday(self):
        """미정(처리 필요) 항목의 마감일은 D-day 계산용 data-due 속성과
        클라이언트 스크립트를 동반해야 한다 (빌드 결정성 유지)."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn('data-due="2026-05-25"', html,
                      "pending due date should carry data-due for client-side D-day")
        self.assertIn('class="dday"', html, "checklist should render a .dday slot")
        self.assertIn("getAttribute('data-due')", html,
                      "checklist should include the D-day computing script")


class TransitFoldTests(unittest.TestCase):
    """이동 설명을 평이 요약(summary) + 접기 상세(details.leg)로 렌더하는 회귀 가드."""

    def test_plain_transit_labels_present(self):
        run()
        for path in (INDEX, ITINERARY):
            html = path.read_text(encoding="utf-8")
            for label in ("걸어서", "버스로", "전철로", "공항특급으로"):
                with self.subTest(path=path.name, label=label):
                    self.assertIn(label, html, f"plain transit label '{label}' missing in {path.name}")

    def test_transit_rendered_as_collapsible_leg(self):
        run()
        for path in (INDEX, ITINERARY, TABLE):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn('<details class="leg"', html,
                              f"{path.name} should render transit legs as <details class=\"leg\">")

    def test_verbose_route_kept_in_detail(self):
        """장문 route 텍스트는 접기 상세 안에 그대로 보존돼야 한다(정보 손실 없음)."""
        run()
        for path in (INDEX, ITINERARY):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn("교토역(京都駅)", html,
                              f"verbose route detail missing in {path.name}")

    def test_pass_recommendation_folded(self):
        """교통패스 추천(🎫)은 추천 요약 + 근거 접기로, 근거 텍스트는 보존."""
        run()
        for path in (INDEX, ITINERARY):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn("🎫 iPhone Apple Wallet ICOCA 단권", html,
                              f"pass recommendation summary missing in {path.name}")
                self.assertIn("본전 미달", html, f"pass rationale detail lost in {path.name}")

    def test_playbook_collapsed_but_text_preserved(self):
        run()
        import json as _json
        data = _json.loads((BASE / "data" / "itinerary.json").read_text(encoding="utf-8"))
        steps = data.get("trip", {}).get("transit_pass_playbook") or []
        for path in (INDEX, ITINERARY):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn("실행 단계", html, f"playbook header missing in {path.name}")
                for s in steps:
                    self.assertIn(s["when"], html, f"step.when {s['when']!r} not in {path.name}")


class NoteFoldTests(unittest.TestCase):
    """긴 예약·숙박 메모(예약번호·PIN·탑승객 등)를 접기로 렌더하는 회귀 가드."""

    def test_long_notes_collapsed_in_lodging_and_checklist(self):
        run()
        for path in (LODGING, CHECKLIST):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn('<details class="leg"', html,
                              f"{path.name} should collapse long notes into a fold")

    def test_collapsed_note_detail_preserved(self):
        """접어도 운영 메모 텍스트(PIN·확정번호)는 HTML에 그대로 남아야 한다."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("PIN 5647", html, "checklist note detail (PIN) lost after fold")
        self.assertIn("20260513170241828", html, "checklist note detail (confirm no.) lost after fold")


class ChecklistDetailFoldTests(unittest.TestCase):
    """긴 예약번호·권장 값을 접어 모바일에서 우측 정렬 셀이 넘치지 않게 하는 회귀 가드.

    PR #45가 lodging·checklist를 fold 비대상으로 두었던 것을, '모든 화면 접기' 요청에 따라
    checklist 구조화 행(예약번호·권장)에도 확장한다.
    """

    SHORT = "에어서울 RS · A8YW58 · 발권"
    LONG = ("Trip.com ① 1400827143416024 (성인2, ₩94,108) · ② 1400827143410570 "
            "(성인2, PIN 2362) · 6/1 10:30 · LEE/SOYEON · 조건부 취소")

    def test_short_value_stays_plain_row(self):
        out = build_index.detail_row("예약번호", self.SHORT)
        self.assertIn('class="row"', out)
        self.assertIn(">예약번호<", out)
        self.assertNotIn("<details", out)

    def test_long_value_is_collapsible(self):
        out = build_index.detail_row("예약번호", self.LONG)
        self.assertIn('<details class="leg"', out,
                      "long structured value should fold into <details class=\"leg\">")
        self.assertNotIn('class="row"', out)

    def test_long_value_detail_is_lossless(self):
        out = build_index.detail_row("예약번호", self.LONG)
        for tok in ("1400827143416024", "1400827143410570", "PIN 2362", "LEE/SOYEON", "조건부 취소"):
            with self.subTest(tok=tok):
                self.assertIn(tok, out, f"detail_row dropped {tok!r} after folding")

    def test_empty_value_renders_nothing(self):
        self.assertEqual(build_index.detail_row("예약번호", ""), "")
        self.assertEqual(build_index.detail_row("예약번호", None), "")

    def test_long_reference_folded_in_checklist_html(self):
        """프로덕션 빌드에서 긴 예약번호(사이호지·트립닷컴 등)는 접기 요약으로 렌더돼야 한다."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("▸", html)  # leg summary 마커
        self.assertIn("예약번호 ·", html,
                      "long reference should fold with a '예약번호 · …' summary")
        # 접어도 전체 예약번호 텍스트는 보존
        self.assertIn("1400827143410570", html,
                      "folded reference detail (saihoji 2nd booking) lost")


class PlaceLinkMarkupTests(unittest.TestCase):
    """note 본문의 위키식 마크업 [[label|query]]을 Google Maps 링크로 변환하는 헬퍼."""

    def test_link_places_converts_markup_with_query(self):
        """[[코메다|Komeda Coffee]] → <a href=...>코메다</a>"""
        text = "여기서 [[코메다|Komeda Coffee]]로 간다"
        out = build_index.link_places(text)
        self.assertIn('<a href="https://maps.google.com/?q=Komeda', out)
        self.assertIn(">코메다<", out)
        self.assertNotIn("[[", out, "markup should be converted, not left raw")

    def test_link_places_converts_label_only_markup(self):
        """[[교토역]] → 검색어=교토역"""
        text = "다음은 [[교토역]]이다"
        out = build_index.link_places(text)
        self.assertIn('<a href="https://maps.google.com/?q=', out)
        self.assertIn(">교토역<", out)

    def test_link_places_preserves_plain_urls(self):
        """본문의 HTTP URL은 linkify() 경유로 여전히 링크"""
        text = "자세한 정보는 https://example.com 를 보세요"
        out = build_index.link_places(text)
        self.assertIn('<a href="https://example.com"', out)

    def test_link_places_escapes_html_content(self):
        """마크업 외의 <, & 등은 escape"""
        text = "사람 & 동물 [[가게|Query]]"
        out = build_index.link_places(text)
        self.assertIn("&amp;", out, "& should be escaped")
        self.assertNotIn("&<", out)

    def test_link_places_preserves_multiple_markups(self):
        """다중 마크업 모두 변환"""
        text = "[[카페|Cafe]]과 [[식당|Restaurant]]을 찾아가자"
        out = build_index.link_places(text)
        self.assertEqual(out.count('<a href="https://maps.google.com'), 2)
        self.assertIn(">카페<", out)
        self.assertIn(">식당<", out)

    def test_link_places_nested_markups_safe(self):
        """중첩된 마크업은 처리하지 않음 (잘못된 입력)"""
        text = "[[a|[[b]]]]"
        # 단순히 깨지지 않고 처리되어야 함
        out = build_index.link_places(text)
        self.assertIsInstance(out, str)

    def test_strip_place_markup_returns_display_text(self):
        """strip_place_markup: [[label|query]] → label"""
        text = "여기서 [[코메다|Komeda]]로 간다"
        out = build_index.strip_place_markup(text)
        self.assertEqual(out, "여기서 코메다로 간다")

    def test_strip_place_markup_label_only(self):
        """[[label]] → label"""
        text = "[[교토역]]에서 만난다"
        out = build_index.strip_place_markup(text)
        self.assertEqual(out, "교토역에서 만난다")

    def test_strip_place_markup_multiple(self):
        """다중 마크업 모두 제거"""
        text = "[[가게1|Q1]]과 [[가게2|Q2]]"
        out = build_index.strip_place_markup(text)
        self.assertEqual(out, "가게1과 가게2")

    def test_strip_place_markup_no_markup(self):
        """마크업 없으면 원문 반환"""
        text = "이것은 일반 텍스트다"
        out = build_index.strip_place_markup(text)
        self.assertEqual(out, text)

    def test_memo_block_uses_display_text_for_length(self):
        """memo_block: 마크업 포함 note는 display text 길이로 fold 판정"""
        # 마크업 포함하면 실제 보이는 길이는 짧음
        short_with_markup = "[[코메다|Very Long Coffee Shop Name]]로 간다"
        out = build_index.memo_block(short_with_markup)
        # display text = "코메다로 간다" (13글자 < 50) → fold 안 함
        self.assertNotIn("<details", out, "short display text should not fold")
        self.assertIn("코메다", out, "label should be in output")

    def test_memo_block_long_display_text_folds(self):
        """마크업 제거 후 길이 > 50이면 fold"""
        # 마크업 제거하면 50자 초과
        long_note = "[[코메다|Query]]는 니조역 인근에 있고 " + "여기는 " * 10 + "아주 긴 설명입니다"
        out = build_index.memo_block(long_note)
        self.assertIn("<details", out, "long display text should fold")
        self.assertIn("maps.google.com", out, "place link should survive folding")

    def test_memo_block_place_link_in_detail(self):
        """long note 접어도 detail에 place link 보존"""
        memo = ("[[오가와 커피|Ogawa Coffee]]는 니조역 근처 유명한 커피숍입니다. "
                "정원도 아름답고 조용한 분위기에서 시간을 보낼 수 있습니다. "
                "가격은 중간대이고 계절 한정 메뉴가 많습니다.")
        out = build_index.memo_block(memo)
        self.assertIn('<details class="leg"', out, "long memo should fold")
        self.assertIn("maps.google.com/?q=Ogawa", out, "maps link must be in folded detail")
        self.assertIn(">오가와 커피<", out, "label must be clickable in detail")


class ItineraryTableTests(unittest.TestCase):
    def test_table_file_is_generated(self):
        run()
        self.assertTrue(TABLE.exists(), "viz/itinerary-table.html should be generated by build_index.py")

    def test_table_has_four_day_columns(self):
        run()
        html = TABLE.read_text(encoding="utf-8")
        for label in ("5/31", "6/1", "6/2", "6/3"):
            self.assertIn(label, html, f"day column '{label}' missing in itinerary-table.html")

    def test_table_has_key_activities(self):
        run()
        html = TABLE.read_text(encoding="utf-8")
        for activity in ("키요미즈데라", "죽림길", "후시미", "카덴쇼"):
            self.assertIn(activity, html, f"activity '{activity}' missing in itinerary-table.html")

    def test_table_is_standalone(self):
        run()
        html = TABLE.read_text(encoding="utf-8")
        self.assertNotIn("fetch(", html, "itinerary-table.html must be standalone (no fetch)")
        self.assertNotIn("XMLHttpRequest", html)

    def test_table_references_data_source(self):
        run()
        html = TABLE.read_text(encoding="utf-8")
        self.assertIn("data/itinerary.json", html)

    def test_check_detects_drift_in_table(self):
        run()
        original = TABLE.read_text(encoding="utf-8")
        try:
            TABLE.write_text(original + "<!-- drift -->", encoding="utf-8")
            r = run("--check")
            self.assertEqual(r.returncode, 1, "--check should fail when itinerary-table.html drifts")
        finally:
            TABLE.write_text(original, encoding="utf-8")


class BlogReviewsTests(unittest.TestCase):
    def test_blog_reviews_css_present(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        for cls in (".blog-strip", ".blog-card", ".blog-thumb", ".blog-comment"):
            self.assertIn(cls, itin, f"CSS class '{cls}' missing in itinerary.html")

    def test_blog_reviews_rendered_for_key_places(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertGreaterEqual(itin.count('class="blog-reviews"'), 1, "no blog-reviews sections rendered")
        self.assertGreaterEqual(itin.count('class="blog-card"'), 3, "expected at least 3 blog cards")
        # Key places should have reviews
        for place in ("키요미즈데라", "죽림길", "후시미"):
            self.assertIn(place, itin, f"'{place}' missing from itinerary.html")

    def test_blog_reviews_link_to_naver(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertIn("blog.naver.com", itin, "no Naver blog links found in itinerary.html")

    def test_blog_reviews_have_images(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertIn('class="blog-thumb"', itin, "blog thumbnail images missing")
        self.assertIn("pstatic.net", itin, "expected pstatic.net image URLs in blog reviews")

    def test_blog_reviews_standalone(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertNotIn("fetch(", itin, "itinerary.html must remain standalone (no fetch)")

    def test_blog_reviews_in_table_mobile_view(self):
        run()
        html = TABLE.read_text(encoding="utf-8")
        self.assertIn('class="blog-reviews"', html, "blog-reviews missing from itinerary-table.html mobile view")


class FoodQualityRenderTests(unittest.TestCase):
    def test_food_quality_rendered_in_itinerary(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            itin.count('class="food-quality"'), 1,
            "no food-quality badges rendered in itinerary.html",
        )
        # 실제 평점 출처가 본문에 노출되어야 함 (식당이 검증됐다는 신호).
        self.assertIn("타베로그", itin, "Tabelog rating missing from itinerary.html")

    def test_food_quality_rating_links_to_source(self):
        # 평점 출처(url)가 탭 가능한 링크여야 함 — 모바일에서 검증 가능성.
        run()
        for path in (ITINERARY, TABLE):
            html = path.read_text(encoding="utf-8")
            block = html[html.index('class="food-quality"'):]
            self.assertIn("tabelog.com", html, f"no Tabelog source link in {path.name}")
            self.assertRegex(
                block, r'class="food-quality"[^>]*>\s*<a href="https?://',
                f"food-quality rating is not wrapped in a link in {path.name}",
            )

    def test_food_quality_in_table_views(self):
        run()
        html = TABLE.read_text(encoding="utf-8")
        self.assertIn('class="food-quality"', html, "food-quality missing from itinerary-table.html")

    def test_food_quality_absent_from_minimal_index(self):
        run()
        index = INDEX.read_text(encoding="utf-8")
        self.assertNotIn('class="food-quality"', index, "minimal index.html should not carry food-quality badges")


class ItineraryMemoFoldTests(unittest.TestCase):
    """일정 카드·시간표의 긴 장소 메모·맛집 상세 노트를 '첫 문장 요약 + 접기'로 렌더(모든 화면 fold 확장)."""

    def test_short_memo_stays_plain(self):
        out = build_index.memo_block("17:00 마감 주의")
        self.assertIn('class="sub"', out)
        self.assertNotIn("<details", out)

    def test_long_memo_folds_with_first_sentence_summary(self):
        memo = "시오 도보 10분. 외정원 30분, 본궁 입장(¥1,300/인)은 시간·체력 절약 차 생략 권장 — 5/31 당일 컨디션으로 결정"
        out = build_index.memo_block(memo)
        self.assertIn('<details class="leg"', out)
        self.assertIn("시오 도보 10분</summary>", out, "first sentence should become the summary")
        self.assertIn("5/31 당일 컨디션으로 결정", out, "memo tail lost after folding")

    def test_long_memo_prefers_earlier_separator(self):
        # 첫 ". "가 60자 밖이면 ' · '로 앞 토막을 가른다
        memo = ("니넨자카 진입점 스타벅스 야사카차야점(100년 마치야 매장) · % 아라비카 교토 히가시야마점 — "
                "둘 중 택1 카페 휴식 권장. 4인 좌석 대기 길 수 있음")
        out = build_index.memo_block(memo)
        self.assertIn('<details class="leg"', out)
        self.assertIn("매장)</summary>", out)

    def test_memo_without_separator_uses_generic_summary(self):
        memo = "가" * 70
        out = build_index.memo_block(memo)
        self.assertIn('<details class="leg"', out)
        self.assertIn("상세 보기", out)
        self.assertIn("가" * 70, out, "memo body lost in generic fold")

    def test_custom_class_preserved_for_short_memo(self):
        out = build_index.memo_block("교토역 도보 5분", cls="t-note")
        self.assertIn('class="t-note"', out)

    def test_long_memo_folded_in_itinerary_views(self):
        run()
        for path in (ITINERARY, TABLE):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn("니넨자카(二年坂)·산넨자카(産寧坂) 인근 말차 디저트 카페</summary>", html,
                              "long place memo should fold into a first-sentence summary")
                self.assertIn("영업 11:00~20:00", html, "memo tail lost (not lossless)")

    def test_long_food_note_folded_but_rating_kept(self):
        run()
        html = ITINERARY.read_text(encoding="utf-8")
        self.assertIn('class="food-quality"', html, "rating line must stay visible")
        self.assertIn("쓰촨 중식</summary>", html, "long food note should fold to first sentence")
        self.assertIn("1인 ¥4,000~5,000", html, "food note detail lost after folding")


class ItineraryDocLinkTests(unittest.TestCase):
    """일정 항목의 link(url/label)가 화면에서 탭 가능한 <a> 앵커로 렌더되어야 함.

    조식 슬롯이 참조하는 breakfast-near-lodging.md를 모바일 화면에서 바로 열 수 있도록.
    """

    def _breakfast_link_urls(self):
        import json
        data = json.loads((BASE / "data" / "itinerary.json").read_text(encoding="utf-8"))
        urls = []
        for day in data["days"]:
            for it in day["items"]:
                link = it.get("link") or {}
                if link.get("url"):
                    urls.append(link["url"])
        return urls

    def test_itinerary_link_rendered_as_anchor(self):
        run()
        urls = self._breakfast_link_urls()
        self.assertGreater(len(urls), 0, "fixture must have at least one item with a link.url")
        for path in (ITINERARY, TABLE):
            html = path.read_text(encoding="utf-8")
            for url in urls:
                self.assertIn(
                    f'href="{url}"', html,
                    f"item link {url!r} not rendered as <a href> in {path.name}",
                )

    def test_itinerary_doc_link_is_onsite_not_github_or_raw_md(self):
        # Vercel 화면에서 GitHub 링크 금지 + .md raw 서빙 회피 → 사이트 내 HTML 페이지여야 함.
        urls = self._breakfast_link_urls()
        for url in urls:
            self.assertNotIn("github.com", url, f"Vercel doc link must not point to GitHub: {url!r}")
            self.assertFalse(url.endswith(".md"), f"doc link must not be a raw .md path: {url!r}")
            self.assertTrue(url.endswith(".html"), f"doc link should be an on-site HTML page: {url!r}")

    def test_breakfast_link_resolves_to_built_page(self):
        # 일정의 조식 doc-link 대상이 실제 빌드되는 viz 페이지여야 함.
        run()
        urls = set(self._breakfast_link_urls())
        for url in urls:
            self.assertTrue(
                (BASE / "viz" / url).exists(),
                f"breakfast doc-link target {url!r} is not a built page",
            )


class BreakfastPageTests(unittest.TestCase):
    def test_breakfast_page_built_with_key_content(self):
        run()
        html = BREAKFAST.read_text(encoding="utf-8")
        for needle in ("코메다", "카덴쇼", "아침별 권장", "출처"):
            self.assertIn(needle, html, f"breakfast.html missing {needle!r}")

    def test_breakfast_page_has_no_github_links(self):
        run()
        html = BREAKFAST.read_text(encoding="utf-8")
        self.assertNotIn("github.com", html, "breakfast.html (Vercel) must not contain GitHub links")

    def test_breakfast_stores_are_clickable_map_links(self):
        # 카페 등 모든 가게명은 모바일에서 탭하면 지도가 열려야 함.
        import json as _json
        run()
        html = BREAKFAST.read_text(encoding="utf-8")
        bf = _json.loads((BASE / "data" / "breakfast.json").read_text(encoding="utf-8"))
        store_count = sum(
            len(g.get("stores", []))
            for lg in bf["lodgings"]
            for g in lg["groups"]
        )
        self.assertGreaterEqual(store_count, 10, "fixture sanity: expected many stores")
        map_links = html.count("google.com/maps/search")
        self.assertGreaterEqual(
            map_links, store_count,
            f"every store should be a map link: {map_links} links < {store_count} stores",
        )
        # 대표 가게명이 앵커 안에 들어가야 함.
        self.assertRegex(html, r'<a class="map-link"[^>]*>코메다[^<]*🗺</a>')

    def test_breakfast_page_standalone(self):
        run()
        html = BREAKFAST.read_text(encoding="utf-8")
        self.assertNotIn("fetch(", html, "breakfast.html must remain standalone (no fetch)")

    def test_breakfast_shows_menu_and_price(self):
        # 가격·메뉴가 전용 라인(.bf-menu)으로 노출돼야 함 (스크린샷 피드백 회귀 가드).
        run()
        html = BREAKFAST.read_text(encoding="utf-8")
        self.assertIn("bf-menu", html, "menu line class missing")
        for price in ("¥750", "¥650", "¥800", "¥1,660"):
            with self.subTest(price=price):
                self.assertIn(price, html, f"breakfast.html missing price {price!r}")

    def test_breakfast_long_text_not_right_aligned_rows(self):
        # 긴 텍스트(아침 표·아침별 권장)는 우측정렬 k/v 행이 아니라
        # 좌측정렬 블록(.bf-item/.bf-body)으로 렌더돼야 함.
        import json as _json
        import re
        run()
        html = BREAKFAST.read_text(encoding="utf-8")
        bf = _json.loads((BASE / "data" / "breakfast.json").read_text(encoding="utf-8"))
        block_count = len(bf["mornings"]) + len(bf["recommendations"])
        self.assertGreaterEqual(html.count('class="bf-item"'), block_count)
        self.assertIn("bf-body", html)
        # 권장 본문이 .v(우측정렬) 안에 들어가면 안 됨.
        reco_text = bf["recommendations"][0]["text"][:20]
        self.assertNotRegex(html, r'<span class="v">[^<]*' + re.escape(reco_text))

    def test_breakfast_long_blocks_are_collapsible(self):
        # 긴 가게 목록·주의는 <details>로 접혀 모바일 기본 화면이 간결해야 함.
        import json as _json
        run()
        html = BREAKFAST.read_text(encoding="utf-8")
        bf = _json.loads((BASE / "data" / "breakfast.json").read_text(encoding="utf-8"))
        group_count = sum(len(lg["groups"]) for lg in bf["lodgings"])
        # 각 가게 그룹 + 주의 블록이 fold(<details class="leg">)로 감싸져야 함.
        details = html.count('<details class="leg"')
        self.assertGreaterEqual(
            details, group_count + 1,
            f"expected >= {group_count + 1} folds (groups + caution), got {details}",
        )
        # 접힘 요약에 그룹 개수 표기가 들어가야 함 (예: "· 3곳").
        self.assertRegex(html, r"<summary>[^<]*· \d+곳</summary>")


class TabBarTests(unittest.TestCase):
    TAB_PAGES = (INDEX, ITINERARY, TABLE, CHECKLIST, LODGING, ARCHIVE)

    def test_tab_bar_present_on_all_pages(self):
        run()
        for path in self.TAB_PAGES:
            with self.subTest(path=path.name):
                self.assertIn('class="tab-bar"', path.read_text(encoding="utf-8"),
                              f"{path.name} is missing the bottom tab bar")

    def test_each_page_has_correct_active_tab(self):
        run()
        cases = {
            INDEX:    "home",
            ITINERARY: "itinerary",
            TABLE:    "itinerary",
            CHECKLIST: "checklist",
            LODGING:  "lodging",
        }
        for path, expected in cases.items():
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn(f'data-tab="{expected}"', html,
                              f"{path.name} should have active tab '{expected}'")

    def test_lodging_file_is_generated(self):
        run()
        self.assertTrue(LODGING.exists(), "viz/lodging.html should be generated")

    def test_lodging_has_key_content(self):
        run()
        html = LODGING.read_text(encoding="utf-8")
        for keyword in ("에어비앤비", "카덴쇼", "항공"):
            self.assertIn(keyword, html, f"lodging.html missing '{keyword}'")


DOC_PAGE_OUTPUTS = (
    BASE / "viz" / "report.html",
    BASE / "viz" / "itinerary-doc.html",
    BASE / "viz" / "research.html",
    BASE / "viz" / "transit-pass.html",
    BASE / "viz" / "decision-kyoto.html",
    BASE / "viz" / "decision-log.html",
)


class DocPageTests(unittest.TestCase):
    """레포 마크다운 → 사이트 내 HTML 렌더 페이지 (GitHub 링크 대체)."""

    def test_all_doc_pages_generated(self):
        run()
        for path in DOC_PAGE_OUTPUTS:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"{path.relative_to(BASE)} not generated")

    def test_doc_pages_have_no_github_links(self):
        """검사 J 핵심: 렌더된 문서 페이지에 github.com이 남으면 안 된다."""
        run()
        for path in DOC_PAGE_OUTPUTS:
            with self.subTest(path=path.name):
                self.assertNotIn("github.com", path.read_text(encoding="utf-8"))

    def test_report_renders_markdown_table_and_strips_frontmatter(self):
        run()
        html = (BASE / "viz" / "report.html").read_text(encoding="utf-8")
        self.assertIn("<table>", html, "GFM table should render from final-report.md")
        self.assertIn('<div class="doc">', html, "doc body wrapper missing")
        self.assertNotIn("title: 일본 여행 결정", html, "YAML frontmatter should be stripped")

    def test_decision_log_index_links_kyoto_entry(self):
        run()
        html = (BASE / "viz" / "decision-log.html").read_text(encoding="utf-8")
        self.assertIn('href="decision-kyoto.html"', html, "kyoto decision entry should link to its page")
        entries = sorted(
            p for p in (BASE / "docs" / "decision-log").glob("*.md") if p.name != "README.md"
        )
        self.assertEqual(html.count("<li>"), len(entries), "every decision-log entry should be listed")

    def test_checklist_doc_links_rewritten_to_in_site_pages(self):
        """booking-checklist.json의 레포 문서 경로 link.url이 사이트 내 페이지로 치환되어야 한다."""
        run()
        html = CHECKLIST.read_text(encoding="utf-8")
        self.assertIn('href="research.html"', html, "research doc link should resolve in-site")
        self.assertIn('href="transit-pass.html"', html, "transit-pass doc link should resolve in-site")
        self.assertNotIn("docs/booking-research-2026-05-24.md\"", html,
                         "raw repo md path should not be used as href")

    def test_doc_pages_have_og_meta(self):
        run()
        for path in DOC_PAGE_OUTPUTS:
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                self.assertIn('property="og:title"', html)
                self.assertIn("/assets/og-", html)

    def test_doc_pages_drift_detected_by_check(self):
        run()
        for path in DOC_PAGE_OUTPUTS:
            with self.subTest(path=path.name):
                original = path.read_text(encoding="utf-8")
                try:
                    path.write_text(original + "<!-- drift -->", encoding="utf-8")
                    r = run("--check")
                    self.assertEqual(r.returncode, 1, f"--check should fail on drift in {path.name}")
                finally:
                    path.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
