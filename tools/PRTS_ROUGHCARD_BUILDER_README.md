# PRTS → 粗糙世界书生成器

用途：从仓库现有 canonical 索引出发，逐页读取 PRTS 的短结构化字段，自动生成可供后续人工/静静精修的粗糙角色卡、地点卡、组织/种族/世界设定条目。

## 边界

本工具不是百科镜像器：

- 只提取短结构化事实（如种族、所属、出身、感染情况、身高、类型等）。
- 不保存百科长正文、剧情长文本、角色台词或技能说明全文。
- 无法从结构化字段确定的信息统一写成 `待精修`。
- 每个生成条目保留 PRTS 来源 URL，便于后续核验。
- 信息素 AU 不由本工具生成；仍由后续精修阶段按项目规范单独制作。

## 安装

在 `Arknights-Lore` 仓库根目录执行：

```bash
python -m pip install -r tools/requirements-prts-roughcard.txt
```

## 先做小规模测试

```bash
python tools/prts_roughcard_builder.py --scope operators --limit 5
```

输出：

```text
build/rough-worldbook/
├─ characters/
│  ├─ operators/
│  └─ npcs/
├─ locations/
├─ settings/
│  ├─ races/
│  ├─ organizations/
│  └─ world-terms/
├─ merged/
├─ manifest.json
└─ QA-fetch-errors.json
```

## 全量生成

```bash
python tools/prts_roughcard_builder.py --scope all
```

默认行为：

- 使用 `reference/prts-index/catalog/index.v1.json` 作为唯一 canonical 入口。
- 每次未缓存的网络请求之间等待 1.2 秒。
- 抓取结果只缓存结构化事实，默认缓存到 `~/.cache/arknights-lore-prts/`。
- 页面抓取失败不会中断全任务，会在 `QA-fetch-errors.json` 中记录并继续生成带 `待精修` 的骨架。

## 只生成骨架、不访问网络

```bash
python tools/prts_roughcard_builder.py --scope all --no-fetch
```

适合先检查索引数量、文件命名和目录结构。

## 指定某一类

```bash
python tools/prts_roughcard_builder.py --scope operators
python tools/prts_roughcard_builder.py --scope npcs
python tools/prts_roughcard_builder.py --scope geography
python tools/prts_roughcard_builder.py --scope races
python tools/prts_roughcard_builder.py --scope organizations
python tools/prts_roughcard_builder.py --scope world_terms
```

## 自动本地提交

```bash
python tools/prts_roughcard_builder.py --scope all --commit
```

这只执行 `git add` + `git commit`，不会自动 `git push`。

## 后续精修建议

粗卡生成后，批量精修优先级建议：

1. 角色：补 `印象 / 外观 / 经历 / 关系 / 心理模型 / 对话范例 / 能力`。
2. 地点：补 `概况 / 重要组织 / 相关人物 / 相关事件`。
3. 组织与种族：把 PRTS 事实重新组织为适合咩咩世界书的简洁条目。
4. 信息素 AU：只在符合项目成人边界与适用条件时单独生成。
5. 每批完成后再跑来源、去重、格式、关键词、体积 QA。

## 与项目架构的关系

- 本工具生成的是 **build-time 粗稿**，不是远程运行时资源。
- 正式角色/地点/设定仍进入卡内世界书。
- 远程层仍只承载巨大剧情时间线。
- 禁止修改咩咩预设。
