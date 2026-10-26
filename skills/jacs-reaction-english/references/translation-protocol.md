# Translation protocol and terminology ledger

Use this workflow for a paragraph or larger passage. It avoids literal translation while
preserving chemistry, numbers, and evidence boundaries.

## Before drafting

Record the section, article type, intended audience, source version, and requested output. Make
a small ledger with these columns:

| Source phrase | Chosen English | Scope/definition | Alternatives rejected | Needs author check |
|---|---|---|---|---|

Fill it for every acronym, representation, metric, success definition, and model-specific noun.
Reuse the project ledger on later sections. If a term has no stable English equivalent, retain
the Chinese concept in a note and choose a descriptive English phrase rather than inventing an
acronym.

## Drafting pass

1. Mark each sentence as motivation, method operation, measured result, interpretation, or
   implication. Keep these functions visible in English.
2. Resolve the main verb and its object before polishing modifiers. Prefer `the model predicts
   the TS-WBO matrix` to a noun stack such as `TS-WBO matrix prediction by the model`.
3. Put conditions next to the claim: dataset, split, input, candidate budget, selection rule,
   reference level, and whether the value is pre- or post-refinement.
4. Use the terminology reference for the representation and workflow terms. Check whether
   `generate`, `predict`, `optimize`, `refine`, `validate`, `recover`, and `reproduce` refer
   to different stages in this manuscript.
5. Replace Chinese rhetorical connectors with the actual relation. Use continuation, contrast,
   consequence, or qualification only when the source logic supports it.
6. Keep sentence length moderate. Split a sentence when it carries both a multi-stage method
   definition and a numerical comparison, or when a pronoun could refer to the TS, the candidate,
   or the pathway.

## Verification pass

- Compare every number, unit, symbol, denominator, model name, and panel reference with the
  source. Do not silently convert `ΔE‡` to `ΔG‡` or `pathway recovery` to `TS success`.
- Check that a result reported for a selected subset is not generalized to the full test set.
- Confirm that `reference-conditioned`, `predicted-conditioned`, and `reference-assisted`
  selection remain distinguishable.
- Check that all scientifically distinct curves or panels are named when the paragraph interprets
  a figure.
- Ensure a claim of causality has a discriminating comparison. Otherwise state the design
  operation and use a precise interpretation such as `consistent with`.
- Mark missing facts as `[AUTHOR TO CONFIRM]` or `[VALUE NEEDED]`; never fill them from a
  superficially similar paper.

## Output modes

- **Translation only:** return the English passage. If no ambiguity or claim-strength change is
  present, a prose-only request can remain text-only. If an ambiguity, missing fact, or claim-
  strength correction is material, preserve an inline `[AUTHOR TO CONFIRM]` marker or return a
  compact `Terminology decisions` note even when the user asked for prose-only output; do not
  hide a consequential uncertainty merely to satisfy a formatting preference.
- **Translation plus review:** return the English passage, then a table of consequential choices,
  unresolved facts, and claims that require source confirmation.
- **Skill distillation:** return general rules and synthetic examples; do not copy private
  manuscript sentences or publish unpublished results.

## Minimal example

Chinese source concept: “模型先预测键级图，再在图条件下生成三态构象，最后通过 IRC 验证路径。”

Professional rendering: `The model first predicts a candidate bond-order graph, then generates
R/TS/P conformers conditioned on that graph, and finally validates the resulting pathway by IRC.`

The rendering distinguishes the graph, the generated structures, and the validation operation;
it does not claim that the graph itself is a validated transition state.
