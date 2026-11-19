# SEC-bench: Automated Benchmarking of LLM Agents on Real-World Software Security Tasks

Hwiwon Lee¹, Ziqi Zhang¹, Hanxiao Lu², Lingming Zhang¹

¹ University of Illinois Urbana-Champaign — {hwiwonl2, ziqi24, lingming}@illinois.edu
² Purdue University — lu525@purdue.edu

*39th Conference on Neural Information Processing Systems (NeurIPS 2025).*

## Abstract

Rigorous security-focused evaluation of large language model (LLM) agents is imperative for establishing trust in their safe deployment throughout the software development lifecycle. However, existing benchmarks largely rely on synthetic challenges or simplified vulnerability datasets that fail to capture the complexity and ambiguity encountered by security engineers in practice. We introduce SEC-bench, the first fully automated benchmarking framework for evaluating LLM agents on authentic security engineering tasks. SEC-bench employs a novel multi-agent scaffold that automatically constructs code repositories with harnesses, reproduces vulnerabilities in isolated environments, and generates gold patches for reliable evaluation. Our framework automatically creates high-quality software vulnerability datasets with reproducible artifacts at a cost of only $0.87 per instance. Using SEC-bench, we implement two critical software security tasks to rigorously evaluate LLM agents' capabilities: proof-of-concept (PoC) generation and vulnerability patching. A comprehensive evaluation of state-of-the-art LLM code agents reveals significant performance gaps, achieving at most 18.0% success in PoC generation and 34.0% in vulnerability patching on our complete dataset. These results highlight the crucial steps needed toward developing LLM agents that are more practical, intelligent, and autonomous for security engineering.

- **Code**: https://github.com/SEC-bench/SEC-bench
- **Dataset**: https://hf.co/datasets/SEC-bench/SEC-bench
- **Leaderboard**: https://sec-bench.github.io

## 1. Introduction

**Security Benchmark for LLM Agents.** Rigorous security benchmarking of LLM agents is imperative as their integration into the software development lifecycle presents both significant opportunities and complex challenges, particularly given our limited understanding of their performance on real-world security tasks [5]. While recent software engineering benchmarks demonstrate impressive progress—with state-of-the-art (SOTA) LLMs advancing from solving less than 2% of SWE-bench issues in 2023 [29] to over 60% success rates today—security tasks remain uniquely challenging due to their inherent complexity and sophisticated reasoning requirements. Pioneering security researchers have already begun exploring LLMs' potential in this domain, as exemplified by Google's projects evaluating agent performance in exploiting vulnerabilities [73] and successfully identifying real-world vulnerabilities in open-source software [58].

**Limitation of Existing Security Benchmarks.** Existing cybersecurity benchmarks inadequately address real-world security challenges due to the absence of automatic methods for constructing verifiable high-quality proof-of-concept (PoC) inputs for in-the-wild vulnerabilities. These PoC inputs are crucial for validating both vulnerabilities and the effectiveness of corresponding patches. This deficiency impedes benchmark scalability and results in questionable data quality. Recent work indicates that existing datasets suffer from inaccuracy in up to 71% of samples [15]. CYBENCH [74] and CVE-BENCH⋄ [77] manually craft a small number of CTF challenges and web application vulnerabilities to evaluate LLM agents, respectively. Specifically, CVE-BENCH⋄ is constrained to specific web frameworks, which facilitates bug reproduction but lacks generalizability. CVE-BENCH⋆ [61] directly reuses the CVEFIXES dataset [12], whose ground truth labels achieve only 51% accuracy [18] due to the lack of a reliable patch verification process.¹ ARVO [37] focuses exclusively on structured bug datasets with pre-validated PoC from OSS-FUZZ [11], neglecting the complex reality of in-the-wild vulnerabilities that security engineers encounter in practice. These limitations prevent existing benchmarks from capturing the complex nature of security engineering, where experts must systematically navigate codebases, identify subtle vulnerability patterns, and develop effective PoC payloads and security patches through continuous interaction with the target environment.

¹ Two distinct projects share the name; we distinguish them as CVE-BENCH⋆ [61] and CVE-BENCH⋄ [77].

**Goal and Challenge of SEC-bench.** We aim to propose a framework to automatically collect and verify real-world CVE instances with reproducible PoC artifacts and validated security patches, creating a benchmark to evaluate LLM agents on authentic security tasks. We aim to satisfy three key qualities: High-Quality vulnerabilities with verified PoCs and precise triggering conditions; Automatic construction requiring minimal manual intervention, facilitating seamless extension with new vulnerabilities; and Realistic scenarios that faithfully reflect security engineering challenges encountered in professional practice. To construct this benchmark, we extract seed instances and corresponding PoC artifacts from public CVE databases [59, 40] with bug reports.

Building reliable security benchmarks presents three intertwined challenges. First, bug reports lack a common schema: analyses of 1.9M GitHub issues reveal that 33% of reports ignore the template [56], while studies across issue tracking systems identify mismatched fields that render automated mining brittle [8]. Second, reproducing vulnerabilities is highly environment-sensitive: even bugs with detailed reproduction steps fail more than half the time without exact matches in compiler flags, library versions, and operating system [39, 49, 35]. Third, public PoCs are frequently insufficient or unreliable: nearly 40% of disclosures lack working PoCs or require manual repair [39], only 4.2% of 75,807 CVE instances have associated public exploit code within a year [26], and researchers identify hundreds of malicious or fake PoCs on GitHub that necessitate rigorous verification [69].

**A Comprehensive Framework for Security Benchmarking.** Addressing these challenges requires an automated approach to standardize diverse vulnerability report formats, configure precise environments, and rigorously verify vulnerability artifacts. We introduce SEC-bench, a comprehensive framework that leverages the complementary capabilities of specialized LLM agents to overcome these obstacles and automate the construction of high-fidelity security benchmarks from real-world vulnerability datasets. Our architecture integrates three specialized modules working in concert:

The Preprocessor systematically selects in-the-wild vulnerability datasets and retrieves heterogeneous bug reports across different platforms, establishing consistent interactive environments for verification. The Verifier deploys specialized LLM multi-agents to automatically reproduce and verify collected instances in controlled environments, rigorously filtering out cases that lack reliable vulnerability reproduction. We focus on memory safety vulnerabilities in C/C++ projects verifiable by sanitizers—a design choice enabling objective, deterministic verification for scalable benchmark construction. The Evaluator transforms verified instances into structured security tasks, packaging them with secure, containerized environments as Docker images that ensure consistent assessment of LLM agent capabilities across diverse security tasks.

**Overall Results.** SEC-bench successfully verifies 200 real-world CVE instances, representing an 85.7% improvement over the SOTA single-agent scaffold, CODEACT [62]. Our framework is automatic and self-evolving with minimal manual effort, and can be easily extended to support diverse security tasks with additional vulnerability types. When evaluated on our verified datasets, SOTA code agents—SWE-agent [70], OpenHands [63], and Aider [6]—achieve at most 18.0% success in PoC generation and at most 34.0% in vulnerability patching, demonstrating the challenging nature of our benchmark and significant room for improvement in LLM agents' security capabilities.

**Key Contributions.** Our work makes three primary contributions:

- We develop the first general multi-agent scaffold for constructing practical and scalable security benchmarks that can automatically reproduce vulnerabilities from real-world repositories.
- We formulate challenging and realistic security tasks based on our benchmark, focusing specifically on PoC generation and vulnerability patching, reflecting security engineering workflows.
- We conduct comprehensive evaluations of state-of-the-art LLM code agents on our benchmark, demonstrating their capabilities and limitations in solving real-world security challenges.

## 2. SEC-bench

### 2.1. Overview

SEC-bench consists of three modules: a preprocessor module, a verifier, and an evaluator module, as illustrated in Figure 1. The preprocessor module collects instances from public CVE databases and extracts essential metadata such as reference URLs and repository information. It then constructs interactive environments using Docker containers for verifying the collected instances.

Our verifier, SECVERIFIER, works to reproduce and validate the collected vulnerability instances. For an instance to be considered successfully verified, it must have a reliable project configuration, a functional proof-of-concept (PoC), and a reliable patch that resolves the vulnerability.

The evaluator module builds upon verified instances by creating Docker images with all necessary artifacts. It then formulates specific security engineering tasks that challenge LLM agents to solve real-world security problems, mirroring the workflows of professional security engineers.

Memory safety sanitizers [50] detect vulnerabilities with call stack information by instrumenting code with memory access monitoring checks, commonly used in open-source projects. We establish sanitizer verdicts as our oracle—accepting PoC only when they trigger expected reports and validating patches when these reports disappear. This design choice prioritizes objective verification: sanitizers provide deterministic validation without subjective judgment, enabling scalable benchmark construction with reliable ground truth. This approach aligns with DARPA AIxCC's methodology, which similarly uses sanitizers as the ground truth for assessing vulnerability discovery and repair [16].

> **Figure 1.** Overview of SEC-bench.

### 2.2. Preprocessor

SEC-bench targets CVE instances in open-source C/C++ projects that can be verified using memory safety sanitizers. We focus on C/C++ projects due to their prevalence in critical infrastructure and their susceptibility to memory safety vulnerabilities.

**Step 1: Metadata Collection.** We begin by collecting CVE instances from the OSV database [59], a comprehensive, distributed, and open database cataloging vulnerabilities in open-source software. From this source, we extract essential metadata including vulnerability descriptions, reference URLs, provider information, and repository details. This initial collection yields 38,201 potential instances spanning 7,926 open-source projects.

**Step 2: Bug Report and Candidate Fix Extraction.** For each instance, we implement customized web scraping tools to gather vulnerability reports from diverse bug tracking platforms (e.g. GitHub Issues, RedHat Bugzilla [25], Chromium Issue Tracker [24]). These reports often contain crucial information about vulnerability reproduction methods and potential fixes. We adapt configuration files from the OSS-FUZZ project [11] to accommodate different project requirements, resulting in 4,836 instances with sufficient documentation.

**Step 3: Environment Configuration.** We construct interactive environments where each instance can be reliably verified. Rather than using a one-size-fits-all approach, we create customized Docker configurations with project-specific dependencies and settings. To streamline the verification process, we develop a harness designed for LLM agents to build projects, execute PoCs, and validate patches with ease. The harness enables efficient vulnerability verification by allowing LLM agents to focus on the core task without being distracted by unessential environmental details. After filtering for instances where sanitizer-generated reports are available, we retain 898 instances as candidates.

### 2.3. Verifier

SECVERIFIER works with the environments and bug reports prepared by the preprocessor to verify vulnerabilities through reproduction. Figure 1 illustrates our multi-agent verification framework, which decomposes the complex verification process into three sequential subtasks managed by specialized agents and coordinated by a manager agent.

**Manager Agent.** The manager agent oversees the verification process by coordinating specialized sub-agents: builder, exploiter, and fixer. It assigns tasks, tracks their progress, and ensures effective communication among agents. After each task, the manager evaluates outputs against predefined objectives. If results do not meet the required standards, the manager provides targeted feedback and reassigns the task to the appropriate sub-agent for improvement. This iterative process continues until all verification criteria are met or a maximum number of iterations is reached, ensuring robustness even with complex vulnerabilities or unclear bug reports.

**Builder Agent.** The builder agent ensures that the vulnerable code repository can be successfully compiled in the target environment. It systematically builds the project, diagnoses and resolves compilation errors, and refines the harness for reliable project compilation. The builder outputs ❶ an optimized build script, ❷ a dependency list, and ❸ a patch file addressing compilation issues.

**Exploiter Agent.** The exploiter agent creates or validates a functional PoC artifact that demonstrates the vulnerability. It analyzes bug reports to extract or construct the PoC, even when information is incomplete or inaccurate. The agent identifies PoC-related content, downloads or adapts available PoC files, validates the exploit by execution, and documents the commands required to reproduce the vulnerability. In rare cases when no available PoC is found, the agent attempts to generate one from scratch by analyzing the root cause, vulnerability patterns, and affected code paths, though this remains challenging due to the complexity of crafting precise exploit inputs. The final artifact consists of ❶ a functional PoC input and ❷ the command sequence needed to trigger it.

**Fixer Agent.** The fixer agent synthesizes a unified patch that addresses the vulnerability. Because fixes often span multiple commits, mixing relevant and unrelated changes, the agent analyzes candidate fix commits to isolate only the vulnerability-related modifications. It then consolidates these changes into a single comprehensive patch file. If no appropriate fix commits are available or existing fixes fail, the agent independently devises a patch by investigating the underlying vulnerability and tracing the relevant code paths. The agent validates the patch by ensuring it prevents the PoC from triggering the vulnerability while preserving original functionality.

### 2.4. Evaluator

The evaluator module transforms verified vulnerability instances into structured benchmarks for assessing LLM capabilities in security tasks. For each verified instance, we create a clean Docker image containing the vulnerable codebase, environment configurations, and essential artifacts from the verification process. We formulate two challenging and critical security tasks that mirror real-world security engineering workflows: PoC generation and vulnerability patching [30, 48, 16, 68, 17].

Note that more challenging security tasks can be formulated on top of our benchmark, such as fuzz driver generation [76, 67, 36] and vulnerability discovery [55, 20, 75].

**PoC Generation.** The first task challenges LLM agents to create a working PoC for a known vulnerability, given only a basic vulnerability description with a sanitizer-generated report and access to the codebase. This tests an agent's ability to understand vulnerability descriptions, analyze codebases, and craft specific inputs that trigger the vulnerability. Evaluation uses execution-based metrics where a successful solution must produce a PoC that, when executed, triggers the sanitizer to report the correct vulnerability type at expected locations.

**Vulnerability Patching.** The second task requires agents to create security fixes for known vulnerabilities given a vulnerability description, access to the codebase, and a working PoC. This evaluates an agent's capacity to understand root causes and create reliable security patches. Our multi-stage evaluation process first applies the generated patch, then compiles the patched code to ensure successful project build, and finally executes the original PoC against the patched codebase to confirm mitigation. Success requires meeting two criteria: a valid patch that compiles correctly and prevents the sanitizer from reporting the vulnerability.

### 2.5. Manual Verification

To ensure benchmark quality, we manually inspect all verified instances to eliminate low-quality cases. This manual inspection process is critical for benchmark reliability and is adopted by various state-of-the-art benchmarks, such as Multi-SWE-bench [72], SWE-bench Verified [42], and SWE-bench Lite S [66]. Two authors with over five years of security engineering experience conduct the inspection process, focusing on two key aspects: bug reports and patches. This rigorous quality control ensures that our benchmark accurately reflects real-world security engineering challenges without artificial shortcuts or oversimplified scenarios.

**Bug Report Inspection.** We examine whether bug reports contain official patch information, such as patch commits or code snippets. When reports include such information, agents can exploit this by directly copying patch code or applying commits. This occurs in reports constructed from GitHub issues, where developers discuss with reporters and provide patch candidates. Such instances fail to correctly evaluate agent patch generation capabilities and compromise the integrity of the benchmark. To prevent this issue, we inspect all bug reports and remove directly provided patches while preserving essential context. We maintain discussions between developers and bug reporters, as real-world security engineers often require this collaborative information to generate effective patch candidates. This careful curation ensures that agents must demonstrate genuine vulnerability understanding rather than relying on simple copy-paste strategies.

**Patch Inspection.** We verify that patches can fix vulnerabilities without employing superficial solutions like simply removing vulnerable code. Additionally, we check patch applicability to the instance environment and verify vulnerability resolution. Some patches originate from commits too distant from the base commit, preventing successful application. These issues require systematic revision to maintain benchmark quality and reliability.

We perform three rounds of manual patch inspection to address these challenges systematically.

**Round 1:** We validate agent-generated patches by reviewing patch content and comparing with official patches. This ensures patches do not simply remove vulnerable code without proper fixes. Patches generally consistent with official patches proceed to the next round.

**Round 2:** We use automated scripts to verify patch applicability and vulnerability resolution. We consider patches correct if: ❶ the PoC triggers sanitizer errors at the base commit, ❷ the patch applies successfully to the base commit, and ❸ the PoC fails to trigger sanitizer errors at the patched commit. This round identifies 17 problematic instances for correction.

**Round 3:** We manually adjust base commits for problematic instances. We locate official patch commits from the NVD database [40] and iterate backwards from patch commits to base commits. For each commit, we verify the three conditions above. Commits satisfying these conditions become new base commits, and we update instance information through systematic revision.

Our comprehensive inspection process ensures all instance patches can be successfully applied to the environment, fix vulnerabilities effectively, and avoid superficial removal of vulnerable code.

### 2.6. Statistics of SEC-bench

Three tasks have different levels of difficulty. The success rates of the builder, exploiter, and fixer agents are 81.7%, 39.4%, and 69.2%, respectively. Note that each agent is executed sequentially, meaning that if the previous agent fails, the next agent will not be executed. The building step is the easiest, as project documentation is usually well-structured and actively maintained. The builder can readily understand the project structure and build the project. The exploiter step is the most difficult and has the lowest success rate because PoCs are not always provided in bug reports, and when available, the information can be inaccurate or obsolete. In such cases, the exploiter agent must understand the bug reports and generate the PoC from scratch. The fixer step is also challenging, as there may be multiple candidate commits to fix the vulnerability. The fixer agent needs to understand all commits and generate a unified patch. Even worse, official fix commits can sometimes introduce new vulnerabilities, further complicating the generation of a reliable patch [1].

Success rate varies across different projects. upx and php have low rates of 12.0% and 4.2%, respectively. The bottleneck of upx is the exploiter agent (16.7%). We find that many upx bug reports lack detailed reproduction steps and contain complex binary compression vulnerabilities that require specialized domain knowledge. Similarly, php suffers from an extremely low exploiter success rate of 9.7%. The php codebase is one of the largest in our dataset and has a complex architecture with numerous interdependencies. Its security issues often involve intricate language interpreter vulnerabilities that require deep understanding of PHP's internals. In contrast, faad2, mruby, and njs demonstrate much higher success rates over 40%. These projects benefit from a consistent codebase structure and well-documented vulnerabilities, with impressive exploiter success rates above 66.0%.

**Comparison of SEC-bench and SWE-bench Instance Statistics.** Table 2 shows the code statistics of SEC-bench instances. The projects have an average of 563.6 files, which is 18.7% of the file count in SWE-bench [70] (3,010 files). However, SEC-bench has 482K lines of code, which is 10.1% more than SWE-bench (438K lines on average). For issue length, SEC-bench has an average of 921.1 words, 4.7× larger than SWE-bench (195.1 words). It's because SEC-bench focuses on real-world CVE instances with sanitizer bug reports, which typically include detailed crash information with call stacks. For gold patch size, SEC-bench has an average of 17.3 lines, 1.3 files, and 1.6 functions, which are smaller than those of SWE-bench (32.8 lines, 1.7 files, and 3 functions).

**Table 1.** Overall performance of SECVERIFIER in verifying vulnerability instances. Out of 898 seed instances, SECVERIFIER successfully verifies 200 instances. The table shows statistics for the 29 projects that contain at least one verified instance.

| Projects | # Seed | # Verified | Overall (%) | Builder (%) | Exploiter (%) | Fixer (%) | Avg Cost ($) | Avg Steps |
|---|---|---|---|---|---|---|---|---|
| gpac | 147 | 43 | 29.3 | 68.7 | 45.5 | 93.5 | 0.91 | 62.5 |
| imagemagick | 116 | 31 | 26.7 | 94.8 | 35.5 | 79.5 | 0.82 | 63.8 |
| mruby | 34 | 21 | 61.8 | 97.1 | 78.8 | 80.8 | 0.61 | 50.5 |
| libredwg | 71 | 20 | 28.2 | 91.5 | 55.4 | 55.6 | 1.01 | 68.2 |
| njs | 40 | 17 | 42.5 | 75.0 | 66.7 | 85.0 | 0.56 | 55.1 |
| faad2 | 20 | 12 | 60.0 | 100.0 | 75.0 | 80.0 | 0.60 | 50.4 |
| exiv2 | 43 | 10 | 23.3 | 88.4 | 47.4 | 55.6 | 0.87 | 66.0 |
| matio | 19 | 7 | 36.8 | 100.0 | 68.4 | 53.8 | 1.20 | 64.0 |
| openjpeg | 29 | 5 | 17.2 | 100.0 | 27.6 | 62.5 | 0.76 | 76.7 |
| upx | 25 | 3 | 12.0 | 96.0 | 16.7 | 75.0 | 0.91 | 78.0 |
| yara | 11 | 3 | 27.3 | 100.0 | 36.4 | 75.0 | 0.73 | 64.6 |
| libarchive | 8 | 3 | 37.5 | 100.0 | 37.5 | 100.0 | 0.58 | 45.8 |
| md4c | 6 | 3 | 50.0 | 83.3 | 60.0 | 100.0 | 0.50 | 51.3 |
| openexr | 4 | 3 | 75.0 | 75.0 | 100.0 | 100.0 | 0.59 | 55.8 |
| php | 48 | 2 | 4.2 | 64.6 | 9.7 | 66.7 | 1.17 | 59.4 |
| libiec61850 | 18 | 2 | 11.1 | 83.3 | 40.0 | 33.3 | 1.17 | 75.4 |
| libheif | 10 | 2 | 20.0 | 70.0 | 28.6 | 100.0 | 0.81 | 64.5 |
| libdwarf | 3 | 2 | 66.7 | 100.0 | 66.7 | 100.0 | 0.64 | 47.3 |
| liblouis | 14 | 1 | 7.1 | 28.6 | 50.0 | 50.0 | 1.01 | 78.3 |
| libsndfile | 9 | 1 | 11.1 | 66.7 | 50.0 | 33.3 | 0.75 | 57.0 |
| qpdf | 7 | 1 | 14.3 | 100.0 | 14.3 | 100.0 | 1.01 | 77.1 |
| libxls | 7 | 1 | 14.3 | 57.1 | 75.0 | 33.3 | 0.87 | 69.0 |
| libplist | 6 | 1 | 16.7 | 100.0 | 33.3 | 50.0 | 0.65 | 61.3 |
| libjpeg | 6 | 1 | 16.7 | 100.0 | 33.3 | 50.0 | 0.76 | 60.0 |
| wabt | 6 | 1 | 16.7 | 50.0 | 66.7 | 50.0 | 0.77 | 62.7 |
| yaml | 5 | 1 | 20.0 | 80.0 | 75.0 | 33.3 | 0.89 | 63.6 |
| jq | 1 | 1 | 100.0 | 100.0 | 100.0 | 100.0 | 0.64 | 58.0 |
| libmodbus | 1 | 1 | 100.0 | 100.0 | 100.0 | 100.0 | 0.63 | 35.0 |
| readstat | 1 | 1 | 100.0 | 100.0 | 100.0 | 100.0 | 0.49 | 40.0 |
| Total/Avg | 898† | 200 | 22.3 | 81.7 | 39.4 | 69.2 | 0.87 | 66.3 |

**Table 2.** Statistics of SEC-bench task instances showing average and maximum values for key attributes. Values represent micro-averages across all instances without repository-level grouping.

|  | Mean | Max |
|---|---|---|
| Issue Text — Length (Words) | 921.1 | 4406 |
| Codebase — # Files (non-test) | 563.6 | 3015 |
| Codebase — # Lines (non-test) | 482K | 2.02M |
| Gold Patch — # Lines edited | 17.3 | 650 |
| Gold Patch — # Files edited | 1.3 | 11 |
| Gold Patch — # Func. edited | 1.6 | 11 |

**Table 3.** Comparison between SECVERIFIER and CODEACT on 50 randomly selected instances across 23 projects from SEC-bench. SECVERIFIER achieves an 85.7% higher overall success rate than CODEACT, with substantial improvements in both builder and fixer agents.

| Type | Overall (%) | Builder (%) | Exploiter (%) | Fixer (%) | Avg. Steps / Cost ($) |
|---|---|---|---|---|---|
| CODEACT | 14.0 | 72.0 | 33.3 | 58.3 | 60.5 / 0.72 |
| SECVERIFIER | 26.0 | 90.0 | 35.6 | 81.2 | 64.4 / 0.82 |

**Ablation on Multi-Agent Framework.** We compare SECVERIFIER with a single-agent baseline, CODEACT [62], which is built on top of the same agent framework, OpenHands [63], and allows a controlled comparison that isolates the impact of our multi-agent approach while eliminating confounding variables. We evaluate on 50 randomly selected instances from SEC-bench across 23 projects. As shown in Table 3, SECVERIFIER achieves a success rate of 26.0% while CODEACT only achieves 14.0%. SECVERIFIER outperforms CODEACT by 85.7% in overall success rate. SECVERIFIER demonstrates superior performance across all agent components. The improvements of the fixer and builder are 22.9% and 18.0%, respectively. The multi-agent framework effectively decomposes and solves complex security tasks, demonstrating its advantage over single-agent approaches with only slightly more steps and cost.

## 3. Evaluation

### 3.1. Experimental Setup

**Agents and Models.** To comprehensively measure LLM agent capabilities in security tasks, we select three SOTA code agents: SWE-agent [70], OpenHands [63], and Aider [6]. We also choose three strong representative models: Claude 3.7 Sonnet [9], GPT-4o [41], and o3-mini [44].

**Tasks for Evaluation.** We formulate two critical security tasks, PoC generation and vulnerability patching, to systematically evaluate LLM agent capabilities in addressing real-world security vulnerabilities. Due to budget constraints, we evaluate the best-performing agent on the full dataset, while a detailed comparison among all agents is conducted using 80 representative instances from SEC-bench. For PoC generation, we provide the vulnerability description, harnesses, and the codebase within a Docker environment. For vulnerability patching, we provide the vulnerability description with call stack information, harnesses, and the codebase within a Docker environment.

### 3.2. Performance of LLM Agents in Security Tasks

**Main Results.** We evaluate Claude 3.7 Sonnet with the three agent scaffolds on the full dataset of 200 instances for both tasks, with results displayed on our leaderboard.² The reason to select Claude 3.7 Sonnet is that it has better performance than other models in our evaluation over a random selected 80-instance subset. Results from the full dataset evaluation show that SWE-agent and OpenHands are comparable, both achieving over 30% success rate on vulnerability patching and over 10% success rate on PoC generation. The highest success rate on PoC generation is 18.0% and on vulnerability patching is 34.0%.

² https://sec-bench.github.io

**Table 4.** Overall performance of code agents on PoC generation and vulnerability patching tasks across different LLMs and agent scaffolds, evaluated on 80 instances from 13 projects.

| Task | Model | SWE-agent % Resolved | SWE-agent $ Avg. Cost | OpenHands % Resolved | OpenHands $ Avg. Cost | Aider % Resolved | Aider $ Avg. Cost |
|---|---|---|---|---|---|---|---|
| Patch | Claude 3.7 Sonnet | 33.8 | 1.29 | 31.2 | 0.61 | 20.0 | 0.44 |
| Patch | GPT-4o | 26.2 | 0.48 | 15.0 | 1.53 | 11.2 | 0.29 |
| Patch | o3-mini | 31.2 | 0.13 | 12.5 | 0.15 | 17.5 | 0.15 |
| PoC | Claude 3.7 Sonnet | 12.5 | 1.52 | 8.8 | 1.56 | 1.2 | 0.21 |
| PoC | GPT-4o | 3.8 | 0.56 | 2.5 | 1.51 | 0.0 | 0.22 |
| PoC | o3-mini | 10.0 | 0.13 | 5.0 | 0.19 | 1.2 | 0.04 |

**Table 5.** Performance comparison on security tasks before (≺ KC) and after (≻ KC) the knowledge cutoff (KC) date, using GPT-4o and Claude 3 Haiku with the SWE-agent scaffold as baseline. R and S represent the resolved rate (%) and submitted rate (%), respectively.

| Cutoff | PoC, GPT-4o R | PoC, GPT-4o S | PoC, Claude 3 Haiku R | PoC, Claude 3 Haiku S | Patch, GPT-4o R | Patch, GPT-4o S | Patch, Claude 3 Haiku R | Patch, Claude 3 Haiku S |
|---|---|---|---|---|---|---|---|---|
| ≺ KC | 6.7 | 100 | 0 | 33.3 | 33.3 | 100.0 | 20.0 | 86.7 |
| ≻ KC | 0 ↓ 6.7 | 100 | 0 | 26.7 ↓ 6.6 | 40.0 ↑ 6.7 | 93.3 ↓ 6.7 | 13.3 ↓ 6.7 | 93.3 ↑ 6.6 |

**Impact of Agent Scaffolds and Models.** We study the detailed impact of agent scaffolds and models on the 80-instance subset and present results in Table 4. In addition, to guarantee the stability of our evaluation, we select SWE-agent and o3-mini as the representative agent and model, and repeat the experiments five times. The average success rate is 30.0% with a standard deviation of 7.9%, demonstrating the validity of the reported values. SWE-agent and OpenHands achieve comparable performance. SWE-agent achieves a 33.8% successful patch rate and 12.5% PoC resolve rate on the 80-instance subset, while OpenHands achieves a 34.0% successful patch rate and 18.0% PoC resolve rate on the 200-instance full dataset. Aider shows consistently lower performance across models and tasks. SWE-agent's agent-computer interface [70] and OpenHands' AgentSkill [63] library enable these agents to better utilize tools, understand codebases, and reason about vulnerabilities.

**Challenges of Security Tasks.** We can observe that both PoC generation and vulnerability patching in our benchmark present significant challenges. For PoC generation, most vulnerabilities involve memory-access violations that require precisely crafted, byte-level payloads to trigger. Such payloads demand sophisticated reasoning about runtime memory layouts and execution paths—capabilities that current LLMs lack despite their strengths in natural language and source code. Existing models trained predominantly on textual data rather than low-level binary operations, struggle to generate effective exploits that must interact with program memory at the byte level, explaining their poor performance even when deployed as agents. Note that for patch generation, we provide vulnerability call stack information which often hints at which files and functions to review, but agents still struggle to generate correct patches, highlighting the complexity of the task. This stands in stark contrast to recent advances in general software engineering tasks, where models like Claude 3.7 Sonnet achieve over 60% resolve rate on SWE-bench verified [57, 9]. The significant performance gap highlights the unique complexity of security tasks, which require agents to: ❶ identify and understand vulnerability root causes within broader codebase context, ❷ thoroughly analyze data and control flow to trace attack vectors, and ❸ implement precise fixes that eliminate vulnerabilities while preserving functionality and avoiding security regressions.

**Data Contamination.** Data contamination occurs when evaluation instances overlap with an LLM's training data, potentially inflating performance metrics through memorization rather than reasoning. We randomly select 15 instances before and 15 instances after the LLM's knowledge cutoff (KC) date based on CVE reserved dates. The submitted rate (S) reflects the proportion of successfully submitted instances, regardless of its correctness. The resolved rate (R) measures the proportion of successfully solved instances. We test GPT-4o (KC: Sep 2023) and Claude 3 Haiku (KC: Aug 2023) due to their early KC dates, enabling evaluation on more instances after KC. Table 5 shows neither model performs consistently better on pre-cutoff data. For PoC generation, post-cutoff data shows a lower resolve rate on GPT-4o (6.7%) and lower submission rate on Haiku (6.6%). For patching, GPT-4o achieves a 6.7% higher resolve rate on post-cutoff data compared to pre-cutoff data, while Haiku exhibits a 6.7% lower resolve rate after the cutoff. We also calculate the per-pair difference between pre- and post-cutoff data and apply the Wilcoxon signed-rank test [65]. The resulting p-value of 0.27 indicates no significant difference between the two groups.

### 3.3. Failure Analysis

This section analyzes failure cases to provide insights for future agent design. For vulnerability patching, we classify failures into four categories: No Patch (NP), Improper Format (IF), Compilation Error (CE), and Still Vulnerable (SV). Figure 2 presents the failure type distribution across different code agents and their underlying models. As shown in the figure, SWE-agent predominantly struggles with CE and SV across all models, with o3-mini showing the highest number of CE cases. OpenHands exhibits a distinct pattern with IF being the dominant failure type, representing 62.18% of its total failures. In contrast, Aider exhibits a higher proportion of NP failures, especially when paired with GPT-4o, while completely avoiding IF failures across all models due to its Git integration that ensures proper patch formatting and version control.

> **Figure 2.** Failure types in vulnerability patching. NP (No Patch): the agent fails to generate any patch; IF (Improper Format): the generated patch has an incorrect format; CE (Compilation Error): the patch causes the repository to fail compilation; SV (Still Vulnerable): the patch compiles but does not successfully remediate the security vulnerability when tested.

NP is caused by large code contexts that exceeds token budget. The agents are required to review many files repeatedly, guided by sanitizer reports and multiple command executions. IF arises when agents generate excessively large patches due to iterative attempts, which increases the risk of formatting errors. OpenHands tends to produce longer patches; for example, in gpac.cve-2023-0358 [2], OpenHands modified about 7,000 lines, while patches from SWE-agent and Aider are under 10 lines. CE occurs when patches introduce defects like mismatched types or pointer dereference errors. After multiple attempts to resolve such compilation issues, agents reach cost or iteration limits. SV happens when agents misidentify the root cause of a vulnerability. For example, in mruby.cve-2022-1201 [3], SWE-agent attributes the issue to one file, while the gold patch addresses three distinct files.

For PoC generation, the overall performance is low due to the difficulty of generating effective payloads requiring precise byte-level interactions with program memory. The main failure reasons include: First, many codebases contain numerous files, making it challenging to efficiently analyze the data flow necessary to trigger the vulnerability. Second, the absence of a dedicated usage of harness often results in excessive and irrelevant outputs (e.g. lengthy build logs), which obscure critical information needed for exploit development. Third, failure to utilize a debugger significantly impedes the ability to craft precise exploit payloads, as interactive inspection and stepwise execution are essential for understanding program state and memory layout at the point of vulnerability.

## 4. Related Work

**Cybersecurity Benchmarks.** Researchers have developed various security benchmarks that can be categorized into two types: CTF-based and vulnerability-based. CTF-based benchmarks (e.g. NYU CTF BENCH [53] and CYBENCH [74]) use CTF challenges to test LLMs' skills, but may not reflect real-world vulnerability scenarios and are difficult to scale due to manual construction requirements. These benchmarks require human annotators to construct tasks from CTF challenges, which requires expertise and manual effort. Vulnerability-based benchmarks are constructed from public vulnerability databases. BIGVUL [22] and PRIMEVUL [19] cover various CWE categories, but do not provide reproducible CVE instances. CVE-BENCH⋄ [77] and SECLLMHOLMES [60] manually craft a small number of CVE instances, making them difficult to scale. CVE-BENCH⋆ [61] is based on CVEFIXES [12] but suffers from low label accuracy [19]. ARVO [37] focuses on structured bug datasets but is not scalable to in-the-wild CVE instances. AutoPatchBench [38] is a recent benchmark for the automated repair of vulnerabilities identified through fuzzing. CyberSecEval2 benchmark utilizes synthetic programs [13]. These benchmarks either suffer from limited scale, reproducibility issues, or unrealistic vulnerability scenarios. SEC-bench utilizes multiple agents to construct the benchmark by automatically collecting reproducible and practical CVE instances with high-quality PoCs and reliable patches. SEC-bench does not rely on manual construction and is capable of scaling to a large number of CVE instances and newly discovered vulnerabilities.

**Software Engineering Benchmarks.** Software engineering (SE) represents a significant application domain for LLMs [70], and numerous benchmarks have been developed. SWE-BENCH [29] and its variants [42, 7, 70] leverage real-world bug-fixing issues collected from GitHub repositories. Multi-SWE-bench [72] and SWE-PolyBench [46] extend SWE-BENCH to include issues in multiple programming languages, enhancing the diversity and difficulty of the benchmark. Other benchmarks, including HUMANEVAL [14], MBPP [47], BIGCODEBENCH [78], LIVECODEBENCH [27], and EVALPLUS [31, 32], are constructed using programming problems. These SE benchmarks primarily focus on code generation and bug fixing tasks, which are relatively straightforward compared to security tasks. In contrast, SEC-bench targets real-world security tasks that require a deeper understanding of complex codebases and vulnerability patterns, presenting a more challenging and realistic evaluation of LLM agents in the security domain compared to conventional SE benchmarks.

**Code Agents.** Researchers have actively employed LLM-based agents to address coding tasks [33]. SWE-agent [70] and ENIGMA [4] introduce agent-computer interfaces for environment interaction. Aider [6] offers an interface for AI pair programming. AGENTLESS [66] proposes a two-stage framework for solving SE tasks. SWE-RL [64] applies GRPO [54] to improve agents' reasoning abilities. SWE-GYM [45], R2E-GYM [28], and SWE-smith [71] provide interactive training environments for SE tasks. Major technology companies, including Google [23], Anthropic [10], OpenAI [43], and ByteDance [34], have also launched significant projects in the code agents domain.

## 5. Limitations and Future Work

SEC-bench mainly has two limitations. First, we focus on C/C++ projects due to the reliability of memory safety sanitizers in C/C++. This is an intentional design choice that provides objective verification rather than a limitation in methodology. Although already challenging enough, extending SEC-bench to other languages would be a significant advancement. We can adapt SECVERIFIER to leverage language-specific sanitization and testing tools, similar to how OSS-FUZZ has expanded beyond C/C++ to Java, Python, Go, and Rust. Second, our current implementation covers a specific subset of vulnerability types detectable by memory safety sanitizers. This design enables deterministic, automated validation without subjective judgment, ensuring scalable benchmark construction. Our approach is generalizable to a wider range of vulnerabilities, and we aim to support them in future work. Developing additional verification methods beyond sanitizer tools would enable handling a broader spectrum of vulnerability classes, particularly those in web applications, operating system kernels, and distributed systems.

## 6. Conclusion

We propose SEC-bench, a comprehensive benchmarking framework for evaluating LLM agents on security engineering tasks. Our multi-agent SECVERIFIER processes, reproduces, and verifies software vulnerabilities, creating high-quality benchmarks from unstructured bug reports. Our evaluation reveals significant performance gaps in SOTA code agents, and we hope SEC-bench will establish consistent standards to accelerate development of more capable security engineering agents.
