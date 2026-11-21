# 英文草稿 TODO 清单

历史清单：对应 11/19 首稿。当前源码和行号见 [11/20 清单](draft-todos-2026-11-20.md)。

日期：2026-11-19。由当前 LaTeX 中可见的 TODO 标记提取。本文是内部草稿，尚未完成实证结论核验，不能作为可直接投稿的定稿。

## 建议处理顺序

1. **研究必需：** DES（实际选例与运行配置）、AUD（证据与结果）、CASE（案例验证）、COD（轨迹编码）、ANA/RQ（重新统计）和 VAL（有效性核查）。删除打分不替代这些工作。
2. **条件性补实验：** EXP-01 环境就绪对照、EXP-02 提示词对照、EXP-03 第二 harness。若不做，对应结论需保持观察性和配置边界；不是当前全部必须新增的实验。
3. **成稿整理：** 核验后更新 ABS、INTRO、RQ-ANS、DISC 和 CONC，写入实际成立的发现。
4. **投稿准备：** ETH、OS 和 SUP 补齐实际安全措施、匿名 artifact 链接、开放范围及补充材料。

## 逐项清单


- **ABS-01** — [000-abstract.tex](../paper/sections/000-abstract.tex):13

  Insert the audited outcome distribution and two principal cross-case findings after evidence review.

- **INTRO-01** — [100-introduction.tex](../paper/sections/100-introduction.tex):74

  Replace this draft-status paragraph with a concise summary of the audited principal findings before submission.

- **INTRO-02** — [100-introduction.tex](../paper/sections/100-introduction.tex):83

  Replace the intended-contribution wording with final, specific findings and the actual scope of the released resource.

- **DES-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):104

  Reconcile the actual 30 run identifiers with all selection lists; recover the 696-to-30 exclusion counts and selection dates. Audit product, affected version, class, ISA, and reference status for every case.

- **DES-02** — [300-study-design.tex](../paper/sections/300-study-design.tex):128

  Recover host and container configuration, image digests, OpenCode commit, tool versions, isolation flags, model providers/snapshots, sampling parameters, and run dates from original records.

- **DES-03** — [300-study-design.tex](../paper/sections/300-study-design.tex):145

  Recover the exact executable prompt and control loop; verify budget enforcement, retry and stop rules, tool permissions, cross-run reset behavior, and whether any operator interventions occurred.

- **AUD-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):180

  Build a run-level evidence manifest, classify missingness, inspect all claimed successes, and sample other strata to detect omitted successes and incorrect negative labels.

- **AUD-02** — [300-study-design.tex](../paper/sections/300-study-design.tex):228

  Freeze and apply the per-class rules, revalidate original target identity and effects, and adjudicate component-level versus documented-entry reproduction. Report control availability and unresolved cases. Do not claim that all controls have already been run.

- **COD-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):253

  Conduct pilot coding; specify analysts, sampling, independent overlap, agreement measures, codebook revisions, and disagreement resolution. This draft does not claim completed multi-analyst validation.

- **ANA-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):269

  Generate outcome and activity-state tables from adjudicated records, document the chosen paired/clustered uncertainty procedure, and report sensitivity to unknown outcomes and incomplete traces.

- **ANA-02** — [300-study-design.tex](../paper/sections/300-study-design.tex):278

  Audit token, billing, timing, and termination records; distinguish zero-priced routes from zero inference use and missing logs from infrastructure failures.

- **RQ1-01** — [400-results.tex](../paper/sections/400-results.tex):53

  Replace the candidate table with adjudicated per-run outcomes, component/documented-entry scope, unknown counts, and CVE-clustered uncertainty; retain candidate counts only if useful for explaining the audit. Examine noncandidate records for false negatives.

- **CASE-01** — [400-results.tex](../paper/sections/400-results.tex):80

  Verify image/component hashes and process identity against the trace; replay a benign and triggering input, and exclude direct proof-file creation by setup or client code.

- **RQ1-02** — [400-results.tex](../paper/sections/400-results.tex):93

  Apply the component-versus-entry distinction to all 16 candidates, including the RouterOS cases; state which result satisfies the final primary outcome and report the narrower results separately.

- **RQ1-03** — [400-results.tex](../paper/sections/400-results.tex):118

  Produce the activity-state matrix and coverage by case and configuration from reviewed artifacts. Identify paths that revisit earlier activities and ensure that progress comes from the same run.

- **RQ1-04** — [400-results.tex](../paper/sections/400-results.tex):139

  Compute paired repetition patterns, identify same-case contrasts, and report both per-run and at-least-one results with their denominators.

- **RQ1-ANS** — [400-results.tex](../paper/sections/400-results.tex):147

  Replace this provisional answer with the audited outcome distribution and repetition findings.

- **RQ2-01** — [400-results.tex](../paper/sections/400-results.tex):172

  Validate acquisition and version-mismatch episodes, including whether alternative sources were tried. Separate unavailable material, temporary access errors, incorrect artifacts, unverified assertions, and missing records; report the cases and runs underlying each count.

- **RQ2-02** — [400-results.tex](../paper/sections/400-results.tex):206

  Code verified startup episodes and their exact error messages, dependency changes, and outcomes. Report ISA and execution-mode coverage where known; examine same-case successes as counterexamples to claims of unavoidable environmental failure.

- **CASE-02** — [400-results.tex](../paper/sections/400-results.tex):232

  Recover the Ghidra invocation, tool output, and termination record if available. Otherwise retain the stopping reason as unknown and exclude this run from claims about responses to observed tool errors.

- **RQ2-03** — [400-results.tex](../paper/sections/400-results.tex):258

  Identify post-startup obstacles among runs with verified original-target execution. Report the eligible subset and analyze protocol, authentication, configuration, and trigger-evidence problems without treating unattempted later activities as observed failures.

- **RQ2-04** — [400-results.tex](../paper/sections/400-results.tex):275

  Produce the reviewed obstacle distribution, denominators, and paired case comparisons. Replace historical failure-family totals with the frozen codebook results; report unresolved and multiply coded episodes.

- **RQ2-ANS** — [400-results.tex](../paper/sections/400-results.tex):288

  Insert the cross-case patterns, their counts, counterexamples, and uncertainty; do not identify a dominant bottleneck from old phase scores.

- **RQ3-01** — [400-results.tex](../paper/sections/400-results.tex):313

  Code response episodes after verified feedback, identify which changes led to new observed states, and compare repair, repetition, alternative execution, and stopping across adequately observed runs.

- **RQ3-02** — [400-results.tex](../paper/sections/400-results.tex):334

  Reconcile 204 versus 209 terminal-label counts, then recode any simulation, first simulation, return to target, and final tested object from primary evidence. Report trace coverage separately for temporal claims.

- **CASE-03** — [400-results.tex](../paper/sections/400-results.tex):362

  Adjudicate the simulation case from source, saved output, and any recoverable trace. Preserve the explicit disclaimer in report coding; do not infer an actual download history from its absence.

- **RQ3-03** — [400-results.tex](../paper/sections/400-results.tex):382

  Select matched same-CVE trajectories with verified time order, including a return-to-target or other counterexample if observed. Plot actual event sequences; do not fabricate a paired contrast from unrelated cases.

- **RQ3-04** — [400-results.tex](../paper/sections/400-results.tex):409

  Cross-tabulate report claims against adjudicated outcomes and target types; audit stop reasons from control-loop records, keeping absent or ambiguous evidence explicit.

- **RQ3-ANS** — [400-results.tex](../paper/sections/400-results.tex):415

  Replace these case-level observations with validated response patterns, report-alignment counts, temporal evidence, and bounded interpretations.

- **EXP-01** — [500-discussion.tex](../paper/sections/500-discussion.tex):42

  Optional, if the final claim concerns the effect of environment readiness: compare CVE-only and verified-ready-target conditions on the same cases with matched agent setup and budget. Report the common eligible subset, its selection bias, and negative results.

- **DISC-01** — [500-discussion.tex](../paper/sections/500-discussion.tex):58

  Develop the final cross-RQ interpretation from validated patterns and counterexamples. Identify which explanation the evidence supports beyond the individual cases, and retain competing explanations where unresolved.

- **EXP-02** — [500-discussion.tex](../paper/sections/500-discussion.tex):96

  Optional, if claiming that task wording changes simulation or report alignment: compare the historical instruction with an explicit original-target requirement that permits honest failure reporting. Keep the environment and budget matched and measure both progress and claims.

- **VAL-01** — [600-validity.tex](../paper/sections/600-validity.tex):12

  Report the actual number of independently checked targets, replayed outcomes, available controls, and unresolved disagreements; align the claims with that coverage.

- **EXP-03** — [600-validity.tex](../paper/sections/600-validity.tex):59

  Optional, if a principal finding is claimed to generalize across harnesses: replicate a preselected, diverse subset under a second harness with the same model route and comparable resources.

- **VAL-02** — [600-validity.tex](../paper/sections/600-validity.tex):76

  Report final coverage, sampling, counterexamples, missing-data sensitivity, and any exploratory comparisons omitted for insufficient evidence. Remove or narrow interpretations that do not survive these checks.

- **CONC-01** — [800-conclusion.tex](../paper/sections/800-conclusion.tex):10

  Replace the preliminary summary with audited cross-case findings, their scope, and the principal practical implication. Complete the outstanding validation before making a final performance or bottleneck claim.

- **ETH-01** — [900-ethics.tex](../paper/sections/900-ethics.tex):18

  Verify the actual container privileges, mounts, device exposure, network controls, download destinations, and human oversight. State the measures actually used and investigate any unexpected external activity before making a containment claim.

- **ETH-02** — [900-ethics.tex](../paper/sections/900-ethics.tex):28

  Inspect artifacts for credentials, API tokens, proprietary content, personal data, and identifying metadata; redact unnecessary values while retaining a documented basis for checking the reported effect.

- **ETH-03** — [900-ethics.tex](../paper/sections/900-ethics.tex):40

  Confirm whether reanalysis uncovered any previously unreported issue and document any necessary coordinated disclosure; record the actual sharing decisions and reasons for restricted items.

- **OS-01** — [910-open-science.tex](../paper/sections/910-open-science.tex):5

  Insert a stable anonymous artifact URL without tracking; verify access for the entire review period and freeze the submitted snapshot. The internal archive is not yet a reviewer-accessible release.

- **OS-02** — [910-open-science.tex](../paper/sections/910-open-science.tex):31

  Package and verify the available trajectories, relevant artifact excerpts, labels, and analysis entry point; list missing runs and nonshareable components explicitly. Check that a fresh reader can reproduce every main-text count from the frozen reviewed records.

- **OS-03** — [910-open-science.tex](../paper/sections/910-open-science.tex):45

  Complete the licensing and confidentiality review, specify the exact access status of each artifact class, and validate an anonymous reanalysis package. Do not claim full experimental reproducibility from the inventory script alone.

- **SUP-01** — [920-supplement.tex](../paper/sections/920-supplement.tex):71

  Publish the full case/reference table, exact recovered prompt, coding rules, coverage strata, and completed sensitivity results; keep decisive methods and findings in the main body.
