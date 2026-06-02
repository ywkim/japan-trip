#!/usr/bin/env python3
"""외부 일정 이미지(장소 사진·블로그 썸네일)를 레포에 자가호스팅으로 내려받는다.

비행기 모드 완전 오프라인 보장(PR #80 후속): 외부 호스트(위키미디어·네이버
pstatic·타베로그)는 핫링크 보호(referer 검사)로 서비스 워커 사전 캐시가 막혀
오프라인에서 깨졌다. 이 스크립트는 referer 없이(=`<img referrerpolicy=no-referrer>`
와 동일) 이미지를 받아 `assets/place-images/<hash>.<ext>`로 저장하고, URL→로컬
경로 매핑을 `data/local-image-map.json`에 기록한다. 이미지·매핑을 커밋하면
build_index.py가 빌드 시 외부 URL을 로컬 경로로 치환한다(빌드는 네트워크 비의존·결정론).

용법:
  uv run python scripts/fetch_assets.py          # 전 이미지 내려받기 + 매핑 갱신
  uv run python scripts/fetch_assets.py --check   # 누락(미다운로드) URL만 보고, 쓰기 없음

근거: docs/decision-log/2026-05-31-02-offline-image-selfhosting.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
IMG_DIR = BASE / "assets" / "place-images"
MAP_PATH = DATA / "local-image-map.json"
ITINERARY = DATA / "itinerary.json"

EXT_BY_CT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
UA = "Mozilla/5.0 (japan-trip-offline asset fetcher)"


_MD_IMG_RE = re.compile(r'!\[[^\]]*\]\((https?://[^)]+)\)')


def collect_urls() -> list:
    """itinerary.json의 모든 외부 이미지 URL(image_url + blog_reviews[].img). 순서 보존·중복 제거."""
    d = json.loads(ITINERARY.read_text(encoding="utf-8"))
    seen, out = set(), []

    def add(u):
        if isinstance(u, str) and u.startswith("http") and u not in seen:
            seen.add(u)
            out.append(u)

    days = list(d.get("days", []))
    for rc in d.get("route_candidates", []):
        if isinstance(rc, dict):
            days.extend(rc.get("days", []))
    for day in days:
        for it in day.get("items", []):
            add(it.get("image_url"))
            for r in it.get("blog_reviews", []) or []:
                add(r.get("img"))
    return out


def collect_doc_urls() -> list:
    """docs/*.md의 마크다운 이미지 URL(외부만). 순서 보존·중복 제거."""
    seen, out = set(), []
    for f in sorted((DATA.parent / "docs").glob("*.md")):
        for url in _MD_IMG_RE.findall(f.read_text(encoding="utf-8")):
            if url not in seen:
                seen.add(url)
                out.append(url)
    return out


def local_name(url: str, content_type: str | None) -> str:
    """URL 해시 기반 결정론적 파일명. 확장자는 content-type 우선, 없으면 경로 확장자."""
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    ext = EXT_BY_CT.get((content_type or "").split(";")[0].strip().lower())
    if not ext:
        path_ext = Path(urlparse(url).path).suffix.lower()
        ext = path_ext if path_ext in (".jpg", ".jpeg", ".png", ".webp", ".gif") else ".jpg"
    return f"{h}{ext}"


def download(url: str, ctx) -> tuple[bytes, str | None]:
    # 위키미디어 원본은 거대할 수 있어 폭 1280으로 캡(맵 키는 원본 URL 유지).
    fetch_url = url
    if "commons.wikimedia.org" in urlparse(url).netloc and "width=" not in url:
        fetch_url += ("&" if "?" in url else "?") + "width=1280"
    req = urllib.request.Request(fetch_url, headers={"User-Agent": UA})  # Referer 없음
    # 429(rate limit)는 백오프 재시도 — 위키미디어가 부하 시 자주 반환.
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                return r.read(), r.headers.get("Content-Type")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="미다운로드 URL만 보고(쓰기 없음)")
    args = ap.parse_args()

    itinerary_urls = collect_urls()
    doc_urls = [u for u in collect_doc_urls() if u not in set(itinerary_urls)]
    urls = itinerary_urls + doc_urls
    existing = json.loads(MAP_PATH.read_text(encoding="utf-8")) if MAP_PATH.exists() else {}

    if args.check:
        missing = [u for u in urls if u not in existing or not (BASE / existing[u].lstrip("/")).exists()]
        for u in missing:
            print(f"MISSING {u}")
        print(f"{len(urls) - len(missing)}/{len(urls)} cached locally, {len(missing)} missing.")
        return 1 if missing else 0

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    ctx = ssl.create_default_context()
    # 이미 받아 둔(파일 존재) 항목은 보존 — 재실행은 누락분만 받는다(429·일시 실패에 강건).
    mapping: dict[str, str] = {
        u: p for u, p in existing.items() if u in set(urls) and (BASE / p.lstrip("/")).exists()
    }
    ok = skip = fail = 0
    for u in urls:
        if u in mapping:
            skip += 1
            continue
        try:
            data, ct = download(u, ctx)
            name = local_name(u, ct)
            (IMG_DIR / name).write_bytes(data)
            mapping[u] = f"/assets/place-images/{name}"
            ok += 1
            print(f"OK   {name}  ({len(data):,}B)  {u[:70]}")
        except Exception as e:  # 실패한 URL은 외부 유지(SW best-effort + no-referrer가 처리)
            fail += 1
            print(f"FAIL {type(e).__name__}: {e}  {u[:70]}", file=sys.stderr)

    # 결정론: url 정렬해 기록
    MAP_PATH.write_text(
        json.dumps({k: mapping[k] for k in sorted(mapping)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {MAP_PATH.relative_to(BASE)}: {ok} new, {skip} cached, {fail} kept external.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
