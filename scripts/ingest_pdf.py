#!/usr/bin/env python3
"""Initialize an ERA workspace from exactly one PDF report."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

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
            "vector_or_text_figure_review": bool(drawings) and not images,
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
