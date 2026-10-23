# MVU Story Cover Media

《明日方舟》PRTS 作战档案媒体目录。

- 主线：`media/mvu/story/main/main-00.webp` ～ `main-17.webp`。
- SideStory：`media/mvu/story/side/<timeline-slug>.webp`。
- 73卷正式显示名/来源键：`manifest/mvu-story-media.v1.json`。
- 世界书切换结构：`manifest/mvu-timeline-switch.v1.json`。

规则：
1. 正式 MVU 只通过本仓库的 jsDelivr CDN 加载图片；
2. 不把图片/Base64写进角色卡；
3. PRTS只用于核对/抓取源素材，不作为运行时媒体依赖；
4. 上传前统一转 WebP，并保留宽高比；
5. Swipe 时只懒加载当前卷与相邻卷；
6. 缺图时回退纯文字/默认框，不得阻断世界书切卷；
7. 只有仓库文件实际存在并完成CDN验收后，媒体状态才可标记 ready。

当前：73/73标题与目标路径已冻结；二进制镜像待完成。
