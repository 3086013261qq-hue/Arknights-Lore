# 《明日方舟》MVU 最终设计 → 咩咩全栈装配交接 QA v1.0

## A. 设计冻结状态

- [x] MVU 最终视觉基线：`docs/mvu-final-ui-spec-v1.md`
- [x] 机器可读布局：`manifest/mvu-ui-layout.v1.json`
- [x] 73 卷切换规范：`docs/mvu-timeline-switch-spec-v1.md`
- [x] 73 卷切换 manifest：`manifest/mvu-timeline-switch.v1.json`
- [x] 73 / 73 剧情封面完成：`manifest/mvu-story-media.v1.json`
- [x] 干员媒体路径核验：`media/mvu/operators/<干员名>/elite1.png` + `idle.gif`
- [x] 咩咩预设为唯一游戏状态源
- [x] 本轮不修改任何已封版 lore / 时间线 / 干员正文

## B. 静静组装时必须实现

### 状态

- [ ] 首页直接读取 `<status>`，不得镜像成第二套长期变量。
- [ ] 干员关系 / 好感 / 状态直接读取咩咩已有输出。
- [ ] 当前卷由唯一 enabled 的 `ARKNIGHTS_TIMELINE:*` 条目推导。
- [ ] MVU 只保存临时 UI 状态。

### 作战档案

- [ ] MAIN 18 + SIDE STORY 55 均可浏览。
- [ ] Swipe / 箭头只预览，不写世界书。
- [ ] ENTER 执行“73 全关 → 目标开启 → 一次写回”。
- [ ] 写回成功后再更新 ACTIVE。
- [ ] 任意时刻最多 1 条时间线条目 enabled。
- [ ] 不使用世界书数字 ID，只用稳定 marker。
- [ ] 不建立持久 `_current_volume`。
- [ ] 不自动推进下一卷。

### 媒体

- [ ] CDN 基址：`https://cdn.jsdelivr.net/gh/3086013261qq-hue/Arknights-Lore@main/`
- [ ] 剧情封面由 `manifest/mvu-story-media.v1.json` 派生，不手写 73 URL。
- [ ] 只预加载当前卷 + 相邻卷。
- [ ] 干员默认只加载 `elite1.png`。
- [ ] 只有点击 DYNAMIC 才加载 `idle.gif`。
- [ ] 不预载 463×2 媒体。
- [ ] 无 Base64。
- [ ] 无 PRTS 运行时依赖。
- [ ] 图片失败有 fallback，不得白屏。

### UI

- [ ] 原版《明日方舟》/ PRTS 视觉语法：黑灰白 + 黄强调、硬边、斜切、编号、英文微字。
- [ ] 不做玻璃拟态 / 紫蓝霓虹 / 大圆角。
- [ ] 系统字体，不打包游戏专有字体。
- [ ] 360px CSS 宽安卓端可用。
- [ ] 560px 最大宽度。
- [ ] 除作战档案横向卷轴外无整体横向溢出。
- [ ] 120～180ms 微动效 + `prefers-reduced-motion`。

### 四页

- [ ] `TERMINAL / 终端`
- [ ] `OPERATIONS ARCHIVE / 作战档案`
- [ ] `OPERATOR RECORDS / 干员档案`
- [ ] `TERRA ARCHIVE / 泰拉档案`

### 持续组件

- [ ] 单实例 `AUDIO TERMINAL`，全卡始终只有一个 audio 实例。
- [ ] PRTS 悬浮终端只读 `<status>`。

## C. 禁止回归

- [ ] 不改咩咩预设。
- [ ] 不改 73 卷时间线正文。
- [ ] 不改 463 干员正文或萌点。
- [ ] 不改 18 NPC、85 地点、57 核心设定。
- [ ] 不复制 lore 进 UI 数据文件。
- [ ] 不新建地图引擎、关系图谱、服务器、数据库、WebSocket。
- [ ] 不让 MVU 成为第二剧情事实源。

## D. 实机最终 PASS 条件

必须全部满足：

1. 首页 `<status>` 显示正确；
2. 当前行动与唯一 enabled 条目一致；
3. Swipe 不改变世界书；
4. ENTER 后恰好 1 / 73 enabled；
5. 切卷失败不伪装成功；
6. 73 / 73 封面可远程加载；
7. 干员静态 / 动态媒体按需工作；
8. 动态 GIF 未点击前无网络请求；
9. 一个 audio 实例；
10. 360px Android 无整体横溢；
11. 所有本地 UI 状态清空后，剧情事实不受影响；
12. `<world_timeline>` 从未被 UI 修改；
13. 无 Base64、无运行时 PRTS；
14. 视觉明显属于罗德岛 / PRTS / 《明日方舟》终端体系。

全部 PASS 后才能输出正式成品 PNG / JSON / 完整工程与 QA 报告。
