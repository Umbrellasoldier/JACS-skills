"""Configurable project encodings and display-only unit typography."""

from __future__ import annotations

import json
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
PALETTE = json.loads((SKILL / "assets/palettes.json").read_text())
UNITS = {
    "kcal/mol": r"$\mathrm{kcal\ mol^{-1}}$",
    "kJ/mol": r"$\mathrm{kJ\ mol^{-1}}$",
    "cm-1": r"$\mathrm{cm^{-1}}$",
    "mA/cm2": r"$\mathrm{mA\ cm^{-2}}$",
    "kJ/mol/nm": r"$\mathrm{kJ\ mol^{-1}\ nm^{-1}}$",
    "a.u.": "a.u.",
}


def axis_label(quantity: str, unit: str) -> str:
    """Change notation only; never convert values or invent a missing unit."""
    if unit == "dimensionless":
        return quantity
    return f"{quantity} ({UNITS.get(unit, unit)})"


def encodings(spec: dict, names: list[str]) -> dict:
    return {
        name: {
            "color": spec.get("colors", {}).get(name, PALETTE["categorical"][i]),
            "fill": spec.get("colors", {}).get(name, PALETTE["fills"][i]),
            "marker": PALETTE["markers"][i],
            "linestyle": PALETTE["linestyles"][i],
        }
        for i, name in enumerate(names)
    }


def point_style(encoding: dict) -> dict:
    return {
        "facecolors": encoding["fill"],
        "edgecolors": encoding["color"],
        "marker": encoding["marker"],
        "linewidths": 0.65,
    }


def quiet_grid(ax, axis: str = "y") -> None:
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color=PALETTE["guide"], linewidth=0.5, alpha=0.65)
