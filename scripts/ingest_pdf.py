#!/usr/bin/env python3
"""Initialize an ERA workspace from one PDF and flag likely vector-figure pages."""
from __future__ import annotations

import argparse
import shutil
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


def _item_type_counts(drawings):
    counts = Counter()
    for drawing in drawings:
        for item in drawing.get("items") or ():
            if item:
                counts[str(item[0])] += 1
    return counts


def _grid_components(cell_weights):
    remaining = set(cell_weights)
    components = []
    while remaining:
        seed = remaining.pop()
        queue = deque([seed])
        component = [seed]
        while queue:
            x, y = queue.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbour = (x + dx, y + dy)
                    if neighbour in remaining:
                        remaining.remove(neighbour)
                        queue.append(neighbour)
                        component.append(neighbour)
        components.append(component)
    return components


def assess_vector_figure_review(drawings, page_rect):
    """Flag spatially coherent, plot-like vector clusters for human review.

    Candidate scoring uses the central-page cluster, not the union of every
    drawing on the whole page. The legacy drawing_bbox_area_ratio now reports
    the largest cluster's bounding area; the full-page union is separate.
    This is triage, not semantic chart recognition.
    """
    drawing_count = len(drawings)
    item_counts = _item_type_counts(drawings)
    drawing_item_count = sum(item_counts.values())
    page_width = float(page_rect.width)
    page_height = float(page_rect.height)
    page_area = page_width * page_height
    if page_width <= 0 or page_height <= 0:
        return {
            "drawing_item_count": drawing_item_count,
            "drawing_bbox_area_ratio": 0.0,
            "drawing_full_page_union_bbox_area_ratio": 0.0,
            "drawing_grid_occupancy_ratio": 0.0,
            "central_drawing_count": 0,
            "largest_cluster_drawing_count": 0,
            "vector_item_type_counts": dict(item_counts),
            "vector_or_text_figure_review": False,
            "vector_review_reason": None,
        }

    rects = [d.get("rect") for d in drawings if d.get("rect") is not None]
    if rects:
        x0 = min(float(r.x0) for r in rects)
        y0 = min(float(r.y0) for r in rects)
        x1 = max(float(r.x1) for r in rects)
        y1 = max(float(r.y1) for r in rects)
        full_page_union_ratio = min(1.0, max(0.0, (x1 - x0) * (y1 - y0) / page_area))
    else:
        full_page_union_ratio = 0.0

    # Ignore the outer page furniture for candidate scoring, but retain all
    # drawings and source metadata in the page inventory.
    cell_weights = defaultdict(int)
    cell_types = defaultdict(Counter)
    central_drawings = []
    columns, rows = 8, 6
    for drawing in drawings:
        rect = drawing.get("rect")
        if rect is None:
            continue
        cx = (float(rect.x0) + float(rect.x1)) / 2.0 / page_width
        cy = (float(rect.y0) + float(rect.y1)) / 2.0 / page_height
        if not (0.04 <= cx <= 0.96 and 0.12 <= cy <= 0.90):
            continue
        central_drawings.append(drawing)
        gx = min(columns - 1, max(0, int(cx * columns)))
        gy = min(rows - 1, max(0, int(cy * rows)))
        cell = (gx, gy)
        items = drawing.get("items") or ()
        cell_weights[cell] += max(1, len(items))
        for item in items:
            if item:
                cell_types[cell][str(item[0])] += 1

    components = _grid_components(cell_weights)
    if components:
        largest = max(components, key=lambda cells: sum(cell_weights[c] for c in cells))
        largest_set = set(largest)
        cluster_drawing_count = 0
        for drawing in central_drawings:
            rect = drawing.get("rect")
            cx = (float(rect.x0) + float(rect.x1)) / 2.0 / page_width
            cy = (float(rect.y0) + float(rect.y1)) / 2.0 / page_height
            cell = (
                min(columns - 1, max(0, int(cx * columns))),
                min(rows - 1, max(0, int(cy * rows))),
            )
            if cell in largest_set:
                cluster_drawing_count += 1
        cluster_types = Counter()
        for cell in largest:
            cluster_types.update(cell_types[cell])
        min_x = min(cell[0] for cell in largest)
        max_x = max(cell[0] for cell in largest)
        min_y = min(cell[1] for cell in largest)
        max_y = max(cell[1] for cell in largest)
        cluster_bbox_ratio = ((max_x - min_x + 1) / columns) * ((max_y - min_y + 1) / rows)
    else:
        cluster_drawing_count = 0
        cluster_types = Counter()
        cluster_bbox_ratio = 0.0

    occupied_ratio = len(cell_weights) / float(columns * rows)
    line_items = cluster_types.get("l", 0)
    rectangle_items = cluster_types.get("re", 0)
    quad_items = cluster_types.get("qu", 0)
    plot_primitives = line_items + rectangle_items + quad_items

    reason = None
    if cluster_drawing_count >= 50 and plot_primitives >= 80:
        reason = "dense_vector_figure_cluster"
    elif (
        cluster_drawing_count >= 12
        and rectangle_items >= 8
        and cluster_bbox_ratio >= 0.04
        and len(max(components, key=len)) >= 2
    ):
        reason = "moderate_rectangular_plot_cluster"
    elif (
        cluster_drawing_count >= 18
        and line_items >= 32
        and occupied_ratio >= 0.04
        and cluster_bbox_ratio >= 0.06
    ):
        reason = "moderate_line_plot_cluster"

    return {
        "drawing_item_count": drawing_item_count,
        "drawing_bbox_area_ratio": round(cluster_bbox_ratio, 4),
        "drawing_full_page_union_bbox_area_ratio": round(full_page_union_ratio, 4),
        "drawing_grid_occupancy_ratio": round(occupied_ratio, 4),
        "central_drawing_count": len(central_drawings),
        "largest_cluster_drawing_count": cluster_drawing_count,
        "vector_item_type_counts": dict(item_counts),
        "cluster_plot_primitive_counts": {
            "line": line_items,
            "rectangle": rectangle_items,
            "quad": quad_items,
        },
        "vector_or_text_figure_review": reason is not None,
        "vector_review_reason": reason,
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
        "vector_detector_version": "spatial-vector-cluster/0.2.0",
        "vector_review_candidate_count": sum(1 for item in page_records if item["vector_or_text_figure_review"]),
        "workspace_revision": "0.3.0",
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
    print(f"Vector figure review candidates: {sum(1 for item in page_records if item['vector_or_text_figure_review'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
