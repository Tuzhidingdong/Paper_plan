#!/usr/bin/env python3
"""Refresh vector-review diagnostics in an existing workspace without resetting evidence."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from era_core import atomic_write_json, get_source_pdf, sha256_file, workspace_paths
from ingest_pdf import assess_vector_figure_review

DETECTOR_VERSION = "spatial-vector-cluster/0.2.0"


def refresh(workspace: Path) -> dict:
    paths = workspace_paths(workspace)
    source_pdf = get_source_pdf(workspace)
    manifest_path = paths["manifest"]
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing state manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_hash = sha256_file(source_pdf)
    expected = (
        (manifest.get("source_pdf") or {}).get("sha256")
        or (manifest.get("source") or {}).get("sha256")
    )
    if expected != source_hash:
        raise ValueError("Source PDF hash differs from workspace manifest; refusing to refresh stale page diagnostics")

    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required; install requirements.txt") from exc

    doc = fitz.open(source_pdf)
    if len(doc) != len(manifest.get("pages", [])):
        doc.close()
        raise ValueError("PDF page count differs from workspace manifest")

    changed = []
    total_candidates = 0
    for index, page in enumerate(doc):
        record = manifest["pages"][index]
        diagnostics = assess_vector_figure_review(page.get_drawings(), page.rect)
        record.update(diagnostics)
        record["vector_detector_version"] = DETECTOR_VERSION
        if diagnostics["vector_or_text_figure_review"]:
            total_candidates += 1
        changed.append({
            "page_number": index + 1,
            "candidate": diagnostics["vector_or_text_figure_review"],
            "reason": diagnostics["vector_review_reason"],
            "drawing_count": record.get("drawing_count", 0),
            "drawing_item_count": diagnostics["drawing_item_count"],
            "largest_cluster_drawing_count": diagnostics["largest_cluster_drawing_count"],
            "drawing_bbox_area_ratio": diagnostics["drawing_bbox_area_ratio"],
            "drawing_full_page_union_bbox_area_ratio": diagnostics["drawing_full_page_union_bbox_area_ratio"],
        })
    doc.close()
    manifest["vector_detector_version"] = DETECTOR_VERSION
    manifest["vector_review_candidate_count"] = total_candidates
    atomic_write_json(manifest_path, manifest)
    return {
        "source_sha256": source_hash,
        "page_count": len(changed),
        "candidate_count": total_candidates,
        "pages": changed,
        "manifest": str(manifest_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    try:
        report = refresh(workspace)
    except Exception as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    report["status"] = "PASS"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
