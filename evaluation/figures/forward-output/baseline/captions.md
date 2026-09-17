# Figure captions

**Figure 1. Comparison of predicted activation Gibbs free energies using synthetic example data.** (a) Predictions from Baseline and Candidate for the same eight reactions; the dashed line denotes agreement with the reference. (b) Signed residuals, defined as prediction minus reference, with all reaction identifiers retained. Gray segments connect paired results; the small vertical offsets in (b) separate the two markers and have no quantitative meaning. MAE and RMSE are calculated from all eight records per method, without uncertainty or significance estimates. All energies are in kcal mol⁻¹, relative to separated reactants, at 298.15 K and a 1 mol L⁻¹ standard state. Both methods share the same example computational level and solvent settings; their specific identities were not supplied.

**Figure 2. Stagewise outcomes for a synthetic cohort of 199 reactions.** Stacked bars show passed, failed, and pending counts on a common absolute-count axis. Only passed reactions enter the following stage. Each displayed pass rate is passed/entering that stage, with denominators of 199, 150, 110, and 90, respectively; pending reactions remain in their stage denominator. The final 65 passed reactions represent 32.7% of the initial cohort. Rows describe nested stage populations and must not be summed as independent reaction cohorts.

**Figure 3. Two-dimensional depictions of the supplied synthetic stereoisomers.** Isomer 1 (s1) and Isomer 2 (s2) retain their atom-map labels :1–:6 and specified stereochemistry. Solid and hashed wedges distinguish opposite configurations at mapped atom 2; the shared drawing layout does not imply a three-dimensional geometry or quantitative bond lengths.

Original mapped inputs, preserved verbatim:

| ID | Label | Atom-mapped SMILES |
|---|---|---|
| s1 | Isomer 1 | `[CH3:1][C@H:2]([OH:3])[C:4](=[O:5])[OH:6]` |
| s2 | Isomer 2 | `[CH3:1][C@@H:2]([OH:3])[C:4](=[O:5])[OH:6]` |
