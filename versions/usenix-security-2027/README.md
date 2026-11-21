# USENIX Security 2027

此目录是新投稿版本的独立工作区。现已基于大纲 v2 和历史素材写成英文实证研究草稿，并核读、迁入适合复用的旧图表，保留官方 `usenix.sty` 的格式设置。

## 当前草稿

- [当前完整 PDF：20 页](submission/drafts/reprobench-usenix27-with-figures-2026-11-20.pdf)：正文 13 页、参考文献 2 页、附录 5 页；含 3 图、5 表。
- [当前仅正文 PDF：13 页](submission/drafts/reprobench-usenix27-main-13pages-2026-11-20.pdf)：供逐页审阅；引用、原始提示词图和完整案例表见完整版本。
- [LaTeX 主文件](paper/usenixsecurity2027.tex)，章节源文件位于 `paper/sections/`。
- [43 项 TODO 清单](notes/draft-todos-2026-11-20.md)：区分研究必需工作、条件性补实验及成稿/投稿事项。
- [旧图表核读、复用与论述作用](notes/visual-reuse-2026-11-20.md)：含六张旧图和全部旧表的处理理由。
- [11/19 首稿说明](notes/draft-status-2026-11-19.md)及[当时完整 PDF](submission/drafts/reprobench-usenix27-draft-2026-11-19.pdf)：保留作对照。

草稿采用结果、障碍、应对行为三个递进 RQ，不使用加权评分。当前包含历史注释统计和已核读的案例产物；完整结果核验、轨迹编码和最终科学发现仍以 TODO 标明，没有新增 agent 实验。它是供作者审阅的工作稿，尚非投稿定稿。

本次直接复用原始提示词 PDF，改绘旧框架与案例图，改写六类活动/证据检查表、触发证据表及完整案例元数据表。未把旧阶段评分曲线、漏斗或分数排名转写成新结果。

## 构建

从仓库根目录运行：

```sh
bash compile.sh usenix-security-2027
```

构建输出位于 `build/usenix-security-2027/usenixsecurity2027.pdf`。当前采用本机可用的 `plain.bst` 并在引用字段中保留来源链接，解决原示例依赖 `plainurl.bst` 缺失的问题；未修改官方页面尺寸、字体、行距、页边距或标题/作者块。原始官方示例完整保存在 `submission/usenixsecurity2027_latex_templates.zip`。

正文放 `paper/`，历史材料清单与后续分析放 `experiments/`，讨论与待办放 `notes/`，审阅快照放 `submission/drafts/`。
