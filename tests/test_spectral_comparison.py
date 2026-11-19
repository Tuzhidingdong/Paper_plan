from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from prepare_spectral_comparison import build_comparison_tasks, classify_spectral_modality
from record_spectral_comparison import register_comparison, validate_comparison
from compile_prompt_context import compile_context


def make_card(plot_type="Raman spectrum"):
    return {
        "plot_type": plot_type,
        "axes": {"x": {"label": "Wavenumber", "unit": "cm-1"},
                 "y": {"label": "Intensity", "unit": "a.u."}},
        "legend_series": [],
        "instrument_checklist": {},
        "observations": [{"description": "visual trace", "source_status": "Observed"}],
        "visual_legibility": "High", "data_origin": "Visual_Estimate",
        "quantitative_permission": "Trend_Only",
        "caption_text": "MUST NOT LEAK", "report_narrative": "MUST NOT LEAK"
    }


def make_bundle():
    return {
        "source": {"file_name": "synthetic.pdf", "sha256": "a" * 64},
        "regions": {
            "REG001": {"region_id": "REG001", "page_number": 1, "image_path": "r1.png", "pixel_sha256": "1" * 64},
            "REG002": {"region_id": "REG002", "page_number": 2, "image_path": "r2.png", "pixel_sha256": "2" * 64},
        },
        "panels": {},
        "samples": {
            "S001": {"sample_id": "S001", "aliases": [{"alias": "initial"}], "identity_status": "CONFIRMED"},
            "S002": {"sample_id": "S002", "aliases": [{"alias": "treated"}], "identity_status": "CONFIRMED"},
        },
        "result_units": {
            "R001": {"result_id": "R001", "region_ids": ["REG001"], "data_type": "Raman spectrum",
                    "data_origin": "Visual_Estimate", "visual_legibility": "High", "quantitative_permission": "Trend_Only",
                    "measurement_context": {"technique": "Raman", "measurement_group": "series-A",
                       "measurement_conditions": {"time_min": 0},
                       "sample_associations": [{"sample_id": "S001", "mapping_status": "CONFIRMED"}]}, "observations": []},
            "R002": {"result_id": "R002", "region_ids": ["REG002"], "data_type": "Raman spectrum",
                    "data_origin": "Visual_Estimate", "visual_legibility": "High", "quantitative_permission": "Trend_Only",
                    "measurement_context": {"technique": "Raman", "measurement_group": "series-B",
                       "measurement_conditions": {"time_min": 30},
                       "sample_associations": [{"sample_id": "S002", "mapping_status": "CONFIRMED"}]}, "observations": []},
        },
        "visual_inspections": {"REG001": {"initial": make_card()}, "REG002": {"initial": make_card()}},
        "findings": {}
    }


def make_record(task):
    units = [x["unit_id"] for x in task["comparison_units"]]
    return {
        "task_id": task["task_id"], "comparison_status": "CONDITIONALLY_COMPARABLE",
        "compared_units": units,
        "comparability_dimensions": {
            "spectral_modality_and_acquisition_mode": {"status": "MATCHED", "reason": "Same modality"},
            "spectral_range_and_x_axis_unit": {"status": "MATCHED", "reason": "Same unit"},
            "intensity_or_transmittance_basis": {"status": "MATCHED", "reason": "Same displayed basis"},
            "baseline_and_normalization": {"status": "UNKNOWN", "reason": "Not reported"},
            "instrument_and_acquisition_conditions": {"status": "UNKNOWN", "reason": "Not reported"},
            "sample_state_and_preparation": {"status": "UNKNOWN", "reason": "Not reported"},
            "timepoint_or_treatment_condition": {"status": "MATCHED", "reason": "Recorded times differ as intended"},
            "plot_scaling_offsets_and_stacking": {"status": "UNKNOWN", "reason": "Not reported"}
        },
        "band_comparisons": [{
            "band_id": "B1", "unit_ids": units, "observed_difference": "Broad band appears weaker in unit 2",
            "peak_position_estimates_cm1": [
                {"unit_id": units[0], "range": [3440, 3460], "confidence": "Medium"},
                {"unit_id": units[1], "range": [3440, 3460], "confidence": "Medium"}],
            "shift_direction": "NO_CLEAR_SHIFT", "shift_magnitude_cm1_range": [0, 10],
            "relative_intensity_trend": "DECREASED", "relative_peak_area_trend": "NOT_ASSESSABLE",
            "band_presence_change": "PRESENT_IN_ALL", "assignment_candidates": [],
            "epistemic_status": "Observed", "alternative_explanations": ["Baseline changes"]
        }],
        "overall_synthesis": "Visual weakening only; absolute intensity is not established.",
        "cross_validation_targets": ["Independent chemical or physical measurement"],
        "uncertainty_note": "Visual comparison only; no curve digitization was performed."
    }


class SpectralComparisonTests(unittest.TestCase):
    def test_modality_classification(self):
        self.assertEqual(classify_spectral_modality("in situ Raman"), "RAMAN")
        self.assertEqual(classify_spectral_modality("DRIFTS spectrum"), "DRIFTS")
        self.assertEqual(classify_spectral_modality("FTIR"), "FTIR")
        self.assertIsNone(classify_spectral_modality("XRD pattern"))

    def test_joint_task_across_different_measurement_groups_and_no_caption_leak(self):
        task = build_comparison_tasks(make_bundle())[0]
        self.assertEqual(task["modality"], "RAMAN")
        self.assertEqual(len(task["comparison_units"]), 2)
        self.assertEqual({x["measurement_group"] for x in task["comparison_units"]}, {"series-A", "series-B"})
        for asset in task["assets"]:
            self.assertIsNone(asset["visual_inspection"]["caption_text"])
            self.assertFalse(asset["visual_inspection"]["report_narrative_included"])

    def test_one_panel_two_legend_series_becomes_two_units(self):
        bundle = make_bundle()
        bundle["result_units"] = {"R001": bundle["result_units"]["R001"]}
        bundle["result_units"]["R001"]["measurement_context"]["sample_associations"] = []
        bundle["visual_inspections"]["REG001"]["initial"]["legend_series"] = [{"label": "A"}, {"label": "B"}]
        task = build_comparison_tasks(bundle)[0]
        self.assertEqual(len(task["comparison_units"]), 2)
        self.assertEqual(len(task["assets"]), 1)

    def test_single_spectrum_does_not_create_task(self):
        bundle = make_bundle()
        bundle["result_units"].pop("R002")
        self.assertEqual(build_comparison_tasks(bundle), [])

    def test_raman_and_drifts_are_not_merged(self):
        bundle = make_bundle()
        bundle["result_units"]["R002"]["measurement_context"]["technique"] = "DRIFTS"
        bundle["result_units"]["R002"]["data_type"] = "DRIFTS spectrum"
        bundle["visual_inspections"]["REG002"]["initial"] = make_card("DRIFTS spectrum")
        self.assertEqual(build_comparison_tasks(bundle), [])

    def test_record_is_traceable_and_unknown_dimensions_block_comparable(self):
        task = build_comparison_tasks(make_bundle())[0]
        record = make_record(task)
        validate_comparison(task, record)
        saved = register_comparison(make_bundle(), task, record)
        self.assertIn(task["task_id"], saved["task_id"])
        record["comparison_status"] = "COMPARABLE"
        with self.assertRaisesRegex(ValueError, "COMPARABLE requires"):
            validate_comparison(task, record)

    def test_rejects_unlinked_unit_and_exact_point_without_range(self):
        task = build_comparison_tasks(make_bundle())[0]
        record = make_record(task)
        record["compared_units"] = [record["compared_units"][0], "NOT_IN_TASK"]
        with self.assertRaisesRegex(ValueError, "task-pack units"):
            validate_comparison(task, record)
        record = make_record(task)
        record["band_comparisons"][0]["peak_position_estimates_cm1"][0]["range"] = None
        with self.assertRaisesRegex(ValueError, "must use ranges"):
            validate_comparison(task, record)

    def test_context_contains_comparison_findings_and_boundaries(self):
        task = build_comparison_tasks(make_bundle())[0]
        bundle = make_bundle()
        bundle["spectral_comparisons"] = {task["task_id"]: {
            **make_record(task), "modality": "RAMAN", "source_entities": ["REG001", "REG002"],
            "source_result_ids": ["R001", "R002"],
            "compared_unit_context": [{"unit_id": "R001", "samples": [{"label": "initial", "sample_id": "S001"}],
                                       "condition_summary": {"time_min": 0}, "quantitative_permission": "Trend_Only"}]
        }}
        context = compile_context(bundle)
        self.assertIn("Cross-sample Raman / IR comparisons", context)
        self.assertIn("Broad band appears weaker", context)
        self.assertIn("no curve digitization", context.lower())


if __name__ == "__main__":
    unittest.main()
