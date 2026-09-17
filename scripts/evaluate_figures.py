#!/usr/bin/env python3
"""Execute public figure acceptance cases; write actual results and original synthetic plots."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/jacs-figure/scripts"))
from audit_figure import audit_layout  # noqa: E402
from figure_spec import digest  # noqa: E402
from plot_figures import render  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cases_path = ROOT / "evaluation/figures/cases.json"
    cases = json.loads(cases_path.read_text())
    results = []
    for case in cases:
        row = {"id": case["id"], "purpose": case["purpose"], "expected": case["expected"]}
        if "layout" in case:
            findings = audit_layout(case["layout"])
            row.update(
                observed="FAIL"
                if any(f["status"] == "FAIL" for f in findings)
                else "MECHANICAL_PASS",
                findings=findings,
            )
        else:
            source = ROOT / "skills/jacs-figure/assets/examples" / (case["example"] + ".json")
            spec = json.loads(source.read_text())
            for change in case.get("changes", []):
                target = spec
                for key in change["path"][:-1]:
                    target = target[key]
                target[change["path"][-1]] = change["value"]
            original = copy.deepcopy(spec)
            path = args.output_dir / (case["id"] + ".input.json")
            path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
            try:
                qa = render(path, args.output_dir / case["id"], overwrite=True)
                row.update(
                    observed=qa["verdict"],
                    findings=qa["findings"],
                    pdf_sha256=qa["pdf_sha256"],
                    provenance=qa["provenance"],
                )
            except ValueError as exc:
                row.update(observed="REJECTED", reason=str(exc))
            row["input_preserved"] = json.loads(path.read_text()) == original
        row["passed"] = row["observed"] in case["expected"] and row.get("input_preserved", True)
        results.append(row)
    report = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "cases_sha256": digest(cases_path),
        "renderer_sha256": digest(ROOT / "skills/jacs-figure/scripts/plot_figures.py"),
        "cases": results,
        "passed": sum(r["passed"] for r in results),
        "total": len(results),
        "scope": "Mechanical acceptance, not blind aesthetic or scientific-author validation",
    }
    (args.output_dir / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("passed", "total", "scope")}))
    return int(report["passed"] != report["total"])


if __name__ == "__main__":
    raise SystemExit(main())
