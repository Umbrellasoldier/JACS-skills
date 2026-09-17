from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/jacs-figure/scripts"))
import figure_spec as spec_module  # noqa: E402


def example(name):
    path = ROOT / "skills/jacs-figure/assets/examples" / (name + ".json")
    return json.loads(path.read_text())


class StatisticalDataTests(unittest.TestCase):
    def test_histogram_rejects_excluded_points_and_bad_edges(self):
        for edges in ([0, 1], [-100, 2, 2, 100]):
            spec = example("histogram")
            spec["bin_edges"] = edges
            with self.assertRaises(ValueError):
                spec_module.validate(spec)

    def test_distribution_preserves_measurements_and_declared_groups(self):
        original = example("boxplot")
        validated = spec_module.validate(original)
        self.assertEqual(validated["data"], original["data"])
        duplicate = copy.deepcopy(original)
        duplicate["data"].append(duplicate["data"][0])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            spec_module.validate(duplicate)
        original["group_order"] = ["Baseline"]
        with self.assertRaisesRegex(ValueError, "every observed group"):
            spec_module.validate(original)

    def test_interval_cannot_invent_or_misstate_bounds(self):
        for mutation in ("missing_definition", "outside", "mixed_units"):
            spec = example("intervals")
            if mutation == "missing_definition":
                del spec["interval_definition"]
            elif mutation == "outside":
                spec["data"][0]["lower"] = 100
            else:
                spec["data"][0]["unit"] = "kJ/mol"
            with self.assertRaises(ValueError):
                spec_module.validate(spec)

    def test_curve_rejects_partial_bands_reordered_x_and_nonpositive_bounds(self):
        for mutation in ("partial", "reordered", "log_bound", "zero_reference"):
            spec = example("learning")
            if mutation == "partial":
                del spec["data"][0]["lower"]
                del spec["data"][0]["upper"]
            elif mutation == "reordered":
                spec["data"][0], spec["data"][1] = spec["data"][1], spec["data"][0]
            elif mutation == "log_bound":
                spec["y_scale"] = "log"
                spec["data"][0]["lower"] = 0
            else:
                spec.update(y_scale="log", zero_reference=True)
            with self.assertRaises(ValueError):
                spec_module.validate(spec)

    def test_heatmap_missing_is_distinct_from_zero_and_clipping_is_rejected(self):
        spec = example("heatmap")
        spec["data"][0]["value"] = 0
        result = spec_module.validate(spec)
        self.assertEqual(result["data"][0]["value"], 0)
        self.assertIsNone(result["data"][-1]["value"])
        for mutation in ("omit", "clip", "center"):
            changed = copy.deepcopy(spec)
            if mutation == "omit":
                changed["data"].pop()
            elif mutation == "clip":
                changed["vmax"] = 1
            else:
                changed.update(color_scale="diverging", center=100)
            with self.assertRaises(ValueError):
                spec_module.validate(changed)

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Install figures group")
    def test_statistics_account_for_outliers_ties_and_boundary_bins(self):
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from statistical_figures import distribution

        spec = example("boxplot")
        spec["data"] = [
            {"observation_id": str(i), "group": "A", "value": v}
            for i, v in enumerate([0, 1, 1, 2, 100])
        ]
        for mode in ("box", "ecdf", "histogram"):
            spec.update(display=mode, bin_edges=[0, 2, 100])
            fig = plt.figure()
            facts = distribution(fig, spec_module.validate(spec))
            self.assertEqual(facts["summary"]["A"]["n"], 5)
            if mode == "box":
                self.assertEqual(facts["summary"]["A"]["median"], 1)
                self.assertEqual(facts["summary"]["A"]["whiskers"], [0, 2])
                self.assertEqual(len(fig.axes[0].collections[0].get_offsets()), 5)
            elif mode == "histogram":
                self.assertEqual(facts["summary"]["A"]["bin_counts"], [3, 2])
            else:
                self.assertEqual(fig.axes[0].lines[0].get_ydata()[-1], 1)
                self.assertEqual(list(fig.axes[0].lines[0].get_xdata())[1:-1], [0, 1, 1, 2, 100])
                self.assertLess(fig.axes[0].lines[0].get_xdata()[0], 0)
                self.assertGreater(fig.axes[0].lines[0].get_xdata()[-1], 100)
            plt.close(fig)

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Install figures group")
    def test_small_or_constant_group_does_not_receive_fabricated_density(self):
        import matplotlib.pyplot as plt
        from statistical_figures import distribution

        spec = example("violin")
        spec["data"] = [{"observation_id": str(i), "group": "A", "value": 3} for i in range(6)]
        fig = plt.figure()
        facts = distribution(fig, spec_module.validate(spec))
        self.assertEqual(facts["violin_skipped_groups"], ["A"])
        self.assertEqual(len(fig.axes[0].collections), 1)
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
