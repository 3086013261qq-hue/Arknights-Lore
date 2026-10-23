# 《明日方舟》MVU 主线沙盒自动衔接规范 v1.2

> 本文件只定义 MAIN-00～MAIN-17 的自动衔接。
> SideStory 全部禁止自动串联。
> v1.2 新增：**切卷后一次性 Event A 交接锁（MAIN_HANDOFF）**，防止上一卷沙盒状态污染下一卷并产生连续跳卷。

## 1. 目标

主线每卷最后都有 `沙盒模式`。当前 MAIN 进入“沙盒模式过渡 / 沙盒模式”后，MVU自动切到下一 MAIN。

但切卷成功不等于新卷已经开始。切卷后必须进入一次性交接阶段：

1. 下一轮剧情**必须从新卷事件A开始**；
2. 上一卷的沙盒 / wlog / current stage 立即视为过期，不得继承；
3. 在新卷事件A真正出现之前，自动切卷保持 DISARMED；
4. 只有确认新卷已经进入正式事件后，才重新 ARMED。

序列：
- MAIN-00 -> MAIN-01
- MAIN-01 -> MAIN-02
- ...
- MAIN-16 -> MAIN-17
- MAIN-17 -> 最终沙盒，不再自动切卷

---

## 2. 沙盒触发来源

只允许当前最新消息作为触发证据，优先级：

1. `Mvu.getMvuData({type:'message', message_id})`
2. `getVariables({type:'message', message_id})`
3. 当前最新消息中的咩咩世界运行报告 / `<wlog>` / 当前剧情阶段文本

普通历史正文、旧楼层、旧 assistant message 中的沙盒字样一律无资格触发。

### 可触发状态

- `沙盒模式过渡`
- `至 沙盒模式过渡`
- `进入沙盒模式`
- `沙盒模式`
- `本卷已完成`
- `SANDBOX`

推荐识别：

`/(?:至\s*)?沙盒模式(?:过渡)?|进入沙盒模式|本卷已完成|SANDBOX/i`

---

## 3. 第一次自动切换条件

必须同时满足：

1. 73条 `ARKNIGHTS_TIMELINE:*` 中恰好1条 enabled；
2. enabled 条目是 MAIN-00～MAIN-16；
3. 当前最新消息明确命中沙盒/过渡状态；
4. 若原生对象明确给出 MAIN-XX，必须与 enabled MAIN 一致；
5. 若报告未写 MAIN-XX，可用唯一 enabled MAIN 确认归属；
6. 当前 `(chat/context, message_id, active MAIN)` 尚未消费；
7. **MAIN_HANDOFF 当前必须为 disabled**。

MAIN_HANDOFF 开启期间，任何沙盒文本都不能再次触发自动切卷。

---

## 4. 切卷事务 + MAIN_HANDOFF

自动从 MAIN-X 切至 MAIN-Y 时，复用现有成熟世界书串行事务，并在**同一次 writeback**中完成：

1. 73条时间线全部 disabled；
2. 只启用目标 `MAIN-Y`；
3. 启用非时间线控制条目 `【ARKNIGHTS_MAIN_HANDOFF】`；
4. 一次性写回；
5. 写回成功后重读世界书；
6. 必须仍然恰好1/73时间线 enabled；
7. UI ACTIVE 更新为 MAIN-Y；
8. 自动切卷状态进入 `DISARMED_AWAITING_EVENT_A`。

`ARKNIGHTS_MAIN_HANDOFF`：

- 不属于73条时间线；
- 不代表剧情事实；
- 不属于咩咩游戏状态；
- 不建立 `_current_volume`；
- 只是一枚一次性、模型可见的“新卷起始握手”控制标记。

其源文件：`worldbook/runtime/main-handoff.md`。

---

## 5. 下一轮必须从 Event A 开始

只要 `ARKNIGHTS_MAIN_HANDOFF` enabled，下一次模型生成必须遵守：

1. 当前唯一 enabled `ARKNIGHTS_TIMELINE:MAIN-Y` 就是新卷事实源；
2. 上一条消息中的 `沙盒模式 / 沙盒模式过渡 / ∞` 全部属于上一卷，立即失效；
3. **世界主线必须从当前 MAIN-Y 的第一个正式事件 `事件A` 开始**；
4. 不得继续输出上一卷 `事件L/I/...: 沙盒模式`；
5. 不得跳过事件A直接进入B/C/沙盒；
6. 当前时间必须采用 MAIN-Y 事件A自身已经核定的时间锚点；
7. 若事件A只有相对时间，则按该事件前置规则推进，不继承旧沙盒无限时间；
8. `<wlog>` 的【世界主线】必须写成新卷事件A，而不是旧沙盒；
9. `<story_driver>` 的【世界主线】必须与同一事件A一致。

这是硬规则，不允许“为了连续性”保留上一卷沙盒。

### 示例

上一条：
`MAIN-00 / 事件L: 沙盒模式`

MVU切卷：
`MAIN-00 disabled -> MAIN-01 enabled + MAIN_HANDOFF enabled`

下一轮必须：
`MAIN-01 / 事件A: 1-1《孤岛》·行动前 ...`

禁止：
`MAIN-01 ACTIVE + 事件L: 沙盒模式`

---

## 6. Event A 确认与重新武装

MVU在后续最新 assistant message 中确认以下条件后，才允许结束交接：

1. MAIN_HANDOFF 仍 enabled；
2. 当前唯一 enabled MAIN 与切换后的目标卷一致；
3. 当前最新消息的世界主线明确是该卷的 `事件A`（允许 `事件A1` 仅在同一轮已经明确先进入A的情况下出现）；
4. 当前阶段**不包含** `沙盒模式 / 沙盒模式过渡 / 本卷已完成 / SANDBOX`。

确认成功后：

1. 仅把 `ARKNIGHTS_MAIN_HANDOFF` disabled；
2. 不改当前 MAIN；
3. 不改剧情变量；
4. 自动切卷重新进入 `ARMED`。

如果下一轮仍错误输出沙盒：

- MAIN_HANDOFF 保持 enabled；
- 当前 MAIN 保持不变；
- 自动切卷继续 DISARMED；
- 绝不允许继续跳到下一 MAIN；
- 下一轮仍要求从事件A开始。

---

## 7. 防连续跳卷硬规则

以下情况全部禁止自动切卷：

- MAIN_HANDOFF enabled；
- 当前 active MAIN 是刚刚自动切换得到的新卷，但尚未确认事件A；
- 最新 wlog 仍在复述上一卷沙盒；
- 最新消息只是重新渲染 / Swipe / 历史消息；
- 当前 MAIN 与原生显式 MAIN 不一致；
- 0条或多于1条时间线 enabled；
- SideStory；
- MAIN-17。

**不得因为“当前 enabled MAIN 已经变成下一卷”就把同一个/下一条遗留沙盒报告解释为新卷已完成。**

---

## 8. SideStory

55个 SideStory 全部保持手动切换。

- 沙盒后不自动下一卷；
- 不使用 MAIN_HANDOFF 自动串联；
- manifest数组顺序不等于时间顺序。

---

## 9. MAIN-17

MAIN-17进入沙盒/过渡后：

- 不自动切卷；
- MAIN-17保持唯一 enabled；
- 显示 `MAIN STORY COMPLETE / SANDBOX`；
- 不启用 MAIN_HANDOFF。

---

## 10. QA

- [ ] MAIN-00沙盒可切到MAIN-01；
- [ ] 切到MAIN-01的同一次writeback启用MAIN_HANDOFF；
- [ ] MAIN_HANDOFF期间自动切卷为DISARMED；
- [ ] 上一卷沙盒wlog不能把MAIN-01继续切到MAIN-02；
- [ ] 下一轮强制从MAIN-01事件A开始；
- [ ] Event A使用自身时间锚点，不继承旧沙盒∞；
- [ ] Event A确认后MAIN_HANDOFF自动关闭；
- [ ] 关闭HANDOFF后才重新ARMED；
- [ ] 如果模型错误继续输出沙盒，保持当前卷并继续要求A，不连跳；
- [ ] 自动切换后始终恰好1/73时间线enabled；
- [ ] 历史沙盒、Swipe、重绘不触发；
- [ ] SideStory不自动切；
- [ ] MAIN-17不自动切；
- [ ] 不新增持久 `_current_volume` 或第二套剧情状态。
