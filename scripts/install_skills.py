#!/usr/bin/env python3
"""Install the sibling skill folders with dependency checks and rollback."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import tempfile
from pathlib import Path

NAMES = ("jacs-shared", "jacs-style-distill", "jacs-writing", "jacs-polishing", "jacs-figure")


def check_links(root: Path) -> None:
    for name in NAMES:
        if not (root / name / "SKILL.md").is_file():
            raise ValueError(f"Missing skill dependency: {name}")
        for file in (root / name).rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
                if re.match(r"^[a-z]+://", target) or target.startswith("#"):
                    continue
                path = (file.parent / target.split("#")[0]).resolve()
                if not path.is_relative_to(root.resolve()) or not path.exists():
                    raise ValueError(
                        f"Missing or external local skill reference: {file.name}: {target}"
                    )


def install(source: Path, destination: Path, replace: bool = False) -> list[str]:
    source, destination = source.resolve(), destination.expanduser().resolve()
    if destination == source or destination.is_relative_to(source):
        raise ValueError("Choose a destination outside the source skill tree")
    check_links(source)
    conflicts = [
        name for name in NAMES if (destination / name).exists() or (destination / name).is_symlink()
    ]
    if conflicts and not replace:
        raise ValueError("Existing skills require --replace: " + ", ".join(conflicts))
    destination.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".jacs-install-", dir=destination.parent))
    cleanup = True
    try:
        stage = temp / "stage"
        backup = temp / "backup"
        backup.mkdir()
        for name in NAMES:
            shutil.copytree(
                source / name, stage / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )
        check_links(stage)
        moved, installed = [], []
        try:
            for name in NAMES:
                target = destination / name
                if name in conflicts:
                    os.replace(target, backup / name)
                    moved.append(name)
                os.replace(stage / name, target)
                installed.append(name)
        except OSError:
            cleanup = False
            try:
                for name in reversed(installed):
                    target = destination / name
                    if target.is_dir() and not target.is_symlink():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                for name in reversed(moved):
                    os.replace(backup / name, destination / name)
            except OSError as recovery_error:
                raise RuntimeError(
                    f"Recovery incomplete; preserved backups in {backup}"
                ) from recovery_error
            cleanup = True
            raise
    finally:
        if cleanup:
            shutil.rmtree(temp)
    return list(NAMES)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--replace", action="store_true", help="Replace only these five named skills"
    )
    args = parser.parse_args()
    try:
        names = install(
            Path(__file__).resolve().parents[1] / "skills", args.destination, args.replace
        )
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"error: {error}\n")
    print("Installed: " + ", ".join(names))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
