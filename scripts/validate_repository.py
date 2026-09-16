#!/usr/bin/env python3
"""Validate skill packaging, source references and corpus split integrity without network access."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def validate(root: Path = ROOT, source_blocks: Path | None = None) -> dict:
    errors = []
    skills = root / "skills"
    spec = importlib.util.spec_from_file_location("installer", root / "scripts/install_skills.py")
    installer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installer)
    try:
        installer.check_links(skills)
    except ValueError as error:
        errors.append(str(error))
    for name in installer.NAMES:
        entry = skills / name / "SKILL.md"
        if not entry.exists():
            continue
        text = entry.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        if not match:
            errors.append(f"Missing frontmatter: {name}")
        else:
            if f"name: {name}" not in match[1] or not re.search(
                r"^description: \S", match[1], re.M
            ):
                errors.append(f"Invalid name or description: {name}")
        if "[TODO" in text or "TODO:" in text:
            errors.append(f"Unfinished scaffold: {name}")
        ui = skills / name / "agents/openai.yaml"
        if not ui.is_file():
            errors.append(f"Missing UI metadata: {name}")
    refs = skills / "jacs-shared/references"
    records = jsonl(refs / "corpus-manifest.jsonl")
    manifest = {row["paper_id"]: row for row in records}
    if len(manifest) != len(records) or len({x["doi"].casefold() for x in records}) != len(records):
        errors.append("Duplicate paper ID or DOI in corpus")
    if any(x["journal"] != "Journal of the American Chemical Society" for x in records):
        errors.append("A non-JACS article is in the JACS manifest")
    split = json.loads((root / "evaluation/split.json").read_text(encoding="utf-8"))
    for label in ("development", "holdout"):
        actual = sorted(x["paper_id"] for x in records if x["split"] == label)
        if actual != sorted(split[label]):
            errors.append(f"Frozen split disagrees with manifest: {label}")
    annotation_list = jsonl(refs / "pilot-annotations.jsonl")
    annotations = {row["annotation_id"]: row for row in annotation_list}
    if len(annotations) != len(annotation_list):
        errors.append("Duplicate annotation ID")
    blocks = {}
    if source_blocks is not None:
        for path in source_blocks.glob("*.jsonl"):
            blocks.update({x["block_id"]: x for x in jsonl(path)})
    for annotation in annotation_list:
        paper = manifest.get(annotation["paper_id"])
        if not paper or paper["split"] != "development":
            errors.append(f"Annotation leaks non-development source: {annotation['annotation_id']}")
            continue
        if (
            annotation["doi"] != paper["doi"]
            or annotation["source_sha256"] != paper["acquisition"]["source_sha256"]
        ):
            errors.append(f"Annotation provenance mismatch: {annotation['annotation_id']}")
        if not annotation["locator"] or not re.fullmatch(
            r"[a-f0-9]{64}", annotation["text_sha256"]
        ):
            errors.append(f"Annotation has invalid locator/digest: {annotation['annotation_id']}")
        if source_blocks is not None:
            block = blocks.get(annotation["block_id"])
            if not block:
                errors.append(f"Missing source block: {annotation['block_id']}")
            elif (
                block["locator"] != annotation["locator"]
                or hashlib.sha256(block["text"].encode()).hexdigest() != annotation["text_sha256"]
            ):
                errors.append(f"Source block mismatch: {annotation['block_id']}")
    rules = jsonl(refs / "style-rules.jsonl")
    if len({x["rule_id"] for x in rules}) != len(rules):
        errors.append("Duplicate rule ID")
    for rule in rules:
        if rule["rule_type"] == "corpus_observation" and not rule["supporting_annotations"]:
            errors.append(f"Unsubstantiated observation: {rule['rule_id']}")
        for ref in rule["supporting_annotations"] + rule["counterexamples"]:
            if ref not in annotations:
                errors.append(f"Unknown rule evidence: {rule['rule_id']}: {ref}")
    stats = json.loads((refs / "pilot-statistics.json").read_text(encoding="utf-8"))
    if stats["split"] != "development" or any(
        manifest[x]["split"] != "development" for x in stats["paper_ids"]
    ):
        errors.append("Pilot statistics contain non-development papers")
    if stats["paper_count"] != len(stats["paper_ids"]):
        errors.append("Pilot statistics paper count mismatch")
    if stats["word_count"] != sum(x["words"] for x in stats["sections"]):
        errors.append("Pilot statistics word count mismatch")
    files = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    for name in files:
        path = root / name
        if name.startswith(("local/", ".venv/")) or path.suffix.lower() in {
            ".pdf",
            ".xyz",
            ".ckpt",
            ".pkl",
            ".pt",
            ".docx",
        }:
            errors.append(f"Private/raw/binary artifact in publication set: {name}")
        if path.suffix in {".md", ".json", ".jsonl", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            if "/mnt/sto3/" in text or "/home/caoxiangyu/" in text:
                errors.append(f"Machine-specific private path in publication: {name}")
    return {
        "skills": len(installer.NAMES),
        "papers": len(records),
        "pilot_papers": stats["paper_count"],
        "annotations": len(annotations),
        "rules": len(rules),
        "source_blocks_checked": source_blocks is not None,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-blocks", type=Path)
    args = parser.parse_args()
    report = validate(source_blocks=args.source_blocks)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(report["errors"])


if __name__ == "__main__":
    raise SystemExit(main())
