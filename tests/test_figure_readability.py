from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/jacs-figure/scripts"
sys.path.insert(0, str(SCRIPTS))
from figure_spec import validate  # noqa: E402


def example(name):
    return json.loads((SCRIPTS.parent / "assets/examples" / f"{name}.json").read_text())


class SemanticInputTests(unittest.TestCase):
    def test_normalized_label_requires_a_declared_convention(self):
        spec = example("spectra")
        spec.pop("normalization")
        with self.assertRaisesRegex(ValueError, "normalization"):
            validate(spec)
        spec["y_quantity"] = "Model intensity"
        validate(spec)

    def test_spectral_normalization_is_reproducible_from_retained_raw_values(self):
        rows = example("spectra")["data"]
        for name in {r["series"] for r in rows}:
            group = [r for r in rows if r["series"] == name]
            peak = max(r["raw_y"] for r in group)
            self.assertEqual(max(r["y"] for r in group), 1)
            for row in group:
                self.assertAlmostEqual(row["y"], row["raw_y"] / peak)

    def test_ticks_and_display_transforms_cannot_silently_change_semantics(self):
        for name, field, bad in (
            ("ecdf", "value_transform", "square"),
            ("learning", "x_ticks", [0, 100]),
            ("heatmap", "colorbar_ticks", [0, 8]),
        ):
            spec = example(name)
            spec[field] = bad
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate(spec)

    def test_panel_grid_rejects_mixed_data_status(self):
        spec = example("showcase")
        spec["panels"][0]["spec"]["data_status"] = "real"
        with self.assertRaisesRegex(ValueError, "data_status"):
            validate(spec)

    def test_log_distribution_checks_the_explicitly_transformed_values(self):
        spec = example("boxplot")
        spec.update(scale="log", value_transform="absolute", zero_reference=False)
        spec["data"] = [{"observation_id": "1", "group": "A", "value": -2}]
        self.assertEqual(validate(spec)["data"][0]["value"], -2)
        spec["data"][0]["value"] = 0
        with self.assertRaisesRegex(ValueError, "positive"):
            validate(spec)


@unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Install figures group")
class ReadabilityTests(unittest.TestCase):
    def test_paired_ties_have_distinct_locations_and_preserve_pair_links(self):
        import matplotlib.pyplot as plt
        import numpy as np
        from plot_figures import comparison

        raw = example("comparison")
        original = copy.deepcopy(raw)
        fig = plt.figure()
        try:
            facts = comparison(fig, validate(raw))
            ax = fig.axes[0]
            methods = list(facts["summary"])
            ids = list(facts["category_offsets_by_reaction"])
            for i, (method, points) in enumerate(zip(methods, ax.collections, strict=True)):
                positions = np.array(points.get_offsets())
                self.assertEqual(len(positions), 6)
                self.assertEqual(len(set(map(tuple, positions))), 6)
                expected = [
                    next(
                        r["value"]
                        for r in raw["data"]
                        if r["method"] == method and r["reaction_id"] == identity
                    )
                    for identity in ids
                ]
                np.testing.assert_array_equal(positions[:, 1], expected)
                for j, line in enumerate(ax.lines[: len(ids)]):
                    self.assertEqual(line.get_xdata()[i], positions[j, 0])
                    self.assertEqual(line.get_ydata()[i], positions[j, 1])
            self.assertEqual(raw, original)
        finally:
            plt.close(fig)

    def test_absolute_ecdf_retains_raw_values_ties_and_common_tails(self):
        import matplotlib.pyplot as plt
        import numpy as np
        from statistical_figures import distribution

        spec = example("ecdf")
        spec["data"] = [
            {"observation_id": str(i), "group": name, "value": value}
            for name, values in [("A", [-3, -1, 1]), ("B", [-2, 0, 2])]
            for i, value in enumerate(values)
        ]
        original = copy.deepcopy(spec)
        fig = plt.figure()
        try:
            distribution(fig, validate(spec))
            lines = fig.axes[0].lines
            np.testing.assert_array_equal(lines[0].get_xdata()[1:-1], [1, 1, 3])
            for line in lines:
                np.testing.assert_allclose(line.get_ydata(), [0, 1 / 3, 2 / 3, 1, 1])
                self.assertEqual(line.get_xdata()[0], 0)
                self.assertEqual(line.get_xdata()[-1], lines[0].get_xdata()[-1])
                self.assertGreater(line.get_xdata()[-1], 3)
            self.assertEqual(spec, original)
        finally:
            plt.close(fig)

    def test_missing_heatmap_values_remain_identified_without_numeric_annotations(self):
        import matplotlib.pyplot as plt
        from statistical_figures import heatmap

        spec = example("heatmap")
        spec["annotate"] = False
        spec["data"][0]["value"] = 0
        fig = plt.figure()
        try:
            facts = heatmap(fig, validate(spec))
            self.assertEqual(facts["observed_cells"], 8)
            self.assertEqual(facts["missing_cells"], 1)
            self.assertEqual([t.get_text() for t in fig.axes[0].texts], ["NA"])
            self.assertEqual(len([p for p in fig.axes[0].patches if p.get_hatch()]), 1)
        finally:
            plt.close(fig)

    def test_facets_keep_all_records_and_comparable_domains(self):
        import matplotlib.pyplot as plt
        from plot_figures import parity

        spec = validate(example("agreement"))
        fig = plt.figure(layout="constrained")
        try:
            facts = parity(fig, spec)
            self.assertEqual(len(fig.axes), 6)
            for ax in fig.axes:
                self.assertEqual(len(ax.collections[0].get_offsets()), 72)
                self.assertEqual(ax.get_xlim(), fig.axes[0].get_xlim())
            for ax in fig.axes[:3]:
                self.assertEqual(ax.get_xlim(), ax.get_ylim())
            for ax in fig.axes[3:]:
                self.assertEqual(ax.get_ylim(), fig.axes[3].get_ylim())
            self.assertEqual(sum(v["n"] for v in facts["metrics"].values()), 216)
        finally:
            plt.close(fig)


@unittest.skipUnless(importlib.util.find_spec("pypdf"), "Install figures group")
class CaptionDeliveryTests(unittest.TestCase):
    def test_interval_definition_survives_export_and_rerender_without_duplication(self):
        from plot_figures import render

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            spec = example("intervals")
            (base / "input.json").write_text(json.dumps(spec))
            result = render(base / "input.json", base / "first")
            delivered = (base / "first.caption.txt").read_text()
            self.assertIn(spec["interval_definition"], delivered)
            self.assertIn(spec["quantity_definition"], delivered)
            self.assertEqual(result["caption"], delivered)
            render(base / "first.spec.json", base / "second")
            self.assertEqual(delivered, (base / "second.caption.txt").read_text())

    def test_native_panel_export_carries_both_data_and_interval_meanings(self):
        from plot_figures import render

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            spec = example("showcase")
            spec["panels"][1]["spec"] = example("learning")
            spec["panels"][1].update(title="Training size", role="Run-to-run variation")
            spec["population"] = "Distinct explicitly declared demonstration cohorts"
            (base / "input.json").write_text(json.dumps(spec))
            result = render(base / "input.json", base / "output")
            self.assertNotEqual(result["verdict"], "FAIL", result["findings"])
            caption = (base / "output.caption.txt").read_text()
            self.assertIn(spec["panels"][1]["spec"]["interval_definition"], caption)
            self.assertIn("Q1–Q3", caption)
            saved = json.loads((base / "output.spec.json").read_text())
            self.assertEqual(saved["panels"][0]["spec"]["data"], spec["panels"][0]["spec"]["data"])

    def test_svg_panel_caption_is_bundled_and_can_move_away_from_its_source(self):
        from plot_figures import render

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "panel.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 70">'
                '<text x="10" y="30" font-size="8">Estimate</text></svg>'
            )
            note = "Point: mean of eight runs. Interval: sample SD, not a confidence interval."
            (base / "note.txt").write_text(note)
            spec = {
                "kind": "assembly",
                "data_status": "synthetic",
                "claim": "Demonstration",
                "caption": "Synthetic estimate",
                "profile": "single",
                "height_pt": 110,
                "panels": [{"label": "a", "svg": "panel.svg", "caption_file": "note.txt"}],
            }
            (base / "input.json").write_text(json.dumps(spec))
            result = render(base / "input.json", base / "bundle/first")
            self.assertIn(note, result["caption"])
            self.assertEqual(result["provenance"]["sources"][0]["name"], "note.txt")
            (base / "note.txt").unlink()
            (base / "panel.svg").unlink()
            rerun = render(base / "bundle/first.spec.json", base / "bundle/second")
            self.assertEqual(rerun["caption"], result["caption"])
            broken = copy.deepcopy(spec)
            broken["panels"][0].pop("caption_file")
            with self.assertRaisesRegex(ValueError, "caption"):
                validate(broken)


if __name__ == "__main__":
    unittest.main()
