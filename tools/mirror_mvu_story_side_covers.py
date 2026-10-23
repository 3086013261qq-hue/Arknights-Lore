#!/usr/bin/env python3
"""Mirror the 55 SideStory cover/key-art images from PRTS into media/mvu/story/side.

The resolver inspects images actually used on each PRTS activity page, filters small UI assets,
and prefers early, large, event-title-bearing artwork. It never silently substitutes a low-score image.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest/mvu-story-media.v1.json"
REPORT = ROOT / "QA/mvu-story-media-side-mirror-report.json"
API = "https://prts.wiki/api.php"
UA = "Arknights-Lore-MVU-SideStory-Mirror/1.0 (+https://github.com/3086013261qq-hue/Arknights-Lore)"

BAD = (
    "材料", "家具", "敌人", "头像", "干员", "技能", "职业", "信物", "代币",
    "蚀刻章", "道具", "芯片", "寻访", "掉落", "商店", "按钮", "图标_物品",
    "logo_prts", "favicon", "wiki", "sprite", "音乐",
)
GOOD = ("活动", "主视觉", "宣传", "封面", "banner", "keyart", "key_art", "kv", "主题")


def request_json(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def resolve_file(name: str) -> dict | None:
    data = request_json({
        "action": "query", "format": "json", "prop": "imageinfo", "redirects": 1,
        "iiprop": "url|size|mime", "titles": "File:" + name,
    })
    for page in data.get("query", {}).get("pages", {}).values():
        if "missing" in page:
            continue
        ii = (page.get("imageinfo") or [None])[0]
        if ii and ii.get("url"):
            return {"title": page.get("title"), **ii}
    return None


def page_images(title: str) -> tuple[str, list[str]]:
    tries = [title]
    if title == "落叶逐火":
        tries += ["落叶逐火2026"]
    last = None
    for page in tries:
        try:
            data = request_json({
                "action": "parse", "format": "json", "page": page,
                "prop": "images", "redirects": 1,
            })
            parsed = data.get("parse") or {}
            images = parsed.get("images") or []
            if images:
                return parsed.get("title") or page, images
        except Exception as exc:
            last = exc
    if last:
        raise last
    return title, []


def score_candidate(index: int, name: str, info: dict, title: str) -> float | None:
    low = name.lower()
    if any(term.lower() in low for term in BAD):
        return None
    w, h = int(info.get("width") or 0), int(info.get("height") or 0)
    if w < 420 or h < 240:
        return None
    ratio = w / h if h else 0
    if ratio < 0.55 or ratio > 3.2:
        return None
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
    ranked = []
    for idx, name in enumerate(names):
        try:
            info = resolve_file(name)
        except Exception:
            continue
        if not info:
            continue
        score = score_candidate(idx, name, info, title)
        if score is None:
            continue
        ranked.append((score, idx, name, info))
    ranked.sort(key=lambda x: x[0], reverse=True)
    audit = {
        "page": page_title,
        "image_count": len(names),
        "candidates": [
            {"score": round(s, 1), "index": i, "file": n, "width": x.get("width"), "height": x.get("height")}
            for s, i, n, x in ranked[:8]
        ],
    }
    if not ranked:
        return None, audit
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None
    if top[0] < 5200:
        audit["decision"] = "low-score"
        return None, audit
    if second and top[0] - second[0] < 180 and title not in top[2]:
        audit["decision"] = "ambiguous"
        return None, audit
    audit["decision"] = "selected"
    audit["selected_file"] = top[2]
    audit["selected_score"] = round(top[0], 1)
    return top[3], audit


def download(url: str, referer: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


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


def main() -> int:
    d = json.loads(MANIFEST.read_text("utf-8"))
    report = {"schema_version": "mvu-story-media-side-mirror-report-v1", "items": []}
    ready = 0
    unresolved = 0
    for ident, slug, title in d["side"]:
        target = ROOT / f"media/mvu/story/side/{slug}.webp"
        item = {"id": ident, "slug": slug, "title": title, "target": str(target.relative_to(ROOT))}
        try:
            info, audit = resolve_activity_cover(title)
            item["resolver"] = audit
            if not info:
                item["status"] = "unresolved"
                unresolved += 1
                report["items"].append(item)
                print("UNRESOLVED", title, audit.get("decision"), audit.get("candidates", [])[:2])
                continue
            page = audit.get("page") or title
            raw = download(info["url"], "https://prts.wiki/w/" + urllib.parse.quote(page))
            meta = to_webp(raw, target)
            item.update(status="ready", source_url=info["url"], source_file=audit.get("selected_file"), **meta)
            ready += 1
            print("READY", title, target.relative_to(ROOT))
        except Exception as exc:
            item.update(status="error", error=repr(exc))
            unresolved += 1
            print("ERROR", title, repr(exc))
        report["items"].append(item)
    report["summary"] = {"total": len(d["side"]), "ready": ready, "unresolved_or_error": unresolved}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("REPORT", report["summary"])
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
