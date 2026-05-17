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
ALL_OUTPUTS = (INDEX, ITINERARY, CHECKLIST)
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
        html = INDEX.read_text(encoding="utf-8")
        for section_id in ("summary", "tsuyu", "airbnb", "kadensho", "flights", "budget", "itinerary", "checklist", "score"):
            self.assertIn(f'id="{section_id}"', html, f"section #{section_id} missing")

    def test_sync_comments_present(self):
        run()
        html = INDEX.read_text(encoding="utf-8")
        self.assertGreaterEqual(html.count("<!-- SYNC:"), 9, "expected at least 9 SYNC comments (one per section)")

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

    def test_all_outputs_use_token_palette(self):
        run()
        for path in ALL_OUTPUTS:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("#F7F6F2", content, f"{path.name}: light bg token not injected")
                self.assertIn("#3E5C76", content, f"{path.name}: slate-indigo accent not injected")
                for legacy in ("#d33", "#fafafa", "#ff6464", "#c33", "#c80", "#2a7"):
                    self.assertNotIn(
                        legacy, content,
                        f"{path.name}: legacy color {legacy} still present",
                    )

    def test_route_candidates_rendered_in_itinerary(self):
        run()
        itin = ITINERARY.read_text(encoding="utf-8")
        self.assertIn("후보 코스", itin, "route candidates section missing in itinerary.html")
        for candidate_name in ("여유형", "서북 사찰 집중형", "미식+문화 체험형"):
            self.assertIn(candidate_name, itin, f"candidate '{candidate_name}' missing in itinerary.html")


if __name__ == "__main__":
    unittest.main()
