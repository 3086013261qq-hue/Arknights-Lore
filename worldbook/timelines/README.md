# Timeline Worldbook Assembly

这里保存《明日方舟》73卷时间线的**世界书装配规则**，不复制封版时间线正文。

正式正文唯一源：

- `timeline/main/main-00.md` ～ `timeline/main/main-17.md`
- `timeline/side/*.md`（55篇）

正式装配清单：`manifest/mvu-timeline-switch.v1.json`

每个 manifest entry 在最终角色卡中材料化为**一个独立世界书条目**，完整注入对应 source 的 `<world_timeline>`，默认 disabled；MVU点击“进入本卷”时只做73选1原子切换。

稳定标识统一使用 `【ARKNIGHTS_TIMELINE:*】`，禁止依赖会漂移的世界书数字ID。

封面媒体只走仓库/CDN，不进入卡体。
