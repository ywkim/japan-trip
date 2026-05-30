#!/usr/bin/env python3
"""출처(source) 인벤토리 — data/*.json의 근거 URL을 추출·분류한다.

근거 채널로 쓰이는 키(`source`·`source_url`·`url`)만 순회한다. 콘텐츠 이미지
(`image_url`·blog 썸네일 `img`)는 근거가 아니므로 제외한다.

각 항목을 두 그룹으로 분류한다.
  - url   : http(s) URL을 가진 항목 → Playwright MCP 도달성 검증 대상
  - text  : `source` 문자열에 URL이 없는 항목 → source_url 보완 후보

용법:
  python scripts/list_sources.py            # 사람용 표
  python scripts/list_sources.py --json     # JSON (검증 파이프라인용)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
DATA_FILES = (
    "itinerary.json",
    "booking-checklist.json",
    "cost-options.json",
    "flights.json",
    "weather.json",
)

URL_RE = re.compile(r"https?://[^\s)\"']+")
EVIDENCE_KEYS = {"source", "source_url", "url"}
SKIP_KEYS = {"image_url", "img", "image_credit"}


def walk(node, pointer: str, out: list):
    if isinstance(node, dict):
        for k, v in node.items():
            child = f"{pointer}/{k}"
            if k in SKIP_KEYS:
                continue
            if k in EVIDENCE_KEYS and isinstance(v, str):
                urls = URL_RE.findall(v)
                out.append({"pointer": child, "key": k, "value": v, "urls": urls})
            else:
                walk(v, child, out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{pointer}[{i}]", out)


def collect() -> dict:
    url_group, text_group = [], []
    for fname in DATA_FILES:
        path = DATA / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        entries: list = []
        walk(data, "", entries)
        for e in entries:
            e["file"] = fname
            if e["urls"]:
                for u in e["urls"]:
                    url_group.append({"file": fname, "pointer": e["pointer"], "url": u})
            elif e["key"] == "source":
                text_group.append({"file": fname, "pointer": e["pointer"], "value": e["value"]})
    # URL 중복 제거 (같은 URL이 여러 곳에서 쓰임).
    seen, unique_urls = set(), []
    for e in url_group:
        if e["url"] not in seen:
            seen.add(e["url"])
            unique_urls.append(e)
    return {"url_group": url_group, "unique_urls": unique_urls, "text_group": text_group}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = collect()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"=== URL group: {len(result['url_group'])} occurrences, "
          f"{len(result['unique_urls'])} unique ===")
    for e in result["unique_urls"]:
        print(f"  [{e['file']}] {e['url']}")
    print(f"\n=== Text-only source (URL 보완 후보): {len(result['text_group'])} ===")
    for e in result["text_group"]:
        v = e["value"]
        snippet = v if len(v) <= 70 else v[:67] + "..."
        print(f"  [{e['file']}] {e['pointer']}\n      {snippet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
