#!/usr/bin/env python3
"""Build triage-only contact sheets, omitting repeated layout assets by default."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from era_core import load_evidence_bundle, workspace_paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--per-sheet", type=int, default=6)
    parser.add_argument("--include-layout-assets", action="store_true")
    args = parser.parse_args()
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        parser.error("Pillow is required for contact sheets. Install requirements.txt")

    workspace = args.workspace.expanduser().resolve()
    paths = workspace_paths(workspace)
    bundle = load_evidence_bundle(workspace)
    all_regions = sorted(bundle.get("regions", {}).values(), key=lambda item: (item["page_number"], item["region_id"]))
    omitted = [] if args.include_layout_assets else [
        item for item in all_regions if item.get("triage_role") == "REPEATED_LAYOUT_ASSET"
    ]
    regions = all_regions if args.include_layout_assets else [
        item for item in all_regions if item.get("triage_role") != "REPEATED_LAYOUT_ASSET"
    ]
    print(f"Regions retained in evidence: {len(all_regions)}")
    print(f"Repeated layout assets omitted from triage: {len(omitted)}")
    if not regions:
        print("No triage candidates remain. Use --include-layout-assets to inspect all preserved regions.")
        return 0
    columns = 2
    rows = math.ceil(args.per_sheet / columns)
    cell_w, cell_h = 520, 390
    for start in range(0, len(regions), args.per_sheet):
        batch = regions[start:start + args.per_sheet]
        sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, region in enumerate(batch):
            image_path = workspace / region["image_path"]
            try:
                image = Image.open(image_path).convert("RGB")
            except Exception:
                continue
            image.thumbnail((cell_w - 24, cell_h - 60))
            x = (offset % columns) * cell_w + (cell_w - image.width) // 2
            y = (offset // columns) * cell_h + 38
            sheet.paste(image, (x, y))
            draw.text(((offset % columns) * cell_w + 12, (offset // columns) * cell_h + 10),
                      f"{region['region_id']} | p{region['page_number']} | TRIAGE ONLY", fill="black")
        output = paths["contact_sheets"] / f"contact_{start // args.per_sheet + 1:03d}.jpg"
        sheet.save(output, quality=90)
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
