#!/usr/bin/env python3
"""Reproduce three synthetic, publication-size chemistry figures.

Run with the supplied environment:
  python make_figures.py
Inputs and outputs are resolved relative to this file; no network is used.
"""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import re
from pathlib import Path
from xml.etree import ElementTree as ET

import cairosvg
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pypdf
import rdkit
import PIL
from PIL import Image
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D


ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
DPI = 600
BLUE = "#0072B2"
ORANGE = "#D55E00"
PASS = "#009E73"
FAIL = "#E69F00"
PENDING = "#D9DDE1"
INK = "#20252B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.labelsize": 8.5,
    "axes.titlesize": 9,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "legend.fontsize": 8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "svg.hashsalt": "forward-baseline-synthetic-figures",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.unicode_minus": True,
})


def csv_rows(name: str) -> list[dict[str, str]]:
    with (INPUTS / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save_plot(fig: plt.Figure, stem: str) -> None:
    """Keep specified physical size; do not crop the page to the artwork."""
    fig.savefig(ROOT / f"{stem}.pdf", metadata={"Title": stem, "Creator": "make_figures.py"})
    fig.savefig(ROOT / f"{stem}.svg", metadata={"Title": stem, "Date": None})
    fig.savefig(ROOT / f"{stem}.png", dpi=DPI)
    plt.close(fig)


def figure_predictions() -> dict:
    rows = csv_rows("predictions.csv")
    methods = list(dict.fromkeys(row["method"] for row in rows))
    assert methods == ["Baseline", "Candidate"]
    ids = list(dict.fromkeys(row["reaction_id"] for row in rows))
    assert len(rows) == len(ids) * len(methods) == 16
    keyed = {(row["reaction_id"], row["method"]): row for row in rows}
    assert len(keyed) == len(rows), "Duplicate reaction/method row"
    ref = np.array([float(keyed[(rid, methods[0])]["reference_value"]) for rid in ids])
    predictions = {}
    residuals = {}
    metrics = {}
    for method in methods:
        other_ref = np.array([float(keyed[(rid, method)]["reference_value"]) for rid in ids])
        assert np.array_equal(ref, other_ref), "References differ between paired methods"
        pred = np.array([float(keyed[(rid, method)]["predicted"]) for rid in ids])
        assert np.isfinite(pred).all() and np.isfinite(ref).all()
        err = pred - ref
        predictions[method] = pred
        residuals[method] = err
        metrics[method] = {
            "n": len(ids), "mae": float(np.mean(np.abs(err))),
            "rmse": float(np.sqrt(np.mean(err**2))), "mean_residual": float(np.mean(err)),
        }

    fig = plt.figure(figsize=(7.0, 4.00))
    left = fig.add_axes((0.085, 0.28, 0.333, 0.58275))
    right = fig.add_axes((0.608, 0.28, 0.342, 0.58275))
    fig.text(0.065, 0.925, "(a)", weight="bold", fontsize=10)
    fig.text(0.113, 0.925, "Predicted vs reference", fontsize=9.5)
    fig.text(0.567, 0.925, "(b)", weight="bold", fontsize=10)
    fig.text(0.615, 0.925, "Paired residuals", fontsize=9.5)

    left.plot([0, 45], [0, 45], color="#7B838B", lw=0.8, ls=(0, (4, 3)), zorder=1)
    for x, a, b in zip(ref, predictions["Baseline"], predictions["Candidate"]):
        left.plot([x, x], [a, b], color="#AEB5BC", lw=0.7, zorder=1)
    left.scatter(ref, predictions["Baseline"], s=35, marker="o", facecolors="white",
                 edgecolors=BLUE, linewidths=1.2, zorder=3)
    left.scatter(ref, predictions["Candidate"], s=24, marker="^", color=ORANGE,
                 linewidths=0.6, zorder=4)
    left.set(xlim=(0, 45), ylim=(0, 45), xticks=np.arange(0, 46, 10),
             yticks=np.arange(0, 46, 10))
    left.set_aspect("equal", adjustable="box")
    left.set_xlabel(r"Reference $\Delta G^{\ddagger}$ (kcal mol$^{-1}$)")
    left.set_ylabel(r"Predicted $\Delta G^{\ddagger}$ (kcal mol$^{-1}$)")
    left.text(0.05, 0.96, "8 paired reactions", transform=left.transAxes,
              ha="left", va="top", fontsize=7.5)
    left.text(0.91, 0.06, "$y=x$", transform=left.transAxes,
              ha="right", va="bottom", color="#68717A", fontsize=7.5)

    y = np.arange(len(ids))
    offset = 0.12
    right.axvline(0, color="#68717A", lw=0.85, ls=(0, (4, 3)), zorder=1)
    for i in y:
        right.plot([residuals["Baseline"][i], residuals["Candidate"][i]],
                   [i - offset, i + offset], color="#AEB5BC", lw=0.8, zorder=2)
    right.scatter(residuals["Baseline"], y - offset, s=31, marker="o", facecolors="white",
                  edgecolors=BLUE, linewidths=1.2, zorder=3)
    right.scatter(residuals["Candidate"], y + offset, s=24, marker="^", color=ORANGE,
                  linewidths=0.6, zorder=4)
    right.set(yticks=y, yticklabels=ids, ylim=(len(ids) - 0.55, -0.55),
              xlim=(-7, 7), xticks=np.arange(-6, 7, 2))
    right.set_xlabel(r"Residual (kcal mol$^{-1}$)")
    right.tick_params(axis="y", length=0, pad=5)
    right.grid(axis="x", color="#E7EBEE", linewidth=0.5, zorder=0)
    right.set_axisbelow(True)
    for ax in (left, right):
        ax.spines[["top", "right"]].set_visible(False)

    legend = [
        Line2D([], [], marker="o", markersize=5.8, markerfacecolor="white", color=BLUE,
               markeredgewidth=1.2, linestyle="none"),
        Line2D([], [], marker="^", markersize=5, color=ORANGE, linestyle="none"),
    ]
    labels = [f"{method}: MAE {metrics[method]['mae']:.2f}, RMSE {metrics[method]['rmse']:.2f}"
              for method in methods]
    fig.legend(legend, labels, loc="center", bbox_to_anchor=(0.51, 0.135),
               ncols=2, frameon=False, columnspacing=2.1, handletextpad=0.5)
    fig.text(0.51, 0.077, r"Residual = predicted $-$ reference; MAE and RMSE in kcal mol$^{-1}$.",
             ha="center", fontsize=7.5)
    fig.text(0.51, 0.028, "Synthetic example data", ha="center", fontsize=7, color="#5E6770")
    save_plot(fig, "figure_1_predictions")

    with (ROOT / "prediction_residuals.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) + ["residual"])
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "residual": format(float(row["predicted"]) - float(row["reference_value"]), ".12g")})
    return {"records": len(rows), "reaction_ids": ids, "metrics": metrics,
            "residual_sign": "predicted - reference", "all_pairs_share_reference": True}


def figure_stages() -> dict:
    rows = csv_rows("stages.csv")
    initial = 199
    entering = initial
    summary = []
    for row in rows:
        counts = {k: int(row[k]) for k in ("passed", "failed", "pending")}
        assert all(n >= 0 for n in counts.values())
        assert sum(counts.values()) == entering, f"Stage population mismatch: {row['stage']}"
        summary.append({"stage": row["stage"], "entering": entering, **counts,
                        "pass_rate": counts["passed"] / entering})
        entering = counts["passed"]

    fig = plt.figure(figsize=(3.25, 3.65))
    ax = fig.add_axes((0.075, 0.245, 0.885, 0.540))
    fig.text(0.075, 0.957, "Initial cohort: 199 reactions", weight="bold", fontsize=9)
    fig.text(0.075, 0.906, "Pass rate = passed / entering this stage", fontsize=7.6)
    handles = [Patch(facecolor=PASS, label="Passed"),
               Patch(facecolor=FAIL, label="Failed"),
               Patch(facecolor=PENDING, edgecolor="#747D85", linewidth=0.4, hatch="///", label="Pending")]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(0.048, 0.853),
               ncols=3, frameon=False, handlelength=1.0, handletextpad=0.5,
               columnspacing=1.0, fontsize=7.5)
    y_positions = [3, 2, 1, 0]
    for y, row in zip(y_positions, summary):
        start = 0
        for key, color, hatch in [("passed", PASS, None), ("failed", FAIL, None),
                                  ("pending", PENDING, "///")]:
            value = row[key]
            ax.barh(y, value, left=start, height=0.30, color=color,
                    edgecolor="white" if key != "pending" else "#747D85",
                    linewidth=0.5, hatch=hatch, zorder=2)
            ax.text(start + value / 2, y, str(value), ha="center", va="center",
                    fontsize=7.5, color="white" if key == "passed" else INK,
                    bbox=dict(facecolor=color, edgecolor="none", pad=0.2) if hatch else None,
                    zorder=3)
            start += value
        ax.text(0, y + 0.28, row["stage"], ha="left", va="bottom", fontsize=7.6)
        ax.text(initial, y + 0.28,
                f"{row['passed']}/{row['entering']} ({row['pass_rate']:.1%})",
                ha="right", va="bottom", fontsize=7.4)
    ax.set(xlim=(0, initial), ylim=(-0.38, 3.70), yticks=[], xticks=[0, 50, 100, 150, 199])
    ax.set_xlabel("Reaction count", fontsize=8, labelpad=4)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=7)
    fig.text(0.075, 0.100, "Only passed reactions enter the next stage.", fontsize=7.3)
    fig.text(0.075, 0.058, f"Final passed: 65/199 ({65/199:.1%} of initial cohort).", fontsize=7.3)
    fig.text(0.075, 0.019, "Synthetic example data", fontsize=7, color="#5E6770")
    save_plot(fig, "figure_2_stages")
    with (ROOT / "stage_denominators.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    return {"initial": initial, "stages": summary,
            "final_passed_fraction_of_initial": 65 / initial,
            "all_stage_populations_conserved": True}


def figure_structures() -> dict:
    records = json.loads((INPUTS / "structures.json").read_text(encoding="utf-8"))
    assert len(records) == 2
    mols = []
    summary = []
    for record in records:
        mol = Chem.MolFromSmiles(record["smiles"])
        assert mol is not None
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        maps = [atom.GetAtomMapNum() for atom in mol.GetAtoms()]
        assert sorted(maps) == list(range(1, 7)), "Unexpected or missing atom-map number"
        centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
        assert len(centers) == 1 and centers[0][1] in {"R", "S"}
        rdDepictor.Compute2DCoords(mol)
        summary.append({**record, "canonical_isomeric_smiles": Chem.MolToSmiles(mol, isomericSmiles=True),
                        "atom_maps_in_input_order": maps,
                        "stereocenters": [{"atom_map": mol.GetAtomWithIdx(i).GetAtomMapNum(), "CIP": cip}
                                          for i, cip in centers]})
        mols.append(mol)
    assert summary[0]["stereocenters"][0]["CIP"] != summary[1]["stereocenters"][0]["CIP"]
    assert [a.GetAtomicNum() for a in mols[0].GetAtoms()] == [a.GetAtomicNum() for a in mols[1].GetAtoms()]
    # Identical 2D coordinates make the opposite wedges directly comparable.
    second_conf = mols[1].GetConformer()
    for i in range(mols[0].GetNumAtoms()):
        second_conf.SetAtomPosition(i, mols[0].GetConformer().GetAtomPosition(i))

    # FreeType paths preserve the renderer's glyph spacing in SVG/PDF/PNG.
    drawing = rdMolDraw2D.MolDraw2DSVG(468, 238, 234, 238, False)
    opts = drawing.drawOptions()
    opts.useBWAtomPalette()
    opts.fixedFontSize = 17
    opts.minFontSize = 17
    opts.maxFontSize = 17
    opts.legendFontSize = 18
    opts.legendFraction = 0.17
    opts.padding = 0.06
    opts.bondLineWidth = 1.6
    opts.multipleBondOffset = 0.16
    opts.addStereoAnnotation = False
    opts.explicitMethyl = True
    drawing.DrawMolecules(mols, legends=[f"{row['label']} ({row['id']})" for row in records])
    drawing.FinishDrawing()
    svg = drawing.GetDrawingText()
    # Drawing user units are two per point: 468 x 238 -> 234 x 119 pt.
    svg = re.sub(r"width='468px' height='238px'", "width='234pt' height='119pt'", svg, count=1)
    assert "width='234pt' height='119pt'" in svg
    # Explicit metadata makes the exact mapped input inspectable in the vector file.
    xml = ET.fromstring(svg)
    ns = "http://www.w3.org/2000/svg"
    title = ET.Element(f"{{{ns}}}title")
    title.text = "Synthetic mapped stereoisomers: Isomer 1 (s1) and Isomer 2 (s2)"
    desc = ET.Element(f"{{{ns}}}desc")
    desc.text = "; ".join(f"{r['id']} | {r['label']} | {r['smiles']}" for r in records)
    xml.insert(0, title)
    xml.insert(1, desc)
    ET.register_namespace("", ns)
    svg = ET.tostring(xml, encoding="unicode", xml_declaration=True)
    path = ROOT / "figure_3_structures.svg"
    path.write_text(svg, encoding="utf-8")
    cairosvg.svg2pdf(url=str(path), write_to=str(ROOT / "figure_3_structures.pdf"))
    cairosvg.svg2png(url=str(path), write_to=str(ROOT / "figure_3_structures.png"),
                    output_width=1950, output_height=round(119 / 72 * DPI))
    with Image.open(ROOT / "figure_3_structures.png") as rendered:
        rendered.save(ROOT / "figure_3_structures.png", dpi=(DPI, DPI))
    return {"records": summary, "same_2d_coordinates": True,
            "three_dimensional_geometry_generated": False,
            "physical_size_inches": [3.25, 119 / 72]}


def export_audit() -> dict:
    expected = {"figure_1_predictions": (7, 4.0), "figure_2_stages": (3.25, 3.65),
                "figure_3_structures": (3.25, 119 / 72)}
    audit = {}
    for stem, inches in expected.items():
        pdf = pypdf.PdfReader(ROOT / f"{stem}.pdf")
        assert len(pdf.pages) == 1
        page = pdf.pages[0]
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        assert abs(width / 72 - inches[0]) < 0.005
        assert abs(height / 72 - inches[1]) < 0.005
        raster = plt.imread(ROOT / f"{stem}.png")
        assert raster.shape[1] == round(inches[0] * DPI)
        assert abs(raster.shape[0] - round(inches[1] * DPI)) <= 1
        ET.parse(ROOT / f"{stem}.svg")
        border = np.concatenate([raster[0, :, :3], raster[-1, :, :3],
                                 raster[:, 0, :3], raster[:, -1, :3]])
        assert border.min() > 0.98, f"Nonwhite page-edge content in {stem}"
        fonts = page.get("/Resources").get_object().get("/Font", {})
        font_info = []
        for name, ref in fonts.items():
            font = ref.get_object()
            descendants = font.get("/DescendantFonts", [font])
            embedded = []
            for descendant in descendants:
                descriptor = descendant.get_object().get("/FontDescriptor")
                embedded.append(bool(descriptor and any(
                    key in descriptor.get_object() for key in ("/FontFile", "/FontFile2", "/FontFile3"))))
            assert all(embedded), f"Unembedded font in {stem}"
            font_info.append({"name": str(name), "subtype": str(font.get("/Subtype")),
                              "basefont": str(font.get("/BaseFont")), "embedded": all(embedded)})
        assert len(page.images) == 0, f"Unexpected raster image in PDF: {stem}"
        with Image.open(ROOT / f"{stem}.png") as png:
            metadata_dpi = png.info["dpi"]
            assert all(abs(resolution - DPI) < 0.01 for resolution in metadata_dpi)
        audit[stem] = {"page_inches": [width / 72, height / 72],
                       "png_pixels": [raster.shape[1], raster.shape[0]],
                       "png_dpi": list(metadata_dpi), "page_edge_clear": True,
                       "pdf_raster_image_count": len(page.images),
                       "svg_well_formed": True, "pdf_fonts": font_info}
    return audit


def main() -> None:
    data = {"predictions": figure_predictions(), "stages": figure_stages(),
            "structures": figure_structures()}
    data["exports"] = export_audit()
    data["input_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(INPUTS.iterdir()) if p.is_file()}
    versions = {"python": platform.python_version(), "matplotlib": matplotlib.__version__,
                "numpy": np.__version__, "cairosvg": cairosvg.__version__,
                "pypdf": pypdf.__version__, "rdkit": rdkit.__version__, "pillow": PIL.__version__}
    data["runtime_versions"] = versions
    (ROOT / "validation.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "runtime_versions.txt").write_text("\n".join(f"{k}=={v}" for k, v in versions.items()) + "\n", encoding="utf-8")
    print(json.dumps({"figures_written": 3, "formats_per_figure": ["pdf", "svg", "png"],
                      "metrics": data["predictions"]["metrics"], "checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
