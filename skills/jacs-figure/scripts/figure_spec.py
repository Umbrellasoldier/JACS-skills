"""Validate figure data before importing plotting packages. No inferred measurements."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

KINDS = {
    "energy",
    "parity",
    "stages",
    "comparison",
    "workflow",
    "structures",
    "assembly",
    "distribution",
    "interval",
    "curve",
    "heatmap",
}
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


def ordered_levels(spec: dict, field: str) -> list:
    required(spec, (field,))
    levels = spec[field]
    if not isinstance(levels, list) or not levels or any(not isinstance(x, str) for x in levels):
        raise ValueError(f"{field} must be a nonempty list of labels")
    if len(set(levels)) != len(levels):
        raise ValueError(f"Duplicate labels in {field}")
    return levels


def validate_statistical(spec: dict, rows: list[dict]) -> None:
    kind = spec["kind"]
    if kind == "distribution":
        same_metadata(spec, rows, ("metric", "unit", "population", "unit_of_analysis"))
        mode = spec.setdefault("display", "box")
        if mode not in {"box", "violin", "ecdf", "histogram"}:
            raise ValueError("distribution display must be box, violin, ecdf or histogram")
        seen = set()
        for row in rows:
            required(row, ("observation_id", "group", "value"))
            key = (str(row["observation_id"]), row["group"])
            if key in seen:
                raise ValueError("Duplicate observation within group; define the replicate unit")
            seen.add(key)
            row["value"] = number(row["value"], "value")
        if mode == "violin":
            required(spec, ("bandwidth",))
            spec["bandwidth"] = number(spec["bandwidth"], "bandwidth")
            if spec["bandwidth"] <= 0:
                raise ValueError("Violin bandwidth factor must be positive")
        if mode == "histogram":
            required(spec, ("bin_edges",))
            edges = [number(v, "bin_edges") for v in spec["bin_edges"]]
            if len(edges) < 2 or any(a >= b for a, b in zip(edges, edges[1:], strict=False)):
                raise ValueError("Histogram bin edges must be strictly increasing")
            if any(not edges[0] <= row["value"] <= edges[-1] for row in rows):
                raise ValueError("Histogram bins would exclude observations")
            spec["bin_edges"] = edges
        groups = list(dict.fromkeys(row["group"] for row in rows))
        if "group_order" in spec:
            if set(ordered_levels(spec, "group_order")) != set(groups):
                raise ValueError("group_order must contain every observed group exactly once")
        else:
            spec["group_order"] = groups
    elif kind == "interval":
        same_metadata(spec, rows, ("metric", "unit", "population"))
        required(spec, ("interval_definition",))
        labels = []
        for row in rows:
            required(row, ("label", "estimate", "lower", "upper"))
            labels.append(row["label"])
            for key in ("estimate", "lower", "upper"):
                row[key] = number(row[key], key)
            if not row["lower"] <= row["estimate"] <= row["upper"]:
                raise ValueError("Interval must enclose the supplied estimate")
        if len(set(labels)) != len(labels):
            raise ValueError("Interval labels must be unique")
        if "reference_value" in spec:
            spec["reference_value"] = number(spec["reference_value"], "reference_value")
    elif kind == "curve":
        same_metadata(spec, rows, ("x_quantity", "x_unit", "y_quantity", "y_unit", "population"))
        groups = defaultdict(list)
        for row in rows:
            required(row, ("series", "x", "y"))
            row["x"], row["y"] = number(row["x"], "x"), number(row["y"], "y")
            groups[row["series"]].append(row)
            if "lower" in row or "upper" in row:
                required(spec, ("interval_definition",))
                required(row, ("lower", "upper"))
                row["lower"] = number(row["lower"], "lower")
                row["upper"] = number(row["upper"], "upper")
                if not row["lower"] <= row["y"] <= row["upper"]:
                    raise ValueError("Curve bounds must enclose y")
        roles = spec.setdefault("series_roles", {})
        if set(roles) - set(groups):
            raise ValueError("Unknown series in series_roles")
        for name, data in groups.items():
            roles.setdefault(name, "observed")
            if roles[name] not in {"observed", "model", "reference"}:
                raise ValueError("Series role must be observed, model or reference")
            if any(a["x"] >= b["x"] for a, b in zip(data, data[1:], strict=False)):
                raise ValueError("Curve x must increase within series; no silent reordering")
            if any("lower" in r for r in data) and not all("lower" in r for r in data):
                raise ValueError("Supply bounds for every point in a banded series")
        for axis, fields in (("x", ("x",)), ("y", ("y", "lower", "upper"))):
            scale = spec.setdefault(axis + "_scale", "linear")
            if scale not in {"linear", "log"}:
                raise ValueError("Curve scales must be linear or log")
            if scale == "log" and any(
                row[key] <= 0 for row in rows for key in fields if key in row
            ):
                raise ValueError("Log curve data and bounds must be positive")
        if spec["y_scale"] == "log" and spec.get("zero_reference", False):
            raise ValueError("A zero reference cannot be displayed on a logarithmic y axis")
    elif kind == "heatmap":
        same_metadata(spec, rows, ("quantity", "unit", "population"))
        row_order = ordered_levels(spec, "row_order")
        column_order = ordered_levels(spec, "column_order")
        seen = set()
        for row in rows:
            required(row, ("row", "column"))
            if "value" not in row:
                raise ValueError("Use an explicit null value for missing cells")
            key = (row["row"], row["column"])
            if key in seen or row["row"] not in row_order or row["column"] not in column_order:
                raise ValueError("Duplicate or unknown heatmap cell")
            seen.add(key)
            if row["value"] is not None:
                row["value"] = number(row["value"], "value")
        if len(seen) != len(row_order) * len(column_order):
            raise ValueError("Heatmap needs explicit observed or null entries for every cell")
        values = [r["value"] for r in rows if r["value"] is not None]
        if not values:
            raise ValueError("Heatmap needs at least one observed value")
        mode = spec.setdefault("color_scale", "sequential")
        if mode not in {"sequential", "diverging"}:
            raise ValueError("Use a sequential or diverging color scale")
        for key, default in (("vmin", min(values)), ("vmax", max(values))):
            spec[key] = number(spec.setdefault(key, default), key)
        if spec["vmin"] >= spec["vmax"]:
            raise ValueError("Heatmap color limits must span a nonzero range")
        if spec["vmin"] > min(values) or spec["vmax"] < max(values):
            raise ValueError("Color limits would clip observed values")
        if mode == "diverging":
            required(spec, ("center",))
            spec["center"] = number(spec["center"], "center")
            if not spec["vmin"] < spec["center"] < spec["vmax"]:
                raise ValueError("Diverging center must lie inside the color limits")
    count_key = {"distribution": "group", "curve": "series"}.get(kind)
    if count_key and len({r[count_key] for r in rows}) > 6:
        raise ValueError("More than six series: use facets or an explicit custom encoding")


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
    elif kind in {"distribution", "interval", "curve", "heatmap"}:
        validate_statistical(spec, rows)
    scale = spec.setdefault("scale", "linear")
    if scale not in {"linear", "log"}:
        raise ValueError("Only declared linear or log scales are supported")
    if scale == "log":
        if kind not in {"parity", "comparison", "distribution", "interval"}:
            raise ValueError("Use x_scale/y_scale for curves; generic log is unsupported here")
        if kind == "distribution" and spec["display"] not in {"box", "violin"}:
            raise ValueError("Histogram/ECDF log transforms need a custom declared encoding")
        fields = {
            "parity": ("reference_value", "predicted"),
            "interval": ("estimate", "lower", "upper"),
        }.get(kind, ("value",))
        if any(row[field] <= 0 for row in rows for field in fields):
            raise ValueError("Log scale requires positive values; no implicit filtering or offset")
        if kind == "interval" and spec.get("reference_value", 1) <= 0:
            raise ValueError("Log reference must be positive")
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
