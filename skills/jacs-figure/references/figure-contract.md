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
| `kind` | `energy`, `parity`, `stages`, `comparison`, `workflow`, `structures`, `distribution`, `interval`, `curve`, `heatmap`, `panel_grid`, `assembly` |
| `data_status` | `real` or `synthetic`; synthetic output carries a visible label |
| `claim`, `caption` | Author-supplied bounded claim and caption; no automatically invented conclusion |
| `caption_mode` | `compose` (default) appends facts; `authored` exports supplied prose and a separate facts file. Neither validates scientific prose. |
| `quantity_definition`, `normalization` | Optional supplied definitions carried into the delivered caption; define signed differences and transformation references here |
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
| `assembly` | `panels`, optional `columns` | Each panel: `label`, `svg`, and `caption` or `caption_file`; paths relative to the spec |
| `panel_grid` | `panels`, `population`, optional `columns` (default 2) | Each panel: `label`, `title`, `role`, and inline child `spec` |
| `distribution` | `metric`, `unit`, `population`, `unit_of_analysis`; `display`: box/violin/ecdf/histogram | `observation_id`, `group`, `value` |
| `interval` | `metric`, `unit`, `population`, `interval_definition`; optional `reference_value` | `label`, `estimate`, `lower`, `upper` |
| `curve` | `x_quantity`, `x_unit`, `y_quantity`, `y_unit`, `population` | `series`, `x`, `y`; optional `lower`, `upper` |
| `heatmap` | `quantity`, `unit`, `population`, `row_order`, `column_order` | `row`, `column`, `value` (JSON null means explicitly unavailable) |

### Statistical display choices

Distribution groups need not share observation IDs or sample size. Define the independent
unit correctly; grouped distributions do not imply a paired test. `group_order` can explicitly
order every observed group. At most six groups/curve series use the bundled palette; beyond
that, facet or write an explicit encoding. Category jitter is deterministic and changes only
the category coordinate. No outliers are removed.
`point_layout: swarm` packs points after final layout, moves only the category coordinate,
and records remaining spacing conflicts. It does not promise a readable display at arbitrary n.

- `box`: Q1–Q3, median, whiskers at observed points inside 1.5 IQR fences; all raw observations
  remain visible, including outliers. Quantiles use NumPy's linear method.
- `violin`: supply a positive `bandwidth` (Gaussian KDE factor, e.g. 0.35). Equal maximum
  widths do not encode sample size or equal density area. KDE is computed in raw units; a
  log-transformed density needs a separate explicit analysis. Groups with fewer than five
  observations or zero spread show raw points and a median without a density silhouette.
  Half densities and raw observations occupy separate sides. QA records local-mode counts
  at the stated and doubled bandwidth on a 150-point grid; sensitivity is not a test of
  whether subpopulations exist. Do not tune the bandwidth to manufacture a preferred shape.
  `show_bandwidth_sensitivity: true` overlays a dashed density at twice the bandwidth;
  both densities use their own equal maximum-width normalization.
- `ecdf`: empirical cumulative fractions, steps without smoothing; includes all observations
  and extends tails to a common domain. Use signed values for bias/distribution questions;
  use `value_transform: absolute` for absolute-error threshold coverage. This explicit option
  transforms displayed values and summaries, preserves raw input, and is disclosed in the caption.
- `histogram`: supply `bin_edges`, shared by all groups and covering every observation.
  Heights are counts; normalization to density is not implicit. NumPy closes the last bin
  on the right. A count histogram with unequal bins is not a density comparison. The default
  draws outlines to avoid mixed fill colors. Bins cover displayed values after any explicit transform.
  `facet_groups: true` instead uses one row per group with common bins and axes; allocate
  adequate height. This option is standalone and cannot be nested in the single-axis panel grid.

`interval` draws supplied bounds without calling them confidence intervals. Set
`interval_definition` to SD, SE, confidence/credible interval with level and method, or an
accurate noninferential description. The estimate must lie within its bounds. A reference
line is optional, not automatically interpreted as a null hypothesis.
Use `estimate_definition` to record what the point estimates; the renderer does not infer
it from bounds. The gallery's mean ± SD example retains its underlying synthetic values.

`curve` requires strictly increasing x within each series. Sort explicitly upstream if needed
and preserve the original input. `series_roles` maps names to `observed` (points, default),
`model` (lines) or `reference` (neutral dashed line). `connect_observations: true` adds visual
guides, not a fitted law. Bands need bounds for every point of that series and a common
`interval_definition`. Different uncertainty meanings require separate figures/custom code.
`x_scale`/`y_scale` accept linear/log; log data and bounds must be positive. `reverse_x`
supports conventional spectral axes. `zero_reference` requires a linear y axis.
`x_ticks` supplies meaningful numerical settings without replacing the true x coordinates;
ticks must increase and be positive on a log axis. A y label containing normalized/normalised
requires `normalization`; other languages and implicit transformations still need author review.
The renderer records the convention but does not perform curve normalization. The spectral
example explicitly divides each series by its sampled maximum and retains `raw_y`.

`heatmap` requires every cell, including explicit nulls; omission is not silently interpreted
as zero or missing. For missing CSV cells, prepare an explicit JSON null mapping upstream
(empty strings are rejected). `color_scale` is sequential by default; diverging also needs a
meaningful `center`. `vmin`/`vmax` must span and cover observed values. No silent clipping,
imputation, row normalization or interpolation occurs. Hatched neutral cells with `NA` denote
unavailable values, even if ordinary numeric annotation is disabled; observed zero is printed
as 0. Optional `missing_label` changes the label, not its meaning. The colorbar includes quantity
and unit, with four ticks by default (a diverging map includes its center). `colorbar_ticks`
must increase within the limits. Use `column_definitions` to explain domain/split labels and n
when known; do not invent missing reasons or sample counts. A small matrix need not have square cells.
`column_label` names the column axis; `value_format` controls cell precision (default `.2g`,
e.g. `.2f` for consistent decimal places). Retained n, IDs and raw errors support upstream
recalculation; the renderer itself draws supplied summaries without recomputing them.

The unit string `dimensionless` omits an unnecessary parenthesis. Common display aliases
such as `kcal/mol` → `kcal mol⁻¹` change typography only; numerical units never change.

`conditions` can be a structured object identifying theory, temperature, solvent and standard
state. A stated unknown is preferable to an invented method. Numeric IDs are normalized to
strings without changing existing string IDs or leading zeros.

Method comparisons require one record per reaction per method and the same reaction set.
Replicate-level or unpaired data need a separately declared analysis and suitable plot; do not
mislabel replicates as independent reactions just to use this template. Parity MAE/RMSE are
recorded for the actual plotted records (also appended in compose mode). `facet_methods: true`
separates parity methods into columns with common domains and a residual row. Allocate height
and width for the number of methods; this option does not guarantee readability for many columns.
The comparison template shows observations, paired lines and medians, with no inferred error bars.
One deterministic horizontal offset per reaction follows it across methods; measured values do
not move. Coincident y values can still crowd at large n, so inspect or use a different layout.

Stage counts satisfy `passed + failed + pending = entered`; entered is the initial population
or the preceding stage's passed count. A later stage with no entrants has an undefined
conditional rate, not zero. The neutral not-entered segment includes upstream failures and
pending cases, excluded from the conditional denominator. Record `observation_window` when
pending work makes the snapshot relevant. Branching workflows require separate cohorts.

PNG is a 300 dpi preview. Declare the TIFF content class; exporting a low-resolution source
at a higher DPI does not restore its detail. Embedded raster panels require a separate source
resolution check at their final displayed size.

SVG assembly preserves aspect ratio and rejects external resources or active content.
Embedded base64 PNG/JPEG images are supported; this does not make the PDF entirely vector. It
does not recognize chemistry or make embedded tiny labels readable. Inspect scaled panels
in the exported PDF and enlarge/restructure when necessary. Structure SMILES are parsed and
canonical isomeric identities are recorded; original SMILES remain in the saved spec.
Structure examples may add `title`, a short multiline `note`, and left-to-right `edges` between
neighboring nodes in one row. A node's optional `bond_highlights` contains zero-based atom-index
pairs; each must be an actual bond in that supplied molecule. Highlights need an authored meaning.
`proposed_bonds` instead draws specified single edges as dashed blue links in a supplied
candidate graph; this is an editing convention, not a TS geometry or computed bond order.
`separate_fragments: true` adds plus signs between disconnected SMILES components and cannot
be combined with atom-index highlights. TOC notes use 8 pt lettering; check space after wrapping.
Energy `state_labels` can map stable state IDs to display labels such as `TS$_A$`.
`level_label_layout: inline` places the state and energy on one line when neighboring
levels would overlap a stacked label. Inspect label-versus-level collisions after export.
Workflow nodes can set `emphasis: true`; other nodes remain neutral. Default row traversal is
serpentine, with `reading_order: row_major` available for an explicitly authored layout.

### Composites and delivered captions

Use `panel_grid` for compatible quantitative panels that benefit from laying out native axes
together. Supported children: energy, comparison, distribution, interval, curve, heatmap. The
outer canvas controls geometry; child physical-size hints are not separately imposed. Labels,
roles, child definitions and computed statistics enter the caption in compose mode. Population
text describes the connection; it does not automatically prove that IDs or study cohorts match.
Custom code or SVG composition remains appropriate for unequal panel areas and chemical schemes.

SVG `assembly` now requires each panel's caption text or an explicitly supplied caption file.
Caption files are read with source hashes and embedded in the rerunnable specification, so the
bundle does not depend on their original location. This is a migration requirement for older
assembly inputs; a generic overall caption cannot explain unknown embedded marks.

The saved `caption` remains author prose. With `caption_mode: compose` (the compatibility
default), `.caption.txt` combines it with known definitions and panel facts. With `authored`,
the supplied prose is exported without metadata appendices; synthetic status still survives.
Both modes write `.caption-facts.json`, including child definitions and computed statistics.
Rerendering does not duplicate facts. The composer does not validate prose or infer missing
definitions: review caption, facts and source together before delivery.

## Original examples

- [Energy](../assets/examples/energy.json)
- [Parity and residuals](../assets/examples/parity.json)
- [Stage accounting](../assets/examples/stages.json)
- [Paired comparison](../assets/examples/comparison.json)
- [Workflow](../assets/examples/workflow.json)
- [Stereochemical structures](../assets/examples/structures.json)
- [TOC concept](../assets/examples/toc.json)
- [Box and raw observations](../assets/examples/boxplot.json), [violin](../assets/examples/violin.json),
  [ECDF](../assets/examples/ecdf.json), [histogram](../assets/examples/histogram.json)
- [Point and interval](../assets/examples/intervals.json), [learning curve and SD band](../assets/examples/learning.json)
- [Spectra](../assets/examples/spectra.json), [reference-stratified MAE matrix](../assets/examples/heatmap.json)
- [Larger parity/residual example](../assets/examples/agreement.json)
- [Shared-cohort signed-error and absolute-error panels](../assets/examples/showcase.json)

All are demonstrations, not HERMES results. The output contains PDF, editable-text SVG where
the backend supports it, PNG, a normalized rerunnable JSON spec, caption text, source hashes
and QA JSON. Supplied SVG assets are copied beside the saved spec for reproducibility. The
repository source and lockfile provide the renderer and environment; record the commit when
sharing a bundle. A PDF containing images is not necessarily an entirely vector figure.
