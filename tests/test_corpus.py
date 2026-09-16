from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "corpus", ROOT / "skills/jacs-style-distill/scripts/corpus.py"
)
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)

PAPER = {
    "paper_id": "S01",
    "doi": "10.1021/example",
    "pmcid": "PMC123",
    "split": "development",
    "journal": "Journal of the American Chemical Society",
}


def bioc(doi: str | None = PAPER["doi"]) -> bytes:
    passages = [
        {
            "offset": 0,
            "infons": {
                "section_type": "TITLE",
                "type": "front",
                **({"article-id_doi": doi} if doi else {}),
            },
            "text": "Test",
        },
        {
            "offset": 5,
            "infons": {"section_type": "ABSTRACT", "type": "abstract"},
            "text": "However, ΔE‡ was 12 kcal mol−1.",
        },
        {
            "offset": 50,
            "infons": {"section_type": "INTRO", "type": "title_1"},
            "text": "Introduction",
        },
        {
            "offset": 70,
            "infons": {"section_type": "INTRO", "type": "paragraph"},
            "text": "A chemical problem.",
        },
        {
            "offset": 100,
            "infons": {"section_type": "INTRO", "type": "title_1"},
            "text": "Reactivity of scaffold X",
        },
        {
            "offset": 150,
            "infons": {"section_type": "INTRO", "type": "paragraph"},
            "text": "The reaction was studied.",
        },
        {
            "offset": 200,
            "infons": {"section_type": "FIG", "type": "fig_caption"},
            "text": "However however figure.",
        },
        {
            "offset": 250,
            "infons": {"section_type": "METHODS", "type": "title_1"},
            "text": "Computational Methods",
        },
        {
            "offset": 270,
            "infons": {"section_type": "METHODS", "type": "paragraph"},
            "text": "However methods.",
        },
    ]
    return json.dumps([{"documents": [{"id": "PMC123", "passages": passages}]}]).encode()


JATS = b"""<article><front><article-meta><article-id pub-id-type="doi">10.1021/example</article-id>
<abstract><p>Abstract text.</p></abstract></article-meta></front><body>
<sec><title>Results and Discussion</title><p>Energy <italic>E</italic> was measured.</p>
<sec><title>Subtopic</title><p>A result.</p></sec>
<fig><caption><p>Figure evidence.</p></caption></fig></sec></body>
<back><ref-list><ref><mixed-citation>Not prose.</mixed-citation></ref>
</ref-list></back></article>"""


class IngestTests(unittest.TestCase):
    def test_bioc_preserves_chemical_text_and_real_source_locator(self):
        rows, info = c.ingest(bioc(), "bioc", PAPER, "https://example.org/source")
        self.assertEqual(rows[1]["text"], "However, ΔE‡ was 12 kcal mol−1.")
        self.assertEqual(rows[1]["locator"], "BioC:PMC123:passage[1]:offset=5")
        self.assertEqual(info["identity_status"], "source_doi_verified")
        self.assertEqual(rows[1]["text_sha256"], c.digest(rows[1]["text"].encode()))

    def test_wrong_source_is_rejected_even_with_user_assertion(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            c.ingest(bioc("10.1021/other"), "bioc", PAPER, "source", PAPER["doi"])

    def test_missing_doi_requires_explicit_assertion(self):
        with self.assertRaisesRegex(ValueError, "DOI absent"):
            c.ingest(bioc(None), "bioc", PAPER, "source")
        _, info = c.ingest(bioc(None), "bioc", PAPER, "source", PAPER["doi"])
        self.assertEqual(info["identity_status"], "user_asserted_doi")

    def test_reviewed_heading_override_does_not_alter_original_tag(self):
        rows, _ = c.ingest(
            bioc(),
            "bioc",
            PAPER,
            "source",
            overrides={"Reactivity of scaffold X": "results_discussion"},
        )
        self.assertEqual(rows[5]["section"], "results_discussion")
        self.assertEqual(rows[5]["section_source_tag"], "INTRO")
        unchanged, _ = c.ingest(bioc(), "bioc", PAPER, "source")
        self.assertEqual(unchanged[5]["section"], "body")

    def test_jats_nested_sections_and_figures_are_not_double_counted(self):
        rows, _ = c.ingest(JATS, "jats", PAPER, "source")
        body = [
            r for r in rows if r["kind"] == "paragraph" and r["section"] == "results_discussion"
        ]
        self.assertEqual([r["text"] for r in body], ["Energy E was measured.", "A result."])
        self.assertEqual(len([r for r in rows if r["kind"] == "caption"]), 1)
        self.assertFalse(any("Not prose" in r["text"] for r in rows))

    def test_html_error_is_not_accepted_as_jats(self):
        with self.assertRaisesRegex(ValueError, "Expected JATS"):
            c.ingest(b"<html><body>Unavailable</body></html>", "jats", PAPER, "source")

    def test_structured_abstract_locators_follow_actual_tree(self):
        data = JATS.replace(
            b"<abstract><p>Abstract text.</p></abstract>",
            b"<abstract><sec><p>First.</p></sec><sec><p>Second.</p></sec></abstract>",
        )
        rows, _ = c.ingest(data, "jats", PAPER, "source")
        abstract = [row for row in rows if row["section"] == "abstract"]
        self.assertEqual(len(abstract), 2)
        self.assertTrue(abstract[0]["locator"].endswith("abstract[1]/sec[1]/p[1]"))
        self.assertTrue(abstract[1]["locator"].endswith("abstract[1]/sec[2]/p[1]"))

    def test_explicit_blocks_require_real_unique_locators(self):
        block = {
            "text": "Observation.",
            "section": "results",
            "section_original": "Results",
            "kind": "paragraph",
            "locator": "PDF:page=2:paragraph=1",
        }
        data = (json.dumps(block) + "\n" + json.dumps(block)).encode()
        with self.assertRaisesRegex(ValueError, "duplicated"):
            c.ingest(data, "blocks", PAPER, "source", PAPER["doi"])

    def test_doi_prefix_and_case_normalization(self):
        self.assertEqual(c.normalize_doi("https://doi.org/10.1021/EXAMPLE"), PAPER["doi"])
        with self.assertRaises(ValueError):
            c.normalize_doi("not-a-doi")


class StatisticsTests(unittest.TestCase):
    def setUp(self):
        self.rows, _ = c.ingest(bioc(), "bioc", PAPER, "source")

    def test_captions_methods_and_holdout_are_excluded(self):
        held = {**PAPER, "paper_id": "H01", "doi": "10.1021/held", "split": "holdout"}
        extra = {**self.rows[1], "paper_id": "H01", "doi": held["doi"], "block_id": "H01:p2"}
        report = c.statistics(self.rows + [extra], {"S01": PAPER, "H01": held})
        self.assertEqual(report["paper_ids"], ["S01"])
        self.assertEqual(report["connectors"]["however"]["count"], 1)
        self.assertEqual(report["excluded_blocks"]["different_split"], 1)

    def test_duplicate_block_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate block"):
            c.statistics(self.rows + [self.rows[1]], {"S01": PAPER})

    def test_multiple_source_versions_are_rejected(self):
        other = {**self.rows[1], "block_id": "S01:other", "source_sha256": "changed"}
        with self.assertRaisesRegex(ValueError, "Multiple source versions"):
            c.statistics(self.rows + [other], {"S01": PAPER})

    def test_wrong_block_doi_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "disagrees"):
            c.statistics([{**self.rows[1], "doi": "10.1021/wrong"}], {"S01": PAPER})

    def test_changed_text_requires_source_reimport(self):
        with self.assertRaisesRegex(ValueError, "text digest mismatch"):
            c.statistics([{**self.rows[1], "text": "Edited after import."}], {"S01": PAPER})

    def test_manifest_deduplicates_doi_variants(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.jsonl"
            other = {**PAPER, "paper_id": "S02", "doi": "https://doi.org/10.1021/EXAMPLE"}
            path.write_text(json.dumps(PAPER) + "\n" + json.dumps(other))
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                c.manifest_rows(path)


class RetrievalTests(unittest.TestCase):
    def test_crossref_404_is_unresolved_not_false_citation(self):
        error = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
        with patch.object(c, "request_bytes", side_effect=error):
            result = c.verify(PAPER["doi"])
        self.assertEqual(result["status"], "unresolved")

    def test_crossref_title_mismatch_needs_review(self):
        reply = json.dumps(
            {"message": {"DOI": PAPER["doi"], "title": ["A different title"]}}
        ).encode()
        with patch.object(c, "request_bytes", return_value=reply):
            result = c.verify(PAPER["doi"], "Expected title")
        self.assertEqual(result["status"], "needs_review")
        self.assertFalse(result["fulltext_verified"])

    def test_fetch_fallback_and_verified_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            with patch.object(c, "request_bytes", side_effect=[b"Not available", JATS]):
                result = c.fetch(PAPER, target)
            self.assertEqual(result["format"], "jats")
            self.assertEqual(len(result["attempts"]), 1)
            with patch.object(c, "request_bytes", side_effect=AssertionError("unexpected network")):
                cached = c.fetch(PAPER, target)
            self.assertTrue(cached["cache_reused"])

    def test_cache_corruption_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            with patch.object(c, "request_bytes", return_value=bioc()):
                c.fetch(PAPER, target)
            (target / "source.json").write_text("corrupted")
            with self.assertRaisesRegex(ValueError, "conflicts"):
                c.fetch(PAPER, target)
            self.assertEqual((target / "source.json").read_text(), "corrupted")


if __name__ == "__main__":
    unittest.main()
