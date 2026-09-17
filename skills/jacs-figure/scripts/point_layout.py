"""Deterministic packing on a categorical axis; measurement coordinates never change."""

from __future__ import annotations

import math


def pack_points(fig):
    import numpy as np

    reports = []
    for ax in fig.axes:
        for collection in ax.collections:
            config = getattr(collection, "_jacs_swarm", None)
            if config is None:
                continue
            offsets = np.array(collection.get_offsets(), dtype=float)
            center, lower, upper = config
            pixels = ax.transData.transform(offsets)
            # A conservative bounding circle includes the marker path and its outline.
            marker_diameter = 2 * max(
                float(np.linalg.norm(path.vertices, axis=1).max())
                for path in collection.get_paths()
            )
            radius = (
                (
                    math.sqrt(float(max(collection.get_sizes()))) * marker_diameter
                    + float(max(collection.get_linewidths()))
                    + 0.2
                )
                * fig.dpi
                / 72
            )
            left = ax.transData.transform((center + lower, offsets[0, 1]))[0]
            right = ax.transData.transform((center + upper, offsets[0, 1]))[0]
            middle = (left + right) / 2
            placed = []
            collisions = 0
            for index in np.argsort(pixels[:, 1], kind="stable"):
                y = pixels[index, 1]
                nearby = [(x0, y0) for x0, y0 in placed if abs(y - y0) < radius]
                candidates = [middle, left, right]
                for x0, y0 in nearby:
                    shift = math.sqrt(max(0, radius**2 - (y - y0) ** 2))
                    candidates.extend([x0 - shift, x0 + shift])
                candidates = sorted(
                    {x for x in candidates if left <= x <= right},
                    key=lambda x: (abs(x - middle), x),
                )
                score = [
                    min(((x - x0) ** 2 + (y - y0) ** 2 for x0, y0 in nearby), default=float("inf"))
                    for x in candidates
                ]
                eligible = [i for i, distance in enumerate(score) if distance >= radius**2 - 1e-6]
                chosen = eligible[0] if eligible else int(np.argmax(score))
                collisions += not bool(eligible)
                x = candidates[chosen]
                offsets[index, 0] = ax.transData.inverted().transform((x, y))[0]
                placed.append((x, y))
            collection.set_offsets(offsets)
            reports.append(
                {
                    "n": len(offsets),
                    "unresolved_spacing": collisions,
                    "measurement_coordinates_preserved": True,
                }
            )
    return reports
