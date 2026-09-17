# Figure corpus: coverage and limits

Snapshot: 2026-09-17. This is a chemistry-focused pilot, not a representative survey of JACS.
The [paper registry](figure-corpus.jsonl) records 14 papers, 91 unique available Figure/Scheme
identifiers and 92 available image assets. One Scheme has two assets; assets are not counted
as independent figures. All source images remain local.

| Stratum | Papers | Actually inspected figures | Use |
|---|---:|---:|---|
| Development Article | 9 | 33 | Derive conditional visual observations |
| Communication calibration | 2 | 7 | Describe separately; not pooled as Article evidence |
| Held-out Article | 2 | 6 | Check frozen observations on different papers |
| Held-out Perspective | 1 | 3 | Check scope boundaries, not Article validation |
| Total | 14 | 49 | Agent visual inspection; no human ratings |

Development papers: A07, A10, B06, C03, C10, F01–F04. Communication: C02, F05.
Held out: A08, F06 and F07 (Perspective). The split is by paper/DOI, not by image or panel.
F05 was corrected to Communication from publisher JATS before its observations were promoted.
The figure and prose registries have independent splits; reuse of an identifier does not change
the earlier writing evaluation.

## Evidence chain

1. Discover exact PMCID versions in the current NLM PMC Article Dataset.
2. Check DOI and journal in metadata and JATS; record manuscript status and license code.
3. Download linked Figure/Scheme assets, verify metadata MD5, and record SHA-256.
4. Open the actual complete image, then write an original observation with a locator and
   limits. Captions aid interpretation but cannot establish visual features.
5. Freeze the 40 development/calibration annotations and six rules before opening held-out
   images. Separate held-out notes live in the repository's `evaluation/figures/` directory.

The [annotations](figure-annotations.jsonl) identify source URLs and hashes. The
[rules](figure-rules.jsonl) link each observation to supporting figures, distinct papers and
counterexamples. Frozen rules were not changed after the held-out inspection.

## What the pilot supports

| Rule | Conditional observation | Distinct supporting Article papers |
|---|---|---:|
| JF01 | Organize complementary evidence roles around a shared question | 9 |
| JF02 | Reuse colors for the same chemical entities or methods | 7 |
| JF03 | Align comparable plots/views with scientifically meaningful scales | 5 |
| JF04 | Keep state identities and quantity labels near energy/structure evidence | 3 |
| JF05 | Add markers, line styles, direct labels or hatching where useful | 5 |
| JF06 | Connect numerical results with chemically identified systems | 9 |

Figures differ in palette, saturation, fonts, panel-letter case, backgrounds and panel size.
Some published comparisons use unequal ranges; some rely on color alone. The skill therefore
uses conditional guidance and explicit exceptions. Its bundled palette, 7–8 pt working text
sizes and open axes are project defaults, not inferred journal requirements.

The six renderer families are implementation choices for the intended research workflow.
In particular, sequential generation/optimization/validation accounting follows declared
population semantics; the pilot does not establish a unique JACS success-rate chart style.

## Held-out findings

A08 connects a chemical workflow, descriptor/model comparison and experimental structures;
F06 links reaction schemes to kinetics and crystallographic evidence. Both fit several frozen
rules. F06 also uses different time scales for different experiments, reinforcing the condition
on comparable axes. The Perspective includes a repeated parity matrix and qualitative radar
chart: complementary panel roles and redundant encodings are not universal conventions.

No selected held-out figure directly tests JF04's energy-profile guidance. These nine figures
are a small transfer check, not a quantified generalization score or independent expert review.
Results and original inspection notes are in `evaluation/figures/` in the repository.

## Limits

- Years span 2008–2026; subjects emphasize reaction chemistry, machine learning and molecular
  modeling. The sampling is intentionally relevant to this project and access-biased.
- Source metadata labels these versions as non-manuscript PMC articles. This is recorded
  provenance, not an independent reconstruction of the journal's production process.
- Normalized author-name strings show no development/holdout overlap (60 versus 16 names),
  but this is not ORCID verification or a split by research group, institution or lineage.
- Physical font sizes and stroke widths cannot be recovered reliably from these raster
  assets without verified publication scale. All such annotation fields remain unknown.
- One downloaded F06 kinetic figure appears clipped at its right edge. Its visible features
  are described with that limit; source clipping is not treated as good design.
- Reading a figure does not validate the underlying chemical conclusions. Published
  uncertainty, energy references and structures must still be interpreted in context.

Current submission requirements are a separate layer in [graphics policy](graphics-policy.md).
Open source access does not transfer a paper's copyright to this project. The repository
distributes source locators and original observations, not the original figures.
