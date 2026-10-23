# MVU Story Cover Media

章节封面云端媒体目录。

## 路径

- 主线：`media/mvu/story/main/main-00.webp` ～ `main-17.webp`
- SideStory：`media/mvu/story/side/<timeline-slug>.webp`

## 规则

- 素材优先从PRTS核验官方/官方衍生章节或活动视觉；下载后再做来源与卷映射审计。
- 正式发布统一使用 WebP；必要时保留来源记录，但卡内不嵌入图片/Base64。
- MVU通过 jsDelivr 从本仓库远程加载，并做懒加载；滑动预览不应一次请求全部73张。
- 封面缺失不得阻断世界书切卷；UI回退到纯文字/默认占位框。
- 本目录只负责章节/活动封面，不改动 `media/mvu/operators/` 已封版的463套干员PNG/GIF。
