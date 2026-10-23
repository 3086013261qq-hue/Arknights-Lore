# QA — MVU 作战档案标题/封面映射 v1

结果：**PASS（标题/路径层）**；**MEDIA MIRROR PENDING（二进制层）**。

- [x] 总卷数 73 = 主线18 + SideStory55。
- [x] 73/73 正式中文显示名已填写。
- [x] 73/73 与 switch manifest 的稳定 ID 可一一连接。
- [x] 73/73 仓库目标 WebP 路径可确定。
- [x] 主线18卷 PRTS `章节名称_<章节>.png` 源文件名已解析。
- [x] SideStory55卷已绑定正式中文活动名，可按对应 PRTS 活动页继续核原图。
- [x] 卡本体不嵌入图片/Base64。
- [x] 正式运行时媒体源限定为仓库镜像 + jsDelivr。
- [x] 未修改任何封版 timeline 正文、角色、地点、设定或既有干员媒体。
- [ ] 73张 WebP 二进制镜像完成。
- [ ] 73/73 CDN可访问性、Content-Type、尺寸与失败回退验收。

当前媒体 manifest 必须保持 `binary_ready=0`，直到实际文件存在后才能提升状态。
