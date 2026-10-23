#!/usr/bin/env python3
"""Mirror the 55 SideStory cover/key-art images from PRTS."""
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
UA = "Arknights-Lore-MVU-SideStory-Mirror/2.2 (+https://github.com/3086013261qq-hue/Arknights-Lore)"
WORKERS = 8
TIMEOUT = 15

BAD = (
    "材料", "家具", "敌人", "头像", "干员", "技能", "职业", "信物", "代币",
    "蚀刻章", "道具", "芯片", "寻访", "掉落", "商店", "按钮", "图标_物品",
    "logo_prts", "favicon", "wiki", "sprite", "音乐", "技能图标", "职业分支",
)


def strip_ns(value: str) -> str:
    value = value.strip()
    if ":" in value:
        prefix, rest = value.split(":", 1)
        if prefix.casefold() in {"file", "image", "文件"}:
            value = rest
    return value


def norm_name(value: str) -> str:
    return " ".join(strip_ns(value).replace("_", " ").split()).casefold()


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
                time.sleep(1 + attempt)
    raise last


def imageinfo(names: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
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
            returned = strip_ns(page.get("title") or "")
            out[norm_name(returned)] = {"file": returned, "title": page.get("title"), **ii}
    return out


def exact_cover(title: str) -> tuple[dict | None, str | None]:
    candidates = [
        f"活动图标_{title}.png",
        f"活动名称_{title}.png",
        f"活动图标_{title.replace('：', '')}.png",
        f"活动名称_{title.replace('：', '')}.png",
    ]
    infos = imageinfo(candidates)
    for name in candidates:
        info = infos.get(norm_name(name))
        if info:
            return info, name
    return None, None


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


def score(index: int, name: str, info: dict, title: str) -> float | None:
    low = name.casefold()
    if any(x.casefold() in low for x in BAD):
        return None
    w, h = int(info.get("width") or 0), int(info.get("height") or 0)
    if w < 250 or h < 110:
        return None
    ratio = w / h if h else 0
    if ratio < 0.45 or ratio > 4.5:
        return None
    value = max(0, 3000 - index * 40) + min(1800, math.sqrt(w * h) * 1.8)
    if title in name:
        value += 4500
    if "活动图标" in name:
        value += 6000
    elif "活动名称" in name:
        value += 4000
    elif any(x in low for x in ("主视觉", "宣传", "封面", "banner", "keyart", "kv")):
        value += 2500
    return value


def fallback_cover(title: str) -> tuple[dict | None, dict]:
    page_title, names = page_images(title)
    filtered = []
    for idx, name in enumerate(names):
        low = name.casefold()
        if any(x.casefold() in low for x in BAD):
            continue
        if idx < 55 or title in name or "活动图标" in name or "活动名称" in name:
            filtered.append((idx, name))
    filtered = filtered[:70]
    infos = imageinfo([n for _, n in filtered])
    ranked = []
    for idx, name in filtered:
        info = infos.get(norm_name(name))
        if not info:
            continue
        s = score(idx, name, info, title)
        if s is not None:
            ranked.append((s, idx, name, info))
    ranked.sort(key=lambda x: x[0], reverse=True)
    audit = {
        "page": page_title,
        "image_count": len(names),
        "metadata_checked": len(filtered),
        "candidates": [
            {"score": round(s, 1), "index": i, "file": n, "width": x.get("width"), "height": x.get("height")}
            for s, i, n, x in ranked[:8]
        ],
    }
    if not ranked:
        audit["decision"] = "no-candidate"
        return None, audit
    top = ranked[0]
    audit.update(decision="selected", selected_file=top[2], selected_score=round(top[0], 1))
    return top[3], audit


def resolve_cover(title: str) -> tuple[dict | None, dict]:
    info, exact_name = exact_cover(title)
    if info:
        return info, {"decision": "selected-exact", "selected_file": exact_name, "page": title}
    return fallback_cover(title)


def download(url: str, referer: str) -> bytes:
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except Exception as exc:
            last = exc
            time.sleep(1 + attempt)
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
        info, audit = resolve_cover(title)
        item["resolver"] = audit
        if not info:
            item["status"] = "unresolved"
            return item
        page = audit.get("page") or title
        raw = download(info["url"], "https://prts.wiki/w/" + urllib.parse.quote(page))
        meta = to_webp(raw, target)
        item.update(status="ready", source_url=info["url"], source_file=audit.get("selected_file") or info.get("file"), **meta)
        return item
    except Exception as exc:
        item.update(status="error", error=repr(exc))
        return item


def main() -> int:
    data = json.loads(MANIFEST.read_text("utf-8"))
    entries = [tuple(x) for x in data["side"]]
    items = []
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = [ex.submit(process, entry) for entry in entries]
        for fut in cf.as_completed(futures):
            item = fut.result()
            items.append(item)
            print(item["status"].upper(), item["title"], flush=True)
    order = {entry[0]: i for i, entry in enumerate(entries)}
    items.sort(key=lambda x: order[x["id"]])
    ready = sum(1 for x in items if x["status"] in ("ready", "already-ready"))
    unresolved = len(items) - ready
    report = {
        "schema_version": "mvu-story-media-side-mirror-report-v2.2",
        "summary": {"total": len(items), "ready": ready, "unresolved_or_error": unresolved},
        "items": items,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("REPORT", report["summary"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
