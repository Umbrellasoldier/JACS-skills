# Independent forward-test artifacts

The same [raw request and inputs](../forward-inputs/request.md) were given to two separate
agent contexts. One used the new skill; the other did not read this repository's skills,
scripts or examples. Neither saw the other output. A third context assessed anonymized
figures and captions; the mapping was withheld until that assessment finished.

These folders retain the original PNG/SVG artwork, captions, calculations and runnable
programs. PDF artifacts were inspected locally; they can be regenerated rather than being
included in the publication set. All data are synthetic. Reports describe agent inspection,
not review by a human chemistry or graphics expert.

| Workflow | Program | Data/QA | Figures |
|---|---|---|---|
| Without skill | [make_figures.py](baseline/make_figures.py) | [validation.json](baseline/validation.json) | [Prediction](baseline/figure_1_predictions.png), [stages](baseline/figure_2_stages.png), [structures](baseline/figure_3_structures.png) |
| With skill | [render_figures.py](with-skill/render_figures.py) | [integrity checks](with-skill/qa/integrity-checks.json) | [Prediction](with-skill/figures/figure1_predictions.png), [stages](with-skill/figures/figure2_stages.png), [structures](with-skill/figures/figure3_structures.png) |

Copy either directory to an ignored local directory before executing its program, using the
repository's locked `figures` and `chemistry` dependencies. Create `figures/` and `previews/`
in the copied with-skill directory if missing. Other input/source folders are already bundled.
PDF metadata can vary across runs; a regenerated hash need not equal the evaluated file hash.

[Snapshot manifest](snapshot-manifest.json) records original and published program hashes.
Only machine-specific interpreter/source-directory strings were normalized for publication;
the plotting and audit logic were not edited. These historical programs and helper snapshots
are excluded from repository style formatting so later changes do not rewrite the experiment.
They are evidence artifacts, not additional runtime modules or promises of universal behavior.

The skill-assisted agent chose custom plotting with the skill's validator and auditor;
the experiment tests the whole workflow, not just a fixed Matplotlib style sheet.
