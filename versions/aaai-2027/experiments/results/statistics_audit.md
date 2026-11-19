# 论文统计量审计报告

## 概述

本报告逐项梳理论文中使用的每一个统计量，标注其统计方式（best-of-three / per-run / 混合），评估合理性，并给出改进建议。

**统计方式定义：**
- **Best-of-three (BOT)**：对每个 CVE-模型对（3 次 run），取 max(plan)、max(task)、max(per-run overall)，分别独立取最大值
- **Per-run**：直接对 450 次 run 取平均或计数
- **Per-pair**：对 150 个 CVE-模型对取平均或计数（每个 pair 内可能先做 BOT 再聚合）

---

## 逐项审计

### 1. Table 1: 模型总分表（400-experimental-design.tex）

| 列 | 统计量 | 统计方式 | 论文位置 |
|---|---|---|---|
| Avg Plan | 各模型 30 个 pair 的 best-of-three plan 平均 | BOT → per-pair average | 第 44-48 行 |
| Avg Task | 各模型 30 个 pair 的 best-of-three task 平均 | BOT → per-pair average | 第 44-48 行 |
| Avg Overall | 各模型 30 个 pair 的 max(per-run overall) 平均 | BOT → per-pair average | 第 44-48 行 |
| Max Overall | 各模型 30 个 pair 中 max(per-run overall) 的最大值 | BOT → max | 第 44-48 行 |
| P5≥15 | 各模型 30 个 pair 中 max(R5)≥15 的 pair 数 | BOT → count | 第 44-48 行 |
| P6≥15 | 各模型 30 个 pair 中 max(R6)≥15 的 pair 数 | BOT → count | 第 44-48 行 |
| All 行 | 150 个 pair 的聚合 | BOT → per-pair aggregate | 第 50 行 |

**统计方式**：统一使用 BOT → per-pair

**合理性**：✅ 合理。Table 1 是论文的核心结果表，使用 BOT 反映"给定多次尝试，模型能否至少成功一次"。Avg Overall 使用 max(per-run overall) 而非 0.2×max(plan)+0.8×max(task)，避免了拼凑效应。

**潜在问题**：Avg Plan 和 Avg Task 分别取 BOT，但 Avg Overall 取的是 max(per-run overall)，三者来自不同的聚合路径。读者可能误以为 Avg Overall = 0.2×Avg Plan + 0.8×Avg Task，但实际不等（如 glm-5.2: 0.2×86.7+0.8×59.9=65.3 ≠ 64.6）。

**改进建议**：在表格 caption 中加注 "Avg Overall is the average of max per-run overall scores, not a recombination of Avg Plan and Avg Task."

---

### 2. 501-overall.tex: 模型排名与 Overall 分数

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| "glm-5.2 achieves highest (64.6/100)" | BOT average | BOT → per-pair | ✅ 与 Table 1 一致 |
| "mimo (52.9)" | BOT average | BOT → per-pair | ✅ |
| "claude (50.0)" | BOT average | BOT → per-pair | ✅ |
| "only 11 out of 150 CVE-model pairs achieve near-full P5" | P5≥15 pair count | BOT → count | ✅ 与 Table 1 一致 |
| "of which 8 also achieve near-full P6" | P5∩P6 overlap | BOT → count | ✅ 正确使用了交集而非简单相加 |
| "best single run reaches 99.0/100" | max(per-run overall) | BOT → max | ✅ |
| "five CVEs achieve full or near-full reproduction (≥90)" | CVE-level max | BOT → max across pairs → CVE count | ✅ |

**统计方式**：统一 BOT

**合理性**：✅ 合理。

---

### 3. 501-overall.tex: 模型行为分析

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| "glm-5.2 averages 11.5/15 on P2 under best-of-three scoring" | glm P2 BOT average | BOT → per-pair | ✅ 明确标注了 BOT |
| "claude-sonnet-4-6's 7.7/15" | claude P2 BOT average | BOT → per-pair | ✅ |
| "claude has 20 runs where plan exceeds 50 yet task stalls below 15" | per-run count | **Per-run** | ⚠️ 混用 |
| "glm-5.2 achieves strongest fallback planning (32.2/100)" | per-run fallback average | **Per-run** | ⚠️ 混用 |
| "15.0--28.6 for the others" | per-run fallback range | **Per-run** | ⚠️ 混用 |

**问题**：Table 1 和模型排名使用 BOT，但模型行为分析中的 P2 分数用 BOT、plan>50&task<15 用 per-run count、fallback 用 per-run average。同一段落内混用了两种统计方式。

**合理性**：⚠️ 混用不合理。
- P2 用 BOT 是为了与 Table 1 对齐
- plan>50&task<15 用 per-run 是因为要统计"有多少次 run 出现这种情况"，但 BOT 下一个 pair 最多 3 次 run，用 per-run count 会让 run 数多的模型看起来更差
- fallback 用 per-run average 会拉低数值（因为有些 run 的 plan=0/fallback=0）

**改进建议**：统一使用 BOT。plan>50&task<15 改为"X out of 30 pairs"（BOT 下 best plan>50 且 best task<15 的 pair 数）。fallback 改为 BOT average。

---

### 4. 502-failure.tex: Stage Funnel 表格

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| P1=13.9/15 (92.8%) | BOT phase average | BOT → per-pair average | ✅ |
| P2=9.0/15 (59.8%) | BOT phase average | BOT → per-pair average | ✅ |
| P3=8.1/15 (53.7%) | BOT phase average | BOT → per-pair average | ✅ |
| P4=7.6/15 (50.8%) | BOT phase average | BOT → per-pair average | ✅ |
| P5=3.7/20 (18.6%) | BOT phase average | BOT → per-pair average | ✅ |
| P6=2.8/20 (13.8%) | BOT phase average | BOT → per-pair average | ✅ |

**统计方式**：统一 BOT

**合理性**：✅ 合理。

---

### 5. 502-failure.tex: 失败归因计数

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| Simulation substitution 316/450 (70.2%) | per-run count | **Per-run** | ✅ 失败归因是 per-run 属性 |
| Rehosting gap 97/450 (21.6%) | per-run count | **Per-run** | ✅ |
| Extraction failures 37/450 (8.2%) | per-run count | **Per-run** | ✅ |
| Infrastructure failures 15/450 (3.3%) | per-run count | **Per-run** | ✅ |
| P2 terminal blockers 202/450 | per-run count | **Per-run** | ✅ |
| P5 terminal blockers 109/450 | per-run count | **Per-run** | ✅ |

**统计方式**：统一 Per-run

**合理性**：✅ 合理。失败归因是 per-run 的属性（每次 run 有一个 terminal blocker），使用 per-run count 正确。虽然 Table 1 和 stage funnel 使用 BOT，但失败分析描述的是"450 次 run 中发生了什么"，用 per-run 是正确的。

**注意**：465 = 316+97+37+15 ≠ 450，因为有 15 次 run 属于 infrastructure failure 且同时被归入 simulation（评分器 multi-label）。论文中已按非重叠方式重新计算为 316+97+37+15=465，超出 450 的 15 个是 infrastructure failure 被单独列出的同时其 run 也在 simulation 中。论文需要说明这些是重叠的或使用非重叠分类。

**改进建议**：明确说明失败归因是 per-run 且各类别可能重叠（一个 run 可同时被归因为 simulation 和 infrastructure failure），或者使用非重叠的优先级分类使总和=450。

---

### 6. 502-failure.tex: 正文中的 funnel 描述

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| "P1 strongest at 13.9/15" | BOT average | BOT | ✅ 与表格一致 |
| "P2--P4 show moderate scores (7.6--9.0/15)" | BOT average range | BOT | ✅ |
| "P5 averages only 3.7/20" | BOT average | BOT | ✅ |
| "P6 averages 2.8/20" | BOT average | BOT | ✅ |

**统计方式**：统一 BOT

**合理性**：✅ 合理。

---

### 7. 503-feature.tex: 异常分析

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| "across all 450 runs" | per-run | **Per-run** | ✅ 异常分析在 per-run 层面检测 |
| "≥40% of phase maximum while majority ≤15%" | per-run threshold | **Per-run** | ✅ |
| "18 CVEs exhibiting divergence" | per-run → CVE count | **Per-run → CVE** | ✅ |
| "only one of 15 runs curls the Xiaomi CDN" | per-run count | **Per-run** | ✅ 特定 CVE 的 15 次 run |
| "only 4/15 runs know the delink tool" | per-run count | **Per-run** | ✅ |
| "top-scoring run (glm-5.2, 19/20)" | single run | **Per-run (single)** | ✅ 引用特定 run 的分数 |

**统计方式**：统一 Per-run

**合理性**：✅ 合理。异常分析的目的是发现"在同一 CVE 的 15 次 run 中，少数成功 vs 多数失败"的分化，必须使用 per-run。

---

### 8. 504-vulclass.tex: 漏洞类型分析

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| "best-of-three overall score (58.5 vs 48.9 vs 46.0)" | BOT average by type | BOT → per-pair | ✅ 明确标注了 BOT |
| "Agents average 7.23/15 on P2" (BOF) | **per-run** average | **Per-run** | ⚠️ 混用 |
| "6.81/15 on P4" (BOF) | **per-run** average | **Per-run** | ⚠️ 混用 |
| "62% of runs acquire the firmware" (BOF) | per-run percentage | **Per-run** | ⚠️ 混用 |
| "3.3% full-trigger rate (5/150 runs reaching P6≥18)" (CMDI) | per-run count | **Per-run** | ⚠️ 混用，且阈值从 ≥15 变为 ≥18 |
| "P4: 3.68/15 per-run average" (AUTH) | per-run average | **Per-run** | ⚠️ 混用，但已标注 |
| "CVE-2023-26315 and CVE-2024-23624 reach 99.0 and 80.8" | CVE-level max overall | BOT → max | ✅ |

**问题**：Overall score 用 BOT，但 phase-level 数字用 per-run。同一段落内混用。

**合理性**：⚠️ 混用不太合理。读者看到 "58.5 vs 48.9 vs 46.0"（BOT）后，自然预期 "7.23/15 on P2" 也是 BOT，但实际是 per-run。per-run 会比 BOT 低（因为 per-run 包含了 0 分的失败 run）。

**改进建议**：统一使用 BOT 或在文中明确标注每个数字的统计口径。如果 phase-level 数字用 per-run，应加 "per-run average" 标注（AUTH 的 P4 已标注，但 BOF 的 P2/P4 未标注）。

---

### 9. Abstract / Introduction: 汇总数字

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| "70.2% of test runs resort to simulation" (abstract) | per-run percentage | **Per-run** | ✅ |
| "5.3% of runs achieve successful reproduction" (abstract) | per-pair percentage (8/150) | **Per-pair (BOT)** | ⚠️ 标签错误 |
| "70.2% of runs" (intro) | per-run percentage | **Per-run** | ✅ |
| "5.3%" (intro) | per-pair percentage (8/150) | **Per-pair (BOT)** | ⚠️ 标签错误 |
| "collapse at rehosting (3.7/20)" (conclusion) | BOT average | BOT | ✅ |

**问题**：abstract 和 intro 说 "5.3% of runs"，但 5.3% = 8/150 是 per-pair（BOT 下 P6≥15 的 pair 数），不是 per-run。per-run 的成功复现率是 16/450 = 3.6%（基于 poc_execution_against_real_target > 0 AND vulnerability_specific_trigger_evidence > 0 标准）。

**合理性**：❌ 不合理。"of runs" 标签与 per-pair 统计不匹配。

**改进建议**：
- 方案 A：改为 "5.3% of CVE-model pairs"（保持 BOT 口径，改标签）
- 方案 B：改为 "3.6% of runs"（保持 per-run 口径，改数字）
- 方案 C：两个数字都用 per-run："70.2% of runs resort to simulation... while 3.6% achieve successful reproduction"

---

### 10. 700-discussion.tex

| 统计量 | 值 | 统计方式 | 合理性 |
|---|---|---|---|
| "70.2% of our runs produce simulated reproductions" | per-run | **Per-run** | ✅ |

**统计方式**：Per-run

**合理性**：✅ 合理。

---

## 统计方式混用汇总

| 位置 | BOT 统计量 | Per-run 统计量 | 混用？ |
|---|---|---|---|
| Table 1 | Avg Plan/Task/Overall, P5/P6 count | 无 | 否 |
| 501 模型排名 | Overall average | 无 | 否 |
| 501 模型行为 | P2 average | plan>50&task<15 count, fallback average | ⚠️ **是** |
| 502 Stage Funnel | Phase averages | 无 | 否 |
| 502 失败归因 | 无 | 所有计数 (316/97/37/15/202/109) | 否（全部 per-run） |
| 503 异常分析 | 无 | 所有 (450 runs, 18 CVEs, 4/15, 1/15) | 否（全部 per-run） |
| 504 漏洞类型 | Overall score | P2/P4 average, FW%, P6≥18 count | ⚠️ **是** |
| Abstract/Intro | 5.3% (标为 "of runs" 实为 per-pair) | 70.2% | ⚠️ **是** |

---

## 改进建议总结

### 必须修复

1. **Abstract & Intro: "5.3% of runs" → "5.3% of CVE-model pairs" 或 "3.6% of runs"**
   - 当前 "of runs" 标签与 per-pair 统计不匹配
   - 建议改为 "5.3% of CVE--model pairs"（保持与 Table 1 的 P6≥15 一致）

2. **501 模型行为: plan>50&task<15 和 fallback 的统计口径**
   - 当前混用 BOT（P2）和 per-run（count, fallback）
   - 建议：plan>50&task<15 改为 BOT 口径（"X out of 30 pairs where best plan > 50 yet best task < 15"）；fallback 改为 BOT average

3. **504 漏洞类型: phase-level 数字标注口径**
   - 当前 Overall 用 BOT，P2/P4 用 per-run 但未标注（AUTH 的 P4 已标注）
   - 建议：统一使用 per-run 并全部标注 "per-run average"，或统一使用 BOT

### 建议改进

4. **502 失败归因: 说明各类别是否重叠**
   - 316+97+37+15=465 > 450
   - 建议说明"failure families may overlap"或使用非重叠分类

5. **504: P6≥18 vs P6≥15 阈值不一致**
   - 501/Table 1 使用 P6≥15，504 CMDI 使用 P6≥18
   - 建议统一或解释原因

6. **Table 1 caption: 说明 Avg Overall ≠ 0.2×AvgPlan + 0.8×AvgTask**
   - 加注避免读者困惑

---

## 建议的统计方式统一方案

| 类别 | 建议统计方式 | 理由 |
|---|---|---|
| 模型排名与总分 (Table 1) | **BOT** | 反映"多次尝试的最佳表现" |
| Stage Funnel | **BOT** | 与 Table 1 对齐 |
| 失败归因计数 | **Per-run** | 失败是 per-run 属性 |
| 异常分析 | **Per-run** | 分析 run 间分化 |
| 漏洞类型 Overall | **BOT** | 与 Table 1 对齐 |
| 漏洞类型 Phase 数字 | **Per-run**（需标注） | 反映"典型表现"而非"最佳" |
| 模型行为 P2 对比 | **BOT** | 与 Table 1 对齐 |
| 模型行为 plan>50&task<15 | **BOT**（改为 pair count） | 与 Table 1 对齐 |
| 模型行为 fallback | **BOT** | 与 Table 1 对齐 |
| Abstract/Intro 成功率 | **Per-pair (BOT)**，标签改为 "of CVE-model pairs" | 与 Table 1 的 P6≥15 一致 |
| Abstract/Intro 模拟率 | **Per-run** | "of runs" 标签正确 |

---

*生成时间：2026-07-24，基于 reprobench 仓库最新版本分析*
