# Character Worldbook Build Records

本目录是角色世界书的施工与验收记录层，不是角色正文的长期唯一事实源。

- `batch_CORE_01/`：早期核心样板批次，保留作历史基准。
- `batch_OPERATOR_REFINEMENT_01/`：Operator Refinement Batch 01 的施工/QA记录。
- 后续 Batch 可继续在此记录范围、QA、冲突与统计。

正式可持续返修的角色正文统一保存于：
`worldbook/operators/<干员名>.md`

规则：
1. Batch 完成后，将对应角色独立文件写入 `worldbook/operators/`。
2. 后续单人返修只改正式角色文件，并同步 `manifest/operator-worldbook.v1.json` 的状态/版本信息（如需要）。
3. 不要求为一次单人返修重新生成整个 Batch。
4. 时间线、媒体与角色正文分别维护，互不做无关重建。
