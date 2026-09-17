from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_figures import validate  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "figure_corpus", ROOT / "skills/jacs-style-distill/scripts/figure_corpus.py"
)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class SourceTests(unittest.TestCase):
    def source(self, doi="10.1021/test", journal="Journal of the American Chemical Society"):
        xml = (
            '<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><journal-meta>'
            f"<journal-title>{journal}</journal-title></journal-meta><article-meta>"
            f'<article-id pub-id-type="doi">{doi}</article-id></article-meta></front>'
            '<body><fig id="f1"><label>Figure 1</label><caption><p>Example.</p></caption>'
            '<graphic xlink:href="image.jpg"/><graphic xlink:href="thumb.jpg" '
            'content-type="thumb"/></fig></body></article>'
        ).encode()
        image = b"mock image content"
        prefix = c.BUCKET + "PMC123.1/"
        xml_url = prefix + "PMC123.1.xml?md5=" + hashlib.md5(xml).hexdigest()
        image_url = prefix + "image.jpg?md5=" + hashlib.md5(image).hexdigest()
        metadata = {
            "pmcid": "PMC123",
            "doi": "10.1021/test",
            "xml_url": xml_url,
            "media_urls": [image_url],
            "is_manuscript": True,
        }
        objects = {
            prefix + "PMC123.1.json": json.dumps(metadata).encode(),
            xml_url: xml,
            image_url: image,
        }
        return objects, metadata

    def test_versioned_assets_remain_unreviewed_and_record_actual_hash(self):
        objects, _ = self.source()
        with (
            tempfile.TemporaryDirectory() as temp,
            patch.object(c, "get", side_effect=objects.__getitem__),
        ):
            result = c.fetch("PMC123", 1, "10.1021/test", "T01", "development", Path(temp))
            self.assertEqual(result["source_version"], "author_manuscript")
            self.assertEqual(len(result["figures"]), 1)
            self.assertEqual(result["figures"][0]["status"], "downloaded_not_reviewed")
            self.assertEqual(result["visual_review_status"], "not_reviewed")
            self.assertEqual(
                result["figures"][0]["source_sha256"],
                hashlib.sha256((Path(temp) / "image.jpg").read_bytes()).hexdigest(),
            )

    def test_metadata_identity_journal_and_jats_identity_are_checked(self):
        for doi, journal in [
            ("10.1021/wrong", "Journal of the American Chemical Society"),
            ("10.1021/test", "Different Journal"),
        ]:
            objects, _ = self.source(doi=doi, journal=journal)
            with (
                tempfile.TemporaryDirectory() as temp,
                patch.object(c, "get", side_effect=objects.__getitem__),
            ):
                with self.assertRaises(ValueError):
                    c.fetch("PMC123", 1, "10.1021/test", "T01", "development", Path(temp))

    def test_checksum_and_foreign_version_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "MD5"):
            c.verify_download(b"modified", c.BUCKET + "test?md5=" + "0" * 32)
        objects, metadata = self.source()
        metadata["xml_url"] = c.BUCKET + "PMC123.2/PMC123.2.xml"
        objects[c.BUCKET + "PMC123.1/PMC123.1.json"] = json.dumps(metadata).encode()
        with (
            tempfile.TemporaryDirectory() as temp,
            patch.object(c, "get", side_effect=objects.__getitem__),
        ):
            with self.assertRaisesRegex(ValueError, "different article version"):
                c.fetch("PMC123", 1, "10.1021/test", "T01", "development", Path(temp))

    def test_pagination_does_not_drop_versions(self):
        pages = [
            b"<ListBucketResult><CommonPrefixes><Prefix>PMC123.1/</Prefix></CommonPrefixes>"
            b"<NextContinuationToken>next</NextContinuationToken></ListBucketResult>",
            b"<ListBucketResult><CommonPrefixes><Prefix>PMC123.2/</Prefix></CommonPrefixes></ListBucketResult>",
        ]
        with patch.object(c, "get", side_effect=pages) as get:
            self.assertEqual(c.discover("PMC123"), ["PMC123.1", "PMC123.2"])
            self.assertIn("continuation-token=next", get.call_args.args[0])

    def test_frozen_corpus_provenance_and_split(self):
        self.assertEqual(validate(ROOT)["errors"], [])


if __name__ == "__main__":
    unittest.main()
