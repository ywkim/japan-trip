"""score.py·budget.py --json 출력 스키마 회귀 테스트."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def run_json(script: str) -> dict:
    r = subprocess.run([sys.executable, str(BASE / "scripts" / script), "--json"],
                       capture_output=True, text=True, cwd=BASE, check=True)
    return json.loads(r.stdout)


def run_human(script: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(BASE / "scripts" / script)],
                          capture_output=True, text=True, cwd=BASE)


class ScoreJsonTests(unittest.TestCase):
    def test_json_schema(self):
        data = run_json("score.py")
        self.assertIn("scored", data)
        self.assertIn("unscored", data)
        for r in data["scored"]:
            self.assertIn("id", r)
            self.assertIn("name", r)
            self.assertIsInstance(r["score"], (int, float))
            self.assertGreaterEqual(r["score"], 0)
            self.assertLessEqual(r["score"], 10)

    def test_scored_sorted_desc(self):
        data = run_json("score.py")
        scores = [r["score"] for r in data["scored"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_kyoto_full_weight(self):
        """교토는 7기준 모두 입력됨 → used_weight == 1.0"""
        data = run_json("score.py")
        kyoto = next((r for r in data["scored"] if r["id"] == "kyoto"), None)
        self.assertIsNotNone(kyoto)
        self.assertAlmostEqual(kyoto["used_weight"], 1.0, places=2)

    def test_human_output_preserved(self):
        r = run_human("score.py")
        self.assertEqual(r.returncode, 0)
        self.assertIn("교토", r.stdout)


class BudgetJsonTests(unittest.TestCase):
    def test_json_schema(self):
        data = run_json("budget.py")
        self.assertIn("cap_krw", data)
        self.assertIn("scenarios", data)
        for s in data["scenarios"]:
            self.assertIn("id", s)
            self.assertIn("confirmed_total_krw", s)
            self.assertIn("passes_cap", s)
            self.assertIsInstance(s["passes_cap"], bool)
            for c in s["categories"]:
                self.assertIn(c["status"], ("ok", "near", "over"))

    def test_target_scenario_exists(self):
        data = run_json("budget.py")
        ids = [s["id"] for s in data["scenarios"]]
        self.assertIn("kyoto_may31_kadensho_early_bird", ids)

    def test_human_output_preserved(self):
        r = run_human("budget.py")
        self.assertEqual(r.returncode, 0)
        self.assertIn("예산 상한", r.stdout)


class FetchAssetsDocUrlTests(unittest.TestCase):
    """fetch_assets.py가 docs/*.md 마크다운 이미지 URL도 수집한다."""

    def test_collect_doc_urls_returns_list(self):
        from scripts.fetch_assets import collect_doc_urls
        urls = collect_doc_urls()
        self.assertIsInstance(urls, list)
        for u in urls:
            self.assertTrue(u.startswith("http"), f"non-http URL in doc urls: {u}")

    def test_collect_doc_urls_no_duplicates(self):
        from scripts.fetch_assets import collect_doc_urls
        urls = collect_doc_urls()
        self.assertEqual(len(urls), len(set(urls)), "duplicate URLs found")

    def test_collect_doc_urls_includes_wikimedia_images(self):
        """isetan-porta-shopping-translation.md의 위키미디어 이미지가 포함된다."""
        from scripts.fetch_assets import collect_doc_urls
        urls = collect_doc_urls()
        wikimedia = [u for u in urls if "upload.wikimedia.org" in u]
        self.assertTrue(len(wikimedia) >= 1, f"위키미디어 이미지가 doc URLs에 없음: {urls[:5]}")


class FetchAssetsNonAsciiUrlTests(unittest.TestCase):
    """fetch_assets.py가 non-ASCII 문자 포함 URL을 퍼센트 인코딩해 처리한다."""

    def test_safe_url_ascii_unchanged(self):
        from scripts.fetch_assets import safe_url
        url = "https://example.com/path/image.jpg"
        self.assertEqual(safe_url(url), url)

    def test_safe_url_encodes_non_ascii(self):
        from scripts.fetch_assets import safe_url
        url = "https://sushinomusashi.com/wp-content/uploads/2022/10/バッテラ.jpg"
        result = safe_url(url)
        self.assertNotIn("バッテラ", result)
        self.assertIn("%E3%83%90%E3%83%83%E3%83%86%E3%83%A9", result)
        self.assertTrue(result.startswith("https://sushinomusashi.com/"))

    def test_safe_url_preserves_query_and_fragment(self):
        from scripts.fetch_assets import safe_url
        url = "https://example.com/path/画像.jpg?size=800&foo=bar"
        result = safe_url(url)
        self.assertIn("size=800", result)
        self.assertIn("foo=bar", result)
        self.assertNotIn("画像", result)


if __name__ == "__main__":
    unittest.main()
