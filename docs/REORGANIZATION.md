# 目录整理记录

整理日期：2026-11-19。整理前内层 Git 提交：`dc709b2`。保留原工作区未提交内容；未提交、推送或改写 Git 历史。

完整备份在外层 `backups/20261119-173001/`，其中：

- `reprobench-scoring.tar.gz`：整理前整个外层目录，包含隐藏文件、内层 `.git` 和所有未提交文件，约 297 MiB。
- `manifest.json`：整理前 1,586 个文件和目录条目，包括 1,269 个普通文件的 SHA-256。
- `SHA256SUMS`：归档校验值。
- `RESTORE.txt`：恢复命令。

归档生成后逐文件校验了内容和权限；复制到上述持久目录后再次校验归档 SHA-256。`/tmp/reprobench-scoring-backup-20261119-173001/` 也保留了一份。

从外层工作目录检查备份并恢复到独立空目录：

```sh
(cd backups/20261119-173001 && sha256sum -c SHA256SUMS)
mkdir -p /tmp/reprobench-scoring-restored
tar --acls --xattrs -xzpf backups/20261119-173001/reprobench-scoring.tar.gz \
  -C /tmp/reprobench-scoring-restored
```

恢复后的完整旧工作区在 `/tmp/reprobench-scoring-restored/reprobench-scoring/`。先在该目录核对文件，再决定是否替换当前目录。

| 整理前路径（相对外层目录） | 整理后路径 |
| --- | --- |
| `reprobench/reprobench.tex` | `reprobench/versions/aaai-2027/paper/main.tex` |
| `reprobench/reprobench_arxiv.tex` | `reprobench/versions/arxiv/paper/main.tex` |
| `reprobench/sections/`、`aaai2027.*` | 两版各自的 `paper/`，互相独立 |
| `reprobench/data/` | 两版各自的 `experiments/results/`，内容相同的历史快照 |
| `reprobench/figures/` | `reprobench/archive/figure-workspace/`；论文引用图另复制进各版 `paper/figures/` |
| `reprobench/figures/3d_method_trajectories/` | 完整原件随图稿归档；输出另存各版 `experiments/phase-trajectories/`，维护的绘图脚本在 `scripts/` |
| 根目录 PDF、arXiv ZIP | 相应版本 `submission/`，保留原文件名和字节内容 |
| `260925-AAAI-review.txt`、`AAAI-submission-instructions.txt` | AAAI `submission/` |
| `reprobench/usenix_security_2027/` | USENIX `submission/`；模板另原样解压到 `paper/` |
| `ref/` | `reprobench/references/papers/` |
| `AuthorKit27/`、`AuthorKit27.zip` | `reprobench/references/templates/aaai-2027/` |
| `reprobench/bench-paper/` | `reprobench/references/summaries/` |
| 外层 `SKILL.md`、`scripts/` | 原地保留，并在内层 `archive/installed-scoring-snapshot/` 留档 |

本次仅调整目录、构建与路径入口。未改变论文文字、图表内容、实验数据或评分规则。USENIX 只建立模板工作区，没有虚构或自动改写研究正文。

共用脚本的调整包括：按版本定位正文和结果；修正统计核对器沿用的三个旧章节文件名；trace 和 Excel 工具显式接收外部数据目录；绘图工具显式接收未随仓库提供的元数据与 ground truth。原脚本均已留档。

尚未核实的事项：AAAI 实际提交对应哪个 Git 版本；arXiv ZIP 的正式上传版本号；两份汇总脚本分别与哪些历史结果对应。三个版本的 `manifest.json` 明确记录这些来源限制，避免把当前工作副本误标为已确认的投稿原稿。

逐文件迁移结果见 `migration-inventory.json`；验证结果见 [VALIDATION.md](VALIDATION.md)。
