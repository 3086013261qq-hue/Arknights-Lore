# 《明日方舟》MVU 咩咩原生状态桥规范 v1.0

> 本规范修复实机候选02中 `TIME / WORLD` 长期显示“待记录”，以及由此导致 MAIN 沙盒自动衔接无法触发的问题。
> 这是运行时桥接修正，不修改剧情、时间线、角色、媒体或咩咩预设。

## 1. 已确认根因

候选02当前 PRTS 运行时通过 `getChatMessages()` 扫描助手正文中的 `<status>...</status>` 文本，再用正则读取时间/阶段。

实机已经证明：咩咩自己的“世界运行报告”能够正确显示当前时间、事件与位置，但这些真实状态不保证以 PRTS 期待的 `<status>` 文本出现在助手消息正文中。

因此：

- 咩咩状态真实存在；
- PRTS读取源错误；
- 继续强化 `<status>` 提示词不能从根本解决；
- MAIN沙盒自动衔接若继续依赖助手正文 `<status>`，将不可靠或永远不触发。

## 2. 唯一正确方向

PRTS必须直接继承旧成熟卡已经验证的咩咩原生变量桥。

读取优先级固定为：

1. `Mvu.getMvuData({type:'message', message_id})`
2. `getVariables({type:'message', message_id})`
3. 仅在前两者均不可用时，才允许解析当前消息正文 `<status>` 作为降级 fallback
4. 三层均失败才显示“待记录”

禁止把“扫描助手消息文本”继续作为主数据源。

## 3. 当前消息绑定

状态必须绑定到**当前 PRTS 所属的最新有效消息 / 当前消息ID**，沿用成熟桥：

- 优先 `getCurrentMessageId()`；
- 若 iframe 环境无该接口，则从当前 iframe / `.mes[mesid]` 取得所属消息ID；
- 不扫描整个历史聊天寻找“最近看起来像状态”的文本作为主真值；
- Swipe后重新读取新的当前消息变量；
- 切聊天后清空旧消息缓存。

## 4. 原生状态适配器

静静必须先读取候选02实机中 `Mvu.getMvuData` / `getVariables` 返回的真实对象结构，再写一个**单一 adapter**，将咩咩原生状态投影为：

```js
{
  time: string,
  location: string,
  stage: string,
  objective: string,
  activeVolume: string | null,
  relationSource: object | string | null,
  raw: object
}
```

注意：

- 不允许根据猜测硬编码不存在的变量路径；
- 先在实机/酒馆助手变量对象中确认字段，再映射；
- Adapter只读，不回写咩咩时间/阶段；
- PRTS不创建第二份时间、阶段或当前卷变量。

## 5. TIME / LOCATION / WORLD / OBJECTIVE

### TIME

优先读取咩咩原生世界时间。

实机世界运行报告已经能展示类似：

`1096年12月23日 / 14:15 / 星期四`

PRTS必须显示同一事实源，而不是再次让模型生成时间文本。

### LOCATION

同样读取咩咩原生当前位置；如果现有LOCATION已经稳定，可保留现有适配，但最终仍应统一经过同一个 native adapter。

### WORLD / 阶段

优先读取咩咩原生剧情/事件阶段。

若原生状态对象没有独立阶段字段，但拥有世界运行报告中的当前事件信息，则由 adapter 只读组合显示，例如：

`MAIN-00 / 事件C / 0-1《坍塌》·行动前`

这里只做显示投影，不创建持久阶段变量。

### OBJECTIVE

优先读取咩咩原生任务/进度；没有任务时显示“无”。

## 6. 当前行动 ACTIVE

当前卷仍然保持原规则：

- 唯一 enabled 的 `ARKNIGHTS_TIMELINE:*` 世界书条目是当前卷唯一事实源；
- native adapter中的 `activeVolume` 只用于交叉校验；
- 如果咩咩状态与世界书 ACTIVE 不一致，PRTS显示警告，不擅自覆盖其中任何一方。

## 7. MAIN 沙盒自动衔接必须改用 native adapter

候选02现有 `createMainSandboxAdvance()` 通过最新助手消息 `<status>` 判断：

- 当前行动是否为 MAIN-XX；
- 世界/剧情阶段是否为“沙盒模式”。

这一判断必须替换为：

1. 读取唯一 enabled MAIN卷；
2. 从当前消息的咩咩原生状态对象读取当前阶段；
3. 当前阶段明确等于：
   - `沙盒模式`
   - `本卷已完成`
   - `SANDBOX`
   或静静在实际变量对象中确认的等价正式值；
4. 当前active MAIN必须与状态对象归属一致；
5. 然后复用原有串行世界书切卷事务进入下一MAIN。

**禁止再以助手正文 `<status>` 作为自动切卷主触发源。**

## 8. MAIN-17 / SideStory

保持原设计不变：

- MAIN-00～MAIN-16：当前原生阶段进入沙盒后自动衔接下一MAIN；
- MAIN-17：进入沙盒后停留，显示 `MAIN STORY COMPLETE / SANDBOX`；
- 所有SideStory：不自动串联。

## 9. 实时刷新

沿用成熟咩咩桥已经验证的事件刷新机制。

至少监听：

- `mag_variable_initialized`
- `mag_variable_update_ended`

并结合酒馆消息事件：

- `MESSAGE_UPDATED`
- `MESSAGE_SWIPED`
- `CHARACTER_MESSAGE_RENDERED`
- `CHAT_CHANGED`

要求：

- 变量更新后立即刷新TIME/WORLD；
- 不等待用户关闭重开PRTS；
- 事件绑定必须幂等；
- DOM重绘后恢复，但不得重复listener；
- 可保留低频定时刷新作为兜底，但不能把轮询作为唯一同步方式。

## 10. 正文 `<status>` 的新定位

`<status>` 不删除，但降级为：

- 模型可读/可见的文本状态输出；
- 原生变量接口不可用时的兼容fallback；
- 调试与QA辅助。

它不再承担：

- PRTS TIME唯一来源；
- PRTS WORLD唯一来源；
- MAIN沙盒自动衔接主触发器。

## 11. 禁止事项

- 禁止继续只靠 `getChatMessages()` 扫 `<status>`；
- 禁止为了修TIME/WORLD再增加一套 `_current_time` / `_world_stage` 持久变量；
- 禁止让PRTS反向覆盖咩咩原生时间；
- 禁止扫描历史消息中的旧“沙盒模式”触发切卷；
- 禁止从时间线日期猜“当前已经到沙盒”；
- 禁止因为状态接口短暂未初始化就把已确认状态永久重置为“待记录”。

## 12. 实机QA硬门槛

静静下一候选必须在真实 Android / SillyTavern 中验证：

- [ ] 咩咩世界运行报告显示时间后，PRTS TIME同步显示同一时间；
- [ ] 咩咩事件阶段变化后，PRTS WORLD同步变化；
- [ ] 刷新PRTS、折叠/展开悬浮窗后TIME/WORLD不丢；
- [ ] Swipe到新回复后读取新消息变量；
- [ ] 当前消息没有正文 `<status>` 时，TIME/WORLD仍能正常显示；
- [ ] 临时禁用Mvu主接口后，`getVariables` fallback可工作；
- [ ] 两个变量接口都不可用时才允许回退正文 `<status>`；
- [ ] MAIN-00～16在原生阶段进入沙盒后只自动切一次；
- [ ] 历史消息里的沙盒不会触发；
- [ ] MAIN-17不自动切卷；
- [ ] SideStory不自动切卷；
- [ ] 自动切卷后仍恰好1/73 enabled；
- [ ] 写入失败不假成功。

本项全部PASS前，不得把主线自动衔接标为正式完成。
