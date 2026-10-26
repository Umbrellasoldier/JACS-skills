# Claim grammar for reaction-methods papers

These are reusable sentence shapes, not text to copy. Insert the actual dataset, model,
population, metric, and condition before choosing a strong verb.

## Abstract

Use a short evidence chain:

1. **Problem:** `Efficient generation of [object] remains difficult because [specific bottleneck].`
2. **Gap:** `Existing approaches [require X / leave Y unconstrained / incur Z].`
3. **Design:** `Here we introduce [method], which [operation] through [representation or staged workflow].`
4. **Mechanistic role:** `The [representation] links [input] to [output] and constrains [specific uncertainty].`
5. **Evidence:** `On [dataset and population], [method] achieves [metric] under [condition].`
6. **Utility:** `After [validation stage], the resulting candidates support [scientific task].`

Do not jump from an intermediate prediction metric to a downstream success rate. Name the
structure-quality or pathway-validation stage that connects them. Separate datasets when they
answer different questions, for example structural accuracy, barrier ranking, or chemical
application.

## Introduction

Group prior work by the input or physical representation that determines the reader's comparison:

`Methods conditioned on [3D endpoint information] can [advantage], but require [practical input].
By contrast, [2D-input methods] avoid that preparation while leaving [bonding, conformation,
or relative orientation] to the generator. These routes motivate an intermediate representation
that [design rationale].`

Use `however`, `by contrast`, or `whereas` only for a real contrast. Use `in addition`,
`more recently`, or a new sentence for continuation. Introduce a cited model for the role it
plays in the argument; do not append a name without explaining its input, output, or limitation.

## Results

Orient the reader before reporting the number:

`We first evaluated [quantity] against [reference source] on [population]. The model [brief
operation] under [input condition]. It achieved [metric], indicating [local interpretation].`

For a multistage result, keep these predicates separate:

- `The model predicts [representation].`
- `The generator produces [structure] conditioned on [graph/endpoints].`
- `The optimizer/refiner yields [stationary point or refined structure].`
- `The validation procedure confirms [IRC connectivity, endpoint identity, or barrier property].`

For all curves in a figure, identify the metric and comparison before grouping the trend. Say
`remained higher across the evaluated budgets` only after checking every budget; say `declined
more slowly` only after checking the change from the first to the last point. Preserve a crossover
when it changes the advertised comparison.

## Methods

Use a compact operation–object–condition structure:

`Given [inputs], the model encodes [representation] and predicts [target]. The resulting
[object] is decoded/conditioned to generate [output]. Candidates are filtered by [criterion]
and validated by [procedure].`

Keep the meaning of core equations, variables, training/inference distinction, and claim-defining
thresholds in the main text. Move exhaustive hyperparameters, seeds, file layouts, and environment
details to the SI only when the SI actually contains them.

## Discussion and conclusion

Use a calibrated causal ladder:

- **Operation:** `The graph explicitly encodes [information].`
- **Observation:** `This design yields [measured advantage] under [condition].`
- **Interpretation:** `The result is consistent with [mechanistic rationale].`
- **Implication:** `This provides a practical route to [application].`

Do not turn a comparison with multiple changed inputs into a component-causal proof. Do not end
every favorable paragraph with a generic limitation. Keep a limitation when it changes the scope
of the headline claim, and place it next to that claim.

## High-value Chinese calques to repair

| Literal tendency | Professional alternative |
|---|---|
| `大幅提高/显著提升` without a test | `increased [metric] by [value]` or `achieved [metric]`; reserve `substantially` for a documented comparison. |
| `解决了……问题` | `addresses [bottleneck]`, `reduces [failure mode]`, or `provides a route to [task]`. |
| `证明了模型有效` | `supports the model's ability to [specific task]` or `demonstrates [measured capability]`. |
| `高效地生成` | `generates [object] with [measured speed/cost]` or simply `generates [object]`. |
| `可以用于` | `can be used to`, `enables`, or `supports`, chosen from the actual demonstrated use. |
| `精确地还原` | `reproduces`, `recovers`, or `matches within [tolerance]`, with the reference and metric stated. |
| `精修结构` | `refines the geometry`, `relaxes the structure`, or `optimizes the TS`, depending on the operation. |
| `能垒变化趋势` | `trend in barrier heights` or `barrier ranking`, depending on whether magnitude or order is measured. |
| `反应成功率` | `reaction success rate` only if a reaction-level success definition is given. |
| `候选成功率` | `candidate success rate` only if the candidate-level denominator is given. |
