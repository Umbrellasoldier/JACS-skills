#!/usr/bin/env python3
"""Preview an opaque chart in grayscale and three modeled color-vision conditions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def linear_rgb(rgb):
    import numpy as np

    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def simulate(rgb, mode: str):
    import numpy as np

    if mode == "grayscale":
        luminance = linear_rgb(rgb) @ np.array([0.2126, 0.7152, 0.0722])
        gray = np.where(
            luminance <= 0.0031308,
            luminance * 12.92,
            1.055 * luminance ** (1 / 2.4) - 0.055,
        )
        return np.repeat(gray[..., None], 3, axis=-1)
    from colorspacious import cspace_convert

    # Colorspacious documents CVD -> sRGB1 for a simulation (the reverse is wrong).
    cvd = {"name": "sRGB1+CVD", "cvd_type": mode, "severity": 100}
    return np.clip(cspace_convert(rgb, cvd, "sRGB1"), 0, 1)


def preview(path: Path, output: Path) -> dict:
    import numpy as np
    from PIL import Image

    output.mkdir(parents=True, exist_ok=True)
    rgba = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", rgba.size, "white")
    rgb = np.asarray(Image.alpha_composite(bg, rgba).convert("RGB")) / 255
    files = []
    for mode in ("grayscale", "deuteranomaly", "protanomaly", "tritanomaly"):
        target = output / f"{path.stem}-{mode}.png"
        pixels = np.rint(simulate(rgb, mode) * 255).astype("uint8")
        Image.fromarray(pixels).save(target)
        files.append({"mode": mode, "file": target.name})
    report = {
        "source": path.name,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "method": "Colorspacious 1.1.2 / Machado et al. model, severity 100; gamut clipped",
        "grayscale": "Linear-sRGB relative luminance, encoded back to sRGB",
        "limitation": "Model previews, not an accessibility certification or user study",
        "files": files,
    }
    (output / (path.stem + "-color-review.json")).write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(preview(args.image, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
