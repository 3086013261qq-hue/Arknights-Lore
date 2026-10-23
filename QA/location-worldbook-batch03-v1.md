# 地点世界书 Batch 03 / 全量封版 QA v1

## 范围

- 基线 HEAD：`7842c9246613c634a4887db396844e263ad0b0bd`
- 本批：B41-B45 + C01-C25，共30个。
- 累计正式地点：85 / 85。
- 正式源：`worldbook/locations/*.md`
- 格式：咩咩制卡包·全栈 `<核心设定:地点名>`。

## 结构检查

- 本批30/30：一地点一文件。
- 本批30/30：存在唯一 `<核心设定:地点名>` 开标签与对应闭标签。
- 本批30/30：包含类型、国家/地区、上级地点、定位、空间与环境、社会与功能、主要组织/势力、关键人物关联、剧情关联、时间状态、知识迷雾、RP场景特征、互动约束、触发词、来源锚点。
- 全量85/85：manifest登记，ID覆盖 A01-A15、B01-B45、C01-C25。
- 全量：地点ID、正式名称、正式文件路径一一对应；未新增 `<location>` / `<place>` 等非原生标签。

## 高剧透与特殊空间检查

- `泽尔格勒石棺设施`、`万星园`、`荒域·巫王塔`、`夕之画境·婆山镇`、`泡影国`、`梦城堡`、`岁兽梦境·梦中书塔`、`源石内化宇宙`等均显式设置剧情阶段/知识迷雾限制。
- 特殊空间不当作普通现实地理，不给普通NPC全知权限。
- 梦境、画境、异世界与认知空间中的事实不会自动覆盖现实人物身份、关系与地理规则。
- 石棺、源石计划、天空屏障等深层真相继续受 `worldbook/settings/04_前文明与深层真相.md` 约束。

## 内容检查

- 城市总卡与子地点继续分工，子地点不重复整段国家/城市宏观设定。
- 银心湖与登山铁路分别承担区域和交通空间功能；不重复拆分车厢、站台等微场景。
- 拉特兰荒野修道院因封版时间线未给可确认独立专名，采用明确的功能性名称并在正文注明。
- 零号公路按连续旅行走廊合并大涌泉镇—洋蓟村—太阳谷—红砂镇，不机械拆卡。
- 未添加无来源的精确人口、距离、建筑尺寸、武器数量、秘密通道或工程参数。
- 游戏机制未写成世界内硬事实。
- 地点状态不覆盖封版时间线；跨时代变化仍以对应剧情块为准。

## 来源检查

本批以已封版主线、SideStory、正式人物与57条核心世界设定为施工锚点；来源优先级遵循 `docs/source-policy.md`。

重点锚点包括：
- `timeline/side/the-rides-to-lake-silberneherze.md`
- `timeline/side/hortus-de-escapismo.md`
- `timeline/side/inudi-harek-horakhet.md`
- `timeline/side/zhidao-dadi-biancheng-yike-suancheng.md`
- `timeline/side/near-light.md`
- `timeline/side/guiding-ahead.md`
- `timeline/side/heart-of-surging-flame.md`
- `timeline/side/zwillingsturme-im-herbst.md`
- `timeline/side/who-is-real.md`
- `timeline/side/paoying-cangting.md`
- `timeline/side/wuyou-mengyi.md`
- `timeline/side/cisui-xing.md`
- `timeline/side/babel.md`
- `timeline/side/terra-meal.md`
- `timeline/main/main-07.md`、`main-08.md`、`main-11.md`、`main-13.md`、`main-15.md`、`main-16.md`、`main-17.md`

## 封版资产保护

- timeline：未修改。
- worldbook/operators：未修改。
- worldbook/operator-moe：未修改。
- worldbook/npcs：未修改。
- manifest/character-weapon-audit.v1.json：未修改。
- worldbook/settings：未修改。
- manifest/world-settings.v1.json：未修改。
- media：未修改。
- 咩咩预设：未修改。

## 结论

Batch 03：PASS。

地点世界书主体：85 / 85，PASS，可进入全量封版状态。
