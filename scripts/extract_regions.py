#!/usr/bin/env python3
"""Extract embedded raster image blocks and explicitly specified PDF regions."""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any

from era_core import (
    EXTRACTOR_VERSION, atomic_write_json, get_source_pdf, load_evidence_bundle,
    make_region_anchor, normalize_bbox, register_anchor, sha256_bytes, sha256_file,
    workspace_paths,
)


def canonicalize_image(data: bytes) -> tuple[bytes, str, int, int]:
    """Return deterministic RGB PNG bytes and a hash of decoded pixels."""
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(data)).convert("RGB")
        width, height = image.size
        pixels = image.tobytes()
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=False)
        return output.getvalue(), sha256_bytes(width.to_bytes(4, "big") + height.to_bytes(4, "big") + pixels), width, height
    except Exception:
        try:
            import fitz
            pixmap = fitz.Pixmap(data)
            if pixmap.n not in (3, 4):
                pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
            if pixmap.n == 4:
                pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
            rgb = pixmap.samples
            width, height = pixmap.width, pixmap.height
            return pixmap.tobytes("png"), sha256_bytes(width.to_bytes(4, "big") + height.to_bytes(4, "big") + rgb), width, height
        except Exception as exc:
            raise ValueError("Cannot decode extracted image into canonical pixels; preserve it for manual review") from exc


def record_region(workspace: Path, bundle: dict[str, Any], page_number: int,
                  bbox: tuple[float, float, float, float], page_width: float, page_height: float,
                  image_data: bytes, region_type: str, extractor_version: str) -> dict[str, Any]:
    paths = workspace_paths(workspace)
    png_data, pixel_hash, pixel_width, pixel_height = canonicalize_image(image_data)
    normalized = normalize_bbox(bbox, page_width, page_height)
    anchor = make_region_anchor(bundle["source"]["sha256"], page_number, normalized, pixel_hash, extractor_version)
    region_id = register_anchor(
        workspace, "REG", anchor, "region",
        {"page_number": page_number, "bbox_normalized": normalized, "pixel_sha256": pixel_hash},
    )
    relative_path = Path("extracted") / "regions" / f"{region_id}.png"
    output = workspace / relative_path
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        output.write_bytes(png_data)
    region = {
        "region_id": region_id, "anchor_key": anchor, "page_number": page_number,
        "bbox_pdf": [round(float(v), 3) for v in bbox], "bbox_normalized": normalized,
        "image_path": relative_path.as_posix(), "pixel_sha256": pixel_hash,
        "pixel_width": pixel_width, "pixel_height": pixel_height, "perceptual_hash": None,
        "region_type": region_type, "extractor_version": extractor_version,
        "caption_blind_ready": region_type in {"embedded_image_block", "specified_pdf_region"},
    }
    bundle["regions"][region_id] = region
    return region


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--regions-json", type=Path, help="Optional JSON list of manual PDF-coordinate regions")
    parser.add_argument("--min-area-ratio", type=float, default=0.002)
    parser.add_argument("--min-pixels", type=int, default=32)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    try:
        import fitz
    except ImportError:
        print("PyMuPDF is required. Install with: python -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    workspace = args.workspace.expanduser().resolve()
    source_pdf = get_source_pdf(workspace)
    bundle = load_evidence_bundle(workspace)
    if sha256_file(source_pdf) != bundle.get("source", {}).get("sha256"):
        print("Source PDF hash mismatch. Do not continue with stale workspace state.", file=sys.stderr)
        return 2

    document = fitz.open(source_pdf)
    added = 0
    for page_index, page in enumerate(document):
        page_width, page_height = float(page.rect.width), float(page.rect.height)
        page_area = page_width * page_height
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") != 1:
                continue
            bbox = tuple(block.get("bbox", (0, 0, 0, 0)))
            if len(bbox) != 4 or (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) < page_area * args.min_area_ratio:
                continue
            image_data = block.get("image")
            if not image_data:
                continue
            if int(block.get("width", 0)) < args.min_pixels or int(block.get("height", 0)) < args.min_pixels:
                continue
            record_region(workspace, bundle, page_index + 1, bbox, page_width, page_height,
                          image_data, "embedded_image_block", EXTRACTOR_VERSION)

    if args.regions_json:
        specs = json.loads(args.regions_json.read_text(encoding="utf-8"))
        if not isinstance(specs, list):
            raise ValueError("regions-json must contain a JSON list")
        for spec in specs:
            page_number = int(spec["page_number"])
            if page_number < 1 or page_number > len(document):
                raise ValueError(f"Invalid page_number: {page_number}")
            page = document[page_number - 1]
            rect = fitz.Rect(spec["bbox_pdf"])
            if not page.rect.contains(rect) or rect.is_empty:
                raise ValueError(f"Region BBox outside page or empty: {spec}")
            pix = page.get_pixmap(matrix=fitz.Matrix(args.dpi / 72, args.dpi / 72), clip=rect, alpha=False)
            record_region(workspace, bundle, page_number, tuple(rect), float(page.rect.width),
                          float(page.rect.height), pix.tobytes("png"), "specified_pdf_region", EXTRACTOR_VERSION)

    document.close()
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    manifest["stage"] = "REGIONS_EXTRACTED"
    manifest["region_count"] = len(bundle["regions"])
    atomic_write_json(paths["manifest"], manifest)
    print(f"Total known regions: {len(bundle['regions'])}")
    print("Reminder: vector-only charts may still require explicit region BBoxes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
