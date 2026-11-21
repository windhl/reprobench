# 带复用图表版本的 TODO 清单

日期：2026-11-20。对应当前 LaTeX 和带图表草稿。共 43 项；复用旧素材未将待核验标签转成最终发现。

- DES/AUD/CASE/COD/ANA/RQ/VAL：研究所需的配置核查、证据核验、重新标注与统计。
- EXP-01/02/03：条件性补实验；不做时应收窄对应结论。
- ABS/INTRO/DISC/CONC：根据核验后的发现更新论证。
- ETH/OS/SUP：实际安全措施、artifact 访问与共享材料。提示词原图和历史案例表已保留，实际执行输入和元数据核验仍需完成。


- **ABS-01** — [000-abstract.tex](../paper/sections/000-abstract.tex):13

  Insert the audited outcome distribution and two principal cross-case findings after evidence review.

- **INTRO-01** — [100-introduction.tex](../paper/sections/100-introduction.tex):74

  Replace this draft-status paragraph with a concise summary of the audited principal findings before submission.

- **INTRO-02** — [100-introduction.tex](../paper/sections/100-introduction.tex):83

  Replace the intended-contribution wording with final, specific findings and the actual scope of the released resource.

- **DES-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):65

  Reconcile the actual 30 run identifiers with all selection lists; recover the 696-to-30 exclusion counts and selection dates. Audit product, affected version, class, ISA, and reference status for every case.

- **DES-02** — [300-study-design.tex](../paper/sections/300-study-design.tex):89

  Recover host and container configuration, image digests, OpenCode commit, tool versions, isolation flags, model providers/snapshots, sampling parameters, and run dates from original records.

- **DES-03** — [300-study-design.tex](../paper/sections/300-study-design.tex):108

  Recover the exact executable prompt and control loop; verify budget enforcement, retry and stop rules, tool permissions, cross-run reset behavior, and whether any operator interventions occurred.

- **AUD-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):143

  Build a run-level evidence manifest, classify missingness, inspect all claimed successes, and sample other strata to detect omitted successes and incorrect negative labels.

- **AUD-02** — [300-study-design.tex](../paper/sections/300-study-design.tex):215

  Freeze and apply the per-class rules, revalidate original target identity and effects, and adjudicate component-level versus documented-entry reproduction. Report control availability and unresolved cases. Do not claim that all controls have already been run.

- **COD-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):240

  Conduct pilot coding; specify analysts, sampling, independent overlap, agreement measures, codebook revisions, and disagreement resolution. This draft does not claim completed multi-analyst validation.

- **ANA-01** — [300-study-design.tex](../paper/sections/300-study-design.tex):256

  Generate outcome and activity-state tables from adjudicated records, document the chosen paired/clustered uncertainty procedure, and report sensitivity to unknown outcomes and incomplete traces.

- **ANA-02** — [300-study-design.tex](../paper/sections/300-study-design.tex):265

  Audit token, billing, timing, and termination records; distinguish zero-priced routes from zero inference use and missing logs from infrastructure failures.

- **RQ1-01** — [400-results.tex](../paper/sections/400-results.tex):50

  Replace the candidate table with adjudicated per-run outcomes, component/documented-entry scope, unknown counts, and CVE-clustered uncertainty; retain candidate counts only if useful for explaining the audit. Examine noncandidate records for false negatives.

- **CASE-01** — [400-results.tex](../paper/sections/400-results.tex):77

  Verify image/component hashes and process identity against the trace; replay a benign and triggering input, and exclude direct proof-file creation by setup or client code.

- **RQ1-02** — [400-results.tex](../paper/sections/400-results.tex):105

  Apply the component-versus-entry distinction to all 16 candidates, including the RouterOS cases; state which result satisfies the final primary outcome and report the narrower results separately.

- **RQ1-03** — [400-results.tex](../paper/sections/400-results.tex):128

  Produce the activity-state matrix and coverage by case and configuration from reviewed artifacts. Identify paths that revisit earlier activities and ensure that progress comes from the same run.

- **RQ1-04** — [400-results.tex](../paper/sections/400-results.tex):147

  Compute paired repetition patterns, identify same-case contrasts, and report both per-run and at-least-one results with their denominators.

- **RQ1-ANS** — [400-results.tex](../paper/sections/400-results.tex):155

  Replace this provisional answer with the audited outcome distribution and repetition findings.

- **RQ2-01** — [400-results.tex](../paper/sections/400-results.tex):177

  Validate acquisition and version-mismatch episodes, including whether alternative sources were tried. Separate unavailable material, temporary access errors, incorrect artifacts, unverified assertions, and missing records; report the cases and runs underlying each count.

- **RQ2-02** — [400-results.tex](../paper/sections/400-results.tex):211

  Code verified startup episodes and their exact error messages, dependency changes, and outcomes. Report ISA and execution-mode coverage where known; examine same-case successes as counterexamples to claims of unavoidable environmental failure.

- **CASE-02** — [400-results.tex](../paper/sections/400-results.tex):237

  Recover the Ghidra invocation, tool output, and termination record if available. Otherwise retain the stopping reason as unknown and exclude this run from claims about responses to observed tool errors.

- **RQ2-03** — [400-results.tex](../paper/sections/400-results.tex):263

  Identify post-startup obstacles among runs with verified original-target execution. Report the eligible subset and analyze protocol, authentication, configuration, and trigger-evidence problems without treating unattempted later activities as observed failures.

- **RQ2-04** — [400-results.tex](../paper/sections/400-results.tex):280

  Produce the reviewed obstacle distribution, denominators, and paired case comparisons. Replace historical failure-family totals with the frozen codebook results; report unresolved and multiply coded episodes.

- **RQ2-ANS** — [400-results.tex](../paper/sections/400-results.tex):293

  Insert the cross-case patterns, their counts, counterexamples, and uncertainty; do not identify a dominant bottleneck from old phase scores.

- **RQ3-01** — [400-results.tex](../paper/sections/400-results.tex):318

  Code response episodes after verified feedback, identify which changes led to new observed states, and compare repair, repetition, alternative execution, and stopping across adequately observed runs.

- **RQ3-02** — [400-results.tex](../paper/sections/400-results.tex):339

  Reconcile 204 versus 209 terminal-label counts, then recode any simulation, first simulation, return to target, and final tested object from primary evidence. Report trace coverage separately for temporal claims.

- **CASE-03** — [400-results.tex](../paper/sections/400-results.tex):367

  Adjudicate the simulation case from source, saved output, and any recoverable trace. Preserve the explicit disclaimer in report coding; do not infer an actual download history from its absence.

- **RQ3-03** — [400-results.tex](../paper/sections/400-results.tex):387

  Select matched same-CVE trajectories with verified time order, including a return-to-target or other counterexample if observed. Plot actual event sequences; do not fabricate a paired contrast from unrelated cases.

- **RQ3-04** — [400-results.tex](../paper/sections/400-results.tex):414

  Cross-tabulate report claims against adjudicated outcomes and target types; audit stop reasons from control-loop records, keeping absent or ambiguous evidence explicit.

- **RQ3-ANS** — [400-results.tex](../paper/sections/400-results.tex):420

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

  Audit and complete the retained case/reference table, recover the executed prompt, and publish coding rules, coverage strata, and completed sensitivity results; keep decisive methods and findings in the main body.
