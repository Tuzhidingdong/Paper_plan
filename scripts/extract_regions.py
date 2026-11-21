#!/usr/bin/env python3
"""Extract embedded raster blocks and explicit PDF regions with layout triage hints."""
from __future__ import annotations

import argparse
import io
import json
import math
import sys
from collections import defaultdict
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


def difference_hash(png_data: bytes) -> str:
    """A 64-bit visual-similarity hint; it never merges or deletes Region IDs."""
    from PIL import Image
    image = Image.open(io.BytesIO(png_data)).convert("L").resize((9, 8))
    pixels = list(image.getdata())
    bits = []
    for row in range(8):
        offset = row * 9
        for col in range(8):
            bits.append("1" if pixels[offset + col] > pixels[offset + col + 1] else "0")
    return "".join(bits)


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
        "pixel_width": pixel_width, "pixel_height": pixel_height,
        "layout_fingerprint": difference_hash(png_data),
        "region_type": region_type, "extractor_version": extractor_version,
        "triage_role": "REVIEW_CANDIDATE",
        "triage_reasons": [],
        "caption_blind_ready": False,
        "caption_separation_status": "UNVERIFIED",
    }
    bundle["regions"][region_id] = region
    return region


def mark_repeated_layout_assets(bundle: dict[str, Any], page_count: int) -> int:
    """Label repeated top/bottom assets for Contact Sheet suppression only."""
    groups = defaultdict(list)
    for region in bundle.get("regions", {}).values():
        if region.get("region_type") != "embedded_image_block":
            continue
        bbox = region.get("bbox_normalized") or [0, 0, 1, 1]
        y0, y1 = float(bbox[1]), float(bbox[3])
        zone = "header" if y1 <= 0.24 else ("footer" if y0 >= 0.76 else "body")
        if zone != "body" and region.get("layout_fingerprint"):
            pixel_width = int(region.get("pixel_width") or 0)
            pixel_height = int(region.get("pixel_height") or 0)
            bbox_width = round(float(bbox[2]) - float(bbox[0]), 2)
            bbox_height = round(float(bbox[3]) - float(bbox[1]), 2)
            shape_bucket = (round(pixel_width / 16), round(pixel_height / 16), bbox_width, bbox_height)
            groups[(region["layout_fingerprint"], zone, shape_bucket)].append(region)

    minimum_pages = max(3, int(math.ceil(page_count * 0.15)))
    marked = 0
    for (fingerprint, zone, shape_bucket), members in groups.items():
        pages = {item["page_number"] for item in members}
        if len(pages) < minimum_pages:
            continue
        for region in members:
            region["triage_role"] = "REPEATED_LAYOUT_ASSET"
            region["triage_reasons"] = [
                f"Near-identical {zone} image appears on {len(pages)} pages; retained in evidence but omitted from default triage sheets"
            ]
            marked += 1
    return marked


def _vector_geometry_sidecar(page, crop_rect, candidate_id: str, page_number: int,
                                source_sha256: str, region_id: str) -> dict[str, Any]:
    """Preserve PDF-native vector paths and text spans in crop-local PDF points."""
    import fitz

    def local_point(point):
        return [round(float(point.x) - float(crop_rect.x0), 4),
                round(float(point.y) - float(crop_rect.y0), 4)]

    paths = []
    for drawing in page.get_drawings():
        drawing_rect = fitz.Rect(drawing.get("rect", crop_rect))
        if not drawing_rect.intersects(crop_rect):
            continue
        items = []
        for item_index, item in enumerate(drawing.get("items") or []):
            if not item:
                continue
            command = str(item[0])
            points = []
            if command == "l" and len(item) >= 3:
                points = [local_point(item[1]), local_point(item[2])]
            elif command == "c" and len(item) >= 5:
                points = [local_point(value) for value in item[1:5]]
            elif command == "re" and len(item) >= 2:
                rect = fitz.Rect(item[1])
                points = [
                    [round(float(rect.x0) - crop_rect.x0, 4), round(float(rect.y0) - crop_rect.y0, 4)],
                    [round(float(rect.x1) - crop_rect.x0, 4), round(float(rect.y0) - crop_rect.y0, 4)],
                    [round(float(rect.x1) - crop_rect.x0, 4), round(float(rect.y1) - crop_rect.y0, 4)],
                    [round(float(rect.x0) - crop_rect.x0, 4), round(float(rect.y1) - crop_rect.y0, 4)],
                ]
            elif command == "qu" and len(item) >= 2:
                quad = item[1]
                points = [local_point(getattr(quad, name)) for name in ("ul", "ur", "lr", "ll")]
            else:
                continue
            if points:
                items.append({"item_index": item_index, "command": command, "points": points})
        if not items:
            continue
        paths.append({
            "path_id": f"VEC-{len(paths) + 1:06d}",
            "bbox": [
                round(float(drawing_rect.x0) - crop_rect.x0, 4),
                round(float(drawing_rect.y0) - crop_rect.y0, 4),
                round(float(drawing_rect.x1) - crop_rect.x0, 4),
                round(float(drawing_rect.y1) - crop_rect.y0, 4),
            ],
            "stroke_color": drawing.get("color"),
            "fill_color": drawing.get("fill"),
            "stroke_width": drawing.get("width"),
            "close_path": bool(drawing.get("closePath", False)),
            "items": items,
        })

    text_spans = []
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                bbox = span.get("bbox")
                if not bbox:
                    continue
                span_rect = fitz.Rect(bbox)
                if not span_rect.intersects(crop_rect):
                    continue
                text_spans.append({
                    "text": str(span.get("text") or ""),
                    "bbox": [
                        round(float(span_rect.x0) - crop_rect.x0, 4),
                        round(float(span_rect.y0) - crop_rect.y0, 4),
                        round(float(span_rect.x1) - crop_rect.x0, 4),
                        round(float(span_rect.y1) - crop_rect.y0, 4),
                    ],
                    "font": span.get("font"),
                    "font_size": span.get("size"),
                    "flags": span.get("flags"),
                })
    text_spans.sort(key=lambda item: (item["bbox"][1], item["bbox"][0]))
    return {
        "schema_version": 1,
        "geometry_source": "PDF_NATIVE_VECTOR_AND_TEXT",
        "source_pdf_sha256": source_sha256,
        "candidate_id": candidate_id,
        "region_id": region_id,
        "page_number": page_number,
        "coordinate_system": "PDF_CROP_POINT",
        "coordinate_frame": {
            "width": round(float(crop_rect.width), 4),
            "height": round(float(crop_rect.height), 4),
        },
        "bbox_pdf": [round(float(value), 4) for value in crop_rect],
        "path_count": len(paths),
        "text_span_count": len(text_spans),
        "paths": paths,
        "text_spans": text_spans,
        "limitations": [
            "Vector coordinates preserve PDF drawing geometry, not the instrument's original numeric data.",
            "Text-span extraction preserves glyph text and location but does not assign tick labels to axes.",
            "Cubic path control points are not measured data points; use a curve parameter only when the displayed path itself is the intended trace."
        ],
    }


def extract_vector_figure_candidates(document, manifest, workspace: Path, bundle: dict[str, Any], dpi: int) -> int:
    """Rasterize every ingest-time vector plot candidate at the requested DPI.

    Candidate records are durable source-coverage obligations. A candidate is
    not assumed to be a scientific figure until the Agent explicitly triages it.
    """
    import fitz
    figure_candidates = bundle.setdefault("figure_candidates", {})
    added = 0
    for page_record in manifest.get("pages", []):
        if not page_record.get("vector_or_text_figure_review"):
            continue
        page_number = int(page_record.get("page_number") or 0)
        if page_number < 1 or page_number > len(document):
            raise ValueError(f"Invalid vector-candidate page number: {page_number}")
        page = document[page_number - 1]
        candidates = page_record.get("vector_figure_candidates") or []
        if not candidates and page_record.get("vector_candidate_bbox_pdf"):
            candidates = [{
                "candidate_index": 1,
                "bbox_pdf": page_record["vector_candidate_bbox_pdf"],
                "bbox_normalized": page_record.get("vector_candidate_bbox_normalized"),
                "reason": page_record.get("vector_review_reason") or "legacy_vector_candidate",
            }]
        region_ids = []
        if not candidates:
            candidate_id = f"VFIG-P{page_number:04d}-01"
            figure_candidates[candidate_id] = {
                "candidate_id": candidate_id,
                "candidate_type": "VECTOR_PLOT_CLUSTER",
                "page_number": page_number,
                "extraction_status": "BLOCKED_NO_BBOX",
                "triage_status": "PENDING_TRIAGE",
                "disposition": None,
                "reason": "The ingest detector flagged this page but did not retain a crop BBox.",
            }
            page_record["vector_candidate_extraction_status"] = "BLOCKED_NO_BBOX"
            continue

        for index, candidate in enumerate(candidates, start=1):
            candidate_id = f"VFIG-P{page_number:04d}-{index:02d}"
            bbox_values = candidate.get("bbox_pdf")
            if not isinstance(bbox_values, (list, tuple)) or len(bbox_values) != 4:
                figure_candidates[candidate_id] = {
                    "candidate_id": candidate_id,
                    "candidate_type": "VECTOR_PLOT_CLUSTER",
                    "page_number": page_number,
                    "extraction_status": "BLOCKED_INVALID_BBOX",
                    "triage_status": "PENDING_TRIAGE",
                    "disposition": None,
                    "reason": "The vector candidate has no valid four-coordinate PDF BBox.",
                }
                continue
            rect = fitz.Rect(bbox_values) & page.rect
            if rect.is_empty or rect.width <= 0 or rect.height <= 0:
                raise ValueError(f"Vector candidate BBox is empty or outside page {page_number}: {bbox_values}")
            pix = page.get_pixmap(
                matrix=fitz.Matrix(dpi / 72, dpi / 72),
                clip=rect,
                alpha=False,
                colorspace=fitz.csRGB,
            )
            region = record_region(
                workspace, bundle, page_number, tuple(rect),
                float(page.rect.width), float(page.rect.height),
                pix.tobytes("png"), "vector_plot_candidate", EXTRACTOR_VERSION,
            )
            relative = Path(region["image_path"])
            asset_path = workspace / relative
            geometry = _vector_geometry_sidecar(
                page, rect, candidate_id, page_number,
                str(bundle.get("source", {}).get("sha256") or ""), region["region_id"]
            )
            geometry_relative = Path("extracted") / "vector_geometry" / f"{candidate_id}.json"
            geometry_path = workspace / geometry_relative
            atomic_write_json(geometry_path, geometry)
            figure_candidates[candidate_id] = {
                "candidate_id": candidate_id,
                "candidate_type": "VECTOR_PLOT_CLUSTER",
                "page_number": page_number,
                "bbox_pdf": [round(float(value), 3) for value in rect],
                "bbox_normalized": region["bbox_normalized"],
                "region_id": region["region_id"],
                "image_path": region["image_path"],
                "pixel_sha256": region["pixel_sha256"],
                "asset_sha256": sha256_file(asset_path),
                "pixel_width": region["pixel_width"],
                "pixel_height": region["pixel_height"],
                "vector_geometry_path": geometry_relative.as_posix(),
                "vector_geometry_sha256": sha256_file(geometry_path),
                "vector_geometry_path_count": geometry["path_count"],
                "vector_geometry_text_span_count": geometry["text_span_count"],
                "detector_reason": candidate.get("reason"),
                "extraction_status": "EXTRACTED",
                "triage_status": "PENDING_TRIAGE",
                "disposition": None,
                "result_ids": [],
                "reason": None,
            }
            region_ids.append(region["region_id"])
            added += 1
        page_record["vector_candidate_region_ids"] = region_ids
        page_record["vector_candidate_extraction_status"] = (
            "EXTRACTED" if region_ids else "BLOCKED"
        )
    return added


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
    paths = workspace_paths(workspace)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8")) if paths["manifest"].exists() else {"pages": []}
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
            added += 1

    vector_added = extract_vector_figure_candidates(document, manifest, workspace, bundle, args.dpi)
    added += vector_added

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
            added += 1

    page_count = len(document)
    document.close()
    repeated = mark_repeated_layout_assets(bundle, page_count)
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    manifest["stage"] = "REGIONS_EXTRACTED"
    manifest["region_count"] = len(bundle["regions"])
    manifest["repeated_layout_asset_count"] = repeated
    atomic_write_json(paths["manifest"], manifest)
    print(f"Newly processed regions: {added}")
    print(f"Total known regions: {len(bundle['regions'])}")
    print(f"Automatically rasterized vector plot candidates: {vector_added}")
    print(f"Pending source-figure triage decisions: {sum(1 for item in bundle.get('figure_candidates', {}).values() if item.get('triage_status') == 'PENDING_TRIAGE')}")
    print(f"Repeated header/footer assets marked for triage suppression: {repeated}")
    print("All Regions remain preserved; vector candidate images retain PDF-coordinate provenance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
