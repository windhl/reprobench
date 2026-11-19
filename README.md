# ReproBench

三个投稿版本各自保存正文、最终插图、实验结果和提交材料。当前正在准备 USENIX Security 2027；该版本尚未迁入研究正文。

| 版本 | 论文入口 | 实验快照 | 原始提交材料 |
| --- | --- | --- | --- |
| [AAAI 2027](versions/aaai-2027/README.md) | [main.tex](versions/aaai-2027/paper/main.tex) | [experiments](versions/aaai-2027/experiments/README.md) | [submission](versions/aaai-2027/submission/README.md) |
| [arXiv](versions/arxiv/README.md) | [main.tex](versions/arxiv/paper/main.tex) | [experiments](versions/arxiv/experiments/README.md) | [submission](versions/arxiv/submission/README.md) |
| [USENIX Security 2027](versions/usenix-security-2027/README.md) | [官方示例模板](versions/usenix-security-2027/paper/usenixsecurity2027.tex) | 尚未开展 | [模板及本地征稿说明](versions/usenix-security-2027/submission/README.md) |

AAAI 和 arXiv 的 `paper/` 均从整理前的当前工作区独立复制，保留当时的未提交修改。它们并非已核实的实际投稿原稿。原有 PDF、ZIP 保存在各版 `submission/`，不会被重新构建覆盖。

```text
versions/       每版独立的 paper、experiments、submission、notes 和 manifest.json
skills/         共用的评分与 ground truth 工具
scripts/        共用的构建、统计核对、导出和绘图工具
references/     参考论文、阅读总结和原始 AAAI 作者工具包
archive/        原始图稿工作区、旧脚本、安装副本和旧编译产物
docs/           整理记录、迁移清单和验证结果
build/          新生成的 PDF、日志和临时编译文件，Git 忽略
```

在本仓库根目录执行：

```sh
# AAAI：正文、独立附录和复现清单
bash compile.sh aaai-2027
# arXiv：含作者信息和附录的正文
bash compile.sh arxiv
# USENIX：目前仅构建官方示例模板
bash compile.sh usenix-security-2027
```

构建依赖 TeX Live 的 `pdflatex` 和 `bibtex`。USENIX 原始模板还依赖 `plainurl.bst`，本机目前缺少此文件，需补齐该 TeX 依赖后才能完成其参考文献编译。模板保持原样，未替换参考文献样式。

构建在 `build/<版本>/sources-*/` 的独立副本中进行，最终 PDF 写到 `build/<版本>/`。失败会返回非零状态，并保留日志；不会把旧 PDF 当成本次成功结果。也可以只构建某个目标：

```sh
python3 scripts/build_paper.py aaai-2027 main
```

统计核对及外部数据工具：

```sh
python3 scripts/verify_paper_numbers.py --version aaai-2027
python3 scripts/verify_paper_numbers.py --version arxiv

python3 scripts/extract_trace_tokens.py \
  --trace-root /实际路径/repro_trace --output-dir build/token-analysis
python3 scripts/export_evaluation_to_xlsx.py \
  --eval-root /实际路径/evaluation --output build/evaluation.xlsx
python3 scripts/plot_3d_method_trajectories.py \
  --summary versions/aaai-2027/experiments/results/evaluation_summary.txt \
  --metadata /实际路径/reprobench_cve_metadata.csv \
  --groundtruth /实际路径/repro_groundtruth \
  --output-dir build/phase-trajectories
```

导出工具需要 `openpyxl`；绘图工具需要 `matplotlib` 和 `numpy`。原始逐次评分 JSON、trace、固件和部分绘图元数据未包含在本仓库中，需显式提供外部路径。旧版漏洞类型分析脚本按原样归档在各版结果快照中，仍含历史绝对路径，暂不作为统一执行入口。

现有统计核对器内置的是旧稿期望值。两版均完成 136 项检查并报告 13 项差异；使用原脚本和兼容文件名复查得到相同结果，属于整理前已有的不一致。本次未调整论文数值或评分口径，详见 [验证记录](docs/VALIDATION.md)。

评分工具保留两个来源：仓库中的 `skills/reprobench-scoring/`，以及外层正在使用的安装副本 `../SKILL.md`、`../scripts/`。安装副本另在 `archive/installed-scoring-snapshot/` 留档。两份汇总脚本有实现差异，尚未确认历史结果由哪份生成，本次未合并或同步覆盖。

每个版本的 `manifest.json` 记录整理前的 Git 提交、工作区来源和尚未核实的实验归属。今后新增实验写入相应版本目录，重新生成的临时结果先写 `build/`，核对后再保存为版本快照。

完整备份、恢复方式和路径对应关系见 [整理记录](docs/REORGANIZATION.md)。
