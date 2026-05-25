"""design-tokens.json: 스키마·hex 포맷·레거시 팔레트 회귀 테스트."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TOKENS_PATH = BASE / "data" / "design-tokens.json"
DESIGN_MD = BASE / "DESIGN.md"

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
REQUIRED_TOP_KEYS = {
    "_doc",
    "version",
    "theme_name",
    "color",
    "typography",
    "spacing_rem",
    "radius_px",
    "elevation",
    "breakpoint_px",
}
REQUIRED_COLOR_KEYS = {
    "bg",
    "surface",
    "surface_sunken",
    "ink",
    "ink_muted",
    "border",
    "accent",
    "accent_soft",
    "ok",
    "warn",
    "danger",
    "table_stripe",
    "bar_track",
}
LEGACY_HEXES = {"#d33", "#ff6464", "#fafafa", "#c33", "#c80", "#2a7"}


class DesignTokensTests(unittest.TestCase):
    def setUp(self):
        self.tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))

    def test_top_level_keys_present(self):
        missing = REQUIRED_TOP_KEYS - set(self.tokens)
        self.assertFalse(missing, f"missing top-level keys: {missing}")

    def test_color_variants_have_identical_keys(self):
        light = set(self.tokens["color"]["light"])
        dark = set(self.tokens["color"]["dark"])
        self.assertEqual(light, dark, "light·dark color key sets must match")
        missing = REQUIRED_COLOR_KEYS - light
        self.assertFalse(missing, f"required color keys missing: {missing}")

    def test_every_color_is_valid_hex(self):
        for variant in ("light", "dark"):
            for key, value in self.tokens["color"][variant].items():
                self.assertRegex(
                    value, HEX_RE, f"color.{variant}.{key} = {value!r} not a 6-digit hex"
                )

    def test_no_legacy_palette_in_tokens(self):
        flat = []
        for variant in ("light", "dark"):
            flat.extend(v.lower() for v in self.tokens["color"][variant].values())
        for legacy in LEGACY_HEXES:
            self.assertNotIn(
                legacy, flat, f"legacy color {legacy} reintroduced in tokens"
            )

    def test_design_md_quotes_theme_name_and_version(self):
        md = DESIGN_MD.read_text(encoding="utf-8")
        self.assertIn(self.tokens["theme_name"], md, "theme_name not quoted in DESIGN.md")
        self.assertIn(self.tokens["version"], md, "version not quoted in DESIGN.md")

    def test_typography_scale_monotonic(self):
        scale = self.tokens["typography"]["scale_rem"]
        ordered = [scale[k] for k in ("xs", "sm", "base", "md", "lg", "xl")]
        self.assertEqual(
            ordered, sorted(ordered), f"typography scale not monotonic: {ordered}"
        )


if __name__ == "__main__":
    unittest.main()
