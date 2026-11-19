# arXiv

`paper/main.tex` 是整理前 `reprobench_arxiv.tex` 的原样副本，包含作者信息和正文内附录。正文、插图、参考文献独立于 AAAI 保存。

`submission/reprobench_arxiv.zip` 和 PDF 原样保留。ZIP 内 22 个文件中有 21 个与整理前对应文件相同；相关工作章节存在差异。`paper/` 保留当前工作区内容，没有用 ZIP 静默覆盖正文。尚未确认该 ZIP 的实际上传版本号和日期。

在仓库根目录执行 `bash compile.sh arxiv`，输出位于 `build/arxiv/main.pdf`。

实验目录来自整理前共用的 `data/`，不是独立开展的一组新实验。来源记录见 [manifest.json](manifest.json)。
