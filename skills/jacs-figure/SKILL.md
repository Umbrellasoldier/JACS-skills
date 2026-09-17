---
name: jacs-figure
description: Design, create, revise, and audit JACS data figures, chemical schemes, method illustrations, TOC and cover artwork. Use for JACS 科研绘图、数据图、方法示意图、TOC、封面和 imagegen 绘图选择; use jacs-polishing for caption-only prose edits.
---

# JACS scientific figures

Create a reproducible figure that answers the author's scientific question and preserves the
meaning of the supplied data. The visual study spans 50 selected JACS papers in modeling, catalysis, spectroscopy,
materials and biological chemistry; its observations are conditional, not a whole-journal style.

## Route the request

- **Plan:** identify the question, necessary evidence and panel roles. Missing measurements
  can remain explicit gaps; plotting dependencies are unnecessary for a plan.
- **Create or restructure:** read [figure contract](references/figure-contract.md) and the
  relevant part of [chemistry figures](references/chemistry-figures.md).
- **Revise:** preserve the existing data mapping, backend and unaffected design. A color or
  label change does not authorize changing scientific content or rebuilding the whole figure.
- **Illustration, cover or imagegen choice:** read [image-generation routing and composition](references/imagegen-workflow.md).
  Choose by the output's role and what each visual element asserts. ACS TOC graphics use no
  AI-generated images under the current [policy snapshot](../jacs-shared/references/graphics-policy.md#ai-generated-artwork).
  A request for a recommendation or plan does not itself request image generation.
- **Audit or export:** read [QA](references/qa.md) and the applicable
  [graphics policy](../jacs-shared/references/graphics-policy.md).
- **Submission readiness:** also read [submission review](references/submission-readiness.md)
  to distinguish export quality, scientific meaning and completeness of the submission package.
- **Derive style from papers:** use the figure route in
  [jacs-style-distill](../jacs-style-distill/SKILL.md); captions alone do not establish visual style.

For a new quantitative rendering task use Python unless the user or supplied workflow establishes
another backend. Respect an existing R or chemistry drawing workflow. Use editable vector tools
for simple diagrams and chemical drawings; use available image-generation tools for suitable
nonquantitative illustrations. Read-only review needs no backend choice. The bundled Python
templates are optional tools, not the entire skill.

## Scientific meaning before styling

Record the claim, source data, panel roles, quantities/units, population and target format.
For a composite, state how the panels' populations or derivations connect to the same
question. A gallery of unrelated chart types is not a research narrative. Prefer fewer
panels when another chart adds no necessary evidence.
Read [chemistry semantics](../jacs-shared/references/chemistry-semantics.md) when energies,
transition states, pathways or model comparisons are involved. Keep generated candidates,
frequency characterization, IRC and endpoint validation distinct. Preserve reaction IDs,
atom mapping, stereochemistry, charge and the actual uncertainty definition.

Use all relevant supplied observations by default. Document justified exclusions and any
aggregation; never silently drop failures, outliers, nonpositive values or incomplete pairs
to fit a template. Production figures require real supplied values. Example data remain
explicitly marked synthetic in both the image and provenance.

## Design and render

Choose the analytical relationship using [chart selection](references/chart-catalog.md).
Read [labels, layout and scale](references/labels-layout-scale.md) for axes, legends,
typography and composition, and [color design](references/color-design.md) for the light
fill/strong-outline palette. [Visual evidence](references/visual-rules.md) explains provenance.
Select complementary panels for a shared question; equal-size comparisons and unequal-size
explanatory panels are both valid. Reuse semantic colors across the manuscript and redundant
markers/labels where helpful. Do not infer an official palette or panel-letter convention.
Choose fill area, mark density and emphasis together: pale colors do not make a crowded
plot readable. Check coincident observations and drawing order, not just record counts.

Choose the narrowest column format that keeps the actual content readable. For a small
structure pair or short stage sequence, inspect a single-column design before allocating
double-column width. Keep IDs horizontal when possible; transpose a categorical residual
plot if that makes paired observations easier to compare. Move repeated explanatory prose
to the caption when the figure remains self-contained.

The bundled [renderer](scripts/plot_figures.py) accepts JSON specifications and optional CSV
data. [Examples and schema](references/figure-contract.md#bundled-specifications) describe the
ten plot families, a native quantitative panel grid and SVG assembly. Do not force unsupported data into a helper. Resolve scripts and assets relative to this SKILL.md. Keep the
input intact. Use an isolated output directory and the task's available environment; the
repository's locked `figures` group supplies plotting dependencies and `chemistry` adds RDKit.

Use chemical drawing software or real structure assets for molecules and TS panels. A 2D
SMILES depiction is not a calculated 3D geometry. Do not infer bond distances from its pixels.
The structure template draws SMILES or assembles supplied SVG; obtain a real geometry renderer
for XYZ/SDF-based 3D views. Generated artwork must not substitute for measured/calculated data.
In a mixed illustration, keep data marks, structures, labels and process arrows in source-backed
layers. Generated raster assets may supply a conceptual visual where appropriate; adding vector
labels or tracing an image does not remove its AI origin. A pale palette alone does not justify
generating a new image. Improve scientific specificity and visual hierarchy first.

## Verify and deliver

Inspect the actual final PDF/SVG and a final-size preview after rendering. Review grayscale
and color-vision simulations when categorical colors carry information; redundant shapes
and line patterns matter because light hues can merge. Verify the actual uncertainty
definition, numeric scale, binning/normalization and explicit missing-value treatment. Run applicable
data, dimension, text and layout checks; repair deterministic failures and inspect warnings.
The bundled auditor explicitly leaves chemical correctness, many graphic collisions and
unsupported objects to visual review. `MECHANICAL_PASS` is not complete scientific approval.
Never report `UNKNOWN` as passed or reuse a QA report after changing its figure.
Read the delivered figure together with its delivered caption. Readers must be able to
identify the statistic, sample unit/n, interval meaning, signed difference, normalization,
reference and missing-value encoding where applicable. Metadata alone is insufficient;
carry these facts through assembly and export. Keep publication prose separate from the
reproduction record. The renderer supports an authored caption and a separate facts file;
its compatibility composer appends facts but does not establish publication-ready prose.
Check either mode against the source for omissions and contradictions. Synthetic templates
can demonstrate a usable design; they cannot establish readiness of a research figure.

Deliver requested formats with the specification, plotting source/version, data or source
index, caption facts and concise QA notes. Keep source papers and private project data local.
When generated assets are used, also retain their actual prompts, available tool/model metadata,
original outputs, final placements and applicable disclosure. Inspect the exported composite;
the PDF auditor cannot verify raster content or establish publication-policy compliance.
For prose-only captions use [jacs-polishing](../jacs-polishing/SKILL.md); when drafting Results
use [jacs-writing](../jacs-writing/SKILL.md) with the verified figure facts. Do not upgrade the
claim beyond the evidence. Apply submission-specific checks only to the requested deliverable.
