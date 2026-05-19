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
ALL_OUTPUTS = (INDEX, ITINERARY, CHECKLIST, TABLE, LODGING)
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

    def test_check_detects_drift_in_each_output(self):
        run()
        for path in ALL_OUTPUTS:
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
        # 홈 탭: 요약·장마·예산·점수
        html = INDEX.read_text(encoding="utf-8")
        for section_id in ("summary", "tsuyu", "budget", "score"):
            self.assertIn(f'id="{section_id}"', html, f"index.html section #{section_id} missing")
        # 숙박·항공 탭: lodging.html에 분리
        lodging = LODGING.read_text(encoding="utf-8")
        for section_id in ("airbnb", "kadensho", "flights"):
            self.assertIn(f'id="{section_id}"', lodging, f"lodging.html section #{section_id} missing")

    def test_sync_comments_present(self):
        run()
        total = sum(p.read_text(encoding="utf-8").count("<!-- SYNC:") for p in ALL_OUTPUTS)
        self.assertGreaterEqual(total, 9, "expected at least 9 SYNC comments across all outputs (one per section)")

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


class TabBarTests(unittest.TestCase):
    TAB_PAGES = (INDEX, ITINERARY, TABLE, CHECKLIST, LODGING)

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
