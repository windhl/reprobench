# 整理后的验证

日期：2026-11-19。

| 检查 | 结果 |
| --- | --- |
| 整理前完整备份 | 1,586 个条目、1,269 个普通文件；归档内容逐项校验通过 |
| 备份持久副本 | `../backups/20261119-173001/`（相对仓库根）；SHA-256 与原归档一致 |
| 实际解压恢复 | 见 [backup-restore.json](validation/backup-restore.json) |
| 迁移内容核对 | 397 个非 Git 文件均在新目录中找到 SHA-256 一致的内容，见 [迁移清单](migration-inventory.json) |
| AAAI 构建 | 正文、独立附录、复现清单三份 PDF 均编译成功 |
| arXiv 构建 | 含附录的正文编译成功 |
| USENIX 示例构建 | pdflatex 成功；BibTeX 因本机缺少 `plainurl.bst` 返回非零状态，未发布最终构建 PDF |
| 两版正文依赖 | 各自的章节与图表引用均存在，无跨版本共享正文或图表 |
| 共用 Python 脚本 | 语法解析及命令行帮助检查通过 |
| 维护代码与新增说明的空白检查 | 通过；历史稿件、原始模板及参考论文源码保留原有空白格式 |

AAAI 与 arXiv 均使用完全保留的当前工作区稿件构建。构建成功不代表格式或统计内容已满足投稿要求；历史提交 PDF、ZIP 未覆盖。

统计核对结果：

- [AAAI 核对报告](validation/aaai-paper-numbers.txt)：136 项检查，13 项差异。
- [arXiv 核对报告](validation/arxiv-paper-numbers.txt)：相同的 13 项差异。
- [原脚本兼容路径复查](validation/original-verifier-compatible-paths.txt)：只在临时目录为旧章节名提供别名，原脚本未修改，报告相同的 13 项差异。
- [原脚本初始运行](validation/original-verifier-before-path-fix.txt)：原来直接运行会因 `502-failure.tex` 不存在而中止。

差异包括部分漏洞类型均分、若干旧稿文本期望值和案例计数。核对器本身包含硬编码旧值，报告不能直接用于判定论文或数据哪一方正确。此次只修复路径入口和三个旧章节文件名，没有更改评分规则、期望值、论文数值或结果快照。

外部逐次评分 JSON、trace、ground truth 和 CVE 元数据不在当前仓库内，因此没有重新评分、提取全部 trace 或重新绘制依赖这些数据的轨迹图。旧输出保留，维护脚本要求显式提供缺失的外部数据。
