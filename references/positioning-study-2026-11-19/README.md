# ReproBench：benchmark 与实证研究定位调研

## 本地论文缓存（不随 Git clone 下载）

`papers/` 中的 PDF 和 `texts/` 中的全文提取文本是本地缓存，已从 Git 跟踪中移除；现有本地文件保留。阅读笔记、来源清单、版本说明及 SHA-256 继续纳入 Git。下表链接指向公开来源。

在仓库根目录运行（Python 3.11+）：

```sh
python scripts/restore_study_papers.py
# 同时重新生成全文提取文本，需要安装 Poppler 的 pdftotext
python scripts/restore_study_papers.py --with-text
# 只核验或复用已有本地 PDF，不访问网络
python scripts/restore_study_papers.py --offline
```

脚本优先复用既有 PDF，其次使用来源清单中的下载地址；arXiv 优先使用记录的版本号。恢复时核验原始 SHA-256，不接受不同版本覆盖。四篇沿用旧资料的论文从 `references/papers/bench_papers/` 复用。如果来源失效或文件版本变化，请按 `sources.json` 的来源和 SHA-256 手动恢复，命令会报告失败。重新提取的文本可能因 pdftotext 版本不同而有排版差异。

日期：2026-11-19。目的：比较两种论文的贡献和证据要求，判断现有 ReproBench 数据更适合哪种叙事；不修改现有论文、评分或实验结果。

先读 [定位判断与讨论](recommendation.md)，逐篇依据见 [文献阅读笔记](notes/literature-notes.md)。[sources.json](sources.json) 记录来源、版本说明、PDF 页数、SHA-256 和本地文件位置。PDF 在 `papers/`，`pdftotext -layout` 提取文本在 `texts/`；提取文本不是出版原稿的替代品，图表应以 PDF 为准。

| 类型 | 论文 | 核查的版本/发表状态 | 公开来源 |
| --- | --- | --- | --- |
| Benchmark | CVE-Bench | ICML 2025；本地 arXiv v4 | [PDF](https://proceedings.mlr.press/v267/zhu25i.html) |
| Benchmark | Cybench | ICLR 2025 正式论文 | [PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/3e9412a9c1d93810ef3ef7825115016b-Paper-Conference.pdf) |
| Benchmark | BountyBench | NeurIPS 2025 Datasets and Benchmarks 正式论文 | [PDF](https://bountybench.github.io/) |
| Benchmark | SEC-bench | NeurIPS 2025 正式论文 | [PDF](https://github.com/SEC-bench/SEC-bench) |
| 实证研究＋研究系统 | Patch-to-PoC / K-Repro | arXiv:2602.07287v2；未核实正式发表 | [PDF](https://arxiv.org/abs/2602.07287) |
| 能力实证研究 | LLM Agents can Autonomously Exploit One-day Vulnerabilities | arXiv:2404.08144v2；按预印本使用 | [PDF](https://arxiv.org/pdf/2404.08144v2) |
| 实证研究＋测试平台 | LLMs as Hackers | Empirical Software Engineering 31:70，2026；正式期刊 PDF | [PDF](https://link.springer.com/content/pdf/10.1007/s10664-025-10758-3.pdf) |
| 实证研究＋评估方法 | Uncovering the Limits of Machine Learning for Automatic Vulnerability Detection | USENIX Security 2024 | [PDF](https://www.usenix.org/system/files/usenixsecurity24-risse.pdf) |
| 能力实证研究 | Analysis of Local Open-Weight LLM Agents on Vulnerability-Reproduction Tasks | arXiv:2611.06257v1；作者注明 JSS 在审，尚非录用论文 | [PDF](https://arxiv.org/pdf/2611.06257) |
| 研究＋新系统 | PentestGPT | USENIX Security 2024 | [PDF](https://www.usenix.net/system/files/usenixsecurity24-deng.pdf) |
| IoT 研究＋新系统 | FirmAgent | NDSS 2026 | [PDF](https://netsec.ccert.edu.cn/files/papers/ndss26-firmagent.pdf) |
| 直接相关的环境重建系统 | CVE-GENIE | arXiv:2509.01835v2；未核实正式发表 | [PDF](https://arxiv.org/pdf/2509.01835v2) |

阅读范围：围绕贡献、任务边界、实验设计、判定成功的方法、结果解释与局限阅读正文。CVE-Bench、BountyBench、Patch-to-PoC、One-day 和 Local Open-Weight 是定位比较的主要阅读材料；其余论文重点核读上述相关章节，具体章节写在阅读笔记中。没有声称逐页精读全部附录：Cybench 的 PDF 为 150 页，BountyBench 为 120 页，大量篇幅是日志、逐任务说明和补充材料；本次只选择与研究设计有关的附录核读。

四份既有 PDF 从 `../papers/bench_papers/` 复制：CVE-Bench、BountyBench、SEC-bench、K-Repro。其余从 arXiv、会议、出版社或作者站点下载。没有依赖第三方自动生成的论文解读作为判断依据。
