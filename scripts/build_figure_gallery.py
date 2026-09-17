#!/usr/bin/env python3
"""Reproduce the original synthetic v0.3 gallery; keep full bundles in ignored local storage."""

from __future__ import annotations

import argparse
import copy
import json
import math
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/jacs-figure/scripts"))
from figure_spec import digest  # noqa: E402
from plot_figures import render  # noqa: E402

ASSETS = ROOT / "skills/jacs-figure/assets/examples"


def write(name: str, spec: dict) -> None:
    (ASSETS / (name + ".json")).write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")


def synthetic_specs() -> list[str]:
    import numpy as np

    rng = np.random.default_rng(20260917)
    common = {
        "data_status": "synthetic",
        "profile": "single",
        "height_pt": 195,
        "raster_class": "color",
        "claim": "Demonstrate an encoding with synthetic values.",
        "caption": "Synthetic demonstration; not results of a chemical study.",
    }
    values = []
    for method, scale, offset in [
        ("Baseline", 2.1, 0.8),
        ("Transfer", 1.25, 0.15),
        ("Refined", 0.75, -0.05),
    ]:
        for j, value in enumerate(rng.normal(offset, scale, 32)):
            values.append(
                {"observation_id": f"R{j + 1:03}", "group": method, "value": round(float(value), 3)}
            )
    base = {
        **common,
        "kind": "distribution",
        "metric": "Barrier error",
        "unit": "kcal/mol",
        "population": "32 synthetic reactions per group",
        "unit_of_analysis": "reaction",
        "data": values,
    }
    for mode, name in [
        ("box", "boxplot"),
        ("violin", "violin"),
        ("ecdf", "ecdf"),
        ("histogram", "histogram"),
    ]:
        spec = {**copy.deepcopy(base), "display": mode}
        if mode == "violin":
            spec["bandwidth"] = 0.35
            spec["caption"] += " Gaussian KDE factor 0.35; median and every observation shown."
        elif mode == "box":
            spec["caption"] += (
                " Boxes: Q1–Q3; center: median; whiskers: observations within 1.5 IQR;"
                " every raw point is shown, including outliers."
            )
        elif mode == "histogram":
            spec["bin_edges"] = list(range(-6, 9))
            spec["caption"] += " Shared unit-width bins; counts, not density."
        else:
            spec["caption"] += " Empirical cumulative fractions; no smoothing or fitted CDF."
        write(name, spec)
    write(
        "intervals",
        {
            **common,
            "kind": "interval",
            "metric": "Barrier difference",
            "unit": "kcal/mol",
            "population": "four synthetic reaction families",
            "interval_definition": "Illustrative supplied bounds; no CI inference",
            "reference_value": 0,
            "data": [
                {"label": label, "estimate": estimate, "lower": lo, "upper": hi}
                for label, estimate, lo, hi in [
                    ("Cycloaddition", -1.4, -2.1, -0.6),
                    ("C–N coupling", -0.6, -1.1, 0.2),
                    ("Proton transfer", 0.15, -0.35, 0.5),
                    ("Bond dissociation", 0.85, 0.35, 1.5),
                ]
            ],
        },
    )
    learning = []
    for name, multiplier in [("Baseline", 1.0), ("Transfer", 0.73), ("Refined", 0.52)]:
        for n in [50, 100, 200, 400, 800, 1600, 3200]:
            replicates = rng.normal(multiplier * (20 / math.sqrt(n) + 0.3), 0.12, 8)
            mean, sd = float(replicates.mean()), float(replicates.std(ddof=1))
            learning.append(
                {"series": name, "x": n, "y": mean, "lower": mean - sd, "upper": mean + sd}
            )
    write(
        "learning",
        {
            **common,
            "kind": "curve",
            "x_quantity": "Training reactions",
            "x_unit": "dimensionless",
            "y_quantity": "MAE",
            "y_unit": "kcal/mol",
            "population": "Eight independently generated synthetic values per setting",
            "x_scale": "log",
            "connect_observations": True,
            "interval_definition": "Mean ± sample SD across eight synthetic runs",
            "caption": common["caption"] + " Points: means of eight synthetic runs;"
            " bands: ±1 sample SD; connectors are visual guides, not fitted laws.",
            "data": learning,
        },
    )
    spectral = []
    for name, shift in [("State I", 0), ("State II", 35)]:
        for x in np.linspace(1100, 1800, 151):
            y = np.exp(-(((x - 1320 - shift) / 34) ** 2)) + 0.68 * np.exp(
                -(((x - 1625 + shift) / 55) ** 2)
            )
            spectral.append({"series": name, "x": float(x), "y": float(y)})
    write(
        "spectra",
        {
            **common,
            "kind": "curve",
            "x_quantity": "Wavenumber",
            "x_unit": "cm-1",
            "y_quantity": "Normalized intensity",
            "y_unit": "dimensionless",
            "population": "Two synthetic model spectra",
            "reverse_x": True,
            "series_roles": {"State I": "model", "State II": "model"},
            "data": spectral,
        },
    )
    rows, cols = ["Baseline", "Transfer", "Refined"], ["In-domain", "New scaffold", "New charge"]
    grid = [[1.3, 2.8, 4.1], [0.9, 1.7, 2.5], [0.6, 1.1, None]]
    write(
        "heatmap",
        {
            **common,
            "kind": "heatmap",
            "height_pt": 185,
            "quantity": "MAE",
            "unit": "kcal/mol",
            "population": "Synthetic benchmark",
            "row_order": rows,
            "column_order": cols,
            "vmin": 0,
            "vmax": 4.5,
            "caption": common["caption"] + " Gray dash: unavailable, not zero.",
            "data": [
                {"row": r, "column": c, "value": grid[i][j]}
                for i, r in enumerate(rows)
                for j, c in enumerate(cols)
            ],
        },
    )
    parity = json.loads((ASSETS / "parity.json").read_text())
    parity.update(width_pt=504, height_pt=240, quantity=r"$\Delta G^{\ddagger}$", data=[])
    references = rng.uniform(4, 32, 72)
    for name, error in [("Baseline", 2.3), ("Transfer", 1.4), ("Refined", 0.8)]:
        for i, ref in enumerate(references):
            parity["data"].append(
                {
                    "reaction_id": f"R{i + 1:03}",
                    "method": name,
                    "reference_value": float(ref),
                    "predicted": float(ref + rng.normal(0, error)),
                }
            )
    write("agreement", parity)
    return [
        "boxplot",
        "violin",
        "ecdf",
        "histogram",
        "intervals",
        "learning",
        "spectra",
        "heatmap",
        "agreement",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "local/figure-v3/gallery")
    parser.add_argument(
        "--publish", action="store_true", help="Copy original PNG/SVG examples into repo"
    )
    args = parser.parse_args()
    names = ["energy", "parity", "stages", "comparison", "workflow", "structures", "toc"]
    names += synthetic_specs()
    gallery = ROOT / "examples/figures"
    results = []
    for name in names:
        qa = render(ASSETS / (name + ".json"), args.output_dir / name, overwrite=True)
        results.append(
            {
                "example": name,
                "verdict": qa["verdict"],
                "files": qa["files"],
                "implementation_sha256": qa["implementation_sha256"],
                "visual_review": "Pending; see evaluation/figure-v3/REPORT.md for actual review",
            }
        )
        print(name, qa["verdict"], flush=True)
        if qa["verdict"] == "FAIL":
            print(json.dumps(qa["findings"], indent=2))
    showcase = {
        "kind": "assembly",
        "profile": "double",
        "width_pt": 504,
        "height_pt": 430,
        "columns": 2,
        "data_status": "synthetic",
        "claim": "Complementary synthetic panels",
        "caption": "Synthetic distribution, convergence, interval and matrix demonstrations.",
        "panels": [
            {"label": label, "svg": "assembly-panels/" + name + ".svg"}
            for label, name in zip(
                "abcd", ["boxplot", "learning", "intervals", "heatmap"], strict=True
            )
        ],
    }
    # Each standalone remains visibly synthetic. The assembly has one common footer,
    # so remove only the duplicate footer text from disposable, generated panel copies.
    panel_dir = args.output_dir / "assembly-panels"
    panel_dir.mkdir(exist_ok=True)
    for name in ("boxplot", "learning", "intervals", "heatmap"):
        tree = ET.parse(args.output_dir / (name + ".svg"))
        for parent in tree.iter():
            for child in list(parent):
                if child.tag.endswith("}text") and "".join(child.itertext()).strip() == (
                    "SYNTHETIC DEMONSTRATION"
                ):
                    parent.remove(child)
        tree.write(panel_dir / (name + ".svg"), encoding="unicode")
    path = args.output_dir / "showcase.input.json"
    path.write_text(json.dumps(showcase, indent=2) + "\n")
    qa = render(path, args.output_dir / "showcase", overwrite=True)
    results.append(
        {
            "example": "showcase",
            "verdict": qa["verdict"],
            "files": qa["files"],
            "implementation_sha256": qa["implementation_sha256"],
            "visual_review": "Pending; SVG assembly needs visual review",
        }
    )
    if args.publish:
        for row in results:
            for ext in (".png", ".svg"):
                source = args.output_dir / (row["example"] + ext)
                shutil.copyfile(source, gallery / source.name)
            row["spec_sha256"] = digest(
                ASSETS / (row["example"] + ".json") if row["example"] != "showcase" else path
            )
        (gallery / "manifest.json").write_text(json.dumps(results, indent=2) + "\n")
    return int(any(r["verdict"] == "FAIL" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
