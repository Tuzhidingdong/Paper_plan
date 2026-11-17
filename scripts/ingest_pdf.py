#!/usr/bin/env python3
"""Initialize an ERA workspace from exactly one PDF report."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def assess_vector_figure_review(drawings, page_rect):
    """Return a conservative review flag and diagnostics for vector-heavy pages.

    Embedded raster images are deliberately not part of this decision: a page may
    contain both a banner/logo image and a scientifically relevant vector chart.
    This is a triage heuristic, not automatic figure recognition.
    """
    drawing_count = len(drawings)
    drawing_item_count = sum(len(drawing.get("items") or ()) for drawing in drawings)

    rects = [drawing.get("rect") for drawing in drawings if drawing.get("rect") is not None]
    if rects and float(page_rect.width) > 0 and float(page_rect.height) > 0:
        x0 = min(float(rect.x0) for rect in rects)
        y0 = min(float(rect.y0) for rect in rects)
        x1 = max(float(rect.x1) for rect in rects)
        y1 = max(float(rect.y1) for rect in rects)
        bbox_area_ratio = max(0.0, (x1 - x0) * (y1 - y0)) / (
            float(page_rect.width) * float(page_rect.height)
        )
        bbox_area_ratio = min(1.0, bbox_area_ratio)
    else:
        bbox_area_ratio = 0.0

    # Dense vector pages are always candidates. Smaller groups are flagged only
    # when they contain many drawing commands or span a meaningful page area.
    if drawing_count >= 100:
        review_reason = "dense_vector_paths"
    elif drawing_count >= 12 and (drawing_item_count >= 48 or bbox_area_ratio >= 0.06):
        review_reason = "distributed_or_complex_vector_drawings"
    else:
        review_reason = None

    return {
        "drawing_item_count": drawing_item_count,
        "drawing_bbox_area_ratio": round(bbox_area_ratio, 4),
        "vector_or_text_figure_review": review_reason is not None,
        "vector_review_reason": review_reason,
    }


from era_core import (
    atomic_write_json,
    atomic_write_text,
    default_evidence_bundle,
    ensure_workspace_dirs,
    sha256_file,
    workspace_paths,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Input experimental-report PDF")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--force-new-source", action="store_true", help="Replace the source only when creating a new workspace revision")
    args = parser.parse_args()

    source = args.pdf.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        parser.error("Input must be an existing PDF file")

    try:
        import fitz
    except ImportError:
        print("PyMuPDF is required. Install with: python -m pip install -r requirements.txt", file=sys.stderr)
        return 2

    workspace = args.workspace.expanduser().resolve()
    paths = ensure_workspace_dirs(workspace)
    destination = paths["source"] / "original_report.pdf"
    if destination.exists():
        existing_hash = sha256_file(destination)
        incoming_hash = sha256_file(source)
        if existing_hash != incoming_hash and not args.force_new_source:
            print("Workspace already contains a different source PDF. Use a new workspace or --force-new-source.", file=sys.stderr)
            return 2
        if existing_hash == incoming_hash:
            print(f"Source unchanged: {existing_hash}")
            return 0

    if source != destination:
        shutil.copy2(source, destination)
    try:
        destination.chmod(0o444)
    except OSError:
        pass

    document = fitz.open(destination)
    page_records = []
    text_root = workspace / "extracted" / "page_text"
    text_root.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(document):
        page_text = page.get_text("text") or ""
        text_path = text_root / f"page_{index + 1:04d}.txt"
        atomic_write_text(text_path, page_text)
        drawings = page.get_drawings()
        images = page.get_images(full=True)
        vector_review = assess_vector_figure_review(drawings, page.rect)
        page_records.append({
            "page_number": index + 1,
            "width": round(float(page.rect.width), 3),
            "height": round(float(page.rect.height), 3),
            "rotation": int(page.rotation),
            "text_path": str(text_path.relative_to(workspace)).replace("\\", "/"),
            "text_characters": len(page_text),
            "embedded_image_count": len(images),
            "image_block_count": sum(1 for block in page.get_text("dict").get("blocks", []) if block.get("type") == 1),
            "drawing_count": len(drawings),
            **vector_review,
        })
    document.close()

    source_hash = sha256_file(destination)
    bundle = default_evidence_bundle()
    bundle["source"] = {
        "file_name": destination.name,
        "sha256": source_hash,
        "page_count": len(page_records),
        "tool_versions": {"pymupdf": getattr(fitz, "VersionBind", "unknown")},
    }
    atomic_write_json(paths["bundle"], bundle)
    manifest = {
        "schema_version": 1,
        "workspace_revision": "0.1.0",
        "stage": "INGESTED",
        "source_pdf": {
            "path": "source/original_report.pdf",
            "sha256": source_hash,
            "page_count": len(page_records),
        },
        "pages": page_records,
        "bundles": {"evidence_bundle.json": "HEAD"},
        "tools": {"pymupdf": getattr(fitz, "VersionBind", "unknown")},
        "validation": {"status": "NOT_RUN", "errors": [], "warnings": []},
        "capability_profile": None,
    }
    atomic_write_json(paths["manifest"], manifest)
    print(f"Initialized ERA workspace: {workspace}")
    print(f"PDF SHA-256: {source_hash}")
    print(f"Pages: {len(page_records)}")
    print(f"Vector/text pages requiring review: {sum(1 for item in page_records if item['vector_or_text_figure_review'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
