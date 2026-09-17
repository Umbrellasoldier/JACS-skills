#!/usr/bin/env python3
"""Check frozen visual observations, paper splits and optional local image hashes."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def validate(root: Path, sources: Path | None = None) -> dict:
    refs = root / "skills/jacs-shared/references"
    papers = jsonl(refs / "figure-corpus.jsonl")
    annotations = jsonl(refs / "figure-annotations.jsonl")
    rules = jsonl(refs / "figure-rules.jsonl")
    split = json.loads((root / "evaluation/figures/split.json").read_text())
    freeze = json.loads((root / "evaluation/figures/rule-freeze.json").read_text())
    errors = []
    manifest = {p["paper_id"]: p for p in papers}
    if len(manifest) != len(papers) or len({p["doi"].lower() for p in papers}) != len(papers):
        errors.append("Figure corpus contains a duplicate paper ID or DOI")
    for label in ("development", "communication", "holdout"):
        if sorted(p["paper_id"] for p in papers if p["split"] == label) != sorted(split[label]):
            errors.append(f"Figure split differs from the frozen split: {label}")
    for p in papers:
        if p["journal"] != "Journal of the American Chemical Society":
            errors.append(f"Non-JACS figure source: {p['paper_id']}")
        if p["split"] == "development" and p["article_type"] != "Article":
            errors.append(f"Non-Article in figure development stratum: {p['paper_id']}")
        if p["reviewed_figures"] > p["available_figures"]:
            errors.append(f"Reviewed count exceeds available figures: {p['paper_id']}")
    for name, sha in freeze["sha256"].items():
        if hashlib.sha256((refs / name).read_bytes()).hexdigest() != sha:
            errors.append(f"Frozen figure rule evidence changed: {name}")
    by_id = {a["annotation_id"]: a for a in annotations}
    if len(by_id) != len(annotations):
        errors.append("Duplicate figure annotation")
    for a in annotations:
        paper = manifest.get(a["paper_id"])
        if not paper or paper["split"] not in {"development", "communication"}:
            errors.append(f"Figure rule evidence leaks held-out data: {a['annotation_id']}")
            continue
        if any(a[k] != paper[k] for k in ("doi", "split", "article_type", "source_version")):
            errors.append(f"Figure annotation provenance mismatch: {a['annotation_id']}")
        if not a["locator"] or not re.fullmatch(r"[a-f0-9]{64}", a["source_sha256"]):
            errors.append(f"Invalid figure locator/hash: {a['annotation_id']}")
        if not a["review_method"] or not a["measurement_limit"]:
            errors.append(f"Figure observation lacks its review scope: {a['annotation_id']}")
        if sources is not None:
            path = sources / a["paper_id"] / Path(urlsplit(a["source_url"]).path).name
            if (
                not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != a["source_sha256"]
            ):
                errors.append(f"Local figure bytes do not match observation: {a['annotation_id']}")
    for rule in rules:
        support = rule["supporting_annotations"]
        if not support or rule["is_journal_requirement"]:
            errors.append(f"Invalid corpus observation status: {rule['rule_id']}")
        ids = support + rule["counterexamples"]
        if any(i not in by_id for i in ids):
            errors.append(f"Unknown figure rule evidence: {rule['rule_id']}")
            continue
        if any(by_id[i]["split"] != "development" for i in ids):
            errors.append(f"Non-Article development evidence in figure rule: {rule['rule_id']}")
        if sorted({by_id[i]["paper_id"] for i in support}) != sorted(rule["supporting_papers"]):
            errors.append(f"Figure rule paper counts disagree: {rule['rule_id']}")
    heldout = jsonl(root / "evaluation/figures/heldout-observations.jsonl")
    for row in heldout:
        paper = manifest.get(row["paper_id"])
        if not paper or paper["split"] != "holdout" or row["doi"] != paper["doi"]:
            errors.append(f"Invalid held-out figure provenance: {row['paper_id']}")
        if row["reviewed_at"] <= freeze["frozen_at"]:
            errors.append(f"Held-out figure reviewed before rule freeze: {row['paper_id']}")
        if sources is not None:
            path = sources / row["paper_id"] / Path(urlsplit(row["source_url"]).path).name
            if (
                not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != row["source_sha256"]
            ):
                errors.append(
                    f"Held-out source hash mismatch: {row['paper_id']}-{row['figure_id']}"
                )
    counts = Counter(a["paper_id"] for a in annotations + heldout)
    if any(p["reviewed_figures"] != counts[p["paper_id"]] for p in papers):
        errors.append("Recorded figure-review counts do not match inspection notes")
    return {
        "papers": len(papers),
        "paper_splits": dict(Counter(p["split"] for p in papers)),
        "development_and_calibration_figures": len(annotations),
        "heldout_figures": len(heldout),
        "rules": len(rules),
        "local_image_hashes_checked": sources is not None,
        "errors": errors,
    }
