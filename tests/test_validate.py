"""validate.py: 가격 필드·묵은 가격·SYNC 무결성 검사 단위 테스트."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402


def make_fixture(
    tmp: Path,
    *,
    cost: dict,
    index_html: str = "",
    final_report: str = "## §1\n## §2\n",
    weather: dict | None = None,
    weather_md: str | None = None,
    flights: dict | None = None,
    flights_md: str | None = None,
    design_tokens: dict | None = None,
    design_md: str | None = None,
    itinerary: dict | None = None,
    vercel_html: dict | None = None,
) -> Path:
    (tmp / "data").mkdir()
    (tmp / "reports").mkdir()
    (tmp / "docs").mkdir()
    (tmp / "data" / "cost-options.json").write_text(json.dumps(cost), encoding="utf-8")
    (tmp / "reports" / "final-report.md").write_text(final_report, encoding="utf-8")
    if index_html:
        (tmp / "index.html").write_text(index_html, encoding="utf-8")
    if weather is not None:
        (tmp / "data" / "weather.json").write_text(json.dumps(weather, ensure_ascii=False), encoding="utf-8")
    if weather_md is not None:
        (tmp / "docs" / "weather.md").write_text(weather_md, encoding="utf-8")
    if flights is not None:
        (tmp / "data" / "flights.json").write_text(json.dumps(flights, ensure_ascii=False), encoding="utf-8")
    if flights_md is not None:
        (tmp / "docs" / "flights.md").write_text(flights_md, encoding="utf-8")
    if design_tokens is not None:
        (tmp / "data" / "design-tokens.json").write_text(
            json.dumps(design_tokens, ensure_ascii=False), encoding="utf-8"
        )
    if design_md is not None:
        (tmp / "DESIGN.md").write_text(design_md, encoding="utf-8")
    if itinerary is not None:
        (tmp / "data" / "itinerary.json").write_text(json.dumps(itinerary, ensure_ascii=False), encoding="utf-8")
    if vercel_html is not None:
        for rel, content in vercel_html.items():
            path = tmp / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return tmp


VALID_COST = {
    "flights": [{"id": "f1", "source": "Skyscanner 2026-05-11", "data_quality": "researched_market_rate"}],
    "lodging": [{"id": "l1", "source": "Agoda 2026-05-11", "data_quality": "confirmed_booking"}],
    "daily_fixed": [{"id": "d1", "source": "official 2026-05-11", "data_quality": "official_fare"}],
    "one_time": [{"id": "o1", "source": "JR 2026-05-11", "data_quality": "official_fare"}],
}


VALID_WEATHER = {
    "months": ["2026-05", "2026-06"],
    "cities": {
        "tokyo": {
            "name": "도쿄",
            "2026-05": {"comfort_score": 8},
            "2026-06": {"comfort_score": 5},
        },
        "osaka": {
            "name": "오사카",
            "2026-05": {"comfort_score": 9},
            "2026-06": {"comfort_score": 5},
        },
    },
}


VALID_WEATHER_MD = """# 날씨

| 후보 | 5월 | 6월 |
|---|---|---|
| 도쿄 | 8 | 5 |
| 오사카 | 9 | 5 |
"""


VALID_FLIGHTS = {
    "version": "v2.1",
    "snapshot_date": "2026-05-11",
    "ranking_4pax_median_5night_2026_05": {
        "by_total_low_to_high": [
            {"city": "fukuoka", "route": "ICN-FUK", "median_4pax_krw": 630000},
            {"city": "osaka", "route": "GMP-KIX", "median_4pax_krw": 850000},
        ],
    },
}


VALID_FLIGHTS_MD = """# 항공권 (v2.1 · 2026-05-11)

| 도시 | 4인 median |
|---|---|
| 후쿠오카 | 63만 |
| 오사카 | 85만 |
"""


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


class WeatherSyncTests(unittest.TestCase):
    """검사 E: docs/weather.md ↔ data/weather.json 동기화."""

    def test_weather_in_sync_passes(self):
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                weather=VALID_WEATHER,
                weather_md=VALID_WEATHER_MD,
                flights=VALID_FLIGHTS,
                flights_md=VALID_FLIGHTS_MD,
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertEqual(errs, [])

    def test_weather_score_drift_fails(self):
        bad_md = VALID_WEATHER_MD.replace("| 도쿄 | 8 | 5 |", "| 도쿄 | 3 | 7 |")
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                weather=VALID_WEATHER,
                weather_md=bad_md,
                flights=VALID_FLIGHTS,
                flights_md=VALID_FLIGHTS_MD,
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any(e.startswith("[E]") for e in errs), errs)

    def test_weather_missing_city_in_md_fails(self):
        bad_md = "# 날씨\n\n| 도시 | 5월 | 6월 |\n|---|---|---|\n| 도쿄 | 8 | 5 |\n"
        # 오사카가 md에 없음
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                weather=VALID_WEATHER,
                weather_md=bad_md,
                flights=VALID_FLIGHTS,
                flights_md=VALID_FLIGHTS_MD,
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any(e.startswith("[E]") and "오사카" in e for e in errs), errs)


class FlightsSyncTests(unittest.TestCase):
    """검사 F: docs/flights.md ↔ data/flights.json 동기화."""

    def test_flights_in_sync_passes(self):
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                weather=VALID_WEATHER,
                weather_md=VALID_WEATHER_MD,
                flights=VALID_FLIGHTS,
                flights_md=VALID_FLIGHTS_MD,
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertEqual(errs, [])

    def test_snapshot_date_drift_fails(self):
        bad_md = VALID_FLIGHTS_MD.replace("2026-05-11", "2026-01-01")
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                weather=VALID_WEATHER,
                weather_md=VALID_WEATHER_MD,
                flights=VALID_FLIGHTS,
                flights_md=bad_md,
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any(e.startswith("[F]") and "snapshot_date" in e for e in errs), errs)

    def test_no_median_match_fails(self):
        # md에 4인 median 만원 표기 (63만/85만)가 둘 다 없음 — drift
        bad_md = "# 항공권 (v2.1 · 2026-05-11)\n\n| 도시 | median |\n|---|---|\n| 후쿠오카 | 99만 |\n"
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                weather=VALID_WEATHER,
                weather_md=VALID_WEATHER_MD,
                flights=VALID_FLIGHTS,
                flights_md=bad_md,
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any(e.startswith("[F]") and "median" in e for e in errs), errs)


def _itin(items_day0, walking_km=1):
    return {
        "trip": {"destination": "교토", "dates": "2026-05-31 → 2026-06-03", "nights": 3, "travelers": 4, "walking_km_total": walking_km},
        "days": [
            {"date": "2026-05-31", "day_label": "D1", "walking_km": walking_km, "lodging": "—", "items": items_day0}
        ],
    }


VALID_ARRIVE_FROM = {
    "mode": "bus",
    "duration_min": 4,
    "distance_km": 1.6,
    "route": "市バス 59",
    "source": "https://example.com",
    "source_fetched_at": "2026-05-17",
    "data_quality": "researched_market_rate",
}


class ItineraryTransitTests(unittest.TestCase):
    """검사 G: data/itinerary.json arrive_from 무결성 + walking_km 정합성."""

    def _base(self, td, itin):
        return make_fixture(Path(td), cost=VALID_COST, index_html="<html></html>", itinerary=itin)

    def test_valid_arrive_from_passes(self):
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": VALID_ARRIVE_FROM},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertEqual(errs, [], errs)

    def test_missing_source_fails(self):
        af = dict(VALID_ARRIVE_FROM); del af["source"]
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": af},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[G]") and "source" in e for e in errs), errs)

    def test_invalid_data_quality_fails(self):
        af = dict(VALID_ARRIVE_FROM); af["data_quality"] = "guess"
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": af},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[G]") and "data_quality" in e for e in errs), errs)

    def test_tbd_quality_accepted(self):
        af = dict(VALID_ARRIVE_FROM); af["data_quality"] = "tbd_needs_browser_mcp"
        af["source_fetched_at"] = "2020-01-01"  # tbd는 stale 검사 면제
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": af},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertEqual(errs, [], errs)

    def test_stale_source_fetched_at_fails(self):
        af = dict(VALID_ARRIVE_FROM); af["source_fetched_at"] = "2026-01-01"  # 136d
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": af},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[G]") and "stale" in e for e in errs), errs)

    def test_walk_sum_exceeds_declared_fails(self):
        # declared walking_km=1, leg walk distance 5km — sum exceeds declared by 4km > 2km tolerance
        af_walk = {**VALID_ARRIVE_FROM, "mode": "walk", "distance_km": 5.0}
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": af_walk},
        ], walking_km=1)
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[G]") and "exceeds" in e for e in errs), errs)

    def test_walk_sum_under_declared_ok(self):
        # declared walking_km=5 (경내 산책 포함), leg walk 0.6km — OK
        af_walk = {**VALID_ARRIVE_FROM, "mode": "walk", "distance_km": 0.6}
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": af_walk},
        ], walking_km=5)
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertEqual(errs, [], errs)

    def test_invalid_mode_fails(self):
        af = dict(VALID_ARRIVE_FROM); af["mode"] = "teleport"
        itin = _itin([
            {"time": "09:00", "title": "A", "maps_query": "A"},
            {"time": "10:00", "title": "B", "maps_query": "B", "arrive_from": af},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[G]") and "mode" in e for e in errs), errs)
VALID_TOKENS = {
    "theme_name": "Quiet Ledger",
    "version": "1.0.0",
    "color": {
        "light": {"bg": "#F7F6F2", "ink": "#1B1D24", "accent": "#3E5C76"},
        "dark": {"bg": "#161821", "ink": "#E8E6DE", "accent": "#8AA8C7"},
    },
}

VALID_DESIGN_MD = """# DESIGN.md — Quiet Ledger

Version: 1.0.0

Colors used: `#F7F6F2`, `#1B1D24`, `#3E5C76`, `#161821`, `#E8E6DE`, `#8AA8C7`.
"""

class DesignSyncTests(unittest.TestCase):
    """검사 H: DESIGN.md ↔ data/design-tokens.json hex 양방향 + theme_name·version."""

    def _fixture(self, td, *, design_md=VALID_DESIGN_MD, tokens=None):
        return make_fixture(
            Path(td),
            cost=VALID_COST,
            index_html="<html></html>",
            design_tokens=tokens if tokens is not None else VALID_TOKENS,
            design_md=design_md,
        )

    def test_design_in_sync_passes(self):
        with tempfile.TemporaryDirectory() as td:
            base = self._fixture(td)
            errs, _ = validate.run(base, date(2026, 5, 14))
            self.assertEqual([e for e in errs if e.startswith("[H]")], [], errs)

    def test_hex_in_md_not_in_tokens_fails(self):
        bad_md = VALID_DESIGN_MD + "\nstray color: #ABCDEF\n"
        with tempfile.TemporaryDirectory() as td:
            base = self._fixture(td, design_md=bad_md)
            errs, _ = validate.run(base, date(2026, 5, 14))
            self.assertTrue(
                any(e.startswith("[H]") and "not in design-tokens.json" in e for e in errs),
                errs,
            )

    def test_token_color_not_in_md_fails(self):
        bad_tokens = json.loads(json.dumps(VALID_TOKENS))
        bad_tokens["color"]["light"]["accent"] = "#123456"
        with tempfile.TemporaryDirectory() as td:
            base = self._fixture(td, tokens=bad_tokens)
            errs, _ = validate.run(base, date(2026, 5, 14))
            self.assertTrue(
                any(e.startswith("[H]") and "not documented in DESIGN.md" in e for e in errs),
                errs,
            )

    def test_theme_name_drift_fails(self):
        bad_tokens = json.loads(json.dumps(VALID_TOKENS))
        bad_tokens["theme_name"] = "Loud Ledger"
        with tempfile.TemporaryDirectory() as td:
            base = self._fixture(td, tokens=bad_tokens)
            errs, _ = validate.run(base, date(2026, 5, 14))
            self.assertTrue(
                any(e.startswith("[H]") and "theme_name" in e for e in errs), errs
            )

    def test_version_drift_fails(self):
        bad_tokens = json.loads(json.dumps(VALID_TOKENS))
        bad_tokens["version"] = "9.9.9"
        with tempfile.TemporaryDirectory() as td:
            base = self._fixture(td, tokens=bad_tokens)
            errs, _ = validate.run(base, date(2026, 5, 14))
            self.assertTrue(
                any(e.startswith("[H]") and "version" in e for e in errs), errs
            )


VALID_FOOD_QUALITY = {
    "rating": "타베로그 3.50 (100)",
    "source": "Tabelog 2026-05-17",
    "source_fetched_at": "2026-05-17",
    "data_quality": "researched_market_rate",
}


class FoodQualityTests(unittest.TestCase):
    """검사 I: data/itinerary.json food_quality(식사 평점 출처) 무결성."""

    def _base(self, td, itin):
        return make_fixture(Path(td), cost=VALID_COST, index_html="<html></html>", itinerary=itin)

    def test_valid_food_quality_passes(self):
        itin = _itin([
            {"time": "12:00", "title": "점심", "maps_query": "A", "food_quality": VALID_FOOD_QUALITY},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertEqual(errs, [], errs)

    def test_absent_food_quality_ok(self):
        itin = _itin([
            {"time": "12:00", "title": "동네 끼니", "maps_query": "A"},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertEqual(errs, [], errs)

    def test_missing_source_fails(self):
        fq = dict(VALID_FOOD_QUALITY); del fq["source"]
        itin = _itin([
            {"time": "12:00", "title": "점심", "maps_query": "A", "food_quality": fq},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[I]") and "source" in e for e in errs), errs)

    def test_missing_rating_fails(self):
        fq = dict(VALID_FOOD_QUALITY); del fq["rating"]
        itin = _itin([
            {"time": "12:00", "title": "점심", "maps_query": "A", "food_quality": fq},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[I]") and "rating" in e for e in errs), errs)

    def test_invalid_data_quality_fails(self):
        fq = dict(VALID_FOOD_QUALITY); fq["data_quality"] = "guess"
        itin = _itin([
            {"time": "12:00", "title": "점심", "maps_query": "A", "food_quality": fq},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[I]") and "data_quality" in e for e in errs), errs)

    def test_stale_food_quality_fails(self):
        fq = dict(VALID_FOOD_QUALITY); fq["source_fetched_at"] = "2026-01-01"  # 136d
        itin = _itin([
            {"time": "12:00", "title": "점심", "maps_query": "A", "food_quality": fq},
        ])
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[I]") and "stale" in e for e in errs), errs)

    def test_route_candidate_food_quality_checked(self):
        fq = dict(VALID_FOOD_QUALITY); fq["data_quality"] = "guess"
        itin = _itin([{"time": "09:00", "title": "A", "maps_query": "A"}])
        itin["route_candidates"] = [{
            "id": "food_culture", "name": "미식형",
            "days": [{"date": "2026-05-31", "day_label": "D1", "walking_km": 1, "items": [
                {"time": "12:00", "title": "대안 점심", "maps_query": "A", "food_quality": fq},
            ]}],
        }]
        with tempfile.TemporaryDirectory() as td:
            base = self._base(td, itin)
            errs, _ = validate.run(base, date(2026, 5, 17))
            self.assertTrue(any(e.startswith("[I]") and "data_quality" in e for e in errs), errs)


class NoGithubLinkTests(unittest.TestCase):
    """검사 J: Vercel 산출물 HTML에 github.com 링크/URL이 없어야 함."""

    def test_clean_outputs_pass(self):
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html><a href='viz/archive.html'>아카이브</a></html>",
                vercel_html={"viz/checklist.html": "<html>리서치 상세: docs/booking-research-2026-05-24.md</html>"},
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertEqual([e for e in errs if e.startswith("[J]")], [], errs)

    def test_github_link_in_index_fails(self):
        html = '<html><a href="https://github.com/ywkim/japan-trip/blob/main/reports/final-report.md">보고서</a></html>'
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(Path(td), cost=VALID_COST, index_html=html)
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any(e.startswith("[J]") and "index.html" in e for e in errs), errs)

    def test_github_url_in_viz_output_fails(self):
        html = "<html>출처: https://github.com/ywkim/japan-trip/blob/main/docs/x.md</html>"
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                vercel_html={"viz/checklist.html": html},
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any(e.startswith("[J]") and "viz/checklist.html" in e for e in errs), errs)

    def test_github_in_new_viz_page_caught_by_glob(self):
        """검사 J는 viz/*.html 전체를 glob하므로 신규 문서 페이지도 자동 포함."""
        html = "<html>https://github.com/ywkim/japan-trip/blob/main/reports/final-report.md</html>"
        with tempfile.TemporaryDirectory() as td:
            base = make_fixture(
                Path(td),
                cost=VALID_COST,
                index_html="<html></html>",
                vercel_html={"viz/report.html": html},
            )
            errs, _ = validate.run(base, date(2026, 5, 12))
            self.assertTrue(any(e.startswith("[J]") and "viz/report.html" in e for e in errs), errs)


class ProductionDataTests(unittest.TestCase):
    """현재 레포 데이터가 validate를 통과하는지 회귀 검사."""

    @classmethod
    def setUpClass(cls):
        # 산출물(index.html 등)은 gitignore되어 fresh checkout에 없을 수 있다.
        # 검사 D가 index.html을 읽으므로, 없으면 빌드해 테스트를 자기완결화한다.
        base = Path(__file__).resolve().parent.parent
        if not (base / "index.html").exists():
            subprocess.run(
                [sys.executable, str(base / "scripts" / "build_index.py")],
                cwd=base, check=True, capture_output=True,
            )

    def test_repo_data_validates(self):
        base = Path(__file__).resolve().parent.parent
        errs, _ = validate.run(base, date(2026, 5, 12))
        self.assertEqual(errs, [], f"production data validation failed: {errs}")


if __name__ == "__main__":
    unittest.main()
