# Figure design study, v0.3

The user requested lighter colors and a much broader study of chart types, marks,
legends, axis language, typography, scales and composition. This study adds 36 papers
to the 14-paper v0.2 archive. A downloaded image is not a reviewed image.

## Selection and separation

The immutable `selection.json` was written before opening the new figures. Europe PMC
queries used `JOURNAL:"J Am Chem Soc" AND OPEN_ACCESS:Y` and publication dates
2022-01-01 through 2026-09-17, with six topic queries (computation, catalysis,
spectroscopy, materials, biological chemistry, and statistical/thermodynamic methods).
Sixty results per query formed a convenience search frame; titles and public metadata
guided purposive selection. This favors recent accessible articles and is not a random
or representative sample of JACS.

Thirty new papers are development sources. N08, N15, N21, N27, N33 and N36 are held out
at paper level. Their images must not inform the initial v0.3 rules. Freeze the rules
and development observations before opening these six papers; record exceptions or
failures separately. Shared author names will be reported, not interpreted as verified
independence of research groups. No paper is reassigned to improve an evaluation.

The old 14 papers retain their original v0.2 records and evaluation. All previously
seen papers, including the old holdouts, are prior/development evidence for this
iteration. Never report them as fresh holdouts. Separate Article, Communication and
Perspective observations using article metadata.

## Review procedure

Verify DOI and exact journal against versioned PMC JATS and object metadata. Record
license, manuscript/publisher status, figure locator and SHA-256. Keep article PDFs,
full text and figure images in ignored local storage. Publish original observations,
source links and synthetic demonstrations, not a repackaged publisher image collection.

Inspect up to the first four available numbered main figures of each new paper, and
additional figures when they add a relevant chart type. A sheet may aid navigation;
review at readable source resolution. Record specific observed chart families,
composition, colors/marks, legend/axis details and limitations. Do not infer tiny text,
units, physical font size or statistical interval semantics from an unreadable preview.
Captions may clarify semantics but cannot substitute for visual inspection.

For a PDF subset, inspect rendered pages and attempt text/transform measurement.
Embedded raster plot lettering has no recoverable PDF font size. Publisher caption
fonts are not evidence for figure fonts. Report measured physical figure geometry
separately from inferred visual hierarchy and project typography defaults.

Counts use unique papers and figure identifiers, not downloaded assets, crops or
contact sheets. A multi-panel figure counts once; no panel count is claimed without
separate panel annotation. Keep prior and newly inspected counts explicit.

## Design and validation

Rules distinguish corpus observations, ACS requirements, Data plugin adaptations and
user/project preferences. Color comfort is a design judgment, not an experimentally
established property of a hex palette. Use pale large fills, stronger boundaries and
charcoal text, then inspect actual examples, grayscale and color-vision simulations.

Validate supplied data, transforms, denominators, units, limits and interval definitions
before visual polish. Render at declared physical dimensions, inspect final exports
and execute meaningful regression cases. A mechanical pass is not an aesthetic or
scientific approval. A fresh independent forward task will test the skill on new raw
inputs; preserve the earlier unfavorable v0.2 blind review unchanged.
