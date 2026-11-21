# 参考资料

- `papers/`：原外层 `ref/`，保留参考论文 PDF、源码和原始 ZIP。
- `summaries/`：原 `bench-paper/`，保留文献阅读总结。
- `templates/aaai-2027/`：原始 `AuthorKit27/` 和 ZIP。
- [positioning-study-2026-11-19/](positioning-study-2026-11-19/README.md)：benchmark 与实证研究定位调研，含 12 篇论文 PDF、来源清单、阅读笔记和 ReproBench 定位建议。
- [empirical-related-work-2026-11-19/](empirical-related-work-2026-11-19/README.md)：补充实证研究与 related work 素材，含 12 份新保存 PDF、阅读笔记、中英文介绍素材和 BibTeX；另有实证研究写法总结及据此更新的大纲 v2。

这些材料为多版本共用。各版实际编译所需的样式文件另随 `paper/` 独立保存。

两组 2026-11-19 调研中的 PDF 和全文提取文本作为本地缓存，不随 Git clone 下载。来源、校验值和阅读笔记仍在仓库中；按需恢复：`python scripts/restore_study_papers.py --with-text`（PDF 恢复需要 Python 3.11+，文本提取另需 pdftotext）。
