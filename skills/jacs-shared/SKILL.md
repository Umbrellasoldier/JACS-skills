---
name: jacs-shared
description: Internal reference support for JACS writing, figures, polishing, and style distillation. Load a specific referenced file when another JACS skill needs journal policy, chemistry semantics, or corpus provenance; not a standalone workflow.
---

# Shared JACS references

Read only what the requesting task needs, then return to that skill's workflow.

- [Journal policy](references/journal-policy.md): JACS Article/Communication distinctions,
  source date, and actual title, abstract, length, and submission-stage requirements.
- [Chemistry semantics](references/chemistry-semantics.md): energy definitions, TS/path
  validation, selectivity, and model evaluation boundaries.
- [Project facts](references/project-facts.md): author data and terminology, separate from
  journal-level observations.
- [Pilot findings](references/pilot-findings.md): scope and reviewed interpretation of the
  first corpus pilot.
- [Style rules](references/style-rules.jsonl): conditional corpus observations with locators.
- [Corpus manifest](references/corpus-manifest.jsonl): bibliography, split, and acquisition state.
- [Pilot annotations](references/pilot-annotations.jsonl): paraphrased evidence notes and locators.
- [Pilot statistics](references/pilot-statistics.json): measured counts and tokenization scope.
- [Graphics policy](references/graphics-policy.md): main figures and TOC specifications.
- [Figure corpus](references/figure-corpus.jsonl): separate image availability and visual review.
- [Figure annotations](references/figure-annotations.jsonl): original source-located visual notes.
- [Figure rules](references/figure-rules.jsonl): conditional observations with paper counts.
- [Figure findings](references/figure-findings.md): actual coverage, held-out checks and limits.

Policy, observations, scientific semantics, and project facts are different evidence classes.
Do not present a corpus heuristic as an ACS requirement or infer results from an example profile.
