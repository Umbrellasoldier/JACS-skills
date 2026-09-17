# JACS figure skill evaluation — v0.2.0

Date: 2026-09-17. The implementation runs and preserves the tested scientific information.
The first small blind comparison **does not demonstrate a visual-quality advantage over an
agent working without the skill**. Its main verified contributions are explicit evidence
contracts, source-traceable guidance, reusable tooling and reviewable delivery records.

## Mechanical and source checks

| Check | Actual result | Boundary |
|---|---|---|
| Repository unit/integration suite | 51 tests passed with figure and chemistry dependencies installed | Synthetic data, mocked acquisition, local rendering; no GPU or private data |
| [Acceptance cases](cases.json) | 12/12 expected behaviors; see [actual results](acceptance-results.json) | Six normal figure families, five invalid-input rejections and one alignment failure detected |
| Original gallery | Six families plus TOC generated as PDF/SVG/PNG; TOC also TIFF | Structure layout remains `UNKNOWN` to the automatic auditor and was inspected visually |
| Corpus | 14 papers; 49 figures actually viewed | 40 development/calibration observations and 9 post-freeze held-out checks |
| Frozen evidence | Annotation and rule hashes match [freeze record](rule-freeze.json) | Does not establish independent scientific validity of published results |
| Skill packaging | All five entrypoints validated; complete installation and installed structure-render smoke check succeeded | Runtime dependencies stay in the separate project environment |
| Archived forward programs | Both published program snapshots reran successfully in isolated local copies | Regenerated PDF metadata/hashes may differ from the evaluated originals |
| Export checks | Physical PDF dimensions, transformed text sizes, declared panel alignment, TIFF pixel dimensions | Font embedding, arbitrary graphic collisions and embedded-image source DPI are not fully audited |

Meaningful regressions cover incompatible energy definitions, nonfinite data, mismatched
reaction sets, stage denominators, zero entrants, explicit log-domain failures, atom maps and
stereochemical identity, local asset integrity, current PMC version identity, source checksums,
clipping, displaced panels, transformed PDF text and SVG resource references.

The six gallery families and TOC were opened as actual PNG renders. At release-size dimensions,
the PDF auditor checks the supported text/layout properties. Structure depictions retain
opposite wedge conventions; energy connectors are explicitly schematic; paired comparisons
contain no invented uncertainty. Raster source papers were not used as generation assets.

Commands from the repository root:

```bash
uv sync --locked --group dev --group figures --group chemistry
uv run --locked --group dev --group figures --group chemistry python -m unittest discover -s tests -v
uv run --locked --group figures --group chemistry python scripts/evaluate_figures.py --output-dir local/figure-evaluation
uv run --locked --group dev python scripts/validate_repository.py
uv run --locked --group dev ruff check .
uv run --locked --group dev ruff format --check .
```

## Frozen-rule transfer check

The [split](split.json) precedes rule derivation; the [rule freeze](rule-freeze.json) precedes
the [held-out visual observations](heldout-observations.jsonl). No rules were edited after
those observations. The three held-out papers are two Articles and one Perspective, not
three interchangeable Article samples.

A08 and F06 show several expected connections between chemically identified structures,
quantitative comparisons and experimental evidence. F06 also shows why different time scales
may be necessary. F07's Perspective contains qualitative ratings and repeated parity panels,
which limit any claim that every panel must have a different evidence role. No selected
held-out image directly tests the energy-profile rule JF04.

All reviewed-image hashes were checked against local source bytes. There is no overlap of
normalized author-name strings between development and held-out papers, but no research-group
isolation or identity-resolved author analysis was attempted. This is a small qualitative
transfer check, not a numerical generalization estimate.

## Independent forward test

Two independent agent contexts received the same [request](forward-inputs/request.md) and
raw synthetic CSV/SMILES inputs. One read `jacs-figure` and its relevant references; the
other was barred from reading repository skills, scripts, examples or other outputs.
Both produced three actual figures and inspected their own work. The skill agent chose
custom plotting plus the supplied validation/QA helpers, which is a supported use of the skill.

A third context received only anonymized PNG/SVG/PDF artifacts, captions and original inputs.
It opened images, rendered PDFs at a common physical scale, checked SVG coordinates against
the data and recorded hashes. It did not receive the workflow mapping or proposed conclusions.
No human or independent-model expert rating is claimed.

| Task | Blind result | Interpretation |
|---|---|---|
| Predicted activation free energies and residuals | Without skill preferred | Horizontal IDs, paired connectors and larger main labels improved reading |
| Sequential stage accounting | Without skill preferred, moderate confidence | A compact single-column plot retained necessary information; both denominator treatments were correct |
| Atom-mapped opposite stereoisomers | Tie | Both preserved identity and configuration; compactness versus extractable labels/notes was a tradeoff |

Both workflows preserved 16 prediction records for 8 reactions, all 12 stage counts, stage
denominators 199/150/110/90 and the final 65/199 fraction, plus both mapped stereochemical
identities. Neither invented significance, uncertainty or 3D geometry. The judge found no
confirmed numerical or chemical error in either set.

See the unabridged [blind assessment](blind-review.md), [structured evidence](blind-review.json),
[identity mapping](forward-output/blind-mapping.json) and [original output/program snapshots](forward-output/README.md).
Code and original audit reports were outside the blind package, so the judge correctly left
those completeness checks unverified. They are provided separately for reproducibility.

## Feedback incorporated, without rewriting the experiment

The entrypoint and chemistry guide now ask for a content-appropriate column width, readable
horizontal identifiers where useful, and captions that avoid repeated in-figure prose.
They recognize both stage-length and full-cohort accounting displays. These are implementation
preferences prompted by the observed readability differences, not new journal requirements
or additions to the frozen corpus rules.

The original artworks, hashes and blind verdicts remain unchanged. No second blind experiment
was run after these small guidance edits; their effect on future outputs remains unmeasured.
Do not turn this pilot into a win-rate claim, a submission-readiness guarantee, or evidence
that a validated JSON schema can replace scientific and visual judgment.
