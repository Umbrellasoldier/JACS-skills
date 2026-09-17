#!/usr/bin/env python3
"""Reproduce the synthetic v0.5 gallery; keep full bundles in ignored local storage."""

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
        "caption_mode": "authored",
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
            spec["point_layout"] = "swarm"
            spec["show_bandwidth_sensitivity"] = True
            spec["height_pt"] = 260
            spec["caption"] = (
                "Synthetic activation Gibbs-energy errors (prediction minus reference), "
                "n = 32 reactions per illustrative predictor. Points show all observations; "
                "horizontal offsets separate coincident values. Solid half violins show Gaussian "
                "kernel density estimates with bandwidth h = 0.35 times the sample SD; dashed "
                "curves use 2h. Each density is scaled to the same maximum width. Dark segments "
                "denote medians. The change in lobes with bandwidth precludes interpreting "
                "these shapes alone as distinct reaction populations."
            )
        elif mode == "box":
            spec["point_layout"] = "swarm"
            spec["height_pt"] = 205
            spec["caption"] = (
                "Synthetic activation Gibbs-energy errors (prediction minus reference), "
                "n = 32 reactions per illustrative predictor. Boxes span the first to third "
                "quartiles, center lines mark medians, and whiskers reach the most extreme "
                "observations within 1.5 interquartile ranges. All observations are shown. "
                "Horizontal offsets reduce overlap; the dashed line marks zero error."
            )
        elif mode == "histogram":
            spec["bin_edges"] = list(range(-3, 6))
            spec["facet_groups"] = True
            spec["zero_reference"] = False
            spec["height_pt"] = 285
            spec["caption"] = (
                "Synthetic activation Gibbs-energy errors (prediction minus reference), "
                "n = 32 reactions per illustrative predictor. Facets share both axes and "
                "1 kcal mol−1 bins with edges from −3 to 5 kcal mol−1. Bins include their left "
                "edge; the last bin also includes its right edge. All observations are counted."
            )
        else:
            spec.update(
                value_transform="absolute",
                metric=r"Absolute $\Delta G^{\ddagger}$ error",
                zero_reference=False,
            )
            spec["caption"] = (
                "Empirical cumulative distributions of absolute activation Gibbs-energy errors "
                "for three illustrative predictors (synthetic data; n = 32 reactions per group). "
                "Each step gives the fraction with absolute prediction-minus-reference error "
                "at or below the horizontal-axis value. Curves are unsmoothed and extend over "
                "a common domain."
            )
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
            "estimate_definition": "Arithmetic mean of eight synthetic reaction-level differences",
            "interval_definition": "Mean ± sample SD (ddof = 1), not a confidence interval",
            "unit_of_analysis": "reaction",
            "reference_value": 0,
            "caption": (
                "Synthetic activation Gibbs-energy differences between two illustrative methods "
                "(B minus A). Points are means of eight synthetic reaction-level "
                "differences per illustrative reaction family; error bars show ±1 sample SD "
                "(denominator n − 1), not confidence intervals. The dashed line denotes equal "
                "predictions. No significance test is implied."
            ),
            "data": [
                {
                    "label": label,
                    "estimate": float(np.mean(samples)),
                    "lower": float(np.mean(samples) - np.std(samples, ddof=1)),
                    "upper": float(np.mean(samples) + np.std(samples, ddof=1)),
                    "replicates": samples,
                    "n": len(samples),
                }
                for label, samples in [
                    ("Cycloaddition", [-2.4, -2.0, -1.7, -1.4, -1.4, -1.1, -0.8, -0.4]),
                    ("C–N coupling", [-1.4, -1.1, -0.8, -0.6, -0.6, -0.4, -0.1, 0.2]),
                    ("Proton transfer", [-0.45, -0.2, 0.0, 0.15, 0.15, 0.3, 0.5, 0.75]),
                    ("Bond dissociation", [0.05, 0.35, 0.6, 0.85, 0.85, 1.1, 1.35, 1.65]),
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
            "caption": (
                "Synthetic learning curves for three illustrative predictors. Each point is "
                "the mean of eight independently simulated MAE values at the indicated training "
                "set size; bands show ±1 sample SD, not a confidence interval. MAE refers to "
                "activation Gibbs-energy predictions. Connectors guide the eye. These simulated "
                "summaries do not establish performance on a measured or held-out test population."
            ),
            "data": learning,
        },
    )
    spectral = []
    for name, shift in [("Model I", 0), ("Model II", 35)]:
        for x in np.linspace(1100, 1800, 151):
            y = np.exp(-(((x - 1320 - shift) / 34) ** 2)) + 0.68 * np.exp(
                -(((x - 1625 + shift) / 55) ** 2)
            )
            spectral.append({"series": name, "x": float(x), "y": float(y)})
    for name in ("Model I", "Model II"):
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
                "Synthetic two-Gaussian spectra. Centers are 1320 and 1625 cm−1 for Model I "
                "and 1355 and 1590 cm−1 for Model II. Each curve is divided by its own maximum "
                "sampled intensity; absolute intensities cannot be compared. Peak positions are "
                "model inputs and carry no experimental vibrational assignments."
            ),
            "reverse_x": True,
            "series_roles": {"Model I": "model", "Model II": "model"},
            "data": spectral,
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
        caption_mode="authored",
        caption=(
            "Synthetic activation Gibbs-energy predictions for the same 72 reactions per "
            "illustrative predictor. (a–c) Predicted versus reference values; dashed lines mark "
            "identity. MAE is the mean absolute prediction-minus-reference error in kcal mol−1. "
            "(d–f) Signed residuals for the corresponding methods; dashed lines mark zero error. "
            "All methods share the same axes within each row."
        ),
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
    # A new, fully defined example replaces the earlier untraceable summary cells.
    # Stratification uses only the reference values; no observations are excluded.
    strata = np.array_split(np.argsort(references), 3)
    columns = ["Low", "Middle", "High"]
    cells = []
    for method in ("Baseline", "Transfer", "Refined"):
        predictions = [r for r in parity["data"] if r["method"] == method]
        for label, indices in zip(columns, strata, strict=True):
            selected = [predictions[int(i)] for i in indices]
            errors = [r["predicted"] - r["reference_value"] for r in selected]
            cells.append(
                {
                    "row": method,
                    "column": label,
                    "value": float(np.mean(np.abs(errors))),
                    "n": len(errors),
                    "signed_errors": errors,
                    "reaction_ids": [r["reaction_id"] for r in selected],
                }
            )
    write(
        "heatmap",
        {
            **common,
            "kind": "heatmap",
            "height_pt": 155,
            "column_label": "Reference barrier stratum",
            "value_format": ".2f",
            "quantity": "MAE",
            "unit": "kcal/mol",
            "vmin": 0,
            "vmax": 3,
            "colorbar_ticks": [0, 1, 2, 3],
            "population": "Same 72 synthetic reactions as the agreement example",
            "quantity_definition": "MAE of activation Gibbs energies: prediction minus reference",
            "column_definitions": {
                label: {
                    "n": len(indices),
                    "minimum_reference": float(references[indices].min()),
                    "maximum_reference": float(references[indices].max()),
                }
                for label, indices in zip(columns, strata, strict=True)
            },
            "row_order": ["Baseline", "Transfer", "Refined"],
            "column_order": columns,
            "caption": (
                "Mean absolute activation Gibbs-energy errors for three illustrative predictors "
                "on 72 synthetic reactions. Reactions are sorted by their reference barrier and "
                "divided into equal low-, middle- and high-barrier strata (24 reactions per cell); "
                "the same strata are used for every predictor. Cell labels and color both encode "
                "MAE in kcal mol−1. All reactions are included. Strata denote "
                "reference barriers and do not establish chemical-domain generalization."
            ),
            "data": cells,
        },
    )
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
    parser.add_argument("--output-dir", type=Path, default=ROOT / "local/figure-v5/gallery")
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
                "visual_review": "Pending; see evaluation/figure-v5/REPORT.md for actual review",
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
        "claim": "Compare signed and absolute errors in one synthetic cohort",
        "caption": "Synthetic activation Gibbs-energy errors for three illustrative predictors.",
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
        "height_pt": 300,
        "columns": 2,
        "data_status": "synthetic",
        "claim": "Characterize signed-error distributions and absolute-error coverage",
        "caption_mode": "authored",
        "population": "Same 72 synthetic reactions and three prediction methods in both panels",
        "caption": (
            "Synthetic activation Gibbs-energy errors for the same 72 reactions per illustrative "
            "predictor in both panels. (a) Signed errors (prediction minus reference). Boxes span "
            "Q1–Q3; center lines mark medians, not mean signed error; whiskers reach observations "
            "within 1.5 interquartile ranges. Every observation is shown with horizontal offsets "
            "to reduce overlap. (b) Unsmoothed empirical cumulative fractions at or below each "
            "absolute-error threshold. Method labels denote illustrative predictors."
        ),
        "panels": [
            {
                "label": "a",
                "title": "Signed-error distribution",
                "role": "Signed-error distribution",
                "spec": {
                    **copy.deepcopy(shared),
                    "display": "box",
                    "zero_reference": True,
                    "point_layout": "swarm",
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
