# Chemistry semantics for scientific editing

These are evidence-accounting checks for computational reaction writing, not an exhaustive
chemistry protocol and not additional journal policy. Read only the applicable subsection.

## Energies and chemical identities

Record what a reported quantity means before changing its notation: electronic energy,
enthalpy, Gibbs free energy, barrier, reaction energy, or difference between competing paths.
Keep the reference state, units, theory, solvent, temperature, standard state, and applicable
corrections with the claim or its cited source. A missing condition stays unknown.

Preserve atom mapping, stereochemistry, protonation, charge, spin state, and the distinction
between an isolated fragment and a complex. A minimum-energy conformer and an ensemble result
are different reporting choices. Check a unit conversion numerically, record rounding, and
preserve the identity and conditions of the quantity being converted.

## Transition states and pathways

Keep these evidence stages distinct: generated candidate, converged optimization, frequency
characterization, reaction-path calculation, endpoint identity, thermochemistry, and any
dynamics or experimental validation. Name the stage that was actually completed.

A geometric similarity score is not a completed pathway validation. Frequency information
must be described as such; endpoint claims need relevant connectivity evidence. Static-path
results should not silently become branching probabilities or observed product selectivity.
Check the supplied scientific protocol rather than assuming every system needs an identical
validation recipe. See the pilot B06 source in the corpus manifest for an example where
pathway and dynamics evidence have separate roles.

## Machine-learning and screening claims

Identify inputs available during training, candidate generation, selection, and evaluation.
If a reference structure or answer is used to choose the best candidate retrospectively,
retain that condition. Distinguish deployment ranking from retrospective best-case evaluation.

Tie every metric to its unit of analysis and population: reactions, candidates, conformers,
successful optimizations, or completed validated pathways. Keep exclusions and failures visible.
Check whether compared runs share chemical tasks, splits, budgets, theory, and success criteria.
Name train/validation/test uses, scaffold or reaction-family splits, and known overlap when
those affect a generalization claim. Do not infer independence just from different filenames.

Timing claims need the included stages and relevant hardware/budget. A case study supports
its tested scope; a broader claim needs broader evidence. Read A10 in the pilot for an example
of comparing learned predictions with a simpler data-distribution explanation.

## Mechanism and selectivity

Keep computed support, correlations, proposed explanations, and experimental observations
distinguishable. A structure–reactivity trend can motivate a mechanism without uniquely
establishing it. Identify the evidence that discriminates alternatives before strengthening
the wording. Do not infer rate ratios from barrier differences without the required physical
assumptions and conditions. Preserve uncertainty when evidence is incomplete.
