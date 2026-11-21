# 英文草稿说明

这是 11/19 首稿的历史状态。当前带复用图表的版本见[11/20 图表复用说明](visual-reuse-2026-11-20.md)；下列首稿 PDF 快照保留，LaTeX 工作文件已继续更新。

本次根据作者要求，将大纲 v2 写成可编译的 USENIX Security 2027 英文草稿。正文 13 页；完整 PDF 18 页，含 2 页参考文献与各 1 页伦理、Open Science、补充材料。当前有 28 条参考文献、43 项可见 TODO。

## 阅读入口

- [完整草稿](../submission/drafts/reprobench-usenix27-draft-2026-11-19.pdf)
- [仅正文 13 页](../submission/drafts/reprobench-usenix27-main-13pages-2026-11-19.pdf)
- [LaTeX](../paper/usenixsecurity2027.tex)
- [待办清单](draft-todos-2026-11-19.md)

## 使用的材料和边界

沿用旧稿中的任务定义、历史 30×5×3 设计、提示/主机/容器描述、公开参考材料和案例。保留实际五个模型 route 标签，不将 `free` 后缀擅自去除。取消论文中的 Plan/Task/Overall 加权评分；原始实验曾要求计划和报告，这一事实保留。

参考文献结合两轮本地阅读材料，正式发表身份与预印本身份分开。使用本机已安装的 `plain.bst`，引用条目中显式保留来源链接；修正了迁入条目中明显无意义的页码、标题转义及部分年份，不批量复制旧稿全部 bibliography。

对历史归档执行只读 inventory，记录 450 个 JSON 的哈希和运行级目录状态。计数用于描述“历史标签”和“文件可用性”，不是人工验证的结果。

草稿没有将旧稿的 5.3% 直接称为已验证成功率，也没有将 45.3% 直接称为实际模拟发生率。当前 JSON 的标签查询得到 316 次任一 simulation、209 次任一 terminal simulation；旧稿 terminal 204 的差异留作 RQ3-02。没有为了凑结果而重跑 judge。

核读了以下三组原始 workspace/相关日志，未执行其中代码：

1. CVE-2023-26315 / claude-sonnet-4-6 / 1：报告、保存的 PoC 执行输出、服务链日志与 trace metadata。原始组件执行的候选证据与直接组件入口的范围区别写入正文；完整身份/触发重放仍为 TODO。
2. CVE-2024-23624 / glm-5.2 / 2：固件/反汇编产物、Ghidra 脚本；确认保存的脚本含拼写错误，但 trace 为空，不能据此断定实际异常顺序和停止原因。
3. CVE-2020-27866 / claude-sonnet-4-6 / 1：计划、Python 替代服务、测试输出；明确保留 agent 自己说明 simulation 的事实，不能写成其隐瞒模拟。空 trace 也不证明从未尝试过下载。

这三组是说明证据边界的案例，不是已经完成跨案例标注的代表性抽样。全文的核心跨案例 findings 仍需重新分析后写入。

## TODO 的含义

- AUD、DES、CASE、COD、ANA、RQ 和 VAL：建立可信研究结论需要的核验、标注或统计；部分任务可能需要针对性重放。
- EXP-01/02/03：条件性补实验，分别检验环境就绪、提示词说明、第二 harness。可以选择不做并收窄结论，不能把预期效果写成已验证。
- ABS、INTRO、DISC、CONC：在发现明确后重写摘要、贡献与解释。
- ETH、OS、SUP：记录真实安全措施、匿名访问地址和实际可共享材料，未虚构已完成的隔离审计或公开发布。

## 格式及构建检查

依据本地保存的 CFP、官方模板，以及 [2026-11-09 修订 CFP](https://www.usenix.org/sites/default/files/sec27_cfp_110926.pdf) 的格式、匿名和开放科学要求。保留官方 `usenix.sty` 原文件；letter 双栏、10pt、官方 7×9 英寸正文区域，保留作者块与标题区域，没有负间距或改字体挤页。

正文结束于第 13 页；References 从第 14 页开始；Ethical Considerations、Open Science 和 Supplementary Evidence 分别从第 16、17、18 页开始。后两份审阅 PDF 分别为完整稿和正文导出，不是两套实验版本。

通过三遍 pdfLaTeX 与 BibTeX 构建；未发现未定义引用或 Overfull 内容。字体全部嵌入，无 Type 3 字体。已检查全稿页面缩略图、主文末页和图表；示意图和表格以黑白为主。仍有官方包常见提示及少量 Underfull 排版提示，不影响构建。

草稿 PDF 的作者 metadata 为空，正文保留匿名作者区域，没有写入本机绝对数据路径。该检查不是完整投稿匿名化审计；artifact 仍未发布，需完成 OS 系列 TODO。

原始模板 ZIP、两个历史论文版本及其数据未改动。当前稿是带待办的内部审阅版本，完成 TODO 与作者审查之前不能视为可提交的定稿。
