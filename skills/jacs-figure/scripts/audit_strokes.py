"""Audit painted PDF path strokes, including affine transforms and invoked Form objects."""

from __future__ import annotations

import copy
import math


def multiply(left, right):
    a, b, c, d, e, f = left
    g, h, i, j, k, offset_y = right
    return (
        a * g + c * h,
        b * g + d * h,
        a * i + c * j,
        b * i + d * j,
        a * k + c * offset_y + e,
        b * k + d * offset_y + f,
    )


def scales(matrix):
    a, b, c, d, _, _ = matrix
    norm = a * a + b * b + c * c + d * d
    determinant = a * d - b * c
    high = math.sqrt((norm + math.sqrt(max(0, norm * norm - 4 * determinant * determinant))) / 2)
    return (abs(determinant) / high if high else 0, high)


def audit_strokes(reader, floor=0.5):
    from pypdf.generic import ContentStream

    records, unknown = [], []

    def scan(stream, resources, inherited, trail=()):
        if hasattr(resources, "get_object"):
            resources = resources.get_object()
        state = copy.deepcopy(inherited)
        stack = []
        path = False
        for args, op in ContentStream(stream, reader).operations:
            if op == b"q":
                stack.append(copy.deepcopy(state))
            elif op == b"Q":
                if stack:
                    state = stack.pop()
                else:
                    unknown.append("Unbalanced graphics state")
            elif op == b"cm":
                state["matrix"] = multiply(state["matrix"], tuple(map(float, args)))
            elif op == b"w":
                state["width"] = float(args[0])
            elif op in (b"G", b"RG", b"K", b"g", b"rg", b"k"):
                key = "stroke" if op.isupper() else "fill"
                state[key] = (op.upper(), tuple(map(float, args)))
            elif op in (b"CS", b"SC", b"SCN", b"cs", b"sc", b"scn"):
                state["stroke" if op.isupper() else "fill"] = None
            elif op == b"gs":
                states = resources.get("/ExtGState", {})
                if hasattr(states, "get_object"):
                    states = states.get_object()
                ext = states.get(args[0])
                if ext is not None:
                    ext = ext.get_object()
                    for source, target in (
                        ("/LW", "width"),
                        ("/CA", "stroke_alpha"),
                        ("/ca", "fill_alpha"),
                    ):
                        if source in ext:
                            state[target] = float(ext[source])
                    if ext.get("/SMask", "/None") != "/None":
                        unknown.append("Soft-mask visibility is not established")
            elif op in (b"m", b"l", b"c", b"v", b"y", b"re"):
                path = True
            elif op in (b"S", b"s", b"B", b"B*", b"b", b"b*"):
                if path and state["stroke_alpha"] > 0:
                    low, high = scales(state["matrix"])
                    lower, upper = state["width"] * low, state["width"] * high
                    filled = op in (b"B", b"B*", b"b", b"b*")
                    solid_silhouette = (
                        filled
                        and state["fill"] is not None
                        and state["fill"] == state["stroke"]
                        and state["fill_alpha"] == state["stroke_alpha"] == 1
                    )
                    status = "PASS"
                    if lower + 1e-6 < floor:
                        status = "WARN" if solid_silhouette or upper + 1e-6 >= floor else "FAIL"
                    records.append(
                        {
                            "minimum_pt": lower,
                            "maximum_pt": upper,
                            "status": status,
                            "filled_same_color": solid_silhouette,
                            "object": "/".join(map(str, trail)) or "page",
                        }
                    )
                path = False
            elif op in (b"f", b"F", b"f*", b"n"):
                path = False
            elif op == b"Do":
                objects = resources.get("/XObject", {})
                if hasattr(objects, "get_object"):
                    objects = objects.get_object()
                obj = objects.get(args[0])
                if obj is None:
                    unknown.append("Unresolved XObject")
                    continue
                obj = obj.get_object()
                if obj.get("/Subtype") != "/Form":
                    if obj.get("/Subtype") == "/Image":
                        unknown.append("Embedded raster strokes require separate inspection")
                    continue
                if len(trail) >= 16 or id(obj) in state["forms"]:
                    unknown.append("Recursive or deeply nested Form")
                    continue
                child = copy.deepcopy(state)
                child["forms"].add(id(obj))
                child["matrix"] = multiply(
                    child["matrix"], tuple(map(float, obj.get("/Matrix", [1, 0, 0, 1, 0, 0])))
                )
                scan(obj, obj.get("/Resources", resources), child, (*trail, str(args[0])))

    for page in reader.pages:
        unit = float(page.get("/UserUnit", 1))
        state = {
            "matrix": (unit, 0, 0, unit, 0, 0),
            "width": 1,
            "stroke": (b"G", (0,)),
            "fill": (b"G", (0,)),
            "stroke_alpha": 1,
            "fill_alpha": 1,
            "forms": set(),
        }
        try:
            scan(page.get_contents(), page.get("/Resources", {}), state)
        except (ValueError, TypeError, KeyError, AttributeError, NotImplementedError) as error:
            unknown.append(str(error))
    thin = [r for r in records if r["status"] != "PASS"]
    status = "FAIL" if any(r["status"] == "FAIL" for r in thin) else "WARN" if thin else "PASS"
    if unknown and status == "PASS":
        status = "UNKNOWN"
    return {
        "check": "pdf_path_strokes",
        "status": status,
        "detail": (
            f"{len(records)} painted path strokes checked at {floor:g} pt; "
            f"{len(thin)} require attention"
        ),
        "minimum_stroke_pt": min((r["minimum_pt"] for r in records), default=None),
        "thin_strokes": thin,
        "unknown": sorted(set(unknown)),
        "scope": (
            "Painted paths and invoked Forms; excludes text-glyph outlines, "
            "tiling-pattern strokes and clipping visibility. Same-color filled outlines "
            "and anisotropic bounds need review."
        ),
    }
