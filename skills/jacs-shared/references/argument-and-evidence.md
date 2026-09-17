# Persuasive scientific argument from author evidence

Use for contribution-focused drafting, structural revision, or learning an author's preferences
from paired drafts. These are editorial decisions informed by author feedback and revision
comparisons, not measured JACS-wide conventions. Apply the relevant parts at the requested scale.

## Lead with what the result establishes

Give each substantial result a scientific purpose: the question, decisive observation,
interpretation and consequence for the method or chemistry. Lead with a supported advantage
and use precise comparisons to make it persuasive. A reader should learn what improved,
under what conditions, and why that improvement matters.

Replace audit-like narration, implementation inventories and repeated self-disqualifying endings
with a coherent result. An accurate statement need not end with a request for further validation.
Do not add a limitation paragraph merely because a comparison is observational. Conversely,
retain conditions that define the result: successful subsets, reference-assisted selection,
different model/input settings, and the actual validation stage. Put these compactly beside
the claim or in a clearly connected caption/method definition; do not hide a headline-changing
qualification only in SI. Report an outcome that changes the central comparison where needed.

Prefer the strongest supported formulation over either promotional overstatement or reflexive
caution. These original synthetic rewrites illustrate different evidential roles:

| Evidence and intent | Useful wording |
|---|---|
| A reference-assisted selection finds accurate candidates; emphasize the pool's quality | “Reference-assisted selection identified accurate structures within the generated candidate pool.” |
| Architecture explicitly conditions coordinates on a chemical graph | “The graph supplies an explicit chemical condition for coordinate generation.” |
| Different systems show different sampling distributions; no component ablation | “The more concentrated distribution is consistent with organizing conformational sampling around an explicit bonding hypothesis.” |
| Candidate quality stays above a baseline, but its absolute decline is larger | “The method maintained a higher cumulative candidate success rate across the evaluated budgets.” |

Keep the factual predicate strong and specific. Qualify an uncertain explanation locally, not
the whole established result. Do not replace meaningful chemistry with repeated claims of
robustness, superiority, significance or novelty.

## Connect the stages of a method paper

For a multistage generation-and-validation paper, connect the intermediate representation,
the structures it produces, and the downstream useful outcome in the abstract and Results.
When each is central and supported, do not jump from representation accuracy directly to
validation yield while omitting structure quality. Distinguish reference-conditioned geometry
tests, prediction-conditioned generation and post-refinement performance. Do not turn a geometry
metric on a successful subset into one for all test cases.

Give each dataset a role. One may establish geometry and budget efficiency; another may test
larger systems, pathway coverage or barrier ranking. Present their results separately enough
to preserve conditions and purpose. Do not pool denominators or infer broad transfer solely
from a different dataset name. Author-requested emphasis guides which supported metrics lead;
it does not require every future abstract to contain the same datasets or a fixed number list.

In a Results subsection, a useful order is reference/target provenance, a brief explanation of
the evaluated model, then prediction performance and its meaning. Introduce the dataset and
population at first use. If these are already clear locally, avoid repeating a miniature Methods
section. Explain what a plotted comparison tests before asking readers to interpret its numbers.

## Build logical introductions

Choose transitions by their actual relationship: continuation, classification, contrast,
consequence or a remaining question. A taxonomy of methods by available inputs does not itself
justify “however” or “但.” Make the subject and relationship explicit instead of mechanically
swapping connectors. Genuine contrasts still benefit from contrastive language.

Describe the complete practical input requirement. For a method conditioned on optimized 3D
endpoints, going from SMILES may require conformer construction, geometry optimization, fragment
placement and endpoint pairing; check what the cited method actually requires. Compare routes
fairly rather than manufacturing a weakness in a competitor.

Add relevant prior work where it changes the argument about inputs, generation, physical search
or chemical application. Explain its role rather than appending names. When adding or updating
citations, verify claims against available primary sources, distinguish author-supplied from
independently checked statements, and update citation numbering/references together. A method
named in one author's revision is not mandatory background for every manuscript.

## Reconcile text, figures and numbers

For affected claims, maintain a small local source map: source/version, model and input setting,
dataset/population, metric definition, unit, selection rule, panel/curve and manuscript locations.
Use it to reconcile the abstract, Results, caption, table and SI after changes. Ordinary local
grammar edits do not need a manuscript-wide ledger.

When adjacent numbers differ, first check whether they describe different models, selected
populations, budgets, references or runs. Explain a legitimate distinction where readers meet
it; do not force equality through rounding or silently replace a result. When no source resolves
the conflict, leave a focused author query while completing supported prose.

Account for every scientifically distinct panel or curve relevant to the argument. A panel
with four criteria needs those four criteria identified, not a discussion of only two selected
curves. Group related trends rather than reciting every plotted point. Distinguish binary
connectivity from bond-order-labeled graph agreement and whole-graph from reaction-center
criteria when used. After adding a panel, update downstream panel letters, cross-references,
captions and Source Data references together.

### Candidate-budget comparisons

Keep the unit of analysis explicit. With N reactions, k candidates per reaction, and success
indicator s_ij, cumulative candidate success is sum(s_ij)/(N k), whereas reaction success is
the fraction of reactions with at least one success among the first k candidates. If some
reactions lack k candidates, use the actual design and denominator rather than applying N k.
Establish the success definition, order and tested population; do not sort by eventual success
or reference error unless reporting that retrospective protocol explicitly.

Organize the narrative around initial yield, the budget needed for a meaningful coverage target,
and candidate quality as the budget grows. These are different advantages. Check the full
reported range before saying “always,” “more slowly” or “saturates.” A curve can remain higher
while declining faster, and a method can lead at low budgets while a competitor leads at the
largest budget. Emphasize the supported regime and preserve a reversal relevant to the claim.

When an author's proposed advantage does not match the data, substitute the strongest accurate
advantage in the manuscript. Do not add a rebuttal of the drafting instruction as a new result.
For example, stating both curves' endpoints and sustained separation can explain higher candidate
quality without an extra sentence foregrounding the larger decline. Retain a crossover or other
outcome that changes the advertised comparison; put additional diagnostic arithmetic in edit
notes when requested or needed to resolve the claim. This is a placement decision, not permission
to hide data or preserve an unsupported “slower decline” assertion.

State rate differences in percentage points; a relative candidate-budget reduction uses the
baseline budget as denominator. Use the first observed qualifying budget at a specified target;
do not invent intermediate measurements or silently change the target. Fewer validated candidates
establishes a candidate-budget advantage, not automatically lower wall time or total compute.
Distinguish cumulative candidate success from success at the newly added rank.

When tabular source data are available, independently recompute consequential comparisons and
reconcile curve/text values. Data's analysis-quality criteria inform these checks; the task
remains manuscript writing unless the user also requests analysis or a new plot. A quoted past
plotting instruction is evidence of revision intent, not an instruction to execute it again.

## Explain why without overstating causality

Connect a design choice to its operational consequence and the observed result. The architecture
can establish what information is supplied, what is constrained and how sampling is organized.
Performance observations establish what the evaluated system achieved. A controlled comparison
or other discriminating evidence is needed to isolate a component's causal contribution.

Use direct design language for verified operations and confident result language for observed
advantages. Use “consistent with,” “supports this design rationale,” or an equivalent precise
interpretation when the explanation is not isolated. Do not dilute every result with “may.”
Also do not turn a plausible rationale into “proves that component X caused the improvement.”
Architecture differences can be stated compactly as part of the comparison's identity rather
than an obligatory concluding sentence about missing ablations.

## Separate main-text explanation from SI detail

| Keep in the main scientific argument | Place in SI or a reproducibility record when requested/appropriate |
|---|---|
| Problem, design rationale, inputs/outputs and how stages connect | Exhaustive configuration, file layouts, commands, seeds and environment locks |
| Essential representations, core equations, symbol meanings and training/inference distinctions | Full auxiliary losses, tuning ranges, optimizer settings and implementation variants |
| Definitions and conditions needed to interpret headline metrics | Expanded metric derivations, secondary tables and detailed stage diagnostics |
| Selection/validation principles and claim-defining populations/budgets | Complete thresholds and procedures, retaining a threshold locally if it defines the claim |
| Which reference/theory supports each comparison, including material version differences | Detailed computational settings, exact archived versions and parameter manifests |

Main Methods should explain the scheme, design, formulas and workflow, including what an overview
figure leaves ambiguous. Each essential equation needs defined symbols and a clear role; moving
parameter values should not remove the meaning of the model. Keep source-version distinctions
that change reported results even when their engineering explanation moves to SI.

For a requested main-text/SI reorganization, track each moved item to its destination, including
equations, tables and cross-references. Check the actual SI, not merely a new “see SI” phrase.
If the user requests separate Word documents, deliver both and inspect the requested formats;
do not count a prose outline as a completed SI. If SI is absent from a paired-draft review,
record that its contents were not checked and continue learning from the supplied documents.

## Learn from paired revisions

Separate the author's stated intent, observed changes, and changes that source evidence supports.
Keep a local map of before/after paragraph or table locations and consequential numerical checks.
An accepted revision guides tone and structure; it does not automatically validate every new
number, citation, causal sentence or SI reference. Preserve effective existing text where the
revision did not need to change it.

Distill conditional rules, not project-specific sentences or a universal list of favored methods.
Use newly authored synthetic examples for public demonstrations. Unpublished manuscript text,
results, figures, source files and identifying local paths stay in the author's local workspace.
Do not expand a request to learn/update skills into a new manuscript rewrite, plot or SI delivery
merely because those actions appear in the quoted historical prompt.
