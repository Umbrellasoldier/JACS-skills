"""Compose local, self-contained SVG panels and draw supplied molecular identities."""

from __future__ import annotations

import copy
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


def tag(name: str) -> str:
    return f"{{{SVG}}}{name}"


def parse_svg(data: bytes) -> ET.Element:
    from defusedxml.ElementTree import fromstring

    root = fromstring(data)
    if root.tag != tag("svg"):
        raise ValueError("Expected an SVG root")
    for element in root.iter():
        if element.tag.split("}")[-1] in {"script", "foreignObject"}:
            raise ValueError("SVG panels must contain static scientific artwork")
        for key, value in element.attrib.items():
            if key.split("}")[-1].lower().startswith("on"):
                raise ValueError("SVG event handlers are not supported")
            if key.split("}")[-1] == "href" and not value.startswith("#"):
                embedded_image = element.tag == tag("image") and re.fullmatch(
                    r"data:image/(?:png|jpeg);base64,[A-Za-z0-9+/=\s]+", value
                )
                if not embedded_image:
                    raise ValueError("SVG panels must be self-contained without external resources")
            for target in re.findall(r"url\(\s*['\"]?([^)'\"]+)", value, re.I):
                if not target.startswith("#"):
                    raise ValueError("External SVG paint resources are not supported")
        if element.tag == tag("style") and element.text:
            if "@import" in element.text.lower() or any(
                not t.startswith("#")
                for t in re.findall(r"url\(\s*['\"]?([^)'\"]+)", element.text, re.I)
            ):
                raise ValueError("External CSS resources are not supported")
    return root


def viewbox(root: ET.Element) -> list[float]:
    if "viewBox" in root.attrib:
        box = [float(x) for x in re.split(r"[,\s]+", root.attrib["viewBox"].strip())]
    else:

        def length(value):
            match = re.fullmatch(r"([\d.]+)(pt|px|mm|cm|in)?", value)
            if not match:
                raise ValueError("SVG needs a viewBox or absolute dimensions")
            value, unit = match.groups()
            factor = {None: 1, "px": 1, "pt": 96 / 72, "mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96}[
                unit
            ]
            return float(value) * factor

        box = [0, 0, length(root.attrib.get("width", "")), length(root.attrib.get("height", ""))]
    if len(box) != 4 or not all(math.isfinite(x) for x in box) or min(box[2:]) <= 0:
        raise ValueError("Invalid SVG viewBox")
    return box


def prefix_ids(root: ET.Element, prefix: str) -> None:
    ids = {e.attrib["id"]: prefix + e.attrib["id"] for e in root.iter() if "id" in e.attrib}
    for element in root.iter():
        if "id" in element.attrib:
            element.set("id", ids[element.attrib["id"]])
        for key, value in list(element.attrib.items()):

            def replace_paint(match):
                old = match.group(1)
                return f"url(#{ids.get(old, old)})"

            value = re.sub(
                r"url\(\s*['\"]?#([^)'\"\s]+)['\"]?\s*\)", replace_paint, value, flags=re.I
            )
            for old, new in ids.items():
                if key.split("}")[-1] == "href" and value == "#" + old:
                    value = "#" + new
            element.set(key, value)
    # Matplotlib's embedded stylesheet is element-based, not ID-based.
    # Refuse custom ID selectors rather than silently breaking their styling.
    for element in root.iter(tag("style")):
        if element.text and any(
            re.search(r"#" + re.escape(old) + r"\b", element.text) for old in ids
        ):
            raise ValueError("Flatten ID-based CSS before SVG panel assembly")


def text(root, x, y, value, size=8, weight="normal"):
    element = ET.SubElement(
        root,
        tag("text"),
        {
            "x": str(x),
            "y": str(y),
            "font-family": "Liberation Sans,DejaVu Sans,sans-serif",
            "font-size": str(size),
            "font-weight": weight,
            "fill": "#222222",
        },
    )
    element.text = str(value)


def molecular_svg(smiles: str, width: float, height: float) -> tuple[ET.Element, dict]:
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES; molecular identity cannot be inferred")
    canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
    drawer = rdMolDraw2D.MolDraw2DSVG(int(width), int(height), -1, -1, True)
    options = drawer.drawOptions()
    options.fixedFontSize = 8
    options.bondLineWidth = 0.8
    options.padding = 0.1
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    root = parse_svg(drawer.GetDrawingText().encode())
    return root, {
        "input_smiles": smiles,
        "canonical_isomeric_smiles": canonical,
        "atom_count": mol.GetNumAtoms(),
        "formal_charge": Chem.GetFormalCharge(mol),
        "geometry": "2D depiction, not optimized or experimentally measured geometry",
    }


def draw(spec: dict, base: Path) -> tuple[bytes, dict]:
    width, height = spec["width_pt"], spec["height_pt"]
    panels = spec.get("panels") if spec["kind"] == "assembly" else spec["data"]
    columns = int(spec.get("columns", min(2, len(panels))))
    if columns <= 0:
        raise ValueError("columns must be positive")
    rows = math.ceil(len(panels) / columns)
    margin, gap, label_space = 8, 12, 15
    bottom = 16 if spec["data_status"] == "synthetic" else 8
    cell_width = (width - 2 * margin - (columns - 1) * gap) / columns
    cell_height = (height - margin - bottom - (rows - 1) * gap) / rows
    if min(cell_width, cell_height - label_space) < 25:
        raise ValueError("Panels are too small; increase the figure or split the assembly")
    root = ET.Element(
        tag("svg"),
        {"width": f"{width}pt", "height": f"{height}pt", "viewBox": f"0 0 {width} {height}"},
    )
    ET.SubElement(root, tag("rect"), {"width": "100%", "height": "100%", "fill": "white"})
    provenance = []
    for i, panel in enumerate(panels):
        x = margin + (i % columns) * (cell_width + gap)
        y = margin + (i // columns) * (cell_height + gap)
        if "smiles" in panel:
            child, record = molecular_svg(panel["smiles"], cell_width, cell_height - label_space)
        else:
            import hashlib

            path = base / panel["svg"]
            raw = path.read_bytes()
            child = parse_svg(raw)
            record = {
                "asset": path.name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "source": panel.get("source", "supplied panel"),
                "chemical_review": "required",
            }
        child = copy.deepcopy(child)
        child.set("viewBox", " ".join(map(str, viewbox(child))))
        prefix_ids(child, f"p{i}_")
        child.attrib.update(
            x=str(x),
            y=str(y + label_space),
            width=str(cell_width),
            height=str(cell_height - label_space),
            preserveAspectRatio="xMidYMid meet",
        )
        text(
            root,
            x,
            y + 9,
            panel["label"],
            weight="bold" if spec["kind"] == "assembly" else "normal",
        )
        root.append(child)
        provenance.append({"panel": panel.get("id", panel["label"]), **record})
    if spec["data_status"] == "synthetic":
        text(root, margin, height - 4, "SYNTHETIC DEMONSTRATION", size=6)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), {
        "panels": provenance,
        "layout": "uniform cells; embedded label/glyph geometry requires PDF and visual review",
    }
