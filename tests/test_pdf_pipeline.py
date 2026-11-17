from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class PdfPipelineTests(unittest.TestCase):
    def test_vector_review_detects_mixed_raster_and_vector_pages(self):
        try:
            import fitz
            from PIL import Image
        except ImportError:
            self.skipTest("PyMuPDF and Pillow are required for PDF integration test")

        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_path = root / "banner.png"
            Image.new("RGB", (180, 40), "white").save(image_path)
            pdf_path = root / "vector_review.pdf"

            doc = fitz.open()

            # Dense vector chart plus an unrelated embedded banner image:
            # the raster image must not suppress the vector-review flag.
            dense_page = doc.new_page(width=600, height=800)
            dense_page.insert_image(fitz.Rect(20, 20, 200, 60), filename=str(image_path))
            for i in range(60):
                y = 220 + i * 5
                dense_page.draw_line((70, y), (530, y), color=(0, 0, 0), width=0.4)
                dense_page.draw_line((70 + i * 5, 220), (70 + i * 5, 520), color=(0, 0, 0), width=0.4)

            # A few ordinary decorative paths on a page that also has an image
            # should not be enough to request vector-figure review.
            decorative_page = doc.new_page(width=600, height=800)
            decorative_page.insert_image(fitz.Rect(20, 20, 200, 60), filename=str(image_path))
            decorative_page.draw_rect(fitz.Rect(30, 30, 190, 55), color=(0.2, 0.2, 0.2))
            decorative_page.draw_line((30, 70), (190, 70), color=(0.2, 0.2, 0.2))
            decorative_page.draw_line((30, 72), (190, 72), color=(0.2, 0.2, 0.2))

            # A moderate number of vector bars spread over a figure-sized area
            # should also be considered a review candidate.
            chart_page = doc.new_page(width=600, height=800)
            for i in range(15):
                x = 70 + i * 28
                top = 300 + (i % 5) * 20
                chart_page.draw_rect(fitz.Rect(x, top, x + 14, 600), color=(0, 0, 0))

            doc.save(pdf_path)
            doc.close()

            workspace = root / "workspace"
            ingest = subprocess.run(
                [sys.executable, str(repo / "scripts" / "ingest_pdf.py"), str(pdf_path), "--workspace", str(workspace)],
                capture_output=True, text=True,
            )
            self.assertEqual(ingest.returncode, 0, ingest.stdout + ingest.stderr)

            manifest = json.loads((workspace / "state" / "state_manifest.json").read_text(encoding="utf-8"))
            pages = manifest["pages"]
            self.assertEqual(len(pages), 3)
            self.assertGreater(pages[0]["embedded_image_count"], 0)
            self.assertGreaterEqual(pages[0]["drawing_count"], 100)
            self.assertTrue(pages[0]["vector_or_text_figure_review"])
            self.assertEqual(pages[0]["vector_review_reason"], "dense_vector_figure_cluster")
            self.assertFalse(pages[1]["vector_or_text_figure_review"])
            self.assertIsNone(pages[1]["vector_review_reason"])
            self.assertTrue(pages[2]["vector_or_text_figure_review"])
            self.assertEqual(pages[2]["vector_review_reason"], "moderate_rectangular_plot_cluster")

    def test_ingest_extract_panel_registration_and_repeat_ids(self):
        try:
            import fitz
            from PIL import Image
        except ImportError:
            self.skipTest("PyMuPDF and Pillow are required for PDF integration test")

        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image_path = root / "chart.png"
            Image.new("RGB", (480, 320), "white").save(image_path)
            pdf_path = root / "tiny.pdf"
            doc = fitz.open()
            page = doc.new_page(width=600, height=800)
            page.insert_text((40, 40), "Synthetic ERA test report")
            page.insert_image(fitz.Rect(50, 100, 550, 500), filename=str(image_path))
            doc.save(pdf_path)
            doc.close()

            workspace = root / "workspace"
            ingest = subprocess.run(
                [sys.executable, str(repo / "scripts" / "ingest_pdf.py"), str(pdf_path), "--workspace", str(workspace)],
                capture_output=True, text=True,
            )
            self.assertEqual(ingest.returncode, 0, ingest.stdout + ingest.stderr)

            for _ in range(2):
                extract = subprocess.run(
                    [sys.executable, str(repo / "scripts" / "extract_regions.py"), "--workspace", str(workspace)],
                    capture_output=True, text=True,
                )
                self.assertEqual(extract.returncode, 0, extract.stdout + extract.stderr)

            bundle_path = workspace / "state" / "evidence_bundle.json"
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(len(bundle["regions"]), 1)
            region = next(iter(bundle["regions"].values()))
            self.assertEqual(region["region_id"], "REG001")
            self.assertTrue((workspace / region["image_path"]).is_file())

            panel_spec = root / "panel_layout.json"
            panel_spec.write_text(json.dumps({
                "parent_region_id": "REG001",
                "panels": [{"label": "a", "bbox_relative": [0.0, 0.0, 0.5, 1.0], "quantitative": False}]
            }), encoding="utf-8")
            panel_command = [
                sys.executable, str(repo / "scripts" / "segment_panels.py"),
                "--workspace", str(workspace), "--spec", str(panel_spec)
            ]
            for _ in range(2):
                panel_run = subprocess.run(panel_command, capture_output=True, text=True)
                self.assertEqual(panel_run.returncode, 0, panel_run.stdout + panel_run.stderr)
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(len(bundle["panels"]), 1)
            panel = next(iter(bundle["panels"].values()))
            self.assertEqual(panel["panel_id"], "PANEL001")
            self.assertTrue((workspace / panel["image_path"]).is_file())

            reserve_command = [
                sys.executable, str(repo / "scripts" / "assign_entity_ids.py"),
                "--workspace", str(workspace), "result-slot",
                "--parent-region-id", "REG001", "--slot-index", "1"
            ]
            first = subprocess.run(reserve_command, capture_output=True, text=True)
            second = subprocess.run(reserve_command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(json.loads(first.stdout)["entity_id"], json.loads(second.stdout)["entity_id"])

            validate = subprocess.run(
                [sys.executable, str(repo / "scripts" / "validate_evidence.py"), "--workspace", str(workspace)],
                capture_output=True, text=True,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)


if __name__ == "__main__":
    unittest.main()
