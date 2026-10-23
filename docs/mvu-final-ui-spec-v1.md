# 《明日方舟》独立卡 MVU 最终 UI 设计规范 v1.0

> 本文件是交给“静静”使用咩咩制卡包·全栈组装 MVU 的唯一最终 UI 设计基线。
> 不再增加第二套状态机，不重做已封版资料，不复制剧情事实源。

## 0. 总原则

MVU 的职责只有四件事：

1. 读取并展示咩咩预设现有状态；
2. 切换 73 个剧情时间线世界书条目；
3. 浏览仓库中已经封版的干员 / 泰拉资料与远程媒体；
4. 提供单实例音乐与轻量 PRTS 悬浮终端。

### 唯一状态源

- 游戏状态唯一来源：咩咩预设。
- 当前时间、地点、世界阶段、剧情进度：直接读取 `<status>`。
- 干员关系 / 好感 / 当前状态：直接读取咩咩原生状态，不在 MVU 建立持久副本。
- 当前剧情卷：直接以 73 个 `ARKNIGHTS_TIMELINE:*` 世界书条目中唯一 `enabled=true` 的条目为事实源。
- MVU 仅允许保存临时 UI 状态；刷新后丢失也不能影响剧情事实。

---

# 1. 视觉方向：直接采用《明日方舟》原版 UI 语法

不要做“泛赛博朋克”，不要玻璃拟态，不要圆润 App 卡片，不要紫蓝霓虹。

整体采用罗德岛 / PRTS / 原版终端的视觉语言：

- 主背景：`#0B0D0F`
- 一级面板：`#171A1D`
- 二级面板：`#24282C`
- 主文字：`#F2F2ED`
- 次文字：`#91989F`
- 主强调黄：`#F0C400`
- 警告红：仅错误 / 危险提示使用
- 分隔线：1px 灰黑硬线
- 圆角：0～2px，尽量方正
- 斜切角、短斜杠、编号、英文微字、模块编号作为主要装饰
- 标题英文大写 + 中文副标题，例如 `OPERATIONS ARCHIVE / 作战档案`
- 不打包或复制游戏专有字体；使用系统无衬线字体，通过字距、大小写、粗细模拟原版气质
- 动效短促：120～180ms ease-out；支持 `prefers-reduced-motion`

推荐整体容器：

- `width: 100%`
- `max-width: 560px`
- 手机优先，360px CSS 宽度必须完整可用
- 除“作战档案横向卷轴”外禁止横向溢出

顶部固定识别：

`P.R.T.S. // RHODES ISLAND`

底部固定四页导航：

`TERMINAL` / `OPERATIONS` / `OPERATOR` / `TERRA`

持续组件：

- 单实例音乐条 `AUDIO TERMINAL`
- 可折叠 PRTS 迷你终端

---

# 2. 页面一：TERMINAL / 终端首页

定位：进入卡片后第一眼就是“明日方舟终端首页”，而不是仪表盘网页。

## 2.1 顶部状态条

直接读取咩咩 `<status>`，显示：

- 当前时间
- 当前地点
- 当前世界阶段 / 剧情阶段
- 当前任务或进度文字（若 `<status>` 已提供）

禁止复制为 MVU 自己的长期变量。

## 2.2 当前行动主卡

从 73 条时间线世界书中寻找唯一启用项：

- 有唯一启用项：显示该卷封面、标题、卷 ID、`ACTIVE` 标记；
- 没有启用项：显示 `NO ACTIVE OPERATION`；
- 若异常出现多条启用：显示警告，不擅自猜测当前卷。

封面来自：

- 主线：`media/mvu/story/main/main-XX.webp`
- SideStory：`media/mvu/story/side/<slug>.webp`

通过 jsDelivr 远程加载。

## 2.3 四个主功能块

采用原版首页不对称模块块状布局：

- `OPERATIONS ARCHIVE / 作战档案`
- `OPERATOR RECORDS / 干员档案`
- `TERRA ARCHIVE / 泰拉档案`
- `AUDIO TERMINAL / 音频终端`

只做导航，不制造新业务状态。

---

# 3. 页面二：OPERATIONS ARCHIVE / 作战档案

这是 MVU 核心页面。

## 3.1 顶部分段

两个硬切换标签：

- `MAIN`：18 卷
- `SIDE STORY`：55 卷

切换仅改变前端预览集合。

## 3.2 横向卷轴

使用 `scroll-snap` / 横向滑动：

- 当前卷卡片居中；
- 左右相邻卡片露出一部分；
- Swipe / 左右箭头仅改变预览，不写世界书；
- 只加载当前 + 左右邻近封面；
- 不预载 73 张。

每张卷卡显示：

- 远程封面
- ID（如 `MAIN-08` / `SIDE:BABEL`）
- 中文标题
- 类型标签
- 若该条目当前启用，显示黄色 `ACTIVE`

## 3.3 唯一正式切卷按钮

大按钮：

`ENTER / 进入记录`

只有点击它才允许修改世界书。

执行顺序必须严格使用现有 `manifest/mvu-timeline-switch.v1.json`：

1. 在内存中将 73 条 `ARKNIGHTS_TIMELINE:*` 全部设为 disabled；
2. 将目标 marker 设为 enabled；
3. 一次性写回；
4. 写回成功后 UI 才能显示目标为 ACTIVE；
5. 失败则保持原状态并显示错误。

禁止：

- Swipe 自动切卷；
- 依赖世界书数字 ID；
- 持久化 `_current_volume`；
- 自动判断“下一卷”；
- MVU 自己推进 `<world_timeline>`。

现有封版 `<world_timeline>` 只读。

## 3.4 数据与媒体

- 切卷 manifest：`manifest/mvu-timeline-switch.v1.json`
- 标题 / 媒体 manifest：`manifest/mvu-story-media.v1.json`
- 当前媒体完成度：73 / 73
- CDN 基址：`https://cdn.jsdelivr.net/gh/3086013261qq-hue/Arknights-Lore@main/`
- 运行时不请求 PRTS。

---

# 4. 页面三：OPERATOR RECORDS / 干员档案

定位：像原版干员档案 / 人事终端，重点是“查阅”，不是创造第二套角色系统。

## 4.1 列表

- 支持 463 名干员本地搜索；
- 名字 / 简单排序 / 搜索都只是临时 UI 状态；
- 不一次性把 463 张 PNG + 463 个 GIF 全部加载。

建议布局：左侧/顶部搜索与干员列表，选中后进入单人详情。

## 4.2 单人详情

主视觉默认使用：

`media/mvu/operators/<干员名>/elite1.png`

动态按钮：

`DYNAMIC / 动态档案`

玩家主动开启时才加载：

`media/mvu/operators/<干员名>/idle.gif`

已核验目录结构示例：

- `media/mvu/operators/12F/elite1.png`
- `media/mvu/operators/12F/idle.gif`

均通过 jsDelivr CDN 加载。

## 4.3 详情分栏

保持简单，只做三个标签：

- `PROFILE / 档案`
- `ARMAMENT / 武装`
- `STATUS / 状态`

来源：

- 档案正文：`worldbook/operators/<干员名>.md`
- 武器 / 能力：使用仓库已封版正文与武器审计结果，不另建事实表
- 状态 / 关系 / 好感：读取咩咩已有状态，不在 MVU 建副本

禁止在 UI 层复制 463 份角色正文。

---

# 5. 页面四：TERRA ARCHIVE / 泰拉档案

保持原版资料库 / 情报终端式查阅，不做地图引擎，不做关系图谱。

三个大类：

- `CORE / 核心设定`：57
- `LOCATIONS / 地点`：85
- `NPC / 核心人物`：18

交互：

- 类别切换
- 文本搜索
- 条目列表
- 单条详情

所有内容直接读取仓库封版世界书，不在 MVU 再复制一份 lore 数据。

---

# 6. AUDIO TERMINAL / 音频终端

音乐只允许一个 `<audio>` 实例。

常驻迷你条：

- 曲名
- 播放 / 暂停
- 简单进度
- 点击展开轻量曲目抽屉

音乐播放只属于本地 UI，不写剧情状态、不写世界书。

如果正式组装时仓库没有可用曲目 manifest，则保留播放器壳体与接口，不凭空生成曲库。

---

# 7. PRTS 悬浮迷你终端

做一个贴边小标签，视觉像 PRTS 终端模块。

收起：

`P.R.T.S. // ONLINE`

展开后直接显示咩咩 `<status>` 的：

- 时间
- 地点
- 当前剧情 / 阶段
- 简短任务进度

仍然只是只读视图。

---

# 8. 唯一允许的 MVU 本地状态

这些变量全部是临时 UI 状态，可以刷新即失效：

- `activePage`
- `previewBucket` (`main` / `side`)
- `previewVolumeIndex`
- `operatorSearch`
- `selectedOperator`
- `operatorMediaMode` (`static` / `dynamic`)
- `terraCategory`
- `searchQuery`
- `terminalExpanded`
- `musicPanelOpen`
- `audioTrackIndex`
- `audioPlaying`

禁止新增游戏事实型持久变量。

---

# 9. 远程资源策略

所有图片 / GIF 均只走仓库 + jsDelivr，卡本体不嵌 Base64。

CDN 基址：

`https://cdn.jsdelivr.net/gh/3086013261qq-hue/Arknights-Lore@main/`

规则：

- 剧情封面：由 `manifest/mvu-story-media.v1.json` 推导路径；
- 干员媒体：`media/mvu/operators/<URL编码后的干员目录>/elite1.png` / `idle.gif`；
- 图片失败必须有 CSS fallback，不允许整个 MVU 白屏；
- GIF 仅玩家主动启用时下载；
- 不在运行时连接 PRTS；
- 不手写 73 个 CDN URL。

---

# 10. 静静装配硬性禁止项

禁止：

- 第二套游戏状态 schema；
- `_current_volume` 一类持久当前卷变量；
- 把 Swipe 绑定为世界书写入；
- 改动已封版主线 / SideStory；
- 改动 463 干员正文 / 萌点；
- 改动 18 NPC、85 地点、57 核心设定；
- 修改咩咩预设；
- Base64 图片；
- 预载 926 个干员媒体文件；
- 运行时依赖 PRTS；
- 新建服务器、数据库、WebSocket；
- 泛赛博霓虹 / 玻璃拟态 / 大圆角 UI；
- 复制游戏专有字体或 UI 图片素材作为壳体。

只使用 CSS / 系统字体复刻《明日方舟》原版 UI 视觉语法，媒体使用本仓库现有已审计资源。

---

# 11. 实机验收目标

完成组装后必须满足：

1. 360px 宽安卓端无整体横向溢出；
2. 首页状态直接来自 `<status>`；
3. 当前卷直接由唯一 enabled 时间线条目推导；
4. Swipe 不写世界书；
5. 点击 ENTER 后 73 条中恰好 1 条 enabled；
6. 切卷失败时 UI 不假装成功；
7. 73 / 73 剧情封面远程可加载；
8. 干员静态立绘按需加载；
9. `idle.gif` 只有点 DYNAMIC 才加载；
10. 音乐始终只有一个 audio 实例；
11. 无 Base64；
12. 无 PRTS 运行时依赖；
13. `<world_timeline>` 不被 MVU 修改；
14. 所有 UI 临时状态丢失后不会破坏剧情；
15. 视觉一眼应是罗德岛 / PRTS / 《明日方舟》终端语言，而不是通用网页后台。

达到以上条件后，即可进入咩咩制卡包·全栈正式组装与实机 QA。
