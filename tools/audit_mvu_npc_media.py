#!/usr/bin/env python3
"""Audit official story-character portraits for the 19 core NPCs from PRTS.

This script deliberately does NOT publish portrait binaries. It resolves the
剧情角色一览 row for every core NPC, ranks official story-art candidates and
writes an auditable report + selected source metadata back into the manifest.
A later mirror step may download only selections that pass this audit.
"""
from __future__ import annotations

import json
import math
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest/npc-media.v1.json"
REPORT = ROOT / "QA/mvu-npc-media-audit-v1.json"
API = "https://prts.wiki/api.php"
PAGE = "剧情角色一览"
UA = "Arknights-Lore-MVU-NPC-Audit/1.1 (+https://github.com/3086013261qq-hue/Arknights-Lore)"
TIMEOUT = 15

BAD = (
    "enemy_", "敌人", "头像", "head", "icon", "图标", "skill", "技能", "logo",
    "职业", "材料", "sprite", "地图", "map", "活动图标", "活动名称", "家具",
)
GOOD = (
    "avg_avg_npc", "avg_npc", "avg_", "剧情", "立绘", "portrait", "character",
)
EXT_RE = re.compile(r"\.(?:png|jpe?g|webp)$", re.I)
URL_RE = re.compile(r"(?:https?:)?//[^\"'<>\s]+?\.(?:png|jpe?g|webp)(?:\?[^\"'<>\s]*)?", re.I)
FILE_RE = re.compile(r"(?:Avg|avg)[^\"'<>\s/\\]*?\.(?:png|jpe?g|webp)", re.I)


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


def norm(value: str) -> str:
    value = urllib.parse.unquote(value or "")
    value = value.replace("_", " ").replace("·", "").replace("・", "")
    value = re.sub(r"[\s，,。.!！?？:：;；'\"“”‘’（）()《》〈〉【】\[\]]+", "", value)
    return value.casefold()


def strip_file_namespace(value: str) -> str:
    value = urllib.parse.unquote((value or "").strip())
    for prefix in ("File:", "Image:", "文件:", "文件："):
        if value.casefold().startswith(prefix.casefold()):
            value = value[len(prefix):]
            break
    return value


def file_from_url(url: str) -> str | None:
    if not url:
        return None
    url = urllib.parse.unquote(url)
    if url.startswith("//"):
        url = "https:" + url
    try:
        path = urllib.parse.urlparse(url).path
    except Exception:
        path = url
    parts = [p for p in path.split("/") if p]
    for part in reversed(parts):
        if EXT_RE.search(part):
            part = re.sub(r"^\d+px-", "", part)
            return part
    return None


def fetch_story_character_html() -> str:
    data = request_json({
        "action": "parse",
        "format": "json",
        "page": PAGE,
        "prop": "text",
        "redirects": 1,
    })
    return ((data.get("parse") or {}).get("text") or {}).get("*") or ""


def row_match_name(row, aliases: list[str]) -> str | None:
    cells = row.find_all(["td", "th"], recursive=False)
    if not cells:
        return None
    first = cells[0].get_text(" ", strip=True)
    nfirst = norm(first)
    for alias in aliases:
        na = norm(alias)
        if nfirst == na or nfirst.startswith(na):
            return first
    return None


def candidate_files_from_row(row) -> list[str]:
    ordered: list[str] = []

    def add(value: str | None) -> None:
        if not value:
            return
        value = strip_file_namespace(value)
        if not EXT_RE.search(value):
            return
        if value not in ordered:
            ordered.append(value)

    for a in row.find_all("a"):
        href = a.get("href") or ""
        decoded = urllib.parse.unquote(href)
        if "文件:" in decoded or "File:" in decoded or "Image:" in decoded:
            tail = decoded.split("/", 2)[-1]
            if "文件:" in tail:
                tail = tail.split("文件:", 1)[1]
            elif "File:" in tail:
                tail = tail.split("File:", 1)[1]
            elif "Image:" in tail:
                tail = tail.split("Image:", 1)[1]
            add(tail.split("#", 1)[0].split("?", 1)[0])

    for img in row.find_all("img"):
        for key in ("alt", "src", "data-src", "data-original", "data-lazy-src"):
            raw = img.get(key)
            if not raw:
                continue
            from_url = file_from_url(raw)
            if from_url:
                add(from_url)
            add(raw)
        srcset = img.get("srcset") or ""
        for token in srcset.split(","):
            from_url = file_from_url(token.strip().split(" ", 1)[0])
            if from_url:
                add(from_url)

    raw_html = str(row)
    for match in URL_RE.findall(raw_html):
        add(file_from_url(match))
    for match in FILE_RE.findall(raw_html):
        add(match)

    return ordered


def imageinfo(names: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for start in range(0, len(names), 40):
        chunk = names[start:start + 40]
        if not chunk:
            continue
        data = request_json({
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "redirects": 1,
            "iiprop": "url|size|mime",
            "titles": "|".join("File:" + n for n in chunk),
        })
        for page in data.get("query", {}).get("pages", {}).values():
            if "missing" in page:
                continue
            ii = (page.get("imageinfo") or [None])[0]
            if not ii or not ii.get("url"):
                continue
            file_name = strip_file_namespace(page.get("title") or "")
            out[norm(file_name)] = {"file": file_name, **ii}
    return out


def score(index: int, name: str, info: dict) -> float | None:
    low = name.casefold()
    if any(b.casefold() in low for b in BAD):
        return None
    w = int(info.get("width") or 0)
    h = int(info.get("height") or 0)
    if w < 180 or h < 240:
        return None
    ratio = w / h if h else 0
    if ratio < 0.20 or ratio > 2.2:
        return None

    value = max(0.0, 2200.0 - index * 80.0)
    value += min(2200.0, math.sqrt(w * h) * 1.8)
    for rank, token in enumerate(GOOD):
        if token.casefold() in low:
            value += 6000.0 - rank * 450.0
            break
    if low.endswith(".png"):
        value += 900.0
    return value


def audit_entry(entry: dict, soup: BeautifulSoup) -> dict:
    aliases = entry["aliases"]
    matched_row = None
    matched_label = None
    for row in soup.find_all("tr"):
        label = row_match_name(row, aliases)
        if label:
            matched_row = row
            matched_label = label
            break

    result = {
        "index": entry["index"],
        "name": entry["name"],
        "aliases": aliases,
        "target": entry["target"],
        "row_found": bool(matched_row),
        "matched_label": matched_label,
    }
    if matched_row is None:
        result["status"] = "row-not-found"
        result["candidates"] = []
        return result

    names = candidate_files_from_row(matched_row)
    infos = imageinfo(names)
    ranked = []
    for idx, file_name in enumerate(names):
        info = infos.get(norm(file_name))
        if not info:
            continue
        s = score(idx, file_name, info)
        if s is not None:
            ranked.append((s, idx, file_name, info))

    # PRTS' own Ver.1 / Ver.2 / ... order is authoritative for the default
    # portrait. Resolution is only a quality gate; it must not make a later
    # expression/costume difference outrank the first valid standard version.
    ranked.sort(key=lambda x: (x[1], -x[0]))

    result["candidate_file_count"] = len(names)
    result["candidates"] = [
        {
            "score": round(s, 1),
            "dom_index": idx,
            "file": file_name,
            "url": info.get("url"),
            "width": info.get("width"),
            "height": info.get("height"),
            "mime": info.get("mime"),
        }
        for s, idx, file_name, info in ranked[:8]
    ]
    if not ranked:
        result["status"] = "no-usable-candidate"
        return result

    top = ranked[0]
    result.update(
        status="selected-for-review",
        selected_file=top[2],
        selected_url=top[3].get("url"),
        selected_width=top[3].get("width"),
        selected_height=top[3].get("height"),
        selected_score=round(top[0], 1),
    )
    return result


def main() -> int:
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    html = fetch_story_character_html()
    if not html:
        raise SystemExit("PRTS 剧情角色一览 parse returned empty HTML")
    soup = BeautifulSoup(html, "html.parser")

    items = []
    for entry in manifest["entries"]:
        item = audit_entry(entry, soup)
        items.append(item)
        print(item["status"].upper(), item["name"], item.get("selected_file", ""), flush=True)

    selected = sum(x["status"] == "selected-for-review" for x in items)
    row_found = sum(bool(x["row_found"]) for x in items)
    report = {
        "schema_version": "mvu-npc-media-audit-v1.1",
        "source_page": PAGE,
        "policy": "audit only; no portrait binaries are published by this script; first valid PRTS story-art version is preferred",
        "summary": {
            "target": len(items),
            "row_found": row_found,
            "selected_for_review": selected,
            "unresolved": len(items) - selected,
        },
        "items": items,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")

    by_name = {x["name"]: x for x in items}
    for entry in manifest["entries"]:
        audit = by_name[entry["name"]]
        entry["audit_status"] = audit["status"]
        if audit.get("selected_file"):
            entry["source_page"] = PAGE
            entry["source_file"] = audit["selected_file"]
            entry["source_url"] = audit["selected_url"]
            entry["source_width"] = audit["selected_width"]
            entry["source_height"] = audit["selected_height"]
        else:
            for key in ("source_page", "source_file", "source_url", "source_width", "source_height"):
                entry.pop(key, None)
    manifest["summary"]["audit_selected"] = selected
    manifest["status"] = f"audit-selected-{selected}-of-{len(items)}"
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")

    print("REPORT", report["summary"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
