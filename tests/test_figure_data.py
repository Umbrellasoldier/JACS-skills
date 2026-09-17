from __future__ import annotations

import copy
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/jacs-figure/scripts"
sys.path.insert(0, str(SCRIPTS))
import figure_spec as f  # noqa: E402


def example(name: str) -> dict:
    return json.loads((SCRIPTS.parent / "assets/examples" / (name + ".json")).read_text())


class FigureDataTests(unittest.TestCase):
    def test_validation_preserves_input_and_every_measurement(self):
        spec = example("parity")
        original = copy.deepcopy(spec)
        output = f.validate(spec)
        self.assertEqual(spec, original)
        self.assertEqual(output["data"], original["data"])

    def test_energy_reference_unit_and_quantity_cannot_be_silently_mixed(self):
        for field, value in (
            ("unit", "kJ/mol"),
            ("reference", "encounter complex"),
            ("quantity", "E"),
        ):
            with self.subTest(field=field):
                spec = example("energy")
                spec["data"][1][field] = value
                with self.assertRaisesRegex(ValueError, "Mixed"):
                    f.validate(spec)

    def test_nonfinite_and_boolean_values_are_not_measurements(self):
        for value in (None, "", math.nan, math.inf, True):
            with self.subTest(value=value):
                spec = example("energy")
                spec["data"][1]["energy"] = value
                with self.assertRaises(ValueError):
                    f.validate(spec)

    def test_stage_denominators_and_unprocessed_counts(self):
        result = f.validate(example("stages"))
        last = result["data"][-1]
        self.assertEqual(last["entered"], 70)
        self.assertAlmostEqual(last["conditional_rate"], 61 / 70)
        self.assertAlmostEqual(last["overall_rate"], 61 / 100)
        self.assertEqual(last["pending"], 3)

    def test_invalid_stage_accounting_and_population_units(self):
        for change in ({"passed": 1000}, {"entered": 95}, {"unit_of_analysis": "candidates"}):
            spec = example("stages")
            spec["data"][1].update(change)
            with self.assertRaises(ValueError):
                f.validate(spec)

    def test_zero_entrants_have_undefined_conditional_rate(self):
        spec = example("stages")
        spec["data"] = [
            {"stage": "first", "passed": 0, "failed": 100, "pending": 0},
            {"stage": "second", "passed": 0, "failed": 0, "pending": 0},
        ]
        result = f.validate(spec)
        self.assertIsNone(result["data"][1]["conditional_rate"])
        self.assertEqual(result["data"][1]["overall_rate"], 0)

    def test_matched_comparison_rejects_duplicates_and_missing_reactions(self):
        for mutation in ("duplicate", "missing"):
            spec = example("comparison")
            if mutation == "duplicate":
                spec["data"].append(copy.deepcopy(spec["data"][0]))
            else:
                spec["data"].pop()
            with self.assertRaises(ValueError):
                f.validate(spec)

    def test_parity_keeps_one_reference_per_reaction(self):
        spec = example("parity")
        spec["data"][-1]["reference_value"] += 2
        with self.assertRaisesRegex(ValueError, "Reference values differ"):
            f.validate(spec)

    def test_log_domain_preserves_input_without_dropping_rows(self):
        spec = example("comparison")
        spec["scale"] = "log"
        spec["data"][0]["value"] = 0
        original = copy.deepcopy(spec)
        with self.assertRaisesRegex(ValueError, "positive"):
            f.validate(spec)
        self.assertEqual(spec, original)

    def test_toc_and_main_dimensions_are_separate(self):
        spec = example("toc")
        spec["width_pt"] = 240
        with self.assertRaisesRegex(ValueError, "TOC"):
            f.validate(spec)
        main = example("energy")
        main["width_pt"] = 600
        with self.assertRaisesRegex(ValueError, "Double-column"):
            f.validate(main)

    def test_csv_ids_and_count_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / "data.csv").write_text("reaction_id,method,value\n001,A,2\n001,B,1\n")
            spec = example("comparison")
            del spec["data"]
            spec["input_csv"] = "data.csv"
            (path / "spec.json").write_text(json.dumps(spec))
            output, provenance = f.load(path / "spec.json")
            self.assertEqual(output["data"][0]["reaction_id"], "001")
            self.assertEqual(provenance["input_records"], 2)
            self.assertEqual(provenance["excluded_records"], 0)
            self.assertEqual(provenance["sources"][0]["sha256"], f.digest(path / "data.csv"))


if __name__ == "__main__":
    unittest.main()
