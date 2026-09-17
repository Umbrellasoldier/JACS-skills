# Chemistry figure decisions

## Workflows

Distinguish information available during training, candidate generation, ranking and final
evaluation. A reference-based best-of-many selection needs an explicit label; do not visually
present it as deployable ranking. Arrows encode the supplied process, not proof of causality.
Use a custom layout when branching, loops or several populations exceed the simple grid helper.

Improve a text-box workflow by showing the scientific objects at the informative stages:
mapped endpoints, explicit proposed bond changes, source-coordinate 3D seeds, and the actual
frequency/IRC checks where available. Select only the details needed to explain the method;
do not invent geometries or validation results to fill space. Keep direction and stage names
editable. [Image-generation routing](imagegen-workflow.md) covers optional conceptual inserts;
a simple box-and-arrow diagram normally stays vector.

## Energy profiles

Preserve E/H/G, activation versus reaction quantities, solvent, theory, temperature, standard
state and corrections. Compare pathways only with compatible reference states. A bound
reactant complex and separated reactants are different zeros. The energy template plots
discrete levels with schematic connectors, not a computed IRC or a continuous potential.

State labels and nearby structures should identify the chemical alternatives. When a real
IRC is supplied, preserve coordinate ordering and its physical definition; do not smooth away
features for appearance. Branching probabilities need dynamics or other appropriate evidence.

## Prediction and method comparison

Name the measured quantity and units on both axes; distinguish fit from identity lines. Keep
outliers and failures accounted for. Residuals often provide information that a second summary
metric does not. Share population, split and calculation budget when comparing methods.
Comparable quantities benefit from comparable axes; differing quantities need their own scales.

Large scatter data can use rasterized marks while retaining vector axes. Declared aggregation
or density maps can also help. Rendering speed alone is not permission to remove observations.
Do not add a confidence band without an estimator, replicate unit and justified calculation.
For a small matched reaction set, a horizontal residual plot with readable IDs and paired
connectors can be clearer than rotated tick labels. Disclose any display-only category offsets.

## Validation stages

Graph hypotheses, optimized structures, frequency-characterized TSs, IRC calculations,
endpoint identities and thermochemistry are distinct results. A successful optimization is
not a successful complete path. Identify whether the population is reactions, candidates,
conformers or attempts. Show failed and unprocessed cases separately and state the denominator.
Bars can end at each stage's entered count, or extend to the initial cohort with explicit
earlier-attrition segments. Choose according to the comparison; the gray remainder is optional
and never changes the conditional denominator. Avoid expanding a simple accounting plot to
double-column width merely to accommodate repeated explanations.

## Structures and schemes

Use source geometries or chemically checked drawings. Preserve stereochemistry, charge,
protonation, atom maps and spin metadata. A drawn dashed bond can denote a forming bond or
another convention; define it instead of assigning a generic meaning. Keep reaction and
retrosynthetic arrow directions distinct. Scheme reagents, yields and conditions are facts.

The bundled SMILES route supplies 2D depictions only. For TSs, render actual XYZ/SDF geometries
with available chemistry tools and compose their SVG assets, or write a source-backed custom
renderer. Calculate displayed distances from the original coordinates with explicit atom
indices and units. A geometry projection must not change the underlying measurements.
Record rendering orientation/selection and inspect relevant bonds for occlusion. Matched
orientations and scale help compare conformers without asserting they have identical geometry.

## TOC

Start from the paper's central chemical idea and a small number of structures or process steps.
Reduce detail according to the TOC purpose, then render at its own physical size. Do not shrink
a full results page. Use the separate [TOC policy](../../jacs-shared/references/graphics-policy.md).
The current [ACS AI policy](../../jacs-shared/references/graphics-policy.md#ai-generated-artwork)
excludes AI-generated images from TOC graphics. Use original chemical drawings and author-sourced
assets; do not insert a generated background, trace generated artwork, or rename a TOC as a
graphical abstract to bypass this distinction. A cover or captioned main-text concept illustration
has a different route in [image-generation guidance](imagegen-workflow.md).

Make the chemical problem identifiable: supplied reactant/product connectivity, a relevant
structural contrast, or another concrete chemical object should explain what the method acts
on. Three generic boxes such as input/generation/validation rarely communicate that specificity.
Name the central operation and distinguish its proposals from verified outcomes. A connectivity
arrow or highlighted product bond does not establish a TS geometry or a validated mechanism.
