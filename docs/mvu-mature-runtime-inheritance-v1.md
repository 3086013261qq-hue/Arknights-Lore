# 《明日方舟》MVU 成熟运行时继承总规范 v1.0

> 本文件是静静正式组装《明日方舟》独立卡时的最高优先级“不要重新发明轮子”规范。
> 核心原则：**凡是在《狐妖小红娘·梦灯笼》、亚空间演唱会 / Warhammer BanG！！、脑叶公司及后续卡中已经实机验证稳定的 MVU 运行时流程，一律继承；《明日方舟》只替换数据、视觉皮肤、条目规模和显示字段。**

## 0. 继承边界

### 可以重新做的只有

- 《明日方舟》/ PRTS / 罗德岛高保真视觉；
- 73 卷（MAIN 18 + SideStory 55）的数据与显示；
- 463 干员档案及远程 PNG/GIF 显示；
- 57 核心设定、85 地点、18 核心 NPC 的资料浏览；
- 《明日方舟》/ 塞壬唱片网易云曲目列表；
- 与咩咩 `<status>` 对应的显示字段。

### 禁止重新发明的底层

- 世界书卷切换事务；
- GitHub → jsDelivr 仓库远程加载；
- manifest 驱动资源解析；
- 媒体懒加载与 fallback；
- MVU UI 事件桥接；
- DOM / AI 楼层重绘恢复；
- 生命周期清理与 singleton；
- 网易云播放器底层；
- 全局可拖拽悬浮窗底层；
- 咩咩状态源与 MVU 的边界。

---

# 1. 卷切换：直接继承《狐妖小红娘·梦灯笼》成熟流程

本项目 73 卷的表现层不同，但切换事务必须复用成熟范式。

## 1.1 预览与正式切换分离

- Swipe / 左右箭头 / 点击卡片只改变前端预览；
- 预览不得写世界书；
- 只有玩家明确点击 `ENTER / 进入记录` 才进入正式切换事务；
- 当前预览不是剧情事实。

## 1.2 正式切换事务

按现有 `manifest/mvu-timeline-switch.v1.json`：

1. 读取 73 条稳定 marker；
2. 在内存准备“73 全关 + 目标 1 条开启”的完整结果；
3. 一次性写回世界书；
4. 写回成功后，UI 才将目标标成 `ACTIVE`；
5. 写回失败则保持原 ACTIVE，显示错误，不伪装成功。

继承梦灯笼已验证的原则：**先业务写入成功，再更新 MVU 表现；失败不允许前端假成功。**

## 1.3 识别方式

- 只用稳定 marker：`【ARKNIGHTS_TIMELINE:<ID>】`；
- 禁止依赖世界书数字 ID；
- 禁止 `_current_volume` 第二真值；
- 73 条中唯一 `enabled=true` 的条目就是当前卷事实源。

## 1.4 生命周期

- 切卷后只刷新需要变化的当前卷 / ACTIVE / 封面区域；
- 不重建整个 MVU；
- 不重新挂第二个播放器或第二个悬浮窗；
- 历史消息 / 历史楼层不得反向触发切卷。

---

# 2. 仓库与媒体：直接继承梦灯笼 GitHub → jsDelivr 架构

正式运行时数据源：

`3086013261qq-hue/Arknights-Lore@main`

CDN 基址：

`https://cdn.jsdelivr.net/gh/3086013261qq-hue/Arknights-Lore@main/`

## 2.1 卡本体只留轻量索引与逻辑

禁止：

- 把 PNG/GIF/WebP/Base64 塞进卡本体；
- 把 73 张封面硬编码成 73 条 URL；
- 把 463×2 干员媒体预载进内存；
- 运行时再去 PRTS 抓资源。

MVU 只读取 manifest / 路径并拼接 CDN 地址。

## 2.2 Manifest 是资源事实源

正式使用：

- `manifest/mvu-story-media.v1.json`：73 卷标题 / 封面；
- `manifest/mvu-timeline-switch.v1.json`：73 卷世界书切换；
- `manifest/operator-media.v1.json`：463 干员媒体；
- `manifest/mvu-music-playlist.v1.json`：明日方舟网易云歌单；
- `manifest/mvu-ui-layout.v1.json`：MVU 页面 / 组件布局。

不在 UI 脚本中复制第二份同义表。

## 2.3 懒加载：沿用成熟 media lifecycle

### 作战档案

- 当前卷：立即加载；
- 相邻卷：预取；
- 其余 70 张左右：不加载；
- Swipe 后更新“当前 + 邻近”窗口；
- 离开作战档案页后允许浏览器缓存保留，但 JS 不继续创建额外实例。

### 干员档案

- 选中干员才加载该人的 `elite1.png`；
- 只有玩家点击 `DYNAMIC` 才请求 `idle.gif`；
- 切换干员时停止继续维护旧 GIF 视图；
- 禁止预载 463 个 GIF。

### Fallback

媒体失败时：

1. 保留文字 / 信息层；
2. 使用 CSS/占位视觉 fallback；
3. 记录该资源错误；
4. 不白屏、不拖垮页面、不阻断世界书切换。

继承梦灯笼“媒体只是展示层、失败不能拖业务”的原则。

---

# 3. UI桥接：沿用成熟事件委托，不用脆弱 inline 交互

静静组装时：

- 统一使用事件委托 + `data-action` / `data-id`；
- 禁止把大量 `onclick` 内联在动态生成节点上；
- 业务 action 通过单一 controller/dispatcher 路由；
- MVU DOM 被宿主重绘后，桥接自动恢复；
- 重绑必须幂等，不能一重绘就多绑定一次事件；
- 同一点击不得因重复 listener 执行两次切卷 / 两次切歌 / 两次切媒体。

推荐 action 类型固定：

- `nav-page`
- `preview-volume`
- `enter-volume`
- `select-operator`
- `operator-media-static`
- `operator-media-dynamic`
- `terra-category`
- `audio-select-track`
- `audio-open-app`
- `float-expand`
- `float-collapse`
- `float-close`
- `float-restore`

动作名字可按咩咩全栈实际 API 调整，但不得拆成多套互不兼容的桥。

---

# 4. DOM / 楼层重绘：成熟恢复策略

凡宿主导致消息 / AI楼层 DOM 重绘：

- 主 MVU：重新发现宿主并幂等挂接；
- 网易云：恢复唯一 outchain iframe，不生成第二实例；
- PRTS PLAYER WINDOW：恢复 body 级 singleton；
- 当前卷：从唯一 enabled 世界书重新读取，而不是从旧 DOM 猜；
- `<status>`：重新读取咩咩当前输出；
- 干员动态媒体：仅在当前用户仍主动选择 DYNAMIC 时恢复，否则回静态；
- 旧监听、Observer、timer 在重建前清理。

禁止使用“多挂几个实例，总有一个能活”的方式规避生命周期问题。

---

# 5. 网易云：继承成熟模块

网易云完整规则见：

`docs/mvu-mature-netease-floating-window-v1.md`

本文件只再次强调：

- 不重写播放器；
- 单实例 outchain；
- `auto=0`；
- 曲目列表只换成《明日方舟》；
- 音乐错误与 MVU 业务隔离。

---

# 6. 悬浮窗：继承成熟 body 级运行时

完整规则同样见：

`docs/mvu-mature-netease-floating-window-v1.md`

本项目仅替换：

- 皮肤 → 明日方舟 / PRTS；
- PLAYER STATUS → 咩咩 `<status>`；
- CURRENT OPERATION → 73 卷唯一 enabled；
- AUDIO → 同一个成熟网易云实例。

底层拖拽、折叠、关闭、恢复、visualViewport、安全区、singleton、DOM 重绘恢复全部继承，不重新设计。

---

# 7. 咩咩状态：继续唯一事实源

- `<status>` = 时间 / 地点 / 世界阶段 / 任务等；
- 咩咩 affinity/status = 干员关系与状态；
- `<world_timeline>` = 剧情事实；
- 唯一 enabled 的 `ARKNIGHTS_TIMELINE:*` = 当前卷；
- MVU = 展示 / 导航 / 明确玩家操作。

MVU 不建立任何同义长期状态。

---

# 8. 构建与交付：沿用成熟“先业务、后视觉、再打包”流程

静静不得一上来直接出最终 PNG。

建议正式顺序：

1. 装配世界书与 73 卷切换；
2. 装配仓库 manifest loader + jsDelivr；
3. 装配 463 干员按需媒体；
4. 装配成熟网易云；
5. 装配成熟悬浮窗；
6. 装配《明日方舟》高保真 UI / 特效；
7. 浏览器 QA；
8. Android / SillyTavern 实机 QA；
9. 只在前述通过后输出正式 JSON / PNG / 完整工程与 QA。

媒体、视觉或网易云失败时只返工对应层，不回退已通过的剧情 / 世界书业务。

---

# 9. 静静最终判断题

如果某一功能在旧成熟卡中已经解决过，静静必须先问自己：

> “我是在复用成熟流程，只替换明日方舟的数据/皮肤吗？”

如果答案不是“是”，就说明正在重新发明轮子，应停止并回到本规范。

最终目标不是做一套“全新的明日方舟 MVU 框架”，而是：

**成熟框架 + 明日方舟数据 + 明日方舟高保真皮肤。**
