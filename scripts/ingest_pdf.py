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
        seed = min(remaining, key=lambda cell: (cell[1], cell[0]))
        remaining.remove(seed)
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
        components.append(sorted(component, key=lambda cell: (cell[1], cell[0])))
    components.sort(
        key=lambda cells: (
            min(cell[1] for cell in cells),
            min(cell[0] for cell in cells),
            max(cell[1] for cell in cells),
            max(cell[0] for cell in cells),
        )
    )
    return components


def assess_vector_figure_review(drawings, page_rect):
    """Identify plot-like vector clusters and record crop bounds for rasterization.

    The detector is deliberately a recall-oriented page triage heuristic, not
    semantic chart recognition. Each accepted spatial component is retained as
    a separate crop candidate so multiple plots on one page are not collapsed
    into a single page-wide image.
    """
    drawing_item_count = sum(
        len(drawing.get("items") or ()) for drawing in drawings
    )
    page_width = float(page_rect.width)
    page_height = float(page_rect.height)
    page_area = page_width * page_height
    empty = {
        "drawing_item_count": drawing_item_count,
        "drawing_bbox_area_ratio": 0.0,
        "drawing_full_page_union_bbox_area_ratio": 0.0,
        "drawing_grid_occupancy_ratio": 0.0,
        "central_drawing_count": 0,
        "largest_cluster_drawing_count": 0,
        "vector_item_type_counts": dict(_item_type_counts(drawings)),
        "cluster_plot_primitive_counts": {"line": 0, "rectangle": 0, "quad": 0},
        "vector_or_text_figure_review": False,
        "vector_review_reason": None,
        "vector_figure_candidates": [],
        "vector_candidate_bbox_pdf": None,
        "vector_candidate_bbox_normalized": None,
    }
    if page_width <= 0 or page_height <= 0:
        return empty

    all_rects = [item.get("rect") for item in drawings if item.get("rect") is not None]
    if all_rects:
        ux0 = min(float(rect.x0) for rect in all_rects)
        uy0 = min(float(rect.y0) for rect in all_rects)
        ux1 = max(float(rect.x1) for rect in all_rects)
        uy1 = max(float(rect.y1) for rect in all_rects)
        full_page_union_ratio = min(1.0, max(0.0, (ux1-ux0)*(uy1-uy0)/page_area))
    else:
        full_page_union_ratio = 0.0

    columns, rows = 8, 6
    cell_weights = defaultdict(int)
    cell_types = defaultdict(Counter)
    central_drawings = []
    drawing_cells = {}
    for drawing in drawings:
        rect = drawing.get("rect")
        if rect is None:
            continue
        cx = ((float(rect.x0) + float(rect.x1)) / 2.0 - float(page_rect.x0)) / page_width
        cy = ((float(rect.y0) + float(rect.y1)) / 2.0 - float(page_rect.y0)) / page_height
        if not (0.04 <= cx <= 0.96 and 0.12 <= cy <= 0.90):
            continue
        cell = (
            min(columns - 1, max(0, int(cx * columns))),
            min(rows - 1, max(0, int(cy * rows))),
        )
        central_drawings.append(drawing)
        drawing_cells[id(drawing)] = cell
        cell_weights[cell] += max(1, len(drawing.get("items") or ()))
        for item in drawing.get("items") or ():
            if item:
                cell_types[cell][str(item[0])] += 1

    components = _grid_components(cell_weights)
    occupied_ratio = len(cell_weights) / float(columns * rows)
    component_records = []
    for component_index, component in enumerate(components, start=1):
        component_set = set(component)
        component_drawings = [
            drawing for drawing in central_drawings
            if drawing_cells.get(id(drawing)) in component_set
        ]
        component_types = Counter()
        for cell in component:
            component_types.update(cell_types[cell])
        min_x = min(cell[0] for cell in component)
        max_x = max(cell[0] for cell in component)
        min_y = min(cell[1] for cell in component)
        max_y = max(cell[1] for cell in component)
        bbox_ratio = ((max_x-min_x+1)/columns) * ((max_y-min_y+1)/rows)
        line_items = component_types.get("l", 0)
        rectangle_items = component_types.get("re", 0)
        quad_items = component_types.get("qu", 0)
        plot_primitives = line_items + rectangle_items + quad_items
        reason = None
        if len(component_drawings) >= 50 and plot_primitives >= 80:
            reason = "dense_vector_figure_cluster"
        elif len(component_drawings) >= 12 and rectangle_items >= 8 and bbox_ratio >= 0.04 and len(component) >= 2:
            reason = "moderate_rectangular_plot_cluster"
        elif len(component_drawings) >= 18 and line_items >= 32 and occupied_ratio >= 0.04 and bbox_ratio >= 0.06:
            reason = "moderate_line_plot_cluster"
        if not reason:
            continue

        rects = [drawing.get("rect") for drawing in component_drawings if drawing.get("rect") is not None]
        if not rects:
            continue
        x0 = min(float(rect.x0) for rect in rects)
        y0 = min(float(rect.y0) for rect in rects)
        x1 = max(float(rect.x1) for rect in rects)
        y1 = max(float(rect.y1) for rect in rects)
        # Include tick labels, axis titles and nearby legend glyphs around the
        # vector primitives; clip the crop to the physical page rectangle.
        pad_x = max(page_width * 0.035, 2.0)
        pad_y = max(page_height * 0.055, 2.0)
        crop = [
            max(float(page_rect.x0), x0-pad_x),
            max(float(page_rect.y0), y0-pad_y),
            min(float(page_rect.x1), x1+pad_x),
            min(float(page_rect.y1), y1+pad_y),
        ]
        if crop[2] <= crop[0] or crop[3] <= crop[1]:
            continue
        normalized = [
            round((crop[0]-float(page_rect.x0))/page_width, 6),
            round((crop[1]-float(page_rect.y0))/page_height, 6),
            round((crop[2]-float(page_rect.x0))/page_width, 6),
            round((crop[3]-float(page_rect.y0))/page_height, 6),
        ]
        component_records.append({
            "candidate_index": component_index,
            "bbox_pdf": [round(value, 3) for value in crop],
            "bbox_normalized": normalized,
            "reason": reason,
            "drawing_count": len(component_drawings),
            "plot_primitive_counts": {
                "line": line_items, "rectangle": rectangle_items, "quad": quad_items
            },
        })

    largest = max(components, key=lambda cells: sum(cell_weights[cell] for cell in cells)) if components else []
    largest_drawings = [
        drawing for drawing in central_drawings
        if drawing_cells.get(id(drawing)) in set(largest)
    ]
    largest_types = Counter()
    for cell in largest:
        largest_types.update(cell_types[cell])
    largest_bbox_ratio = 0.0
    if largest:
        min_x = min(cell[0] for cell in largest)
        max_x = max(cell[0] for cell in largest)
        min_y = min(cell[1] for cell in largest)
        max_y = max(cell[1] for cell in largest)
        largest_bbox_ratio = ((max_x-min_x+1)/columns) * ((max_y-min_y+1)/rows)

    primary = max(component_records, key=lambda item: item["drawing_count"]) if component_records else None
    return {
        "drawing_item_count": drawing_item_count,
        "drawing_bbox_area_ratio": round(largest_bbox_ratio, 4),
        "drawing_full_page_union_bbox_area_ratio": round(full_page_union_ratio, 4),
        "drawing_grid_occupancy_ratio": round(occupied_ratio, 4),
        "central_drawing_count": len(central_drawings),
        "largest_cluster_drawing_count": len(largest_drawings),
        "vector_item_type_counts": dict(_item_type_counts(drawings)),
        "cluster_plot_primitive_counts": {
            "line": largest_types.get("l", 0),
            "rectangle": largest_types.get("re", 0),
            "quad": largest_types.get("qu", 0),
        },
        "vector_or_text_figure_review": bool(component_records),
        "vector_review_reason": primary.get("reason") if primary else None,
        "vector_figure_candidates": component_records,
        "vector_candidate_bbox_pdf": primary.get("bbox_pdf") if primary else None,
        "vector_candidate_bbox_normalized": primary.get("bbox_normalized") if primary else None,
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
        "vector_detector_version": "spatial-vector-cluster/0.3.0",
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
