# Arknights-Lore

《明日方舟》咩咩全栈角色卡的资料、世界书、剧情时间线与媒体资源仓库。

## 当前职责

仓库分为四类长期资产：

- **正式角色世界书源稿**：`worldbook/operators/`
- **剧情时间线远程资源**：`timeline/` + `runtime/`
- **MVU媒体资源**：`media/mvu/operators/`
- **索引、施工记录与QA**：`manifest/`、`build/`、`QA/`、`docs/`

## 核心原则

- 角色正文以 `worldbook/operators/<干员名>.md` 为可持续返修的唯一正式源。
- `build/character-worldbook/` 只保存批次施工记录、样板、QA与装配产物；Batch不是长期角色定位方式。
- 时间线按主线、SideStory、角色个人事件链拆分并按需加载，不与角色正文混为一层。
- MVU媒体独立维护，正式路径为 `media/mvu/operators/<干员名>/elite1.png` 与 `idle.gif`。
- `manifest/` 保存时间线、角色世界书、媒体等稳定索引。
- 不修改咩咩预设；MVU负责展示与轻交互，不作为剧情唯一事实源。
- 原始参考资料不作为正式正文直接镜像；正式条目必须经过整理、压缩与改写。

## 目录

- `worldbook/operators/`：正式干员角色与能力条目，一人一文件。
- `timeline/main/`：主线时间线。
- `timeline/side/`：SideStory时间线。
- `timeline/operator/`：角色个人剧情事件链。
- `runtime/`：剧情远程加载协议与卡侧约定。
- `media/mvu/operators/`：干员 Elite1 PNG 与 idle GIF。
- `manifest/`：剧情、角色世界书、媒体索引。
- `build/character-worldbook/`：角色批次施工与历史验收记录。
- `QA/`：全局验收记录。
- `reference/`：轻量参考索引/目录数据。
- `tools/`：资料与构建工具。
- `docs/`：施工规范、来源策略与版本说明。

## 当前状态

- 主线 + SideStory 时间线：已封版。
- 干员媒体：463/463 PNG + 463/463 GIF，媒体线封版。
- 干员角色主体精修：进行中；正式条目完成后直接进入 `worldbook/operators/`。
- 萌点专项：主体精修全部完成后再逐一补充。
