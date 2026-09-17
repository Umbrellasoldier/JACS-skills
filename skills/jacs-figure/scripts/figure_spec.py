"""Validate figure data before importing plotting packages. No inferred measurements."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

KINDS = {"energy", "parity", "stages", "comparison", "workflow", "structures", "assembly"}
PROFILES = {
    "single": (240.0, 180.0),
    "double": (504.0, 240.0),
    "si": (504.0, 300.0),
    "toc": (234.0, 126.0),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field}: booleans are not measurements")
    try:
        result = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{field}: a finite number is required") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field}: a finite number is required")
    return result


def required(obj: dict, fields: tuple[str, ...]) -> None:
    for field in fields:
        if field not in obj or obj[field] is None or obj[field] == "":
            raise ValueError(f"Missing required field: {field}")


def same_metadata(spec: dict, rows: list[dict], fields: tuple[str, ...]) -> None:
    required(spec, fields)
    for row in rows:
        for field in fields:
            if field in row and row[field] != spec[field]:
                raise ValueError(f"Mixed {field}; explicitly reconcile before plotting")


def matched_rows(rows: list[dict], field: str) -> None:
    groups = defaultdict(set)
    for row in rows:
        required(row, ("reaction_id", "method", field))
        key = str(row["reaction_id"])
        row["reaction_id"] = key
        if key in groups[row["method"]]:
            raise ValueError("Duplicate reaction_id within method; define the replicate unit")
        groups[row["method"]].add(key)
        row[field] = number(row[field], field)
    if any(ids != next(iter(groups.values())) for ids in groups.values()):
        raise ValueError(
            "Methods have different reaction sets; supply a declared matched population"
        )


def validate(spec: dict) -> dict:
    spec = copy.deepcopy(spec)
    required(spec, ("kind", "data_status", "claim", "caption"))
    if spec["kind"] not in KINDS:
        raise ValueError(f"Unknown figure kind: {spec['kind']}")
    if spec["data_status"] not in {"real", "synthetic"}:
        raise ValueError("data_status must be real or synthetic")
    profile = spec.setdefault("profile", "single")
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    default_width, default_height = PROFILES[profile]
    width = number(spec.setdefault("width_pt", default_width), "width_pt")
    height = number(spec.setdefault("height_pt", default_height), "height_pt")
    if width <= 0 or height <= 0:
        raise ValueError("Figure dimensions must be positive")
    if profile == "single" and width > 240:
        raise ValueError("Single-column width exceeds 240 pt")
    if profile == "double" and not 300 <= width <= 504:
        raise ValueError("Double-column width must be 300–504 pt")
    if profile in {"single", "double"} and height >= 660:
        raise ValueError("Reserve room below the 660 pt total height for the caption")
    if profile == "toc" and (width > 234 or height > 126):
        raise ValueError("TOC must fit within 234 × 126 pt")
    if profile == "toc" and spec["kind"] not in {"workflow", "structures", "assembly"}:
        raise ValueError("TOC templates summarize a concept; use workflow, structures or assembly")
    spec["width_pt"], spec["height_pt"] = width, height
    raster_class = spec.setdefault("raster_class", "line_art")
    if raster_class not in {"color", "grayscale", "line_art"}:
        raise ValueError("raster_class must be color, grayscale or line_art")
    rows = spec.get("data", [])
    if not isinstance(rows, list) or (not rows and spec["kind"] != "assembly"):
        raise ValueError("A nonempty data list is required")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("Each data record must be an object")
    kind = spec["kind"]
    if kind == "energy":
        same_metadata(spec, rows, ("quantity", "unit", "reference", "conditions"))
        if spec["quantity"] not in {"E", "H", "G"}:
            raise ValueError("Energy quantity must be E, H or G")
        if spec["unit"] not in {"kcal/mol", "kJ/mol", "eV", "hartree"}:
            raise ValueError("Declare a supported energy unit without implicit conversion")
        seen = set()
        for row in rows:
            required(row, ("path", "state", "order", "energy"))
            row["order"] = number(row["order"], "order")
            row["energy"] = number(row["energy"], "energy")
            key = (row["path"], row["order"])
            if key in seen:
                raise ValueError("Duplicate state order within energy path")
            seen.add(key)
    elif kind == "parity":
        same_metadata(spec, rows, ("quantity", "unit", "reference", "conditions"))
        matched_rows(rows, "predicted")
        references = {}
        for row in rows:
            row["reference_value"] = number(row.get("reference_value"), "reference_value")
            key = str(row["reaction_id"])
            if key in references and references[key] != row["reference_value"]:
                raise ValueError("Reference values differ between methods for the same reaction")
            references[key] = row["reference_value"]
    elif kind == "comparison":
        same_metadata(spec, rows, ("metric", "unit", "population"))
        matched_rows(rows, "value")
    elif kind == "stages":
        same_metadata(spec, rows, ("unit_of_analysis",))
        required(spec, ("population", "population_total"))
        previous = number(spec["population_total"], "population_total")
        if previous <= 0 or not previous.is_integer():
            raise ValueError("population_total must be a positive integer")
        spec["population_total"] = int(previous)
        stages = set()
        for row in rows:
            required(row, ("stage", "passed", "failed", "pending"))
            if row["stage"] in stages:
                raise ValueError("Duplicate stage label")
            stages.add(row["stage"])
            if "entered" in row and number(row["entered"], "entered") != previous:
                raise ValueError("Declared entered count disagrees with the preceding population")
            row["entered"] = int(previous)
            for field in ("passed", "failed", "pending"):
                n = number(row[field], field)
                if n < 0 or not n.is_integer():
                    raise ValueError("Stage counts must be nonnegative integers")
                row[field] = int(n)
            if sum(row[f] for f in ("passed", "failed", "pending")) != previous:
                raise ValueError("passed + failed + pending must equal the preceding population")
            row["conditional_rate"] = row["passed"] / previous if previous else None
            row["overall_rate"] = row["passed"] / spec["population_total"]
            previous = row["passed"]
    elif kind == "workflow":
        ids = []
        for row in rows:
            required(row, ("id", "label"))
            ids.append(row["id"])
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate workflow node ID")
        for edge in spec.get("edges", []):
            if len(edge) != 2 or any(node not in ids for node in edge):
                raise ValueError("Workflow edges must reference two existing node IDs")
    elif kind == "structures":
        for row in rows:
            required(row, ("id", "label"))
            if ("smiles" in row) == ("svg" in row):
                raise ValueError("Each structure needs exactly one SMILES or supplied SVG")
            if "svg" in row:
                required(row, ("source",))
        if len({row["id"] for row in rows}) != len(rows):
            raise ValueError("Duplicate structure ID")
    elif kind == "assembly":
        panels = spec.get("panels", [])
        if not panels:
            raise ValueError("Assembly needs panels")
        labels = []
        for panel in panels:
            required(panel, ("label", "svg"))
            labels.append(panel["label"])
        if len(set(labels)) != len(labels):
            raise ValueError("Duplicate panel label")
    scale = spec.setdefault("scale", "linear")
    if scale not in {"linear", "log"}:
        raise ValueError("Only declared linear or log scales are supported")
    if scale == "log":
        if kind not in {"parity", "comparison"}:
            raise ValueError("Log scale is supported only for parity and comparison")
        fields = ("reference_value", "predicted") if kind == "parity" else ("value",)
        if any(row[field] <= 0 for row in rows for field in fields):
            raise ValueError("Log scale requires positive values; no implicit filtering or offset")
    categories = list(dict.fromkeys(row.get("method", row.get("path")) for row in rows))
    if kind in {"energy", "parity", "comparison"} and len(categories) > 6:
        raise ValueError("More than six series: split the figure or write an explicit encoding")
    return spec


def load(path: Path) -> tuple[dict, dict]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    provenance = {"spec_sha256": digest(path), "sources": []}
    if "input_csv" in spec:
        if "data" in spec:
            raise ValueError("Use data or input_csv, not both")
        data_path = path.parent / spec["input_csv"]
        with data_path.open(encoding="utf-8-sig", newline="") as file:
            spec["data"] = list(csv.DictReader(file))
        provenance["sources"].append({"name": data_path.name, "sha256": digest(data_path)})
    validated = validate(spec)
    provenance["input_records"] = len(spec.get("data", []))
    provenance["excluded_records"] = 0
    provenance["data_sha256"] = hashlib.sha256(
        json.dumps(spec.get("data", []), sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    return validated, provenance
