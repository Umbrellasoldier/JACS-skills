# JACS 图表学习记录 v0.3

本轮针对淡亮配色、图表选择、点线与图例、专业标签、字号、坐标尺度和组图方式进行扩展。
**累计 50 篇论文、199 幅实际查看过的图；本轮新增 36 篇、150 幅。** 旧版的 14 篇／49 幅
保留为已有证据，不算本轮新阅读，也不重新充当留出集。多面板图计为一幅，不把裁剪或下载数当阅读数。
原论文图像与 PDF 仅保存在本地，公开的是来源、哈希、原创观察和合成示例。

## 取样与证据边界

检索六组主题的 Europe PMC 开放获取 JACS 记录，每组取前 60 条候选，再按题目和元数据选样；
时间窗为 2022-01-01 至 2026-09-17。样本偏向近期可获取研究，与期刊随机抽样不同。
本轮 36 篇均经 JATS 验证为 Article／PMC publisher version；旧版 Article、Communication、Perspective
沿用各自身份，不把不同文章类型混为统一风格。

30 篇开发论文的 127 幅图用于提炼 12 条有反例与适用边界的规则；6 篇留出论文的 23 幅图在规则冻结后查看。
先冻结选样，再冻结开发观察与规则；留出检查仅判断可迁移性和反例，不报告虚构的“通过率”。
检索、冻结与哈希见仓库 evaluation/figure-v3；逐图位置见
[开发观察](figure-observations-v3.jsonl)、[条件规则](figure-rules-v3.jsonl) 和 [完整题录](figure-corpus-v3.jsonl)。

| 新增主题层 | 论文数 |
|---|---:|
| computation | 10 |
| catalysis | 5 |
| spectroscopy | 7 |
| materials | 7 |
| bio | 7 |

开发与留出作者的规范化姓名字符串交集：Huse Nils。这不证明课题组独立：拼写变体、合作网络和单位关系尚未人工核验。

## 学到什么，怎样用于绘图

- **图型围绕问题选择。** 分布可用箱线／小提琴／直方／累计分布；预测一致性配残差；
  比较多个方法时显示原始观测或误差分布，不能只凭柱高判断模型。曲线用于连续自变量，矩阵用于两维类别。
  更多类型包括等高线、二维光谱、相图、电化学循环、吸附等温线、显微图、反应网络和结构示意，见
  [图型目录](../../jacs-figure/references/chart-catalog.md)。条目以图形家族组织，不是互斥的期刊流行度排名。
- **淡色用于面积，清晰颜色用于信息边界。** N03、N12、N13、N17 的浅蓝／青绿／淡紫／杏色提供了参考。
  N02、N25、N27 则说明高饱和色和厚重框线也真实存在。新版浅色方案是用户偏好与样本观察的结合，
  不是 JACS 官方配色，也没有“看起来舒服”的受试者实验结论。
- **点、线、带各有含义。** 观测点、模型曲线、参考虚线和不确定性带分开；空心／实心、形状和线型提供冗余。
  稀疏数据不凭空平滑，箱线图交代四分位与须的定义，小样本不制造可靠密度的印象。
- **图例围绕实体和条件组织。** 方法名称、浓度、温度等准确表达且跨图一致；可共享时使用共同图例。
  光谱交叠较多时图例通常比强行贴线标签清楚，孤立曲线可直接标注。统计定义放图注，不塞进每个图例条目。
- **坐标标题 = 量 + 必要单位。** 标明归一化、误差方向和能量参考；m/z、ppm、吸光度等按真实物理含义书写。
  原论文也可能有标签不一致，学习的是有理由的表达，不逐字照搬。N10 的一处角度／长度标注值得回看原文核对。
- **scale 包括数据范围和出版尺寸。** 同量比较用可比坐标；parity 需等比例和 y=x；正数跨数量级可用对数，
  残差保留零线；NMR／红外允许有约定的逆向轴。图中实际字号取决于最终缩放，不能只看脚本中的 fontsize。
- **组图有两种常用逻辑。** 同类比较使用对齐小多图；结构／机制／定量证据可使用不等宽叙事面板。
  共享轴标题和图例可以省空间，但前提是含义相同。显微图比例尺与横纵轴尺度不是一回事。

留出例子进一步限定规则：N08 相同类别下能量量纲和范围不同；N21 重叠光谱需要紧凑图例；
N27 的粗线与粗斜体字是轻量样式的反例；N33、N36 提醒图像比例尺、轮廓和光谱细节不能靠配色检查。

## 字体、字号与 PDF 实测

查看了下面六篇出版 PDF 的相应页面。所选整幅图都以 Image XObject 嵌入；可以通过 placement matrix
测得整幅图物理尺寸，却不能从 PDF 字体列表恢复图内已经栅格化的文字。正文／图注的字体不作为图内字体证据。
下表不是坐标绘图区尺寸，也不声称像素图里的字体可精确识别。

| 论文／图 | PDF 页 | 图像像素 | 整幅图尺寸 / pt | 图内字体与字号 |
|---|---:|---|---|---|
| N01 fig1 | 2 | 2088 × 1305 | 501.11 × 313.17 | 栅格化，未知 |
| N03 fig6 | 5 | 1500 × 924 | 360.00 × 221.73 | 栅格化，未知 |
| N10 fig2 | 4 | 634 × 968 | 152.11 × 232.27 | 栅格化，未知 |
| N13 fig3 | 4 | 2075 × 1327 | 497.99 × 318.44 | 栅格化，未知 |
| N20 fig2 | 2 | 1668 × 1386 | 400.31 × 332.62 | 栅格化，未知 |
| N32 fig2 | 4 | 1751 × 2166 | 420.21 × 519.82 | 栅格化，未知 |

因此，新版建议正文图起始使用 7–9 pt、深灰文字、清晰层级，再按最终尺寸检查。
这属于可执行的项目设置，不是样本测出的平均字号；ACS 的最低规格另见 [官方要求记录](graphics-policy.md)。
完整 PDF URL、文件哈希和对象位置记录在仓库 evaluation/figure-v3/pdf-audit.json。

## Data 插件的设计模式

采用 Data 1.0.8 的 visualize-data、validate-data 与分析质量检查思想：先明确分析关系和总体，
再选择图型；披露变换和统计定义；缺失不等于零；检验坐标、图例和实际导出结果。
[适配表](../../jacs-figure/references/data-design-patterns.md) 说明采用方式。
仪表板布局与产品品牌要求不转成期刊要求，模板中的数据全部是明确标记的合成演示。

## 全部 50 篇题录

`prior` 表示 v0.2 已查看，`development`／`holdout` 表示本轮角色；“图数”仅计实际查看的唯一图号。

| ID | 年份 | 类型 | 本轮角色 | 已看图数 | 论文与来源 |
|---|---:|---|---|---:|---|
| A07 | 2022 | Article | prior | 4 | [Machine-Learning-Guided Discovery of Electrochemical Reactions](https://doi.org/10.1021/jacs.2c08997) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9756344/) |
| A08 | 2025 | Article | prior | 3 | [Transfer Learning-Enabled Ligand Prediction for Ni-Catalyzed Atroposelective Suzuki–Miyaura Cross-Coupling Based on Mechanistic Similarity: Leveraging Pd Knowledge for Ni Discovery](https://doi.org/10.1021/jacs.5c00838) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12063614/) |
| A10 | 2022 | Article | prior | 1 | [Machine Learning May Sometimes Simply Capture Literature Popularity Trends: A Case Study of Heterocyclic Suzuki–Miyaura Coupling](https://doi.org/10.1021/jacs.1c12005) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8949728/) |
| B06 | 2023 | Article | prior | 5 | [Computational Design of a Tetrapericyclic Cycloaddition and the Nature of Potential Energy Surfaces with Multiple Bifurcations](https://doi.org/10.1021/jacs.2c12871) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9951208/) |
| C02 | 2010 | Communication | prior | 3 | [Rapid Cu-Free Click Chemistry with Readily Synthesized Biarylazacyclooctynones](https://doi.org/10.1021/ja100014q) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2840677/) |
| C03 | 2012 | Article | prior | 4 | [Reactivity of Biarylazacyclooctynones in Copper-Free Click Chemistry](https://doi.org/10.1021/ja3000936) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC3368396/) |
| C10 | 2008 | Article | prior | 3 | [Second-Generation Difluorinated Cyclooctynes for Copper-Free Click Chemistry](https://doi.org/10.1021/ja803086r) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC2646667/) |
| F01 | 2025 | Article | prior | 4 | [MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules.](https://doi.org/10.1021/jacs.4c07099) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12123624/) |
| F02 | 2025 | Article | prior | 4 | [Discovery of Ni&lt;sup&gt;(I)&lt;/sup&gt; Complexes for CO&lt;sub&gt;2&lt;/sub&gt; Insertion Enabled by a Machine Learning-Computational-Selection Sequence.](https://doi.org/10.1021/jacs.5c00441) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12395408/) |
| F03 | 2026 | Article | prior | 4 | [A 50,688-Reaction Data Set Reveals General Ligands and Mechanistic Diversity in C-N Couplings.](https://doi.org/10.1021/jacs.6c05959) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13339639/) |
| F04 | 2026 | Article | prior | 4 | [Dynamics of (Hetero)aryl Motifs: An Integrative Approach To Study the Conformational Landscape in Macrocycles.](https://doi.org/10.1021/jacs.6c09765) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13450417/) |
| F05 | 2026 | Communication | prior | 4 | [Triazenyl Furans as Diels-Alder Dienes.](https://doi.org/10.1021/jacs.6c06794) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13281527/) |
| F06 | 2025 | Article | prior | 3 | [Tungsten-Enabled Diels-Alder Cycloaddition and Cycloreversion of Arenes and Alkynes: Divergent Synthesis of Highly Functionalized Barrelenes and Arenes.](https://doi.org/10.1021/jacs.5c08320) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12371869/) |
| F07 | 2026 | Perspective | prior | 3 | [Yield Smarter, Not Harder: Good Practices for Machine Learning of Reaction Outcomes.](https://doi.org/10.1021/jacs.6c02213) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13449950/) |
| N01 | 2026 | Article | development | 5 | [Multiscale Neural Network Potential with Anisotropic Message Passing for the Fast and Accurate Simulation of Protein Dynamics and Enzymatic Reactions.](https://doi.org/10.1021/jacs.6c00217) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13383635/) |
| N02 | 2025 | Article | development | 4 | [Molecular Simulations with a Pretrained Neural Network and Universal Pairwise Force Fields.](https://doi.org/10.1021/jacs.5c09558) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12447504/) |
| N03 | 2026 | Article | development | 5 | [GraPhAI: Neural Networks for Solving Centrosymmetric Crystal Structures.](https://doi.org/10.1021/jacs.6c05607) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13383728/) |
| N04 | 2026 | Article | development | 5 | [Computing Solvation Free Energies of Small Molecules with Experimental Accuracy.](https://doi.org/10.1021/jacs.5c10940) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12903862/) |
| N05 | 2026 | Article | development | 4 | [Diffusion Model-Guided Inverse Design of Bimetallic Catalysts for Ammonia Decomposition.](https://doi.org/10.1021/jacs.5c14652) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12814173/) |
| N06 | 2025 | Article | development | 4 | [Rapid Access to Small Molecule Conformational Ensembles in Organic Solvents Enabled by Graph Neural Network-Based Implicit Solvent Model.](https://doi.org/10.1021/jacs.4c17622) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12022995/) |
| N07 | 2026 | Article | development | 7 | [Yield Prediction of Organic Reactions in Biased Data Sets via Positive-Unlabeled Learning.](https://doi.org/10.1021/jacs.6c00127) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13088182/) |
| N08 | 2026 | Article | holdout | 4 | [Predicting the Thermodynamic Limits of Metal-Organic Framework Metastability.](https://doi.org/10.1021/jacs.5c20253) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13195659/) |
| N09 | 2026 | Article | development | 4 | [Graph-Based Machine Learning Identifies Oxygenated Block Polymer Replacements for Conventional Plastics and Elastics.](https://doi.org/10.1021/jacs.5c21416) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13003491/) |
| N10 | 2026 | Article | development | 4 | [Integrating NMR Restraints into Coarse-Grained Simulations: Toward Accurate Conformational Ensembles of Complex Protein Systems.](https://doi.org/10.1021/jacs.5c22987) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13047695/) |
| N11 | 2026 | Article | development | 4 | [Role of 2-Hydroxyimines in Chiral Phosphoric Acid-Catalyzed Mannich-Type Reactions: Enhancing Reactivity and Selectivity via Dimerization.](https://doi.org/10.1021/jacs.5c22497) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13195647/) |
| N12 | 2026 | Article | development | 4 | [Assessment of Complementary Catalysts in an Uncharted Enantioselective Reaction of Sulfondiimines.](https://doi.org/10.1021/jacs.5c23100) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13185124/) |
| N13 | 2026 | Article | development | 4 | [Attractive Noncovalent Interactions versus Steric Confinement in Asymmetric Supramolecular Catalysis.](https://doi.org/10.1021/jacs.5c17872) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12814166/) |
| N14 | 2025 | Article | development | 4 | [Molecular Origins of Simultaneous Chemo-, Enantio-, and Substrate Selectivity in Non-Natural Photoenzymatic Radical Reactions.](https://doi.org/10.1021/jacs.5c12802) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12616699/) |
| N15 | 2026 | Article | holdout | 4 | [Heteroatom Doping Restructures Interfacial H2O to Resolve Mechanistic Contradictions in CO2 Electroreduction.](https://doi.org/10.1021/jacs.6c08293) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13450404/) |
| N16 | 2026 | Article | development | 4 | [The Curious Case of Dual Emission in 9,10-Bis(phenylethynyl)anthracene.](https://doi.org/10.1021/jacs.6c03064) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13088236/) |
| N17 | 2026 | Article | development | 4 | [Pursuing Heteroleptic Ligand Design Principles for Photoactive Fe Complexes with Ultrafast X-ray Emission and Variable-Temperature Optical Spectroscopies.](https://doi.org/10.1021/jacs.6c09850) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13474941/) |
| N18 | 2026 | Article | development | 4 | [Two of a Kind: Composition and Photophysics of Two Silver Nanoclusters Stabilized by the Same DNA Sequence.](https://doi.org/10.1021/jacs.6c04812) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13340420/) |
| N19 | 2026 | Article | development | 4 | [Femtosecond Soft X-ray Absorption Spectroscopy Identifies Metal-Centered S<sub>1</sub> Excited State of Cyanocobalamin.](https://doi.org/10.1021/jacs.6c01860) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13185098/) |
| N20 | 2025 | Article | development | 4 | [Signatures of a Conical Intersection in Two-Dimensional Spectra of a Red-Absorbing Squaraine Dye.](https://doi.org/10.1021/jacs.5c10393) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12426925/) |
| N21 | 2026 | Article | holdout | 4 | [Time-Resolved Resonant Inelastic X-ray Scattering Reveals How Orbital Symmetry Alignment Enables C-H Activation.](https://doi.org/10.1021/jacs.6c05747) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13185092/) |
| N22 | 2026 | Article | development | 4 | [Femtosecond-to-Second Time-Resolved Spectroscopy Brings Unparalleled Insight Into the Life Cycle of the Versatile Manganese Photocatalyst [Mn<sub>2</sub>(CO)<sub>10</sub>].](https://doi.org/10.1021/jacs.5c16761) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13107439/) |
| N23 | 2026 | Article | development | 4 | [Stable Li Plating/Stripping in LiPF6-Cyclic Ether-Based Electrolytes.](https://doi.org/10.1021/jacs.6c10611) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13474931/) |
| N24 | 2026 | Article | development | 4 | [Structure-Property Relationships to Guide the Selection of Fluorinated Ethers for Li-S Batteries.](https://doi.org/10.1021/jacs.6c04480) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13449949/) |
| N25 | 2026 | Article | development | 4 | [Phosphonium Poly(Ionic Liquid) Electrolytes for Fast Lithium-Ion Conduction.](https://doi.org/10.1021/jacs.6c02428) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13184986/) |
| N26 | 2025 | Article | development | 4 | [Rapid Redox Hopping Charge Transfer and Electrochromism in a Multivariate Metal-Organic Framework.](https://doi.org/10.1021/jacs.5c09275) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12447485/) |
| N27 | 2026 | Article | holdout | 4 | [A Critical Evaluation of the Limiting Current Density in Polymer Electrolytes: Interplay of Ion Transport, Mechanical Stability, and Conformal Li-Electrolyte Interfaces.](https://doi.org/10.1021/jacs.5c16267) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12879923/) |
| N28 | 2026 | Article | development | 4 | [Ligand-Mediated Defects Unlock Fast and Regenerable CO<sub>2</sub> Capture in NICS-24 Metal-Organic Framework.](https://doi.org/10.1021/jacs.6c04820) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13339166/) |
| N29 | 2025 | Article | development | 6 | [Metallicity, Atomic Disorder, and Li-Ion Storage in Fast-Charging Anodes.](https://doi.org/10.1021/jacs.5c06578) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12447494/) |
| N30 | 2026 | Article | development | 4 | [Time-Resolved Native Mass Spectrometry for Direct Measurement of Biomolecular Kinetics.](https://doi.org/10.1021/jacs.5c21842) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13195665/) |
| N31 | 2026 | Article | development | 3 | [Optimizing Stability in Dynamic Small-Molecule Binding Proteins.](https://doi.org/10.1021/jacs.5c19571) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12814167/) |
| N32 | 2026 | Article | development | 4 | [Kinetic Profiling in One-Step Digital Immunoassays Enables Multiplex Quantification across an Ultrabroad Dynamic Range.](https://doi.org/10.1021/jacs.5c17838) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12903848/) |
| N33 | 2026 | Article | holdout | 4 | [Size of Biomolecular Condensates Dictates Fate in Liquid-Solid Phase Transitions through Amorphous-Amyloid Competition.](https://doi.org/10.1021/jacs.6c02816) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13281517/) |
| N34 | 2026 | Article | development | 4 | [Quantifying Protein Homodimer Affinities and the Effect of Molecular Glues and Interface Residues Using Native Mass Spectrometry.](https://doi.org/10.1021/jacs.5c18602) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13088243/) |
| N35 | 2025 | Article | development | 4 | [Multivalency Controls the Growth and Dynamics of a Biomolecular Condensate.](https://doi.org/10.1021/jacs.5c02947) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12291466/) |
| N36 | 2025 | Article | holdout | 3 | [Multiplexed Analysis of Multicomponent Biomolecular Condensates without Any Tag.](https://doi.org/10.1021/jacs.5c14476) · [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12752461/) |
