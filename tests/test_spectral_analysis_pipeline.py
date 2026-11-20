from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fitz
from era_core import atomic_write_json, ensure_workspace_dirs, sha256_file, workspace_paths
from extract_regions import extract_vector_figure_candidates
from ingest_pdf import assess_vector_figure_review
from record_figure_triage import record_figure_triage
from record_scientific_analysis import validate_record
from validate_evidence import validate, validate_figure_candidate_coverage


def _rect(x0, y0, x1, y1):
    return SimpleNamespace(x0=x0, y0=y0, x1=x1, y1=y1)


def _dense_plot_drawings(page_width=800.0, page_height=1000.0):
    drawings = []
    # Six adjacent grid cells provide a compact, connected plot cluster.
    for gx, gy in ((2, 2), (3, 2), (4, 2), (2, 3), (3, 3), (4, 3)):
        cx = (gx + 0.5) / 8.0 * page_width
        cy = (gy + 0.5) / 6.0 * page_height
        for index in range(10):
            x = cx + index * 0.15
            y = cy + index * 0.12
            drawings.append({
                "rect": _rect(x, y, x + 3, y + 3),
                "items": [("l",), ("l",)],
            })
    return drawings


class TestVectorFigureCoverage(unittest.TestCase):
    def test_ingest_detector_retains_crop_bbox_for_dense_vector_plot(self):
        review = assess_vector_figure_review(
            _dense_plot_drawings(),
            _rect(0, 0, 800, 1000),
        )
        self.assertTrue(review["vector_or_text_figure_review"])
        self.assertGreaterEqual(len(review["vector_figure_candidates"]), 1)
        candidate = review["vector_figure_candidates"][0]
        self.assertEqual(len(candidate["bbox_pdf"]), 4)
        self.assertEqual(len(candidate["bbox_normalized"]), 4)
        self.assertGreater(candidate["drawing_count"], 50)
        repeated = assess_vector_figure_review(
            _dense_plot_drawings(),
            _rect(0, 0, 800, 1000),
        )
        self.assertEqual(review["vector_figure_candidates"], repeated["vector_figure_candidates"])

    def test_vector_candidate_is_rasterized_without_manual_regions_json(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            paths = ensure_workspace_dirs(workspace)
            source = workspace / "source" / "original_report.pdf"
            doc = fitz.open()
            page = doc.new_page(width=600, height=800)
            # Build a dense vector-only plot with six connected spatial clusters.
            for gx, gy in ((2, 2), (3, 2), (4, 2), (2, 3), (3, 3), (4, 3)):
                x0 = 70 + gx * 48
                y0 = 150 + gy * 34
                for index in range(12):
                    x = x0 + index * 0.9
                    y = y0 + index * 0.7
                    page.draw_line((x, y), (x + 12, y + 8), color=(0, 0, 0), width=0.6)
            page.insert_text((80, 90), "Vector plot with axes and labels", fontsize=10)
            doc.save(source)
            doc.close()

            source_hash = sha256_file(source)
            manifest = {
                "pages": [{
                    "page_number": 1,
                    "vector_or_text_figure_review": True,
                    "vector_figure_candidates": [{
                        "candidate_index": 1,
                        "bbox_pdf": [80, 120, 360, 280],
                        "bbox_normalized": [0.13, 0.15, 0.6, 0.35],
                        "reason": "synthetic_vector_plot"
                    }]
                }]
            }
            bundle = {"source": {"sha256": source_hash}, "regions": {}, "figure_candidates": {}}
            atomic_write_json(paths["manifest"], manifest)
            document = fitz.open(source)
            count = extract_vector_figure_candidates(document, manifest, workspace, bundle, 300)
            document.close()

            self.assertEqual(count, 1)
            candidate = bundle["figure_candidates"]["VFIG-P0001-01"]
            self.assertEqual(candidate["extraction_status"], "EXTRACTED")
            self.assertEqual(candidate["triage_status"], "PENDING_TRIAGE")
            self.assertTrue((workspace / candidate["image_path"]).is_file())
            self.assertEqual(candidate["asset_sha256"], sha256_file(workspace / candidate["image_path"]))
            self.assertIn(candidate["region_id"], bundle["regions"])

    def test_pending_candidate_blocks_evidence_validation_until_explicit_exclusion(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            paths = ensure_workspace_dirs(workspace)
            image = workspace / "extracted" / "regions" / "REG001.png"
            image.parent.mkdir(parents=True, exist_ok=True)
            image.write_bytes(b"synthetic-image")
            atomic_write_json(paths["manifest"], {
                "pages": [{
                    "page_number": 1,
                    "vector_or_text_figure_review": True,
                    "vector_figure_candidates": [{"candidate_index": 1}]
                }]
            })
            bundle = {
                "regions": {
                    "REG001": {
                        "region_id": "REG001", "page_number": 1,
                        "image_path": "extracted/regions/REG001.png",
                        "pixel_sha256": "a" * 64
                    }
                },
                "figure_candidates": {
                    "VFIG-P0001-01": {
                        "candidate_id": "VFIG-P0001-01",
                        "page_number": 1, "region_id": "REG001",
                        "image_path": "extracted/regions/REG001.png",
                        "pixel_sha256": "a" * 64,
                        "extraction_status": "EXTRACTED",
                        "triage_status": "PENDING_TRIAGE",
                        "result_ids": []
                    }
                },
                "result_units": {}, "panels": {}
            }
            errors, _ = validate_figure_candidate_coverage(bundle, workspace)
            self.assertTrue(any("disposition is missing" in item for item in errors))

            record_figure_triage(bundle, [{
                "candidate_id": "VFIG-P0001-01",
                "disposition": "EXCLUDE_NOT_SCIENTIFIC_FIGURE",
                "reason": "Synthetic fixture candidate is a decorative line cluster."
            }])
            errors, warnings = validate_figure_candidate_coverage(bundle, workspace)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_included_candidate_must_link_to_a_result_unit(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            paths = ensure_workspace_dirs(workspace)
            image = workspace / "regions" / "REG001.png"
            image.parent.mkdir(parents=True, exist_ok=True)
            image.write_bytes(b"synthetic-image")
            atomic_write_json(paths["manifest"], {
                "pages": [{
                    "page_number": 1,
                    "vector_or_text_figure_review": True,
                    "vector_figure_candidates": [{"candidate_index": 1}]
                }]
            })
            bundle = {
                "regions": {"REG001": {"page_number": 1, "image_path": "regions/REG001.png", "pixel_sha256": "a" * 64}},
                "panels": {},
                "result_units": {"R001": {"region_ids": ["REG001"], "panel_ids": []}},
                "figure_candidates": {
                    "VFIG-P0001-01": {
                        "candidate_id": "VFIG-P0001-01", "page_number": 1, "region_id": "REG001",
                        "image_path": "regions/REG001.png", "pixel_sha256": "a" * 64,
                        "extraction_status": "EXTRACTED", "triage_status": "PENDING_TRIAGE", "result_ids": []
                    }
                }
            }
            record_figure_triage(bundle, [{
                "candidate_id": "VFIG-P0001-01",
                "disposition": "INCLUDE_AS_SCIENTIFIC_FIGURE",
                "result_ids": ["R001"],
                "reason": "Scientific plot linked to its Result Unit."
            }])
            errors, _ = validate_figure_candidate_coverage(bundle, workspace)
            self.assertEqual(errors, [])


def _analysis_fixture(workspace: Path):
    image_a = workspace / "assets" / "a.png"
    image_b = workspace / "assets" / "b.png"
    image_a.parent.mkdir(parents=True, exist_ok=True)
    image_a.write_bytes(b"image-a")
    image_b.write_bytes(b"image-b")
    source_hash = "f" * 64
    bundle = {
        "source": {"file_name": "source.pdf", "sha256": source_hash, "page_count": 2},
        "result_units": {
            "R001": {"result_id": "R001", "region_ids": ["REG001"], "panel_ids": [], "observations": []},
            "R002": {"result_id": "R002", "region_ids": ["REG002"], "panel_ids": [], "observations": []}
        },
        "regions": {
            "REG001": {"page_number": 1, "image_path": "assets/a.png"},
            "REG002": {"page_number": 2, "image_path": "assets/b.png"}
        },
        "panels": {}
    }
    request = {
        "analysis_id": "SANA-0123456789abcdef",
        "analysis_mode": "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS",
        "source": {"sha256": source_hash},
        "result_ids": ["R001", "R002"],
        "invocation_audit_required": True,
        "assets": [
            {"image_path": "assets/a.png", "asset_exists": True, "asset_sha256": sha256_file(image_a), "region_id": "REG001", "panel_id": None},
            {"image_path": "assets/b.png", "asset_exists": True, "asset_sha256": sha256_file(image_b), "region_id": "REG002", "panel_id": None}
        ]
    }
    request_log = workspace / "logs" / "request.json"
    response_log = workspace / "logs" / "response.json"
    request_log.parent.mkdir(parents=True, exist_ok=True)
    request_log.write_text(json.dumps({"attachments": ["image-a", "image-b"]}), encoding="utf-8")
    response_log.write_text(json.dumps({"response": "synthetic"}), encoding="utf-8")
    record = {
        "analysis_id": request["analysis_id"],
        "analysis_mode": "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS",
        "analysis_status": "COMPLETE",
        "result_ids": ["R001", "R002"],
        "summary": "Synthetic signal feature comparison.",
        "coverage": [
            {"result_id": "R001", "status": "ANALYZED", "observation_ids": ["OBS-1"], "reason": ""},
            {"result_id": "R002", "status": "ANALYZED", "observation_ids": ["OBS-2"], "reason": ""}
        ],
        "observations": [
            {"observation_id": "OBS-1", "description": "Signal feature one.", "epistemic_status": "Observed",
             "result_ids": ["R001"], "evidence_refs": [{"result_id": "R001", "region_id": "REG001", "panel_id": None, "page_number": 1}], "confidence": "Medium"},
            {"observation_id": "OBS-2", "description": "Signal feature two.", "epistemic_status": "Observed",
             "result_ids": ["R002"], "evidence_refs": [{"result_id": "R002", "region_id": "REG002", "panel_id": None, "page_number": 2}], "confidence": "Medium"}
        ],
        "comparisons": [],
        "relationships": [],
        "interpretations": [],
        "contradictions": [],
        "signal_analysis_coverage": [
            {"result_id": "R001", "status": "APPLICABLE", "feature_ids": ["SIG-1"], "comparison_ids": ["SIGCMP-1"], "reason": ""},
            {"result_id": "R002", "status": "APPLICABLE", "feature_ids": ["SIG-2"], "comparison_ids": ["SIGCMP-1"], "reason": ""}
        ],
        "signal_features": [
            {"feature_id": "SIG-1", "result_id": "R001", "series_id": "A", "feature_type": "BAND", "description": "A visible signal band.",
             "series_label": "Trace A",
             "axis_context": {"x_axis_label": "Wavenumber", "x_axis_unit": "cm-1", "x_axis_scale": "LINEAR",
                              "y_axis_label": "Absorbance", "y_axis_unit": "a.u.", "y_axis_scale": "LINEAR",
                              "normalization_basis": "un-normalized display"},
             "position": {"value": 1000.0, "unit": "cm-1", "reading_basis": "visual axis estimate", "precision_or_uncertainty": "±5 cm-1"},
             "evidence_refs": [{"result_id": "R001", "region_id": "REG001", "panel_id": None, "page_number": 1}]},
            {"feature_id": "SIG-2", "result_id": "R002", "series_id": "B", "feature_type": "BAND", "description": "A shifted visible signal band.",
             "series_label": "Trace B",
             "axis_context": {"x_axis_label": "Wavenumber", "x_axis_unit": "cm-1", "x_axis_scale": "LINEAR",
                              "y_axis_label": "Absorbance", "y_axis_unit": "a.u.", "y_axis_scale": "LINEAR",
                              "normalization_basis": "un-normalized display"},
             "position": {"value": 1010.0, "unit": "cm-1", "reading_basis": "visual axis estimate", "precision_or_uncertainty": "±5 cm-1"},
             "evidence_refs": [{"result_id": "R002", "region_id": "REG002", "panel_id": None, "page_number": 2}]}
        ],
        "signal_comparisons": [
            {"comparison_id": "SIGCMP-1", "feature_ids": ["SIG-1", "SIG-2"], "result_ids": ["R001", "R002"],
             "change_type": "POSITION_SHIFT", "description": "A visible position shift between the two plotted features.",
             "direction_or_pattern": "higher", "comparability_status": "PARTIALLY_COMPARABLE",
             "normalization_basis": "same displayed axis units",
             "quantified_change": {"metric": "position shift", "value": 10.0, "unit": "cm-1", "source_basis": "visual axis estimate", "precision_or_uncertainty": "approx. ±7 cm-1"},
             "evidence_refs": [
                 {"result_id": "R001", "region_id": "REG001", "panel_id": None, "page_number": 1},
                 {"result_id": "R002", "region_id": "REG002", "panel_id": None, "page_number": 2}
             ],
             "interpretation_limits": ["Synthetic visual estimate."]}
        ],
        "model_invocation": {
            "invocation_id": "test-call-1", "status": "RESPONSE_RECEIVED", "model_id": "synthetic-model",
            "input_mode": "NATIVE_IMAGE_ATTACHMENTS", "evidence_level": "AGENT_REPORTED_RUNTIME_RECEIPT",
            "attached_assets": [
                {"image_path": "assets/a.png", "asset_sha256": sha256_file(image_a), "attachment_type": "NATIVE_IMAGE", "attachment_reference": "attachment-a"},
                {"image_path": "assets/b.png", "asset_sha256": sha256_file(image_b), "attachment_type": "NATIVE_IMAGE", "attachment_reference": "attachment-b"}
            ],
            "request_log_path": "logs/request.json", "request_log_sha256": sha256_file(request_log),
            "response_log_path": "logs/response.json", "response_log_sha256": sha256_file(response_log),
            "limitations": ["Synthetic invocation."]
        }
    }
    return bundle, request, record


class TestSignalFeatureAndInvocationAudit(unittest.TestCase):
    def test_valid_signal_features_and_native_image_invocation_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            bundle, request, record = _analysis_fixture(workspace)
            validate_record(bundle, request, record, workspace)

    def test_text_only_paths_cannot_claim_an_image_derived_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            bundle, request, record = _analysis_fixture(workspace)
            record["model_invocation"]["input_mode"] = "TEXT_ONLY_PATHS"
            with self.assertRaisesRegex(ValueError, "native image attachments"):
                validate_record(bundle, request, record, workspace)

    def test_missing_signal_evidence_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            bundle, request, record = _analysis_fixture(workspace)
            record["signal_features"][0]["evidence_refs"] = []
            with self.assertRaisesRegex(ValueError, "must cite at least one source evidence reference"):
                validate_record(bundle, request, record, workspace)

    def test_invocation_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            bundle, request, record = _analysis_fixture(workspace)
            record["model_invocation"]["request_log_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "does not match"):
                validate_record(bundle, request, record, workspace)

    def test_every_result_requires_signal_applicability_disposition(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            bundle, request, record = _analysis_fixture(workspace)
            del record["signal_analysis_coverage"]
            with self.assertRaisesRegex(ValueError, "signal_analysis_coverage must explicitly"):
                validate_record(bundle, request, record, workspace)

    def test_applicable_signal_result_requires_a_feature_record(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            bundle, request, record = _analysis_fixture(workspace)
            record["signal_analysis_coverage"][0]["feature_ids"] = []
            with self.assertRaisesRegex(ValueError, "APPLICABLE signal coverage requires"):
                validate_record(bundle, request, record, workspace)

    def test_signal_comparison_must_link_multiple_features(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            bundle, request, record = _analysis_fixture(workspace)
            record["signal_comparisons"][0]["feature_ids"] = ["SIG-1"]
            with self.assertRaisesRegex(ValueError, "at least two recorded signal features"):
                validate_record(bundle, request, record, workspace)

    def test_evidence_validator_handles_general_and_signal_coverage_maps(self):
        bundle = {
            "source": {"file_name": "source.pdf", "sha256": "f" * 64, "page_count": 1},
            "regions": {
                "REG001": {
                    "region_id": "REG001",
                    "page_number": 1,
                    "bbox_normalized": [0.1, 0.1, 0.9, 0.9],
                    "image_path": "regions/REG001.png",
                }
            },
            "panels": {},
            "samples": {},
            "result_units": {
                "R001": {
                    "result_id": "R001",
                    "region_ids": ["REG001"],
                    "panel_ids": [],
                    "data_origin": "Exact_Table",
                    "visual_legibility": "High",
                    "quantitative_permission": "Trend_Only",
                    "epistemic_status": "Observed",
                    "is_visual_estimate": False,
                    "measurement_context": {},
                    "observations": [],
                }
            },
            "findings": {},
            "audit_records": [],
            "scientific_analyses": {
                "SANA-TEST": {
                    "analysis_id": "SANA-TEST",
                    "analysis_mode": "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS",
                    "analysis_status": "PARTIAL",
                    "result_ids": ["R001"],
                    "coverage": [{
                        "result_id": "R001",
                        "status": "NOT_ASSESSABLE",
                        "observation_ids": [],
                        "reason": "Synthetic fixture isolates validator coverage-map behavior.",
                    }],
                    "invocation_audit_required": True,
                    "signal_analysis_coverage": [{
                        "result_id": "R001",
                        "status": "NOT_ASSESSABLE",
                        "feature_ids": [],
                        "comparison_ids": [],
                        "reason": "Synthetic fixture contains no resolvable signal image.",
                    }],
                    "signal_features": [],
                    "signal_comparisons": [],
                }
            },
        }
        errors, warnings = validate(bundle)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
