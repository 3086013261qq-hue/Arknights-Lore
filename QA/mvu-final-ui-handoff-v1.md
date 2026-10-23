# 《明日方舟》MVU 最终设计 → 咩咩全栈装配交接 QA v1.1

## A. 设计冻结状态

- [x] MVU 最终视觉基线：`docs/mvu-final-ui-spec-v1.md`
- [x] 机器可读布局：`manifest/mvu-ui-layout.v1.json`（v1.3）
- [x] 73 卷切换规范：`docs/mvu-timeline-switch-spec-v1.md`
- [x] 73 卷切换 manifest：`manifest/mvu-timeline-switch.v1.json`
- [x] MAIN 沙盒自动衔接：`docs/mvu-main-sandbox-autoadvance-v1.md` + `manifest/mvu-main-autoadvance.v1.json`
- [x] 73 / 73 剧情封面完成：`manifest/mvu-story-media.v1.json`
- [x] 干员媒体路径核验：`media/mvu/operators/<干员名>/elite1.png` + `idle.gif`
- [x] 费洛蒙 / 气味签名设计：`docs/pheromone-moe-mvu-spec-v1.md` + `manifest/pheromone-profile-spec.v1.json`
- [x] 博士独立 NPC：`worldbook/npcs/博士.md`
- [x] {{user}} / 博士身份隔离：`docs/player-doctor-identity-separation-v1.md`
- [x] NPC manifest 更新为 19 人：`manifest/npc-worldbook.v1.json`
- [x] 咩咩预设为唯一游戏状态源
- [x] 主线与现有支线源文件 `时间待核` 已归零

## B. 静静组装时必须实现

### 状态与身份

- [ ] 首页直接读取 `<status>`，不得镜像成第二套长期变量。
- [ ] 干员关系 / 好感 / 状态直接读取咩咩已有输出。
- [ ] 当前卷由唯一 enabled 的 `ARKNIGHTS_TIMELINE:*` 条目推导。
- [ ] MVU 只保存临时 UI 状态。
- [ ] `{{user}} != 博士`；博士必须作为独立 NPC 存在。
- [ ] 时间线里的“博士 / Doctor / 预言家（博士语境）”不得自动替换为{{user}}。
- [ ] {{user}}不得继承博士的前文明身份、失忆史、PRTS权限、巴别塔履历或原作人物关系。

### 作战档案

- [ ] MAIN 18 + SIDE STORY 55 均可浏览。
- [ ] Swipe / 箭头只预览，不写世界书。
- [ ] 手动 ENTER 执行“73 全关 → 目标开启 → 一次写回”。
- [ ] 写回成功后再更新 ACTIVE。
- [ ] 任意时刻最多 1 条时间线条目 enabled。
- [ ] 不使用世界书数字 ID，只用稳定 marker。
- [ ] 不建立持久 `_current_volume`。
- [ ] MAIN-00～MAIN-16 当前卷明确进入沙盒模式时，按 `manifest/mvu-main-autoadvance.v1.json` 自动切下一 MAIN 卷，并复用同一成熟切卷事务。
- [ ] 历史楼层中的“沙盒模式”不得触发自动切卷。
- [ ] MAIN-17 进入沙盒后保持 MAIN-17 enabled，显示 `MAIN STORY COMPLETE / SANDBOX`。
- [ ] SideStory 55 卷全部禁止自动衔接；沙盒后由玩家手动选择其他卷。

### 费洛蒙 / 萌点

- [ ] 为 463 / 463 干员生成独立 scent profile。
- [ ] 为 19 / 19 核心 NPC（含博士）生成独立 scent profile。
- [ ] 干员短版气味签名直接追加进现有萌点 overlay，不改 canonical operator body。
- [ ] NPC 使用轻量 `worldbook/npc-moe.v1.json` overlay，不改 canonical NPC body。
- [ ] 生成 `manifest/pheromone-profile.v1.json` 供 MVU 只读使用。
- [ ] OPERATOR 详情新增 `PHEROMONE / 气味档案`。
- [ ] NPC详情新增 `SCENT PROFILE / 气味档案`。
- [ ] `RELATION RESPONSE` 只从现有咩咩关系/好感推导，不保存新值。
- [ ] 不新增 `pheromone_affinity`、`mark_level`、气味所有权等第二状态。
- [ ] 机械体使用机械气味签名，不写生物费洛蒙腺体。
- [ ] 未成年 / 年龄风险角色全部 `nonsexual-only`。
- [ ] 气味不能强迫好感、发情、服从、配偶绑定或性同意。

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

- [ ] 成熟单实例 `AUDIO TERMINAL`。
- [ ] 正式 `P.R.T.S. // PLAYER WINDOW` 使用 body 级 singleton，支持拖拽、折叠、关闭与恢复。

## C. 禁止回归

- [ ] 不改咩咩预设。
- [ ] 不擅自重写 73 卷剧情事实；已核定的时间锚点必须保留。
- [ ] 不重写 463 干员 canonical 正文；费洛蒙只进入萌点 overlay。
- [ ] 不重写 19 NPC canonical 正文；气味只进入 NPC 萌点 overlay。
- [ ] 不改 85 地点、57 核心设定的事实内容；博士身份隔离属于现有设定的运行边界修正。
- [ ] 不复制 lore 进 UI 数据文件。
- [ ] 不新建地图引擎、关系图谱、服务器、数据库、WebSocket。
- [ ] 不让 MVU 成为第二剧情事实源。
- [ ] 不让 SideStory 按 manifest 数组顺序自动串联。
- [ ] 不把{{user}}和博士合并。

## D. 实机最终 PASS 条件

必须全部满足：

1. 首页 `<status>` 时间 / 地点 / 世界阶段 / 目标显示正确；
2. 当前行动与唯一 enabled 条目一致；
3. Swipe 不改变世界书；
4. 手动 ENTER 后恰好 1 / 73 enabled；
5. MAIN 沙盒自动衔接后仍恰好 1 / 73 enabled；
6. MAIN-17 沙盒不再自动切卷；SideStory沙盒全部不自动切卷；
7. 切卷失败不伪装成功；
8. 73 / 73 封面可远程加载；
9. 干员静态 / 动态媒体按需工作；
10. 动态 GIF 未点击前无网络请求；
11. 463干员 + 19 NPC 气味档案可查，且不建立第二关系状态；
12. 博士NPC可独立搜索，{{user}}不被识别成博士；
13. 一个网易云 outchain iframe实例；
14. PRTS正式悬浮窗全功能正常；
15. 360px Android 无整体横溢；
16. 所有本地 UI 状态清空后，剧情事实不受影响；
17. `<world_timeline>` 从未被 UI 修改；
18. 无 Base64、无运行时 PRTS；
19. 视觉明显属于罗德岛 / PRTS / 《明日方舟》终端体系。

全部 PASS 后才能输出正式成品 PNG / JSON / 完整工程与 QA 报告。
