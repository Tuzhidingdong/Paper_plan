# Paper_plan 全局科学分析能力开发计划

**Plan version:** 1.0  
**基线分支：** v5.1/researcher-facing-product  
**基线提交：** 401d2043261fb4c09c1793378ff03215923ee211  
**开发分支：** feat/general-scientific-evidence-analysis  
**交付模式：** Code/files only；不合并到 V5.1、不发布；准备 release candidate，等待用户批准后再发布。  
**当前状态：** 通用分析引擎、记录器、验证/上下文接入、Skill 主入口/工作流和合成测试已实施；Python 3.10/3.11/3.12 各 155 项全量测试通过。源码通用性审查完成；Release candidate 已准备。真实项目黑盒验收尚未执行。

---

## Follow-on implementation: spectral and diffraction evidence (2026-11)

The follow-on branch `feat/spectral-analysis-capability` is based on the release-candidate commit `aff67d386109760e3a5267f3d574707878de1b53` and does not modify the parent RC branch.

It adds four engineering capabilities identified by the real-project root-cause audit:
1. retain per-cluster vector figure BBoxes during ingest and rasterize them into original-resolution, source-hashed Region assets;
2. maintain an explicit disposition for every detected vector figure candidate, blocking evidence validation when extraction, triage or Result Unit linkage is missing;
3. represent actual plotted signal features and their comparisons in the authoritative general scientific-analysis record, including position, width, intensity, area, change type, normalization and uncertainty/readout basis;
4. record the model, native image attachment references, source asset SHA-256 values and request/response artifacts, then revalidate those receipts and hashes.

These are engineering safeguards, not an instrument-specific scientific ruleset. The model must discover which plotted features and comparisons matter from the supplied evidence; production instructions must not contain any test project's peak positions, sample labels or expected scientific relationships.

**Acceptance state:** implementation branch created; code review and GitHub Actions plus Agent local acceptance remain pending. A passing structural test or invocation receipt does not certify the scientific correctness of peak/band assignments or interpretations. The user must still inspect the resulting real-data analysis.

## 1. 产品目标与问题定义

Paper_plan 的目标不是把实验图集变成一份更长的目录，也不是只为每一种仪器配置专用清单。目标是：用户给出普通科研材料和研究目标后，Skill 能够自主理解当前项目的证据结构，识别有科学意义的数据关系，分析差异、趋势、收敛、矛盾与异常，将现有证据转化为可追溯的科学判断，再据此组织文献定位、论文主线和研究执行计划。

最近一次不提示分析目标的真实运行表明，V5.1 能完成证据整理、文献定位、论文故事线和实验任务设计，但对已有数据的解释仍明显停留在单项结果说明。例如，报告虽然列出了多种表征，却没有展示它们之间的实质比较，也没有从不同样品或不同处理条件的结果中主动寻找此前遗漏的关系。

这说明缺口不只是一个特定图谱没有分析，而是缺少一个通用、强制、可追溯的“跨结果科学分析”阶段。此前加入的专项比较工具只能作为原型和历史兼容功能，不能作为全局科学发现能力的替代品。

**核心产品原则：用户提出科研任务即可；发现哪些数据应该比较、如何比较、哪些关系值得解释，应由 Skill 自己完成。用户不应每次都重新提供分析清单。**

## 2. 当前能力盘点

### 2.1 已实现并应保留的能力

| 能力 | 当前状态 | 说明 |
|---|---|---|
| 项目入口、原始资料与工作区隔离 | 已实现 | 原始输入指纹、独立工作区、历史结果保护 |
| PDF 页级摄取与文本/图像盘点 | 已实现 | PyMuPDF 文本、图像块、矢量绘图清单 |
| 栅格 Region 提取及来源锚定 | 已实现 | 页面、坐标、像素哈希和提取版本 |
| 矢量图候选识别 | 部分实现 | 启发式候选发现；不能自动完成所有矢量图语义识别 |
| Panel 分割 | 部分实现 | 已支持显式 Panel 坐标；自动语义分割仍有限 |
| 原分辨率单图视觉检查 | 已实现 | Caption-blind 观察、可读性、轴/图例、来源记录 |
| 样品实体与映射状态 | 已实现 | CONFIRMED、PROBABLE、AMBIGUOUS、UNMAPPED 等 |
| Result Unit 与 Finding 证据结构 | 已实现 | 结果、来源、观察、解释、假设与证据角色 |
| 定量测量定义和计算审计 | 已实现 | 测量定义、拟合复现、精度与不确定性控制 |
| 样品/条件可比性结构 | 已实现 | 已具备跨样品/条件比较的部分结构控制 |
| 文献前沿与最近邻比较流程 | 已实现为 Agent 工作流 | 实际覆盖取决于搜索工具、全文权限与执行质量 |
| 研究主线、论文故事线、Figure/SI 与任务包 | 已实现为 V5 产品流程 | 结构化状态加研究者可读叙述 |
| Markdown/PDF 导出及产品 QA | 已实现 | 完整交付和独立 QA 流程 |
| Python 3.10–3.12 CI | 已实现 | 编译与完整 unittest 测试矩阵 |

### 2.2 已有但不能视为全局能力的原型

| 能力 | 当前状态 | 缺口 |
|---|---|---|
| 单一测量技术的联合比较原型 | 已实现专项脚本与 Evidence Bundle 记录 | 专项化；分组依赖技术/测量组元数据；不能解决跨模态、跨指标、趋势、矛盾和项目级关系发现 |
| 单项结果的上下文编译 | 已实现 | 主要压缩 Result Units 与 Findings，尚不能形成完整的跨结果分析图景 |
| 视觉与文本对照 | 已实现流程 | 能检查图文一致性，不等于自动发现多结果之间的科学关系 |
| 测量可比性检查 | 已实现结构控制 | 只在比较被提出后发挥作用；没有主动发现足够广泛的候选比较 |
| 研究者叙述整合 | 已实现 | 最终叙述质量受前面的科学分析深度制约 |

### 2.3 本轮必须解决的未完成事项

1. 缺少对整个 Result Unit 集合的自动关系索引和覆盖闭合。
2. 缺少跨样品、跨条件、跨时间、跨指标及跨测量方法的通用关系发现机制。
3. 缺少“同一 Result Unit 内多条曲线/多个系列”与“多个 Result Unit 之间”同时分析的统一任务表示。
4. 缺少强制的可比性评估与比较结论记录，导致单项图像描述容易被误认为充分分析。
5. 缺少对相互印证、矛盾、异常、负结果、非单调关系和候选机制的统一证据结构。
6. 缺少对每一个 Result Unit 的明确分析处置：已分析、不适用或不可评估。
7. 缺少在最终科学综合之前将分析记录纳入上下文的强制流程。
8. 缺少通用科学分析能力门控与成本控制。
9. 缺少能够证明模型确实完成多模态科学分析、而不仅是脚本和结构测试通过的黑盒验收。
10. 缺少跨研究领域的独立验收，不能以一个项目的成功作为全局泛化证明。

## 3. 目标架构

### 3.1 工作流位置

通用科学分析必须位于“结果抽取与单项观察之后、文献主线与论文叙述综合之前”。

目标流程：

    原始科研资料
      -> 来源与页面/区域清单
      -> 原分辨率图像和文本/表格提取
      -> Sample / Result Unit / Finding 建立
      -> 单项观察、数值定义与来源审计
      -> 通用关系索引与候选分析包
      -> 多模态联合分析与跨结果科学解释
      -> 分析覆盖与证据验证
      -> 文献前沿和最近邻比较
      -> 科学主线及贡献边界决策
      -> Results/Discussion、Figure/SI 与研究任务设计
      -> 研究者可读计划及 PDF

该阶段不可依赖用户点名某种技术、某个图号或某种预期差异。专项技术可以由模型根据当前材料自行识别，但生产规则不能把某一种技术写成通用前提。

### 3.2 两层实现

**确定性 Python 层**负责：
- 汇总全部 Result Units、Sample、Region、Panel、观察、测量定义、来源页码和图像路径；
- 建立候选关系图，说明链接依据但不宣称科学可比；
- 以可控大小生成分析任务包，并保留跨包链接；
- 验证每条观察、比较、解释是否引用本包中的正确来源；
- 强制每个 Result Unit 有分析覆盖状态；
- 保存可追溯分析记录，并将其编入后续上下文。

**模型科学推理层**负责：
- 原分辨率图像及相关结果的联合检查；
- 自主判断哪些关系有科学意义；
- 分析差异、趋势、关系、收敛、矛盾、异常和替代解释；
- 结合本领域知识解释已有证据，但不伪造数据或把假设写成事实；
- 识别由现有数据支持、但用户尚未明确提出的候选科学问题。

不能让 Python 规则假装自己理解科学含义，也不能让模型自由叙述而不保留来源和覆盖记录。

### 3.3 通用分析记录

所有项目统一写入 scientific_analyses，至少包括：
- 项目与源文件指纹；
- 每个分析包涉及的 Result Units；
- 逐项 observations 与原始证据引用；
- comparisons 与维度可比性状态；
- quantitative_differences 与 qualitative_differences；
- relationships（趋势、收敛、分歧、条件响应、相关候选、结构—性质等）；
- interpretations 与 alternative explanations；
- contradictions；
- candidate_scientific_implications；
- unresolved_questions 与 limitations；
- 对每个 Result Unit 的 coverage 状态。

此前 spectral_comparisons 保留用于历史项目兼容；新流程以通用 scientific_analyses 为主，不再把光谱比较作为独立必经专项。

## 4. 本轮功能范围

### In scope
- 通用候选关系发现：共享样品、测量组、测量签名、来源区域及共同条件字段；
- 将候选关系与 Result Units、原始图像和视觉观察组织为联合分析包；
- 单项内部多系列分析与跨 Result Unit 分析；
- 跨测量方法/多模态证据收敛与矛盾发现；
- 可比性和不确定性记录；
- 观察、比较、关系、解释、假设分层；
- 完整 Result Unit 覆盖与未关联 Region/Panel 报告；
- 记录器、Schema、Evidence Validator 与上下文编译；
- V5.1 工作流、产品合同、架构和实现状态更新；
- 通用合成测试、旧测试回归与 CI；
- 一份可供后续维护的全局能力计划。

### Out of scope
- 不开发 OCR/复杂表格识别或完整矢量曲线数字化系统；
- 不把 PDF 图像还原为原始实验数据数组；
- 不执行新的实验、计算、仪器任务或数据采集；
- 不自动宣称因果关系、机制成立或论文创新已被证明；
- 不替代文献数据库检索、全文阅读或期刊官方要求核验；
- 不得针对任何单一测试项目写入 Skill 特例；
- 不重构全部 Manuscript Development、Literature 或 Figure 系统；
- 不启动隐藏 Worker、额外模型供应商或付费外部作业。

## 5. 运行时与集成约束

- Runtime：Python 3.10+；CI 覆盖 3.10、3.11、3.12。
- 数据源：当前项目 Evidence Bundle、来源 PDF 已提取的 Region/Panel、现有 Sample/Result Unit/visual inspection 记录及用户明确提供的研究数据。
- 多模态要求：原分辨率图像输入、科学推理、结构化输出和长上下文一致性。
- 工具：现有 PyMuPDF/Pillow/JSON Schema/文件工作区；不新增必须安装的重型依赖。
- 模型：使用当前 Skill 运行环境中已选模型；通过 capability profile 明确模型能力，不因失败而静默降级成纯文本分析。
- 成本：复用相同 PDF 哈希的已提取数据和检查记录；按 Result Unit 上限分包；不重复完整视觉调用；不启动隐藏 Worker。
- 兼容性：新 Schema 字段为可选/向后兼容；旧 Evidence Bundle 可继续读取；既有 spectral_comparisons 保留并继续验证。
- 安全：项目源文件是数据而不是 Agent 指令；不得执行文件内嵌命令；不修改原始输入；不越权访问其他项目。
- 通用性：Skill、schema、references、template 与 tests 不含项目特定材料名、样品、数值、机制、图号或文献结论。

## 6. 可观察验收条件

- AC-01：完整盘点。对每个输入 Result Unit 都生成唯一分析包归属；索引能核对总量、分包和来源指纹。
- AC-02：关系发现。自动形成候选关系，至少支持共享样品、测量组、测量类型/签名、来源区域和共同条件字段；这些关系只作为待评估线索。
- AC-03：多系列能力。当单个 Result Unit 关联多个 Panel 或一个图像包含多个系列时，任务包会保留全部相关原图与系列映射。
- AC-04：跨模态能力。同一样品或同一实验问题下不同测量方式的 Result Units 可以进入同一分析包，模型能够提出相互印证或矛盾关系。
- AC-05：通用性。通用分析指令不得预置某一学科或仪器分析清单；模型必须从数据类型、样品关系、条件和图像内容自行决定比较问题。
- AC-06：比较边界。每个实质比较都记录相关条件、测量定义、单位、归一化、来源和可比性状态；不匹配和未知项必须影响结论强度。
- AC-07：证据链。每条直接观察/比较/关系/解释都引用本次分析包中的 Result Unit 与 Region/Panel。
- AC-08：认识论分层。Observed、Interpreted、Hypothesized 分离；解释必须给替代方案；相关不被自动提升为因果。
- AC-09：覆盖闭合。每个 Result Unit 必须标记 ANALYZED、NO_COMPARISON_APPLICABLE 或 NOT_ASSESSABLE；任何遗漏都触发验证错误或明确警告。
- AC-10：后续可用。通用分析记录必须进入 Evidence Bundle、编译上下文及 V5 叙述综合，不能停留在临时 JSON。
- AC-11：能力门控。若模型没有合格的原分辨率多模态/科学推理/结构化输出/长上下文能力，分析必须阻塞或降级为明确的 NOT_ASSESSABLE，不得伪装已完成。
- AC-12：历史兼容。旧工作区与旧 spectral_comparisons 能正常读取；现有测试不回归。
- AC-13：项目隔离。生产代码、schema、references 和 Skill 中不得出现本轮具体研究项目的科学内容。
- AC-14：成本与执行。使用现有模型和工具，不启动隐藏 Worker、不重复已缓存抽取、不执行用户未授权的付费作业。
- AC-15：黑盒成功标准。用户不给特定分析提示时，Skill 仍能主动发现有意义的跨结果关系；仅代码测试或生成任务包不构成科学能力通过。

## 7. 开发里程碑与状态

| 里程碑 | 内容 | 基线状态 | 本轮状态/交付 |
|---|---|---|---|
| M0 | V5.1 证据、工作流和产品契约盘点 | 已完成 | 作为本计划依据 |
| M1 | 定义通用关系与分析数据结构 | 已完成 | 通用 scientific_analyses 记录结构、coverage、比较与关系字段 |
| M2 | 自动生成候选关系图与联合分析包 | 已完成 | 按样品/测量组/测量签名/来源区域/共同条件/系列标识建候选关系并分包；链接仅为导航提示 |
| M3 | 结构化分析记录器与来源校验 | 已完成 | 记录器检查每项覆盖、来源 Region/Panel、比较引用、源 PDF 哈希、数值格式与解释依据 |
| M4 | Schema、Evidence Validator、上下文编译接入 | 已完成 | Evidence Bundle 兼容字段、Schema、Validator 与科学上下文输出均已接入；跨包候选关系随记录保留 |
| M5 | Workflow 01 与 V5 Stage 1 强制接入 | 已完成 | Workflow 01、V5 Stage 1 与 SKILL.md 已声明为必经阶段；模型自主选择比较对象 |
| M6 | 通用分析参考规范与产品合同更新 | 已完成 | 新增通用参考规范，更新产品合同、架构、README 和实现状态 |
| M7 | 合成测试、旧测试回归和 CI | 已有基础设施 | 已完成：新增 12 项通用测试；CI 在 Python 3.10/3.11/3.12 各 155 项测试通过 |
| M8 | 源码通用性审查与 release candidate | 已完成 | 新增通用脚本、参考规范、工作流、Skill 主说明与测试均通过项目内容泄漏检查；release candidate 已准备 |
| M9 | 用户本地同步与真实项目黑盒验收 | 未完成 | 等待用户执行 |
| M10 | 多学科独立项目泛化验收 | 未完成 | 后续版本范围 |

### 7.1 本轮完成后仍未完成的全局事项
1. 自动识别 PDF 内所有语义图表、表格与矢量绘图仍不完整，部分需要人工/Agent 定义 Region 或 Panel。
2. 原始数字曲线恢复、复杂表格结构重建、自动统计重算仍依赖额外数据工具和输入质量。
3. 科学分析记录器只能检查结构、引用和覆盖，不能证明模型提出的科学解释正确。
4. 模型视觉分辨率、长上下文和推理质量仍依赖运行时模型；能力档案为操作员声明，不是独立性能基准。
5. 文献前沿和最近邻检索仍受数据库覆盖与全文权限约束。
6. 尚无跨不同科学领域的真实黑盒回归矩阵。
7. 仍需用户检查最终 Markdown/PDF 是否真正把发现的跨结果关系转化为高质量科学故事线。


### 7.2 当前开发实现已完成项

- 新增 \`scripts/prepare_scientific_analysis.py\`：生成通用关系索引、分析包、所有 Result Unit 覆盖映射及未关联 Region/Panel 清单。
- 新增 \`scripts/record_scientific_analysis.py\`：检查分析包身份、逐 Result Unit 覆盖、观察来源、比较来源、解释依据、替代解释，并将记录存入 Evidence Bundle。
- 新增 \`scientific_analyses\` Schema 字段，保留旧工作区可读取性及既有 \`spectral_comparisons\`。
- 更新 Evidence Validator 与 compact context compiler；未分析的 Result Units 会被明确列出，分析观察/比较/关系进入后续上下文。
- 将通用分析列为 Workflow 01 与 V5 Stage 1 的必经阶段；SKILL.md 明确要求用户无需手工指定比较清单。
- 允许在分辨率和坐标轴支持的情况下进行有边界的图像半定量比较；原始数值数据不是一律前置条件。
- 最新已完成的软件回归基线为开发分支提交 0f7f428dc2f9c96b9e41097f05d322250e6744dd，Python 3.10、3.11、3.12 各 155 项测试全部通过。后续文档变更仍需确认触发的 CI 运行通过。

### 7.3 当前未完成/待用户验收项

- **黑盒验收：** 必须由用户同步后在真实项目上使用普通科研任务入口验证模型是否自主发现科学关系；软件 CI 不能替代科学验收。
- **大规模项目评估：** 后续仍需评估超大 Result Unit 集合下的分包成本、关系候选截断和上下文预算。
- **真实科学黑盒验收：** 用户需同步独立分支，按普通用户方式发起科研任务，不给模型提示分析清单；评估是否真正自主发现新关系并在主报告中解释。
- **多学科泛化：** 至少在不同科学领域的真实项目上重复黑盒验收。合成 fixture 和一个案例均不足以证明普适性。
- **视觉提取增强：** 自动语义图表识别、复杂表格重建和矢量图表解析仍是独立后续开发项。

## 8. 测试策略

### 8.1 确定性软件测试
使用完全合成、通用的 Result Unit/Region/Panel fixtures，至少覆盖单一结果与孤立结果；多样品同测量组；同一对象跨测量方式；多条件和时间序列；单个图中多条系列；不可比的单位/归一化/采集条件；共享样品映射模糊；多证据一致与相互矛盾；一个 pack 拆分为多个批次；未关联 Region/Panel；记录缺少覆盖、引用错误、跨包引用和不完整比较。

### 8.2 回归
执行：
- python -m compileall -q scripts tests
- python -m unittest discover -s tests -v
- Python 3.10、3.11、3.12 GitHub Actions。
- 旧 Evidence Bundle Schema、Evidence Validator、visual inspection、manuscript/planning validators 的既有测试。

### 8.3 黑盒科学验收
软件测试不能替代真实科学能力测试。用户同步 release candidate 后，只需使用普通科研任务指令和原有测试资料，不能人为提示应该分析哪类图谱或哪种关系。检查 Skill 是否自行发现之前漏掉的结果关系，并给出来源可追溯、边界适当的科学解释。

本地黑盒验收未完成之前，状态只能标记为 CODE/CI VERIFIED — SCIENTIFIC BLACK-BOX ACCEPTANCE PENDING。软件 CI 全绿不能被描述为科学发现功能已验收。

## 9. 决策与不得再次询问事项
- 保持 Paper_plan V5.1 researcher-facing-product 为基线，不重开论文计划产品架构。
- 不针对任何单一项目、特定测量技术或测试数据写专项生产规则。
- 不把任何测试项目材料、样品标签、科学值、机制或文献结论写入 Skill。
- 优先扩展通用科学结果关系分析；专用光谱原型保留兼容，不再作为主流程。
- 用户希望 Skill 自主发现值得分析的关系，不要求每次手工提示分析对象。
- 不允许 Agent 绕过 Skill 自行补做科学分析来制造通过结果。
- 开发产物仅放在独立 feature 分支；不合并、不发布，用户批准前不进行发布。
- 完成后通知用户同步并进行黑盒测试；不得声称已完成用户本地真实 PDF 验收。

## 10. Release candidate 交付要求
RC 至少包含通用分析包生成器和结果记录器；Evidence Bundle 可选兼容字段及 Schema；coverage/reference Validator；通用分析上下文编译；能力门控；workflow/reference/product contract/architecture/status 更新；合成测试与全量 CI；本计划的更新状态和本分支变更摘要。

用户最终应能在普通科研任务入口中直接运行 Skill，而不需要再写一份人工分析清单。只有当黑盒验收证明该能力确实由 Skill 自主触发并完成，才可批准合并/发布。
