# Image generation: route, compose and inspect

Read when choosing imagegen, creating conceptual artwork, or combining illustration with
scientific figures. These are workflow decisions, not observations distilled from JACS papers.
The current [ACS policy snapshot](../../jacs-shared/references/graphics-policy.md#ai-generated-artwork)
separates captioned figures, covers and TOC graphics. Check the intended use before generating.

## Choose by meaning and destination

| Requested visual | Route | What must remain source-backed |
|---|---|---|
| Quantitative plot, including a schematic energy profile with stated values | Scientific plotting from data | Every observation, curve, distribution, energy, uncertainty interval, scale and label |
| Exact chemical structure, reaction scheme or stereochemical comparison | Chemical drawing software or supplied vector assets | Connectivity, bond order, charge, stereochemistry, atom mapping and authored arrow meanings |
| Calculated TS, conformer, density surface or physical trajectory | Appropriate renderer using supplied coordinates or fields | Geometry, field values, atom identity, orientation and all reported measurements |
| Simple workflow, icons, boxes and arrows | Editable vector drawing | Process order, branch conditions, stage status and labels |
| Captioned main-text method/principle illustration | Imagegen can supply a useful nonquantitative insert or composition study | Exact chemistry, process arrows, labels and any data are separate source-backed layers |
| Cover concept or expressly illustrative science communication | Imagegen is a useful creative route | Bounded scientific idea and identification as a conceptual illustration; apply the destination's requirements |
| ACS TOC, including a graphical abstract serving as the TOC | Original precise drawings and author-sourced assets; no generated-image layer | The chemical object, central operation and evidence boundary |
| Measured image such as a micrograph, gel or detector map | Source-preserving scientific image workflow | Observed features; do not generate, remove or repair evidence with imagegen |

Raster versus vector is a rendering distinction, not a test of scientific origin. A scatter
layer rendered to PNG from a CSV remains data-derived; an AI illustration traced to SVG remains
AI-derived. Do not run a data plot through imagegen to restyle it or repair its labels. A
conceptual energy landscape must not imply a computed PES, a real saddle geometry, barrier
height, population or dynamical trajectory. Use the actual scientific field if that is the claim.

For a plan or suitability question, provide the choice and rationale without generating assets.
When the requested illustration benefits from generation, use the available `imagegen` skill
and its built-in tool route. It is optional, not an installation dependency for ordinary JACS
figures. If unavailable, state that limitation and continue supported planning/drawing work;
do not silently switch to a separate paid API or claim a generated asset exists.

## What this means for the current gallery

- `toc`: retain original chemical drawings. The current proposed-bond diagram can improve its
  hierarchy and chemical explanation without inserting AI artwork.
- `workflow`: the existing six-box sequence stays vector. When the task calls for a fuller
  method overview, add informative endpoint structures, highlighted bond changes and available
  3D/validation assets. A conceptual insert is optional for a captioned main-text figure.
- `structures` and `energy`: keep structure/number-driven renderers. A drawing of a candidate
  graph is not an optimized TS, and a dashed connector is not a calculated path.
- `boxplot`, `violin`, `ecdf`, `histogram`, `intervals`, `learning`, `spectra`, `heatmap`,
  `agreement`, `parity`, `stages`, `comparison` and `showcase`: keep data-driven drawing.
  Improve colors, layout, marks and typography in their existing source.
- Covers and standalone illustrative scenes are additional use cases, not new gallery results.

## Compose a captioned illustration

1. **Fix the content.** State the supplied central idea, destination and final dimensions.
   Identify exact chemical objects, stage relations and any result the illustration must not
   imply. Missing coordinates stay missing; a conceptual placeholder must be identified as such.
2. **Assign layers.** Separate data panels, chemistry/geometry, explanatory artwork, and editable
   labels/arrows. Decide whether an illustration explains something that simpler drawing cannot.
   The user need not fill a new form when the supplied material already answers these questions.
3. **Generate only the useful artwork.** Follow the imagegen skill's input-image and tool rules.
   Inspect local targets first. Name reference/edit-target roles, preserve stated invariants,
   and reserve space for exact overlays. Request no embedded labels when labels will be added
   in vector form. Do not send the entire quantitative panel through a generative edit.
4. **Assemble precisely.** Keep chemical structures from their native sources; draw arrows and
   text in an editable vector layer. Use a native editor or custom SVG composition when needed.
   The bundled assembly accepts SVG panels with embedded PNG/JPEG; it has no imagegen backend
   and does not accept a bare PNG as an SVG panel. See [assembly contract](figure-contract.md).
5. **Review the final composition.** Inspect scientific identity, semantic emphasis, legibility
   and effective raster resolution after scaling. Repair an asset that introduces misleading
   chemistry; do not cover a false bond or label with another layer and assume the issue is solved.
6. **Deliver the sources.** Keep the selected original generated asset, its provenance, the
   editable composition, final export and reviewed caption together. Copy project assets into
   the project; reference files through stable relative paths or embed them. Save a sibling
   version unless replacement was requested. Generation alone is not a finished figure.

For scientific accuracy, the author-data layers take precedence over any generated preview.
Correct a generated insert locally in a separate asset, or omit it when it adds no explanation.
A request for a fully raster illustration can be honored for an appropriate use; separate vector
overlays are a useful default for mixed publication figures, not a universal file-format rule.

## Design choices for this project

Use the author's established palette. If none is supplied, the project's light blue, apricot and
teal palette can provide a starting point: pale large areas, clearer small accents and readable
dark text. See [color design](color-design.md). Do not impose this preference on another project.
Give one scientific idea visual priority; maintain clear negative space around exact labels.
Detail must survive the intended figure size, especially narrow single-column inserts.

Use texture, depth and lighting only when they explain the requested concept. Generic glowing
atoms, decorative neural-network meshes and heavy gradients rarely clarify which operation is
new. A workflow improves when readers can see what changes between stages, not simply when
every stage has a different icon. A flat, accurate drawing can be the most effective result.

## Prompt cards

Adapt these examples to the supplied facts; replace the braces before making a generation call.
Neither card is a TOC prompt. Tool arguments come from the available imagegen skill, not from
these prose fields. Do not infer unreported model versions, generation settings or seed support.

### Captioned method illustration: one conceptual insert

```text
Use case: scientific-educational
Asset type: Nonquantitative illustration insert for a captioned main-text method figure
Primary request: Explain {author-supplied operation} through {approved visual metaphor}.
Scientific scope: {what the illustration means}; it does not assert {unsupported result}.
Input images: {each supplied image and its reference/edit-target role, if any}
Composition: Fit {available panel aspect ratio}; keep {overlay area} clear for exact labels.
Style/medium: {requested style}; coherent with the surrounding scientific figure.
Color palette: {author palette or an explicitly chosen project default}
Text: No embedded text; exact labels and arrows will be added during vector composition.
Constraints: Do not invent molecules, bond connectivity, measured points, numerical axes,
geometries or successful validation. Preserve {specific invariants for an edit}.
```

For example, a candidate-search illustration can communicate exploration and refinement when
that is the supplied method. Its conceptual paths must not be captioned as observed reaction
trajectories. Show real endpoints and geometries in separately rendered inserts when available.

### Cover concept

```text
Use case: stylized-concept
Asset type: Scientific journal cover concept; not a TOC graphic or data figure
Primary request: Communicate {one author-supported scientific idea} using {approved metaphor}.
Scientific scope: Artistic interpretation; do not portray unverified structures as actual results.
Composition: {current cover dimensions and any supplied reserved areas}; one visual focus.
Style/medium: {requested medium, light and depth}; details readable at the intended display size.
Color palette: {supplied preference}
Text: No generated journal masthead, logos, numerical labels or invented chemical notation.
Constraints: Use {provided scientific assets} only as specified; preserve their meaning.
```

Do not assume TOC dimensions apply to a cover. For final cover submission, use the appropriate
cover requirements in addition to the [AI policy snapshot](../../jacs-shared/references/graphics-policy.md#ai-generated-artwork).

## Provenance and final review

Record the following for each generated asset in a simple project-local Markdown or JSON record;
this is an accompanying record, not a new field accepted by the bundled figure-spec schema:

- Asset file and SHA-256; origin: generated or edited; intended role and final figure/panel.
- Actual prompt and revision prompts; input asset identifiers, roles and hashes where used.
- Tool name, generation date, and model/settings only when actually exposed by the tool.
- Source scientific facts, separate data/structure files, and remaining unknowns.
- Final placement dimensions, cropping/compositing operations and exported-figure hash.
- Actual review findings and applicable disclosure text; distinguish author review from agent review.

Preserving prompts supports traceability; it does not promise bit-identical regeneration.
Retain selected output bytes so the final composition can be rebuilt. Tracing or redrawing a
generated concept does not establish that its origin is non-AI; follow the destination's policy.
Do not route a TOC through an AI draft-and-trace workaround.

Inspect the generated asset and final export separately. Check accidental pseudo-text, chemistry,
arrow direction, perspective, missing/duplicated objects, occlusion and implied result status.
Read the caption with the image: conceptual artwork should not be described as a simulation,
optimized geometry, measured field or validated mechanism. Keep frequency checks, IRC execution
and endpoint identification distinct. A checkmark requires actual supporting status.

For each raster placement, compute effective DPI from source pixels divided by displayed inches
on both axes, accounting for cropping/scaling. Increasing export DPI does not recover source
detail. Check edge halos and small decorative texture at final size. Preserve readable vector
labels; the PDF auditor cannot certify labels or strokes baked into a bitmap.

Report what was actually produced and checked. A prompt card is not a generated image; a
renderable PDF is not a scientific or publication-policy approval. Read [QA](qa.md) and apply
submission-specific checks only when delivering for that purpose.
