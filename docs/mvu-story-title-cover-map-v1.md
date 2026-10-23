# 《明日方舟》MVU 作战档案标题与封面映射 v1.0

## 定位

本层冻结 73 卷在 PRTS 作战档案中的正式显示名与媒体目标路径；世界书切换 marker、source、order 等仍由 `manifest/mvu-timeline-switch.v1.json` 管理。

- 主线：18 卷，MAIN-00～MAIN-17。
- SideStory：55 卷。
- 显示名机器索引：`manifest/mvu-story-media.v1.json`。
- 主线封面目标：`media/mvu/story/main/main-XX.webp`。
- SideStory 封面目标：`media/mvu/story/side/<slug>.webp`。

## 原则

1. 显示名使用游戏/PRTS正式中文名，不用英文 slug 直接展示。
2. 图片不进入角色卡/Base64；正式运行时只读本仓库镜像，经 jsDelivr CDN 懒加载。
3. PRTS仅作为素材核验/抓取源，不作为正式运行时图片依赖。
4. 主线源图按 `章节名称_<章节>.png` 核验；SideStory 从对应正式中文活动页核验原图。
5. 当前只把来源、标题和目标路径锁死；二进制未真正镜像前绝不标记 ready。
6. Swipe只预览当前/相邻封面，不切世界书；“进入本卷”仍使用既有73卷原子切换协议。

## 已核高风险命名

- `a-flurry-to-the-flame` → 落叶逐火（不是“春分”）。
- `paoying-cangting` → 泡影苍霆。
- `weixu-zhidi` → 未许之地。
- `wuyou-mengyi` → 无忧梦呓。
- `xueshan-jianglin-1101` → 雪山降临1101。
- `zwillingsturme-im-herbst` → 崔林特尔梅之金。

## 状态

- 73/73 正式显示名：完成。
- 73/73 目标 WebP 路径：完成。
- 主线 18/18 PRTS 章节源文件名：完成。
- SideStory 55/55 PRTS 中文活动页检索键：完成。
- WebP 二进制镜像：待下一媒体落地步骤；本轮不伪造完成状态。
