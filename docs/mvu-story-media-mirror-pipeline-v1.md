# MVU 章节封面镜像流水线 v1

工具：`tools/mirror_mvu_story_covers.py`

## 目标

将 PRTS 已核验的章节/活动视觉源转换成 WebP，写入 `media/mvu/story/`，最终由 jsDelivr 提供给 MVU。角色卡本体不嵌入图片。

## 安全规则

- 默认 dry-run；只有显式 `--apply` 才写 WebP。
- 主线使用 manifest 中已经冻结的 `章节名称_<章节>.png` 精确文件名。
- SideStory 先尝试 `活动图标_正式中文名` / `活动名称_正式中文名`；若出现多个候选或无法唯一确认，标记 unresolved 并停止该项，禁止猜图。
- 不修改任何 `timeline/` 正文。
- 不自动 git commit / push，不创建或触发 GitHub Actions。
- 输出 `QA/mvu-story-media-mirror-report.json`，方便下一步审计后再提交。

## 使用

```bash
python tools/mirror_mvu_story_covers.py
python tools/mirror_mvu_story_covers.py --only main
python tools/mirror_mvu_story_covers.py --apply --only main
python tools/mirror_mvu_story_covers.py --apply --only side
```

依赖：Python 3 + Pillow。网络环境需能访问 `prts.wiki` / `media.prts.wiki`。
