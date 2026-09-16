# Corpus workflow

1. Validate title, journal, DOI, article type, and source version. Use publisher and metadata
   registries as appropriate. A single registry failure is unresolved evidence, not proof
   that a DOI is invented. The helper's `verify` command reports Crossref comparison status;
   it does not substitute for content verification or a full novelty search.
2. Freeze DOI-level development/holdout assignments. Check author overlap as a diagnostic;
   author-name spelling differences mean this cannot prove institutional independence.
3. Acquire public text or import user-supplied material. Record source URL, retrieval time,
   source digest, access/license statement, and published/author-manuscript/unknown version.
4. Inspect headings, prose order, formulas, and captions. BioC section labels can be wrong:
   the pilot C03 labels several substantive sections INTRO. Use an explicit reviewed heading
   map instead of changing source text or pretending all those paragraphs are introductions.
5. Normalize paragraphs with stable source locators. Preserve original headings and source
   offsets; do not invent PDF page numbers for XML or BioC. Keep title, abstract, body,
   captions, tables, methods, and back matter distinct.
6. Derive observations from development papers only. Review selected paragraph functions and
   keep counterexamples. Quantitative summaries use explicit filters; do not pool references,
   SI, synthetic examples, or holdout prose into prose-style statistics.
7. Evaluate before publishing. Check rule references, scope, scientific fidelity, and behavior
   on fixed tasks. Report what was actually assessed, including the limits of a small pilot.

## CLI examples

Run from any directory; replace the paths with real ones. These commands write only specified
local outputs and do not publish, install, or send messages.

```bash
python /path/to/jacs-style-distill/scripts/corpus.py fetch --manifest manifest.jsonl --paper-id C03 --output-dir local/C03
python /path/to/jacs-style-distill/scripts/corpus.py ingest --manifest manifest.jsonl --paper-id C03 --input local/C03/source.json --format bioc --source-url https://example.org/source --output local/C03/blocks.jsonl
python /path/to/jacs-style-distill/scripts/corpus.py stats --manifest manifest.jsonl --input local/C03/blocks.jsonl --output local/statistics.json
python /path/to/jacs-style-distill/scripts/corpus.py verify --doi 10.1021/ja3000936 --title 'Reactivity of Biarylazacyclooctynones in Copper-Free Click Chemistry'
```

`fetch` preserves a matching existing download and otherwise refuses to overwrite a conflicting
output. `stats` excludes holdout papers by default and rejects mixed source versions of a DOI.
For PDF text, use `--format blocks` with the fields described in the annotation schema and
`--source-doi` only after checking the original document. A CLI identity assertion is recorded
as user asserted, not misrepresented as a DOI extracted from the source.

API documentation: [PMC BioC](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/),
[Europe PMC](https://europepmc.org/RestfulWebService),
[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).
