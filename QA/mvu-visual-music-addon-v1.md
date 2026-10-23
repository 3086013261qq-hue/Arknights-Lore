# 《明日方舟》MVU 视觉高保真 + 网易云音乐最终追加 QA v1.0

> 本文件是交给“静静”正式组装前必须读取的最终追加检查单。
> 本追加不改变任何已封版剧情、角色、地点、世界设定或咩咩状态规则，只加强 UI 美术与 AUDIO TERMINAL。

## 1. 静静本轮必须同时读取

1. `docs/mvu-final-ui-spec-v1.md`
2. `manifest/mvu-ui-layout.v1.json`
3. `docs/mvu-timeline-switch-spec-v1.md`
4. `manifest/mvu-timeline-switch.v1.json`
5. `manifest/mvu-story-media.v1.json`
6. **`docs/mvu-arknights-visual-fidelity-v1.md`**
7. **`manifest/mvu-music-playlist.v1.json`**
8. 本文件 `QA/mvu-visual-music-addon-v1.md`

视觉与音乐部分如有表述强弱差异，以第 6、7、8 项为高优先级；状态、剧情、世界书业务仍以原规范为准。

## 2. AUDIO TERMINAL 最终要求

- [ ] 只使用《明日方舟》/ 塞壬唱片-MSR 相关曲目。
- [ ] 曲库直接读取 `manifest/mvu-music-playlist.v1.json`。
- [ ] 预选 8 首：`Speed of Light`、`Renegade`、`Radiant`、`Immutable`、`BE ME (Monster Siren Records)`、`Mystic Light Quest`、`Snow Parade`、`Boiling Blood`。
- [ ] 默认曲：`Speed of Light`。
- [ ] 全 MVU 始终只有一个音频实例。
- [ ] 首次载入不自动播放。
- [ ] 网易云 App 跳转优先，网页链接兜底。
- [ ] manifest 已给出明确 song id 的曲目可直接使用；缺少 id 的曲目必须在组装时按“精确标题 + 明日方舟/塞壬唱片身份”核验后冻结，禁止猜 id。
- [ ] 单曲地区不可用不能导致 MVU 报错或白屏。
- [ ] 音乐不写入剧情状态、好感、世界书或 `<status>`。
- [ ] 播放器外观必须继续使用明日方舟 / PRTS 硬边终端语法，禁止做成圆角网易云小组件。

## 3. “明日方舟同款 UI”是硬门槛，不是建议

以下任一情况出现，正式 QA 直接 FAIL：

- [ ] 只是黑底 + 黄线 + 普通按钮；
- [ ] 首页像通用 Dashboard；
- [ ] 大量等宽圆角卡片；
- [ ] 页面只有文字，没有大图参与构图；
- [ ] 干员立绘只是小头像；
- [ ] 作战封面只是小缩略图；
- [ ] 手机端为了适配而退化成简陋列表；
- [ ] 使用玻璃拟态、紫蓝霓虹、柔光 HUD；
- [ ] 页面空得像原型或测试页；
- [ ] 四页长得完全一样，只替换标题和正文。

必须做到：

- [ ] 非对称模块布局；
- [ ] 大面积黑白灰、小面积高纯黄；
- [ ] 硬边 / 斜切 / 缺角 / 警戒纹；
- [ ] 英文大写标题 + 中文信息 + 微字状态码；
- [ ] 大号编号 / 卷号 / OPERATOR 编号作为背景层；
- [ ] 章节封面和干员立绘成为视觉主体；
- [ ] 至少背景层、主视觉层、信息层、交互层四层关系清晰；
- [ ] 动效短促克制，120～180ms；
- [ ] 360px Android 仍保留完整美术语言；
- [ ] 视觉上明显像罗德岛 / PRTS / 《明日方舟》，而不是“明日方舟配色网页”。

## 4. 页面视觉最终检查

### TERMINAL

- [ ] 当前行动封面是首页主视觉。
- [ ] `<status>` 信息与大号 PRTS / 卷编号错位排版。
- [ ] 四个入口使用不对称尺寸，不允许四等分方块。

### OPERATIONS

- [ ] 当前卷大图居中，左右邻卷露边。
- [ ] MAIN / SIDE STORY 是硬切片式标签。
- [ ] `ENTER / 进入记录` 是最强主操作。
- [ ] ACTIVE 使用黄条 / 黄角标，不把整页刷黄。

### OPERATOR

- [ ] `elite1.png` 占详情页约 45%～60% 视觉面积。
- [ ] 大号编号 + 代号 + PROFILE / ARMAMENT / STATUS 形成原版档案感。
- [ ] DYNAMIC 未点击前绝无 `idle.gif` 请求。

### TERRA

- [ ] CORE / LOCATIONS / NPC 有情报索引式编号与硬切换。
- [ ] 单条详情有标题层、元信息层、正文层，不是一整块纯文字。

## 5. 实机截图必须交付

正式成品前至少提供：

- [ ] 360px TERMINAL；
- [ ] 360px OPERATIONS；
- [ ] 360px OPERATOR；
- [ ] 560px TERMINAL 或 OPERATIONS；
- [ ] AUDIO TERMINAL 展开态。

若截图只能证明“功能能用”，但不能证明“像《明日方舟》”，仍然算 FAIL。

## 6. 最终允许交付的条件

只有以下全部通过后，静静才允许输出正式 PNG / JSON / 完整工程 / QA：

1. 原有状态与 73 卷切换 QA 全 PASS；
2. 73 / 73 剧情封面工作正常；
3. 463 干员媒体按需加载正常；
4. 8 首明日方舟网易云歌单装配完成；
5. 单 audio 实例；
6. 原版视觉高保真 QA 全 PASS；
7. 360px Android 无横向溢出；
8. 没有把 MVU 做成第二状态源；
9. 没有因为“移动端适配”牺牲视觉质量；
10. 成品截图第一眼明确属于《明日方舟》/ PRTS 体系。
