# USENIX Security 2027

当前标题：**Can LLM Agents Reproduce Vulnerabilities from Scratch? An Empirical Study on IoT Firmware**。

2026-11-23 按作者审阅意见，以 arXiv 旧稿为底稿恢复方法、实验和主要分析，局部调整为实证研究叙事。AAAI 和 arXiv 版本保持原样；官方 `usenix.sty` 未修改。

## 当前审阅稿

- [完整 PDF](../../build/usenix-security-2027/usenixsecurity2027.pdf)：本地构建产物，Git 忽略。
- [LaTeX 入口](paper/usenixsecurity2027.tex)：以入口中的 `input` 列表为当前有效正文；未被引用的前版章节保留作历史参考。
- [原底稿](../arxiv/paper/main.tex)：保留选例、reference profile、Plan/Task/Overall 公式、模型汇总、PSC 案例、漏洞类别分析、失败统计及评分附录。
- [11/20 的前版完整 PDF](submission/drafts/reprobench-usenix27-with-figures-2026-11-20.pdf)：属于较大幅度重写的历史快照，不再代表当前稿。

当前正文依次为 Introduction、Background and Related Work、Study Design and Methodology、Experimental Setup、Empirical Results、Discussion、Conclusion。三个 RQ 分别对应总体结果、阶段与类别差异、失败行为；ReproBench 是计划公开的研究材料与工具资源。实际公开范围见 Open Science 附录。

六阶段评分、原始模型汇总表、框架图、阶段得分曲线和漏斗继续使用。旧 iceberg 图局部改为任务起点示意，避免概括全部既有工作。提示词原图在附录保留；旧评分 checklist、attempt、trigger、failure taxonomy、三个案例分数及成本表恢复为附录，已修正错误 CVE 图注和 taxonomy 实际列出的 12 种模式数量。

## 尚需核验的信息

当前没有新增 agent 运行，也没有重新评分。保留数字是旧 rubric 下的历史测量，不等同于独立验证的端到端成功率。

- AUD-01：16 个触发候选的目标身份、效果归因和组件／公开入口范围。
- NUM-01：旧稿 204 次 terminal simulation 与当前清单 209 次的口径差异；316 次是 any-simulation 查询。
- NUM-02：369 条成本记录与 395 个非空 trace 目录的覆盖差异，以及计费、时间和超预算记录。
- CONFIG-01：历史工具版本、model route、实际输入和预算执行方式。
- Ethics / Open Science 附录保留实际安全措施和共享材料的待核查事项。

[11/20 的 43 项 TODO](notes/draft-todos-2026-11-20.md)及[当时的图表迁移说明](notes/visual-reuse-2026-11-20.md)只对应历史重写稿。

## 构建

```sh
python scripts/build_paper.py usenix-security-2027
```

输出位于 `build/usenix-security-2027/usenixsecurity2027.pdf`，构建日志保存在同目录下的 `sources-*`。11/23 修改前的论文源文件另备份在 `build/usenix-security-2027/before-local-revision-2026-11-23.zip`。构建不会覆盖各版 `submission/` 中的历史 PDF。
