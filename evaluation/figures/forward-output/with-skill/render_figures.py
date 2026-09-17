#!/usr/bin/env python3
"""Reproduce the three supplied synthetic JACS example figures.

All paths resolve within this delivery folder. The copied skill helpers validate
the evidence and audit the exported PDF/layout; custom plotting makes IDs,
quantities, stage counts, and denominators explicit in the artwork.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "source/skill_helpers"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image, ImageOps

from audit_figure import audit_layout, audit_pdf, measure_matplotlib, verdict
from figure_spec import load, validate
from svg_panels import molecular_svg, tag, text

matplotlib.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7.5,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "lines.linewidth": 0.7,
        "hatch.linewidth": 0.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
    }
)

COLORS = {"Baseline": "#0072B2", "Candidate": "#D55E00"}
CAPTIONS = {
    "figure1_predictions": (
        "Figure 1. Synthetic comparison of activation Gibbs free energy predictions "
        "for the same eight reactions (RX-001–RX-008). (a) Predicted versus reference "
        "activation Gibbs free energy, with a dashed identity line. (b) Residuals "
        "(prediction minus reference), grouped by reaction ID; horizontal offsets "
        "separate methods. Every supplied prediction is shown. Energies are in "
        "kcal/mol, referenced to separated reactants, at 298.15 K and a 1 mol/L "
        "standard state. The calculation level and solvent settings are shared, "
        "but their identities were not supplied. MAE and RMSE describe these eight "
        "synthetic records per method; no uncertainty or significance is inferred."
    ),
    "figure2_stages": (
        "Figure 2. Synthetic sequential-stage accounting for 199 initial reactions. "
        "Only reactions passing the preceding stage enter the next stage. Colored "
        "segments show passed, failed, and pending reactions at the indicated stage; "
        "gray segments show the cumulative earlier failures or pending reactions. "
        "Each conditional pass rate equals the passed count divided by the entered "
        "count at that stage (199, 150, 110, and 90, respectively); the gray segment "
        "is excluded from that denominator. The final-stage pass count is 65/199 "
        "(32.7%) of the initial population. Stage names are those supplied and do "
        "not establish additional validation procedures."
    ),
    "figure3_structures": (
        "Figure 3. Synthetic structure-depiction example using the two supplied "
        "atom-mapped isomeric SMILES: s1 (Isomer 1) and s2 (Isomer 2). Atom maps 1–6 "
        "are preserved and printed after colons; solid and hashed wedges encode "
        "the supplied opposite configurations. These are RDKit 2D chemical drawings, "
        "not calculated three-dimensional structures or bond-length measurements."
    ),
}


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_specs() -> dict:
    common = {"data_status": "synthetic", "scale": "linear"}
    specs = {
        "figure1_predictions": {
            **common,
            "kind": "parity",
            "profile": "double",
            "width_pt": 504,
            "height_pt": 300,
            "claim": "Descriptive prediction errors for eight shared synthetic reactions.",
            "caption": CAPTIONS["figure1_predictions"],
            "input_csv": "../inputs/predictions.csv",
            "quantity": "activation Gibbs free energy",
            "unit": "kcal/mol",
            "reference": "separated reactants",
            "conditions": {
                "temperature_K": 298.15,
                "standard_state": "1 mol/L",
                "theory": "shared illustrative setting; identity not supplied",
                "solvent": "shared illustrative setting; identity not supplied",
            },
            "population": "same eight supplied reactions, RX-001 through RX-008",
            "split": "not supplied; no generalization claim",
            "colors": COLORS,
            "residual_definition": "predicted minus reference",
            "residual_x": "reaction_id; method offsets -0.13 and +0.13 are display-only",
            "uncertainty": "not supplied and not inferred",
        },
        "figure2_stages": {
            **common,
            "kind": "stages",
            "profile": "double",
            "width_pt": 504,
            "height_pt": 266,
            "claim": "Sequential cohort accounting with conditional pass-rate denominators.",
            "caption": CAPTIONS["figure2_stages"],
            "input_csv": "../inputs/stages.csv",
            "population": "199 initial synthetic reactions, sequential unbranched cohort",
            "population_total": 199,
            "unit_of_analysis": "reactions",
        },
        "figure3_structures": {
            **common,
            "kind": "structures",
            "profile": "double",
            "width_pt": 360,
            "height_pt": 180,
            "claim": "Preserve the two supplied mapped stereochemical identities in 2D.",
            "caption": CAPTIONS["figure3_structures"],
            "columns": 2,
            "data": json.loads((ROOT / "inputs/structures.json").read_text()),
            "geometry": "2D depiction only; no bond lengths inferred",
        },
    }
    result = {}
    for name, spec in specs.items():
        path = ROOT / "specs" / f"{name}.json"
        write_json(path, spec)
        normalized, provenance = load(path)
        normalized.pop("input_csv", None)
        write_json(ROOT / "specs" / f"{name}.normalized.json", normalized)
        result[name] = (normalized, provenance)
    return result


def axes_at(fig, rect, dimensions):
    width, height = dimensions
    x, y, w, h = rect
    return fig.add_axes([x / width, y / height, w / width, h / height])


def figure_text(fig, x, y, value, dimensions, **kwargs):
    width, height = dimensions
    return fig.text(x / width, y / height, value, **kwargs)


def open_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)


def review_artifacts(prefix: Path, dimensions):
    """Rasterize each actual PDF and SVG independently for visual inspection."""
    import cairosvg
    import pypdfium2 as pdfium

    width, height = dimensions
    document = pdfium.PdfDocument(str(prefix.with_suffix(".pdf")))
    page = document[0]
    for dpi in (96, 300):
        bitmap = page.render(scale=dpi / 72)
        image = bitmap.to_pil().convert("RGB")
        image.save(ROOT / "previews" / f"{prefix.name}.pdf-{dpi}dpi.png", dpi=(dpi, dpi))
        if dpi == 96:
            ImageOps.grayscale(image).save(ROOT / "previews" / f"{prefix.name}.grayscale.png")
        bitmap.close()
    page.close()
    document.close()
    cairosvg.svg2png(
        url=str(prefix.with_suffix(".svg")),
        write_to=str(ROOT / "previews" / f"{prefix.name}.svg-96dpi.png"),
        output_width=round(width * 96 / 72),
        output_height=round(height * 96 / 72),
    )


def audit_export(name, spec, provenance, details, fig=None, svg=None, groups=None):
    import cairosvg

    prefix = ROOT / "figures" / name
    width, height = spec["width_pt"], spec["height_pt"]
    layout = None
    if fig is not None:
        layout = measure_matplotlib(fig, groups)
        write_json(ROOT / "qa" / f"{name}.layout.json", layout)
        for extension in (".pdf", ".svg", ".png"):
            fig.savefig(prefix.with_suffix(extension), dpi=300)
        plt.close(fig)
    else:
        prefix.with_suffix(".svg").write_bytes(svg)
        cairosvg.svg2pdf(bytestring=svg, write_to=str(prefix.with_suffix(".pdf")))
        cairosvg.svg2png(
            bytestring=svg,
            write_to=str(prefix.with_suffix(".png")),
            output_width=round(width * 300 / 72),
            output_height=round(height * 300 / 72),
        )
        # CairoSVG preserves pixel size but omits the nominal physical DPI.
        # Add the 300 dpi export metadata without changing any image pixels.
        with Image.open(prefix.with_suffix(".png")) as exported_png:
            exported_png.load()
            exported_png.save(prefix.with_suffix(".png"), dpi=(300, 300))
    result = audit_pdf(prefix.with_suffix(".pdf"), width, height)
    if layout is not None:
        result["findings"].extend(audit_layout(layout))
    else:
        result["findings"].append(
            {
                "check": "embedded_panel_layout",
                "status": "UNKNOWN",
                "detail": "Molecular glyph/bond collision and stereochemical appearance require visual review.",
            }
        )
    result.update(
        name=name,
        details=details,
        provenance=provenance,
        verdict=verdict(result["findings"]),
        visual_review="required; recorded separately after inspecting exported figures",
        data_status="synthetic",
        renderer_sha256=sha(Path(__file__)),
        files={ext: sha(prefix.with_suffix(ext)) for ext in (".pdf", ".svg", ".png")},
    )
    write_json(ROOT / "qa" / f"{name}.qa.json", result)
    prefix.with_suffix(".caption.txt").write_text(spec["caption"] + "\n")
    review_artifacts(prefix, (width, height))
    return result


def render_predictions(spec, provenance):
    name = "figure1_predictions"
    dimensions = (spec["width_pt"], spec["height_pt"])
    fig = plt.figure(figsize=(dimensions[0] / 72, dimensions[1] / 72))
    parity = axes_at(fig, [44, 73, 185, 185], dimensions)
    residual = axes_at(fig, [306, 73, 185, 185], dimensions)
    axes = [parity, residual]
    ids = list(dict.fromkeys(row["reaction_id"] for row in spec["data"]))
    methods = list(dict.fromkeys(row["method"] for row in spec["data"]))
    metrics = {}
    records = []
    for index, method in enumerate(methods):
        rows = [row for row in spec["data"] if row["method"] == method]
        ref = np.array([row["reference_value"] for row in rows])
        prediction = np.array([row["predicted"] for row in rows])
        error = prediction - ref
        opts = (
            {"marker": "o", "s": 26, "facecolors": "none", "edgecolors": COLORS[method], "linewidths": 0.9}
            if index == 0 else
            {"marker": "s", "s": 15, "facecolors": COLORS[method], "edgecolors": COLORS[method], "linewidths": 0.5}
        )
        parity.scatter(ref, prediction, label=method, zorder=3, **opts)
        residual.scatter(np.arange(len(rows)) + (-0.13 if index == 0 else 0.13), error, zorder=3, **opts)
        metrics[method] = {
            "n": len(rows),
            "mae_kcal_per_mol": float(np.mean(np.abs(error))),
            "rmse_kcal_per_mol": float(np.sqrt(np.mean(error ** 2))),
            "reaction_ids": [row["reaction_id"] for row in rows],
        }
        for row, value in zip(rows, error):
            records.append({**row, "residual": float(value)})
    parity.plot([4, 44], [4, 44], "--", color="#777777", linewidth=0.7, zorder=1)
    parity.set(xlim=(4, 44), ylim=(4, 44), xticks=[10, 20, 30, 40], yticks=[10, 20, 30, 40])
    parity.set_xlabel(r"Reference $\Delta G^{\ddagger}$ (kcal/mol)")
    parity.set_ylabel(r"Predicted $\Delta G^{\ddagger}$ (kcal/mol)")
    parity.set_aspect("equal", adjustable="box")
    parity.legend(loc="upper left", frameon=False, borderpad=0.1, labelspacing=0.55)
    residual.axhline(0, linestyle="--", linewidth=0.7, color="#777777", zorder=1)
    residual.set(ylim=(-7, 7), yticks=[-6, -3, 0, 3, 6], xlim=(-0.6, len(ids) - 0.4))
    residual.set_xticks(np.arange(len(ids)), ids, rotation=60, ha="right", rotation_mode="anchor")
    residual.set_ylabel(r"Residual $\Delta G^{\ddagger}$ (kcal/mol)")
    residual.set_xlabel("Reaction ID", labelpad=3)
    for label, ax in zip(("a", "b"), axes):
        open_axes(ax)
        ax.set_title(label, loc="left", fontweight="bold", fontsize=9, pad=5)
    figure_text(fig, 44, 284, "Activation Gibbs free energy predictions", dimensions, fontsize=9.5, fontweight="bold")
    figure_text(fig, 306, 284, "Residual = prediction − reference", dimensions, fontsize=7.5)
    for x, method in zip((44, 306), methods):
        metric = metrics[method]
        figure_text(
            fig, x, 14,
            f"{method}: MAE {metric['mae_kcal_per_mol']:.2f}; RMSE {metric['rmse_kcal_per_mol']:.2f} kcal/mol",
            dimensions, fontsize=7, color=COLORS[method],
        )
    figure_text(fig, 44, 3, "SYNTHETIC DEMONSTRATION  |  n = 8 per method; all records shown", dimensions, fontsize=6)
    with (ROOT / "qa/predictions_with_residuals.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["reaction_id", "method", "reference_value", "predicted", "residual"])
        writer.writeheader()
        writer.writerows(records)
    return audit_export(
        name, spec, provenance,
        {"metrics": metrics, "input_records": 16, "plotted_records": len(records), "excluded_records": 0,
         "residual": "prediction minus reference", "comparable_axes": "parity and residual boxes are 185 x 185 pt; y scales differ by quantity"},
        fig=fig, groups=[{"panels": ["0", "1"], "orientation": "row", "equal_size": True}],
    )


def render_stages(spec, provenance):
    dimensions = (spec["width_pt"], spec["height_pt"])
    fig = plt.figure(figsize=(dimensions[0] / 72, dimensions[1] / 72))
    ax = axes_at(fig, [129, 74, 253, 127], dimensions)
    colors = {"passed": "#93C4DF", "failed": "#E8A58F", "pending": "#EED580", "previous": "#E4E4E4"}
    hatches = {"passed": "", "failed": "///", "pending": "..", "previous": ""}
    total = spec["population_total"]
    for i, row in enumerate(spec["data"]):
        left = 0
        counts = {key: row[key] for key in ("passed", "failed", "pending")}
        counts["previous"] = total - row["entered"]
        for key, value in counts.items():
            ax.barh(i, value, left=left, height=0.64, color=colors[key], hatch=hatches[key], edgecolor="#555555", linewidth=0.5)
            if value:
                ax.text(left + value / 2, i, str(value), ha="center", va="center", fontsize=7,
                        bbox={"facecolor": colors[key], "edgecolor": "none", "pad": 0.2})
            left += value
        ax.text(1.038, i, f"{row['passed']}/{row['entered']} ({row['conditional_rate']:.1%})",
                transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=7.5)
    ax.set_yticks(range(len(spec["data"])), [r["stage"] for r in spec["data"]])
    ax.tick_params(axis="y", length=0, pad=9, labelsize=7.5)
    ax.set_ylim(len(spec["data"]) - 0.48, -0.52)
    ax.set_xlim(0, total)
    ax.set_xticks([0, 50, 100, 150, 199])
    ax.set_xlabel("Number of reactions", labelpad=5)
    ax.spines[["left", "right", "top"]].set_visible(False)
    figure_text(fig, 14, 247, "Sequential reaction validation", dimensions, fontsize=9.5, fontweight="bold")
    legend = [Patch(facecolor=colors[key], hatch=hatches[key], edgecolor="#555555", linewidth=0.5, label=label)
              for key, label in [("passed", "Passed"), ("failed", "Failed"), ("pending", "Pending"), ("previous", "Earlier attrition")]]
    fig.legend(handles=legend, loc="upper left", bbox_to_anchor=(14/504, 234/266),
               ncol=4, frameon=False, borderaxespad=0, columnspacing=1.4, handlelength=1.9)
    figure_text(fig, 392, 212, "Passed / entered", dimensions, fontsize=7.5, fontweight="bold")
    figure_text(fig, 14, 37, "Each stage receives only the preceding stage’s passes.", dimensions, fontsize=7.5)
    figure_text(fig, 14, 25, "Gray counts are earlier failures or pending reactions; excluded from this stage’s denominator.", dimensions, fontsize=7)
    figure_text(fig, 14, 8, "SYNTHETIC DEMONSTRATION  |  initial n = 199 reactions; final-stage passes = 65/199 (32.7%)", dimensions, fontsize=6.5)
    return audit_export(
        "figure2_stages", spec, provenance,
        {"counts": spec["data"], "excluded_records": 0,
         "rate_definition": "passed / entered at this stage; earlier failed and pending excluded",
         "final_overall_rate": spec["data"][-1]["passed"] / total}, fig=fig,
    )


def render_structures(spec, provenance):
    from rdkit import Chem

    width, height = spec["width_pt"], spec["height_pt"]
    root = ET.Element(tag("svg"), {"width": f"{width}pt", "height": f"{height}pt", "viewBox": f"0 0 {width} {height}"})
    ET.SubElement(root, tag("rect"), {"width": "100%", "height": "100%", "fill": "white"})
    text(root, 12, 17, "Mapped stereochemical structures", size=9.5, weight="bold")
    identities = []
    for i, record in enumerate(spec["data"]):
        x = 12 + 178 * i
        text(root, x, 36, f"{record['id']} | {record['label']}", size=8)
        child, details = molecular_svg(record["smiles"], 158, 109)
        child.set("x", str(x))
        child.set("y", "42")
        child.set("width", "158")
        child.set("height", "109")
        root.append(child)
        mol = Chem.MolFromSmiles(record["smiles"])
        Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
        maps = [atom.GetAtomMapNum() for atom in mol.GetAtoms()]
        centers = [(mol.GetAtomWithIdx(idx).GetAtomMapNum(), cip)
                   for idx, cip in Chem.FindMolChiralCenters(mol, includeUnassigned=True)]
        roundtrip = Chem.MolFromSmiles(details["canonical_isomeric_smiles"])
        assert maps == [1, 2, 3, 4, 5, 6]
        assert Chem.MolToSmiles(roundtrip, isomericSmiles=True) == Chem.MolToSmiles(mol, isomericSmiles=True)
        identities.append({"id": record["id"], "label": record["label"], **details,
                           "atom_maps": maps, "stereocenters_atom_map_and_CIP": centers,
                           "roundtrip_identity": "PASS"})
    assert identities[0]["stereocenters_atom_map_and_CIP"] != identities[1]["stereocenters_atom_map_and_CIP"]
    text(root, 12, 161, "Atom maps follow colons; 2D chemical depictions only.", size=7.2)
    text(root, 12, 175, "SYNTHETIC DEMONSTRATION", size=6)
    svg = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return audit_export("figure3_structures", spec, provenance,
                        {"identities": identities, "excluded_records": 0}, svg=svg)


def environment_and_sources():
    packages = ["matplotlib", "numpy", "pypdf", "pillow", "rdkit", "cairosvg", "defusedxml", "pypdfium2"]
    versions = {name: importlib.metadata.version(name) for name in packages}
    write_json(ROOT / "environment.json", {"python": sys.version, "executable_used": sys.executable,
                                           "platform": platform.platform(), "packages": versions})
    (ROOT / "requirements-versions.txt").write_text("\n".join(f"{name}=={version}" for name, version in versions.items()) + "\n")
    files = [path for folder in ("inputs", "source", "specs") for path in (ROOT / folder).rglob("*") if path.is_file()]
    write_json(ROOT / "source-index.json", {
        "source_repository_commit_at_start": "35f3cd0a74568dab19554e30ec974d5db187de83",
        "note": "Hashes identify the exact supplied inputs and skill-helper snapshot; commit alone may not contain uncommitted skill files.",
        "original_input_directory": "evaluation/figures/forward-inputs",
        "copied_files_sha256": {str(path.relative_to(ROOT)): sha(path) for path in files},
        "renderer_sha256": sha(Path(__file__)),
    })


def main():
    specs = prepare_specs()
    results = [
        render_predictions(*specs["figure1_predictions"]),
        render_stages(*specs["figure2_stages"]),
        render_structures(*specs["figure3_structures"]),
    ]
    environment_and_sources()
    (ROOT / "captions.md").write_text("\n\n".join(CAPTIONS.values()) + "\n")
    for result in results:
        print(result["name"], result["verdict"])
        for finding in result["findings"]:
            print(" ", finding["status"], finding["check"], finding["detail"])
    return int(any(result["verdict"] == "FAIL" for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
