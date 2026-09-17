# Figure QA

## Data checks

Compare plotted records with the author source, including row/ID counts, units, filters,
groups and transformations. Check energy references, success denominators, matched comparison
sets and uncertainty definitions. Preserve raw input. The bundled spec validator checks its
supported schemas; correct scientific interpretation remains an author/agent responsibility.

## Render checks

Inspect each panel and the complete figure at its intended size. Check label visibility,
scientific symbols, arrow directions, scales, color/marker consistency, legend placement,
structure identity, crowded bonds and repeated view orientations. Check grayscale or color
vision accessibility where color carries a distinction. Avoid whitespace or salience changes
that hide a control or failure. Statistical annotation requires actual statistical evidence.
Check coincident values, drawing order and interval-to-marker size: record counts can pass
while observations or error bars are hidden. For a density, examine bandwidth sensitivity
when interpreting its shape. For a matrix, inspect missing cells beside low values at final
size. A renderer's no-collision result does not establish hierarchy or scientific narrative.

The bundled renderer writes measured layout geometry for Matplotlib figures and audits the
exported PDF. To inspect a separately generated one-page PDF:

```text
python <skill-dir>/scripts/audit_figure.py figure.pdf --width-pt 504 --height-pt 240
```

Use `--min-font-pt 6` for TOC and `--layout figure.layout.json` for measured layout when
available. Re-measure after layout changes. Matching a script's nominal figsize does not prove
the exported page has that size. The figure's QA JSON records a hash of the PDF it inspected.

| Result | Meaning |
|---|---|
| `FAIL` | A deterministic size/text/stroke/layout/data problem requires correction before claiming readiness |
| `REVIEW_REQUIRED` | An overlap heuristic or unsupported object needs inspection; document the result |
| `MECHANICAL_PASS` | Supported mechanical checks passed; visual and scientific review remain required |
| `UNKNOWN` finding | The stated check could not be established; never convert it to a pass |

The PDF audit checks MediaBox and effective sizes of supported extracted text runs, including
their affine transforms. It does not prove every glyph is extractable, fonts are all embedded,
images have sufficient effective DPI, or chemical structures are correct. The Matplotlib layout
audit detects text bounding-box intersections, clipping and explicitly comparable plot areas.
It excludes tick labels outside the drawn axis limits. It does not implement comprehensive
text-versus-line/path collision detection. SVG and molecular bond overlaps require visual review.
The path auditor checks painted stroke widths through transforms and invoked Form objects.
Fill-only paths do not count as strokes. Narrow outlines on opaque same-color filled shapes
and anisotropic bounds require inspection; pattern internals, glyph outlines, clipping and
raster strokes are not fully established. The categorical point packer warns if final-size
spacing cannot separate all marks; do not suppress this by changing measured values.

Intentional text over a fill may be acceptable. Explain a reviewed exception rather than
weakening a global threshold. A designed large explanatory panel need not match smaller ones;
check comparable groups and their shared edges. Do not equate lack of collision with alignment.

## Delivery

Check caption facts against the figure and source data. A short QA note should state actual
checks, warnings resolved by visual review and any remaining limit. Reference the correct file
hash. Do not claim human review when only an agent inspected the figure. Synthetic examples
remain visibly labeled. Submission files follow the relevant current journal/TOC policy;
preview PNG and editable SVG have distinct roles. Keep a reproducible source/spec/environment.

Read only the actual delivered figure and caption for a second pass: can a reader determine
what each mark means, what n counts, which subtraction/normalization was used, what intervals
represent and how missingness is encoded? Verify that assembled panel definitions survived.
Then use the source to check those statements. The caption composer carries known facts but
cannot resolve conflicting author prose, undefined method names or unsupported causal claims.
Use `.caption-facts.json` to check authored prose, not as extra publication text. Apply
[submission review](submission-readiness.md) when reporting readiness, and distinguish the
technical, visual and scientific conclusions.
