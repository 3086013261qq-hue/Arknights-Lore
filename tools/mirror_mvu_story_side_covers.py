#!/usr/bin/env python3
"""Mirror the 55 SideStory cover/key-art images from PRTS quickly and safely.

This version batches image metadata lookups and processes activities concurrently.
A slow or broken page cannot block the whole batch; unresolved items are recorded in QA.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import io
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest/mvu-story-media.v1.json"
REPORT = ROOT / "QA/mvu-story-media-side-mirror-report.json"
API = "https://prts.wiki/api.php"
UA = "Arknights-Lore-MVU-SideStory-Mirror/2.0 (+https://github.com/3086013261qq-hue/Arknights-Lore)"
WORKERS = 8
TIMEOUT = 15

BAD = (
    "材料", "家具", "敌人", "头像", "干员", "技能", "职业", "信物", "代币",
    "蚀刻章", "道具", "芯片", "寻访", "掉落", "商店", "按钮", "图标_物品",
    "logo_prts", "favicon", "wiki", "sprite", "音乐", "技能图标", "职业分支",
)
GOOD = ("活动", "主视觉", "宣传", "封面", "banner", "keyart", "key_art", "kv", "主题")


def request_json(params: dict, retries: int = 2) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.load(r)
        except Exception as exc:
            last = exc
            if attempt < retries:
                time.sleep(1.0 + attempt)
    raise last


def page_images(title: str) -> tuple[str, list[str]]:
    tries = [title]
    if title == "落叶逐火":
        tries.append("落叶逐火2026")
    last = None
    for page in tries:
        try:
            data = request_json({"action": "parse", "format": "json", "page": page, "prop": "images", "redirects": 1})
            parsed = data.get("parse") or {}
            images = parsed.get("images") or []
            if images:
                return parsed.get("title") or page, images
        except Exception as exc:
            last = exc
    if last:
        raise last
    return title, []


def prefilter(names: list[str], title: str) -> list[tuple[int, str]]:
    out = []
    for idx, name in enumerate(names):
        low = name.lower()
        if any(term.lower() in low for term in BAD):
            continue
        bonus = title in name or any(word.lower() in low for word in GOOD)
        if idx < 45 or bonus:
            out.append((idx, name))
    return out[:60]


def batch_imageinfo(indexed: list[tuple[int, str]]) -> dict[str, dict]:
    names = [name for _, name in indexed]
    result = {}
    for start in range(0, len(names), 40):
        chunk = names[start:start + 40]
        data = request_json({
            "action": "query", "format": "json", "prop": "imageinfo", "redirects": 1,
            "iiprop": "url|size|mime", "titles": "|".join("File:" + n for n in chunk),
        })
        for page in data.get("query", {}).get("pages", {}).values():
            if "missing" in page:
                continue
            ii = (page.get("imageinfo") or [None])[0]
            if not ii or not ii.get("url"):
                continue
            title = (page.get("title") or "").removeprefix("File:")
            result[title] = {"title": page.get("title"), **ii}
    return result


def score_candidate(index: int, name: str, info: dict, title: str) -> float | None:
    w, h = int(info.get("width") or 0), int(info.get("height") or 0)
    if w < 420 or h < 240:
        return None
    ratio = w / h if h else 0
    if ratio < 0.55 or ratio > 3.2:
        return None
    low = name.lower()
    score = max(0, 4200 - index * 90)
    score += min(2800, math.sqrt(w * h) * 2.2)
    if title in name:
        score += 4200
    for word in GOOD:
        if word.lower() in low:
            score += 600
    if 0.75 <= ratio <= 2.25:
        score += 650
    if w >= 900:
        score += 450
    if h >= 500:
        score += 300
    return score


def resolve_activity_cover(title: str) -> tuple[dict | None, dict]:
    page_title, names = page_images(title)
    indexed = prefilter(names, title)
    infos = batch_imageinfo(indexed)
    ranked = []
    for idx, name in indexed:
        info = infos.get(name)
        if not info:
            continue
        score = score_candidate(idx, name, info, title)
        if score is not None:
            ranked.append((score, idx, name, info))
    ranked.sort(key=lambda x: x[0], reverse=True)
    audit = {
        "page": page_title,
        "image_count": len(names),
        "metadata_checked": len(indexed),
        "candidates": [
            {"score": round(s, 1), "index": i, "file": n, "width": x.get("width"), "height": x.get("height")}
            for s, i, n, x in ranked[:8]
        ],
    }
    if not ranked:
        audit["decision"] = "no-candidate"
        return None, audit
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None
    if top[0] < 5200:
        audit["decision"] = "low-score"
        return None, audit
    if second and top[0] - second[0] < 180 and title not in top[2]:
        audit["decision"] = "ambiguous"
        return None, audit
    audit.update(decision="selected", selected_file=top[2], selected_score=round(top[0], 1))
    return top[3], audit


def download(url: str, referer: str) -> bytes:
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except Exception as exc:
            last = exc
            time.sleep(1.0 + attempt)
    raise last


def to_webp(raw: bytes, out: Path) -> dict:
    from PIL import Image
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        if max(im.size) > 1800:
            im.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, "WEBP", quality=90, method=6)
        size = im.size
    data = out.read_bytes()
    return {"width": size[0], "height": size[1], "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def process(entry: tuple[str, str, str]) -> dict:
    ident, slug, title = entry
    target = ROOT / f"media/mvu/story/side/{slug}.webp"
    item = {"id": ident, "slug": slug, "title": title, "target": str(target.relative_to(ROOT))}
    if target.is_file() and target.stat().st_size > 0:
        item["status"] = "already-ready"
        return item
    try:
        info, audit = resolve_activity_cover(title)
        item["resolver"] = audit
        if not info:
            item["status"] = "unresolved"
            return item
        page = audit.get("page") or title
        raw = download(info["url"], "https://prts.wiki/w/" + urllib.parse.quote(page))
        meta = to_webp(raw, target)
        item.update(status="ready", source_url=info["url"], source_file=audit.get("selected_file"), **meta)
        return item
    except Exception as exc:
        item.update(status="error", error=repr(exc))
        return item


def main() -> int:
    d = json.loads(MANIFEST.read_text("utf-8"))
    entries = [tuple(x) for x in d["side"]]
    items = []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        future_map = {ex.submit(process, entry): entry for entry in entries}
        for fut in cf.as_completed(future_map):
            item = fut.result()
            items.append(item)
            print(item["status"].upper(), item["title"], flush=True)
    order = {entry[0]: i for i, entry in enumerate(entries)}
    items.sort(key=lambda x: order[x["id"]])
    ready = sum(1 for x in items if x["status"] in ("ready", "already-ready"))
    unresolved = sum(1 for x in items if x["status"] in ("unresolved", "error"))
    report = {
        "schema_version": "mvu-story-media-side-mirror-report-v2",
        "summary": {"total": len(items), "ready": ready, "unresolved_or_error": unresolved},
        "items": items,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("REPORT", report["summary"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
