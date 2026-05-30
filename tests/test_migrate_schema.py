"""migrate_schema.py: 레거시 arrive_from → steps 변환 단위 테스트 (Work 4.1).

핵심 회귀 가드: from/to는 마이그레이션에서 **생성하지 않는다**. 과거 정규식 파서가
요금·노선번호·조사를 장소로 오인해 데이터를 오염시킨 사건의 재발 방지.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import migrate_schema  # noqa: E402


class MigrateArriveFromTests(unittest.TestCase):
    def test_bus_extracts_operator_and_number_but_no_fromto(self):
        legacy = {
            "mode": "bus", "duration_min": 4, "distance_km": 1.6,
            "route": "시버스(市バス) 59번 금각사도(金閣寺道)→료안지마에(竜安寺前). 약 4분, ¥230",
            "source": "https://example.com", "source_fetched_at": "2026-05-17",
            "data_quality": "researched_market_rate",
        }
        out = migrate_schema.migrate_arrive_from(legacy)
        step = out["steps"][0]
        self.assertEqual(step["operator"]["type"], "shibus")
        self.assertEqual(step["number"], "59")
        self.assertEqual(step["fare_jpy"], 230)
        # from/to는 생성하지 않는다 (수기 ref 작성 대상)
        self.assertNotIn("from", step)
        self.assertNotIn("to", step)

    def test_jr_extracts_line_but_no_fromto(self):
        legacy = {
            "mode": "jr", "duration_min": 12, "distance_km": 8.5,
            "route": "JR 산인본선(嵯峨野線) 니조역(二条駅)→사가아라시야마역(嵯峨嵐山駅). 약 12분, ¥200",
            "source": "https://example.com", "source_fetched_at": "2026-05-17",
            "data_quality": "researched_market_rate",
        }
        out = migrate_schema.migrate_arrive_from(legacy)
        step = out["steps"][0]
        self.assertIn("산인본선", step.get("line", ""))
        self.assertNotIn("from", step)
        self.assertNotIn("to", step)

    def test_route_field_not_carried_over(self):
        legacy = {
            "mode": "bus", "duration_min": 4, "route": "市バス 59",
            "source": "x", "source_fetched_at": "2026-05-17", "data_quality": "researched_market_rate",
        }
        out = migrate_schema.migrate_arrive_from(legacy)
        self.assertNotIn("route", out)

    def test_already_new_schema_is_passthrough(self):
        new = {"steps": [{"mode": "jr", "from": "{{nijo_station}}", "to": "{{kyoto_station}}"}]}
        self.assertIs(migrate_schema.migrate_arrive_from(new), new)

    def test_extract_station_helper_removed(self):
        # 오염 원천이던 헬퍼는 제거됐다.
        self.assertFalse(hasattr(migrate_schema, "extract_station_from_text"))


if __name__ == "__main__":
    unittest.main()
