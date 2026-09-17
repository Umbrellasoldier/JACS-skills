#!/usr/bin/env python3
"""Render chemistry figure specifications without inventing or filtering measurements."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import shutil
import textwrap
from pathlib import Path

from audit_figure import audit_layout, audit_pdf, measure_matplotlib, verdict
from figure_spec import digest, load

SKILL = Path(__file__).resolve().parents[1]
PALETTE = json.loads((SKILL / "assets/palettes.json").read_text())


def series(rows: list[dict], key: str) -> list[str]:
    return list(dict.fromkeys(row[key] for row in rows))


def encodings(spec: dict, names: list[str]) -> dict:
    mapping = {}
    for i, name in enumerate(names):
        mapping[name] = {
            "color": spec.get("colors", {}).get(name, PALETTE["categorical"][i]),
            "marker": PALETTE["markers"][i],
        }
    return mapping


def energy(fig, spec: dict) -> dict:
    ax = fig.subplots()
    rows = spec["data"]
    names = series(rows, "path")
    colors = encodings(spec, names)
    labels = set()
    for name in names:
        data = sorted((r for r in rows if r["path"] == name), key=lambda r: r["order"])
        color = colors[name]["color"]
        ax.plot([], [], color=color, label=name)
        for j, row in enumerate(data):
            x, y = row["order"], row["energy"]
            ax.plot([x - 0.17, x + 0.17], [y, y], color=color, linewidth=1.4)
            if j:
                prev = data[j - 1]
                ax.plot(
                    [prev["order"] + 0.17, x - 0.17],
                    [prev["energy"], y],
                    color=color,
                    linestyle="--",
                    linewidth=0.7,
                )
            key = (x, y, row["state"])
            if key not in labels:
                ax.annotate(
                    f"{row['state']}\n{y:g}",
                    (x, y),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    fontsize=7,
                )
                labels.add(key)
    ax.set_xticks([])
    ax.set_xlabel("Reaction coordinate (schematic)")
    ax.set_ylabel(f"Relative {spec['quantity']} ({spec['unit']})")
    values = [r["energy"] for r in rows]
    span = max(max(values) - min(values), 1)
    ax.set_ylim(min(values) - 0.12 * span, max(values) + 0.32 * span)
    ax.margins(x=0.12)
    ax.legend(loc="upper right")
    return {
        "encoding": colors,
        "energy_reference": spec["reference"],
        "conditions": spec["conditions"],
        "connectors": "schematic, not an interpolated reaction path",
    }


def parity(fig, spec: dict) -> dict:
    import numpy as np

    horizontal = spec["width_pt"] >= 400
    axes = fig.subplots(1, 2) if horizontal else fig.subplots(2, 1)
    ax, residual = axes
    rows = spec["data"]
    names = series(rows, "method")
    colors = encodings(spec, names)
    metrics = {}
    for name in names:
        data = [r for r in rows if r["method"] == name]
        reference = np.array([r["reference_value"] for r in data])
        predicted = np.array([r["predicted"] for r in data])
        error = predicted - reference
        opts = {**colors[name], "s": 15, "alpha": 0.8, "linewidths": 0.4}
        raster = len(data) > 10000
        ax.scatter(reference, predicted, label=name, rasterized=raster, **opts)
        residual.scatter(reference, error, rasterized=raster, **opts)
        metrics[name] = {
            "n": len(data),
            "mae": float(np.abs(error).mean()),
            "rmse": float(np.sqrt(np.mean(error**2))),
            "residual": "predicted minus reference",
        }
    values = [r[key] for r in rows for key in ("reference_value", "predicted")]
    lo, hi = min(values), max(values)
    if spec["scale"] == "log":
        lo, hi = lo / 1.1, hi * 1.1
        ax.set_xscale("log")
        ax.set_yscale("log")
        residual.set_xscale("log")
    else:
        padding = max((hi - lo) * 0.08, 0.1)
        lo, hi = lo - padding, hi + padding
    ax.plot([lo, hi], [lo, hi], color="#555555", linestyle="--", linewidth=0.7)
    ax.set(
        xlim=(lo, hi),
        ylim=(lo, hi),
        xlabel=f"Reference ({spec['unit']})",
        ylabel=f"Predicted ({spec['unit']})",
    )
    residual.axhline(0, color="#555555", linestyle="--", linewidth=0.7)
    residual.set(
        xlim=(lo, hi), xlabel=f"Reference ({spec['unit']})", ylabel=f"Residual ({spec['unit']})"
    )
    ax.legend(loc="upper left")
    # Reserve physical headroom for labels even when aspect-constrained axes
    # consume the available subplot height in a different font environment.
    fig.get_layout_engine().set(rect=(0, 0, 1, 1 - 12 / spec["height_pt"]))
    for label, panel in zip(("a", "b"), axes, strict=True):
        panel.set_box_aspect(1)
        # Titles participate in constrained layout across Matplotlib versions;
        # offset annotations can extend beyond the page even when axes fit.
        panel.set_title(label, loc="left", pad=8, fontweight="bold", fontsize=8)
    return {
        "encoding": colors,
        "metrics": metrics,
        "comparable_groups": [
            {
                "panels": ["0", "1"],
                "orientation": "row" if horizontal else "column",
                "equal_size": True,
            }
        ],
    }


def stages(fig, spec: dict) -> dict:
    ax = fig.subplots()
    colors = PALETTE["stages"]
    for i, row in enumerate(spec["data"]):
        left = 0
        for key, hatch in (("passed", ""), ("failed", "///"), ("pending", "..")):
            ax.barh(
                i,
                row[key],
                left=left,
                color=colors[key],
                height=0.62,
                hatch=hatch,
                edgecolor="#444444",
                linewidth=0.5,
                label=key.capitalize() if i == 0 else None,
            )
            left += row[key]
        omitted = spec["population_total"] - row["entered"]
        ax.barh(
            i,
            omitted,
            left=left,
            color=colors["previous_attrition"],
            height=0.62,
            edgecolor="none",
            label="Earlier attrition" if i == 0 else None,
        )
        ax.text(
            spec["population_total"] * 1.035,
            i,
            f"{row['passed']}/{row['entered']}",
            va="center",
            fontsize=7,
        )
    ax.set_yticks(range(len(spec["data"])), [r["stage"] for r in spec["data"]])
    ax.invert_yaxis()
    ax.set_xlim(0, spec["population_total"] * 1.36)
    ax.set_xlabel(f"Number of {spec['unit_of_analysis']}")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncol=2, fontsize=7)
    return {
        "counts": spec["data"],
        "rate_label": "passed / entered at this stage",
        "earlier_attrition": (
            "failed or pending at prior stages, never included in this stage's denominator"
        ),
    }


def comparison(fig, spec: dict) -> dict:
    import numpy as np

    ax = fig.subplots()
    rows = spec["data"]
    names = series(rows, "method")
    colors = encodings(spec, names)
    ids = series(rows, "reaction_id")
    lookup = {(r["reaction_id"], r["method"]): r["value"] for r in rows}
    for reaction in ids:
        ax.plot(
            range(len(names)),
            [lookup[reaction, m] for m in names],
            color="#BBBBBB",
            linewidth=0.5,
            alpha=0.45,
            zorder=1,
        )
    summaries = {}
    for i, name in enumerate(names):
        values = [lookup[r, name] for r in ids]
        ax.scatter(
            [i] * len(values),
            values,
            s=16,
            **colors[name],
            zorder=2,
            rasterized=len(values) > 10000,
        )
        median = float(np.median(values))
        ax.plot([i - 0.14, i + 0.14], [median, median], color="black", linewidth=1.2, zorder=3)
        summaries[name] = {"n": len(values), "median": median}
    ax.set_xticks(range(len(names)), names)
    ax.set_ylabel(f"{spec['metric']} ({spec['unit']})")
    ax.set_yscale(spec["scale"])
    ax.margins(x=0.2)
    return {
        "encoding": colors,
        "summary": summaries,
        "paired_lines": "same reaction across methods",
        "black_segment": "median; no uncertainty interval inferred",
    }


def workflow(fig, spec: dict) -> dict:
    import math

    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fig.set_layout_engine(None)
    ax = fig.add_axes((0.04, 0.13, 0.92, 0.82))
    ax.set_axis_off()
    nodes = spec["data"]
    columns = int(spec.get("columns", 3 if len(nodes) > 2 else len(nodes)))
    if columns < 1:
        raise ValueError("columns must be positive")
    rows = math.ceil(len(nodes) / columns)
    positions = {}
    w, h = 0.76 / columns, 0.62 / rows
    for i, node in enumerate(nodes):
        x = (i % columns + 0.5) / columns
        y = 1 - (i // columns + 0.5) / rows
        positions[node["id"]] = (x, y)
        box = FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.005,rounding_size=0.012",
            facecolor="#EAF2F7",
            edgecolor="#0072B2",
            linewidth=0.8,
        )
        ax.add_patch(box)
        ax.text(
            x,
            y,
            textwrap.fill(node["label"], width=int(spec.get("wrap_chars", 18))),
            ha="center",
            va="center",
            fontsize=8,
        )
    edges = spec.get("edges", [[nodes[i]["id"], nodes[i + 1]["id"]] for i in range(len(nodes) - 1)])
    for start, end in edges:
        x1, y1 = positions[start]
        x2, y2 = positions[end]
        if y1 == y2:
            sign = 1 if x2 > x1 else -1
            p1, p2 = (x1 + sign * w / 2, y1), (x2 - sign * w / 2, y2)
        else:
            sign = 1 if y2 > y1 else -1
            p1, p2 = (x1, y1 + sign * h / 2), (x2, y2 - sign * h / 2)
        ax.add_patch(
            FancyArrowPatch(
                p1,
                p2,
                arrowstyle="-|>",
                mutation_scale=8,
                linewidth=0.8,
                color="#444444",
                connectionstyle="arc3,rad=0",
            )
        )
    return {
        "nodes": [r["id"] for r in nodes],
        "edges": edges,
        "meaning": (
            "author-supplied process or concept; arrows do not independently establish mechanism"
        ),
    }


DRAW = {
    "energy": energy,
    "parity": parity,
    "stages": stages,
    "comparison": comparison,
    "workflow": workflow,
}


def copy_assets(spec: dict, base: Path, prefix: Path) -> None:
    for i, row in enumerate(spec.get("panels", spec.get("data", []))):
        if "svg" not in row:
            continue
        source = (base / row["svg"]).resolve()
        target_dir = prefix.parent / (prefix.name + ".assets")
        target_dir.mkdir(exist_ok=True)
        target = target_dir / f"{i:02d}_{source.name}"
        if source != target.resolve():
            shutil.copyfile(source, target)
        row["svg"] = target.relative_to(prefix.parent).as_posix()


def render(spec_path: Path, output: Path, overwrite: bool = False) -> dict:
    spec, provenance = load(spec_path)
    if output.suffix:
        raise ValueError("Output is a prefix without a file extension")
    output.parent.mkdir(parents=True, exist_ok=True)
    extensions = [".svg", ".pdf", ".png", ".qa.json", ".spec.json", ".caption.txt", ".layout.json"]
    if spec["profile"] == "toc" or spec.get("tiff", False):
        extensions.append(".tiff")
    if not overwrite and any(output.with_suffix(ext).exists() for ext in extensions):
        raise ValueError("Output exists; choose a new prefix or use --overwrite")
    floor = 6 if spec["profile"] == "toc" else 4.5
    raster_dpi = {"color": 300, "grayscale": 600, "line_art": 1200}[spec["raster_class"]]
    layout = None
    if spec["kind"] in {"structures", "assembly"}:
        import io

        import cairosvg
        from PIL import Image
        from svg_panels import draw

        svg, details = draw(spec, spec_path.parent)
        output.with_suffix(".svg").write_bytes(svg)
        cairosvg.svg2pdf(bytestring=svg, write_to=str(output.with_suffix(".pdf")))
        png = cairosvg.svg2png(
            bytestring=svg,
            output_width=round(spec["width_pt"] * 300 / 72),
            output_height=round(spec["height_pt"] * 300 / 72),
        )
        Image.open(io.BytesIO(png)).save(output.with_suffix(".png"), dpi=(300, 300))
        if ".tiff" in extensions:
            tiff_pixels = cairosvg.svg2png(
                bytestring=svg,
                output_width=round(spec["width_pt"] * raster_dpi / 72),
                output_height=round(spec["height_pt"] * raster_dpi / 72),
            )
            Image.open(io.BytesIO(tiff_pixels)).convert("RGB").save(
                output.with_suffix(".tiff"),
                dpi=(raster_dpi, raster_dpi),
                compression="tiff_lzw",
            )
    else:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with plt.style.context(str(SKILL / "assets/jacs.mplstyle")):
            fig = plt.figure(
                figsize=(spec["width_pt"] / 72, spec["height_pt"] / 72), layout="constrained"
            )
            try:
                details = DRAW[spec["kind"]](fig, spec)
                if spec["data_status"] == "synthetic":
                    fig.supxlabel("SYNTHETIC DEMONSTRATION", fontsize=6)
                # Complete layout once, then keep the audited axes positions in
                # every format instead of re-solving layout for PDF/SVG/PNG DPI.
                fig.canvas.draw()
                fig.set_layout_engine("none")
                layout = measure_matplotlib(fig, details.pop("comparable_groups", []))
                for extension in (".svg", ".pdf", ".png"):
                    fig.savefig(output.with_suffix(extension), dpi=300)
                if ".tiff" in extensions:
                    fig.savefig(
                        output.with_suffix(".tiff"),
                        dpi=raster_dpi,
                        pil_kwargs={"compression": "tiff_lzw"},
                    )
            finally:
                plt.close(fig)
    result = audit_pdf(output.with_suffix(".pdf"), spec["width_pt"], spec["height_pt"], floor)
    if layout:
        result["findings"].extend(audit_layout(layout, floor))
        output.with_suffix(".layout.json").write_text(
            json.dumps(layout, ensure_ascii=False, indent=2) + "\n"
        )
    else:
        result["findings"].append(
            {
                "check": "embedded_panel_layout",
                "status": "UNKNOWN",
                "detail": "SVG labels, molecular bonds and panel collisions need visual inspection",
            }
        )
    result.update(
        schema_version=1,
        kind=spec["kind"],
        profile=spec["profile"],
        data_status=spec["data_status"],
        provenance=provenance,
        details=details,
        claim=spec["claim"],
        caption=spec["caption"],
        visual_review="required",
        renderer_sha256=digest(Path(__file__)),
        implementation_sha256={
            name: digest(Path(__file__).parent / name)
            for name in ("plot_figures.py", "figure_spec.py", "audit_figure.py", "svg_panels.py")
        },
        raster_export={
            "class": spec["raster_class"],
            "tiff_dpi": raster_dpi,
            "preview_png_dpi": 300,
            "embedded_source_resolution": "not established by export DPI",
        },
    )
    packages = ["matplotlib", "numpy", "pypdf", "pillow"]
    if spec["kind"] in {"structures", "assembly"}:
        packages += ["cairosvg", "defusedxml"]
    if spec["kind"] == "structures" and any("smiles" in row for row in spec["data"]):
        packages.append("rdkit")
    result["versions"] = {package: importlib.metadata.version(package) for package in packages}
    result["verdict"] = verdict(result["findings"])
    spec.pop("input_csv", None)
    copy_assets(spec, spec_path.parent, output)
    output.with_suffix(".spec.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n"
    )
    output.with_suffix(".caption.txt").write_text(spec["caption"] + "\n", encoding="utf-8")
    result["files"] = {
        ext: {"name": output.with_suffix(ext).name, "sha256": digest(output.with_suffix(ext))}
        for ext in extensions
        if ext != ".qa.json" and output.with_suffix(ext).exists()
    }
    output.with_suffix(".qa.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument(
        "--output", type=Path, required=True, help="Output prefix without extension"
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        result = render(args.spec, args.output, args.overwrite)
    except (OSError, ValueError, ImportError) as error:
        parser.exit(2, f"error: {error}\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "visual_review": result["visual_review"],
                "findings": result["findings"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return int(result["verdict"] == "FAIL")


if __name__ == "__main__":
    raise SystemExit(main())
