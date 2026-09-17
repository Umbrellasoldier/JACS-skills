# Data plugin patterns adapted to scientific figures

Source: the explicitly requested **Data** plugin, `data-analytics` version 1.0.8,
especially `visualize-data/SKILL.md`, `validate-data/SKILL.md` and
`shared/analysis-quality.md`. These are design/workflow adaptations, not observations
about JACS papers and not ACS submission requirements.

| Pattern | Scientific adaptation |
|---|---|
| Choose the analytical relationship first | Ask whether the claim concerns a distribution, agreement, uncertainty, kinetics, a matrix or a mechanism before picking a template. Repeated chart types are useful when tasks are comparable. |
| Establish grain and population | State what each mark represents: reaction, molecule, conformer, run, cell or independent experiment. Separate repeated measurements from independent samples. |
| Preserve numeric structure | Keep time, concentration and measured rank numeric. A log axis requires a scientific reason and positive values; no silent offset or deletion. |
| Make comparisons visually fair | Share units, order, limits and encodings for comparable small multiples. Disclose independently scaled panels; different physical quantities need not share limits. |
| Let geometry carry meaning | Histogram bins touch; unrelated categories have gaps. Bars that encode magnitude start at zero. Scatter marker area encodes a third quantity only when that mapping is necessary and explained. |
| Control density without hiding data | Use outlines, open symbols, modest opacity, density bins or facets. Disclose binning and smoothing. Preserve outliers and report how many observations are shown. |
| Use stable semantic color | A method keeps its color across panels. One main color can suffice; use a few distinct hues and redundant marker/line encodings. Pale support fills need visible boundaries. |
| Reduce legend work | Prefer direct labels for a few separable curves. Otherwise put a compact legend in unused space or above the plot. Do not duplicate category labels already on a bar axis. |
| Design labels before shrinking fonts | Use concise professional names, horizontal text and sensible line wrapping. Transpose long categories before rotating or reducing type. |
| Match the color scale to the quantity | Use sequential maps for ordered nonnegative magnitudes and diverging maps for a meaningful center. Label the continuous colorbar with quantity and unit. Scientific missing data stay missing, never become structural zero by analogy with a business matrix. |
| State what intervals mean | SD, SE, confidence intervals, credible intervals and ensemble ranges are different. Render supplied bounds or a justified documented calculation; never decorate a line with invented uncertainty. |
| Inspect the rendered artifact | Check final-size reading, clipping, axis integrity, color-vision redundancy and export dimensions. Agreement between outputs sharing one helper is not independent validation. |

Do not import dashboard cards, branding, business KPI conventions or a mandatory web
stack into journal graphics. Use native vector/scientific plotting tools, retaining
the existing backend when revising an author's figure. A richer visual vocabulary is
a menu of scientific encodings, not a demand to use a different chart in every panel.
