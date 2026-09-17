"""Distribution, estimate, curve and matrix renderers with explicit statistical meaning."""

from __future__ import annotations

import textwrap

from figure_style import PALETTE, axis_label, encodings, point_style, quiet_grid


def distribution(fig, spec: dict, ax=None) -> dict:
    import numpy as np
    from matplotlib.colors import to_rgba

    ax = fig.subplots() if ax is None else ax
    rows = spec["data"]
    names = spec["group_order"]
    style = encodings(spec, names)
    mode = spec["display"]
    summaries = {}
    skipped = []
    sensitivity = {}
    rng = np.random.default_rng(0)
    all_values = np.array([r["value"] for r in rows])
    transform = spec.get("value_transform", "identity")
    if transform == "absolute":
        all_values = np.abs(all_values)
    pad = max(float(np.ptp(all_values)), 0.1) * 0.035
    domain = (
        0 if transform == "absolute" else float(all_values.min()) - pad,
        float(all_values.max()) + pad,
    )
    for i, name in enumerate(names):
        values = np.array([r["value"] for r in rows if r["group"] == name])
        if transform == "absolute":
            values = np.abs(values)
        q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75], method="linear")
        summaries[name] = {
            "n": len(values),
            "q1": float(q1),
            "median": float(median),
            "q3": float(q3),
        }
        color, fill = style[name]["color"], style[name]["fill"]
        if mode == "box":
            result = ax.boxplot(
                [values],
                positions=[i],
                widths=0.5,
                patch_artist=True,
                showfliers=False,
                whis=1.5,
                manage_ticks=False,
                medianprops={"color": PALETTE["text"], "linewidth": 1.1},
                boxprops={"facecolor": to_rgba(fill, 0.30), "edgecolor": color, "linewidth": 0.8},
                whiskerprops={"color": color, "linewidth": 0.8},
                capprops={"color": color, "linewidth": 0.8},
            )
            # Record the actual observed whisker endpoints, not ±1.5 IQR fence values.
            summaries[name]["whiskers"] = [
                float(result["whiskers"][j].get_ydata()[1]) for j in (0, 1)
            ]
        elif mode == "violin":
            if len(values) >= 5 and np.ptp(values) > 0:
                body = ax.violinplot(
                    [values],
                    positions=[i],
                    widths=0.72,
                    showextrema=False,
                    points=150,
                    bw_method=spec["bandwidth"],
                )["bodies"][0]
                for path in body.get_paths():
                    path.vertices[:, 0] = np.minimum(path.vertices[:, 0], i)
                body.set(facecolor=to_rgba(fill, 0.45), edgecolor=color, linewidth=0.8, alpha=None)
                grid = np.linspace(values.min(), values.max(), 150)
                mode_counts = []
                for factor in (spec["bandwidth"], 2 * spec["bandwidth"]):
                    h = factor * np.std(values, ddof=1)
                    density = np.exp(-0.5 * ((grid[:, None] - values) / h) ** 2).mean(axis=1)
                    mode_counts.append(
                        int(np.sum((density[1:-1] > density[:-2]) & (density[1:-1] > density[2:])))
                    )
                sensitivity[name] = mode_counts
            else:
                skipped.append(name)
            ax.plot(
                [i - 0.30, i],
                [median, median],
                color=PALETTE["text"],
                linewidth=1.2,
                zorder=4,
            )
        elif mode == "ecdf":
            values = np.sort(values)
            x = np.r_[domain[0], values, domain[1]]
            y = np.r_[0, np.arange(1, len(values) + 1) / len(values), 1]
            ax.step(
                x,
                y,
                where="post",
                color=color,
                linestyle=style[name]["linestyle"],
                label=f"{name} (n = {len(values)})",
                linewidth=1.25,
            )
            summaries[name]["cumulative_mass"] = 1.0
        elif mode == "histogram":
            counts, edges = np.histogram(values, bins=spec["bin_edges"])
            ax.stairs(
                counts,
                edges,
                color=color,
                linewidth=1.1,
                linestyle=style[name]["linestyle"],
                label=f"{name} (n = {len(values)})",
            )
            summaries[name]["bin_counts"] = counts.tolist()
        if mode in {"box", "violin"}:
            # Jitter affects only categorical position, never the measurement coordinate.
            jitter = (
                rng.uniform(0.08, 0.30, len(values))
                if mode == "violin"
                else rng.uniform(-0.22, 0.22, len(values))
            )
            ax.scatter(
                i + jitter,
                values,
                s=5 if len(values) > 40 else 8,
                **{**point_style(style[name], open_fill=True), "linewidths": 0.45},
                zorder=3,
                rasterized=len(values) > 10000,
            )
    if mode in {"box", "violin"}:
        labels = [f"{textwrap.fill(n, 16)}\nn = {summaries[n]['n']}" for n in names]
        ax.set_xticks(range(len(names)), labels)
        ax.set_ylabel(axis_label(spec["metric"], spec["unit"]))
        ax.set_yscale(spec["scale"])
        ax.margins(x=0.2, y=0.12)
    else:
        ax.set_xlabel(axis_label(spec["metric"], spec["unit"]))
        ax.set_ylabel("Cumulative fraction" if mode == "ecdf" else "Count")
        ax.set_ylim(bottom=0, top=1.04 if mode == "ecdf" else None)
        ax.legend(loc="best", handlelength=2.2)
        if mode == "ecdf":
            ax.set_xlim(domain)
    if spec.get("zero_reference") and spec["scale"] == "linear":
        ax.axhline(0, color=PALETTE["axis"], linewidth=0.7, linestyle="--", zorder=1.5)
    quiet_grid(ax)
    return {
        "encoding": style,
        "summary": summaries,
        "display": mode,
        "box_definition": "Q1–Q3, median, observed whiskers within 1.5 IQR; every raw point shown"
        if mode == "box"
        else None,
        "violin_bandwidth_factor": spec.get("bandwidth") if mode == "violin" else None,
        "kde_mode_counts_at_bandwidth_and_double": sensitivity,
        "bandwidth_sensitive_groups": [k for k, v in sensitivity.items() if v[0] != v[1]],
        "display_transform": transform,
        "violin_normalization": "Equal maximum width; KDE computed in raw measurement units"
        if mode == "violin"
        else None,
        "violin_skipped_groups": skipped,
        "violin_limit": (
            "Groups with fewer than five observations or zero spread show raw points only"
        ),
        "jitter": "seed 0, categorical coordinate only" if mode in {"box", "violin"} else None,
        "inference": "Descriptive display; no significance or uncertainty inferred",
    }


def interval(fig, spec: dict, ax=None) -> dict:
    import numpy as np

    ax = fig.subplots() if ax is None else ax
    rows = spec["data"]
    style = encodings(spec, ["Estimate"])["Estimate"]
    estimates = np.array([r["estimate"] for r in rows])
    errors = np.array(
        [[r["estimate"] - r["lower"] for r in rows], [r["upper"] - r["estimate"] for r in rows]]
    )
    y = np.arange(len(rows))
    ax.errorbar(
        estimates,
        y,
        xerr=errors,
        fmt="none",
        ecolor=style["color"],
        elinewidth=1.05,
        capsize=2.5,
        capthick=0.8,
        zorder=2,
    )
    ax.scatter(estimates, y, s=12, **point_style(style, open_fill=True), zorder=3)
    ax.set_yticks(y, [textwrap.fill(r["label"], 24) for r in rows])
    ax.invert_yaxis()
    if "reference_value" in spec:
        ax.axvline(spec["reference_value"], color=PALETTE["axis"], linewidth=0.7, linestyle="--")
    ax.set_xlabel(axis_label(spec["metric"], spec["unit"]))
    ax.set_xscale(spec["scale"])
    ax.margins(x=0.12, y=0.2)
    quiet_grid(ax, "x")
    return {
        "interval_definition": spec["interval_definition"],
        "estimates": rows,
        "calculation": "Supplied estimates and bounds rendered unchanged; no interval inferred",
    }


def curve(fig, spec: dict, ax=None) -> dict:
    from matplotlib.ticker import NullFormatter

    ax = fig.subplots() if ax is None else ax
    rows = spec["data"]
    names = list(dict.fromkeys(row["series"] for row in rows))
    style = encodings(spec, names)
    bands = []
    for name in names:
        data = [r for r in rows if r["series"] == name]
        x, y = [r["x"] for r in data], [r["y"] for r in data]
        role, encoding = spec["series_roles"][name], style[name]
        if "lower" in data[0]:
            ax.fill_between(
                x,
                [r["lower"] for r in data],
                [r["upper"] for r in data],
                color=encoding["fill"],
                alpha=0.28,
                linewidth=0,
                zorder=1,
            )
            bands.append(name)
        if role == "observed":
            ax.scatter(
                x,
                y,
                s=12,
                **point_style(encoding, open_fill=True),
                label=name,
                zorder=3,
                rasterized=len(data) > 10000,
            )
            if spec.get("connect_observations", False):
                ax.plot(x, y, color=encoding["color"], linewidth=0.65, alpha=0.65, zorder=2)
        else:
            ax.plot(
                x,
                y,
                label=name,
                color=PALETTE["axis"] if role == "reference" else encoding["color"],
                linestyle="--" if role == "reference" else encoding["linestyle"],
                linewidth=0.8 if role == "reference" else 1.15,
                zorder=2,
            )
    ax.set_xlabel(axis_label(spec["x_quantity"], spec["x_unit"]))
    ax.set_ylabel(axis_label(spec["y_quantity"], spec["y_unit"]))
    ax.set_xscale(spec["x_scale"])
    ax.set_yscale(spec["y_scale"])
    if spec.get("reverse_x", False):
        ax.invert_xaxis()
    if spec.get("zero_reference", False):
        ax.axhline(0, color=PALETTE["axis"], linewidth=0.65, linestyle="--")
    ax.legend(loc="best", handlelength=2.3)
    ax.margins(x=0.06, y=0.12)
    if "x_ticks" in spec:
        limits = ax.get_xlim()
        ax.set_xticks(spec["x_ticks"], [f"{v:g}" for v in spec["x_ticks"]])
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xlim(limits)
    quiet_grid(ax)
    return {
        "encoding": style,
        "series_roles": spec["series_roles"],
        "banded_series": bands,
        "interval_definition": spec.get("interval_definition"),
        "fitting": "None; supplied samples and bounds only",
        "connectors": "Visual guides through supplied observations"
        if spec.get("connect_observations")
        else None,
    }


def heatmap(fig, spec: dict, ax=None) -> dict:
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
    from matplotlib.patches import Rectangle

    ax = fig.subplots() if ax is None else ax
    row_names, col_names = spec["row_order"], spec["column_order"]
    values = np.full((len(row_names), len(col_names)), np.nan)
    for row in spec["data"]:
        if row["value"] is not None:
            values[row_names.index(row["row"]), col_names.index(row["column"])] = row["value"]
    cmap = LinearSegmentedColormap.from_list("jacs_soft", PALETTE[spec["color_scale"]])
    cmap.set_bad("#EDF0F2")
    if spec["color_scale"] == "diverging":
        norm = TwoSlopeNorm(spec["center"], spec["vmin"], spec["vmax"])
    else:
        norm = Normalize(spec["vmin"], spec["vmax"])
    # Discrete vector cells avoid viewer-dependent smoothing of a tiny SVG raster.
    im = ax.pcolormesh(
        np.arange(len(col_names) + 1) - 0.5,
        np.arange(len(row_names) + 1) - 0.5,
        np.ma.masked_invalid(values),
        cmap=cmap,
        norm=norm,
        shading="flat",
        edgecolors="white",
        linewidth=0.8,
    )
    ax.set_xlim(-0.5, len(col_names) - 0.5)
    ax.set_ylim(len(row_names) - 0.5, -0.5)
    ax.set_xticks(range(len(col_names)), [textwrap.fill(n, 12) for n in col_names])
    ax.set_yticks(range(len(row_names)), [textwrap.fill(n, 18) for n in row_names])
    ax.tick_params(length=0)
    ax.set_xticks(np.arange(-0.5, len(col_names), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(row_names), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1)
    ax.tick_params(which="minor", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for (i, j), value in np.ndenumerate(values):
        if np.isnan(value):
            ax.add_patch(
                Rectangle(
                    (j - 0.5, i - 0.5),
                    1,
                    1,
                    facecolor="#F5F6F7",
                    edgecolor="#C9CED3",
                    hatch="///",
                    linewidth=0.3,
                )
            )
        if spec.get("annotate", True) or np.isnan(value):
            if np.isnan(value):
                label, color = spec.get("missing_label", "NA"), PALETTE["text"]
            else:
                label = f"{value:.2g}"
                rgb = np.array(cmap(norm(value))[:3])
                linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
                luminance = float(linear @ [0.2126, 0.7152, 0.0722])
                color = "white" if luminance < 0.3 else PALETTE["text"]
            ax.text(j, i, label, ha="center", va="center", fontsize=7, color=color)
    bar = fig.colorbar(im, ax=ax, pad=0.035, fraction=0.055)
    ticks = spec.get(
        "colorbar_ticks",
        [spec["vmin"], spec["center"], spec["vmax"]]
        if spec["color_scale"] == "diverging"
        else np.linspace(spec["vmin"], spec["vmax"], 4),
    )
    bar.set_ticks(ticks)
    bar.outline.set_visible(False)
    bar.solids.set_rasterized(False)
    bar.solids.set_edgecolor("face")
    bar.set_label(axis_label(spec["quantity"], spec["unit"]), fontsize=7)
    return {
        "color_scale": spec["color_scale"],
        "limits": [spec["vmin"], spec["vmax"]],
        "center": spec.get("center"),
        "missing_cells": int(np.isnan(values).sum()),
        "observed_cells": int(np.isfinite(values).sum()),
        "missing_encoding": "Hatched neutral cell and explicit missing label; distinct from zero",
        "row_order": row_names,
        "column_order": col_names,
    }
