# Figure contract and bundled specifications

## Minimal contract

Use only fields relevant to the current request:

- Scientific question and claim supported by the supplied evidence.
- Panel roles: setup, decisive comparison, chemical explanation, validation, boundary.
- Data source, reaction/candidate IDs, selection rule and population.
- Quantity, unit, reference state, conditions; statistic and uncertainty where applicable.
- Output role: main Figure, Scheme, SI or TOC; physical size and backend.

Record unknown conditions as unknown. Resolve an ambiguity before it changes the data or
claim; continue layout work that does not depend on it. Aesthetic preferences need not become
a long intake questionnaire. Use the fewest panels that preserve the evidence chain.

## Bundled specifications

Run `python <skill-dir>/scripts/plot_figures.py spec.json --output output/figure`.
The output argument is a prefix without an extension. Existing output requires `--overwrite`.
The input JSON is never modified. Dependencies: Matplotlib, NumPy, Pillow, pypdf; SVG assembly
also uses CairoSVG and defusedxml; drawing SMILES also uses RDKit.

Common fields:

| Field | Meaning |
|---|---|
| `kind` | `energy`, `parity`, `stages`, `comparison`, `workflow`, `structures`, `assembly` |
| `data_status` | `real` or `synthetic`; synthetic output carries a visible label |
| `claim`, `caption` | Author-supplied bounded claim and caption; no automatically invented conclusion |
| `profile` | `single`, `double`, `si`, `toc`; defaults live in `figure_spec.py` |
| `width_pt`, `height_pt` | Physical dimensions in points; 72 points = 1 inch |
| `data` or `input_csv` | Inline records or a CSV path relative to the spec; never both |
| `colors` | Optional mapping from exact method/path display name to color |
| `scale` | Linear by default; supported log plots reject nonpositive values |
| `tiff` | Request an additional raster export; TOC produces TIFF automatically |
| `raster_class` | TIFF resolution: `color` 300, `grayscale` 600, `line_art` 1200 dpi; conservative default `line_art` |

Scalar metadata in a CSV row must agree with the common specification. Unit or reference
conversion is an explicit upstream operation; the renderer does not infer one. Missing or
non-finite measurements stop the template. The helper does not compute hypothesis tests.

| Kind | Required top-level metadata | Required records |
|---|---|---|
| `energy` | `quantity`: E/H/G, `unit`, `reference`, `conditions` | `path`, `state`, `order`, `energy` |
| `parity` | `quantity`, `unit`, `reference`, `conditions` | `reaction_id`, `method`, `reference_value`, `predicted` |
| `comparison` | `metric`, `unit`, `population` | `reaction_id`, `method`, `value` |
| `stages` | `population`, `population_total`, `unit_of_analysis` | `stage`, `passed`, `failed`, `pending` |
| `workflow` | Optional `edges` and `columns` | `id`, `label` |
| `structures` | Optional `columns` | `id`, `label`, exactly one `smiles` or `svg`; external SVG also needs `source` |
| `assembly` | `panels`, optional `columns` | Each panel: `label`, `svg`; paths relative to the spec |

`conditions` can be a structured object identifying theory, temperature, solvent and standard
state. A stated unknown is preferable to an invented method. Numeric IDs are normalized to
strings without changing existing string IDs or leading zeros.

Method comparisons require one record per reaction per method and the same reaction set.
Replicate-level or unpaired data need a separately declared analysis and suitable plot; do not
mislabel replicates as independent reactions just to use this template. Parity MAE/RMSE are
recorded for the actual plotted records. The comparison template shows observations, paired
lines and medians, with no inferred error bars.

Stage counts satisfy `passed + failed + pending = entered`; entered is the initial population
or the preceding stage's passed count. A later stage with no entrants has an undefined
conditional rate, not zero. Earlier attrition remains visible and is excluded from the next
conditional denominator. Branching workflows require separate cohorts; this template is a
single sequential cohort.

PNG is a 300 dpi preview. Declare the TIFF content class; exporting a low-resolution source
at a higher DPI does not restore its detail. Embedded raster panels require a separate source
resolution check at their final displayed size.

SVG assembly preserves aspect ratio and rejects external resources or active content.
Embedded base64 PNG/JPEG images are supported; this does not make the PDF entirely vector. It
does not recognize chemistry or make embedded tiny labels readable. Inspect scaled panels
in the exported PDF and enlarge/restructure when necessary. Structure SMILES are parsed and
canonical isomeric identities are recorded; original SMILES remain in the saved spec.

## Original examples

- [Energy](../assets/examples/energy.json)
- [Parity and residuals](../assets/examples/parity.json)
- [Stage accounting](../assets/examples/stages.json)
- [Paired comparison](../assets/examples/comparison.json)
- [Workflow](../assets/examples/workflow.json)
- [Stereochemical structures](../assets/examples/structures.json)
- [TOC concept](../assets/examples/toc.json)

All are demonstrations, not HERMES results. The output contains PDF, editable-text SVG where
the backend supports it, PNG, a normalized rerunnable JSON spec, caption text, source hashes
and QA JSON. Supplied SVG assets are copied beside the saved spec for reproducibility. The
repository source and lockfile provide the renderer and environment; record the commit when
sharing a bundle. A PDF containing images is not necessarily an entirely vector figure.
