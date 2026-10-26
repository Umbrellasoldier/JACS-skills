---
name: jacs-reaction-english
description: Translate and polish professional English for computational reaction chemistry, transition-state generation, reaction-pathway modeling, and chemical machine learning while preserving chemical meaning, evidence boundaries, and numerical definitions. Use for domain-specific English expression; use jacs-writing for new argument structure and jacs-polishing for general JACS prose editing.
---

# JACS reaction English

Use this skill as the terminology and expression layer for computational reaction chemistry.
It covers Chinese-to-English translation and English revision involving transition states,
reaction pathways, molecular graphs, flow matching, diffusion models, equivariant networks,
machine-learning potentials, and barrier or selectivity analysis. It is a language skill,
not a source of project results and not a substitute for checking calculations.

## Route the request

- For a new argument, section, or manuscript-wide organization, let `jacs-writing` lead and
  use this skill for the domain terminology.
- For editing existing English or translating a supplied passage, let `jacs-polishing` lead
  and use this skill for terminology, collocations, and chemistry-specific claim boundaries.
- For a source-traceable style study, use `jacs-style-distill`; do not turn a handful of papers
  into a universal JACS rule.

Read only the supporting reference needed for the current task:

- [Terminology](references/terminology.md) for canonical terms, variants, and false friends.
- [Claim grammar](references/claim-grammar.md) for section-specific sentence patterns and
  evidence-calibrated verbs.
- [Translation protocol](references/translation-protocol.md) for a manuscript passage or a
  terminology-ledger workflow.
- [Field sources](references/field-sources.md) when the user asks for recent literature,
  citation-aware phrasing, or an update of the field vocabulary.

## Core translation rules

1. Identify the scientific predicate before translating. State what was generated, predicted,
   optimized, validated, or compared; do not translate a Chinese noun phrase into an English
   claim that the source did not make.
2. Keep the representation and validation stage visible. Distinguish a predicted TS graph,
   a generated TS geometry, an optimized stationary point, a path-validated TS, and a barrier
   calculated from a matched candidate and its endpoints.
3. Preserve input conditions and populations beside the result: 2D graph versus 3D endpoint
   conformers, reference-conditioned versus predicted-conditioned generation, single-shot
   versus multi-candidate sampling, selected subsets versus the full test set, and pre- versus
   post-refinement values.
4. Prefer field-native verbs over literal Chinese calques: `encode`, `condition`, `sample`,
   `generate`, `refine`, `relax`, `converge`, `recover`, `validate`, `quantify`, `rank`,
   `reproduce`, and `resolve` when their objects and evidence fit. Use `demonstrate`,
   `establish`, or `enable` only at the strength supported by the data.
5. Preserve symbols, superscripts, units, denominators, dataset names, model names, and
   stereochemical descriptors. Write `kcal mol−1`, `Å`, `RMSD`, `DMAE`, `MAE`, `RMSE`,
   `R²`, and `Spearman ρ` consistently with the source or requested journal format.
6. Translate for an English-speaking chemist rather than word-for-word. Reorder clauses so
   that the actor, operation, object, condition, and consequence are easy to identify.
   Keep a concise active voice in the abstract and Results; use passive voice only when the
   operation or material is more important than its actor.
7. Do not silently strengthen a claim. `suggest`, `support`, and `are consistent with` are
   useful for an interpretation; `show` or `achieve` is appropriate for a measured result;
   `prove`, `solve`, `guarantee`, and `revolutionize` require unusually strong evidence.
8. When a Chinese phrase is scientifically ambiguous, preserve the most defensible meaning
   and flag the decision in a terminology ledger. Do not invent a citation, a validation,
   a causal ablation, or a missing configuration to make the English sound complete.

## Deliverable

For a translation or domain revision, return the English passage in the requested format.
If the task is larger than a sentence, also provide a compact terminology ledger and list
only consequential unresolved choices. For a literature update, give a dated source list with
DOIs or publisher links and label peer-reviewed articles, early versions, and preprints
separately. Public papers calibrate vocabulary; they do not override the user's facts or
turn a field trend into a journal requirement.
