from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install", ROOT / "scripts/install_skills.py")
i = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(i)


class InstallationTests(unittest.TestCase):
    def test_complete_install_resolves_shared_references(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "skills with spaces"
            installed = i.install(ROOT / "skills", dest)
            self.assertEqual(set(installed), set(i.NAMES))
            i.check_links(dest)
            self.assertTrue((dest / "jacs-style-distill/scripts/corpus.py").is_file())

    def test_conflict_preflight_preserves_all_existing_files(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            original = dest / "jacs-writing"
            original.mkdir()
            (original / "personal.txt").write_text("keep")
            with self.assertRaisesRegex(ValueError, "require --replace"):
                i.install(ROOT / "skills", dest)
            self.assertEqual((original / "personal.txt").read_text(), "keep")
            self.assertFalse((dest / "jacs-shared").exists())

    def test_replace_preserves_unrelated_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            unrelated = dest / "unrelated"
            unrelated.mkdir()
            (unrelated / "file").write_text("keep")
            i.install(ROOT / "skills", dest)
            i.install(ROOT / "skills", dest, replace=True)
            self.assertEqual((unrelated / "file").read_text(), "keep")

    def test_failed_replacement_restores_previous_install(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "skills"
            i.install(ROOT / "skills", dest)
            marker = dest / "jacs-shared/marker"
            marker.write_text("original")
            actual_replace = i.os.replace

            def fail_one(source, target):
                if Path(source).parent.name == "stage" and Path(source).name == "jacs-writing":
                    raise OSError("simulated disk error")
                return actual_replace(source, target)

            with patch.object(i.os, "replace", side_effect=fail_one):
                with self.assertRaisesRegex(OSError, "disk error"):
                    i.install(ROOT / "skills", dest, replace=True)
            self.assertEqual(marker.read_text(), "original")
            i.check_links(dest)

    def test_install_cannot_replace_source_tree(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            i.install(ROOT / "skills", ROOT / "skills", replace=True)

    def test_backups_survive_failed_rollback(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "skills"
            i.install(ROOT / "skills", dest)
            (dest / "jacs-shared/marker").write_text("original")
            actual_replace = i.os.replace

            def fail_install_and_restore(source, target):
                source = Path(source)
                if source.parent.name == "backup":
                    raise OSError("restore failed")
                if source.parent.name == "stage" and source.name == "jacs-writing":
                    raise OSError("install failed")
                return actual_replace(source, target)

            with patch.object(i.os, "replace", side_effect=fail_install_and_restore):
                with self.assertRaisesRegex(RuntimeError, "preserved backups"):
                    i.install(ROOT / "skills", dest, replace=True)
            backups = list(Path(temp).glob(".jacs-install-*/backup/jacs-shared/marker"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "original")


if __name__ == "__main__":
    unittest.main()
