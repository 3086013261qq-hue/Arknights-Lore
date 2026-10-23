# 《明日方舟》MVU 核心 NPC 媒体层规范 v1.0

## 1. 范围

目标：为 `manifest/npc-worldbook.v1.json` 中 19 / 19 核心 NPC 建立独立、可审计、远程加载的官方剧情立绘资源层。

本层只提供媒体，不修改 NPC 正文、时间线、咩咩预设或候选卡业务逻辑。

## 2. 为什么不能复用干员媒体

现有 `manifest/operator-media.v1.json` 只覆盖 463 名干员，已核对的 19 名核心 NPC 均不在该 manifest 中。
因此 NPC 媒体必须建立独立 manifest 与路径，不允许依赖“碰巧同名”“运行时临时搜索”或静静手填 URL。

## 3. 唯一目标路径

每名 NPC 只保留一张默认剧情立绘：

`media/mvu/npcs/<NPC名>/portrait.webp`

Manifest：

`manifest/npc-media.v1.json`

运行时 CDN：

`https://cdn.jsdelivr.net/gh/3086013261qq-hue/Arknights-Lore@main/<file>`

不内嵌 Base64，不在运行时请求 PRTS。

## 4. 来源优先级

1. PRTS `剧情角色一览` 中该角色的官方游戏剧情立绘，默认优先 Ver.1 / 标准姿态；
2. 同一剧情角色条目中的官方差分，只有标准姿态不可用时才选；
3. 角色独立 PRTS 页面中的官方剧情立绘；
4. 敌人模型 / 战斗模型只允许作为明确记录的最后兜底，不得伪装成剧情立绘。

禁止：

- 同人图；
- AI生成图；
- “假想干员化”立绘；
- B站/贴吧/论坛二次上传图作为正式源；
- 技能图标、敌人头像、小头像、活动Logo、关卡图。

## 5. 19 人

1. 普瑞赛斯
2. 霜星
3. 塔露拉
4. 爱国者
5. 特雷西斯
6. 安多恩
7. 曼弗雷德
8. 杜卡雷（血魔大君）
9. 赫尔昏佐伦（巫王）
10. 坎诺特
11. 林舸瑞（鼠王）
12. 阿丽娜
13. 梅菲斯特
14. 浮士德
15. ACE
16. Scout
17. Outcast
18. 克丽斯腾·莱特
19. 博士

别名与 PRTS 匹配规则以 `manifest/npc-media.v1.json` 为机器真值。

## 6. 两阶段流程

### Stage A — Audit

`tools/audit_mvu_npc_media.py`

只读取 PRTS，不发布正式二进制。
输出：

- `QA/mvu-npc-media-audit-v1.json`
- 更新 `manifest/npc-media.v1.json` 中候选 source metadata

每个人必须记录：

- 是否在剧情角色一览找到对应行；
- 候选图片；
- 原始文件名；
- PRTS 原图 URL；
- 尺寸；
- 评分；
- 最终建议候选。

只有 19 / 19 都得到可信候选后才能进入 Stage B。

### Stage B — Mirror

由静静/后续镜像脚本只下载 Stage A 已批准的 `source_url`，转换为 WebP 后写入上述目标路径。

不得在 Stage B 再临时改变图片选择算法。

## 7. WebP 规范

- 保留透明通道；
- 长边最大 1800 px，原图更小则不放大；
- WebP quality 90；
- 记录 width / height / bytes / SHA-256；
- 不裁人物身体；
- 不加背景、水印或额外UI。

## 8. MVU加载

`TERRA ARCHIVE -> NPC`：

- 打开 NPC 详情时才加载该 NPC 的 `portrait.webp`；
- 不在启动时预加载19张；
- 加载失败显示统一 PRTS 风格 fallback，不阻塞文本档案；
- NPC媒体只读，不写游戏状态。

博士必须使用自己的 NPC 立绘；禁止拿玩家头像、{{user}}媒体或任意自设头像替代博士。

## 9. QA硬门槛

- [ ] 19 / 19 在 `manifest/npc-media.v1.json` 有唯一条目；
- [ ] 19 / 19 Stage A 候选经过来源审计；
- [ ] 19 / 19 正式文件存在；
- [ ] 19 / 19 source_url 来自 PRTS / media.prts.wiki；
- [ ] 无同人图、AI图、论坛二传图；
- [ ] 无技能图标、敌人头像、Logo误选；
- [ ] 所有WebP可通过 jsDelivr 远程访问；
- [ ] MVU只按需加载当前NPC；
- [ ] 图片失败不影响正文；
- [ ] 博士媒体与{{user}}完全独立。
