# Submission review: meaning, marks and delivered package

Use for submission preparation or a figure-quality critique. These are conditional checks,
not a required set of panels, tests or annotations for every plot.

## Decide what the figure supports

Review the figure together with its final caption. Separate export checks, visual readability,
adequacy of scientific definitions/data, and the complete submission package. A technical pass
establishes only the checked properties. For synthetic examples, report whether the design is
usable and identify the author facts needed to apply it; do not claim research submission readiness.

| Situation | Decision that changes the figure or claim |
|---|---|
| Supplied interval with an undefined point | Establish the estimate and the bounds' meaning. Preserve supplied values while clarifying; do not relabel an arbitrary interval as a CI. If replacing an illustrative dataset, disclose the change. |
| A box center is called bias | A median is not mean signed error. Define and plot the intended statistic, or describe a signed-error distribution. |
| A small-sample violin appears multimodal | Compare a reasonable alternative bandwidth. If substantive shape changes, show sensitivity or choose raw points/ECDF. Do not tune smoothing to a desired story; no universal n cutoff establishes a reliable density. |
| Observations hide one another | Use categorical-only packing, facets or another appropriate display. Preserve measurements and every observation; preserve IDs and links in paired plots. Unresolved crowding needs a design decision, not unreadably small marks. |
| Histogram outlines coincide | Consider facets with shared bins and axes; count every observation and define bin closure. Declare any normalization. |
| Heatmap summaries have unclear populations | Define the cell statistic, memberships and n where needed. State missingness reasons; unknown reasons remain unknown. Do not invent counts or infer domain generalization from arbitrary labels. Use consistent meaningful precision. |
| Learning curves have bands | Identify replicate unit, train/test population and SD/SE/CI meaning. Do not invent a held-out test set for synthetic summaries. Check band visibility at final size. |
| Sequential accounting includes pending work | Declare the snapshot/window. Not-entered cases can include upstream failures and pending work; they are not all failures. Distinguish passed/entered from passed/initial cohort. |
| Energy paths end at different energies | Identify distinct states (e.g., P_A/P_B) and their structures when supplied. Do not give an identical product two energies under one convention. A generic level tutorial is not a chemically specified mechanism. |
| Workflow/TOC claims TS generation | Distinguish graph edits, 3D embedding and validation; define color emphasis. A product drawing alone does not establish a TS method. Dashed proposed links are not measured partial bonds or optimized geometry. |

## Inspect the delivered scale

Inspect final PDF/SVG and an intended-size preview. Compare line weight, marker density,
text, legends and negative space together. Use pale fills with legible outlines. Choose a
compact format for sparse data and sufficient plotting area for dense distributions. Share
scales for comparisons where appropriate; arbitrary zooms can exaggerate differences.
Do not add R², significance stars, confidence intervals or thresholds merely to look scientific.

Check effective strokes after export scaling, not only source linewidth. An opaque black wedge
can have a thin outline but a substantial silhouette; inspect it as a filled shape. A zero-width
setting on a fill-only path is not a painted hairline. The bundled audit follows painted paths,
affine transforms and invoked Forms; glyph outlines, pattern internals, clipping and raster
content remain separate limitations.

## Write the caption as prose

State the scientific object, relevant panel roles, statistic, unit/n, sign convention, interval
meaning and applicable normalization/reference. Use names actually displayed. Keep filenames,
implementation keys, logs and duplicate definitions in the reproduction record. Essential
definitions must also reach the reader; metadata alone is insufficient.

`caption_mode: authored` keeps supplied prose and writes facts separately; `compose` retains
automatic facts-appending behavior. Neither checks scientific prose for truth. Compare caption,
facts, data and final figure, including every panel and their shared population/argument.
Record unresolved author facts and remaining visual limitations. Missing measurements or
methods are not repaired by typography or removing a synthetic label.
