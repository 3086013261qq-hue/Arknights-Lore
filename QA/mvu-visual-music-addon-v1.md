# 《明日方舟》MVU 最终追加 QA v1.1

> 本文件是交给“静静”正式组装前必须读取的最终追加检查单。
> 本追加不改变任何已封版剧情、角色、地点、世界设定或咩咩状态规则；只锁死三件事：**明日方舟高保真视觉、成熟网易云继承、正式 PRTS 悬浮窗**。

## 1. 静静本轮必须同时读取

1. `docs/mvu-final-ui-spec-v1.md`
2. `manifest/mvu-ui-layout.v1.json`
3. `docs/mvu-timeline-switch-spec-v1.md`
4. `manifest/mvu-timeline-switch.v1.json`
5. `manifest/mvu-story-media.v1.json`
6. `docs/mvu-arknights-visual-fidelity-v1.md`
7. `manifest/mvu-music-playlist.v1.json`
8. **`docs/mvu-mature-netease-floating-window-v1.md`**
9. 本文件 `QA/mvu-visual-music-addon-v1.md`

视觉、网易云、悬浮窗部分如有表述强弱差异，以第 6、7、8、9 项为高优先级；状态、剧情、世界书业务仍以原规范为准。

## 2. 网易云：禁止重新设计播放器

- [ ] **直接继承成熟网易云模块，不重写底层。**
- [ ] 固定使用单实例 outchain：`https://music.163.com/outchain/player?type=2&id={track_id}&auto=0&height=66`。
- [ ] 全卡始终只有一个 iframe / 一个播放器实例。
- [ ] 切歌只更新 `track_id` 并重载同一个 iframe。
- [ ] 首次载入 `auto=0`，不强制自动播放。
- [ ] App 跳转只由玩家真实点击触发；App 优先，HTTPS 官方网页 fallback。
- [ ] 登录 / 会员只去官方页面；不保存 Cookie、token、session、密码。
- [ ] DOM / AI 楼层重绘后必须自动恢复单实例并重新绑定。
- [ ] 网易云错误、地区限制、下架均不得影响 MVU / 世界书 / `<status>` / 悬浮窗。
- [ ] `manifest/mvu-music-playlist.v1.json` **只负责《明日方舟》歌单与皮肤，不是新播放器规范**。
- [ ] 曲库只使用《明日方舟》/ 塞壬唱片相关曲目。
- [ ] 默认曲 `Speed of Light`；其他预选曲按 manifest 装配。
- [ ] 缺少明确网易云 ID 的曲目必须核验后冻结，禁止猜 ID。
- [ ] 外层使用 PRTS / 明日方舟硬边皮肤，禁止做成圆角网易云 App 卡片。

## 3. 正式 PRTS 悬浮窗：强制存在

悬浮窗不是可选功能，也不是一枚“只会展开 `<status>` 的小标签”。必须实现成熟全局浮窗运行时：

- [ ] body / document 级独立宿主，不绑定某一条消息 DOM；
- [ ] `position:fixed` + 高 z-index；
- [ ] singleton，任何时候只能存在一个；
- [ ] AI 楼层 / DOM 重绘后自动恢复，不重复生成；
- [ ] 展开 / 折叠 / 关闭 / 恢复四种操作完整可用；
- [ ] 可拖拽，拖动后 clamp 在 visual viewport 内；
- [ ] 不依赖 hover，手机触控可用；
- [ ] 宽度 `min(92vw,420px)`，最大高度约 `70vh`；
- [ ] 适配 `visualViewport`、软键盘与 `safe-area-inset-*`；
- [ ] 收起 / 关闭后透明宿主不得挡聊天正文或选项点击；
- [ ] 360 / 390 / 412 / 430px 手机布局均不得跑出屏幕。

### 悬浮窗内容

- [ ] `PLAYER STATUS`：只读咩咩 `<status>` 的时间、地点、剧情阶段、任务/进度；
- [ ] `CURRENT OPERATION`：读取唯一 enabled 的 `ARKNIGHTS_TIMELINE:*`；
- [ ] `AUDIO`：显示当前网易云曲目并控制/打开同一个成熟播放器；
- [ ] 不建立第二套状态，不维护 `_current_volume`；
- [ ] 不在悬浮窗偷偷提供第二个切卷入口；切卷仍只允许 `OPERATIONS -> ENTER`。

## 4. “明日方舟同款 UI”是硬门槛，不是建议

以下任一情况出现，正式 QA 直接 FAIL：

- [ ] 只是黑底 + 黄线 + 普通按钮；
- [ ] 首页像通用 Dashboard；
- [ ] 大量等宽圆角卡片；
- [ ] 页面只有文字，没有大图参与构图；
- [ ] 干员立绘只是小头像；
- [ ] 作战封面只是小缩略图；
- [ ] 手机端退化成简陋列表；
- [ ] 玻璃拟态、紫蓝霓虹、柔光 HUD；
- [ ] 页面空得像原型或测试页；
- [ ] 四页长得完全一样；
- [ ] 悬浮窗只是普通网页浮层，没有 PRTS / 明日方舟视觉识别。

必须做到：非对称模块、大面积黑白灰 + 小面积高纯黄、硬边/斜切/缺角/警戒纹、英文大写标题 + 中文信息 + 微字状态码、大号编号、章节封面与干员立绘作为视觉主体、明确前后景层级、120～180ms 短动效；360px Android 也不能牺牲这些视觉语言。

## 5. 页面视觉最终检查

### TERMINAL
- [ ] 当前行动封面是首页主视觉。
- [ ] `<status>` 与大号 PRTS / 卷编号错位排版。
- [ ] 四入口使用非对称尺寸，不允许四等分方块。

### OPERATIONS
- [ ] 当前卷大图居中，左右邻卷露边。
- [ ] MAIN / SIDE STORY 是硬切片式标签。
- [ ] `ENTER / 进入记录` 是最强主操作。
- [ ] ACTIVE 使用黄条 / 黄角标。

### OPERATOR
- [ ] `elite1.png` 占详情页约 45%～60% 视觉面积。
- [ ] 大号编号 + 代号 + PROFILE / ARMAMENT / STATUS 形成原版档案感。
- [ ] DYNAMIC 未点击前绝无 `idle.gif` 请求。

### TERRA
- [ ] CORE / LOCATIONS / NPC 有情报索引式编号与硬切换。
- [ ] 单条详情有标题层、元信息层、正文层。

### PLAYER WINDOW
- [ ] 展开态第一眼明确属于 PRTS / 罗德岛终端。
- [ ] 折叠态仍有明日方舟视觉识别，不是普通圆形悬浮球。
- [ ] 拖拽、折叠、关闭后均不挡正文点击。

## 6. 实机截图必须交付

正式成品前至少提供：

- [ ] 360px TERMINAL；
- [ ] 360px OPERATIONS；
- [ ] 360px OPERATOR；
- [ ] 560px TERMINAL 或 OPERATIONS；
- [ ] AUDIO TERMINAL 展开态；
- [ ] **PRTS PLAYER WINDOW 展开态；**
- [ ] **PRTS PLAYER WINDOW 折叠态。**

## 7. 最终允许交付的条件

只有以下全部通过后，静静才允许输出正式 PNG / JSON / 完整工程 / QA：

1. 原有状态与 73 卷切换 QA 全 PASS；
2. 73 / 73 剧情封面工作正常；
3. 463 干员媒体按需加载正常；
4. 《明日方舟》网易云歌单基于成熟 outchain 模块装配完成；
5. 全卡仅 1 个网易云 iframe；
6. PRTS 正式悬浮窗全功能 PASS；
7. 原版视觉高保真 QA 全 PASS；
8. 360px Android 无横向溢出；
9. 没有把 MVU / 悬浮窗做成第二状态源；
10. 网易云故障不影响任何业务；
11. DOM 重绘后播放器与悬浮窗都恢复且不重复；
12. 成品截图第一眼明确属于《明日方舟》/ PRTS 体系。
