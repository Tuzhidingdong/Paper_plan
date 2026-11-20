from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compile_prompt_context import compile_context
from prepare_spectral_comparison import build_payload, discover_groups
from record_spectral_comparison import register_comparison, validate_record


def sample_bundle():
    return {
        "source": {"file_name": "spectra.pdf", "sha256": "a" * 64, "page_count": 3},
        "regions": {
            "REG001": {"region_id": "REG001", "page_number": 1, "image_path": "assets/ftir.png", "pixel_sha256": "b" * 64},
            "REG002": {"region_id": "REG002", "page_number": 2, "image_path": "assets/raman.png", "pixel_sha256": "c" * 64},
        },
        "panels": {
            "PANEL001": {"panel_id": "PANEL001", "parent_region_id": "REG001", "label": "a",
                         "image_path": "assets/ftir_a.png", "pixel_sha256": "d" * 64},
        },
        "samples": {
            "S001": {"sample_id": "S001", "aliases": [{"alias": "Sample A", "source_ref": "p1"}],
                     "identity_status": "CONFIRMED"},
            "S002": {"sample_id": "S002", "aliases": [{"alias": "Sample B", "source_ref": "p1"}],
                     "identity_status": "CONFIRMED"},
        },
        "result_units": {
            "R001": {
                "result_id": "R001", "region_ids": ["REG001"], "panel_ids": ["PANEL001"],
                "data_type": "FTIR spectrum", "data_origin": "Visual_Estimate",
                "visual_legibility": "High", "quantitative_permission": "Trend_Only",
                "epistemic_status": "Observed",
                "measurement_context": {"technique": "FTIR", "measurement_group": "same_batch",
                    "measurement_conditions": {"mode": "ATR"},
                    "sample_associations": [
                        {"sample_id": "S001", "mapping_status": "CONFIRMED", "series_id": "A"},
                        {"sample_id": "S002", "mapping_status": "CONFIRMED", "series_id": "B"},
                    ]},
                "observations": [],
            },
            "R002": {
                "result_id": "R002", "region_ids": ["REG002"], "data_type": "Raman",
                "data_origin": "Qualitative_Observation", "visual_legibility": "Medium",
                "quantitative_permission": "Qualitative_Only", "epistemic_status": "Observed",
                "measurement_context": {"technique": "Raman", "measurement_group": "different_run",
                    "sample_associations": [{"sample_id": "S001", "mapping_status": "CONFIRMED"}]},
                "observations": [],
            },
        },
        "findings": {}, "audit_records": [], "visual_inspections": {},
        "spectral_comparisons": {},
    }


def comparison_record(request, status="COMPLETE"):
    return {
        "comparison_id": request["comparison_id"], "comparison_mode": "SPECTRAL_CROSS_SAMPLE",
        "result_ids": request["result_ids"], "technique": request["technique"],
        "comparison_status": status,
        "summary": "The two visible traces show a relative shift in one band.",
        "comparability_assessment": {
            "status": "PARTIALLY_COMPARABLE",
            "assessed_dimensions": [{"dimension": "normalization", "status": "UNKNOWN", "note": "not stated"}],
            "conclusion": "ATR mode is shared, but normalization basis is not documented.",
        },
        "direct_observations": [{
            "description": "A labelled band shifts to lower wavenumber in Sample B.",
            "result_ids": request["result_ids"], "source_status": "Observed"
        }],
        "band_comparisons": [{
            "change_type": "SHIFT", "observed_change": "Approximate lower-wavenumber shift.",
            "result_ids": request["result_ids"], "position_comparison": "Approximate visual range only.",
            "relative_signal_comparison": "Not assessed.", "signal_basis": "unavailable",
            "evidence_refs": [{"result_id": rid} for rid in request["result_ids"]]
        }],
        "functional_group_interpretations": [{
            "assignment": "Candidate functional-group change",
            "supporting_feature_ids": ["band-1"], "epistemic_status": "Hypothesized",
            "rationale": "The assignment is tentative because normalization is undocumented.",
            "confidence": "Low", "alternatives": ["Band overlap or baseline effect"]
        }],
        "limitations": ["Peak positions are visual estimates, not raw-data fits."],
    }


class TestSpectralComparison(unittest.TestCase):
    def test_discover_groups_separates_technique_and_measurement_group(self):
        groups = discover_groups(sample_bundle())
        self.assertEqual(
            {(technique, group) for technique, group, _, _ in groups},
            {("FTIR", "same_batch"), ("Raman", "different_run")},
        )

    def test_joint_payload_includes_image_sample_map_and_page_provenance(self):
        payload = build_payload(sample_bundle(), Path("."), ["R001"])
        self.assertEqual(payload["technique"], "FTIR")
        self.assertEqual(payload["comparison_mode"], "SPECTRAL_CROSS_SAMPLE")
        self.assertEqual(payload["task_status"], "READY_FOR_JOINT_VISUAL_REVIEW")
        self.assertEqual(payload["images"][0]["crop_scope"], "PANEL")
        self.assertEqual(payload["results"][0]["page_numbers"], [1])
        self.assertEqual(
            {item["sample_id"] for item in payload["results"][0]["sample_associations"]},
            {"S001", "S002"},
        )
        self.assertTrue(any("ONE joint comparison set" in item for item in payload["instructions"]))
        band_template = payload["required_output"]["band_comparisons"][0]
        self.assertIn("position_estimates", band_template)
        self.assertIn("peak_shift_cm1_approx", band_template)
        self.assertIn("uncertainty_cm1_approx", band_template["position_estimates"][0])

    def test_mixed_techniques_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "only one spectral technique"):
            build_payload(sample_bundle(), Path("."), ["R001", "R002"])

    def test_recorder_rejects_missing_direct_observations(self):
        bundle = sample_bundle()
        request = build_payload(bundle, Path("."), ["R001"])
        record = comparison_record(request)
        record["direct_observations"] = []
        with self.assertRaisesRegex(ValueError, "requires direct_observations"):
            validate_record(bundle, request, record)

    def test_registered_comparison_is_compiled_with_limitations(self):
        bundle = sample_bundle()
        request = build_payload(bundle, Path("."), ["R001"])
        register_comparison(bundle, request, comparison_record(request, "PARTIAL"))
        self.assertIn(request["comparison_id"], bundle["spectral_comparisons"])
        context = compile_context(bundle)
        self.assertIn("Raman / FTIR cross-sample comparisons", context)
        self.assertIn("relative shift in one band", context)
        self.assertIn("normalization basis is not documented", context)
        self.assertIn("Peak positions are visual estimates", context)
        self.assertIn("not yet included in a recorded comparison: R002", context)

    def test_context_compiler_warns_when_spectral_comparison_is_missing(self):
        context = compile_context(sample_bundle())
        self.assertIn("Signal-level analysis is part of the general scientific-analysis record.", context)
        self.assertIn("signal_features and signal_comparisons", context)
        self.assertIn("R001", context)


if __name__ == "__main__":
    unittest.main()
