from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from extract_regions import mark_repeated_layout_assets
from ingest_pdf import assess_vector_figure_review


class LayoutTriageTests(unittest.TestCase):
    def test_sparse_decorative_page_is_not_flagged(self):
        drawings = [
            {"rect": SimpleNamespace(x0=20, y0=20, x1=500, y1=22), "items": [("l",)]},
            {"rect": SimpleNamespace(x0=20, y0=30, x1=500, y1=32), "items": [("l",)]},
            {"rect": SimpleNamespace(x0=20, y0=40, x1=500, y1=42), "items": [("l",)]},
        ]
        result = assess_vector_figure_review(drawings, SimpleNamespace(width=600, height=800))
        self.assertFalse(result["vector_or_text_figure_review"])

    def test_coherent_vector_bar_cluster_is_flagged(self):
        drawings = []
        for index in range(15):
            x = 70 + index * 28
            drawings.append({
                "rect": SimpleNamespace(x0=x, y0=300 + index % 4 * 10, x1=x + 14, y1=600),
                "items": [("re",)],
            })
        result = assess_vector_figure_review(drawings, SimpleNamespace(width=600, height=800))
        self.assertTrue(result["vector_or_text_figure_review"])
        self.assertEqual(result["vector_review_reason"], "moderate_rectangular_plot_cluster")
        self.assertGreater(result["drawing_grid_occupancy_ratio"], 0)

    def test_repeated_header_images_are_suppressed_only_in_triage(self):
        bundle = {"regions": {
            f"REG00{i}": {
                "region_id": f"REG00{i}", "page_number": i,
                "region_type": "embedded_image_block", "layout_fingerprint": "same-header",
                "bbox_normalized": [0.1, 0.02, 0.4, 0.10], "triage_role": "REVIEW_CANDIDATE",
            } for i in range(1, 5)
        }}
        count = mark_repeated_layout_assets(bundle, 18)
        self.assertEqual(count, 4)
        self.assertTrue(all(x["triage_role"] == "REPEATED_LAYOUT_ASSET" for x in bundle["regions"].values()))
        self.assertEqual(len(bundle["regions"]), 4)

    def test_body_images_are_not_suppressed_as_header_assets(self):
        bundle = {"regions": {
            f"REG00{i}": {
                "region_id": f"REG00{i}", "page_number": i,
                "region_type": "embedded_image_block", "layout_fingerprint": "same-body",
                "bbox_normalized": [0.1, 0.35, 0.4, 0.65], "triage_role": "REVIEW_CANDIDATE",
            } for i in range(1, 5)
        }}
        self.assertEqual(mark_repeated_layout_assets(bundle, 18), 0)


if __name__ == "__main__":
    unittest.main()
