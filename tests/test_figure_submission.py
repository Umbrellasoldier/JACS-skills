from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/jacs-figure/scripts"
sys.path.insert(0, str(SCRIPTS))


def example(name):
    return json.loads((SCRIPTS.parent / "assets/examples" / f"{name}.json").read_text())


@unittest.skipUnless(importlib.util.find_spec("pypdf"), "Install figures group")
class PaintedStrokeTests(unittest.TestCase):
    def audit(self, content, *, form=None, user_unit=1):
        from audit_strokes import audit_strokes
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import (
            ArrayObject,
            DecodedStreamObject,
            DictionaryObject,
            FloatObject,
            NameObject,
            NumberObject,
        )

        writer = PdfWriter()
        page = writer.add_blank_page(width=200, height=100)
        page[NameObject("/UserUnit")] = FloatObject(user_unit)
        stream = DecodedStreamObject()
        stream.set_data(content)
        page[NameObject("/Contents")] = writer._add_object(stream)
        if form is not None:
            child = DecodedStreamObject()
            child.set_data(form)
            child[NameObject("/Subtype")] = NameObject("/Form")
            child[NameObject("/BBox")] = ArrayObject([NumberObject(x) for x in (0, 0, 100, 100)])
            objects = DictionaryObject({NameObject("/F"): writer._add_object(child)})
            page[NameObject("/Resources")] = writer._add_object(
                DictionaryObject({NameObject("/XObject"): writer._add_object(objects)})
            )
        buffer = io.BytesIO()
        writer.write(buffer)
        return audit_strokes(PdfReader(buffer))

    def test_only_painted_strokes_count(self):
        result = self.audit(b"0 w 0 0 20 20 re f .6 w 0 0 m 20 20 l S")
        self.assertEqual(result["status"], "PASS")
        self.assertAlmostEqual(result["minimum_stroke_pt"], 0.6)
        self.assertEqual(self.audit(b"0 w 0 0 m 20 20 l S")["status"], "FAIL")

    def test_transforms_user_units_and_graphics_state_change_effective_width(self):
        result = self.audit(b"q .5 0 0 .5 0 0 cm .8 w 0 0 m 20 20 l S Q")
        self.assertEqual(result["status"], "FAIL")
        self.assertAlmostEqual(result["minimum_stroke_pt"], 0.4)
        self.assertEqual(self.audit(b".3 w 0 0 m 20 20 l S", user_unit=2)["status"], "PASS")
        self.assertEqual(
            self.audit(b"q .5 0 0 .5 0 0 cm Q .6 w 0 0 m 20 20 l S")["status"],
            "PASS",
        )

    def test_form_resources_are_followed_but_unused_forms_are_not_painted(self):
        path = b".8 w 0 0 m 20 20 l S"
        result = self.audit(b"q .5 0 0 .5 0 0 cm /F Do Q", form=path)
        self.assertEqual(result["status"], "FAIL")
        self.assertAlmostEqual(result["minimum_stroke_pt"], 0.4)
        self.assertEqual(self.audit(b"", form=path)["thin_strokes"], [])

    def test_filled_wedges_and_anisotropic_bounds_need_review_not_false_failure(self):
        result = self.audit(b".4 w 0 g 0 G 0 0 m 20 0 l 20 10 l h B")
        self.assertEqual(result["status"], "WARN")
        self.assertTrue(result["thin_strokes"][0]["filled_same_color"])
        self.assertEqual(self.audit(b".5 0 0 2 0 0 cm .8 w 0 0 m 20 20 l S")["status"], "WARN")


@unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Install figures group")
class SubmissionSemanticsTests(unittest.TestCase):
    def test_intervals_recompute_from_retained_reaction_values(self):
        import numpy as np

        for row in example("intervals")["data"]:
            values = row["replicates"]
            mean, sd = np.mean(values), np.std(values, ddof=1)
            self.assertEqual(row["n"], len(values))
            self.assertAlmostEqual(row["estimate"], mean)
            self.assertAlmostEqual(row["lower"], mean - sd)
            self.assertAlmostEqual(row["upper"], mean + sd)

    def test_heatmap_recomputes_from_same_partitioned_reference_cohort(self):
        import numpy as np

        cohort = example("agreement")["data"]
        cells = example("heatmap")["data"]
        for method in {r["method"] for r in cohort}:
            expected = {r["reaction_id"] for r in cohort if r["method"] == method}
            observed = []
            for cell in (c for c in cells if c["row"] == method):
                observed.extend(cell["reaction_ids"])
                records = [
                    r
                    for r in cohort
                    if r["method"] == method and r["reaction_id"] in cell["reaction_ids"]
                ]
                errors = [r["predicted"] - r["reference_value"] for r in records]
                self.assertEqual(cell["n"], len(records))
                self.assertAlmostEqual(cell["value"], np.mean(np.abs(errors)))
                np.testing.assert_allclose(sorted(errors), sorted(cell["signed_errors"]))
            self.assertEqual(set(observed), expected)
            self.assertEqual(len(observed), len(expected))
        for column in {c["column"] for c in cells}:
            memberships = [set(c["reaction_ids"]) for c in cells if c["column"] == column]
            self.assertTrue(all(ids == memberships[0] for ids in memberships))

    def test_swarm_preserves_measurements_and_reports_impossible_spacing(self):
        import matplotlib.pyplot as plt
        import numpy as np
        from point_layout import pack_points

        fig, ax = plt.subplots(figsize=(3, 2))
        try:
            values = np.array([1, 1, 1, 2, 2, 3])
            points = ax.scatter(np.zeros(6), values, s=12, linewidths=0.6)
            points._jacs_swarm = (0, -0.3, 0.3)
            ax.set_xlim(-0.5, 0.5)
            fig.canvas.draw()
            result = pack_points(fig)[0]
            np.testing.assert_array_equal(points.get_offsets()[:, 1], values)
            self.assertEqual(len(set(map(tuple, points.get_offsets()))), 6)
            self.assertEqual(result["unresolved_spacing"], 0)
            points._jacs_swarm = (0, 0, 0)
            self.assertGreater(pack_points(fig)[0]["unresolved_spacing"], 0)
        finally:
            plt.close(fig)

    def test_histogram_facets_keep_common_bins_scales_and_all_observations(self):
        import matplotlib.pyplot as plt
        from figure_spec import validate
        from statistical_figures import distribution

        spec = validate(example("histogram"))
        fig = plt.figure()
        try:
            result = distribution(fig, spec)
            self.assertEqual(len(fig.axes), len(spec["group_order"]))
            for ax in fig.axes:
                self.assertEqual(ax.get_xlim(), fig.axes[0].get_xlim())
                self.assertEqual(ax.get_ylim(), fig.axes[0].get_ylim())
            for group in result["summary"].values():
                self.assertEqual(sum(group["bin_counts"]), group["n"])
        finally:
            plt.close(fig)

    def test_authored_caption_and_panel_facts_survive_export_separately(self):
        from plot_figures import render

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            spec = example("showcase")
            (base / "input.json").write_text(json.dumps(spec))
            result = render(base / "input.json", base / "figure")
            self.assertEqual(result["caption"].strip(), spec["caption"])
            facts = json.loads((base / "figure.caption-facts.json").read_text())
            self.assertEqual(set(facts["panels"]), {"a", "b"})
            self.assertEqual(
                facts["panels"]["a"]["computed_display_facts"]["summary"]["Transfer"]["n"], 72
            )
            self.assertEqual(result["readiness"]["submission"], "Not established by this renderer")

    def test_missing_cell_outline_meets_stroke_floor_in_export(self):
        from plot_figures import render

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            spec = example("heatmap")
            spec["data"][-1] = {"row": "Refined", "column": "High", "value": None}
            spec["missing_reasons"] = {"Refined / High": "Unavailable in this test fixture"}
            spec["caption"] = "Synthetic export test with one explicitly unavailable cell."
            (base / "input.json").write_text(json.dumps(spec))
            result = render(base / "input.json", base / "figure")
            strokes = next(f for f in result["findings"] if f["check"] == "pdf_path_strokes")
            self.assertEqual(strokes["status"], "PASS", strokes)
            self.assertEqual(result["details"]["missing_cells"], 1)
