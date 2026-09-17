# Scientific chart selection / 科研图表选型

Choose the scientific relationship first. The source IDs below resolve in the
[50-paper study](../../jacs-shared/references/figure-study-v3.md); detailed observations
are in [development records](../../jacs-shared/references/figure-observations-v3.jsonl).
“Observed” means visually inspected, not universally recommended. Variants overlap;
this table is a working vocabulary, not an exhaustive census of JACS.

| 图型 / family | 回答什么问题、数据要求 | 设计与统计边界 | 实看例子 | 模板 |
|---|---|---|---|---|
| 散点 / scatter | 两个连续量如何关联；每点有明确样本身份 | 点大小固定；重叠再用透明度、分面或密度；相关不等于一致 | N17 fig2; N34 fig2 | custom; `curve` for ordered x |
| 一致性散点 / parity | 同一量的预测与参考是否一致；成对样本 | 同单位、同范围、等比例；中性 y=x；给 n、MAE/RMSE；不能只报 R² | N02 fig2; N04 fig3; N06 fig3 | `parity` |
| 残差 / residual | 偏差是否随参考值、样本类型变化 | 明确 prediction − reference；零线；不要改成绝对值后仍叫 residual | N29 fig1; prior F01 | parity companion; custom |
| 箱线 / box | 组间中位数、离散程度、异常值 | 说明四分位数与须定义；小样本叠原始点；不自动配对或推断显著性 | N01 fig3 | `distribution: box` |
| 小提琴 / violin | 分布形状、偏态、多峰 | 标明带宽、归一化方式和 n；原始点/中位数辅助；小 n 不制造光滑确定感 | N03 fig6; N10 fig2–4 | `distribution: violin` |
| 半/分裂小提琴 | 同一条件下的两组分布、随时间的分布变化 | 左右两半含义明确；时间坐标保持真实间距；跨组面积归一化需解释 | N35 fig1,3 | custom |
| 直方 / histogram | 数据落在哪些数值区间、频数如何分布 | 数值箱连续相接；同边界比较；区分 count、fraction、density；不丢尾部 | N07 fig2; N14 fig2; N10 fig4 | `distribution: histogram` |
| 密度 / KDE | 分布形状的平滑估计 | 写带宽与归一化；不能把峰数当作已证实亚群；不要裁掉异常值 | N07 fig6 | violin kernel; custom KDE |
| 累积分布 / CDF | 达到给定阈值的比例 | 经验 ECDF 是阶梯；拟合 CDF 必须标明模型；概率轴 0–1 | N08 fig3, held out: smooth CDF, not identified as ECDF | `distribution: ecdf` is a methodological option |
| 点+区间 / estimate–interval | 估计值和不确定性有多大 | 明确 SD/SE/CI/CrI 或输入范围；适合横排长标签；可用零/一参考线 | N17 fig2; N34 fig2 | `interval` horizontal variant |
| 配对点线 / paired observations | 相同反应在两种方法下如何变化 | 只有真实配对才连线；独立重复不能伪装配对；多样本时弱化连接线 | prior v0.2 comparison task; project option | `comparison` |
| 连续曲线 / ordered line | 时间、浓度、距离等有序变量如何变化 | 不跨缺测连线；不平滑掉噪声；真实 x 间距；实测点与模型线区分 | N01 fig2; N04 fig2 | `curve` |
| 动力学/滴定/校准 | 速率、响应或饱和过程 | 给时间/浓度单位；拟合方法和区间定义；非单调竞争响应不能强套 S 曲线 | N12 fig3; N30 fig4; N32 fig2 | `curve`; fit upstream |
| 学习/收敛/标度曲线 | 样本量、计算规模或迭代的代价/误差 | 对数轴须正值；显示重复或不确定性；斜率比较要求合理比例 | N01 fig4; N04 fig4 | `curve` |
| 带状区间 / ribbon | 连续估计的不确定性随 x 如何变 | 淡色带在点线之下；明确覆盖区间或离散度；容许误差带不是 CI | N17 fig4; N19 fig2; N32 fig2 | `curve` with bounds |
| 类别条形 / bar | 离散类别的真实量级 | 从零起；长标签横排；单色足够时不彩虹；差异很小可换点图 | N05 fig4; N06 fig1 | custom |
| 分组条形 / grouped bar | 少数类别×条件的量级比较 | 组内顺序固定；间隔表示类别；多系列改分面；附真实误差定义 | N03 fig3; N12 fig4; N13 fig3 | custom |
| 堆叠/比例条形 | 可加和构成、阶段去向 | 分母明确；层项真正可加；保留失败/待定；非基底段较难比较 | N19 fig4; N25 fig4 | `stages` for a sequential cohort |
| 热图 / matrix | 两个离散维度上的数值模式 | 有数量/单位色标；缺失≠0；共享范围比较；小矩阵可加数值 | N04 fig5; N09 fig3; N32 fig3 | `heatmap` |
| 混淆矩阵 | 分类结果如何分布 | 真实/预测轴写清；明确总量、行或列归一化；类不平衡不能只看准确率 | N07 fig7 | `heatmap` after explicit calculation |
| 二维密度/hexbin | 大量点如何分布 | 标注 count/probability；写箱尺寸；不要把密度色和类别色混用 | N06 fig1; N35 fig1 | custom |
| 等高线/响应面 | 两个连续量上的第三变量 | 等高线值和色标有单位；正负量可用零中心发散；2D 常比 3D 更易读 | N02 fig3; N20 fig2,4 | custom |
| PCA/降维嵌入 | 特征空间中哪些样本邻近 | 标轴分量，适用时给解释方差；不把任意嵌入距离解释成能垒 | N06 fig2 | custom; embedding upstream |
| 光谱/色谱/质谱 | 峰位、强度、组分与条件 | 区分归一化和 a.u.；NMR/XPS 可反向坐标；m/z 不随意标 Da；选择性峰标注 | N11 fig3; N18 fig1,3; N29 fig11 | `curve` for supplied model traces; specialized tools otherwise |
| 错位叠谱 / offset spectra | 多个条件下峰形如何变化 | 声明垂直偏移；同 x 域；直接条件标签；不要比较已分别归一化的绝对振幅 | N11 fig3; N25 fig3 | custom |
| 衍射拟合+残差 | 观测、模型及偏差是否吻合 | 点=观测、线=拟合、下方=残差、棒=反射位置；明确 Q 或 2θ 单位 | N29 fig1 | custom |
| 电化学/循环性能 | 电位、电流、容量、效率如何演化 | 写参考电极及面积/质量归一化；循环路径按采集顺序；效率不同于容量 | N23 fig3; N24 fig2–4 | custom for loops; `curve` for increasing x |
| 吸附等温/Arrhenius/热分析 | 压力、温度与物性 | 空心/实心可标吸脱附；逆温度/对数变换单位写清；相变区间不瞎拟合 | N25 fig1–3; N28 fig2,3 | `curve` after declared transform |
| 能量剖面 | 离散反应态、能垒与竞争路径 | E/H/G、参考态和单位齐全；示意连接不是 IRC；态名对应结构 | N14 fig3; prior B06 | `energy` |
| 显微图+定量图 | 空间结构如何支持统计结论 | 有物理比例尺、通道和处理记录；同尺度比较；不美化/生成实验图像 | N23 fig4; N26 fig3; N32 fig2 | native image workflow + assembly |
| 结构/机理/流程图 | 化学身份、路径和证据关系 | 化学绘图工具；箭头有明确意义；2D 化学式不冒充 3D 计算结构 | N13 fig1–4; N14 fig3 | `structures`, `workflow`, `assembly` |

Useful options without a development-corpus observation include **Bland–Altman agreement**
(difference versus pair mean; repeated-measure assumptions matter), **raincloud** (half density
plus raw points and summary), **forest** layouts for comparable estimates, and **ROC/PR**
curves for classification. Use them when the question and methodology justify them, and
cite the relevant statistical method. Do not advertise these as frequencies learned from
this JACS sample. Correlation, parity and Bland–Altman answer different questions.

Avoid pie/donut charts for fine comparisons, uncalibrated bubble area, 3D bars, radar areas,
unreconciled waterfalls and Sankey widths with no quantitative mapping. A published example
of a chart is evidence that it occurs, not proof that it is the best choice.
