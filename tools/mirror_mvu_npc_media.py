#!/usr/bin/env python3
"""Mirror the 19 already-audited NPC story portraits from PRTS into the repo.

Source selection is frozen by manifest/npc-media.v1.json. This script MUST NOT
re-resolve or replace a selected portrait; it only validates the audited URL,
downloads it, converts it to WebP, records hashes and reports readiness.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest/npc-media.v1.json"
REPORT = ROOT / "QA/mvu-npc-media-mirror-report-v1.json"
UA = "Arknights-Lore-MVU-NPC-Mirror/1.0 (+https://github.com/3086013261qq-hue/Arknights-Lore)"
REFERER = "https://prts.wiki/w/%E5%89%A7%E6%83%85%E8%A7%92%E8%89%B2%E4%B8%80%E8%A7%88"
WORKERS = 6
TIMEOUT = 20


def download(url: str, retries: int = 2) -> bytes:
    host = (urllib.parse.urlparse(url).hostname or "").casefold()
    if host != "media.prts.wiki":
        raise ValueError(f"refusing non-PRTS media host: {host}")
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": REFERER})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = r.read()
                if not data:
                    raise ValueError("empty response")
                return data
        except Exception as exc:
            last = exc
            if attempt < retries:
                time.sleep(1 + attempt)
    raise last


def to_webp(raw: bytes, out: Path) -> dict:
    from PIL import Image

    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        original = im.size
        if max(im.size) > 1800:
            im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, "WEBP", quality=90, method=6)
        final = im.size
        mode = im.mode

    data = out.read_bytes()
    return {
        "original_width": original[0],
        "original_height": original[1],
        "width": final[0],
        "height": final[1],
        "mode": mode,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def inspect_existing(path: Path) -> dict | None:
    if not path.is_file() or path.stat().st_size <= 0:
        return None
    from PIL import Image

    try:
        with Image.open(path) as im:
            im.load()
            if im.format != "WEBP":
                return None
            w, h = im.size
            mode = im.mode
        data = path.read_bytes()
        return {
            "width": w,
            "height": h,
            "mode": mode,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    except Exception:
        return None


def process(entry: dict) -> dict:
    target = ROOT / entry["target"]
    item = {
        "index": entry["index"],
        "name": entry["name"],
        "target": entry["target"],
        "source_file": entry.get("source_file"),
        "source_url": entry.get("source_url"),
    }

    if entry.get("audit_status") != "selected-for-review":
        item.update(status="refused-unapproved-source")
        return item
    if not entry.get("source_url") or not entry.get("source_file"):
        item.update(status="missing-audited-source")
        return item

    existing = inspect_existing(target)
    if existing:
        item.update(status="already-ready", **existing)
        return item

    try:
        raw = download(entry["source_url"])
        meta = to_webp(raw, target)
        item.update(status="ready", **meta)
        return item
    except Exception as exc:
        item.update(status="error", error=repr(exc))
        return item


def main() -> int:
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    entries = manifest["entries"]
    if len(entries) != 19:
        raise SystemExit(f"expected 19 NPC entries, got {len(entries)}")
    if int(manifest.get("summary", {}).get("audit_selected", 0)) != 19:
        raise SystemExit("source audit is not 19/19; refusing mirror")

    items = []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = [ex.submit(process, entry) for entry in entries]
        for fut in cf.as_completed(futures):
            item = fut.result()
            items.append(item)
            print(item["status"].upper(), item["name"], flush=True)

    order = {entry["name"]: entry["index"] for entry in entries}
    items.sort(key=lambda x: order[x["name"]])
    ready_status = {"ready", "already-ready"}
    ready = sum(x["status"] in ready_status for x in items)
    unresolved = len(items) - ready

    by_name = {x["name"]: x for x in items}
    for entry in entries:
        item = by_name[entry["name"]]
        if item["status"] in ready_status:
            entry["binary_status"] = "ready"
            entry["binary_width"] = item["width"]
            entry["binary_height"] = item["height"]
            entry["binary_bytes"] = item["bytes"]
            entry["binary_sha256"] = item["sha256"]
        else:
            entry["binary_status"] = item["status"]
            for key in ("binary_width", "binary_height", "binary_bytes", "binary_sha256"):
                entry.pop(key, None)

    manifest["summary"]["binary_ready"] = ready
    manifest["status"] = "binary-ready-19-of-19" if ready == 19 else f"binary-partial-{ready}-of-19"
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")

    report = {
        "schema_version": "mvu-npc-media-mirror-report-v1.0",
        "policy": "mirror only Stage-A-approved PRTS source_url values; no source reselection",
        "summary": {"target": len(items), "ready": ready, "unresolved_or_error": unresolved},
        "items": items,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("REPORT", report["summary"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
