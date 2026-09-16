#!/usr/bin/env python3
"""Traceable local corpus import and descriptive statistics. Runtime: Python stdlib."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SECTIONS = {
    "title",
    "abstract",
    "introduction",
    "results_discussion",
    "results",
    "discussion",
    "conclusion",
    "methods",
    "theory",
    "body",
    "captions",
    "tables",
    "back_matter",
    "other",
}
KINDS = {"paragraph", "heading", "caption", "table", "other"}
PROSE_SECTIONS = {
    "abstract",
    "introduction",
    "results_discussion",
    "results",
    "discussion",
    "conclusion",
    "theory",
    "body",
}
CONNECTORS = ("however", "therefore", "furthermore", "moreover", "nevertheless", "thus")
WORD = re.compile(r"[^\W_]+(?:[’'-][^\W_]+)*", re.UNICODE)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_doi(value: str) -> str:
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I).casefold()
    if not re.fullmatch(r"10\.\d{4,9}/\S+", value):
        raise ValueError(f"Invalid DOI syntax: {value!r}")
    return value


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path.name}:{number}: expected an object")
            rows.append(row)
    return rows


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def manifest_rows(path: Path) -> dict[str, dict]:
    rows = {}
    dois = set()
    for row in read_jsonl(path):
        key, doi = row["paper_id"], normalize_doi(row["doi"])
        if key in rows or doi in dois:
            raise ValueError(f"Duplicate paper or DOI in manifest: {key}")
        if row["journal"] != "Journal of the American Chemical Society":
            raise ValueError(f"Not a JACS record: {key}")
        if row["split"] not in {"development", "holdout", "communication", "background"}:
            raise ValueError(f"Unrecognized split for {key}")
        rows[key] = {**row, "doi": doi}
        dois.add(doi)
    return rows


def heading_section(title: str, overrides: dict | None = None) -> str:
    if overrides and title in overrides:
        section = overrides[title]
        if section not in SECTIONS:
            raise ValueError(f"Invalid section override: {section}")
        return section
    title = re.sub(r"^[\d.\s]+", "", title).casefold().strip()
    if "result" in title and "discussion" in title:
        return "results_discussion"
    if title.startswith("intro") or title == "background":
        return "introduction"
    if title.startswith(("conclusion", "concluding")):
        return "conclusion"
    if title == "results":
        return "results"
    if title == "discussion":
        return "discussion"
    if title.startswith(("experimental", "computational method", "methods", "materials and")):
        return "methods"
    if title.startswith(("supporting", "supplement", "reference", "acknowledg", "author")):
        return "back_matter"
    return "body"


def check_identity(observed: str | None, expected: str, asserted: str | None = None) -> str:
    if observed:
        if normalize_doi(observed) != normalize_doi(expected):
            raise ValueError("Source DOI does not match the manifest")
        return "source_doi_verified"
    if asserted and normalize_doi(asserted) == normalize_doi(expected):
        return "user_asserted_doi"
    raise ValueError("Source DOI absent; verify the document and provide --source-doi explicitly")


def parse_bioc(data: bytes, overrides: dict | None = None) -> tuple[list[dict], dict]:
    collections = json.loads(data)
    if isinstance(collections, dict):
        collections = [collections]
    documents = [doc for coll in collections for doc in coll.get("documents", [])]
    if len(documents) != 1:
        raise ValueError("Import exactly one BioC article at a time")
    doc = documents[0]
    passages = doc.get("passages", [])
    front = [p for p in passages if p.get("infons", {}).get("section_type") == "TITLE"]
    meta = front[0].get("infons", {}) if front else {}
    info = {
        "doi": meta.get("article-id_doi"),
        "source_version": "author_manuscript"
        if meta.get("article-id_manuscript")
        or doc.get("infons", {}).get("license") == "author_manuscript"
        else "pmc_article",
        "license_statement": meta.get("license", doc.get("infons", {}).get("license")),
        "document_id": doc.get("id"),
    }
    rows = []
    top_heading, current_heading, section = "", "", "other"
    for index, passage in enumerate(passages):
        infons = passage.get("infons", {})
        kind, code = infons.get("type", ""), infons.get("section_type", "")
        text = passage.get("text", "")
        if not text.strip():
            continue
        block_kind, block_section = "other", "other"
        if code == "TITLE":
            block_kind, block_section = "heading", "title"
        elif code == "FIG":
            block_kind, block_section = "caption", "captions"
        elif code == "TABLE":
            block_kind = "table" if kind == "table" else "caption"
            block_section = "tables"
        elif code == "ABSTRACT":
            block_kind = "paragraph" if kind == "abstract" else "heading"
            block_section = "abstract"
        elif code in {"REF", "SUPPL", "AUTH_CONT", "ACK_FUND", "COMP_INT"}:
            block_section = "back_matter"
        elif kind.startswith("title_"):
            level = kind.split("_")[-1]
            current_heading = text.strip()
            if level == "1":
                top_heading = current_heading
                section = heading_section(top_heading, overrides)
            block_kind, block_section = "heading", section
        elif kind == "paragraph":
            block_kind, block_section = "paragraph", section
        rows.append(
            {
                "locator": f"BioC:{doc.get('id')}:passage[{index}]:offset={passage.get('offset')}",
                "section_original": current_heading or code,
                "section_parent": top_heading,
                "section_source_tag": code,
                "section": block_section,
                "kind": block_kind,
                "text": text,
            }
        )
    return rows, info


def parse_jats(data: bytes, overrides: dict | None = None) -> tuple[list[dict], dict]:
    root = ET.fromstring(data)
    for node in root.iter():
        node.tag = node.tag.rsplit("}", 1)[-1]
    if root.tag != "article":
        raise ValueError("Expected JATS article XML, not a service error or HTML page")
    ids = {x.get("pub-id-type"): x.text for x in root.findall("./front/article-meta/article-id")}

    def txt(node: ET.Element) -> str:
        return "".join(node.itertext()).strip()

    info = {
        "doi": ids.get("doi"),
        "source_version": "author_manuscript" if ids.get("manuscript") else "jats_article",
        "license_statement": " ".join(txt(x) for x in root.findall(".//permissions/license")),
        "document_id": ids.get("pmc"),
    }
    rows = []

    def add(node: ET.Element, path: str, section: str, original: str, kind: str) -> None:
        if txt(node):
            rows.append(
                {
                    "locator": "JATS:/article/" + path,
                    "section_original": original,
                    "section": section,
                    "kind": kind,
                    "text": txt(node),
                }
            )

    for index, node in enumerate(root.findall("./front/article-meta/title-group/article-title")):
        add(
            node,
            f"front/article-meta/title-group/article-title[{index + 1}]",
            "title",
            "Title",
            "heading",
        )

    def abstract_paragraphs(node: ET.Element, path: str) -> None:
        counts: Counter = Counter()
        for child in node:
            counts[child.tag] += 1
            child_path = f"{path}/{child.tag}[{counts[child.tag]}]"
            if child.tag == "p":
                add(child, child_path, "abstract", "Abstract", "paragraph")
            else:
                abstract_paragraphs(child, child_path)

    for index, abstract in enumerate(root.findall("./front/article-meta/abstract")):
        paragraphs = list(abstract.iter("p"))
        if paragraphs:
            abstract_paragraphs(abstract, f"front/article-meta/abstract[{index + 1}]")
        else:
            add(
                abstract,
                f"front/article-meta/abstract[{index + 1}]",
                "abstract",
                "Abstract",
                "paragraph",
            )

    def walk(node: ET.Element, path: str, section: str, original: str, depth: int) -> None:
        counts: Counter = Counter()
        for child in node:
            counts[child.tag] += 1
            child_path = f"{path}/{child.tag}[{counts[child.tag]}]"
            if child.tag == "sec":
                title = child.find("title")
                heading = txt(title) if title is not None else original
                sub_section = heading_section(heading, overrides) if depth == 0 else section
                walk(child, child_path, sub_section, heading, depth + 1)
            elif child.tag == "p":
                add(child, child_path, section, original, "paragraph")
            elif child.tag == "title":
                add(child, child_path, section, original, "heading")
            elif child.tag == "fig":
                add(child, child_path, "captions", original, "caption")
            elif child.tag == "table-wrap":
                add(child, child_path, "tables", original, "table")
            elif child.tag in {"boxed-text", "disp-quote", "list", "list-item"}:
                walk(child, child_path, section, original, depth)

    body = root.find("body")
    if body is not None:
        walk(body, "body", "body", "Body", 0)
    return rows, info


def ingest(
    data: bytes,
    fmt: str,
    paper: dict,
    source_url: str,
    asserted: str | None = None,
    overrides: dict | None = None,
) -> tuple[list[dict], dict]:
    if fmt == "bioc":
        passages, info = parse_bioc(data, overrides)
    elif fmt == "jats":
        passages, info = parse_jats(data, overrides)
    else:
        passages = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
        info = {"doi": None, "source_version": "user_supplied_blocks"}
    status = check_identity(info.get("doi"), paper["doi"], asserted)
    rows, locators = [], set()
    for index, passage in enumerate(passages, 1):
        if passage.get("section") not in SECTIONS or passage.get("kind") not in KINDS:
            raise ValueError("Passage has an invalid section or kind")
        if not passage.get("locator") or passage["locator"] in locators:
            raise ValueError("Passage locator is absent or duplicated")
        if not isinstance(passage.get("text"), str) or not passage["text"].strip():
            raise ValueError("Passage text is empty")
        if not isinstance(passage.get("section_original"), str):
            raise ValueError("Original section label is required")
        locators.add(passage["locator"])
        rows.append(
            {
                **passage,
                "paper_id": paper["paper_id"],
                "doi": normalize_doi(paper["doi"]),
                "block_id": f"{paper['paper_id']}:p{index:04d}",
                "source_url": source_url,
                "source_sha256": digest(data),
                "source_version": info["source_version"],
                "identity_status": status,
                "text_sha256": digest(passage["text"].encode("utf-8")),
            }
        )
    if not rows:
        raise ValueError("Source has no usable passages")
    return rows, {
        **info,
        "identity_status": status,
        "source_sha256": digest(data),
        "block_count": len(rows),
        "sections": sorted({r["section"] for r in rows}),
    }


def request_bytes(url: str, timeout: int = 25) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "JACS-skills/0.1 corpus-tools"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read(20_000_001)
    if len(data) > 20_000_000:
        raise ValueError("Source exceeds the 20 MB structured-text limit")
    return data


def fetch(paper: dict, output_dir: Path) -> dict:
    pmcid = paper.get("pmcid") or ""
    if not re.fullmatch(r"PMC\d+", pmcid):
        raise ValueError("No valid PMCID; obtain publisher or author text and use ingest")
    report_path = output_dir / "acquisition.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        existing = output_dir / report["filename"]
        if (
            normalize_doi(report["doi"]) == normalize_doi(paper["doi"])
            and existing.is_file()
            and digest(existing.read_bytes()) == report["source_sha256"]
        ):
            return {**report, "cache_reused": True}
        raise ValueError(
            "Existing acquisition conflicts with the requested source; use a new directory"
        )
    candidates = [
        (
            f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmcid}/unicode",
            "bioc",
            "source.json",
        ),
        (
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML",
            "jats",
            "source.xml",
        ),
    ]
    if any((output_dir / filename).exists() for _, _, filename in candidates):
        raise ValueError("Source output already exists without a verified acquisition record")
    attempts = []
    for url, fmt, filename in candidates:
        try:
            data = request_bytes(url)
            _, info = ingest(data, fmt, paper, url)
            report = {
                **info,
                "paper_id": paper["paper_id"],
                "doi": paper["doi"],
                "source_url": url,
                "format": fmt,
                "filename": filename,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "attempts": attempts,
            }
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / filename).write_bytes(data)
            write_json(report_path, report)
            return report
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
            attempts.append({"url": url, "error": str(error)})
    raise ValueError("Full text unavailable: " + json.dumps(attempts))


def statistics(rows: list[dict], manifest: dict[str, dict], split: str = "development") -> dict:
    seen_blocks, seen_dois = set(), {}
    groups: dict = defaultdict(
        lambda: {"paragraphs": 0, "words": 0, "sentence_estimate": 0, "connectors": Counter()}
    )
    excluded: Counter = Counter()
    for row in rows:
        paper = manifest[row["paper_id"]]
        if normalize_doi(row["doi"]) != paper["doi"]:
            raise ValueError("Block DOI disagrees with manifest")
        if digest(row["text"].encode("utf-8")) != row["text_sha256"]:
            raise ValueError("Block text digest mismatch; re-import the source")
        if paper["split"] != split:
            excluded["different_split"] += 1
            continue
        key = row["block_id"]
        if key in seen_blocks:
            raise ValueError(f"Duplicate block: {key}")
        seen_blocks.add(key)
        previous = seen_dois.setdefault(row["doi"], row["source_sha256"])
        if previous != row["source_sha256"]:
            raise ValueError("Multiple source versions for one DOI; select one version")
        if row["kind"] != "paragraph" or row["section"] not in PROSE_SECTIONS:
            excluded["non_main_prose"] += 1
            continue
        words = [x.casefold() for x in WORD.findall(row["text"])]
        item = groups[(row["paper_id"], row["section"])]
        item["paragraphs"] += 1
        item["words"] += len(words)
        item["sentence_estimate"] += max(1, len(re.split(r"(?<=[.!?])\s+(?=[A-Z])", row["text"])))
        item["connectors"].update(x for x in words if x in CONNECTORS)
    paper_counts: dict = defaultdict(Counter)
    for (pid, _), values in groups.items():
        paper_counts[pid].update(values["connectors"])
    total_words = sum(v["words"] for v in groups.values())
    totals = Counter()
    for count in paper_counts.values():
        totals.update(count)
    return {
        "split": split,
        "paper_count": len(paper_counts),
        "paper_ids": sorted(paper_counts),
        "word_count": total_words,
        "excluded_blocks": dict(excluded),
        "method": "Unicode word tokens with internal apostrophes/hyphens; sentence counts are "
        "punctuation estimates. Connectors counted anywhere, case-insensitively. "
        "Main prose includes abstract and theory; excludes headings, methods, captions, "
        "tables, back matter and other splits. Not rhetorical annotation.",
        "sections": [
            {"paper_id": pid, "section": sec, **values}
            for (pid, sec), values in sorted(groups.items())
        ],
        "connectors": {
            term: {
                "count": totals[term],
                "per_1000_words": round(totals[term] / total_words * 1000, 4) if total_words else 0,
                "papers_with_term": sum(c[term] > 0 for c in paper_counts.values()),
            }
            for term in CONNECTORS
        },
    }


def verify(doi: str, title: str | None = None) -> dict:
    doi = normalize_doi(doi)
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    try:
        row = json.loads(request_bytes(url))["message"]
    except (OSError, ValueError, KeyError) as error:
        return {
            "doi": doi,
            "status": "unresolved",
            "source": url,
            "reason": str(error),
            "next_step": "Check publisher or another DOI registry; do not infer fabrication.",
        }
    returned_title = (row.get("title") or [""])[0]
    match = normalize_doi(row["DOI"]) == doi

    def normalized(value: str) -> str:
        return " ".join(WORD.findall(value.casefold()))

    title_match = normalized(title) == normalized(returned_title) if title else None
    return {
        "doi": doi,
        "status": "metadata_match" if match and title_match is not False else "needs_review",
        "source": url,
        "title": returned_title,
        "title_exact_normalized_match": title_match,
        "journal": row.get("container-title", []),
        "fulltext_verified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("fetch", "ingest", "stats"):
        sub = commands.add_parser(name)
        sub.add_argument("--manifest", type=Path, required=True)
        if name != "stats":
            sub.add_argument("--paper-id", required=True)
        if name == "fetch":
            sub.add_argument("--output-dir", type=Path, required=True)
        else:
            sub.add_argument(
                "--input", type=Path, required=True, nargs="+" if name == "stats" else None
            )
            sub.add_argument("--output", type=Path, required=True)
        if name == "ingest":
            sub.add_argument("--format", choices=["bioc", "jats", "blocks"], required=True)
            sub.add_argument("--source-url", required=True)
            sub.add_argument("--source-doi")
            sub.add_argument("--section-map", type=Path)
        if name == "stats":
            sub.add_argument(
                "--split",
                choices=["development", "holdout", "communication", "background"],
                default="development",
            )
    sub = commands.add_parser("verify")
    sub.add_argument("--doi", required=True)
    sub.add_argument("--title")
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            print(json.dumps(verify(args.doi, args.title), ensure_ascii=False, indent=2))
            return 0
        manifest = manifest_rows(args.manifest)
        if args.command == "fetch":
            print(
                json.dumps(
                    fetch(manifest[args.paper_id], args.output_dir), ensure_ascii=False, indent=2
                )
            )
        elif args.command == "ingest":
            overrides = json.loads(args.section_map.read_text()) if args.section_map else None
            rows, report = ingest(
                args.input.read_bytes(),
                args.format,
                manifest[args.paper_id],
                args.source_url,
                args.source_doi,
                overrides,
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
            )
            write_json(args.output.with_suffix(".report.json"), report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            rows = [row for path in args.input for row in read_jsonl(path)]
            report = statistics(rows, manifest, args.split)
            write_json(args.output, report)
            print(json.dumps({k: report[k] for k in ["split", "paper_count", "word_count"]}))
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
