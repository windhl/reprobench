# 实验快照

`results/` 是整理前共用 `data/` 的完整独立副本；AAAI 与 arXiv 最初内容相同，并不代表两次独立实验。逐次评分 JSON、trace 和固件位于仓库外部，未随快照包含。与实际投稿采用数据的对应关系尚待核实。

`results/analysis_by_vultype_v1/` 和 `v2/` 保留原始分析脚本及输出，其中脚本仍使用历史绝对路径，作为溯源材料保留。共用的维护入口在仓库根 `scripts/`，参数用法见根 README。

`phase-trajectories/` 保存整理前四面板轨迹图的输出、CSV 和说明；原 README 中的路径属于历史记录。完整原件含脚本保存在 `archive/figure-workspace/3d_method_trajectories/`。论文实际引用的 `3d.pdf` 保持原样，未用该目录中的其他 PDF 替换。

现有统计核对器报告的 13 项差异在旧工具复查中同样存在，详见 `docs/VALIDATION.md`；不要在未核实评分来源前直接重算并覆盖历史结果。
