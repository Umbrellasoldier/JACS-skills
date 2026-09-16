# v0.1.0 validation report

Date: 2026-09-17. This report distinguishes code checks from limited language-model behavior
assessment. **The paired trial did not demonstrate a consistent writing-quality improvement
over a generic JACS prompt.** It supports the narrower conclusion that the tested workflows
completed these tasks without an unresolved material factual error identified by the evaluators.

## Deterministic checks

| Check | Observed result |
|---|---|
| Python unit tests | 25 passed locally on Python 3.10.19. Synthetic sources and network mocks only. |
| Skill structure validation | All four skill entrypoints passed the skill-creator frontmatter/scaffold validator. |
| Repository and actual local source audit | Four skills, 34 records, eight pilot papers, 35 annotations, five rules; no unresolved reference, hash, or split errors. |
| Lint and formatting | Ruff checks passed with the locked development environment. |
| Installation | Four sibling dependencies installed into a temporary directory. Collision protection, replacement, rollback, and backup preservation after failed recovery were tested. |
| Real source path | Eight development BioC imports and one holdout fetch succeeded. A09 and other unacquired records are not counted as analyzed full text. |

The tests cover identity mismatches, explicit user assertions when a source lacks a DOI,
section corrections, chemical text and locator preservation, nested JATS abstracts,
caption/Methods/holdout exclusion, duplicate versions, altered text digests, unresolved
metadata lookup, retrieval fallback, cached-source integrity, and installation recovery.
They do not run calculations or prove scientific validity of an underlying manuscript.

Reproduce the offline checks using the commands in the [README](../README.md). The actual-source
audit additionally requires the local normalized text, which is not distributed. Public
source URLs, offsets, versions, and digests are in the corpus files. The GitHub workflow runs
the same repository/unit/lint checks in a clean Python 3.11 environment.

## Paired forward test

- Inputs: [13 tasks](requests.json), comprising 12 synthetic tasks and one source-derived
  held-out task. Topics included drafting, local edits, compression, energy-unit conversion,
  conditional denominators, restricted generalization, Communication structure, journal routing,
  abstract-only evidence, unverified citations, missing computational settings, and exclusions.
- Skill arm: a separate agent context could read the applicable skill and references.
- Baseline arm: a separate agent context used ordinary scientific-writing judgment and a generic
  clear/precise JACS instruction, with the same literal tasks and author facts.
- Both arms used the parent-inherited model/configuration with no model override. The agent tool
  did not expose an exact backend model identifier or sampling seed; these are not claimed.
- No browsing was performed by the writing arms. Each arm processed the 13 cases in its own
  context; cases within one arm are not independent model trials.
- An independent agent compared anonymized pairs for fidelity, requested scope, clarity, and
  argument quality. Pair labels were shuffled per case using seed 20260917. This was agent
  assessment, not human blind review or a statistical study.

Actual outputs: [skill arm](outputs/with_skills.json), [baseline arm](outputs/baseline.json),
[initial blind assessments](outputs/blind_review.json), and [condition mapping](outputs/key.json).
The [instruction snapshot](skill-snapshot.json) records the files used for the initial trial.

### Result and adjudication

The initial assessment recorded 12 ties and preferred the baseline in R01. It flagged a dated
policy reference as unsupported because the blind evaluator had not been given that reference.
The date was present in the permitted skill reference. After receiving this missing provenance,
the evaluator [adjudicated R01 as a tie](outputs/r01_adjudication.json), with no material factual
error and only a minor concision preference for the baseline.

Thus the final paired assessment is **13 ties**, with no identified unresolved material factual
errors in either arm. The tasks supplied many of their own constraints, and the baseline
performed well. This result does not establish a stylistic advantage, a quantitative accuracy
rate for future work, or improved publication prospects.

The R01 output did expose avoidable metadata in a simple routing answer. A narrow instruction
revision made snapshot-date reporting conditional on its relevance. The subsequent
[single-case output](outputs/r01_followup.json) omitted the irrelevant date. Original outputs
and the original blind review are preserved; [change hashes](followup-changes.json) distinguish
the follow-up from the initial experiment. The wording change was:

```diff
- if offline, report this snapshot's date. JACS Au is a separate journal.
+ Use the snapshot date when an answer depends on an unrefreshed JACS requirement; a routing
+ answer need not add unrelated policy metadata. JACS Au is a separate journal.
```

### Held-out source

H01 used an authoring-agent paraphrase of A08's abstract after the initial style cards were
written. The record remained in the preassigned holdout group. Source:
[JACS, DOI 10.1021/jacs.5c00838](https://doi.org/10.1021/jacs.5c00838);
[version and locator](holdout-provenance.json). Only the supplied facts were passed to the
writing arms; no original prose was a wording-reproduction target. A single short task cannot
establish held-out manuscript quality or cross-domain generalization.

## Remaining limits

The empirical style pilot covers eight Articles, selected passages rather than exhaustive
rhetorical annotation, and an uneven set of topics and author groups. Three sources are author
manuscripts. Communication and Perspective prose are not empirically calibrated. Automatic
skill selection, long manuscripts, independent human preferences, cross-model behavior, PDF/OCR
quality, and journal-wide style coverage remain unvalidated. The installed skills provide
traceable guidance and tools; evidence of broad stylistic improvement remains future work.
