# Labels, typography, layout and scale

The corpus shows several valid conventions. The choices below are project defaults,
combining observed practice with the [Data adaptations](data-design-patterns.md), not
additional journal rules. Read [graphics policy](../../jacs-shared/references/graphics-policy.md)
for ACS limits. The [study](../../jacs-shared/references/figure-study-v3.md) records source
examples and the six-PDF measurement limitations.

## Axis and legend language / 专业表达

Name the quantity first and attach its unit: `Quantity (unit)`. Use sentence case for
ordinary nouns, retain proper method names, mathematical symbols and chemical identifiers.
A variable may be italic; units and descriptive words remain upright. Math text can express
`$\Delta G^{\ddagger}$` and `$k_{\mathrm{obs}}$` without changing numerical meaning.

| Incomplete/ambiguous | Prefer, when true | Needed context |
|---|---|---|
| True / Pred | Reference ΔG‡ (kcal mol⁻¹) / Predicted ΔG‡ (kcal mol⁻¹) | Define reference method and held-out population |
| Error | Prediction − reference (kcal mol⁻¹) | Signed residual; absolute error needs a different label |
| Accuracy | MAE (kcal mol⁻¹), RMSE (eV), or Success rate (%) | Choose the actual metric and denominator |
| Energy | Relative Gibbs energy (kcal mol⁻¹) | E, H and G are not interchangeable; reference and conditions in caption |
| Time | Time (ps), Time (min) | Same units across comparable panels |
| Frequency | Wavenumber (cm⁻¹) for a vibrational spectrum | Frequency and wavenumber are different quantities |
| Signal (a.u.) | Absorbance; Normalized intensity; or Intensity (a.u.) | Do not label calibrated or dimensionless data a.u. by habit |
| Voltage | Potential (V vs RHE) | State the actual reference electrode; do not invent it |
| Current | Current density (mA cm⁻²) | Identify geometric/electrochemical area or other normalization |
| Ratio | Fraction folded; Yield (%); Enantiomeric excess (%) | A fraction and a percentage have different numeric scales |
| Sample | Number of reactions; Training set size | Count unit and independent sampling unit |
| Model1 / Ours | Exact method/version name | Avoid promotional claims as legend labels |
| Theory / Exp. | Calculated / Experimental, or named computational/measurement method | Explain methods in caption; don't expand every legend into prose |
| Error band | Mean ± SD; 95% confidence interval; prediction interval | Only if this is what was actually computed |

Avoid slash chains such as `kcal/mol/atom`; prefer `kcal mol⁻¹ atom⁻¹`. Do not perform an
implicit unit conversion while editing labels. Write a dimensionless quantity without an
invented unit. Explain normalization reference, baseline subtraction, offsets, binning and
sample n in the caption. Keep significant digits consistent with resolution; `0.20, 0.40,
0.60` need not become six-digit ticks. Use a visible ×10ⁿ multiplier rather than cryptic
repeated long numbers, and disclose any additive offset.

A legend explains **encodings**. Use short parallel noun phrases, same capitalization and
condition precision, and consistent order across figures. Include parameter units once in
a legend title when appropriate. The key must match the real point shape, open/filled state,
line pattern or patch. Reference lines and interval bands deserve a definition, but not
every guide needs a legend entry. Do not recolor a chemical element to match a category.

## Points, lines and visual hierarchy

Start with pale fills, stronger outlines, charcoal labels and white background. Place bands
behind lines, thin neutral guides behind data, and selected factual callouts last. Use
sparse horizontal grids only where they help comparisons. Do not add point jitter along
the measured coordinate, spline unsupported trends, trim inconvenient tails, or average
away failures. Dense scatter may use smaller/rasterized points, hexbin or facets with an
explicit count/density key; source rows and exclusions remain traceable.
Count distinct visible locations as well as records: equal values can hide one another.
For paired categories, a small stable offset per ID may separate ties while preserving the
pairing; never jitter either measured coordinate of a parity plot. Inspect which series is
drawn last. Open symbols cannot by themselves solve severe overplotting; facets may be clearer.

Direct-label a few separated lines near their ends, adding a small leader only if needed.
Use a compact legend above or in empty plot space when direct labels collide. Don't cover
points, place a legend outside the final canvas, repeat category names unnecessarily, or
force a two-column legend that disrupts reading order. Check the final rendered legend,
not just the source code.

At final size, compare an error bar's visible length with the marker diameter. A large mean
symbol can conceal a small SD bar even when all coordinates and font sizes pass checks.
Use a smaller mean marker, a taller panel or a clearer interval encoding when dispersion is
part of the claim; never enlarge the numerical interval for visibility.
Use a lighter area fill than the outlines or overlaid observations. Half densities with
separate raw points and outline histograms are useful when filled regions obscure the data.

## Typography at the final physical size

The reviewed sources include serif and sans-serif, thin and heavy axes, upper- and lowercase
panel letters. Six inspected PDF examples store plot lettering in image objects: their
font family and point size are **not recoverable as PDF text**. Caption font metrics do not
measure plot typography. Never claim that JACS universally uses Arial 8 pt.

| Element | Starting project value | Adjustment |
|---|---|---|
| Axis titles / body labels | 8–9 pt | Enlarge for fewer panels and presentation outputs |
| Tick labels / legend | 7–8 pt | Shorten, wrap or widen before shrinking |
| Panel letters | 9–10 pt, semibold/bold | Same placement and baseline across the composition |
| Sparse annotations | 7–8 pt | Move long methods to caption |
| Axes / major ticks | 0.6–0.8 pt | Keep visible after reduction |
| Data lines | 0.9–1.3 pt | Use dash/marker differences before excessive width |
| Point diameter | ~3–5 pt | Smaller for dense data, larger for sparse measurements |
| Error bars / outlines | 0.6–0.9 pt | Preserve caps and visible boundaries |

These are starting values, not source-measured journal averages. ACS's minimum lettering
is a technical floor, not the recommended target. Scale the **whole final composite** and
inspect the resulting type; a 9 pt source panel reduced to 55% has 4.95 pt lettering.
PDF/SVG export at a large pixel size does not fix physically tiny fonts. Use available
sans-serif fonts consistently; never silently mix fonts because one lacks a glyph.

## Single-panel scale

Choose domain, aspect ratio, tick spacing and mark density together. Parity needs equal
x/y limits **and equal data aspect**; a square frame alone does not establish equality.
Use roughly 4–6 readable major ticks as a starting point, not a fixed constraint. Numeric
and time ticks should normally be horizontal. Use 2:1-ish wide panels for long trajectories,
near-square domains for pairwise relationships, and extra height for long category lists.
For sparse learning curves, label enough of the actual training sizes to identify settings
on the log axis. For a small heatmap, size the cells and colorbar for its few values; a compact
rectangular matrix may work better than large square tiles. Fewer colorbar labels can suffice
when cells already show exact values. Keep the full quantitative range and explicit missing key.

Bars that encode magnitude start at zero. Scatter, spectra and interval plots may use a
focused range with clear ticks; do not hide outliers. Log scale is suitable for multiplicative
variation across orders of magnitude, never for silently dropping zero/negative values.
Different log transforms, standardization and per-atom normalization must be declared.
Reversed NMR/XPS axes are legitimate conventions. A second axis is safest for an explicit
physical conversion of the same variable; use separate panels for unrelated quantities.
Prefer an inset or clearly separated zoom over a broken bar axis.

The bundled curve helper requires increasing x in each supplied series and rejects
reordering. Cyclic voltammograms, missing segments, special projections and fitted models
need a custom plot using the same design rules. Never distort the data to fit a helper.

## Multi-panel layout

Use a grid for equal comparison tasks: same axes dimensions, ranges where appropriate,
category order, hue mapping and precision. For a mechanism narrative, allocate more area
to the decisive evidence; a wide overview above two/three smaller analyses often works.
Align plot rectangles, not just PNG outer edges. Reserve gutters for labels and colorbars;
start with ~12–18 pt horizontal and ~16–24 pt vertical spacing, then inspect real text.
First establish the shared question and each panel's population or derivation. Allocate space
by reading task, not the desire to demonstrate many chart types. When composing existing SVGs,
their outer boxes do not expose internal axes; use joint native layout or an explicitly designed
composition when plot edges need alignment. Panel captions must follow the panels into the export.

Panel letters follow reading order, usually left-to-right/top-to-bottom; the sample does
not justify a mandatory letter case. A shared legend or colorbar is useful only when its
mapping is genuinely shared. A microscopy scale bar must retain its physical value after
resizing. Do not stretch a molecule, image or data plot to fill a uniform cell.

Prefer one clear message per panel and remove redundant furniture. Simplicity is useful;
plainness is improved by better evidence composition and hierarchy, not decorative gradients,
colored card backgrounds or adding chart types without a scientific reason.
