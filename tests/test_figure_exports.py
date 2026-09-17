from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/jacs-figure/scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_figure as audit  # noqa: E402
import figure_spec  # noqa: E402

FIGURES = all(
    importlib.util.find_spec(m) for m in ("matplotlib", "pypdf", "cairosvg", "defusedxml")
)
CHEMISTRY = FIGURES and importlib.util.find_spec("rdkit") is not None


class LayoutTests(unittest.TestCase):
    def test_displaced_comparable_panels_fail_without_text_collision(self):
        layout = {
            "width_pt": 500,
            "height_pt": 200,
            "texts": [],
            "axes": [
                {"id": "a", "bbox_pt": [10, 10, 210, 150]},
                {"id": "b", "bbox_pt": [260, 14, 460, 154]},
            ],
            "comparable_groups": [{"panels": ["a", "b"], "orientation": "row"}],
        }
        findings = audit.audit_layout(layout)
        self.assertTrue(
            any(f["check"] == "panel_alignment" and f["status"] == "FAIL" for f in findings)
        )

    def test_clipping_is_distinct_from_intentional_overlap_review(self):
        layout = {
            "width_pt": 100,
            "height_pt": 100,
            "texts": [
                {"text": "a", "font_pt": 8, "bbox_pt": [-2, 0, 10, 10]},
                {"text": "b", "font_pt": 8, "bbox_pt": [0, 0, 12, 10]},
            ],
        }
        findings = audit.audit_layout(layout)
        self.assertIn("text_clipping", [f["check"] for f in findings if f["status"] == "FAIL"])
        self.assertIn("text_overlap", [f["check"] for f in findings if f["status"] == "WARN"])


@unittest.skipUnless(FIGURES, "Install the figures dependency group for rendered checks")
class FigureExportTests(unittest.TestCase):
    def test_parity_panel_labels_fit_with_dejavu_fallback(self):
        import plot_figures

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            assets = base / "skill/assets"
            assets.mkdir(parents=True)
            style = (SCRIPTS.parent / "assets/jacs.mplstyle").read_text()
            style = style.replace("Liberation Sans, DejaVu Sans, Arial, Helvetica", "DejaVu Sans")
            (assets / "jacs.mplstyle").write_text(style)
            with patch.object(plot_figures, "SKILL", base / "skill"):
                result = plot_figures.render(
                    SCRIPTS.parent / "assets/examples/parity.json", base / "figure"
                )
            self.assertNotEqual(result["verdict"], "FAIL", result["findings"])
            layout = json.loads((base / "figure.layout.json").read_text())
            labels = [x for x in layout["texts"] if x["text"] in {"a", "b"}]
            self.assertEqual(len(labels), 2)
            for label in labels:
                self.assertLessEqual(label["bbox_pt"][3], layout["height_pt"])

    def test_normal_templates_export_actual_dimensions_and_preserve_counts(self):
        from plot_figures import render
        from pypdf import PdfReader

        for name in (
            "energy",
            "parity",
            "comparison",
            "stages",
            "workflow",
            "toc",
            "boxplot",
            "violin",
            "ecdf",
            "histogram",
            "intervals",
            "learning",
            "spectra",
            "heatmap",
            "agreement",
            "showcase",
        ):
            if name == "toc" and not CHEMISTRY:
                continue
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                source = SCRIPTS.parent / "assets/examples" / (name + ".json")
                raw = source.read_bytes()
                result = render(source, Path(temp) / "figure")
                self.assertNotEqual(result["verdict"], "FAIL", result["findings"])
                self.assertEqual(source.read_bytes(), raw)
                self.assertEqual(result["provenance"]["excluded_records"], 0)
                page = PdfReader(Path(temp) / "figure.pdf").pages[0]
                spec = json.loads((Path(temp) / "figure.spec.json").read_text())
                self.assertAlmostEqual(float(page.mediabox.width), spec["width_pt"], places=2)
                self.assertIn("SYNTHETIC DEMONSTRATION", page.extract_text())
                self.assertEqual(
                    result["pdf_sha256"], figure_spec.digest(Path(temp) / "figure.pdf")
                )
                if name == "heatmap":
                    self.assertEqual(len(page.images), 0, "Categorical cells must stay vector")
                if name == "parity":
                    self.assertEqual(result["details"]["metrics"]["Method A"]["n"], 6)
                    self.assertAlmostEqual(result["details"]["metrics"]["Method A"]["mae"], 8 / 6)

    def test_pdf_audit_measures_applied_text_scaling(self):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

        with tempfile.TemporaryDirectory() as temp:
            writer = PdfWriter()
            page = writer.add_blank_page(width=240, height=180)
            font = DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                }
            )
            page[NameObject("/Resources")] = DictionaryObject(
                {
                    NameObject("/Font"): DictionaryObject(
                        {NameObject("/F1"): writer._add_object(font)}
                    )
                }
            )
            stream = DecodedStreamObject()
            stream.set_data(b"q 0.4 0 0 0.4 0 0 cm BT /F1 8 Tf 1 0 0 1 20 20 Tm (tiny) Tj ET Q")
            page[NameObject("/Contents")] = writer._add_object(stream)
            path = Path(temp) / "scaled.pdf"
            writer.write(path)
            result = audit.audit_pdf(path, 240, 180)
            self.assertAlmostEqual(result["minimum_text_pt"], 3.2)
            self.assertEqual(audit.verdict(result["findings"]), "FAIL")

    def test_svg_external_resources_are_rejected(self):
        from svg_panels import parse_svg

        with self.assertRaisesRegex(ValueError, "self-contained"):
            parse_svg(
                b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.org/a.png"/></svg>'
            )

    def test_embedded_png_is_supported_but_svg_data_is_not(self):
        from svg_panels import parse_svg

        prefix = '<svg xmlns="http://www.w3.org/2000/svg"><image href="'
        suffix = '"/></svg>'
        parse_svg((prefix + "data:image/png;base64,YWJj" + suffix).encode())
        with self.assertRaises(ValueError):
            parse_svg((prefix + "data:image/svg+xml;base64,YWJj" + suffix).encode())

    def test_assembly_rewrites_quoted_paint_ids_and_fragment_links(self):
        from svg_panels import parse_svg, prefix_ids, tag

        root = parse_svg(
            b'<svg xmlns="http://www.w3.org/2000/svg"><defs><clipPath id="c">'
            b'<rect width="5" height="5"/></clipPath></defs>'
            b'<g clip-path="url(\'\x23c\')"><path id="line"/></g><use href="#line"/></svg>'
        )
        prefix_ids(root, "panel_")
        self.assertEqual(root.find(tag("g")).get("clip-path"), "url(#panel_c)")
        self.assertEqual(root.find(tag("use")).get("href"), "#panel_line")

    @unittest.skipUnless(CHEMISTRY, "TOC example uses chemical structures")
    def test_tiff_pixel_dimensions_follow_content_resolution(self):
        from PIL import Image
        from plot_figures import render

        for raster_class, dpi in [("color", 300), ("grayscale", 600), ("line_art", 1200)]:
            with self.subTest(raster_class=raster_class), tempfile.TemporaryDirectory() as temp:
                base = Path(temp)
                spec = json.loads((SCRIPTS.parent / "assets/examples/toc.json").read_text())
                spec["raster_class"] = raster_class
                (base / "input.json").write_text(json.dumps(spec))
                render(base / "input.json", base / "figure")
                with Image.open(base / "figure.tiff") as image:
                    self.assertEqual(image.size, (round(234 * dpi / 72), round(126 * dpi / 72)))
                    self.assertAlmostEqual(image.info["dpi"][0], dpi)

    def test_assembly_preserves_panels_and_has_rerunnable_assets(self):
        from plot_figures import render

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            asset = base / "one.svg"
            asset.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="100pt" height="60pt" '
                'viewBox="0 0 100 60"><text x="10" y="30" font-size="8">Original</text></svg>'
            )
            spec = {
                "kind": "assembly",
                "profile": "single",
                "data_status": "synthetic",
                "claim": "Test",
                "caption": "Synthetic",
                "height_pt": 100,
                "panels": [
                    {"label": "a", "svg": "one.svg", "caption": "Original annotation."},
                    {"label": "b", "svg": "one.svg", "caption": "Repeated annotation."},
                ],
            }
            (base / "spec.json").write_text(json.dumps(spec))
            render(base / "spec.json", base / "first")
            result = render(base / "first.spec.json", base / "second")
            self.assertNotEqual(result["verdict"], "FAIL", result["findings"])
            self.assertEqual(len(result["details"]["panels"]), 2)


@unittest.skipUnless(CHEMISTRY, "Install the chemistry group for molecular depiction checks")
class MolecularTests(unittest.TestCase):
    def test_depiction_preserves_stereochemistry_and_atom_mapping(self):
        from rdkit import Chem
        from svg_panels import molecular_svg

        smiles = "[CH3:1][C@H:2]([OH:3])[C:4](=[O:5])[OH:6]"
        _, record = molecular_svg(smiles, 200, 120)
        output = Chem.MolFromSmiles(record["canonical_isomeric_smiles"])
        self.assertEqual([atom.GetAtomMapNum() for atom in output.GetAtoms()], [1, 2, 3, 4, 5, 6])
        self.assertEqual(
            Chem.MolToSmiles(Chem.MolFromSmiles(smiles), isomericSmiles=True),
            record["canonical_isomeric_smiles"],
        )
        self.assertIn("@", record["canonical_isomeric_smiles"])
        with self.assertRaisesRegex(ValueError, "Invalid SMILES"):
            molecular_svg("invalid structure", 200, 120)


if __name__ == "__main__":
    unittest.main()
