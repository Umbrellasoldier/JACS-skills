#!/usr/bin/env python3
"""Rebuild public pilot notes/statistics from local source snapshots and authored annotations."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jacs_corpus", ROOT / "skills/jacs-style-distill/scripts/corpus.py"
)
corpus = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(corpus)


def rebuild(raw_dir: Path, output_dir: Path) -> dict:
    manifest = corpus.manifest_rows(ROOT / "skills/jacs-shared/references/corpus-manifest.jsonl")
    spec = json.loads((ROOT / "corpus/annotation-spec.json").read_text(encoding="utf-8"))
    mappings = json.loads((ROOT / "corpus/section-overrides.json").read_text(encoding="utf-8"))
    paper_ids = sorted({item[1].split(":")[0] for item in spec["annotations"]})
    blocks = {}
    for paper_id in paper_ids:
        paper = manifest[paper_id]
        if paper["split"] != "development":
            raise ValueError(f"Pilot annotation points to a non-development paper: {paper_id}")
        data = (raw_dir / (paper_id + ".bioc.json")).read_bytes()
        if corpus.digest(data) != paper["acquisition"]["source_sha256"]:
            raise ValueError(
                f"Source snapshot hash mismatch for {paper_id}; review the new version"
            )
        rows, _ = corpus.ingest(
            data,
            "bioc",
            paper,
            paper["acquisition"]["source_url"],
            overrides=mappings.get(paper_id),
        )
        blocks.update({row["block_id"]: row for row in rows})
    annotations = []
    for annotation_id, block_id, moves, observation in spec["annotations"]:
        block = blocks[block_id]
        annotations.append(
            {
                "annotation_id": annotation_id,
                **{
                    key: block[key]
                    for key in [
                        "paper_id",
                        "doi",
                        "block_id",
                        "locator",
                        "source_sha256",
                        "text_sha256",
                        "section",
                        "section_original",
                        "source_url",
                        "source_version",
                    ]
                },
                "rhetorical_moves": moves,
                "observation": observation,
                "review_status": spec["review_status"],
                "reviewed_on": spec["reviewed_on"],
                "review_method": spec["review_method"],
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "pilot-annotations.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in annotations), encoding="utf-8"
    )
    report = corpus.statistics(list(blocks.values()), manifest)
    corpus.write_json(output_dir / "pilot-statistics.json", report)
    return {
        "papers": len(paper_ids),
        "annotations": len(annotations),
        "words": report["word_count"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(rebuild(args.raw_dir, args.output_dir)))


if __name__ == "__main__":
    main()
