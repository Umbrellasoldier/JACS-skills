#!/usr/bin/env python3
"""Reproduce the synthetic v0.4 gallery; keep full bundles in ignored local storage."""

from __future__ import annotations

import argparse
import copy
import json
import math
import shutil
import sys
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
        "height_pt": 180,
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
        "metric": r"$\Delta G^{\ddagger}$ error",
        "quantity_definition": "Signed activation Gibbs-energy error = prediction minus reference",
        "unit": "kcal/mol",
        "population": "32 synthetic reactions per group",
        "unit_of_analysis": "reaction",
        "data": values,
        "zero_reference": True,
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
            spec["caption"] = (
                "Small synthetic samples for comparing observations and density estimates."
            )
        elif mode == "box":
            spec["caption"] = (
                "Synthetic signed-error distributions for three illustrative predictors."
            )
        elif mode == "histogram":
            spec["bin_edges"] = list(range(-3, 6))
            spec["caption"] = "Synthetic observation counts compared using common bins."
        else:
            spec.update(
                value_transform="absolute",
                metric=r"Absolute $\Delta G^{\ddagger}$ error",
                zero_reference=False,
            )
            spec["caption"] += " Fraction of reactions within an absolute error threshold."
        write(name, spec)
    write(
        "intervals",
        {
            **common,
            "kind": "interval",
            "metric": r"$\Delta\Delta G^{\ddagger}$ (B − A)",
            "quantity_definition": "Activation Gibbs-energy difference: method B minus method A",
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
                {
                    "series": name,
                    "x": n,
                    "y": mean,
                    "lower": mean - sd,
                    "upper": mean + sd,
                    "replicates": replicates.tolist(),
                }
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
            "x_ticks": [50, 200, 800, 3200],
            "quantity_definition": (
                "MAE of predicted activation Gibbs energies against synthetic reference values"
            ),
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
    for name in ("State I", "State II"):
        peak = max(r["y"] for r in spectral if r["series"] == name)
        for row in spectral:
            if row["series"] == name:
                row["raw_y"] = row["y"]
                row["y"] /= peak
    write(
        "spectra",
        {
            **common,
            "kind": "curve",
            "x_quantity": "Wavenumber",
            "x_unit": "cm-1",
            "y_quantity": "Normalized intensity",
            "y_unit": "dimensionless",
            "population": "Two synthetic two-Gaussian model spectra",
            "normalization": (
                "Each model spectrum divided by its maximum sampled raw_y; no area normalization"
            ),
            "caption": (
                "Synthetic model spectra. Gaussian centers: State I, 1320 and 1625 cm-1; "
                "State II, 1355 and 1590 cm-1. Peak shifts are model inputs, "
                "not measured chemical assignments."
            ),
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
            "height_pt": 128,
            "colorbar_ticks": [0, 1.5, 3, 4.5],
            "missing_label": "NA",
            "quantity": "MAE",
            "unit": "kcal/mol",
            "population": (
                "Illustrative benchmark cells; these summaries have no reaction-level sample counts"
            ),
            "quantity_definition": "Illustrative MAE of activation Gibbs-energy predictions",
            "column_definitions": {
                "In-domain": "within the training chemical domain",
                "New scaffold": "scaffold-held-out domain",
                "New charge": "charge-held-out domain",
            },
            "row_order": rows,
            "column_order": cols,
            "vmin": 0,
            "vmax": 4.5,
            "caption": common["caption"] + " NA: unavailable; reason unspecified.",
            "data": [
                {"row": r, "column": c, "value": grid[i][j]}
                for i, r in enumerate(rows)
                for j, c in enumerate(cols)
            ],
        },
    )
    parity = json.loads((ASSETS / "parity.json").read_text())
    parity.update(
        width_pt=504,
        height_pt=300,
        quantity=r"$\Delta G^{\ddagger}$",
        data=[],
        facet_methods=True,
        population="Same 72 synthetic reactions for every method",
    )
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
    parser.add_argument("--output-dir", type=Path, default=ROOT / "local/figure-v4/gallery")
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
                "visual_review": "Pending; see evaluation/figure-v4/REPORT.md for actual review",
            }
        )
        print(name, qa["verdict"], flush=True)
        if qa["verdict"] == "FAIL":
            print(json.dumps(qa["findings"], indent=2))
    # Both panels derive from the same reactions and reference values. Native axes
    # are laid out together; no SVG outer-box alignment or caption stripping.
    cohort = json.loads((ASSETS / "agreement.json").read_text())
    residuals = [
        {
            "observation_id": r["reaction_id"],
            "group": r["method"],
            "value": r["predicted"] - r["reference_value"],
        }
        for r in cohort["data"]
    ]
    shared = {
        "kind": "distribution",
        "data_status": "synthetic",
        "profile": "single",
        "claim": "Compare bias and absolute error in the same synthetic reaction cohort",
        "caption": "Derived from the supplied prediction/reference pairs in agreement.json.",
        "population": "Same 72 synthetic reactions per method",
        "unit_of_analysis": "reaction",
        "quantity_definition": "Activation Gibbs-energy error = prediction minus reference",
        "unit": "kcal/mol",
        "data": residuals,
    }
    showcase = {
        "kind": "panel_grid",
        "profile": "double",
        "width_pt": 504,
        "height_pt": 225,
        "columns": 2,
        "data_status": "synthetic",
        "claim": "Characterize signed bias and absolute-error coverage in the same cohort",
        "population": "Same 72 synthetic reactions and three prediction methods in both panels",
        "caption": (
            "Synthetic activation-barrier benchmark. Both panels use all of the same "
            "prediction/reference pairs; method labels identify illustrative predictors, "
            "not measured performance of real methods."
        ),
        "panels": [
            {
                "label": "a",
                "title": "Bias and spread",
                "role": "Signed-error distribution",
                "spec": {
                    **copy.deepcopy(shared),
                    "display": "box",
                    "zero_reference": True,
                    "metric": r"$\Delta G^{\ddagger}$ error",
                },
            },
            {
                "label": "b",
                "title": "Absolute-error coverage",
                "role": "Fraction within a threshold",
                "spec": {
                    **copy.deepcopy(shared),
                    "display": "ecdf",
                    "value_transform": "absolute",
                    "metric": r"Absolute $\Delta G^{\ddagger}$ error",
                },
            },
        ],
    }
    write("showcase", showcase)
    path = ASSETS / "showcase.json"
    qa = render(path, args.output_dir / "showcase", overwrite=True)
    results.append(
        {
            "example": "showcase",
            "verdict": qa["verdict"],
            "files": qa["files"],
            "implementation_sha256": qa["implementation_sha256"],
            "visual_review": "Pending; inspect native panel alignment and paired caption",
        }
    )
    if args.publish:
        for row in results:
            for ext in (".png", ".svg", ".caption.txt"):
                source = args.output_dir / (row["example"] + ext)
                shutil.copyfile(source, gallery / source.name)
            row["spec_sha256"] = digest(ASSETS / (row["example"] + ".json"))
        (gallery / "manifest.json").write_text(json.dumps(results, indent=2) + "\n")
    return int(any(r["verdict"] == "FAIL" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
