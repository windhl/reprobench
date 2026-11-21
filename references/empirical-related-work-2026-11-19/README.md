# 补充实证研究文献：Related Work 素材

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

日期：2026-11-19。最初按作者要求独立整理相关研究；随后恢复结构讨论，补充实证研究写法总结与论文大纲 v2。未修改 LaTeX 正文、实验或评分代码。

本目录新增保存 12 份 PDF：11 项原始实证研究或带实证分析的研究系统，以及 1 项评估实践综述。不是 12 篇纯 empirical study，也不把 workshop、预印本与正式会议/期刊论文混同。

- [逐篇阅读笔记](notes/reading-notes.md)：研究对象、分析方法、主要观察、范围及可引用表述。
- [实证研究写法总结](notes/empirical-study-writing-guide.md)：归纳原作的论证路径、常见框架和局部行文方式，并说明怎样应用到 ReproBench。
- [ReproBench 论文大纲 v2](../../versions/usenix-security-2027/notes/paper-outline-v2-2026-11-19.md)：基于这些写法重新组织的当前推荐结构，供作者审阅。
- [Related Work 介绍素材](related-work-materials.md)：中文介绍要点与英文段落草稿，供进一步审阅，尚未迁入正文。
- [BibTeX](references.bib)：仅包含核实的基本引用字段；未确认正式发表的工作按 arXiv 记录。
- [来源清单](sources.json)：来源链接、发表状态、下载版本、页数、SHA-256 与阅读范围。

## 文献索引

| 文献 | 已核实的发表状态 | 类型/相关性 | 公开来源 |
| --- | --- | --- | --- |
| Understanding the Reproducibility of Crowd-reported Security Vulnerabilities | USENIX Security 2018 | 人工漏洞复现的直接实证研究 | [PDF](https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-mu.pdf) |
| A Systematic Study on Generating Web Vulnerability Proof-of-Concepts Using Large Language Models | arXiv:2510.10148v1；未核实正式发表 | Web PoC 生成的直接实证研究 | [PDF](https://arxiv.org/pdf/2510.10148v1) |
| Can LLMs Hack Enterprise Networks? Autonomous Assumed Breach Penetration-Testing Active Directory Networks | TOSEM 2026；本地保存 arXiv v3 作者稿 | 企业网络 agent 的定量与定性研究 | [PDF](https://arxiv.org/pdf/2502.04227) |
| From Capabilities to Performance: Evaluating Key Functional Properties of LLM Architectures in Penetration Testing | EMNLP 2025 主会 | 失败模式与功能增强的实证分析 | [PDF](https://aclanthology.org/2025.emnlp-main.802.pdf) |
| Enhancing Linux Privilege Escalation Attack Capabilities of Local LLM Agents | arXiv v2 注明 RAISE workshop 录用 | 从失败分类到系统干预 | [PDF](https://arxiv.org/pdf/2604.27143) |
| Decoupling Reconnaissance and Exploitation: Measuring the Capability Boundaries of LLM-Based Web Penetration Testing | arXiv:2606.25332v1；未核实正式发表 | 阶段耦合与提供前提信息的实验 | [PDF](https://arxiv.org/pdf/2606.25332) |
| How Reliable Are AI Attackers Against a Fixed Vulnerable Target? A 400-Run Empirical Study of LLM Penetration Testing Consistency | arXiv:2605.30096v1；未核实正式发表 | 重复运行、行为差异及故障归因 | [PDF](https://arxiv.org/pdf/2605.30096) |
| Incalmo: An Autonomous LLM-assisted System for Red Teaming Multi-Host Networks | IEEE S&P 2026；本地保存 arXiv v4 | 失败分析驱动的新系统和 benchmark | [PDF](https://arxiv.org/pdf/2501.16466) |
| An Empirical Evaluation of LLMs for Solving Offensive Security Challenges | arXiv:2402.11814v1；未核实正式发表 | 人工交互与自动 CTF 解题的实证研究 | [PDF](https://arxiv.org/pdf/2402.11814) |
| LLMs Cannot Reliably Identify and Reason About Security Vulnerabilities (Yet?): A Comprehensive Evaluation, Framework, and Benchmarks | IEEE S&P 2024；本地保存 arXiv v3 | 安全判断、解释与稳定性的实证评估 | [PDF](https://arxiv.org/pdf/2312.12575) |
| Fixing Security Vulnerabilities with Agentic AI in OSS-Fuzz | ICSE 2026 SEIP | 安全修复的相邻实证研究，含新 agent | [PDF](https://yuntongzhang.github.io/assets/pdf/icse26-seip.pdf) |
| Benchmarking Practices in LLM-driven Offensive Security: Testbeds, Metrics, and Experiment Design | arXiv:2504.10112v2；未核实正式发表 | 方法与文献综述，不是新的攻击实验 | [PDF](https://arxiv.org/pdf/2504.10112) |

## 建议阅读顺序

先读 Crowd-reported Reproducibility、Web PoC Study、Enterprise Networks，分别对应复现困难、PoC 构造和 agent 执行过程。再读 Capabilities to Performance、Local Privilege Escalation、Decoupling，比较它们如何解释失败。Incalmo 属于“实证发现驱动系统设计”的对照；其余论文补充稳定性、结果有效性和研究方法背景。

前一轮已经保存的 Patch-to-PoC、LLMs as Hackers、Local Open-Weight、One-day 等仍在 [上一轮目录](../positioning-study-2026-11-19/README.md)，这里不重复复制。

## 阅读和引用边界

本轮核读各篇与研究问题、实验条件、成功判定、失败分析及局限有关的正文；不是仅根据摘要整理，但也没有声称逐页精读所有附录或独立重现实验。具体范围在笔记和来源清单中记录。全文提取文本在 `texts/`，图表以 PDF 为准。

已确认正式发表不代表下载稿必然与出版终稿逐字相同。Enterprise Networks、SecLLMHolmes、Incalmo 的本地 PDF 是 arXiv 稿，引用时优先使用正式发表信息，具体数字仍应与最终使用的版本对齐。

尤其注意：Incalmo 的旧标题是 *On the Feasibility of Using LLMs to Execute Multistage Network Attacks*；本地 v4 是新标题和 40 网络实验，不能沿用旧版 10 网络数字。评估实践综述本地 v2 覆盖 19 篇论文、18 个 prototype，早期摘要的 16/15 不适用于此版。
