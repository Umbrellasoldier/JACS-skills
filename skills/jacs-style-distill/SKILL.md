---
name: jacs-style-distill
description: Build a source-traceable JACS writing-style corpus from supplied full texts or public article records. Use for JACS 文风蒸馏、语料整理、段落修辞标注; not manuscript drafting or model parameter training.
---

# JACS style distillation

Produce conditional writing guidance supported by identifiable article passages. The bundled
pilot covers a small reaction-chemistry sample; expand its scope only with new source evidence.

## Sources and split

Read [corpus workflow](references/corpus-workflow.md) and
[annotation schema](references/annotation-schema.md) for a new corpus or source format.
Reuse [the manifest](../jacs-shared/references/corpus-manifest.jsonl) when relevant, or create
a user-scoped manifest. Separate Article, Communication, and Perspective/Review. Freeze
development/holdout groups before deriving rules; keep versions of a DOI in one group.

Acquire available full text through publisher/open repositories or user-provided files.
Track unavailable sources rather than inventing access. Metadata and abstracts can support
their own scope only. A paper's presence in PMC does not guarantee a particular API has it.

The bundled [corpus helper](scripts/corpus.py) supports PMC BioC JSON, JATS XML, and explicit
section-tagged JSONL blocks. Resolve its path relative to this SKILL.md, not the working directory.
Run `python <skill-dir>/scripts/corpus.py --help` for the CLI. It checks source identity,
preserves locators and versions, and produces separate prose/caption/method records. Use a
suitable available PDF/OCR tool for other inputs, then inspect the structure before import.

## Derive guidance

Read the actual passages and annotate their argumentative function, supporting evidence,
claim strength, transitions, and exceptions. Keep publisher headings alongside normalized
labels; verify cases where source tagging is wrong. Frequency counts are descriptive and
must identify their denominator, section filter, and tokenizer. Do not label an automatic
count as a human-verified rhetorical annotation.

Each rule needs scope, supporting passage locators, contrary cases or an explicit unassessed
status, and a confidence label. Distinguish an editorial hypothesis from a reviewed corpus
observation. Repeated features from one research group do not establish a journal-wide rule.
Use original explanatory examples; do not reproduce a paper's paragraphs in a public skill pack.

## Deliver

Return the source/acquisition manifest, annotation and rule files, measured statistics, and a
short report of coverage and limits. Raw full text stays in the user's chosen local data area.
When updating an installed rule library, produce a reviewable candidate change and validate
its references and split; do not silently treat every new observation as a universal default.
