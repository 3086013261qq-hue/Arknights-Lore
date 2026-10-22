# Worldbook

本目录保存《明日方舟》角色卡中需要长期维护、可直接返修的正式世界书源稿。

## 角色正式源

- `operators/<干员名>.md`：每名干员一份唯一正式最新版。
- 文件内同时保存 `<角色名character>` 与 `<核心设定:角色名·能力>`。
- 后续发现人物、视觉、关系、心理模型或能力表达需要修正时，直接修改该角色文件，不回头修改历史 Batch。
- `manifest/operator-worldbook.v1.json` 记录已进入正式源的角色、媒体路径与精修状态。

## 与 build 的关系

`build/character-worldbook/` 仅保存批次施工记录、QA、历史样板与装配产物，不再作为角色正文的长期唯一来源。

## 与 media 的关系

媒体已封版，角色文件通过同名路径关联：
- `media/mvu/operators/<干员名>/elite1.png`
- `media/mvu/operators/<干员名>/idle.gif`

角色返修不得因此重新生成或重命名媒体。
