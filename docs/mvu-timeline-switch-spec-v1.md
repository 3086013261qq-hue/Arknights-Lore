# 《明日方舟》MVU 时间线切卷规范 v1.0

## 1. 定位

本层只负责把现有封版剧情时间线装配成咩咩全栈的“每卷一个世界书条目”。

- 主线：18卷（MAIN-00～MAIN-17）。
- SideStory：55卷。
- 总计：73个可切换世界书时间线条目。
- 正文唯一事实源仍为 `timeline/main/*.md` 与 `timeline/side/*.md`，不复制第二份时间线正文。

## 2. 世界书条目材料化

正式打卡时，构建器对 `manifest/mvu-timeline-switch.v1.json` 的每个 entry 执行：

1. 读取 `source` 指向的封版时间线文件；
2. 原样提取完整 `<world_timeline>...</world_timeline>`；
3. 创建一个独立世界书条目；
4. 条目使用该 entry 的稳定 `marker`、`comment`、`order`、`position`、`probability`；
5. 默认全部关闭；
6. 不拆事件A/B/C，不重写正文。

稳定 marker 统一为：`【ARKNIGHTS_TIMELINE:<ID>】`。

禁止依赖世界书数字ID做切卷。

## 3. 切卷规则

切卷仅由玩家点击“进入本卷/开始行动”触发。

- 左右 Swipe 只改变MVU当前预览卡片，不修改世界书。
- 点击进入后：先在内存中把73条全部设为 disabled，再把目标条目设为 enabled，最后一次性写回。
- 任意时刻最多只允许1条 `ARKNIGHTS_TIMELINE:*` 启用。
- 世界书写入失败时，不得让前端伪装成已切换成功。
- 不根据正文内容自动猜测下一卷，不自动推进卷。

当前卷事实源就是“73条中唯一 enabled 的世界书条目”。MVU不再复制 `_current_volume` 等第二份长期状态。

## 4. 咩咩原生状态

MVU首页、悬浮球、干员终端继续只读咩咩预设已有状态：

- 当前时间/地点/世界阶段：读取世界状态栏；
- 干员关系/当前关系展示：读取咩咩原生 affinity/好感相关输出；
- 不在MVU建立这些字段的持久副本。

## 5. 章节媒体

章节/活动封面全部远程加载，不嵌入卡本体。

- 主线：`media/mvu/story/main/main-XX.webp`
- SideStory：`media/mvu/story/side/<slug>.webp`
- 来源：优先PRTS可核验的官方/官方衍生视觉素材；抓取后先审计再发布。
- MVU使用 jsDelivr CDN，按需懒加载。
- Swipe时只加载邻近卷媒体，不预载73张封面。

## 6. 不可越界

本轮不修改：

- 已封版主线/SideStory正文；
- 463干员正文与萌点；
- 18 NPC；
- 85地点；
- 57核心世界设定；
- 咩咩预设；
- 现有463套干员PNG/GIF。

MVU只是PRTS展示/切卷终端，不成为第二剧情事实源。
