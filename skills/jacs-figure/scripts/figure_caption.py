"""Carry supplied definitions and computed display facts into the delivered caption."""

from __future__ import annotations

import json


def compose_caption(spec: dict, details: dict, *, nested: bool = False) -> str:
    """Keep author prose intact; derive only facts established by this rendering."""
    parts = [spec["caption"].strip()]
    if not nested and spec["data_status"] == "synthetic" and "synthetic" not in parts[0].lower():
        parts.append("Synthetic demonstration; not research results.")
    if spec.get("caption_mode") == "authored":
        return " ".join(parts) + "\n"
    for key, label in (
        ("population", "Population"),
        ("unit_of_analysis", "Observation unit"),
        ("quantity_definition", "Quantity definition"),
        ("reference", "Reference"),
        ("conditions", "Conditions"),
        ("normalization", "Normalization"),
    ):
        if key in spec:
            value = spec[key]
            if isinstance(value, dict):
                value = "; ".join(
                    f"T = {v} K" if k == "temperature_K" else f"{k.replace('_', ' ')}: {v}"
                    for k, v in value.items()
                )
            parts.append(f"{label}: {value}.")
    kind = spec["kind"]
    if kind == "distribution":
        counts = "; ".join(f"{k}, n = {v['n']}" for k, v in details["summary"].items())
        parts.append(f"Plotted observations: {counts}.")
        if spec.get("value_transform", "identity") == "absolute":
            parts.append("Displayed values are the absolute values of the supplied measurements.")
        definitions = {
            "box": "Boxes: Q1–Q3; center: median; whiskers: observed values within 1.5 IQR. "
            "All observations, including outliers, are shown.",
            "violin": "Half violins: Gaussian KDE, equal maximum width; segments: medians. "
            "All observations are shown beside the densities. "
            f"Bandwidth factor: {spec.get('bandwidth')}; shape is bandwidth-sensitive.",
            "ecdf": "Steps: empirical cumulative fractions; no smoothing. "
            "Tails extend over the common displayed domain.",
            "histogram": "Outlines: observation counts in common bins with edges "
            f"{json.dumps(spec.get('bin_edges'))}; the last bin includes its right edge.",
        }
        parts.append(definitions[spec["display"]])
        if spec["display"] in {"box", "violin"}:
            parts.append("Point offsets affect only the categorical coordinate.")
        if details.get("bandwidth_sensitive_groups"):
            parts.append(
                "The number of KDE modes changes when the bandwidth factor is doubled for: "
                + ", ".join(details["bandwidth_sensitive_groups"])
                + ". Density lobes alone do not establish subpopulations."
            )
    elif kind == "interval":
        parts.append(f"Points: supplied estimates. Intervals: {spec['interval_definition']}.")
        if "reference_value" in spec:
            parts.append(
                f"Dashed reference: {spec['reference_value']:g}; "
                "crossing it alone does not establish statistical significance."
            )
    elif kind == "curve":
        parts.append(
            "Series roles: "
            + "; ".join(f"{name}: {role}" for name, role in spec["series_roles"].items())
            + "."
        )
        if details["banded_series"]:
            parts.append(f"Bands: {spec['interval_definition']}.")
        if spec.get("connect_observations"):
            parts.append("Connectors between observations are visual guides, not fitted laws.")
    elif kind == "heatmap":
        parts.append(
            f"Cells: {spec['quantity']} ({spec['unit']}); color limits "
            f"{spec['vmin']:g}–{spec['vmax']:g}. "
            f"{details['observed_cells']} observed and {details['missing_cells']} missing cells."
        )
        if details["missing_cells"]:
            parts.append(f"{spec.get('missing_label', 'NA')}: unavailable, not zero.")
        if "column_definitions" in spec:
            parts.append(
                "Column definitions: "
                + "; ".join(f"{k}: {v}" for k, v in spec["column_definitions"].items())
                + "."
            )
    elif kind == "comparison":
        parts.append(
            "Points: individual observations; pale lines link the same reaction across methods; "
            "dark segments: medians, not uncertainty intervals. "
            "Horizontal offsets distinguish reaction IDs without changing measured values."
        )
        parts.append(
            "Sample sizes: "
            + "; ".join(f"{k}, n = {v['n']}" for k, v in details["summary"].items())
            + "."
        )
    elif kind == "parity":
        parts.append(
            "Dashed lines: prediction = reference in parity panels and zero in residual panels. "
            "Residual = prediction − reference."
        )
        parts.append(
            "Errors for plotted reactions: "
            + "; ".join(
                f"{k}, n = {v['n']}, MAE = {v['mae']:.3g}, RMSE = {v['rmse']:.3g}"
                for k, v in details["metrics"].items()
            )
            + f" ({spec['unit']})."
        )
    elif kind == "energy":
        parts.append("Levels are supplied energies; connectors are schematic, not a computed IRC.")
        if "state_definitions" in spec:
            parts.append(
                "States: "
                + "; ".join(f"{k}: {v}" for k, v in spec["state_definitions"].items())
                + "."
            )
    elif kind == "stages":
        parts.append(
            "Bars show counts relative to the initial cohort. Labels give passed/entered "
            "for that stage; only preceding passes enter the next stage. "
            "The not-entered segment includes upstream failures and pending observations; "
            "it is excluded from the conditional denominator."
        )
        parts.extend(f"{r['stage']}: {r['criterion']}." for r in spec["data"] if "criterion" in r)
    elif kind == "structures":
        parts.append(
            "Structures are two-dimensional depictions, not measured or optimized geometries."
        )
    elif kind == "workflow":
        parts.append(
            "Arrows describe the supplied process; they do not establish a reaction mechanism."
        )
    elif kind in {"assembly", "panel_grid"}:
        for panel in spec["panels"]:
            label = panel["label"]
            if kind == "panel_grid":
                child = compose_caption(
                    panel["spec"], details["panels"][label], nested=True
                ).strip()
            else:
                child = panel["caption"]
            role = panel.get("role", "")
            parts.append(f"({label}) {role + ': ' if role else ''}{child}")
    if kind in {"assembly", "panel_grid"}:
        count = len(spec["panels"])
        return "\n\n".join([" ".join(parts[:-count]), *parts[-count:]]) + "\n"
    return " ".join(parts) + "\n"


def caption_facts(spec: dict, details: dict) -> dict:
    """Keep reviewable definitions separate from publication prose; never infer missing facts."""
    keys = (
        "population",
        "unit_of_analysis",
        "quantity_definition",
        "estimate_definition",
        "interval_definition",
        "reference",
        "conditions",
        "normalization",
        "column_definitions",
        "missing_reasons",
        "observation_window",
        "state_definitions",
    )
    facts = {
        "data_status": spec["data_status"],
        "definitions": {key: spec[key] for key in keys if key in spec},
        "computed_display_facts": details,
        "caption_mode": spec.get("caption_mode", "compose"),
        "review": "Check facts against final caption; prose is not validated automatically",
    }
    if spec["kind"] == "panel_grid":
        facts["panels"] = {
            panel["label"]: caption_facts(panel["spec"], details["panels"][panel["label"]])
            for panel in spec["panels"]
        }
    return facts
