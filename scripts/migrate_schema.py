#!/usr/bin/env python3
"""Migration script for Work 4 schema redesign.

Converts itinerary.json days[] and route_candidates[] from flat string schema
to structured schema (title→object, arrive_from→steps array, etc).

Usage:
  python scripts/migrate_schema.py --day 2026-05-31  # Migrate specific day
  python scripts/migrate_schema.py --all             # Migrate all days
  python scripts/migrate_schema.py --candidate 0     # Migrate route_candidate
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
ITINERARY_FILE = DATA / "itinerary.json"


def is_new_schema_title(title) -> bool:
    """Check if title is already in new schema (dict with type/ko_name/ja_name)."""
    return isinstance(title, dict) and "ko_name" in title


def is_new_schema_arrive_from(af) -> bool:
    """Check if arrive_from is already in new schema (has 'steps' array)."""
    return isinstance(af, dict) and isinstance(af.get("steps"), list)


def migrate_title(title_str: str) -> dict:
    """Convert title string to new schema object.

    Current examples:
    - "아침식사 (집에서 간단히)"
    - "킨카쿠지/금각사 (金閣寺)"
    - "폰토초 저녁 (만자라테이·まんざら亭)"

    Strategy: Try to extract ko_name and ja_name from parentheses.
    """
    if not isinstance(title_str, str):
        return {"type": "unknown", "ko_name": str(title_str), "ja_name": "", "ja_reading_ko": "", "en_name": ""}

    title_str = title_str.strip()

    # Try to extract kanji from last parentheses
    kanji_match = re.search(r'（([^）]+)）|（([^）]+)）|\(([^)]+)\)$', title_str)
    ja_name = ""
    ja_reading_ko = ""
    ko_name = title_str

    if kanji_match:
        kanji_str = kanji_match.group(1) or kanji_match.group(2) or kanji_match.group(3)
        # Remove kanji from ko_name for cleaner display
        ko_name = title_str[:kanji_match.start()].strip()

        # If kanji has hiragana/katakana mixed, try to split
        # For now, treat entire content as ja_name
        if kanji_str:
            ja_name = kanji_str

    # Try to extract reading from slash notation (e.g., "킨카쿠지/금각사" → reading=킨카쿠지)
    slash_match = re.match(r'([^\s/]+)/(.+?)(?:\s|$)', title_str)
    if slash_match:
        ja_reading_ko = slash_match.group(1)
        ko_name = slash_match.group(2).split('(')[0].strip()

    # Determine type
    type_ = "place"  # default
    if any(x in title_str for x in ["저녁", "점심", "조식", "카페", "식사", "라멘", "코지"]):
        type_ = "restaurant"
    elif any(x in title_str for x in ["사찰", "신사", "절", "寺", "궁"]):
        type_ = "place"
    elif any(x in title_str for x in ["체크인", "숙박", "야숙"]):
        type_ = "lodging"
    else:
        type_ = "place"

    return {
        "type": type_,
        "ko_name": ko_name,
        "ja_name": ja_name,
        "ja_reading_ko": ja_reading_ko,
        "en_name": "",
    }


def migrate_arrive_from(af_dict: dict) -> dict:
    """Convert arrive_from from single route string to steps array.

    Current schema:
    {
      "mode": "bus",
      "duration_min": 18,
      "distance_km": 3.0,
      "route": "텐류지(天龍寺)/아라시야마(嵐山) → 교토버스(京都バス) 73계통 '코케데라·스즈무시데라(苔寺・鈴虫寺)' 정류장 → 도보 3분",
      "source": "...",
      "source_fetched_at": "2026-05-26",
      "data_quality": "tbd_needs_browser_mcp",
      "maps_url": "..."
    }

    New schema:
    {
      "steps": [
        {
          "mode": "bus",
          "operator": {"ko": "교토버스", "ja": "京都バス", "type": "kyoto_bus"},
          "number": "73",
          "from": {"ko": "...", "ja": "..."},
          "to": {"ko": "...", "ja": "..."},
          "duration_min": 18,
          "fare_jpy": null,
          "distance_km": 3.0
        }
      ],
      "source": "...",
      "source_fetched_at": "2026-05-26",
      "data_quality": "tbd_needs_browser_mcp",
      "maps_url": "..."
    }
    """
    if not af_dict:
        return None

    # If already new schema, return as-is
    if isinstance(af_dict.get("steps"), list):
        return af_dict

    mode = af_dict.get("mode", "walk")
    duration = af_dict.get("duration_min")
    distance = af_dict.get("distance_km")
    route = af_dict.get("route", "")

    # Create a single step based on mode
    step = {
        "mode": mode,
        "duration_min": duration,
        "distance_km": distance,
    }

    # Try to extract bus operator and number from route or mode context
    if mode == "bus":
        # Extract operator and number from route text
        operator = None
        operator_type = None
        number = None

        if "시버스" in route or "市バス" in route:
            operator = {"ko": "시버스", "ja": "市バス"}
            operator_type = "shibus"
        elif "교토버스" in route or "京都バス" in route:
            operator = {"ko": "교토버스", "ja": "京都バス"}
            operator_type = "kyoto_bus"

        if operator:
            # Try to extract bus number (looks for digits after "계통" or "号線")
            num_match = re.search(r'(\d+)\s*(?:계통|号線)', route)
            if num_match:
                number = num_match.group(1)

            step["operator"] = {**operator, "type": operator_type}
            if number:
                step["number"] = number

        # Try to extract from/to station names
        arrow_match = re.search(r'(\S+)\s*→\s*(\S+)', route)
        if arrow_match:
            # Rough extraction - in real migration, would parse more carefully
            from_name = arrow_match.group(1).split('(')[0].strip()
            to_name = arrow_match.group(2).split('(')[0].strip()
            step["from"] = {"ko": from_name, "ja": ""}
            step["to"] = {"ko": to_name, "ja": ""}

    # Create new arrive_from structure
    return {
        "steps": [step],
        "source": af_dict.get("source"),
        "source_fetched_at": af_dict.get("source_fetched_at"),
        "data_quality": af_dict.get("data_quality"),
        "maps_url": af_dict.get("maps_url"),
    }


def migrate_item(item: dict) -> dict:
    """Migrate a single itinerary item to new schema."""
    if not item:
        return item

    item = copy.deepcopy(item)

    # Migrate title if it's still a string
    if "title" in item and isinstance(item["title"], str):
        item["title"] = migrate_title(item["title"])

    # Migrate arrive_from if present
    if "arrive_from" in item:
        item["arrive_from"] = migrate_arrive_from(item["arrive_from"])

    # For now, keep food_quality and other fields as-is
    # In later phases, will migrate food_quality to ratings array

    return item


def migrate_day(day: dict) -> dict:
    """Migrate a single day's items."""
    day = copy.deepcopy(day)

    if "items" in day:
        day["items"] = [migrate_item(item) for item in day["items"]]

    return day


def migrate_itinerary(itin: dict, day_date: str = None, candidate_idx: int = None) -> dict:
    """
    Migrate itinerary.json.

    Args:
        itin: itinerary dict
        day_date: if provided, only migrate this specific day (e.g., "2026-05-31")
        candidate_idx: if provided (0-based), only migrate this route_candidate
    """
    itin = copy.deepcopy(itin)

    # Migrate days
    if "days" in itin:
        if day_date:
            # Only migrate specific day
            for i, day in enumerate(itin["days"]):
                if day.get("date") == day_date:
                    itin["days"][i] = migrate_day(day)
                    print(f"✓ Migrated day: {day_date}")
        else:
            # Migrate all days
            itin["days"] = [migrate_day(day) for day in itin["days"]]
            print(f"✓ Migrated {len(itin['days'])} days")

    # Migrate route_candidates
    if "route_candidates" in itin:
        if candidate_idx is not None:
            # Only migrate specific candidate
            if 0 <= candidate_idx < len(itin["route_candidates"]):
                cand = itin["route_candidates"][candidate_idx]
                if "days" in cand:
                    cand["days"] = [migrate_day(day) for day in cand["days"]]
                print(f"✓ Migrated route_candidate {candidate_idx}: {cand.get('name')}")
        else:
            # Migrate all candidates
            for cand in itin["route_candidates"]:
                if "days" in cand:
                    cand["days"] = [migrate_day(day) for day in cand["days"]]
            print(f"✓ Migrated {len(itin['route_candidates'])} route_candidates")

    return itin


def main():
    parser = argparse.ArgumentParser(description="Migrate itinerary.json to new schema (Work 4)")
    parser.add_argument("--day", help="Migrate specific day (e.g., 2026-05-31)")
    parser.add_argument("--candidate", type=int, help="Migrate specific route_candidate (0-based index)")
    parser.add_argument("--all", action="store_true", help="Migrate all days and candidates")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")

    args = parser.parse_args()

    # Load current itinerary
    with open(ITINERARY_FILE, 'r', encoding='utf-8') as f:
        itin = json.load(f)

    # Determine migration scope
    if args.all:
        migrated = migrate_itinerary(itin)
    elif args.day:
        migrated = migrate_itinerary(itin, day_date=args.day)
    elif args.candidate is not None:
        migrated = migrate_itinerary(itin, candidate_idx=args.candidate)
    else:
        # Default: migrate first day (5/31) + first candidate
        migrated = migrate_itinerary(itin, day_date="2026-05-31", candidate_idx=0)

    if args.dry_run:
        print("\n[DRY RUN] Changes (not saved):")
        print(json.dumps(migrated, ensure_ascii=False, indent=2)[:500] + "...")
    else:
        # Create backup
        backup_file = ITINERARY_FILE.with_stem(ITINERARY_FILE.stem + "_backup")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(itin, f, ensure_ascii=False, indent=2)
        print(f"✓ Backup saved to: {backup_file}")

        # Write migrated data
        with open(ITINERARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(migrated, f, ensure_ascii=False, indent=2)
        print(f"✓ Migrated data written to: {ITINERARY_FILE}")


if __name__ == "__main__":
    main()
