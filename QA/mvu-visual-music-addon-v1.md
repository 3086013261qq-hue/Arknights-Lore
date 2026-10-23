# 《明日方舟》MVU 最终追加 QA v1.2

> 本文件是交给“静静”正式组装前必须读取的最终追加检查单。
> 本追加不改变任何已封版剧情、角色、地点、世界设定或咩咩状态规则；锁死四件事：**成熟运行时继承、明日方舟高保真视觉、成熟网易云、正式 PRTS 悬浮窗**。

## 1. 静静本轮必须同时读取

1. `docs/mvu-final-ui-spec-v1.md`
2. `manifest/mvu-ui-layout.v1.json`
3. `docs/mvu-timeline-switch-spec-v1.md`
4. `manifest/mvu-timeline-switch.v1.json`
5. `manifest/mvu-story-media.v1.json`
6. `manifest/operator-media.v1.json`
7. `docs/mvu-arknights-visual-fidelity-v1.md`
8. `manifest/mvu-music-playlist.v1.json`
9. `docs/mvu-mature-netease-floating-window-v1.md`
10. **`docs/mvu-mature-runtime-inheritance-v1.md`**
11. 本文件 `QA/mvu-visual-music-addon-v1.md`

**第 10 项是最高优先级的“不要重新发明轮子”规范。**
凡旧成熟卡已经解决的底层问题，静静必须直接继承流程，只替换《明日方舟》数据、皮肤与显示字段。

## 2. 成熟运行时继承总门槛

- [ ] 卷切换直接继承《狐妖小红娘·梦灯笼》成熟事务；
- [ ] Swipe / 卡片浏览只预览，绝不写世界书；
- [ ] `ENTER` 才执行“73 全关 → 目标开启 → 一次写回”；
- [ ] 世界书写成功后才更新 ACTIVE；失败保持原状态；
- [ ] 只用稳定 marker，不依赖数字 ID；
- [ ] GitHub → jsDelivr 远程加载直接继承成熟仓库方案；
- [ ] 卡体只保留轻量索引、manifest、路径与运行时逻辑；
- [ ] 不 Base64、不内嵌 73 封面/463 干员媒体；
- [ ] 资源由 manifest 解析，UI 不复制第二份路径表；
- [ ] 作战封面只懒加载当前 + 相邻；
- [ ] 干员只加载当前 `elite1.png`，`idle.gif` 仅点击 DYNAMIC 后请求；
- [ ] 资源失败只降级显示，不允许阻断切卷/状态/档案业务；
- [ ] UI 事件统一用事件委托 + `data-action`/controller；
- [ ] 禁止大量脆弱 inline `onclick`；
- [ ] DOM / AI 楼层重绘后幂等恢复，不重复 listener、iframe、悬浮窗、observer、timer；
- [ ] 老实例 / 老监听在重建前正确清理；
- [ ] 不允许用“多挂几个实例”解决生命周期问题；
- [ ] 咩咩预设继续是唯一游戏状态源。

任一成熟底层被重新实现为一套未经验证的新方案，QA 直接 FAIL。

## 3. 网易云：禁止重新设计播放器

- [ ] 直接继承成熟网易云模块，不重写底层。
- [ ] 固定使用单实例 outchain：`https://music.163.com/outchain/player?type=2&id={track_id}&auto=0&height=66`。
- [ ] 全卡始终只有一个 iframe / 一个播放器实例。
- [ ] 切歌只更新 `track_id` 并重载同一个 iframe。
- [ ] 首次载入 `auto=0`。
- [ ] App 跳转只由玩家真实点击触发；App 优先，HTTPS 官方网页 fallback。
- [ ] 登录 / 会员只去官方页面；不保存 Cookie、token、session、密码。
- [ ] DOM / AI 楼层重绘后自动恢复单实例并重新绑定。
- [ ] 网易云错误、地区限制、下架不得影响 MVU / 世界书 / `<status>` / 悬浮窗。
- [ ] `manifest/mvu-music-playlist.v1.json` 只负责《明日方舟》歌单与皮肤。
- [ ] 曲库只使用《明日方舟》/ 塞壬唱片相关曲目。
- [ ] 默认曲 `Speed of Light`；其他预选曲按 manifest 装配。
- [ ] 缺少明确网易云 ID 的曲目核验后冻结，禁止猜 ID。

## 4. 正式 PRTS 悬浮窗：强制存在

- [ ] body / document 级独立宿主，不绑定某一条消息 DOM；
- [ ] `position:fixed` + 高 z-index；
- [ ] singleton；
- [ ] AI 楼层 / DOM 重绘后自动恢复，不重复生成；
- [ ] 展开 / 折叠 / 关闭 / 恢复完整可用；
- [ ] 可拖拽并 clamp 在 visual viewport 内；
- [ ] 手机触控可用，不依赖 hover；
- [ ] 宽度 `min(92vw,420px)`，最大高度约 `70vh`；
- [ ] 适配 `visualViewport`、软键盘与安全区；
- [ ] 收起 / 关闭后透明宿主不挡正文或选项点击；
- [ ] 360 / 390 / 412 / 430px 手机布局不得跑出屏幕；
- [ ] PLAYER STATUS 只读咩咩 `<status>`；
- [ ] CURRENT OPERATION 读取唯一 enabled 的 `ARKNIGHTS_TIMELINE:*`；
- [ ] AUDIO 控制同一个成熟网易云实例；
- [ ] 悬浮窗不建立第二状态、不偷偷切卷。

## 5. “明日方舟同款 UI”是硬门槛

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
- [ ] 悬浮窗只是普通网页浮层。

必须做到：非对称模块、大面积黑白灰 + 小面积高纯黄、硬边/斜切/缺角/警戒纹、英文大写标题 + 中文信息 + 微字状态码、大号编号、章节封面与干员立绘成为视觉主体、明确前后景层级、120～180ms 短动效；360px Android 也不能牺牲这些视觉语言。

## 6. 页面视觉最终检查

### TERMINAL
- [ ] 当前行动封面是首页主视觉。
- [ ] `<status>` 与大号 PRTS / 卷编号错位排版。
- [ ] 四入口使用非对称尺寸。

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
- [ ] 展开态明确属于 PRTS / 罗德岛终端。
- [ ] 折叠态不是普通圆形悬浮球。
- [ ] 拖拽、折叠、关闭后均不挡正文点击。

## 7. 构建顺序 QA

- [ ] 先世界书/73卷切换；
- [ ] 再 manifest loader + jsDelivr；
- [ ] 再 463 干员按需媒体；
- [ ] 再成熟网易云；
- [ ] 再成熟悬浮窗；
- [ ] 最后才做《明日方舟》高保真美化与特效；
- [ ] 浏览器 QA 后再做 Android / SillyTavern 实机 QA；
- [ ] 已通过业务层不得因视觉返工被回退重做。

## 8. 实机截图必须交付

- [ ] 360px TERMINAL；
- [ ] 360px OPERATIONS；
- [ ] 360px OPERATOR；
- [ ] 560px TERMINAL 或 OPERATIONS；
- [ ] AUDIO TERMINAL 展开态；
- [ ] PRTS PLAYER WINDOW 展开态；
- [ ] PRTS PLAYER WINDOW 折叠态。

## 9. 最终允许交付的条件

只有以下全部通过后，静静才允许输出正式 PNG / JSON / 完整工程 / QA：

1. 成熟运行时继承 QA 全 PASS；
2. 状态与 73 卷切换 QA 全 PASS；
3. 73 / 73 剧情封面工作正常；
4. 463 干员媒体按需加载正常；
5. 《明日方舟》网易云歌单基于成熟 outchain 模块装配完成；
6. 全卡仅 1 个网易云 iframe；
7. PRTS 正式悬浮窗全功能 PASS；
8. 原版视觉高保真 QA 全 PASS；
9. 360px Android 无横向溢出；
10. 没有把 MVU / 悬浮窗做成第二状态源；
11. 媒体/网易云故障不影响业务；
12. DOM 重绘后各组件恢复且不重复；
13. 成品截图第一眼明确属于《明日方舟》/ PRTS 体系。
