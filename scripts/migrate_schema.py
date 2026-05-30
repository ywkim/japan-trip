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

    Handles patterns:
    - "조식 — 마치야 또는 코메다" → ko_name only
    - "치쿠린/죽림길 (竹林の小径)" → ko_name="죽림길", ja_reading_ko="치쿠린", ja_name="竹林の小径"
    - "폰토초 저녁 (만자라테이·まんざら亭)" → ko_name="폰토초 저녁", ja_name="まんざら亭"
    - "MACCHA HOUSE (말차 티라미수)" → en_name="MACCHA HOUSE", ko_name="말차 티라미수"
    - "텐류지 (天龍寺)" → ko_name="텐류지", ja_name="天龍寺"
    """
    if not isinstance(title_str, str):
        return {"type": "unknown", "ko_name": str(title_str), "ja_name": "", "ja_reading_ko": "", "en_name": ""}

    title_str = title_str.strip()
    ko_name = title_str
    ja_name = ""
    ja_reading_ko = ""
    en_name = ""

    # Extract content from parentheses (last match)
    paren_match = re.search(r'\(([^)]+)\)(?!.*\()', title_str)
    paren_content = None
    if paren_match:
        paren_content = paren_match.group(1)
        ko_name = title_str[:paren_match.start()].strip()

        # Classify paren_content: kanji/kana or korean/english
        has_kanji = any('一' <= c <= '鿿' for c in paren_content)
        has_kana = any('぀' <= c <= 'ゟ' or '゠' <= c <= 'ヿ' for c in paren_content)
        has_english = any(c.isascii() and c.isalpha() for c in paren_content)
        has_korean = any('가' <= c <= '힣' for c in paren_content)

        # Prioritize: kanji > kana > korean > english
        if has_kanji or has_kana:
            ja_name = paren_content
        elif has_english and has_korean:
            # Mixed: en_name and ko_name adjustment
            # Pattern: "MACCHA HOUSE (말차 티라미수)" → en_name="MACCHA HOUSE", ko_name="말차 티라미수"
            parts = paren_content.split()
            ko_part = [p for p in parts if any('가' <= c <= '힣' for c in p)]
            en_part = [p for p in parts if any(c.isascii() and c.isalpha() for c in p)]
            if en_part:
                en_name = ' '.join(en_part)
            if ko_part:
                ko_name = ' '.join(ko_part)
        elif has_korean:
            # Pure korean in parens — typically alternative reading, update ko_name
            ko_name = paren_content
        elif has_english:
            en_name = paren_content

    # Extract ja_reading_ko from slash notation before parentheses
    # E.g., "치쿠린/죽림길 (竹林の小径)" → reading="치쿠린", ko_name="죽림길"
    slash_match = re.match(r'([^\s/]+)/(.+?)(?:\s|\(|$)', title_str)
    if slash_match and '/' in title_str:
        potential_reading = slash_match.group(1)
        # Check if first part looks like a reading (katakana/korean)
        is_reading = any('぀' <= c <= 'ゟ' or '가' <= c <= '힣' for c in potential_reading)
        if is_reading:
            ja_reading_ko = potential_reading
            # Update ko_name if we found a reading
            second_part = slash_match.group(2).strip()
            if paren_match:
                # Extract text before parens from second_part
                ko_name = re.match(r'([^(]+)', second_part).group(1).strip() if second_part else ko_name
            else:
                ko_name = second_part.split('(')[0].strip()

    # Type inference
    type_ = "place"
    if any(x in title_str for x in ["저녁", "점심", "조식", "카페", "음식", "라멘", "코지", "식사", "다이호", "뎅"]):
        type_ = "restaurant"
    elif any(x in title_str for x in ["사찰", "신사", "절", "寺", "궁", "신사", "데라", "당고"]):
        type_ = "place"
    elif any(x in title_str for x in ["체크인", "숙박", "야숙", "료칸", "마치야", "보관", "대욕장", "위탁", "가이세키"]):
        type_ = "lodging"
    else:
        type_ = "place"

    return {
        "type": type_,
        "ko_name": ko_name or title_str,
        "ja_name": ja_name,
        "ja_reading_ko": ja_reading_ko,
        "en_name": en_name,
    }


def extract_station_from_text(text: str) -> tuple:
    """Extract station name from text like '니조역(二条駅)' → ('니조역', '二条駅')."""
    match = re.search(r'([^\(\)]+)\(([^\(\)]+)\)', text)
    if match:
        return (match.group(1).strip(), match.group(2).strip())
    return (text.strip(), "")


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
    fare_jpy = None

    # Extract fare from route (e.g., "¥200" or "¥230")
    fare_match = re.search(r'¥(\d+)', route)
    if fare_match:
        fare_jpy = int(fare_match.group(1))

    # Create a single step based on mode
    step = {
        "mode": mode,
        "duration_min": duration,
        "distance_km": distance,
    }
    if fare_jpy is not None:
        step["fare_jpy"] = fare_jpy

    # Handle different modes
    if mode == "bus":
        # Extract operator and number from route
        operator = None
        operator_type = None
        numbers = []

        if "시버스" in route or "市バス" in route:
            operator = {"ko": "시버스", "ja": "市バス", "type": "shibus"}
        elif "교토버스" in route or "京都バス" in route:
            operator = {"ko": "교토버스", "ja": "京都バス", "type": "kyoto_bus"}

        if operator:
            step["operator"] = operator

            # Extract all bus numbers (handles transfers like "11번 ... 59번")
            num_matches = re.findall(r'(\d+)\s*(?:번|計|계통|号線)', route)
            if num_matches:
                numbers = num_matches
                step["number"] = numbers[0]

        # Extract from/to station names using arrow
        arrows = list(re.finditer(r'([^\(→]*(?:\([^\)]*\))?[^\(→]*)\s*→\s*([^\(→]*(?:\([^\)]*\))?[^\(→]*)', route))
        if arrows:
            from_text = arrows[0].group(1).strip()
            to_text = arrows[0].group(2).strip()

            # Clean up extracted text
            from_text = re.sub(r'^.*?([^\s\(]+(?:\([^\)]*\))?)\s*$', r'\1', from_text).strip()
            to_text = re.sub(r'^.*?([^\s\(]+(?:\([^\)]*\))?)\s*$', r'\1', to_text).strip()

            from_ko, from_ja = extract_station_from_text(from_text)
            to_ko, to_ja = extract_station_from_text(to_text)

            step["from"] = {"ko": from_ko, "ja": from_ja}
            step["to"] = {"ko": to_ko, "ja": to_ja}

    elif mode == "jr":
        # JR routes: "JR 산인본선(嵯峨野線) 니조역(二条駅)→사가아라시야마역(嵯峨嵐山駅)"
        line_match = re.search(r'JR\s+([^→]+?)(?:\s+|$)', route)
        if line_match:
            line_info = line_match.group(1).strip()
            step["line"] = line_info

        # Extract stations
        arrow_match = re.search(r'([^\(→]+(?:\([^\)]*\))?)\s*→\s*([^\(→]+(?:\([^\)]*\))?)', route)
        if arrow_match:
            from_ko, from_ja = extract_station_from_text(arrow_match.group(1).strip())
            to_ko, to_ja = extract_station_from_text(arrow_match.group(2).strip())

            step["from"] = {"ko": from_ko, "ja": from_ja}
            step["to"] = {"ko": to_ko, "ja": to_ja}

    elif mode == "airport_express":
        if "하루카" in route or "ハルカ" in route:
            step["operator"] = {"ko": "JR 하루카", "ja": "JR ハルカ"}

    # Create new arrive_from structure (preserve route for warning extraction in rendering)
    return {
        "steps": [step],
        "route": route,  # Keep original for rendering warnings/alternatives
        "source": af_dict.get("source"),
        "source_fetched_at": af_dict.get("source_fetched_at"),
        "data_quality": af_dict.get("data_quality"),
        "maps_url": af_dict.get("maps_url"),
    }


def expand_food_quality(food_quality: dict, item_title: str = "") -> dict:
    """Expand food_quality with place_info, business_hours, ratings if not already present."""
    if not food_quality or not isinstance(food_quality, dict):
        return food_quality

    # Initialize new fields if they don't exist
    if "place_info" not in food_quality:
        food_quality["place_info"] = {}
    if "business_hours" not in food_quality:
        food_quality["business_hours"] = []
    if "ratings" not in food_quality:
        food_quality["ratings"] = []
        # Try to extract rating from 'rating' field
        if "rating" in food_quality:
            rating_text = food_quality["rating"]
            # Parse "타베로그 3.76 · 미쉐린 빕구르망 2024" into structured format
            if "타베로그" in rating_text or "tabelog" in rating_text.lower():
                score_match = re.search(r'(\d+\.\d+)', rating_text)
                if score_match:
                    food_quality["ratings"].append({
                        "source": "tabelog",
                        "score": float(score_match.group(1))
                    })
            if "미쉐린" in rating_text or "michelin" in rating_text.lower():
                if "빕구르망" in rating_text or "bib" in rating_text.lower():
                    food_quality["ratings"].append({
                        "source": "michelin",
                        "badge": "bib-gourmand"
                    })

    return food_quality


def migrate_item(item: dict, expand_food_quality_fields: bool = False) -> dict:
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

    # Optionally expand food_quality
    if expand_food_quality_fields and "food_quality" in item:
        item_title_str = item.get("title", {}).get("ko_name", "") if isinstance(item.get("title"), dict) else str(item.get("title", ""))
        item["food_quality"] = expand_food_quality(item["food_quality"], item_title_str)

    return item


def migrate_day(day: dict, expand_food_quality_fields: bool = False) -> dict:
    """Migrate a single day's items."""
    day = copy.deepcopy(day)

    if "items" in day:
        day["items"] = [migrate_item(item, expand_food_quality_fields) for item in day["items"]]

    return day


def migrate_itinerary(itin: dict, day_date: str = None, candidate_idx: int = None, expand_food_quality_fields: bool = False) -> dict:
    """
    Migrate itinerary.json.

    Args:
        itin: itinerary dict
        day_date: if provided, only migrate this specific day (e.g., "2026-05-31")
        candidate_idx: if provided (0-based), only migrate this route_candidate
        expand_food_quality_fields: if True, add place_info, business_hours, ratings to food_quality
    """
    itin = copy.deepcopy(itin)

    # Migrate days
    if "days" in itin:
        if day_date:
            # Only migrate specific day
            for i, day in enumerate(itin["days"]):
                if day.get("date") == day_date:
                    itin["days"][i] = migrate_day(day, expand_food_quality_fields)
                    print(f"✓ Migrated day: {day_date}")
        else:
            # Migrate all days
            itin["days"] = [migrate_day(day, expand_food_quality_fields) for day in itin["days"]]
            print(f"✓ Migrated {len(itin['days'])} days")

    # Migrate route_candidates
    if "route_candidates" in itin:
        if candidate_idx is not None:
            # Only migrate specific candidate
            if 0 <= candidate_idx < len(itin["route_candidates"]):
                cand = itin["route_candidates"][candidate_idx]
                if "days" in cand:
                    cand["days"] = [migrate_day(day, expand_food_quality_fields) for day in cand["days"]]
                print(f"✓ Migrated route_candidate {candidate_idx}: {cand.get('name')}")
        else:
            # Migrate all candidates
            for cand in itin["route_candidates"]:
                if "days" in cand:
                    cand["days"] = [migrate_day(day, expand_food_quality_fields) for day in cand["days"]]
            print(f"✓ Migrated {len(itin['route_candidates'])} route_candidates")

    return itin


def main():
    parser = argparse.ArgumentParser(description="Migrate itinerary.json to new schema (Work 4)")
    parser.add_argument("--day", help="Migrate specific day (e.g., 2026-05-31)")
    parser.add_argument("--candidate", type=int, help="Migrate specific route_candidate (0-based index)")
    parser.add_argument("--all", action="store_true", help="Migrate all days and candidates")
    parser.add_argument("--candidates", action="store_true", help="Migrate all route_candidates (alias for --all)")
    parser.add_argument("--with-food-quality", action="store_true", help="Expand food_quality with place_info, business_hours, ratings")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")

    args = parser.parse_args()

    # Load current itinerary
    with open(ITINERARY_FILE, 'r', encoding='utf-8') as f:
        itin = json.load(f)

    # Determine migration scope
    all_mode = args.all or args.candidates
    if all_mode:
        migrated = migrate_itinerary(itin, expand_food_quality_fields=args.with_food_quality)
    elif args.day:
        migrated = migrate_itinerary(itin, day_date=args.day, expand_food_quality_fields=args.with_food_quality)
    elif args.candidate is not None:
        migrated = migrate_itinerary(itin, candidate_idx=args.candidate, expand_food_quality_fields=args.with_food_quality)
    else:
        # Default: migrate first day (5/31) + first candidate
        migrated = migrate_itinerary(itin, day_date="2026-05-31", candidate_idx=0, expand_food_quality_fields=args.with_food_quality)

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
