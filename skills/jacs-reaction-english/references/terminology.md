# Computational reaction chemistry terminology

Use the most specific term that matches the operation. Keep an author-supplied acronym after
its first expansion, and record project-specific choices in a ledger rather than changing them
between sections.

## Transition states, structures, and pathways

| Chinese concept | Preferred English | Use carefully |
|---|---|---|
| 过渡态 | transition state (TS) | Use `TS structure` or `TS geometry` when coordinates are meant. |
| 过渡态构型 | TS geometry / TS structure | `conformation` is usually for a minimum or conformer, not the saddle point itself. |
| 过渡态初猜 | initial TS guess / TS initial structure | `initial guess` means an input to optimization, not a validated TS. |
| 候选过渡态 | candidate TS / generated TS candidate | A generated candidate becomes a validated TS only after the stated checks. |
| 一阶鞍点 | first-order saddle point | Use for the stationary-point property confirmed by Hessian/frequency analysis. |
| 过渡态搜索 | transition-state search | `TS search` is acceptable after the first full use. |
| 过渡态生成 | transition-state generation / prediction | Use `generation` for sampling structures and `prediction` for a model output; do not call every optimization a prediction. |
| 反应路径 | reaction pathway / reaction path | Use `pathway` for a chemically interpreted route and `path` for an algorithmic trajectory when that distinction matters. |
| 路径验证 | pathway validation / reaction-path validation | Include the actual test: IRC connectivity, endpoint identity, stereochemistry, or other criterion. |
| 路径恢复成功 | pathway recovery success / successful recovery of the target pathway | Do not shorten this to `TS success` unless the metric is exactly TS finding. |
| 端点 | reactant and product endpoints | `endpoint conformers` or `endpoint geometries` when 3D coordinates are used. |
| 反应物/产物 | reactant/product (R/P) | Introduce `R`, `TS`, and `P` once and use them consistently. |

## Chemical representations

| Chinese concept | Preferred English | Boundary |
|---|---|---|
| 一维输入 | one-dimensional (1D) input / SMILES input | A SMILES string is a representation, not a 3D structure. |
| 二维拓扑 | 2D molecular topology / 2D reaction graph | Use `connectivity` for graph edges when bond order is not the focus. |
| 键合模式 | bonding pattern / bonding arrangement | Prefer when describing which bonds form, break, or change order. |
| 成键状态 | bonding state | Useful for a particular TS hypothesis; do not use interchangeably with a complete molecule graph without definition. |
| 拓扑 | topology / connectivity topology | `topology` can include the full graph; specify reaction-center or full-system scope. |
| 键级 | bond order | For continuous Wiberg values, write `Wiberg bond order (WBO)` or `continuous WBO`. |
| 过渡态键级 | TS Wiberg bond-order matrix (TS-WBO matrix) | Use `matrix` for the numeric object and `TS-WBO graph` for its graph decoding. |
| 连续 TS 键级图 | continuous TS-WBO graph | Use for a graph whose edges carry continuous WBO values; reserve `TS-WBO matrix` for the numeric matrix. |
| 离散键级 | discretized bond-order class / snapped WBO class | Define thresholds and boundary convention before reporting classification metrics. |
| 离散 TS 键级图 | discretized or snapped TS-WBO graph | Use after thresholding or rounding continuous WBO values; do not call it continuous. |
| 构象 | conformer / conformation | `conformer` is a structure; `conformational sampling` is the process. |
| 构象生成 | conformer generation / conformational sampling | Use `joint conformer generation` only when states are generated together. |
| 立体化学 | stereochemistry | Use `stereochemical information` for input constraints and `stereochemical fidelity` only when measured. |
| 原子映射 | atom mapping / mapped atom correspondence | `atom correspondence` is clearer for cross-state edges. |

## Models and workflow operations

| Chinese concept | Preferred English |
|---|---|
| 条件流匹配 | conditional flow matching |
| 流匹配模型 | flow-matching model / conditional flow-matching model |
| 最优传输 | optimal transport (OT) |
| 确定性输运 | deterministic transport |
| 等变网络 | equivariant neural network; `E(3)-equivariant` or `SE(3)-equivariant` as defined by the model |
| 图条件生成 | graph-conditioned generation |
| 端点条件 | endpoint-conditioned / conditioned on reactant and product endpoints |
| 联合生成 | joint generation / jointly generate R/TS/P structures |
| 多候选采样 | multi-candidate sampling / generate multiple candidates |
| 候选池 | candidate pool |
| 几何筛查 | geometric filtering / geometry-based screening |
| 去重 | deduplication |
| 聚类 | clustering; `hierarchical clustering` if the algorithm is specified |
| 代表性候选 | representative candidate |
| 势能面 | potential energy surface (PES) |
| 机器学习势 | machine-learning potential (MLP) / machine-learned interatomic potential (MLIP) |
| 鞍点优化 | saddle-point optimization / TS optimization |
| 结构精修 | structure refinement / geometry refinement | Use `relaxation` for geometry relaxation and `optimization` for an optimization procedure; do not use `polishing`. |
| 频率分析 | frequency analysis |
| 虚频 | imaginary frequency |
| 内禀反应坐标 | intrinsic reaction coordinate (IRC) |
| 双向 IRC | bidirectional IRC tracing / IRC tracing in both directions |
| 端点身份核验 | endpoint-identity verification |
| 能垒 | barrier height / activation barrier | Use `activation free energy` for ΔG‡ and `activation energy` for ΔE‡ only when the quantity is defined. |
| 能垒排序 | barrier ranking / rank ordering of barriers |

## Metrics and comparisons

- `RMSD` is a structural error; introduce the atom set, alignment, and mapping when they
  affect interpretation. `DMAE` means distance-matrix mean absolute error only if defined that
  way in the manuscript.
- Use `median RMSD`, `mean RMSD`, or `the median of per-reaction RMSDs`, not an ambiguous
  `RMSD median` in prose.
- Use `reaction success rate` for the fraction of reactions with at least one successful
  candidate. Use `candidate success rate` for successful candidates divided by the accepted
  candidate evaluations. Use `reaction coverage` only after defining its denominator.
- `Top-k coverage` or `coverage among the first k candidates` means at least one qualifying
  candidate among the first k under the stated ordering. Do not call a retrospective best
  candidate a deployment result.
- State differences in `percentage points` for rates. Say `with fewer candidates` or
  `reduced the candidate budget` only when the same target and validation unit are compared;
  do not infer wall-clock speed from candidate count alone.
- Use `reproduce the barrier ranking` or `recover the rank ordering` for an ordering result;
  use `predict the barrier` for a numerical prediction. Report `Spearman's ρ` with the tested
  population and selection protocol when they matter.

## Capitalization and style

Use `Diels–Alder`, `Suzuki–Miyaura`, `strain-promoted alkyne–azide cycloaddition (SPAAC)`,
`Wiberg bond order`, `Gaussian`, `GFN2-xTB`, `ωB97M-V`, `qRRHO`, and `DFT` as written by the
source or journal style. Keep `Transition1x` and `Transition1X` exactly as the dataset owner
uses them in the cited source; do not silently normalize a project spelling. Use en dashes in
chemical names and ranges, and a true minus sign in units and mathematical notation where the
document format supports it.
