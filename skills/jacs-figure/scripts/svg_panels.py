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


def molecular_svg(
    smiles: str,
    width: float,
    height: float,
    bond_highlights=None,
    proposed_bonds=None,
    separate_fragments=False,
) -> tuple[ET.Element, dict]:
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES; molecular identity cannot be inferred")
    canonical = Chem.MolToSmiles(mol, isomericSmiles=True)
    if separate_fragments and len(Chem.GetMolFrags(mol)) > 1:
        if bond_highlights or proposed_bonds:
            raise ValueError("Separate fragments before applying atom-index bond encodings")
        fragments = Chem.GetMolFrags(mol, asMols=True)
        gap = 12
        part_width = (width - gap * (len(fragments) - 1)) / len(fragments)
        if part_width < 20:
            raise ValueError("Too many fragments for readable plus separators")
        root = ET.Element(tag("svg"), {"viewBox": f"0 0 {width} {height}"})
        for i, fragment in enumerate(fragments):
            child, _ = molecular_svg(Chem.MolToSmiles(fragment), part_width, height)
            prefix_ids(child, f"fragment{i}_")
            child.attrib.update(
                x=str(i * (part_width + gap)), y="0", width=str(part_width), height=str(height)
            )
            root.append(child)
            if i < len(fragments) - 1:
                text(root, (i + 1) * part_width + i * gap + 3, height / 2 + 3, "+", size=9)
        return root, {
            "input_smiles": smiles,
            "canonical_isomeric_smiles": canonical,
            "atom_count": mol.GetNumAtoms(),
            "formal_charge": Chem.GetFormalCharge(mol),
            "fragment_separators": "+",
            "geometry": "2D depiction, not a TS geometry",
        }
    drawer = rdMolDraw2D.MolDraw2DSVG(int(width), int(height), -1, -1, True)
    options = drawer.drawOptions()
    options.fixedFontSize = 8
    options.bondLineWidth = 0.8
    options.padding = 0.1
    highlights = []
    for pair in bond_highlights or []:
        if len(pair) != 2 or any(
            isinstance(i, bool) or not isinstance(i, int) or i < 0 or i >= mol.GetNumAtoms()
            for i in pair
        ):
            raise ValueError("Bond highlights need two valid zero-based atom indices")
        bond = mol.GetBondBetweenAtoms(*pair)
        if bond is None:
            raise ValueError("Highlighted atom pair is not a bond in the supplied molecule")
        highlights.append(bond.GetIdx())
    drawer.DrawMolecule(
        mol,
        highlightAtoms=[],
        highlightBonds=highlights,
        highlightBondColors={i: (0.66, 0.81, 0.91) for i in highlights},
    )
    drawer.FinishDrawing()
    root = parse_svg(drawer.GetDrawingText().encode())
    proposed_ids = []
    for pair in proposed_bonds or []:
        if len(pair) != 2 or any(
            isinstance(i, bool) or not isinstance(i, int) or not 0 <= i < mol.GetNumAtoms()
            for i in pair
        ):
            raise ValueError("Proposed bonds need two valid zero-based atom indices")
        bond = mol.GetBondBetweenAtoms(*pair)
        if bond is None or bond.GetBondType() != Chem.BondType.SINGLE:
            raise ValueError("Proposed links must identify single edges in the supplied graph")
        proposed_ids.append(bond.GetIdx())
    for element in root.iter(tag("path")):
        if any(f"bond-{i}" in element.get("class", "").split() for i in proposed_ids):
            element.set(
                "style",
                "fill:none;stroke:#356E96;stroke-width:1.0px;"
                "stroke-dasharray:3,2;stroke-linecap:butt;stroke-linejoin:round",
            )
    return root, {
        "input_smiles": smiles,
        "canonical_isomeric_smiles": canonical,
        "atom_count": mol.GetNumAtoms(),
        "formal_charge": Chem.GetFormalCharge(mol),
        "highlighted_bond_atom_pairs": bond_highlights or [],
        "proposed_bond_atom_pairs": proposed_bonds or [],
        "graph_convention": "Dashed edges are proposed links, not bond orders or measured distances"
        if proposed_bonds
        else None,
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
    top = 24 if spec.get("title") else margin
    note_lines = spec.get("note", "").splitlines()
    note_size = 8 if spec["profile"] == "toc" else 7
    note_step = note_size + 2
    note_space = note_step * len(note_lines) + 4 if note_lines else 0
    bottom = 16 if spec["data_status"] == "synthetic" else 8
    cell_width = (width - 2 * margin - (columns - 1) * gap) / columns
    cell_height = (height - top - bottom - note_space - (rows - 1) * gap) / rows
    if min(cell_width, cell_height - label_space) < 25:
        raise ValueError("Panels are too small; increase the figure or split the assembly")
    root = ET.Element(
        tag("svg"),
        {"width": f"{width}pt", "height": f"{height}pt", "viewBox": f"0 0 {width} {height}"},
    )
    ET.SubElement(root, tag("rect"), {"width": "100%", "height": "100%", "fill": "white"})
    if spec.get("title"):
        text(root, margin, 12, spec["title"], size=8, weight="bold")
    provenance = []
    positions = {}
    for i, panel in enumerate(panels):
        x = margin + (i % columns) * (cell_width + gap)
        y = top + (i // columns) * (cell_height + gap)
        positions[panel.get("id", panel["label"])] = (x, y)
        if "smiles" in panel:
            child, record = molecular_svg(
                panel["smiles"],
                cell_width,
                cell_height - label_space,
                panel.get("bond_highlights"),
                panel.get("proposed_bonds"),
                panel.get("separate_fragments", False),
            )
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
    if spec.get("edges"):
        defs = ET.SubElement(root, tag("defs"))
        marker = ET.SubElement(
            defs,
            tag("marker"),
            {
                "id": "scheme-arrow",
                "viewBox": "0 0 10 10",
                "refX": "9",
                "refY": "5",
                "markerWidth": "5",
                "markerHeight": "5",
                "orient": "auto",
            },
        )
        ET.SubElement(marker, tag("path"), {"d": "M 0 1 L 9 5 L 0 9 Z", "fill": "#74808C"})
        for start, end in spec["edges"]:
            x1, y1 = positions[start]
            x2, y2 = positions[end]
            if y1 != y2 or abs(x2 - x1 - cell_width - gap) > 1e-6:
                raise ValueError("Structure arrows support left-to-right neighbors in one row")
            y = y1 + label_space + (cell_height - label_space) / 2
            ET.SubElement(
                root,
                tag("line"),
                {
                    "x1": str(x1 + cell_width),
                    "y1": str(y),
                    "x2": str(x2 - 1),
                    "y2": str(y),
                    "stroke": "#74808C",
                    "stroke-width": "0.8",
                    "marker-end": "url(#scheme-arrow)",
                },
            )
    for i, line in enumerate(note_lines):
        text(
            root,
            margin,
            height - bottom - note_space + note_size + note_step * i,
            line,
            size=note_size,
        )
    if spec["data_status"] == "synthetic":
        text(root, margin, height - 4, "SYNTHETIC DEMONSTRATION", size=6)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), {
        "panels": provenance,
        "layout": "uniform cells; embedded label/glyph geometry requires PDF and visual review",
    }
