# Section decisions

These are editorial heuristics. They are not measured journal-wide frequencies or official
requirements. Use the author's argument and the actual article structure to choose among them.

| Target | Useful decision | Evidence-sensitive check |
|---|---|---|
| Title | Name the chemical task or finding; identify the method only if it helps readers understand the contribution. | A model acronym may need expansion or removal under the title policy. Do not improve novelty by adding unsupported priority claims. |
| Abstract | Connect the problem, present contribution, decisive evidence, and bounded consequence. | Include a number only if it carries the claim. Do not turn the abstract into a list of modules or invent a mechanism to complete a template. |
| Introduction | Narrow from the chemical need through specific prior capabilities to the remaining question. | Distinguish an independently checked literature gap from what the supplied manuscript claims. A relevant Perspective can inform context but is not a research-article skeleton. |
| Method overview | Explain the input, output, and scientific purpose of each consequential choice. | Separate information available at deployment from information used during training or retrospective assessment. Put reproducibility details where they can be found. |
| Results and Discussion | Order the evidence by the questions it resolves; attach local interpretation to the relevant result. | Compare matched tasks, budgets, populations, and definitions. Experimental validation, computational support, and a proposed explanation carry different claims. |
| Computational details | Record the model, electronic state, reference state, environment, and consequential thresholds. | Preserve actual settings. Do not fill absent basis sets, solvent models, temperature, or standard-state corrections from convention. |
| Conclusion | State what the work establishes and where it applies. | Do not introduce a new result, stronger validation stage, or untested application. |
| Figure or scheme caption | Explain the comparison, labels, quantities, and conditions needed to read the figure. | A schematic pipeline is not evidence that all stages succeeded. Distinguish representative candidates from a population statistic. |

For a Communication, retain these reasoning functions without adding article-style section
headings. For an Article, keep the actual appropriate section organization; Methods may
precede or follow Results or be documented in SI when the journal allows it.

When moving material to SI, keep in the main text the information that changes the central
conclusion or comparison. Repetition, exhaustive screening tables, and implementation details
can often move; adverse results cannot disappear just because they interrupt a tidy story.

## Method papers with several evidence stages

Use [argument and evidence](../../jacs-shared/references/argument-and-evidence.md) when the
author asks for stronger contribution framing or a substantial revision.

- **Abstract:** when central to the paper, link intermediate prediction, generated structure
  quality and downstream validation/use. Give different datasets distinct evidential roles;
  keep reference-conditioned and prediction-conditioned results identifiable.
- **Introduction:** organize prior work by the relevant scientific distinction and complete
  input requirements. Add new studies where they change that account; choose connectors from
  the actual logic rather than manufacturing a contrast.
- **Results:** establish the dataset, target/reference and brief model context before the
  performance interpretation. Relate a clear finding to the design and scientific use. Cover
  distinct plotted criteria without converting the paragraph into a point-by-point log.
- **Discussion:** synthesize why the observed pattern matters and how it relates to the design.
  Avoid simply repeating the Results or attaching a generic limitation to every advantage.
- **Methods and SI:** retain design, representations, core formulas and workflow in the main
  account; move detailed settings with verifiable destinations. Preserve claim-defining
  population, selection and validation information near the relevant result.

These are conditional choices, not mandatory section templates. A short edit need not invoke
all of them, and an interpretation remains distinct from an isolated causal demonstration.
