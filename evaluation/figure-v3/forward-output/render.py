#!/usr/bin/env python3
"""Reproduce a synthetic three-panel figure and its numerical/mechanical QA.

Run with the frozen package versions in environment.json. All output paths are
relative to this script. Input copies are checked against source_index.json.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ["MPLCONFIGDIR"] = str(ROOT / ".mplconfig")
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "vendor"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pypdfium2 as pdfium
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator
from PIL import Image, ImageDraw

from audit_figure import audit_layout, audit_pdf, measure_matplotlib, verdict
from preview_color import preview


def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(name):
    with (ROOT / "data" / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name, rows):
    with (ROOT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def axes_at(fig, x, y, width, height):
    return fig.add_axes([x / 504, y / 360, width / 504, height / 360])


def title(fig, x, y, letter, text):
    fig.text(x / 504, y / 360, letter, fontsize=10, weight="bold", va="baseline")
    fig.text((x + 16) / 504, y / 360, text, fontsize=8.6, va="baseline")


def quiet_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#DCE3E9", linewidth=0.5)


def main():
    (ROOT / "qa").mkdir(exist_ok=True)
    source_index = json.loads((ROOT / "source_index.json").read_text())
    for item in source_index["inputs"] + source_index["vendored_tools"]:
        assert digest(ROOT / item["bundle_path"]) == item["sha256"], item["bundle_path"]

    methods = ["Direct", "Adapted", "Calibrated"]
    training_sizes = [80, 160, 320, 640, 1280]
    colors = ["#4E86AF", "#B98255", "#428F80"]
    fills = ["#A8CEE8", "#F3C8A8", "#A4D6C8"]
    markers = ["o", "s", "^"]
    linestyles = ["-", "--", "-."]

    errors = read_csv("prediction_errors.csv")
    learning = read_csv("learning_runs.csv")
    transfer = json.loads((ROOT / "data" / "transfer.json").read_text())
    assert len(errors) == 108 and len(learning) == 120
    error_keys = [(r["reaction_id"], r["method"]) for r in errors]
    assert all(n == 1 for n in Counter(error_keys).values())
    ids_by_method = {
        m: {r["reaction_id"] for r in errors if r["method"] == m} for m in methods
    }
    assert all(ids_by_method[m] == ids_by_method[methods[0]] for m in methods)
    ids = sorted(ids_by_method[methods[0]])
    assert len(ids) == 36
    assert set(r["method"] for r in errors) == set(methods)
    error_lookup = {
        (r["reaction_id"], r["method"]): float(r["error_kcal_mol"]) for r in errors
    }
    values = np.array([[error_lookup[(rid, m)] for m in methods] for rid in ids])
    assert np.isfinite(values).all()

    run_keys = [(r["method"], int(r["training_reactions"]), r["run"]) for r in learning]
    assert all(n == 1 for n in Counter(run_keys).values())
    assert set(r["method"] for r in learning) == set(methods)
    learning_values = {}
    learning_summary = []
    for m in methods:
        assert {int(r["training_reactions"]) for r in learning if r["method"] == m} == set(training_sizes)
        for size in training_sizes:
            rows = [r for r in learning if r["method"] == m and int(r["training_reactions"]) == size]
            assert len(rows) == 8 and {r["run"] for r in rows} == {str(i) for i in range(1, 9)}
            arr = np.array([float(r["mae_kcal_mol"]) for r in rows])
            assert np.isfinite(arr).all() and (arr >= 0).all()
            learning_values[m, size] = arr
            mean, sd = float(arr.mean()), float(arr.std(ddof=1))
            learning_summary.append({
                "method": m, "training_reactions": size, "independent_runs": len(arr),
                "mean_mae_kcal_mol": mean, "sample_sd_kcal_mol": sd,
                "lower_mean_minus_sd": mean - sd, "upper_mean_plus_sd": mean + sd,
                "min_mae_kcal_mol": float(arr.min()), "max_mae_kcal_mol": float(arr.max()),
            })

    assert transfer["row_names"] == methods
    assert transfer["column_names"] == ["Neutral", "Charged"]
    assert len(transfer["mae_kcal_mol"]) == 3
    assert all(len(row) == 2 for row in transfer["mae_kcal_mol"])
    missing = [(i, j) for i, row in enumerate(transfer["mae_kcal_mol"]) for j, v in enumerate(row) if v is None]
    assert missing == [(2, 1)]
    transfer_values = np.array([[np.nan if v is None else v for v in row] for row in transfer["mae_kcal_mol"]], dtype=float)
    assert np.isfinite(transfer_values[~np.isnan(transfer_values)]).all()
    assert np.nanmin(transfer_values) >= 0 and np.nanmax(transfer_values) <= 3

    error_summary = []
    box_stats = []
    for i, m in enumerate(methods):
        arr = values[:, i]
        q1, median, q3 = np.quantile(arr, [0.25, 0.5, 0.75], method="linear")
        iqr = q3 - q1
        within = arr[(arr >= q1 - 1.5 * iqr) & (arr <= q3 + 1.5 * iqr)]
        outliers = (arr < q1 - 1.5 * iqr) | (arr > q3 + 1.5 * iqr)
        box_stats.append({"q1": q1, "med": median, "q3": q3, "whislo": within.min(), "whishi": within.max(), "fliers": []})
        error_summary.append({
            "method": m, "matched_reactions": len(arr), "q1_error_kcal_mol": float(q1),
            "median_error_kcal_mol": float(median), "q3_error_kcal_mol": float(q3),
            "lower_whisker_kcal_mol": float(within.min()), "upper_whisker_kcal_mol": float(within.max()),
            "outside_whiskers_retained": int(outliers.sum()), "mae_kcal_mol": float(np.mean(np.abs(arr))),
            "rmse_kcal_mol": float(np.sqrt(np.mean(arr ** 2))),
            "min_error_kcal_mol": float(arr.min()), "max_error_kcal_mol": float(arr.max()),
        })
    write_csv("error_summary.csv", error_summary)
    write_csv("learning_summary.csv", learning_summary)

    specification = {
        "kind": "custom_matplotlib_composite", "data_status": "synthetic",
        "question": "How do the supplied synthetic methods compare in signed error distributions, learning behavior and charge-class MAE?",
        "claim": "Descriptive differences in synthetic inputs only; no scientific result or inferential significance is claimed.",
        "output_role": "JACS main-text-style demonstration", "profile": "double",
        "width_pt": 504, "height_pt": 360,
        "panel_roles": {
            "a": "Distribution comparison of the same 36 reaction IDs across three methods; all 108 signed values, paired connectors and Tukey boxes.",
            "b": "Training-size relation: all 120 raw supplied run-level MAEs, arithmetic means and sample SD from eight independent runs per method and size.",
            "c": "Charge-class comparison: supplied aggregate MAEs; five numeric cells and one explicitly not evaluated cell.",
        },
        "unit": "kcal mol⁻¹", "method_order": methods,
        "encodings": {m: {"outline": colors[i], "fill": fills[i], "marker": markers[i], "line": linestyles[i]} for i, m in enumerate(methods)},
        "statistics": {
            "a_box": "Q1/median/Q3 from NumPy quantile(method='linear'); whiskers are the most extreme observed values within Q1−1.5 IQR to Q3+1.5 IQR. All outliers are plotted.",
            "a_jitter": "NumPy default_rng(20260917), uniform −0.12 to +0.12 in category coordinates; a reaction has the same offset for every method. Measured errors are unaltered.",
            "b_estimate": "Unweighted arithmetic mean of the eight supplied MAEs, never MAE of pooled predictions.",
            "b_interval": "Mean ± sample SD; SD=sqrt(sum((MAE−mean)^2)/(8−1)); descriptive spread, not SE or confidence interval.",
            "b_x": "True training reaction counts on a base-2 logarithmic axis; raw observations at their actual x and y; mean-to-mean lines are visual guides, no fitted scaling law.",
            "c": "One decimal place as supplied; sequential color range 0–3; null is Not evaluated and is never treated as zero.",
        },
        "population_boundary": "The three files are separate synthetic evaluation summaries. Their train/test relations and shared evaluation populations across files are unknown.",
        "unknown": ["Signed-error subtraction order", "Predicted energy quantity and reference method", "Theory, solvent, temperature and other research conditions", "Splits, training budgets and evaluated reaction counts for learning and charge-class summaries"],
        "selection": "No exclusions, trimming, imputation, resampling or fitted model.",
        "layout_rationale": "Double-column width keeps method names, five training-size ticks, raw paired observations and matrix values readable at 7.3–10 pt. The tall distribution panel accommodates the full signed-error range; the two summary panels use independent axes.",
    }
    dump("figure.spec.json", specification)

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8.5,
        "xtick.labelsize": 7.3, "ytick.labelsize": 7.5, "legend.fontsize": 8,
        "text.color": "#303C4B", "axes.labelcolor": "#303C4B",
        "axes.edgecolor": "#74808C", "xtick.color": "#303C4B", "ytick.color": "#303C4B",
        "axes.linewidth": 0.7, "xtick.major.width": 0.7, "ytick.major.width": 0.7,
        "xtick.major.size": 3, "ytick.major.size": 3,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "svg.hashsalt": "jacs-figure-synthetic-forward-v3", "savefig.facecolor": "white",
    })
    fig = plt.figure(figsize=(7, 5), dpi=144, facecolor="white")
    fig.text(0.5, 352 / 360, "SYNTHETIC DEMONSTRATION · NOT RESEARCH RESULTS", ha="center", fontsize=8.1, weight="semibold")
    handles = [Line2D([], [], color=colors[i], marker=markers[i], markerfacecolor=fills[i], markeredgewidth=0.8, markersize=4.4, linestyle=linestyles[i], linewidth=1, label=m) for i, m in enumerate(methods)]
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(0.54, 333 / 360), ncol=3, frameon=False, columnspacing=1.6, handlelength=2.4)
    title(fig, 15, 313, "a", "Paired error distributions")
    title(fig, 260, 313, "b", "Training set size")
    title(fig, 260, 156, "c", "Across charge classes")

    ax_a = axes_at(fig, 46, 55, 178, 244)
    quiet_axes(ax_a)
    ax_a.axhline(0, color="#74808C", linewidth=0.7, linestyle=(0, (3, 3)), zorder=1)
    jitter = np.random.default_rng(20260917).uniform(-0.12, 0.12, len(ids))
    for k in range(len(ids)):
        ax_a.plot(np.arange(3) + jitter[k], values[k], color="#C3CBD2", linewidth=0.5, alpha=0.72, zorder=2)
    boxes = ax_a.bxp(box_stats, positions=np.arange(3), widths=0.5, patch_artist=True, showfliers=False, manage_ticks=False, zorder=3)
    for i in range(3):
        boxes["boxes"][i].set(facecolor=fills[i], edgecolor=colors[i], alpha=0.43, linewidth=0.9)
        boxes["medians"][i].set(color=colors[i], linewidth=1.35)
        for key in ("whiskers", "caps"):
            for item in boxes[key][2 * i:2 * i + 2]:
                item.set(color=colors[i], linewidth=0.8)
        ax_a.scatter(i + jitter, values[:, i], s=14, facecolor=fills[i], edgecolor=colors[i], linewidth=0.65, marker=markers[i], zorder=4)
    ax_a.set(xlim=(-0.5, 2.5), ylim=(-5, 8.2), ylabel="Signed error (kcal mol⁻¹)")
    ax_a.set_xticks(range(3), methods)
    ax_a.set_yticks([-4, -2, 0, 2, 4, 6, 8])
    ax_a.text(0.03, 0.97, "36 matched reactions", transform=ax_a.transAxes, va="top", fontsize=7.8)
    ax_a.tick_params(axis="x", length=0, pad=7)

    ax_b = axes_at(fig, 290, 207, 202, 92)
    quiet_axes(ax_b)
    ax_b.set_xscale("log", base=2)
    ax_b.xaxis.set_major_locator(FixedLocator(training_sizes))
    ax_b.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: str(int(x))))
    ax_b.xaxis.set_minor_locator(NullLocator())
    for i, m in enumerate(methods):
        means, sds = [], []
        for size in training_sizes:
            arr = learning_values[m, size]
            ax_b.scatter(np.full(8, size), arr, s=8, facecolors="none", edgecolors=colors[i], marker=markers[i], linewidths=0.55, alpha=0.6, zorder=3)
            means.append(arr.mean())
            sds.append(arr.std(ddof=1))
        ax_b.errorbar(training_sizes, means, yerr=sds, color=colors[i], linestyle=linestyles[i], linewidth=1.05, marker=markers[i], markersize=4.1, markerfacecolor=fills[i], markeredgewidth=0.75, elinewidth=0.8, capsize=2.3, capthick=0.8, zorder=4)
    ax_b.set(xlim=(65, 1570), ylim=(0, 3.02), ylabel="MAE (kcal mol⁻¹)", xlabel="Training reactions (log₂ scale)")
    ax_b.set_yticks([0, 1, 2, 3])
    ax_b.text(0.98, 0.97, "Mean ± SD; 8 runs", ha="right", va="top", transform=ax_b.transAxes, fontsize=7.5)

    ax_c = axes_at(fig, 340, 55, 104, 81)
    cmap = LinearSegmentedColormap.from_list("soft_blue", ["#F2F7FA", "#B9D6E7", "#75A9C8", "#356D91"])
    cmap.set_bad("#E7E9ED")
    norm = Normalize(0, 3)
    # Vector cells avoid SVG viewers smoothing a tiny embedded raster matrix.
    heat = ax_c.pcolormesh(
        np.arange(3) - 0.5, np.arange(4) - 0.5,
        np.ma.masked_invalid(transfer_values), cmap=cmap, norm=norm,
        shading="flat", edgecolors="white", linewidth=0.8, rasterized=False,
    )
    ax_c.set(xlim=(-0.5, 1.5), ylim=(2.5, -0.5))
    for i in range(3):
        for j in range(2):
            value = transfer_values[i, j]
            if np.isnan(value):
                ax_c.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#E7E9ED", edgecolor="#B8C0C7", hatch="///", linewidth=0.5))
                ax_c.text(j, i, "Not\nevaluated", ha="center", va="center", fontsize=7.4, linespacing=1.15, bbox={"facecolor": "#E7E9ED", "edgecolor": "none", "pad": 0.8})
            else:
                text_color = "white" if value > 2.4 else "#303C4B"
                ax_c.text(j, i, f"{value:.1f}", ha="center", va="center", fontsize=9, color=text_color)
    ax_c.set_xticks(range(2), transfer["column_names"])
    ax_c.set_yticks(range(3), methods)
    ax_c.set_xticks(np.arange(-0.5, 2, 1), minor=True)
    ax_c.set_yticks(np.arange(-0.5, 3, 1), minor=True)
    ax_c.grid(which="minor", color="white", linewidth=0.8)
    ax_c.tick_params(which="both", length=0, pad=5)
    for spine in ax_c.spines.values():
        spine.set_visible(False)
    cax = axes_at(fig, 468, 55, 7, 81)
    colorbar = fig.colorbar(heat, cax=cax, ticks=[0, 1, 2, 3])
    colorbar.solids.set_rasterized(False)
    # Overlap adjacent vector strips to avoid antialiased white seams in SVG renderers.
    colorbar.solids.set_edgecolor("face")
    cax.yaxis.set_ticks_position("left")
    cax.yaxis.set_label_position("right")
    colorbar.set_label("MAE (kcal mol⁻¹)", labelpad=9, fontsize=8)
    colorbar.outline.set_linewidth(0.5)

    pdf = ROOT / "figure.pdf"
    fig.savefig(pdf, metadata={"Title": "Synthetic method evaluation demonstration", "Author": "Synthetic forward evaluation", "CreationDate": None, "ModDate": None})
    fig.savefig(ROOT / "figure.svg", metadata={"Date": None, "Title": "Synthetic method evaluation demonstration"})
    fig.savefig(ROOT / "figure.png", dpi=300)
    layout = measure_matplotlib(fig)
    dump("figure.layout.json", layout)
    audit = audit_pdf(pdf, 504, 360, 7)
    audit["findings"].extend(audit_layout(layout, 7))
    audit["verdict"] = verdict(audit["findings"])
    audit["visual_review"] = "Required; see QA.md for review of this exact output."
    dump("qa/mechanical.json", audit)
    plt.close(fig)

    doc = pdfium.PdfDocument(pdf)
    doc[0].render(scale=2).to_pil().save(ROOT / "qa" / "pdf-render-144dpi.png")
    doc[0].render(scale=96 / 72).to_pil().save(ROOT / "qa" / "final-size-96dpi.png")
    doc.close()
    import cairosvg

    cairosvg.svg2png(url=str(ROOT / "figure.svg"), write_to=str(ROOT / "qa" / "svg-render-144dpi.png"), dpi=144)
    preview(ROOT / "qa" / "pdf-render-144dpi.png", ROOT / "qa" / "color")
    modes = ["grayscale", "deuteranomaly", "protanomaly", "tritanomaly"]
    sheet = Image.new("RGB", (1344, 1008), "white")
    draw = ImageDraw.Draw(sheet)
    for i, mode in enumerate(modes):
        im = Image.open(ROOT / "qa" / "color" / f"pdf-render-144dpi-{mode}.png").convert("RGB")
        im = im.resize((672, 480), Image.Resampling.LANCZOS)
        x, y = (i % 2) * 672, (i // 2) * 504
        draw.text((x + 14, y + 6), mode, fill="#303C4B")
        sheet.paste(im, (x, y + 24))
    sheet.save(ROOT / "qa" / "color-contact-sheet.png")

    dump("qa/data_checks.json", {
        "status": "PASS", "source_hashes_verified": True,
        "errors": {"input_rows": len(errors), "plotted_raw_points": int(values.size), "unique_matched_reactions": len(ids), "duplicate_keys": 0, "nonfinite_values": 0, "excluded_rows": 0, "signed_range": [float(values.min()), float(values.max())]},
        "learning": {"input_rows": len(learning), "plotted_raw_points": 120, "groups": 15, "independent_runs_per_group": 8, "summaries": 15, "sd_ddof": 1, "excluded_rows": 0, "raw_x_jitter": False, "raw_y_jitter": False},
        "transfer": {"cells": 6, "observed": 5, "not_evaluated": 1, "imputed": 0, "color_range": [0, 3]},
        "inference": "No tests, confidence intervals, extrapolation, fitted trends or research claims.",
    })
    packages = ["matplotlib", "numpy", "pillow", "pypdf", "pypdfium2", "cairosvg", "defusedxml", "colorspacious"]
    environment = {"python": platform.python_version(), "platform": platform.platform(), "packages": {p: importlib.metadata.version(p) for p in packages}, "renderer": "render.py (custom Matplotlib)", "renderer_sha256": digest(Path(__file__)), "font": "DejaVu Sans", "font_policy": "PDF TrueType embedding requested; SVG retains editable text and therefore depends on the named font."}
    dump("environment.json", environment)
    (ROOT / "requirements.txt").write_text("\n".join(f"{p}=={environment['packages'][p]}" for p in packages) + "\n")
    dump("qa/artifact_hashes.json", {p.name: digest(p) for p in [ROOT / "figure.pdf", ROOT / "figure.svg", ROOT / "figure.png", ROOT / "figure.spec.json", ROOT / "render.py"]})
    print(json.dumps({"mechanical_verdict": audit["verdict"], "minimum_text_pt": audit["minimum_text_pt"], "findings": audit["findings"]}, indent=2))


if __name__ == "__main__":
    main()
