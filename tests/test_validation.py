from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_evidence import validate as validate_evidence
from validate_samples import validate as validate_samples


def sample_bundle():
    return {
        "schema_version": 1,
        "workspace_revision": "0.1.0",
        "source": {"file_name": "report.pdf", "sha256": "a" * 64, "page_count": 2},
        "regions": {
            "REG001": {
                "region_id": "REG001", "anchor_key": "region-x", "page_number": 1,
                "bbox_normalized": [0.1, 0.1, 0.9, 0.9],
                "image_path": "extracted/regions/REG001.png", "pixel_sha256": "b" * 64,
                "region_type": "embedded_image_block", "triage_role": "REVIEW_CANDIDATE",
            }
        },
        "panels": {},
        "samples": {
            "S001": {
                "sample_id": "S001", "aliases": [{"alias": "Sample A", "source_ref": "P1"}],
                "prep_conditions": {}, "batch_note": None, "identity_status": "PROBABLE",
            }
        },
        "result_units": {
            "R001": {
                "result_id": "R001", "region_ids": ["REG001"], "panel_ids": [],
                "data_type": "XRD", "data_origin": "Visual_Estimate", "visual_legibility": "Medium",
                "is_visual_estimate": True, "quantitative_permission": "Trend_Only",
                "epistemic_status": "Observed",
                "measurement_context": {"sample_associations": [
                    {"sample_id": "S001", "mapping_status": "PROBABLE", "core_link": False}
                ]},
                "observations": [{
                    "description": "[Visual Estimate - Raw Data Required] Possible trend only",
                    "source_status": "Observed", "numeric_value": None, "unit": None,
                    "sample_id": "S001", "mapping_status": "PROBABLE", "data_origin": "Visual_Estimate"
                }],
                "instrument_checklist": {
                    "figure_status": {"scan_rate": {"status": "NOT_SHOWN"}},
                    "report_status": {"scan_rate": {"status": "UNCERTAIN"}}
                },
                "uncertainty_note": "[Visual Estimate - Raw Data Required]", "artifact_audit_ids": []
            }
        },
        "findings": {}, "audit_records": [], "discrepancies": [],
        "visual_inspections": {
            "REG001": {"initial": {
                "inspection_mode": "CAPTION_BLIND", "caption_text_included": False,
                "report_narrative_included": False, "visual_legibility": "Medium",
                "visual_metadata_assessment": {
                    "status": "RECORDED",
                    "assessment_note": "This synthetic plot fixture records visual metadata and explicitly marks microscopy-only dimensions not applicable.",
                    "dimensions": [
                        {"dimension": "imaging_modality", "status": "OBSERVED", "value": "2D plot image",
                         "source_location": "Original figure crop", "recording_method": "VISUAL_REVIEW", "confidence": "HIGH"},
                        {"dimension": "magnification_or_pixel_size", "status": "NOT_APPLICABLE", "reason": "The source is a plotted figure, not a micrograph.",
                         "recording_method": "OTHER", "confidence": "HIGH"},
                        {"dimension": "scale_bar_or_spatial_calibration", "status": "NOT_APPLICABLE", "reason": "The plotted axes define the data scale.",
                         "recording_method": "OTHER", "confidence": "HIGH"},
                        {"dimension": "specimen_state_and_preparation", "status": "NOT_APPLICABLE", "reason": "This visual record is a chart, not a specimen micrograph.",
                         "recording_method": "OTHER", "confidence": "HIGH"},
                        {"dimension": "image_processing_and_contrast", "status": "UNKNOWN", "reason": "The source does not document image processing.",
                         "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
                        {"dimension": "field_selection_and_sampling", "status": "NOT_APPLICABLE", "reason": "Field-of-view sampling does not apply to this chart.",
                         "recording_method": "OTHER", "confidence": "HIGH"}
                    ]
                }
            }, "reinspections": [], "locked": False}
        }
    }


class ValidationTests(unittest.TestCase):
    def test_low_resolution_exact_values_are_rejected(self):
        bundle = sample_bundle()
        result = bundle["result_units"]["R001"]
        result["visual_legibility"] = "Low"
        result["quantitative_permission"] = "Exact_Values"
        result["observations"][0]["numeric_value"] = 10.2
        errors, _ = validate_evidence(bundle)
        self.assertTrue(any("low/unassessable" in item for item in errors))
        self.assertTrue(any("numeric_value forbidden" in item for item in errors))

    def test_visual_estimate_requires_warning_marker(self):
        bundle = sample_bundle()
        result = bundle["result_units"]["R001"]
        result["uncertainty_note"] = "uncertain"
        result["observations"][0]["description"] = "Possible trend"
        errors, _ = validate_evidence(bundle)
        self.assertTrue(any("warning marker" in item for item in errors))

    def test_unknown_sample_reference_is_rejected(self):
        bundle = sample_bundle()
        bundle["result_units"]["R001"]["measurement_context"]["sample_associations"][0]["sample_id"] = "S999"
        errors, _ = validate_evidence(bundle)
        self.assertTrue(any("unknown sample S999" in item for item in errors))

    def test_micro_gate_only_triggers_for_core_unresolved_link(self):
        bundle = sample_bundle()
        errors, warnings, triggered = validate_samples(bundle)
        self.assertFalse(errors)
        self.assertFalse(triggered)
        bundle["result_units"]["R001"]["measurement_context"]["sample_associations"][0]["core_link"] = True
        errors, warnings, triggered = validate_samples(bundle)
        self.assertFalse(errors)
        self.assertTrue(triggered)

    def test_figure_not_shown_is_not_report_absent(self):
        bundle = sample_bundle()
        checklist = bundle["result_units"]["R001"]["instrument_checklist"]
        self.assertEqual(checklist["figure_status"]["scan_rate"]["status"], "NOT_SHOWN")
        self.assertEqual(checklist["report_status"]["scan_rate"]["status"], "UNCERTAIN")
        errors, _ = validate_evidence(bundle)
        self.assertFalse(errors)

    def test_core_numeric_result_requires_verified_measurement_definition(self):
        bundle = sample_bundle()
        result = bundle["result_units"]["R001"]
        result["claim_role"] = "CORE"
        result["quantitative_permission"] = "Exact_Values"
        result["observations"][0]["numeric_value"] = 12.5
        result["observations"][0]["unit"] = "unit-A"
        errors, warnings = validate_evidence(bundle)
        self.assertTrue(any("requires a measurement_definition" in item for item in errors))

    def test_verified_derived_metric_requires_formula_and_parent_result(self):
        bundle = sample_bundle()
        result = bundle["result_units"]["R001"]
        result["claim_role"] = "CORE"
        result["quantitative_permission"] = "Exact_Values"
        result["observations"][0]["numeric_value"] = 12.5
        result["measurement_definition"] = {
            "status": "VERIFIED", "measurand": "Target quantity",
            "raw_signal": "Instrument response", "method": "Defined method",
            "output_unit": "unit-A", "normalization_basis": "Per unit mass",
            "is_derived_metric": True, "formula": None, "parent_result_ids": [],
        }
        errors, warnings = validate_evidence(bundle)
        self.assertTrue(any("requires an explicit calculation formula" in item for item in errors))
        self.assertTrue(any("requires parent_result_ids" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
