# Figure-style distillation

## Sources and split

Start from [figure provenance](../../jacs-shared/references/figure-corpus.jsonl) or a task-local
paper registry. Record DOI, article type, authors, year, version, license and availability.
Freeze paper-level development/holdout groups before deriving rules. All panels, SI, TOC and
versions of a DOI stay together. Track author-group overlap; paper-level separation does not
guarantee independent author practices. Keep Article and Communication strata distinguishable.

The [PMC helper](../scripts/figure_corpus.py) uses the current public PMC Article Dataset:

```text
python <skill-dir>/scripts/figure_corpus.py discover --pmcid PMC9951208
python <skill-dir>/scripts/figure_corpus.py fetch --pmcid PMC9951208 --version 1 --doi 10.1021/jacs.2c12871 --paper-id B06 --split development --output-dir local/B06
```

Inspect version metadata; a higher version is not automatically the publisher version.
The helper verifies DOI/journal identity and metadata-provided MD5 digests, records SHA-256,
and downloads image files referenced by JATS. Downloaded does not mean visually reviewed.
Some author manuscripts expose text but no media in this service. Record unavailable assets;
use legitimate author/publisher/open-repository alternatives or supplied PDFs without inventing
access. The legacy OA locator service was retired in August 2026.

Source documentation: [PMC dataset access](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/),
[current bucket specification](https://pmc-oa-opendata.s3.amazonaws.com/README.txt).
The NLM PMC Article Datasets are the source of the bundled registry's PMC metadata; this
project is not endorsed by NLM, NIH or ACS. Preserve each article's actual reuse terms.

## Inspect and annotate

Open the actual figure or its PDF page. Read the caption for scientific meaning, but derive
layout/color observations only from the image. Record whole-figure and selected-panel scope.
Use [the annotation file](../../jacs-shared/references/figure-annotations.jsonl) as the schema:
source hash and locator, chart family, panel roles, observation, semantic features, caveat,
article type, split and review method. Label agent visual inspection accurately; do not claim
human verification. Keep physical font size unknown when final publication scaling is unknown.

A workflow diagram, a schematic energy profile and a measured trajectory have different
semantics. Mark direct visual facts separately from a scientific interpretation. Record
counterexamples and uncertainty instead of extracting a single universal aesthetic.

## Derive and test

Produce conditional rule cards with annotation IDs and unique supporting paper IDs. Check
whether apparent prevalence comes from one author group or many panels of the same paper.
Evaluate frozen rules on held-out papers and fresh drawing tasks; once a holdout is used to
change rules it becomes development evidence for that iteration. Preserve the original result.

Deliver a source manifest, original annotations, scoped rules and a coverage/limitations
report. Keep raw copyrighted figures and captions in the local acquisition area. Only share
assets whose distribution terms have been checked, or original synthetic demonstrations.
