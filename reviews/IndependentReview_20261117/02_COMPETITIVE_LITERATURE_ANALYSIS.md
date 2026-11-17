# 02 — 独立竞争性文献分析

**检索日期：** 2026-11-17
**系统/来源：** 公开 websearch 索引（出版商页、PMC、CNKI 系期刊英文页、MDPI）、Crossref REST API（DOI 真实性核验）、PMC 全文页 webfetch。
**检索式（目标系统 = 副产石膏酸处理/相变/反应性）：**
1. `comparison acid leaching reactivity flue gas desulfurization gypsum versus phosphogypsum sulfuric acid`
2. `phosphogypsum sulfuric acid conversion quantitative XRD mass balance phase quantified dose response`
3. `by-product gypsum acid treatment specific surface area reactivity impurities comparison study`
4. 补充：`synthetic gypsum purification acid leaching review`、`phosphogypsum low concentration sulfuric acid dissolution phase behavior`

**边界声明：** 以上为有界检索（系统、日期、检索词如上）。**"未检索到"不等于"不存在"**。上一轮 17 篇文献全部为 ABSTRACT_VERIFIED、0 全文；本轮**新增/独立核实 12 篇**，不把上一轮的摘要级条目重复计数，也不把摘要说成全文。

---

## 1. 本轮文献核实清单（按 access tier 分组）

### FULLTEXT_VERIFIED（实际读取了正文，含方法/结果/具体数值）

**LIT-N01 — Zhu G., Yang Y., He L., Li H., Meng Z., Zheng G., Li F., Su X., Xi B., Li Z. (2023).** *Novel Synergistic Process of Impurities Extraction and Phosphogypsum Crystallization Control in Wet-Process Phosphoric Acid.* **ACS Omega 8(31):28122–28132.** DOI `10.1021/acsomega.3c01168`; PMCID `PMC10413463`.
- 获取路径：PMC 全文页 webfetch（方法、结果、图注、结论、参考文献）。
- 精确摘录：
  - "XRD Rietveld quantitative analysis... The content of anhydrite and dihydrate gypsum was **76.85 and 4.52%**, respectively. Meanwhile, there also exists little amount of bassanite (**10.84%**) and quartz (**5.08%**)."
  - 加萃取剂后："anhydrite... content decreased to **55.52%** and the content of dehydrate increased to **29.01%**."
  - 条件："reaction time was **7 h**, reaction temperature **80 °C**, **200 r/min**, O/A 1:1, dilution 1:4."
  - TG-DSC："heated from **90 to 200 °C**, the weight loss... was **2.8%**"；"crystallization (2.2%) and free water (0.6%)".
- 意义：**Rietveld 定量相 + TG-DSC + XPS 杂质形态 + SEM 形貌 + 粒度**已经在磷石膏体系上被组合使用，且明确区分二水/半水/无水/石英并给出分数。上一轮"定量 XRD 尚未建立"的 gap 表述过宽。

**LIT-N02 — [作者名见原文] (2012).** *Studies on the transformation of calcium sulphate dihydrate to hemihydrate in the wet process phosphoric acid production.* **Polish Journal of Chemical Technology 14(2):80–87.** DOI `10.2478/v10026-012-0075-4`.
- 获取路径：出版方 PDF 文本经 search index 暴露（方法、公式、结果表、结论均可见）；非逐页 PDF 阅读，但相关正文已实际检视。
- 精确摘录：
  - "The relative abundance of CaSO4·2H2O, α-CaSO4·0.5H2O and CaSO4 phases were calculated from the (101) reflection of CaSO4·2H2O, the (121) reflection of α-CaSO4·0.5H2O and the (020) reflection of CaSO4."
  - "the **degree of conversion** of CaSO4·2H2O to α-CaSO4·0.5H2O and CaSO4... **α is the conversion degree**... k1 and k2 [are] the coefficients."
  - 条件/结果：85–95 °C、液固比 3:1、P₂O₅ 22–36 wt%、SO₄²⁻ 2–9 wt%、转化度 18–98%。
- 意义：**"用 XRD 峰强度建立相分数与转化度方程"并非新方法**；与原始报告 p13 的线性拟合（y=-0.0237+0.900x, R²=0.9505 等）属同类思路且早 14 年、更系统。

### ABSTRACT_VERIFIED（实际读取摘要/索引暴露的正文片段，未逐页读全文）

**LIT-N03 — Ni Lina, Li Huping, Luo Kangbi, Xie Weiping, Su Yi (2014).** *Research of the dissolution and phase behavior change on the phosphogypsum in the low concentration of sulfuric acid（磷石膏在低浓度硫酸中的溶解及相态变化）.* **Chemical Industry and Engineering Progress（化工进展）33(3):769.** 期刊页 URL `https://hgjz.cip.com.cn/EN/Y2014/V33/I03/769`（页面未给出 DOI，**不虚构**）。
- 精确摘录（英文摘要原文）："investigated the solubility size, crystal morphology, phase composition and the changes of **crystal water contents** of the phosphogypsum in the sulfuric acid solution at **0—80 ℃ and 0—30% of sulfuric acid concentration**." "When the sulfuric acid concentration was **lower than 10%**, the dihydrate calcium sulfate in the phosphogypsum **dissolved with no new phase formation**, and the morphology... did not change much. When... **greater than 10%**, the dihydrate calcium sulfate dissolved and **recrystallized into the anhydrous calcium sulfate**."
- 意义（**本轮最关键竞争文献**）：这是最接近原始报告的既有工作——低浓度硫酸、温度扫描、溶解度 + 相态 + 形貌 + 结晶水。**它直接推翻"低剂量下 100% 相变"的解读**，并大幅压缩 ROUTE001/002 的新意空间。

**LIT-N04 — (2017).** *Deep removal of impurities from phosphogypsum.* 化工进展. DOI `10.16085/j.issn.1000-6613.2017.04.012`.
- 摘录（摘要）：比较水洗、酸洗、酸洗+溶剂萃取；"the main mineral phase of CaSO4·2H2O in PG underwent **dissolution and recrystallization to form CaSO4** both in water washing and acid pickling process, while the transformation speed was **much faster in the latter**." 表征：XRF/XRD/SEM/whiteness。
- 意义：酸洗导致溶解–重结晶已在 2017 年被系统比较；"形貌变化非反应独有指纹"得到支持。

**LIT-N05 — (2024).** *Leaching Characteristics and Mechanisms of Fluorine and Phosphorus from Phosphogypsum.* PMCID `PMC11722157`.
- 摘录（摘要 + 索引正文）："static pH leaching experiments... **Visual MINTEQ simulation** combined with XRD, XPS, and FT-IR"；"The dynamic **'dissolution–crystallization' reaction of CaSO4·H2O** significantly impacts the leaching of fluorine."
- 意义：热力学模拟 + 多表征联用解析酸/ pH 下相与杂质释放已成熟。

**LIT-N06 — (2025).** *Eco-Friendly Utilization of Phosphogypsum via Mechanical Activation...* Sustainability 17:2817 (MDPI). DOI `10.3390/su17072817`（由卷期页推得，DOI 字符串未逐字核验 → 引用时以 URL 为准）。
- 摘录："conversion of gypsum (CaSO4·2H2O) to anhydrite (CaSO4), an increase in surface area **from 5.8 m²/g to 17.8 m²/g**"；XRD/BET/zeta/XPS/SEM 联用。
- 意义：**处理导致 BET 升高是已知且可重复的效应**，削弱 ROUTE003 的新意。

**LIT-N07 — Wu C., Xu W., Song Z., et al. (2026).** *Purification of Synthetic Gypsum: Techniques and Mechanisms.* **Molecules 31(3):484.** DOI `10.3390/molecules31030484`（Crossref 元数据已核实标题/作者/卷期页）。
- 摘录（索引暴露正文 "Acid Leaching" 段）：把 **PG、FGDG、citrogypsum(CG)、titanium gypsum、salt gypsum** 归为 synthetic/chemical gypsum；酸浸用于除 P/F/稀土/放射性核素/重金属。
- 意义：**CG 在文献中常指柠檬酸副产石膏**，与报告"CG=商业/天然石膏"的解释可能冲突（Gate A 必须确认）；同时说明"多来源副产石膏 + 酸处理"作为**综述主题**已存在。

**LIT-N08 — Canovas et al. (2019).** *Leaching of rare earth elements (REEs) and impurities from phosphogypsum.* J. Cleaner Production. DOI `10.1016/j.jclepro.2019.02.104`.
- 摘录（摘要/正文）：0.5 M H₂SO₄ 萃取 REE 46–58%，**溶解石膏 <6%**；高 SO₄²⁻ 因同离子效应限制石膏溶解。
- 意义：邻域（REE 回收）但提供"同离子效应抑制溶解"的机制对照；本研究若用 H₂SO₄，须面对同离子效应。

**LIT-N09 — (2024).** *The Impurity Removal and Comprehensive Utilization of Phosphogypsum: A Review.* Materials 17:2067. DOI `10.3390/ma17092067`（以出版页为准）。
- 摘录（索引正文）：硫酸/草酸/柠檬酸浸出、中和、重结晶；"impurity migration mechanisms at molecular level remain [an open need]"。
- 意义：综述层面的 gap 表述可引用，但不可据此声称本研究填补该 gap。

### METADATA_ONLY（仅核实题录/DOI；不得用于支持技术性论断）

**LIT-N10 — Zhang M., Mei Y., Li Y., Xia J. (2024).** *Research on the technology and mechanism of direct acidification of phosphogypsum and deeply solidify impurities with lime.* J. Environmental Chemical Engineering 12(6):114937. DOI `10.1016/j.jece.2024.114937`。
- 本轮通过 Crossref 核实：标题、4 位作者、卷 12、期 6、文章号 114937、出版年 2024、Elsevier——**证明上一轮 LIT005 的 DOI 真实、非虚构**。但上一轮所给的机制性描述（"CaSO4·2H2O dissolves→II-CaSO4; P/F converted and solidified"）本轮**未独立核实摘要**，保留为上一轮的 ABSTRACT_VERIFIED 陈述，本表不计为全文。

**LIT-N11 — (2025).** *Acidity-gradient controlled conversion of byproduct gypsum into high-purity whiskers: A synergistic process for wastewater treatment and resource recovery.* J. Environmental Chemical Engineering. DOI `10.1016/j.jece.2025.118674`. 仅题录。

**LIT-N12 — Yang X. et al. (2026).** *Insights into leaching-response behavior of phosphorus, fluorine, and metal impurities during sulfuric acid leaching of phosphogypsum.* Minerals Engineering, article 110966. 仅题录（作者/期刊/年来自检索结果）。

**核实数量小结：FULLTEXT_VERIFIED = 2；ABSTRACT_VERIFIED = 7；METADATA_ONLY = 3；合计 12。** 上一轮 17 篇摘要级记录仍有效但不重复计数。

---

## 2. 对四个必答问题的明确回答

**Q1：是否已有研究比较不同来源的脱硫石膏、磷石膏或其他副产石膏的酸反应行为？**
- 原始研究层面，本轮检索到的多为**单一副产物（以 PG 为主）**的酸浸/相变/除杂研究（LIT-N01/02/03/04/05/08）。
- 综述层面，LIT-N07 明确把 PG/FGDG/CG(柠檬酸石膏)/钛石膏/盐石膏并列讨论其酸净化技术。
- **未发现**（在本轮限定的系统/词/日期内）以完全相同条件对 FGDG/PG/CG 做**相定量终点**剂量响应比较的原始论文；但这只是"bounded 未命中"，不是"首次"证明。

**Q2：是否已有研究系统建立酸用量、转化率、物相变化和杂质之间的关系？**
- **部分已有。** LIT-N01 把酸解条件→相分数(Rietveld)→形貌→杂质形态(XPS)→热分析串成完整链条；LIT-N02 用 XRD 强度方程把酸/磷酸盐浓度→转化度→相分数建模；LIT-N05 用 Visual MINTEQ + XRD/XPS/FTIR 关联 pH→杂质释放与相变化。
- 因此上一轮 GAP001 的表述（"searched abstracts do not provide... like-for-like phase-quantified... comparison"）在**跨来源、相定量、同条件**这一限定下仍可维持，但"系统性建立关系"本身已不新颖——创新性必须落到"跨来源 + 严格同条件 + 指标有效性"上。

**Q3：是否已有研究使用定量 XRD、物料衡算或动力学分析解决类似问题？**
- 定量 XRD：**有**（LIT-N01 Rietveld；LIT-N02 XRD 强度转化度方程；LIT-N09 提及 Rietveld）。
- 动力学：**有**（LIT-N02 非线性回归模型；上一轮 LIT017 Çetin 2001 饱和动力学；LIT-N05 MINTEQ）。
- 物料衡算：LIT-N10 题名含"direct acidification ... with lime"，可能含衡算，但**未核实全文，不作断言**。上一轮方案把"物料衡算"列为新增贡献，需 T008 核实后才能写。

**Q4：本研究相对于最接近的已有工作，究竟增加了什么知识？**
- **按原 ROUTE001：增加有限，很可能被审稿人视为重复。** Ni 2014（低浓度酸→相/形貌/结晶水）与 Zhu 2023（Rietveld + TG + XPS + SEM）已经覆盖"酸条件→相→形貌→杂质"的主干。
- **按重构后的指标有效性方向：可能的知识增量**为——
  1. 明确区分"耗酸量代理指标"与"相定量转化率"，并在低剂量区给出两者的**定量分歧**；
  2. 证明或证否"报告类文献中常见的 100% 转化率"是否只是酸被耗尽的假象；
  3. 给出跨来源石膏在**严格同条件、相定量终点**下可比性的边界条件。
  - 以上增量必须经 T008 全文核实确认无人发表后才能进入 Introduction；在此之前只能写成 hypothesized gap。

---

## 3. 关键创新性风险（必须正面回答的审稿人问题）

> **"What is actually being 'converted', into what phase, and by what independent measurement do you know? And how is this not already shown by Ni et al. (2014) for phosphogypsum under 0–30% H₂SO₄, or by Zhu et al. (2023) with Rietveld-quantified phase fractions?"**

拆解为三个具体质疑点：
1. **指标效度风险（最高）**：原始报告的 "conversion rate" 出自标为"耗酸量"的图、由 NaOH 反滴定得到；若论文不预先用相定量方法定义终点，整篇论文的数据基础会被质疑。
2. **剂量区风险**：0.010–0.030 mL/g 属极低剂量；Ni 2014 指出 <10% 酸只溶解二水石膏而无新相。所谓"100% 转化"若被解释为相变，与既有文献直接冲突。
3. **概念拥挤风险**：酸浸、相变、杂质、形貌、BET、定量 XRD 在 PG 上均已有人系统做过；若缺少"跨来源同条件 + 指标效度"这一新轴，论文难以通过创新性审查。

**处理原则：** 不得用"first/unprecedented"措辞；不得把摘要级证据写成全文已核实；不得虚构 DOI（LIT-N03 无 DOI 即如实写"页面未给出 DOI"）。

---

## 4. 必须先完成的文献动作（Gate A 前置）

对以下 5 篇做全文核实（T008 的具体化）：Ni 2014（LIT-N03，中文全文，CNKI/期刊）、Zhu 2023（LIT-N01，已核实）、2012 Polish J Chem Tech（LIT-N02，已核实）、Zhang 2024 JECE（LIT-N10，Elsevier 开放获取或机构权限）、Wu 2026 Molecules 综述（LIT-N07，MDPI 开放获取）。核实目标：建立"条件–终点定义–相定量–杂质–形貌"对照矩阵，确认 LIT-N03 是否已实质覆盖本研究的核心问题。若已覆盖 → 停止原路线，仅保留指标效度角度或另选方向。
