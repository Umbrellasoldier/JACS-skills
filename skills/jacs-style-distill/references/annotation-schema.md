# Annotation and rule schema

The corpus helper writes one JSON object per passage. Fields include `paper_id`, `doi`,
`source_sha256`, `source_url`, `source_version`, `identity_status`, `block_id`, `locator`,
`section_original`, `section`, `kind`, `text`, and `text_sha256`.

For explicit block import, provide at least `text`, `section_original`, `section`, `kind`, and
`locator`. The locator must name a real source position. Supported kinds: `paragraph`,
`heading`, `caption`, `table`, `other`. Supported sections: `title`, `abstract`, `introduction`,
`results_discussion`, `results`, `discussion`, `conclusion`, `methods`, `theory`, `body`,
`captions`, `tables`, `back_matter`, `other`. Do not infer missing section text.

## Public evidence annotations

Publish paraphrased observations rather than full paragraphs. Each annotation has:

- `annotation_id`, `paper_id`, `doi`, `block_id`, `locator`, `source_sha256`, `text_sha256`;
- `section`, `rhetorical_moves`, and an original concise `observation`;
- `review_status`, who/what reviewed it, and any uncertainty.

Use `review_status: agent_reviewed` for an agent's checked interpretation. Do not relabel it
as human-reviewed. Raw passages and extraction artifacts remain local; hashes bind the
public notes to those passages, and source URLs/offsets allow reconstruction where accessible.

## Rule cards

A rule has `rule_id`, `rule_type`, `status`, `scope`, `guidance`, `supporting_annotations`,
`counterexamples`, `confidence`, and `limitations`. `scope` records applicable article types,
domains, and sections. A `corpus_observation` requires real supporting annotations and
development sources. An untested recommendation is `editorial_heuristic` or `hypothesis`.
Neither class is an official journal requirement. Do not invent a prevalence numerator for
purposively selected passages; report measured counts separately.

Record exclusions and unassessed counterexamples explicitly. A corpus pattern can be useful
without being universal. A one-paper example remains a one-paper example.
