#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRTS -> rough worldbook builder for Arknights-Lore.

Design goal:
- Read the repository's canonical PRTS indexes.
- Fetch only the pages needed by those indexes.
- Extract structured facts from table rows and page categories.
- NEVER mirror long wiki prose or game dialogue.
- Emit rough, editable worldbook drafts with placeholders for human refinement.

This is intentionally a "fact harvester + skeleton generator", not a wiki copier.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://prts.wiki/w/"
DEFAULT_INDEX = Path("reference/prts-index/catalog/index.v1.json")
DEFAULT_OUT = Path("build/rough-worldbook")
USER_AGENT = (
    "Arknights-Lore-RoughcardBuilder/1.0 "
    "(structured-facts only; non-mirroring; contact via repository)"
)
MAX_FACT_VALUE = 180

CHARACTER_KEY_ALIASES = {
    "性别": ["性别"],
    "种族": ["种族"],
    "身份": ["身份", "职业", "职位"],
    "所属": ["所属", "阵营", "势力", "所属组织"],
    "出身": ["出身", "出身地", "出生地"],
    "感染情况": ["感染情况", "矿石病感染情况"],
    "身高": ["身高"],
    "职业": ["职业"],
    "分支": ["分支", "职业分支"],
}

GENERIC_FACT_KEYS = {
    "所属国家", "国家", "地区", "位置", "所属", "阵营", "种族",
    "身份", "职业", "组织", "类型", "类别", "别名", "代号", "身高",
    "感染情况", "矿石病感染情况", "出身", "出身地", "出生地",
}


@dataclass
class PageFacts:
    title: str
    url: str
    facts: dict[str, str]
    categories: list[str]
    fetched_at: str


class Fetcher:
    def __init__(self, cache_dir: Path, delay: float = 1.2, timeout: float = 20.0, retries: int = 3) -> None:
        self.cache_dir = cache_dir
        self.delay = max(delay, 0.0)
        self.timeout = timeout
        self.retries = max(retries, 1)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, title: str) -> Path:
        h = hashlib.sha1(title.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{h}.json"

    def fetch(self, title: str, refresh: bool = False) -> PageFacts:
        cp = self._cache_path(title)
        if cp.exists() and not refresh:
            data = json.loads(cp.read_text("utf-8"))
            return PageFacts(**data)

        url = BASE_URL + quote(title, safe="")
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                parsed = parse_structured_facts(response.text)
                item = PageFacts(
                    title=title,
                    url=response.url,
                    facts=parsed["facts"],
                    categories=parsed["categories"],
                    fetched_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                )
                cp.write_text(json.dumps(asdict(item), ensure_ascii=False, indent=2), encoding="utf-8")
                time.sleep(self.delay)
                return item
            except Exception as exc:
                last_error = exc
                time.sleep(min(2 ** attempt, 5))
        raise RuntimeError(f"failed to fetch {title}: {last_error}")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("\u200b", "")


def parse_structured_facts(html: str) -> dict[str, Any]:
    """Extract short key/value facts from tables; ignore narrative paragraphs."""
    soup = BeautifulSoup(html, "lxml")
    facts: dict[str, str] = {}

    for row in soup.select("tr"):
        cells = row.find_all(["th", "td"], recursive=False)
        if len(cells) < 2:
            continue
        key = clean_text(cells[0].get_text(" ", strip=True)).rstrip("：:")
        value = clean_text(" ".join(c.get_text(" ", strip=True) for c in cells[1:]))
        if not key or not value or len(key) > 24 or len(value) > MAX_FACT_VALUE:
            continue
        if key in GENERIC_FACT_KEYS or any(x in key for x in ("所属", "出身", "感染", "种族", "身份", "职业", "类型", "国家")):
            facts.setdefault(key, value)

    categories: list[str] = []
    for a in soup.select("#mw-normal-catlinks a, .mw-normal-catlinks a"):
        t = clean_text(a.get_text(" ", strip=True))
        if t and t != "分类":
            categories.append(t)

    return {"facts": facts, "categories": sorted(set(categories))}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text("utf-8"))


def unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        s = clean_text(str(item))
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def flatten_name_values(obj: Any) -> list[str]:
    skip_keys = {
        "schema_version", "kind", "source", "sources", "policy", "status",
        "notes", "qa_rules", "construction_rules", "next_stage",
        "source_scope", "snapshot_through", "canonical_batches",
        "legacy_noncanonical_batches",
    }
    names: list[str] = []

    def walk(x: Any, parent_key: str = "") -> None:
        if isinstance(x, str):
            if parent_key in skip_keys or x.startswith(("http://", "https://")):
                return
            if len(x) <= 80:
                names.append(x)
        elif isinstance(x, list):
            for item in x:
                walk(item, parent_key)
        elif isinstance(x, dict):
            if "name" in x and isinstance(x["name"], str):
                names.append(x["name"])
            for k, v in x.items():
                if k in skip_keys or k == "name":
                    continue
                walk(v, k)

    walk(obj)
    return unique(names)


def load_operator_names(catalog_dir: Path, operator_index: Path) -> list[str]:
    index = load_json(operator_index)
    out: list[str] = []
    for batch in index.get("canonical_batches", []):
        data = load_json(catalog_dir / batch)
        for e in data.get("entries", []):
            if isinstance(e, str):
                out.append(e)
            elif isinstance(e, dict) and isinstance(e.get("name"), str):
                out.append(e["name"])
    return unique(out)


def load_catalog_names(path: Path) -> list[str]:
    data = load_json(path)
    if isinstance(data.get("entries"), list):
        vals = []
        for e in data["entries"]:
            if isinstance(e, str):
                vals.append(e)
            elif isinstance(e, dict) and isinstance(e.get("name"), str):
                vals.append(e["name"])
        return unique(vals)
    return flatten_name_values(data)


def geography_records(path: Path) -> list[tuple[str, str]]:
    data = load_json(path)
    records: list[tuple[str, str]] = []
    for key in ("modern_countries", "independent_city_states", "regions", "unknown_states", "ancient_states"):
        for name in data.get(key, []):
            records.append((name, ""))
    for country, places in data.get("major_places_by_country", {}).items():
        for name in places:
            records.append((name, country))
    dedup: dict[str, str] = {}
    for name, country in records:
        dedup.setdefault(name, country)
    return list(dedup.items())


def first_fact(facts: dict[str, str], aliases: list[str]) -> str:
    for alias in aliases:
        if alias in facts:
            return facts[alias]
    for k, v in facts.items():
        if any(alias in k for alias in aliases):
            return v
    return ""


def character_card(name: str, page: PageFacts) -> str:
    f = page.facts
    mapped = {key: first_fact(f, aliases) for key, aliases in CHARACTER_KEY_ALIASES.items()}
    body = mapped.get("身高") or "待精修"
    return f"""<{name}character>
名字:{name}
性别:{mapped.get('性别') or '待精修'}
种族:{mapped.get('种族') or '待精修'}
身份:{mapped.get('身份') or '待精修'}
所属:{mapped.get('所属') or '待精修'}
出身:{mapped.get('出身') or '待精修'}
感染情况:{mapped.get('感染情况') or '待精修'}

印象:待精修
发色:待精修
发型:待精修
瞳色:待精修
身材:{body}
胸部:待精修
上衣:待精修
下装:待精修
配饰:待精修
鞋子:待精修

经历:
- 待精修

关系:
- 待精修

心理模型:
- Trauma:待精修
- Defense:待精修
- Trigger:待精修
- Need:待精修

对话范例:
“待精修”
“待精修”
“待精修”
</{name}character>

<核心设定:{name}·能力>
定位:{mapped.get('职业') or mapped.get('身份') or '待精修'}
武器/战斗方式:待精修
源石技艺/特殊能力:待精修
代表性能力:待精修
限制与代价:待精修
战斗习惯:待精修
</核心设定:{name}·能力>

<!-- source: {page.url} -->
"""


def location_card(name: str, country: str, page: PageFacts | None) -> str:
    url = page.url if page else BASE_URL + quote(name, safe="")
    return f"""<地点:{name}>
名称:{name}
所属国家:{country or '待精修'}
类别:待精修
概况:待精修
重要组织:待精修
相关人物:待精修
相关事件:待精修
</地点:{name}>
<!-- source: {url} -->
"""


def simple_setting_card(tag: str, name: str, page: PageFacts | None) -> str:
    url = page.url if page else BASE_URL + quote(name, safe="")
    facts = page.facts if page else {}
    selected = [f"- {k}:{v}" for k, v in facts.items() if k in GENERIC_FACT_KEYS and len(v) <= 120]
    facts_block = "\n".join(selected[:8]) if selected else "- 待精修"
    return f"""<核心设定:{name}>
类型:{tag}
结构化事实:
{facts_block}
概要:待精修
关联人物/组织/地点:待精修
</核心设定:{name}>
<!-- source: {url} -->
"""


def safe_filename(name: str) -> str:
    s = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    return s[:100] or "_"


def write_entry(base: Path, name: str, content: str) -> None:
    base.mkdir(parents=True, exist_ok=True)
    (base / f"{safe_filename(name)}.md").write_text(content, encoding="utf-8")


def write_merged(base: Path, filename: str, chunks: list[str]) -> None:
    base.mkdir(parents=True, exist_ok=True)
    (base / filename).write_text("\n\n---\n\n".join(chunks), encoding="utf-8")


def maybe_fetch(fetcher: Fetcher, title: str, refresh: bool, errors: list[dict[str, str]]) -> PageFacts | None:
    try:
        return fetcher.fetch(title, refresh=refresh)
    except Exception as exc:
        errors.append({"title": title, "error": str(exc)})
        return None


def git_commit(repo_root: Path, message: str) -> None:
    subprocess.run(["git", "add", "build/rough-worldbook"], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo_root, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build rough Arknights worldbook drafts from PRTS structured facts.")
    parser.add_argument("--repo-root", default=".", help="Arknights-Lore repository root")
    parser.add_argument("--index", default=str(DEFAULT_INDEX), help="canonical catalog entrypoint")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="output directory")
    parser.add_argument("--scope", choices=["all", "operators", "npcs", "geography", "races", "organizations", "world_terms"], default="all")
    parser.add_argument("--limit", type=int, default=0, help="debug limit per scope; 0 = no limit")
    parser.add_argument("--delay", type=float, default=1.2, help="seconds between uncached requests")
    parser.add_argument("--refresh", action="store_true", help="ignore cached page facts")
    parser.add_argument("--no-fetch", action="store_true", help="generate skeletons without network")
    parser.add_argument("--commit", action="store_true", help="git add/commit generated rough drafts")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    index_path = root / args.index
    out_dir = root / args.out
    catalog_dir = index_path.parent
    entrypoint = load_json(index_path)
    catalogs = entrypoint["catalogs"]

    cache_dir = Path(os.environ.get("PRTS_ROUGHCARD_CACHE", str(Path.home() / ".cache" / "arknights-lore-prts")))
    fetcher = Fetcher(cache_dir=cache_dir, delay=args.delay)
    errors: list[dict[str, str]] = []
    manifest: dict[str, Any] = {
        "generator": "prts_roughcard_builder.py",
        "policy": "structured facts + placeholders only; no long wiki prose mirrored",
        "scopes": {},
    }

    def limited(xs):
        xs = list(xs)
        return xs[:args.limit] if args.limit > 0 else xs

    def page_for(name: str) -> PageFacts | None:
        if args.no_fetch:
            return None
        return maybe_fetch(fetcher, name, args.refresh, errors)

    scopes = {args.scope} if args.scope != "all" else {"operators", "npcs", "geography", "races", "organizations", "world_terms"}

    if "operators" in scopes:
        names = limited(load_operator_names(catalog_dir, catalog_dir / catalogs["operators"]))
        chunks = []
        for i, name in enumerate(names, 1):
            page = page_for(name) or PageFacts(name, BASE_URL + quote(name, safe=""), {}, [], "")
            content = character_card(name, page)
            write_entry(out_dir / "characters" / "operators", name, content)
            chunks.append(content)
            print(f"[operators {i}/{len(names)}] {name}")
        write_merged(out_dir / "merged", "operators.md", chunks)
        manifest["scopes"]["operators"] = len(names)

    if "npcs" in scopes:
        names = limited(load_catalog_names(catalog_dir / catalogs["curated_story_characters"]))
        chunks = []
        for i, name in enumerate(names, 1):
            page = page_for(name) or PageFacts(name, BASE_URL + quote(name, safe=""), {}, [], "")
            content = character_card(name, page)
            write_entry(out_dir / "characters" / "npcs", name, content)
            chunks.append(content)
            print(f"[npcs {i}/{len(names)}] {name}")
        write_merged(out_dir / "merged", "npcs.md", chunks)
        manifest["scopes"]["npcs"] = len(names)

    if "geography" in scopes:
        records = limited(geography_records(catalog_dir / catalogs["geography"]))
        chunks = []
        for i, (name, country) in enumerate(records, 1):
            page = page_for(name)
            content = location_card(name, country, page)
            write_entry(out_dir / "locations", name, content)
            chunks.append(content)
            print(f"[geography {i}/{len(records)}] {name}")
        write_merged(out_dir / "merged", "locations.md", chunks)
        manifest["scopes"]["geography"] = len(records)

    for scope, key, tag, folder, merged_name in [
        ("races", "races", "种族", "settings/races", "races.md"),
        ("organizations", "organizations", "组织", "settings/organizations", "organizations.md"),
        ("world_terms", "world_terms", "世界设定", "settings/world-terms", "world-terms.md"),
    ]:
        if scope not in scopes:
            continue
        names = limited(load_catalog_names(catalog_dir / catalogs[key]))
        chunks = []
        for i, name in enumerate(names, 1):
            page = page_for(name)
            content = simple_setting_card(tag, name, page)
            write_entry(out_dir / folder, name, content)
            chunks.append(content)
            print(f"[{scope} {i}/{len(names)}] {name}")
        write_merged(out_dir / "merged", merged_name, chunks)
        manifest["scopes"][scope] = len(names)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "QA-fetch-errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nDone. Output: {out_dir}")
    print(f"Fetch errors: {len(errors)}")
    if args.commit:
        git_commit(root, "data: generate rough PRTS worldbook drafts")
        print("Committed generated drafts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
