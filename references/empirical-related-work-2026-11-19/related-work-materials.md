# Related Work 介绍素材（供审阅）

本文件介绍前人做了什么，不固定我们论文的结构或贡献。引用键对应 [references.bib](references.bib)。全部内容仍需作者按最终采用的稿件版本核对；没有将不同设置的成功率放到同一排行榜。

## 1. 漏洞复现的信息与上下文条件

Mu 等通过人工复现实验和专业人士调查，研究公开漏洞报告的信息缺失、资料聚合和复现困难。Zhao 等进一步面向 LLM 生成 Web 漏洞 PoC，比较描述、补丁和代码上下文，并分解攻击内容构造、路径导航和最终 PoC 组装。二者都将复现结果放在具体信息条件下讨论，但前者以人工分析为对象，后者预先准备目标环境，均不等同于 CVE-only 的固件重托管任务。

**英文素材：**

> Vulnerability reproduction depends on the information and execution prerequisites available to the analyst. Mu et al. investigated the reproducibility of crowd-reported vulnerabilities through controlled analyst experiments and a survey of security professionals, examining missing report information and the limits of aggregating public references. Zhao et al. studied LLM-based PoC generation for web vulnerabilities under progressively richer disclosure artifacts, and analyzed failures in payload construction and navigation to vulnerable functionality. These studies examine different reproduction settings: report-driven manual reproduction and PoC generation against prepared web environments, respectively.

引用：`mu2018crowdrepro`、`zhao2025webpocstudy`。

## 2. 安全 agent 的实际执行与失败行为

Shao 等比较人工交互和自动 CTF 工作流，分类实际解题错误。Happe 和 Cito 在企业 AD 网络中结合执行统计与专家主题分析，观察任务传递、遗漏信息和错误恢复。Huang 等比较不同渗透测试架构的功能属性和失败模式。Probst 等由本地 agent 的轨迹归纳失败类别，再比较针对性的增强。它们涵盖不同程度的人类帮助和专用系统，介绍时应分别说明。

**英文素材：**

> Empirical evaluations have also examined how security agents act rather than reporting final outcomes alone. Shao et al. compared human-in-the-loop and automated CTF-solving workflows and categorized unsuccessful outputs. Happe and Cito combined quantitative execution data with expert thematic analysis in Active Directory penetration testing. Huang et al. investigated recurring failures and functional augmentations across penetration-testing architectures, while Probst et al. connected local agents' failure patterns to interventions evaluated in a shared privilege-escalation harness. These studies differ in their human involvement, agent interfaces, and task assumptions.

引用：`shao2024offensivestudy`、`happe2026enterprisenetworks`、`huang2025capabilitiesperformance`、`probst2026localprivesc`。

## 3. 阶段依赖、接口与重复运行

Yu 等通过提供正确漏洞上下文，将侦察与利用的评价分开。Singer 等从多主机基线系统的失败分析出发提出 Incalmo，以高层任务接口与领域执行服务支持攻击。Erdem 则固定目标进行重复运行，分析停止与故障差异。三个方向分别研究阶段前提、系统抽象和运行间波动；不能把结果都称为模型自身能力。

**英文素材：**

> Other work examines dependencies across attack stages and runs. Yu et al. separated reconnaissance from exploitation by injecting vulnerability context after failed reconnaissance. Singer et al. used failure analysis of multi-host offense systems to motivate Incalmo's higher-level planning and execution interfaces. Erdem investigated variability across repeated runs against a fixed multi-service target, distinguishing premature termination and iteration limits from upstream API failures. These evaluations characterize stage prerequisites, interface design, and operational variability under distinct experimental conditions.

引用：`yu2026decoupling`、`singer2026incalmo`、`erdem2026consistency`。

## 4. 结果正确性与评价方法背景

SecLLMHolmes 将安全判断与解释、重复性和代码变换结合研究。CodeRover-S 区分通过触发输入测试的修复、人工认为正确的修复和项目实际采纳。Happe 和 Cito 的评估实践综述梳理测试环境、基线、指标与轨迹分析方式。前两者提供具体实验，后者作为方法综述引用，不能替代原始实验来源。

**英文素材：**

> Evaluation validity is another focus of empirical security research. SecLLMHolmes studied the consistency, explanations, and robustness of LLM vulnerability judgments. In agentic vulnerability repair, Zhang et al. distinguished patches that pass the triggering-input test from patches judged correct through manual inspection and those accepted by maintainers. Complementing these experiments, Happe and Cito reviewed evaluation practices in LLM-driven offensive security, discussing testbed provenance, baselines, metrics, and qualitative trajectory analysis.

引用：`ullah2024secllmholmes`、`zhang2026ossfuzzrepair`、`happe2025offensivepractices`。

## 使用时的注意点

- 不把上述四组直接等同于最终正文的四个小节；这是介绍素材的分组。
- 预印本明确标明状态，不用“顶会证明”概括其结论。
- CTF 靶机、Web CVE、内存错误、AD 网络和固件样本属于不同实验单位。
- 对方法论文中的模型解释或“根因”判断，使用 studied / observed / attributed 等与证据强度相称的表述。
- 不用 these studies all assume a prepared environment 一句覆盖全部工作；应逐篇说明系统和 agent 各自承担哪些准备步骤。
