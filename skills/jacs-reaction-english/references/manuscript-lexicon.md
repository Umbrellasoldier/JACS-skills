# Manuscript and Supporting-Information lexicon

Read this reference when a manuscript combines transition-state generation with quantum
chemistry, data curation, structural benchmarking, pathway validation, thermochemistry, or a
chemical selectivity application. It is a controlled vocabulary, not a list of mandatory JACS
phrases. Keep the author's definitions and use the narrower term when the operation is known.

## Quantum chemistry and bonding analysis

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 固定几何单点 | single-point calculation at fixed geometry | Say that the nuclei were held fixed when that matters; do not call it geometry optimization. |
| 自洽求解 | self-consistent-field (SCF) calculation / self-consistent solution | Use `SCF convergence` for the numerical condition, not as a synonym for an electronic-structure method. |
| Wiberg/Mayer 键级 | Wiberg/Mayer (AO) bond order / bond index | State the implementation and basis/orthogonalization convention when values are compared across methods. |
| 密度矩阵 | density matrix | `one-particle density matrix` when the order matters; do not call it an electron-density map. |
| 重叠矩阵 | overlap matrix | Keep it distinct from a molecular overlap or structural similarity score. |
| 原子轨道 | atomic orbital (AO) | Use `AO basis` or `atomic-orbital basis`; expand the acronym on first use. |
| 分子轨道 | molecular orbital (MO) | `orbital coefficients`, `orbital occupations`, and `orbital energies` are separate quantities. |
| 闭壳层 | closed-shell | Use `open-shell` only when the spin treatment and multiplicity support it. |
| 分数占据 | fractional occupations | State whether occupations are part of the single-point calculation or a model approximation. |
| 半经验方法 | semiempirical quantum-chemical method | Use `GFN2-xTB single-point calculations` when the method is known; avoid calling xTB DFT. |
| 近似标签 | approximate label / surrogate reference | A low-cost label is not a `ground truth` unless the manuscript defines it as such. |
| 部分成键 | partial bond formation / partial bonding | `bond formation extent` is acceptable when the quantity is a continuous WBO; do not imply a discrete bond. |
| 键断裂程度 | extent of bond cleavage | Use alongside `extent of bond formation` for a reaction coordinate or bonding descriptor. |
| Hammond–Leffler 假说 | Hammond–Leffler postulate | Use `postulate`, not `hypothesis`, when referring to the named physical-organic principle. |
| More O'Ferrall–Jencks 图 | More O'Ferrall–Jencks diagram | Use `two-dimensional mechanistic diagram` only as an explanatory gloss. |
| 协同/非协同 | concerted / asynchronous / stepwise | `concerted` describes mechanism; `synchronous` describes the relative timing or extent of bond changes. Do not use them interchangeably. |

When describing a WBO label, use an explicit predicate: `WBO values were evaluated on the
fixed reference geometry` or `the continuous WBO matrix was decoded into a discrete graph.`
Avoid `the TS is represented by a bond order` when the object is a matrix or graph condition.

## Data curation and benchmark construction

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 原子映射 SMILES | atom-mapped reactant/product SMILES | Use `mapped R/P SMILES` after defining R and P. |
| 规范化去映射 SMILES | canonicalized SMILES with atom maps removed | This is a curation operation; it is not the same as canonical atom mapping. |
| 端点组合 | directed R/P endpoint pair | Say `directed` when reversing R and P creates a separate record. |
| 反应方向 | reaction direction / forward direction | Use `forward` and `reverse` for barriers only after defining the reference endpoint. |
| 去重 | deduplication / duplicate removal | State the identity key, such as canonicalized endpoint strings and stereochemistry. |
| 重叠调整 | overlap adjustment / overlap removal | Use `train–test overlap` or `split overlap`; do not call every removed record leakage. |
| 数据泄漏 | data leakage | Reserve for information crossing the evaluation boundary, not ordinary duplicate removal within training. |
| 元素子集 | element-restricted subset / CHON subset | Name the retained elements and whether the filter was applied before or after splitting. |
| 独立测试集 | independent held-out test set | Use only when it was excluded from training and model selection. |
| 参考层级 | reference level of theory | Write `ωB97M-V/def2-TZVPP reference` or `GFN2-xTB label`, not merely `high-level reference`. |
| 源数据 | source dataset / source records | `source data` can mean a file package; use `source dataset` for a benchmark collection. |
| 反应级统计 | reaction-level aggregation | Distinguish from `pair-level`, `candidate-level`, and `atom-pair-level` aggregation. |
| 反应级完全匹配 | reaction-level exact match | Define the evaluated atom-pair scope and whether all pairs must match. |
| 覆盖率 | coverage / reaction coverage | Give the denominator and the qualifying event; `coverage` alone is underspecified. |
| 前 k 候选覆盖 | Top-k coverage / coverage among the first k candidates | Define the ordering and say whether the event is “at least one qualifying candidate.” |

Use `curated`, `filtered`, `deduplicated`, and `held out` for distinct operations. A sentence
such as `The dataset was curated` is incomplete unless the next clause names the filters or
identity rule that matter to interpretation.

## Generative modeling and representation

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 源分布/目标分布 | source distribution / target distribution | Use in flow-matching descriptions; do not call the source a `reactant distribution` unless it is chemically one. |
| 速度场 | velocity field | `learn a conditional velocity field` is preferred to `learn a flow velocity`. |
| 常微分方程输运 | ODE transport / deterministic transport trajectory | State the integration scheme if it affects reproducibility. |
| 线性路径 | linear interpolation path / linear conditional-flow path | `linear path` is not a physical reaction coordinate unless explicitly defined as one. |
| 显式 Euler 积分 | explicit Euler integration | Use `integration step` for the numerical step and `sampling step` only for a generated sample. |
| 图解码 | graph decoding | Distinguish decoding a continuous matrix from thresholding or snapping it. |
| 对称矩阵 | symmetric matrix | Mention a zero diagonal separately; symmetry does not imply a valid chemical graph. |
| 反应中心原子对 | reaction-center atom pairs | Define the threshold or endpoint-change rule used to select them. |
| 反应关键原子对 | reaction-critical atom pairs | Use for the narrower evaluation set; do not silently replace it with `reaction center`. |
| 三态联合生成 | joint R/TS/P conformer generation | `joint` means the states are generated with shared conditions or information exchange, not merely in one batch. |
| 跨态信息交互 | cross-state information exchange / cross-state message passing | State what is connected, for example corresponding atoms across R, TS, and P. |
| 立体化学条件 | stereochemical conditioning | Use `chirality and alkene stereochemistry` when the actual inputs are known. |
| 噪声种子 | random seed / sampling seed | A fixed seed does not imply bitwise reproducibility when nondeterministic kernels are used. |
| 辅助损失 | auxiliary loss term | Name the constrained property, such as connectivity, stereochemistry, or distance ordering. |
| 预热 | warm-up schedule / loss warm-up | Do not translate as `heating` in an optimization context. |
| 提前停止 | early stopping | Include the monitored validation quantity and patience when relevant. |
| 检查点 | checkpoint | Use `best validation-loss checkpoint` only if that selection rule was used. |

## Geometry, symmetry, and candidate-pool evaluation

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| Kabsch 对齐 | Kabsch alignment / optimal proper-rotation alignment | Add `without reflection` when mirror images must remain distinct. |
| 等价原子置换 | symmetry-equivalent atom permutation | State whether the search is exhaustive, restricted, or heuristic. |
| 距离矩阵平均绝对误差 | distance-matrix mean absolute error (DMAE) | Define the atom-pair set and whether hydrogen atoms are included. |
| 两两 RMSD | pairwise RMSD | Say `within-reaction pairwise RMSD` when the statistic is computed among samples for one reaction. |
| 平均链接层次聚类 | average-linkage hierarchical clustering | Give the distance, threshold, and linkage rule. |
| 最大簇占比 | largest-cluster fraction / maximum-cluster fraction | Define the denominator, such as the number of generated conformers. |
| 代表候选 | representative candidate / cluster representative | Use `medoid` only when the representative minimizes a specified within-cluster distance. |
| 候选池 | candidate pool | Keep generated candidates, filtered candidates, successful candidates, and representative candidates separate. |
| 候选预算 | candidate budget | Use `per-reaction candidate budget` when the budget is fixed per reaction. |
| 参考辅助选择 | retrospective reference-assisted selection | It is an upper-bound or attainable-pool analysis, not a deployment-time selector. |
| 可达到精度 | attainable accuracy / candidate-pool accuracy ceiling | Use `error lower bound` only when the selection procedure mathematically defines a lower bound for the reported sample. |
| 精修前后 | pre-refinement / post-refinement | Name the refinement method; `after optimization` is ambiguous when multiple levels are used. |

For a distribution, state the observation unit before the statistic: `the median of the
reaction-level pairwise RMSD values` is clearer than `the median pairwise RMSD`. A box, violin,
or ECDF does not change the scientific definition of the observation.

## Stationary points and pathway validation

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 驻点 | stationary point | Use for a minimum or saddle point before the Hessian classification is stated. |
| 一阶鞍点 | first-order saddle point | Confirm with exactly one negative Hessian eigenvalue or one imaginary frequency under the stated convention. |
| 鞍点优化 | saddle-point optimization / TS optimization | `refinement` may describe a second method or level; it does not replace `optimization`. |
| 有理函数优化 | rational-function optimization (RFO) | Use `restricted-step RFO (RS-RFO)` or the implementation's exact acronym when known. |
| 去局部化内坐标 | delocalized internal coordinates (DLCs) | Expand the acronym in Methods or SI before using `DLC coordinates`. |
| Hessian 曲率 | Hessian curvature / local curvature of the PES | `Hessian eigenvalues` classify curvature; the Hessian itself is a matrix. |
| 显著虚频 | significant imaginary frequency / negative Hessian mode | Give the threshold if small negative modes are permitted. |
| 模式跟随 | mode following | Say which normalized mode and sign convention were used if reproducibility depends on it. |
| 双向 IRC | bidirectional IRC tracing | Prefer `IRC tracing in both directions` when the sentence also contains a direction-dependent criterion. |
| IRC 端点 | IRC endpoints | The endpoints are path results; do not call them the input R/P structures unless they were shown to coincide. |
| 端点身份 | endpoint identity | Include connectivity, formal charge, stereochemistry, and component identity as applicable. |
| 端点核验 | endpoint-identity verification / endpoint matching | `matching` is appropriate for a comparison; `verification` implies a stated acceptance criterion. |
| 反应路径成功 | validated pathway success / successful recovery of the target pathway | Reserve `TS success` for a saddle-point-only metric. |
| 完整流程成功 | full-workflow success | Define all required stages; use `end-to-end` only when the stated input and output cover the entire claimed workflow. |
| 局部极小点 | local minimum | Confirm with no imaginary frequencies under the stated frequency treatment. |
| 高阶鞍点 | higher-order saddle point | Do not label a structure a TS solely because it has a negative mode. |

The preferred validation chain is `TS optimization → frequency analysis → bidirectional IRC
tracing → endpoint optimization → endpoint-identity verification → thermochemistry`. A result
can be reported at an earlier stage, but the English must name that stage.

## Energetics, thermochemistry, and solvent

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 电子能垒 | electronic activation barrier, ΔE‡ | Define the electronic-energy reference and avoid substituting `free-energy barrier`. |
| 活化自由能 | activation free energy, ΔG‡ | Add `forward` or `reverse` when the endpoint changes. |
| 反应自由能 | reaction free energy, ΔG_rxn | Use for product minus reactant free energy under the stated pairing. |
| 相对能垒差 | relative barrier difference / ΔΔG‡ | Use for competing channels and state the subtraction order. |
| 配对热化学 | paired thermochemistry / candidate-paired thermochemistry | Keep each TS paired with its own IRC-derived endpoints. |
| 准刚性转子–谐振子 | quasi-rigid-rotor harmonic-oscillator (qRRHO) correction | Expand once; state low-frequency treatment and frequency scaling when relevant. |
| 零点能 | zero-point energy (ZPE) | Distinguish `ZPE correction` from the full thermal correction. |
| 热校正 | thermal correction / thermochemical correction | Use `G − E thermal correction` when that exact difference is compared. |
| 频率缩放 | frequency scaling | State whether it applies to frequencies, ZPE, or the full thermochemistry protocol. |
| 气相 | gas phase / gas-phase calculation | Hyphenate the adjective; do not imply a gas-phase experiment. |
| 隐式溶剂 | implicit-solvent model | Name the model, such as CPCM or SMD. |
| 溶剂单点 | single-point solvation-energy correction / solvent single point | Avoid `solvent correction` when the calculation changes more than the solvent energy. |
| 标准态 | standard state | State `1 atm` or `1 M`; do not silently convert between them. |
| 反应物片段 | reactant fragments | Use when a bimolecular reactant is split for paired thermochemistry. |
| 速率常数 | rate constant, k or k₂ | Give units, temperature, solvent, and whether the value is measured or calculated. |
| 速率/选择性联系 | barrier–rate relationship / barrier-based selectivity rationale | A barrier ordering supports a qualitative trend; quantitative product ratios require a kinetic model and conditions. |

Use `at the ωB97M-V/def2-TZVPP level` for a method level, `using ORCA` for software, and
`with qRRHO thermal corrections` for the thermochemical treatment. These are different pieces
of information and should not be fused into one unexplained label.

## Reactivity and selectivity applications

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 应变促进炔–叠氮环加成 | strain-promoted alkyne–azide cycloaddition (SPAAC) | Use the full expansion once; retain the en dash in `alkyne–azide`. |
| 伯/仲/叔烷基叠氮 | primary/secondary/tertiary alkyl azide | Do not use `primary-level` or `tertiary-grade`. |
| 取代基效应 | substituent effect | Specify steric, electronic, or both when the evidence supports it. |
| 位阻效应 | steric effect / steric demand | `steric congestion` is a structural interpretation, not a measured descriptor by itself. |
| 电子效应 | electronic effect | Use `electronic contribution` only when a decomposition or comparison supports it. |
| 相对反应性 | relative reactivity | Say how it is inferred: barrier ordering, measured rate constants, or both. |
| 活性反转 | reactivity reversal / reversal in relative reactivity | Define the substituent or reaction pair across which the ordering changes. |
| 半正交标记 | semiorthogonal labeling | Use for a demonstrated sequential labeling strategy; do not infer it from one barrier comparison alone. |
| 区域选择性 | regioselectivity | `site selectivity` is broader and may include non-regioisomeric sites. |
| 竞争进攻位点 | competing attack sites | Use `competing pathways` when the distinction is a full mechanistic channel. |
| 优势位点 | preferred site / favored site | `major site` is appropriate only when the comparison concerns the major experimental product. |
| 区域异构体比 | regioisomeric ratio | Keep `product ratio` for a measured or explicitly calculated product distribution. |
| 产率 | product yield | Do not use yield as a synonym for selectivity or pathway probability. |
| Diels–Alder | Diels–Alder reaction | Use `cycloaddition` when the reaction class, rather than the named reaction, is the point. |
| 双键形成距离 | forming-bond distance / distance of the forming bond | For two new bonds, label them consistently as `bond 1` and `bond 2` after defining the ordering. |
| 反应机理保真度 | mechanistic fidelity | Use for a validated mechanistic/pathway comparison; geometry similarity alone is insufficient. |

For application prose, prefer `the calculations reproduce the reported ordering of ...` or
`the predicted ordering is consistent with ...`. Use `predicts the experimental selectivity`
only when the selectivity observable and comparison protocol are explicit.

## Cost, throughput, and reproducibility

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 并行总历时 | parallel elapsed time / wall-clock time | Give the hardware and concurrency; do not equate it with CPU time. |
| CPU 线程预算 | CPU-thread budget | State whether it is an allocation or an actually measured utilization. |
| CPU 小时 | CPU-hours | Add across workers only when the accounting convention is explicit. |
| 吞吐量 | throughput | Define the unit, such as reactions per hour or validated candidates per GPU-hour. |
| 折算耗时 | amortized time / normalized time per successful candidate | Say what is divided by what; do not present it as the first-success latency. |
| 端到端耗时 | end-to-end elapsed time | Include the declared input-to-output stages; list omitted queueing, retries, or preparation. |
| 选定路径耗时 | selected-path computational cost | Keep separate from all-candidate or full-batch cost. |
| 失败计算 | failed calculation / failed attempt | Failed attempts remain part of cost accounting when the comparison is workflow-level. |
| 复现 | reproduce / reproduce the reported result | Use `reproduce` for an independent run; `replicate` may imply a new experiment or dataset. |
| 可复现性 | reproducibility / computational reproducibility | Mention code, versions, seeds, data split, and hardware only as actually archived. |

Never write `faster` from candidate count alone. A speed claim needs a common task, fidelity,
hardware/resource budget, timing boundary, and inclusion rule. Prefer `required fewer validated
candidates to reach the same reaction coverage` when that is the measured result.

## Compact sentence patterns

- `At fixed reference geometries, [method] was used to obtain continuous Wiberg/Mayer bond-order labels; no geometry optimization was performed.`
- `The model predicts a continuous TS-WBO matrix, which is decoded into candidate bonding graphs before 3D conformer generation.`
- `We report both atom-pair metrics and reaction-level exact-match coverage because a single pairwise error can invalidate an otherwise matching graph.`
- `Candidates were retained after TS optimization, frequency analysis, bidirectional IRC tracing, and endpoint-identity verification; only then were paired free energies evaluated.`
- `The reported barrier is the candidate-paired activation free energy, referenced to the corresponding IRC-optimized reactant fragments.`
- `Under the stated resource budget, the workflow reached [coverage] with fewer validated candidates; this comparison does not by itself establish a wall-clock speedup.`
- `The predicted ordering of the competing channels is consistent with the reported regioselectivity, whereas the calculation does not by itself predict a product ratio.`

