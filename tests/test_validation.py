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
        "findings": {}, "audit_records": [], "discrepancies": []
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


if __name__ == "__main__":
    unittest.main()
