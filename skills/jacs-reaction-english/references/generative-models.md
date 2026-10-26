# Generative-model terminology for reaction chemistry

Use this reference for diffusion, score-based, flow-matching, and related generative-model
passages. The terms describe the learned generative process and its evaluation. They do not turn
the model trajectory into a physical reaction pathway.

## Diffusion and score-based models

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 扩散模型 | diffusion model / denoising diffusion model | Use `denoising diffusion probabilistic model (DDPM)` only for the specified formulation. |
| 基于分数的生成模型 | score-based generative model | Use when the network estimates a score field or an equivalent noise-conditioned gradient. |
| 正向加噪过程 | forward noising process / forward diffusion process | Describe the perturbation kernel or noise schedule when the process is part of the method. |
| 反向去噪过程 | reverse denoising process / reverse-time generative process | Do not call it a reaction pathway. It reconstructs samples in representation space. |
| 噪声调度 | noise schedule / variance schedule | State whether the schedule is variance-preserving, variance-exploding, or another parameterization. |
| 噪声水平 | noise level / diffusion time / timestep | Use `diffusion time` for a continuous-time formulation and `timestep` for a discrete index. |
| 分数网络 | score network / time-conditioned score network | The score is a field such as ∇x log p_t(x), not a generic confidence score. |
| 去噪分数匹配 | denoising score matching | Use for the training objective, not for the sampler. |
| 反向时间 SDE | reverse-time stochastic differential equation (SDE) | State the noise term and solver if they affect sampling or reproducibility. |
| 概率流 ODE | probability-flow ordinary differential equation (ODE) | It shares marginal densities with a diffusion formulation under the stated conditions. It is not automatically a physical trajectory. |
| 采样器 | sampler / numerical sampler | Name DDPM, DDIM, ancestral, predictor–corrector, or the ODE solver when relevant. |
| 采样步数 | sampling steps / number of function evaluations (NFE) | Use NFE for network or vector-field evaluations. Do not equate it with the number of generated candidates. |
| 分类器引导 | classifier guidance | Name the classifier and the target property or condition. |
| 无分类器引导 | classifier-free guidance | State the conditional and unconditional predictions and the guidance scale when it matters. |
| 属性引导 | property guidance / property-conditioned sampling | `Property guidance` may alter the sampling distribution. It is not evidence that the property is preserved without evaluation. |
| 扩散轨迹 | denoising trajectory / diffusion trajectory | Use for the model's trajectory through noisy representations. Reserve `reaction pathway` for a chemically validated path. |

For a molecular diffusion model, identify the variables that are diffused. Coordinates, atom
types, charges, bonds, and latent features can have different noise processes. Do not write that
the model diffuses a molecule when it diffuses only coordinates or a latent representation.

## Flow matching and continuous transport

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 流匹配 | flow matching | Use for training by regressing a vector field along a prescribed probability path. |
| 条件流匹配 | conditional flow matching (CFM) | State the conditioning variable and the conditional path. |
| 概率路径 | probability path / conditional probability path | This path connects distributions in representation space. It is not a molecular reaction coordinate by default. |
| 速度场 | velocity field / conditional velocity field | Prefer `learn a conditional velocity field` to `learn a flow velocity`. |
| 向量场回归 | vector-field regression | Use when describing the flow-matching objective or its target field. |
| 常微分方程输运 | ODE transport / neural ODE transport | Name the solver and integration tolerance when they affect NFE or wall-clock cost. |
| 最优传输插值 | optimal-transport (OT) displacement interpolation | State that OT defines the path or coupling. Do not infer that the learned map is a unique chemical mechanism. |
| 确定性采样 | deterministic sampling / deterministic ODE sampling | Deterministic means fixed initial state, conditions, solver, and numerical settings. A random initial latent still gives different samples across seeds. |
| 无模拟训练 | simulation-free training | Use for flow matching when training avoids solving the generative ODE. It does not mean the model uses no numerical integration at inference. |
| 概率流 | probability flow | Use with an ODE or a specified flow formulation. Avoid using it as a synonym for a reaction flux. |
| 随机插值 | stochastic interpolant | Use for the framework that connects endpoint distributions with a tunable stochastic process. |
| 曲率反应轨迹 | curved transport trajectory | Use for a learned generative trajectory. It is a reaction path only after chemical validation. |

The standard flow-matching description is `the model regresses a conditional velocity field that
transports a source distribution to a target distribution along a prescribed probability path`.
Name the source, target, coupling, path, and integrator when they affect interpretation.

## Molecular geometry and conditioning

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| E(3) 等变 | E(3)-equivariant | A transformed input produces a correspondingly transformed output. This is different from invariance. |
| SE(3) 等变 | SE(3)-equivariant | Use when reflections are excluded by the model or task. |
| 不变表示 | invariant representation | A scalar or feature remains unchanged under the stated group action. |
| 坐标与离散特征联合生成 | joint generation of coordinates and categorical features | Name atom types, charges, bonds, or other discrete variables explicitly. |
| 原子扩散和键扩散 | atom diffusion and bond diffusion | Use only when the model has separate or joint processes for both variables. |
| 图条件生成 | graph-conditioned generation | State whether the graph supplies connectivity, bond order, atom mapping, or reaction-center labels. |
| 端点条件生成 | endpoint-conditioned generation | Define whether the endpoints are 2D graphs, 3D conformers, or both. |
| 目标条件生成 | target-conditioned generation | Name the target, pocket, property vector, or reaction condition. |
| 潜空间控制 | latent-space control / latent-space optimization | Do not call a latent direction interpretable unless the property or structure relation was evaluated. |
| 解耦语义嵌入 | disentangled semantic embedding | Use only when the training objective or analysis supports separation of factors. |
| 自条件 | self-conditioning | State whether the model reuses a previous prediction as an additional input. |
| 分布漂移 | distribution drift / inference-time distribution drift | Use when the model encounters intermediate states or inputs outside the training distribution during sampling. |
| 几何扰动训练 | geometry-distortion training / training with distorted geometries | Distinguish the training augmentation from physical thermal sampling. |
| 虚拟原子 | fake atoms / auxiliary atoms | Define their role in padding, variable-size generation, or graph completion. |

For geometric generation, write `E(3)-equivariant` or `SE(3)-equivariant` with the group. Do not
use `equivariant` as a synonym for geometrically accurate, physically valid, or chirality-aware.

## Sampling, control, and evaluation

| Chinese concept | Preferred English | Boundary or collocation |
|---|---|---|
| 条件采样 | conditional sampling | Put the condition beside the metric or claim. |
| 单样本生成 | single-sample generation | Avoid `single-shot` when it could be confused with a single-step reaction. |
| 多候选采样 | multi-candidate sampling / candidate-pool sampling | Define the candidate budget and ordering. |
| 初始噪声 | initial noise / initial latent | State whether the latent is fixed, resampled, or paired across methods. |
| 生成样本 | generated sample / generated candidate | Use `candidate` for a structure entering downstream screening or validation. |
| 生成分布 | generated distribution / model distribution | Do not equate it with the empirical training distribution without a comparison. |
| 有效性 | validity | Define the chemical, geometric, or task-specific validity test. |
| 唯一性 | uniqueness | State whether duplicates are removed by graph, conformer, or coordinate identity. |
| 新颖性 | novelty | Define the reference set and similarity threshold. |
| 多样性 | diversity | Give the structural distance or property distribution used to compute it. |
| 覆盖率 | coverage / mode coverage | State the modes, reference set, or qualifying reaction events. |
| 物理合理性 | physical plausibility | Define the energy, force, geometry, or stability criterion. It is not the same as chemical validity. |
| 化学有效性 | chemical validity | Define connectivity, valence, charge, stereochemistry, and any pathway checks. |
| 条件满足率 | conditional success rate / condition-satisfaction rate | Name the condition and denominator. |
| 样本质量 | sample quality | Replace this broad term with validity, energy, diversity, fidelity, or the measured property. |

For transition-state generation, keep four levels separate: generated geometry, optimized
stationary point, first-order saddle, and pathway-validated candidate. A diffusion or flow model
can generate a useful initial guess without having located a TS or recovered the target pathway.

## Claim boundaries

- `The model learns the reaction distribution` requires a defined reaction representation, data
  split, and conditioning variables. Use `learns a distribution over [representation]` when the
  object is narrower.
- `The model discovers a new pathway` requires pathway construction and chemical validation. A
  lower predicted barrier or a distinct generated geometry supports a candidate hypothesis only.
- `The model is deterministic` requires fixed initial conditions and numerical settings. A
  deterministic ODE sampler can still produce a stochastic ensemble when the initial latent is
  resampled.
- `The model is physical` requires a stated physical constraint, energy model, or dynamical
  interpretation. Equivariance and low geometric error do not establish physical dynamics.
- `The model is high-throughput` requires a common task, fidelity, hardware, concurrency, and
  timing boundary. Fewer NFE or sampling steps alone does not establish lower end-to-end cost.

## Compact sentence patterns

- `The forward diffusion process perturbs [coordinates, categorical features, or both] according to
  [noise schedule], while a time-conditioned network learns [the score, noise, or denoised state].`
- `At inference, the reverse-time [SDE or ODE] generates [candidate structures] conditioned on
  [graph, endpoints, or properties] using [sampler] and [NFE] network evaluations.`
- `The flow-matching objective regresses a conditional velocity field along a [linear or OT]
  probability path from [source distribution] to [target distribution].`
- `The ODE trajectory is a transport path in representation space. We use IRC validation to
  determine whether a generated TS candidate recovers the target reaction pathway.`
- `We report validity, uniqueness, novelty, diversity, and pathway success separately because
  these metrics answer different questions about the generated candidate pool.`
- `With the initial latent, condition, solver, and numerical settings fixed, the flow sampler is
  deterministic. Resampling the latent produces an ensemble of candidates.`
