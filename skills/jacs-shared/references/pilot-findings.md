# Pilot findings and limits

Checked 2026-09-17. The initial bibliography has 34 JACS records: 25 Articles,
5 Communications, and 4 Perspective/Review records. Seven Articles were held out before
analysis; 18 are development candidates. Eight development Articles yielded usable PMC
BioC text for this pilot: A07, A10, B06, C03, C05, C06, C08, C10.

The [manifest](corpus-manifest.jsonl) records DOI, version, acquisition, digest, and split.
The [annotations](pilot-annotations.jsonl) are agent-reviewed interpretations of selected
passages and headings, not independent human annotations or exhaustive paragraph labeling.
The [five rule cards](style-rules.jsonl) are conditional observations. No manuscript-acceptance
prediction or journal-wide style claim is made.

## What the sample supports

| Observation | Evidence to inspect |
|---|---|
| Introductions connect a design choice to a chemical purpose, with variable roadmap detail. | JACS-P01; A07, C05, C06, C10 introductions. |
| Results supply the definitions needed for a comparison; their opening moves vary. | JACS-P02; A07/A10 population definitions, C08 measurement conditions, B06 figure orientation. |
| Computation, experiment, and dynamics have distinct evidentiary roles. | JACS-P03; B06, C03, C06, C08. |
| Limitations can constrain a specific contribution or identify an unresolved question. | JACS-P04; A07, A10, C03, C08, C10. |
| Section order and heading style are not uniform. | JACS-P05; topical sections in A07/C03 and the earlier Experimental Section in C10. |

Use these observations to choose structure and calibrate claims. The source articles also
contain expansive language and author-specific habits; publication does not make every
sentence a rule worth reproducing.

## Descriptive measurement

The [statistics](pilot-statistics.json) count 31,005 word tokens in the selected main-prose
sections, including abstracts and theory, excluding Methods, captions, tables, back matter,
and headings. The tokenizer and approximate sentence-count method are recorded in that file.
For example, `however` occurs 43 times across all eight papers; `furthermore` occurs nine
times in four. These are counts anywhere in prose, not sentence-initial counts. They are
not a prescription to prefer one connector or target a frequency.

## Source and coverage limitations

- Three inputs (C05, C06, C08) are author manuscripts; distinguish them from publisher versions.
  Their formatting and occasional unresolved internal cross-references are not style templates.
- The source's C03 section tags wrongly group substantive topic sections under INTRO. A reviewed
  heading map separates theory and Results while preserving original headings and offsets.
- Five of the eight Articles are in the SPAAC/bioorthogonal group; several share authors. The
  pilot covers 2008–2023 and does not establish current chemistry-wide lexical preferences.
- None of the seven held-out Articles was used to derive these rules. Exact normalized complete
  author names have no overlap between development and holdout Article records; this is only
  a bibliographic diagnostic, not proof of independent institutions or absence of spelling variants.
- Communication and Perspective writing have no empirical style calibration in this release.
  Communication formatting is supported by the separate official-policy snapshot.
- C09 was attempted but unavailable through the first BioC request. Other unacquired candidates
  remain explicitly marked; the bibliography is larger than the analyzed full-text sample.
