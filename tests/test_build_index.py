"""build_index.py: 결정론(idempotent)·--check 동작·핵심 섹션 회귀 테스트."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
INDEX = BASE / "index.html"
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
        first = INDEX.read_text(encoding="utf-8")
        run()
        second = INDEX.read_text(encoding="utf-8")
        self.assertEqual(first, second, "build_index.py is not idempotent")

    def test_check_detects_drift(self):
        run()
        original = INDEX.read_text(encoding="utf-8")
        try:
            INDEX.write_text(original + "<!-- drift -->", encoding="utf-8")
            r = run("--check")
            self.assertEqual(r.returncode, 1, "expected --check to fail on drift")
        finally:
            INDEX.write_text(original, encoding="utf-8")

    def test_all_sections_rendered(self):
        run()
        html = INDEX.read_text(encoding="utf-8")
        for section_id in ("summary", "tsuyu", "airbnb", "kadensho", "flights", "budget", "itinerary", "checklist", "score"):
            self.assertIn(f'id="{section_id}"', html, f"section #{section_id} missing")

    def test_sync_comments_present(self):
        run()
        html = INDEX.read_text(encoding="utf-8")
        self.assertGreaterEqual(html.count("<!-- SYNC:"), 9, "expected at least 9 SYNC comments (one per section)")


if __name__ == "__main__":
    unittest.main()
