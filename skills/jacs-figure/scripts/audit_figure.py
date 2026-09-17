#!/usr/bin/env python3
"""Inspect exported dimensions/text and measured layout; visual review remains necessary."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def finding(check: str, status: str, detail: str) -> dict:
    return {"check": check, "status": status, "detail": detail}


def overlap(a, b) -> tuple[float, float]:
    return min(a[2], b[2]) - max(a[0], b[0]), min(a[3], b[3]) - max(a[1], b[1])


def audit_layout(layout: dict, min_font_pt: float = 4.5) -> list[dict]:
    width, height = layout["width_pt"], layout["height_pt"]
    findings = []
    texts = layout.get("texts", [])
    for text in texts:
        box = text["bbox_pt"]
        if min(box[:2]) < -0.6 or box[2] > width + 0.6 or box[3] > height + 0.6:
            findings.append(finding("text_clipping", "FAIL", text["text"]))
        if text["font_pt"] < min_font_pt:
            findings.append(finding("text_size", "FAIL", text["text"]))
    for i, left in enumerate(texts):
        for right in texts[i + 1 :]:
            x, y = overlap(left["bbox_pt"], right["bbox_pt"])
            if x > 1.2 and y > 1.2:
                findings.append(
                    finding("text_overlap", "WARN", left["text"] + " / " + right["text"])
                )
    axes = {x["id"]: x["bbox_pt"] for x in layout.get("axes", [])}
    for group in layout.get("comparable_groups", []):
        boxes = [axes[name] for name in group["panels"]]
        indices = (1, 3) if group["orientation"] == "row" else (0, 2)
        for index in indices:
            if max(x[index] for x in boxes) - min(x[index] for x in boxes) > 1.5:
                findings.append(finding("panel_alignment", "FAIL", str(group["panels"])))
        if group.get("equal_size", True):
            dimensions = [(b[2] - b[0], b[3] - b[1]) for b in boxes]
            if any(
                max(x[k] for x in dimensions) - min(x[k] for x in dimensions) > 1.5 for k in (0, 1)
            ):
                findings.append(finding("panel_size", "FAIL", str(group["panels"])))
    if not findings:
        findings.append(
            finding(
                "measured_layout",
                "PASS",
                "No detected text clipping or overlap; declared panel groups align",
            )
        )
    return findings


def measure_matplotlib(fig, groups: list[dict] | None = None) -> dict:
    from matplotlib.text import Text

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    scale = 72 / fig.dpi
    suppressed_ticks = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            lo, hi = sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                if not lo - 1e-10 <= tick.get_loc() <= hi + 1e-10:
                    suppressed_ticks.update((id(tick.label1), id(tick.label2)))
    texts = []
    for text in fig.findobj(Text):
        if id(text) in suppressed_ticks or not text.get_visible() or not text.get_text().strip():
            continue
        box = text.get_window_extent(renderer)
        if box.width <= 0 or box.height <= 0:
            continue
        texts.append(
            {
                "text": text.get_text(),
                "font_pt": float(text.get_fontsize()),
                "bbox_pt": [float(x) * scale for x in box.extents],
            }
        )
    return {
        "width_pt": float(fig.get_figwidth()) * 72,
        "height_pt": float(fig.get_figheight()) * 72,
        "texts": texts,
        "axes": [
            {
                "id": str(i),
                "bbox_pt": [float(x) * scale for x in ax.get_window_extent(renderer).extents],
            }
            for i, ax in enumerate(fig.axes)
        ],
        "comparable_groups": groups or [],
    }


def audit_pdf(path: Path, width_pt: float, height_pt: float, min_font_pt: float = 4.5) -> dict:
    from audit_strokes import audit_strokes
    from pypdf import PdfReader

    reader = PdfReader(path)
    findings = []
    sizes = []
    if len(reader.pages) != 1:
        findings.append(
            finding("page_count", "FAIL", f"Expected one page; got {len(reader.pages)}")
        )
    for page in reader.pages:
        actual = (float(page.mediabox.width), float(page.mediabox.height))
        if abs(actual[0] - width_pt) > 0.2 or abs(actual[1] - height_pt) > 0.2:
            findings.append(
                finding(
                    "physical_size", "FAIL", f"Measured {actual}; requested {(width_pt, height_pt)}"
                )
            )
        else:
            findings.append(finding("physical_size", "PASS", f"Measured {actual} pt"))

        def visit(text, cm, tm, font, font_size):
            if not text.strip() or font is None:
                return
            # Linear part of the text matrix followed by the current transformation.
            a = tm[0] * cm[0] + tm[1] * cm[2]
            b = tm[0] * cm[1] + tm[1] * cm[3]
            c = tm[2] * cm[0] + tm[3] * cm[2]
            d = tm[2] * cm[1] + tm[3] * cm[3]
            squared_norm = a * a + b * b + c * c + d * d
            determinant = a * d - b * c
            largest = math.sqrt(
                (squared_norm + math.sqrt(max(0, squared_norm**2 - 4 * determinant**2))) / 2
            )
            smallest = abs(determinant) / largest if largest else 0
            effective = abs(float(font_size)) * smallest
            if effective > 0:
                sizes.append(effective)

        try:
            page.extract_text(visitor_text=visit)
        except (ValueError, TypeError, KeyError, NotImplementedError) as error:
            findings.append(finding("pdf_text", "UNKNOWN", str(error)))
    if not sizes:
        findings.append(
            finding(
                "pdf_text",
                "UNKNOWN",
                "No supported text runs; outlined/raster text needs visual inspection",
            )
        )
    elif min(sizes) + 0.01 < min_font_pt:
        findings.append(
            finding(
                "pdf_text_size",
                "FAIL",
                f"Effective text minimum {min(sizes):.3f} pt; floor {min_font_pt}",
            )
        )
    else:
        findings.append(
            finding("pdf_text_size", "PASS", f"Effective text minimum {min(sizes):.3f} pt")
        )
    findings.append(audit_strokes(reader))
    return {
        "pdf_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "findings": findings,
        "minimum_text_pt": min(sizes) if sizes else None,
        "scope": (
            "MediaBox, extractable transformed text and supported path strokes; not all glyphs, "
            "image DPI, "
            "chemical identity or data correctness"
        ),
    }


def verdict(findings: list[dict]) -> str:
    if any(f["status"] == "FAIL" for f in findings):
        return "FAIL"
    if any(f["status"] in {"WARN", "UNKNOWN"} for f in findings):
        return "REVIEW_REQUIRED"
    return "MECHANICAL_PASS"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--width-pt", required=True, type=float)
    parser.add_argument("--height-pt", required=True, type=float)
    parser.add_argument("--min-font-pt", default=4.5, type=float)
    parser.add_argument("--layout", type=Path)
    args = parser.parse_args()
    try:
        result = audit_pdf(args.pdf, args.width_pt, args.height_pt, args.min_font_pt)
        if args.layout:
            result["findings"].extend(
                audit_layout(json.loads(args.layout.read_text()), args.min_font_pt)
            )
    except (OSError, ValueError, ImportError) as error:
        parser.exit(2, f"not auditable: {error}\n")
    result["verdict"] = verdict(result["findings"])
    result["visual_review"] = "required"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result["verdict"] == "FAIL")


if __name__ == "__main__":
    raise SystemExit(main())
