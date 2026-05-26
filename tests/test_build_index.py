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
        source가 http URL이면 route 텍스트가 <a href> 링크로 렌더돼야 한다.
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
                src = af.get("source", "")
                if src.startswith("http"):
                    url_legs.append((af["mode"], src.split()[0]))
        self.assertGreater(len(url_legs), 0, "fixture must have at least one URL-sourced leg")
        for path in (INDEX, ITINERARY):
            with self.subTest(path=path.name):
                html = path.read_text(encoding="utf-8")
                for mode, url in url_legs[:5]:
                    self.assertIn(url, html, f"{mode} leg URL {url!r} not linked in {path.name}")

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
        """data/booking-checklist.json 항목 note에 포함된 http URL이
        viz/checklist.html에서 클릭 가능한 <a href> 링크로 렌더돼야 한다.
        모바일 예약 탭에서 출처·상세 문서로 바로 이동하기 위한 회귀 가드.
        """
        run()
        import json as _json
        import re as _re
        data = _json.loads((BASE / "data" / "booking-checklist.json").read_text(encoding="utf-8"))
        url_re = _re.compile(r"https?://[^\s]+")
        urls = []
        for it in data["items"]:
            urls.extend(url_re.findall(it.get("note", "")))
        self.assertGreater(len(urls), 0, "fixture must have at least one note containing a URL")
        html = CHECKLIST.read_text(encoding="utf-8")
        for url in urls:
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
                self.assertIn("JR 하루카 KIX→교토역", html,
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


if __name__ == "__main__":
    unittest.main()
