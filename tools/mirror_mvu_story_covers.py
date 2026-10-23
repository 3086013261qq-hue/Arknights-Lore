#!/usr/bin/env python3
"""Safely mirror Arknights MVU story covers from PRTS into this repository.

Default mode is dry-run. Use --apply to download/convert files.
The script never edits timeline content and never guesses an ambiguous PRTS file.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest/mvu-story-media.v1.json"
REPORT = ROOT / "QA/mvu-story-media-mirror-report.json"
API = "https://prts.wiki/api.php"
UA = "Arknights-Lore-MVU-Mirror/1.0 (+https://github.com/3086013261qq-hue/Arknights-Lore)"


def request_json(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def resolve_file(file_name: str) -> dict | None:
    data = request_json({
        "action": "query", "format": "json", "prop": "imageinfo",
        "iiprop": "url|size|mime", "titles": "File:" + file_name,
    })
    for page in data.get("query", {}).get("pages", {}).values():
        if "missing" in page:
            continue
        ii = (page.get("imageinfo") or [None])[0]
        if ii and ii.get("url"):
            return {"title": page.get("title"), **ii}
    return None


def search_file(title: str) -> list[str]:
    data = request_json({
        "action": "query", "format": "json", "list": "search", "srnamespace": 6,
        "srlimit": 30, "srsearch": title,
    })
    return [x["title"].removeprefix("File:") for x in data.get("query", {}).get("search", [])]


def resolve_side(title: str) -> tuple[dict | None, str]:
    # Known PRTS naming conventions first; no network-wide fuzzy choice if one resolves.
    candidates = [
        f"活动图标_{title}.png", f"活动名称_{title}.png",
        f"活动图标_{title}.webp", f"活动名称_{title}.webp",
    ]
    hits = []
    for name in candidates:
        info = resolve_file(name)
        if info:
            hits.append((name, info))
    if len(hits) == 1:
        return hits[0][1], hits[0][0]
    if len(hits) > 1:
        return None, "ambiguous-exact:" + "|".join(x[0] for x in hits)

    found = search_file(title)
    preferred = [n for n in found if title in n and ("活动图标" in n or "活动名称" in n)]
    if len(preferred) != 1:
        return None, "ambiguous-search:" + "|".join(preferred[:10])
    info = resolve_file(preferred[0])
    return (info, preferred[0]) if info else (None, "unresolved:" + preferred[0])


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()


def to_webp(raw: bytes, out: Path) -> dict:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow is required: pip install pillow") from exc
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        w, h = im.size
        if max(w, h) > 1600:
            im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, "WEBP", quality=88, method=6)
        fw, fh = im.size
    data = out.read_bytes()
    return {"width": fw, "height": fh, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually download and write WebP files")
    ap.add_argument("--only", choices=["main", "side", "all"], default="all")
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    report = {"schema_version": "mvu-story-media-mirror-report-v1", "apply": args.apply, "items": []}

    jobs = []
    if args.only in ("main", "all"):
        for ident, chapter, title, prts_file in manifest["main"]:
            jobs.append((ident, "main", title, f"media/mvu/story/main/main-{ident[-2:]}.webp", prts_file))
    if args.only in ("side", "all"):
        for ident, slug, title in manifest["side"]:
            jobs.append((ident, "side", title, f"media/mvu/story/side/{slug}.webp", None))

    for ident, group, title, target, exact_file in jobs:
        try:
            if exact_file:
                info = resolve_file(exact_file)
                source_name = exact_file
                reason = "exact-main"
            else:
                info, source_name = resolve_side(title)
                reason = "side-resolve"
            item = {"id": ident, "group": group, "title": title, "target": target, "source_file": source_name}
            if not info:
                item.update(status="unresolved", reason=source_name)
                report["items"].append(item)
                print("UNRESOLVED", ident, source_name)
                continue
            item["source_url"] = info["url"]
            item["source_mime"] = info.get("mime")
            if not args.apply:
                item["status"] = "resolved-dry-run"
                report["items"].append(item)
                print("RESOLVED", ident, source_name)
                continue
            raw = download(info["url"])
            meta = to_webp(raw, ROOT / target)
            item.update(status="ready-local-webp", **meta)
            report["items"].append(item)
            print("READY", ident, target)
        except Exception as exc:
            report["items"].append({"id": ident, "group": group, "title": title, "target": target, "status": "error", "error": repr(exc)})
            print("ERROR", ident, exc, file=sys.stderr)

    counts = {}
    for item in report["items"]:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    report["summary"] = {"total": len(report["items"]), **counts}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("REPORT", REPORT.relative_to(ROOT), report["summary"])
    return 1 if counts.get("error") or counts.get("unresolved") else 0


if __name__ == "__main__":
    raise SystemExit(main())
