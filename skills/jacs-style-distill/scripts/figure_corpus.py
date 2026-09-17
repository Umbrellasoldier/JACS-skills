#!/usr/bin/env python3
"""Acquire versioned figure assets from the current public PMC Article Dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import urlopen

BUCKET = "https://pmc-oa-opendata.s3.amazonaws.com/"
XLINK = "{http://www.w3.org/1999/xlink}href"


def get(url: str) -> bytes:
    with urlopen(url, timeout=30) as response:
        return response.read()


def https_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme == "s3" and parsed.netloc == "pmc-oa-opendata":
        return BUCKET.rstrip("/") + parsed.path + ("?" + parsed.query if parsed.query else "")
    if parsed.scheme == "https" and parsed.netloc == "pmc-oa-opendata.s3.amazonaws.com":
        return url
    raise ValueError("Expected an object in the public PMC dataset bucket")


def verify_download(data: bytes, url: str) -> str:
    expected = parse_qs(urlsplit(url).query).get("md5", [])
    if expected and hashlib.md5(data).hexdigest() != expected[0]:
        raise ValueError("PMC object MD5 does not match its version metadata")
    return hashlib.sha256(data).hexdigest()


def discover(pmcid: str) -> list[str]:
    if not re.fullmatch(r"PMC\d+", pmcid):
        raise ValueError("Use a complete PMCID")
    params = {"list-type": "2", "prefix": pmcid + ".", "delimiter": "/"}
    versions = []
    while True:
        root = ET.fromstring(get(BUCKET + "?" + urlencode(params)))
        versions.extend(x.text.rstrip("/") for x in root.findall(".//{*}CommonPrefixes/{*}Prefix"))
        token = root.findtext("{*}NextContinuationToken")
        if not token:
            return sorted(versions)
        params["continuation-token"] = token


def figure_nodes(root: ET.Element) -> list[dict]:
    result = []
    for node in root.iter():
        if node.tag not in {"fig", "chem-struct-wrap"}:
            continue
        label = " ".join(node.findtext("label", default="").split())
        caption = (
            " ".join(" ".join(node.find("caption").itertext()).split())
            if (node.find("caption") is not None)
            else ""
        )
        graphics = [
            g.get(XLINK)
            for g in node.findall(".//graphic")
            if g.get("content-type") != "thumb" and g.get(XLINK)
        ]
        if graphics:
            result.append(
                {
                    "figure_id": node.get("id"),
                    "label": label,
                    "caption": caption,
                    "graphics": graphics,
                }
            )
    return result


def fetch(pmcid: str, version: int, doi: str, paper_id: str, split: str, output: Path) -> dict:
    if not re.fullmatch(r"PMC\d+", pmcid) or version < 1:
        raise ValueError("Invalid article version")
    prefix = f"{pmcid}.{version}"
    metadata_url = f"{BUCKET}{prefix}/{prefix}.json"
    metadata_bytes = get(metadata_url)
    metadata = json.loads(metadata_bytes)
    if metadata.get("doi", "").casefold() != doi.casefold() or metadata.get("pmcid") != pmcid:
        raise ValueError("Article metadata identity mismatch")
    if metadata.get("is_retracted"):
        raise ValueError("Retracted source: choose a different style source")
    xml_url = https_url(metadata["xml_url"])
    if not urlsplit(xml_url).path.startswith(f"/{prefix}/"):
        raise ValueError("JATS object belongs to a different article version")
    xml_data = get(xml_url)
    xml_hash = verify_download(xml_data, xml_url)
    root = ET.fromstring(xml_data)
    journal = root.findtext(".//journal-title")
    if journal != "Journal of the American Chemical Society":
        raise ValueError(f"Not JACS: {journal}")
    xml_dois = [x.text for x in root.findall(".//article-meta/article-id[@pub-id-type='doi']")]
    if doi.casefold() not in [x.casefold() for x in xml_dois if x]:
        raise ValueError("JATS DOI does not match the requested article")
    output.mkdir(parents=True, exist_ok=True)
    (output / "metadata.json").write_bytes(metadata_bytes)
    (output / "article.xml").write_bytes(xml_data)
    media = {}
    for raw in metadata.get("media_urls", []):
        url = https_url(raw)
        if not urlsplit(url).path.startswith(f"/{prefix}/"):
            raise ValueError("Media object belongs to a different article version")
        name = Path(urlsplit(url).path).name
        media[name] = url
        media.setdefault(Path(name).stem, url)
    assets = []
    for figure in figure_nodes(root):
        for graphic in figure["graphics"]:
            name = Path(graphic).name
            url = media.get(name, media.get(Path(name).stem))
            record = {**figure, "graphic": graphic, "status": "unavailable"}
            if url and Path(urlsplit(url).path).suffix.lower() in {
                ".jpg",
                ".jpeg",
                ".png",
                ".tif",
                ".tiff",
            }:
                data = get(url)
                sha = verify_download(data, url)
                filename = Path(urlsplit(url).path).name
                (output / filename).write_bytes(data)
                record.update(
                    status="downloaded_not_reviewed",
                    filename=filename,
                    source_url=url,
                    source_sha256=sha,
                )
            assets.append(record)
    index = {
        "paper_id": paper_id,
        "doi": doi,
        "pmcid": pmcid,
        "version": version,
        "journal": journal,
        "split": split,
        "source_version": "author_manuscript"
        if metadata.get("is_manuscript")
        else "pmc_publisher_version",
        "license_code": metadata.get("license_code"),
        "metadata_url": metadata_url,
        "xml_url": xml_url,
        "xml_sha256": xml_hash,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "visual_review_status": "not_reviewed",
        "figures": assets,
    }
    (output / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    discover_parser = sub.add_parser("discover")
    discover_parser.add_argument("--pmcid", required=True)
    fetch_parser = sub.add_parser("fetch")
    fetch_parser.add_argument("--pmcid", required=True)
    fetch_parser.add_argument("--version", type=int, required=True)
    fetch_parser.add_argument("--doi", required=True)
    fetch_parser.add_argument("--paper-id", required=True)
    fetch_parser.add_argument(
        "--split", choices=["development", "holdout", "communication", "background"], required=True
    )
    fetch_parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "discover":
            result = {"versions": discover(args.pmcid)}
        else:
            index = fetch(
                args.pmcid, args.version, args.doi, args.paper_id, args.split, args.output_dir
            )
            result = {
                "paper_id": index["paper_id"],
                "figures": len({x["figure_id"] for x in index["figures"]}),
                "assets": len(index["figures"]),
                "available_assets": sum(
                    x["status"] == "downloaded_not_reviewed" for x in index["figures"]
                ),
                "review_status": "not_reviewed",
            }
    except (OSError, ValueError, ET.ParseError) as error:
        parser.exit(2, f"error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
