"""Validate v0.3 evidence, frozen records and optional locally acquired image bytes."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def validate(root: Path, sources: Path | None = None) -> dict:
    refs = root / "skills/jacs-shared/references"
    evaluation = root / "evaluation/figure-v3"
    papers = jsonl(refs / "figure-corpus-v3.jsonl")
    development = jsonl(refs / "figure-observations-v3.jsonl")
    heldout = jsonl(evaluation / "heldout-observations.jsonl")
    rules = jsonl(refs / "figure-rules-v3.jsonl")
    manifest = {p["paper_id"]: p for p in papers}
    annotations = {a["annotation_id"]: a for a in development}
    errors = []
    if len(manifest) != len(papers) or len({p["doi"].lower() for p in papers}) != len(papers):
        errors.append("Duplicate v3 paper ID or DOI")
    if any(p["journal"] != "Journal of the American Chemical Society" for p in papers):
        errors.append("Non-JACS paper in v3 manifest")
    freeze = json.loads((evaluation / "rule-freeze.json").read_text())
    for file, expected in freeze["files"].items():
        if hashlib.sha256((root / file).read_bytes()).hexdigest() != expected:
            errors.append(f"Changed v3 frozen artifact: {file}")
    selection = json.loads((evaluation / "selection.json").read_text())
    for p in selection["papers"]:
        current = manifest.get(p["paper_id"], {})
        if any(current.get(k) != p[k] for k in ("doi", "pmcid", "split")):
            errors.append(f"Changed v3 source identity/split: {p['paper_id']}")
        if current.get("v3_role") != p["split"]:
            errors.append(f"Incorrect v3 evidence role: {p['paper_id']}")
    all_notes = development + heldout
    if len({a["annotation_id"] for a in all_notes}) != len(all_notes):
        errors.append("Duplicate v3 visual annotation")
    for role, notes in (("development", development), ("holdout", heldout)):
        for note in notes:
            paper = manifest.get(note["paper_id"], {})
            if paper.get("v3_role") != role or note["doi"] != paper.get("doi"):
                errors.append(f"Invalid v3 observation provenance: {note['annotation_id']}")
            if not note["locator"] or not note["review_method"] or not note["limitation"]:
                errors.append(f"Missing v3 review scope: {note['annotation_id']}")
            if sources is not None:
                path = sources / note["paper_id"] / Path(urlsplit(note["source_url"]).path).name
                if (
                    not path.is_file()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != note["source_sha256"]
                ):
                    errors.append(f"v3 source bytes mismatch: {note['annotation_id']}")
    counts = Counter(a["paper_id"] for a in all_notes)
    old = {p["paper_id"]: p for p in jsonl(refs / "figure-corpus.jsonl")}
    for paper in papers:
        if paper["v3_role"] == "prior_evidence":
            expected = old.get(paper["paper_id"], {}).get("reviewed_figures")
            if paper["prior_reviewed_figures"] != expected or paper["v3_new_figures_reviewed"]:
                errors.append(f"Invalid carried-forward counts: {paper['paper_id']}")
        elif paper["reviewed_figures"] != counts[paper["paper_id"]]:
            errors.append(f"v3 review count mismatch: {paper['paper_id']}")
    for rule in rules:
        ids = rule["supporting_annotations"] + rule["counterexamples"]
        if not rule["supporting_annotations"] or any(i not in annotations for i in ids):
            errors.append(f"Unknown or held-out v3 rule evidence: {rule['rule_id']}")
    coverage = json.loads((evaluation / "coverage.json").read_text())
    if coverage["papers_total"] != len(papers) or coverage["figures_total"] != sum(
        p["reviewed_figures"] for p in papers
    ):
        errors.append("Published v3 coverage disagrees with manifest")
    return {
        "papers": len(papers),
        "figures": sum(p["reviewed_figures"] for p in papers),
        "new_development_figures": len(development),
        "new_heldout_figures": len(heldout),
        "conditional_rules": len(rules),
        "local_image_hashes_checked": sources is not None,
        "errors": errors,
    }
