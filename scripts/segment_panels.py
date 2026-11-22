#!/usr/bin/env python3
"""Create reproducible panel crops from an explicit normalized panel layout."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from era_core import (
    atomic_write_json,
    get_source_pdf,
    load_evidence_bundle,
    make_region_anchor,
    normalize_bbox,
    register_anchor,
    sha256_bytes,
    sha256_file,
    workspace_paths,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    try:
        import fitz
    except ImportError:
        print("PyMuPDF is required.", file=sys.stderr)
        return 2

    workspace = args.workspace.expanduser().resolve()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    parent_id = spec["parent_region_id"]
    bundle = load_evidence_bundle(workspace)
    parent = bundle["regions"].get(parent_id)
    if not parent:
        raise KeyError(f"Unknown parent_region_id: {parent_id}")
    source_pdf = get_source_pdf(workspace)
    if sha256_file(source_pdf) != (bundle.get("source") or {}).get("sha256"):
        raise RuntimeError("Source PDF hash mismatch")

    document = fitz.open(source_pdf)
    page_number = int(parent["page_number"])
    page = document[page_number - 1]
    page_rect = page.rect
    parent_rect = fitz.Rect(parent["bbox_pdf"])
    panels = spec.get("panels", [])
    if not panels:
        raise ValueError("At least one panel is required")
    for panel_spec in panels:
        rel = [float(v) for v in panel_spec["bbox_relative"]]
        if len(rel) != 4 or not (0 <= rel[0] < rel[2] <= 1 and 0 <= rel[1] < rel[3] <= 1):
            raise ValueError(f"Invalid bbox_relative: {rel}")
        rect = fitz.Rect(
            parent_rect.x0 + rel[0] * parent_rect.width,
            parent_rect.y0 + rel[1] * parent_rect.height,
            parent_rect.x0 + rel[2] * parent_rect.width,
            parent_rect.y0 + rel[3] * parent_rect.height,
        )
        if not page_rect.contains(rect):
            raise ValueError(f"Panel outside parent page: {panel_spec}")
        pix = page.get_pixmap(matrix=fitz.Matrix(args.dpi / 72, args.dpi / 72), clip=rect, alpha=False)
        image_data = pix.tobytes("png")
        pixel_hash = sha256_bytes(image_data)
        bbox_norm = normalize_bbox(tuple(rect), float(page_rect.width), float(page_rect.height))
        anchor = make_region_anchor(bundle["source"]["sha256"], page_number, bbox_norm, pixel_hash)
        panel_id = register_anchor(workspace, "PANEL", anchor, "panel", {
            "parent_region_id": parent_id, "label": str(panel_spec["label"])
        })
        relative_path = Path("extracted") / "panels" / f"{panel_id}.png"
        output = workspace / relative_path
        output.parent.mkdir(parents=True, exist_ok=True)
        if not output.exists():
            output.write_bytes(image_data)
        bundle["panels"][panel_id] = {
            "panel_id": panel_id,
            "parent_region_id": parent_id,
            "label": str(panel_spec["label"]),
            "bbox_pdf": [round(float(v), 3) for v in rect],
            "bbox_normalized": bbox_norm,
            "bbox_relative_to_parent": rel,
            "image_path": relative_path.as_posix(),
            "pixel_sha256": pixel_hash,
            "segmentation_status": "SPECIFIED",
            "quantitative": bool(panel_spec.get("quantitative", False)),
            "axes_review_status": "PENDING",
            "caption_separation_status": "UNVERIFIED",
        }
    document.close()
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    manifest["panel_count"] = len(bundle["panels"])
    atomic_write_json(paths["manifest"], manifest)
    print(f"Registered {len(panels)} panels under {parent_id}. Review each crop and its axes before use.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
