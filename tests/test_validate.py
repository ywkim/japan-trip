"""validate.py: 가격 필드·묵은 가격·SYNC 무결성 검사 단위 테스트."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402


def make_fixture(tmp: Path, *, cost: dict, index_html: str = "", final_report: str = "## §1\n## §2\n") -> Path:
    (tmp / "data").mkdir()
    (tmp / "reports").mkdir()
    (tmp / "data" / "cost-options.json").write_text(json.dumps(cost), encoding="utf-8")
    (tmp / "reports" / "final-report.md").write_text(final_report, encoding="utf-8")
    if index_html:
        (tmp / "index.html").write_text(index_html, encoding="utf-8")
    return tmp


VALID_COST = {
    "flights": [{"id": "f1", "source": "Skyscanner 2026-05-11", "data_quality": "researched_market_rate"}],
    "lodging": [{"id": "l1", "source": "Agoda 2026-05-11", "data_quality": "confirmed_booking"}],
    "daily_fixed": [{"id": "d1", "source": "official 2026-05-11", "data_quality": "official_fare"}],
    "one_time": [{"id": "o1", "source": "JR 2026-05-11", "data_quality": "official_fare"}],
}


class PriceFieldTests(unittest.TestCase):
    def test_valid_data_passes(self):
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=VALID_COST, index_html="<html></html>")
            errs, warns = validate.run(base, date(2026, 5, 12))
            self.assertEqual(errs, [])

    def test_missing_source_fails(self):
        bad = json.loads(json.dumps(VALID_COST))
        del bad["flights"][0]["source"]
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=bad, index_html="<html></html>")
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any("missing 'source'" in e for e in errs), errs)

    def test_missing_data_quality_fails(self):
        bad = json.loads(json.dumps(VALID_COST))
        del bad["lodging"][0]["data_quality"]
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=bad, index_html="<html></html>")
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any("missing 'data_quality'" in e for e in errs), errs)

    def test_invalid_data_quality_value_fails(self):
        bad = json.loads(json.dumps(VALID_COST))
        bad["one_time"][0]["data_quality"] = "guess"
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=bad, index_html="<html></html>")
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any("not in" in e for e in errs), errs)


class StalePriceTests(unittest.TestCase):
    def test_stale_30_to_60_days_warns_only(self):
        cost = json.loads(json.dumps(VALID_COST))
        cost["flights"][0]["source"] = "Skyscanner 2026-04-01"  # 41d before 2026-05-12
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=cost, index_html="<html></html>")
            errs, warns = validate.run(base, date(2026, 5, 12))
            self.assertEqual(errs, [])
            self.assertTrue(any("aging" in w for w in warns), warns)

    def test_stale_over_60_days_fails(self):
        cost = json.loads(json.dumps(VALID_COST))
        cost["flights"][0]["source"] = "Skyscanner 2026-02-01"  # 100d before 2026-05-12
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=cost, index_html="<html></html>")
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any("stale" in e for e in errs), errs)

    def test_confirmed_booking_old_does_not_fail(self):
        cost = json.loads(json.dumps(VALID_COST))
        cost["lodging"][0]["source"] = "Agoda 2025-01-01"
        cost["lodging"][0]["data_quality"] = "confirmed_booking"
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=cost, index_html="<html></html>")
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertEqual(errs, [])


class SyncCommentTests(unittest.TestCase):
    def test_valid_sync_path_passes(self):
        html = '<!-- SYNC: reports/final-report.md §1 -->'
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=VALID_COST, index_html=html)
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertEqual(errs, [])

    def test_missing_sync_path_fails(self):
        html = '<!-- SYNC: data/nonexistent.json -->'
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=VALID_COST, index_html=html)
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any("SYNC path missing" in e for e in errs), errs)

    def test_out_of_range_section_fails(self):
        html = '<!-- SYNC: reports/final-report.md §99 -->'
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=VALID_COST, index_html=html)
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any("out of range" in e for e in errs), errs)

    def test_missing_index_html_fails(self):
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=VALID_COST, index_html="")
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any("index.html missing" in e for e in errs), errs)


class ProductionDataTests(unittest.TestCase):
    """현재 레포 데이터가 validate를 통과하는지 회귀 검사."""

    def test_repo_data_validates(self):
        base = Path(__file__).resolve().parent.parent
        errs, _ = validate.run(base, date(2026, 5, 12))
        self.assertEqual(errs, [], f"production data validation failed: {errs}")


if __name__ == "__main__":
    unittest.main()
