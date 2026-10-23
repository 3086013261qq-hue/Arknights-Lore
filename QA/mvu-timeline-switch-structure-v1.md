# MVU Timeline Switch Structure QA v1

状态：PASS（结构层）

- 主线条目：18。
- SideStory条目：55。
- 总条目：73。
- 73个ID唯一。
- 73个marker唯一，统一 `ARKNIGHTS_TIMELINE` 命名空间。
- 73个source一对一映射现有封版时间线文件。
- 默认启用数：0。
- order范围：548～476，均位于咩咩全栈输出规则/时间线段位内。
- position：统一 `@Depth 0`。
- probability：统一100。
- Swipe不会触发世界书切换。
- 正式切换策略：全部disabled → 目标enabled → 单次写回。
- 当前卷不建立MVU持久副本；唯一enabled世界书条目即当前卷事实源。
- 章节封面路径已预留为远程WebP；当前状态为 media pending。
- 未修改任何封版时间线正文、角色、NPC、地点、核心设定、干员媒体或咩咩预设。

后续QA：PRTS封面素材抓取/映射完成后，再做73/73媒体存在性与CDN可达性验收。
