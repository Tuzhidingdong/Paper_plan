from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scientific_quality_gates import (
    validate_evidence_integrity,
    validate_fit_reproducibility,
    validate_route_selection,
    validate_visual_claim_comparability,
)


class RegionIntegrityTests(unittest.TestCase):
    def make_bundle(self):
        return {
            "regions": {
                "REG001": {
                    "region_id": "REG001",
                    "page_number": 2,
                    "bbox_normalized": [0.1, 0.2, 0.9, 0.8],
                    "region_type": "embedded_image_block",
                    "triage_role": "REVIEW_CANDIDATE",
                }
            },
            "panels": {},
            "visual_inspections": {},
            "result_units": {
                "R001": {
                    "result_id": "R001",
                    "region_ids": ["REG001"],
                    "panel_ids": [],
                    "source_location": "PDF p.2 — microscopy image",
                    "data_origin": "Exact_Text",
                }
            },
        }

    def test_repeated_header_asset_cannot_anchor_a_result(self):
        bundle = self.make_bundle()
        bundle["regions"]["REG001"]["triage_role"] = "REPEATED_LAYOUT_ASSET"
        errors, _ = validate_evidence_integrity(bundle)
        self.assertTrue(any("repeated header/footer" in item for item in errors), errors)
        self.assertTrue(any("no usable linked Region" in item for item in errors), errors)

    def test_repeated_header_is_inferred_even_without_triage_label(self):
        bundle = self.make_bundle()
        bundle["regions"]["REG001"]["layout_fingerprint"] = "same-header"
        bundle["regions"]["REG001"]["bbox_normalized"] = [0.1, 0.02, 0.9, 0.10]
        bundle["regions"]["REG002"] = {
            "region_id": "REG002", "page_number": 1,
            "bbox_normalized": [0.1, 0.02, 0.9, 0.10],
            "region_type": "embedded_image_block",
            "triage_role": "REVIEW_CANDIDATE",
            "layout_fingerprint": "same-header",
        }
        bundle["regions"]["REG003"] = {
            "region_id": "REG003", "page_number": 3,
            "bbox_normalized": [0.1, 0.02, 0.9, 0.10],
            "region_type": "embedded_image_block",
            "triage_role": "REVIEW_CANDIDATE",
            "layout_fingerprint": "same-header",
        }
        bundle["source"] = {"page_count": 3}
        errors, _ = validate_evidence_integrity(bundle)
        self.assertTrue(any("repeated header/footer" in item for item in errors), errors)

    def test_source_page_must_match_linked_region_page(self):
        bundle = self.make_bundle()
        bundle["regions"]["REG001"]["page_number"] = 1
        errors, _ = validate_evidence_integrity(bundle)
        self.assertTrue(any("no usable linked Region is anchored" in item for item in errors), errors)

    def test_matching_non_repeated_region_is_accepted(self):
        errors, warnings = validate_evidence_integrity(self.make_bundle())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_image_derived_observation_requires_linked_caption_blind_inspection(self):
        bundle = self.make_bundle()
        bundle["result_units"]["R001"]["data_origin"] = "Qualitative_Observation"
        errors, _ = validate_evidence_integrity(bundle)
        self.assertTrue(any("requires a recorded CAPTION_BLIND" in item for item in errors), errors)

    def test_caption_blind_inspection_must_be_for_a_linked_region(self):
        bundle = self.make_bundle()
        bundle["result_units"]["R001"]["data_origin"] = "Visual_Estimate"
        bundle["visual_inspections"]["REG999"] = {
            "initial": {
                "inspection_mode": "CAPTION_BLIND",
                "caption_text_included": False,
                "report_narrative_included": False,
                "visual_legibility": "High",
            }
        }
        errors, _ = validate_evidence_integrity(bundle)
        self.assertTrue(any("requires a recorded CAPTION_BLIND" in item for item in errors), errors)

    def make_visual_metadata(self):
        dimensions = [
            {"dimension": "imaging_modality", "status": "OBSERVED", "value": "SEM",
             "source_location": "Image metadata", "recording_method": "SOURCE_METADATA", "confidence": "HIGH"},
            {"dimension": "magnification_or_pixel_size", "status": "UNKNOWN", "reason": "No calibration metadata is available.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
            {"dimension": "scale_bar_or_spatial_calibration", "status": "OBSERVED", "value": "50",
             "unit": "μm", "source_location": "Scale bar within the original crop", "recording_method": "SCALE_BAR_READ", "confidence": "HIGH"},
            {"dimension": "specimen_state_and_preparation", "status": "UNKNOWN", "reason": "The inspection pack does not include preparation metadata.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
            {"dimension": "image_processing_and_contrast", "status": "UNKNOWN", "reason": "Processing history is not supplied.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
            {"dimension": "field_selection_and_sampling", "status": "UNKNOWN", "reason": "Field-selection metadata are not supplied.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
        ]
        return {
            "status": "RECORDED",
            "dimensions": dimensions,
            "assessment_note": "All required visual metadata dimensions were recorded; unavailable items are explicitly marked.",
        }

    def test_linked_caption_blind_inspection_is_accepted(self):
        bundle = self.make_bundle()
        bundle["result_units"]["R001"]["data_origin"] = "Qualitative_Observation"
        bundle["visual_inspections"]["REG001"] = {
            "initial": {
                "inspection_mode": "CAPTION_BLIND",
                "caption_text_included": False,
                "report_narrative_included": False,
                "visual_legibility": "High",
                "visual_metadata_assessment": self.make_visual_metadata(),
            }
        }
        errors, _ = validate_evidence_integrity(bundle)
        self.assertEqual(errors, [])


class FitReproducibilityTests(unittest.TestCase):
    def make_bundle(self, reported=(2.0, 1.0, 1.0), include_audit=True):
        result = {
            "result_id": "R002",
            "claim_role": "CORE",
            "measurement_definition": {
                "is_derived_metric": True,
                "method": "least-squares linear fit",
                "status": "VERIFIED",
            },
            "observations": [{"numeric_values": list(reported)}],
        }
        if include_audit:
            result["calculation_audits"] = [{
                "audit_type": "OLS_LINEAR_FIT",
                "x_source": {"result_id": "R001", "observation_index": 0},
                "y_source": {"result_id": "R001", "observation_index": 1},
                "reported_source": {
                    "result_id": "R002",
                    "observation_index": 0,
                    "value_indices": {"intercept": 1, "slope": 0, "r_squared": 2},
                },
                "displayed_precision": {"slope": 3, "intercept": 3, "r_squared": 3},
                "statistical_quality_assessment": {
                    "status": "ASSESSED",
                    "diagnostics": [{
                        "diagnostic": "residual pattern",
                        "method": "residual plot review",
                        "result": "No material structure observed in this synthetic fixture.",
                    }],
                    "uncertainty_status": "QUALITATIVELY_ADDRESSED",
                    "uncertainty_note": "The synthetic residual spread was discussed qualitatively; no interval was available.",
                    "assessment_note": "The synthetic regression fixture records a separate quality review.",
                },
                "validation_assessment": {
                    "level": "INTERNAL_RESAMPLING",
                    "resampling_method": "five-fold cross-validation",
                    "split_unit": "independent observation unit",
                    "leakage_controls": ["All transformations are fitted within each training fold."],
                    "limitations": ["Synthetic fixture does not establish external transportability."],
                },
            }]
        return {
            "result_units": {
                "R001": {
                    "result_id": "R001",
                    "observations": [
                        {"numeric_values": [0, 1, 2, 3]},
                        {"numeric_values": [1, 3, 5, 7]},
                    ],
                },
                "R002": result,
            }
        }

    def test_ols_fit_reproduced_within_printed_rounding_precision(self):
        errors, warnings = validate_fit_reproducibility(self.make_bundle())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_non_reproducible_core_fit_is_rejected(self):
        errors, _ = validate_fit_reproducibility(
            self.make_bundle(reported=(1.8, 1.0, 0.99))
        )
        self.assertTrue(any("NOT_REPRODUCED" in item and "slope" in item for item in errors), errors)
        self.assertTrue(any("NOT_REPRODUCED" in item and "r_squared" in item for item in errors), errors)

    def test_core_statistical_fit_cannot_omit_calculation_audit(self):
        errors, _ = validate_fit_reproducibility(self.make_bundle(include_audit=False))
        self.assertTrue(any("requires calculation_audits" in item for item in errors), errors)

    def test_non_core_unreproduced_fit_is_warned_not_promoted(self):
        bundle = self.make_bundle(reported=(1.8, 1.0, 0.99))
        bundle["result_units"]["R002"]["claim_role"] = "SUPPORTING"
        errors, warnings = validate_fit_reproducibility(bundle)
        self.assertEqual(errors, [])
        self.assertTrue(any("NOT_REPRODUCED" in item for item in warnings), warnings)

    def test_mismatched_source_vector_lengths_are_rejected(self):
        bundle = self.make_bundle()
        bundle["result_units"]["R001"]["observations"][1]["numeric_values"] = [1, 2]
        errors, _ = validate_fit_reproducibility(bundle)
        self.assertTrue(any("at least three finite observations" in item for item in errors), errors)


class VisualComparabilityTests(unittest.TestCase):
    REQUIRED_DIMENSIONS = [
        "imaging_modality",
        "magnification_or_pixel_size",
        "scale_bar_or_spatial_calibration",
        "specimen_state_and_preparation",
        "image_processing_and_contrast",
        "field_selection_and_sampling",
    ]

    def make_inputs(self, include_assessment=True, missing_dimension=None, one_mismatch=False):
        evidence = {
            "result_units": {
                "R001": {
                    "result_id": "R001",
                    "data_type": "SEM micrograph",
                    "data_origin": "Qualitative_Observation",
                    "measurement_context": {"technique": "scanning electron microscopy"},
                },
                "R002": {
                    "result_id": "R002",
                    "data_type": "SEM micrograph",
                    "data_origin": "Qualitative_Observation",
                    "measurement_context": {"technique": "scanning electron microscopy"},
                },
            },
            "findings": {},
        }
        framework = {
            "claims": {
                "C001": {
                    "claim_id": "C001",
                    "claim_text": "Morphology changes between the compared states.",
                    "claim_type": "Descriptive",
                    "evidence_refs": [
                        {"kind": "result_unit", "id": "R001", "evidence_role": "SUPPORTS_CLAIM"},
                        {"kind": "result_unit", "id": "R002", "evidence_role": "SUPPORTS_CLAIM"},
                    ],
                    "comparability_assessment_ids": ["CMP001"] if include_assessment else [],
                }
            }
        }
        package = {"comparability_assessments": {}}
        if include_assessment:
            dimensions = []
            for name in self.REQUIRED_DIMENSIONS:
                if name == missing_dimension:
                    continue
                status = "MISMATCHED" if one_mismatch and name == "scale_bar_or_spatial_calibration" else "MATCHED"
                dimensions.append({
                    "dimension": name,
                    "match_status": status,
                    "values_by_entity": {"R001": "A", "R002": "B"},
                    "assessment_note": "Compared from source metadata.",
                })
            package["comparability_assessments"]["CMP001"] = {
                "assessment_id": "CMP001",
                "comparison_purpose": "Compare microscopy images across specimen states",
                "comparison_entities": [
                    {"entity_id": "R001", "entity_type": "result_unit", "label": "Image A"},
                    {"entity_id": "R002", "entity_type": "result_unit", "label": "Image B"},
                ],
                "dimensions": dimensions,
                "assessment_status": "NOT_COMPARABLE" if one_mismatch else "COMPARABLE",
                "limitations": ["Image scale/acquisition metadata were checked."],
                "permitted_inference": "Only image-level statements within the assessed scope.",
                "prohibited_inference": ["Do not infer morphology change across mismatched scale bars."],
            }
        return package, framework, evidence

    def test_multiple_image_results_require_comparability_assessment(self):
        package, framework, evidence = self.make_inputs(include_assessment=False)
        errors, _ = validate_visual_claim_comparability(package, framework, evidence)
        self.assertTrue(any("without a linked visual comparability assessment" in item for item in errors), errors)

    def test_complete_visual_comparability_dimensions_are_accepted(self):
        package, framework, evidence = self.make_inputs()
        errors, warnings = validate_visual_claim_comparability(package, framework, evidence)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_nonvisual_comparison_can_coexist_with_visual_assessment(self):
        package, framework, evidence = self.make_inputs()
        package["comparability_assessments"]["CMP002"] = {
            "assessment_id": "CMP002",
            "comparison_purpose": "Compare non-image experimental conditions",
            "comparison_entities": [
                {"entity_id": "R001", "entity_type": "result_unit", "label": "Result A"},
                {"entity_id": "R002", "entity_type": "result_unit", "label": "Result B"},
            ],
            "dimensions": [
                {"dimension": "reaction_temperature", "match_status": "MATCHED",
                 "values_by_entity": {"R001": 25, "R002": 25}, "assessment_note": "Same setpoint."}
            ],
            "assessment_status": "COMPARABLE",
            "limitations": [],
            "permitted_inference": "Temperature was matched.",
            "claim_ids": ["C001"],
        }
        errors, warnings = validate_visual_claim_comparability(package, framework, evidence)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_scale_or_acquisition_dimension_is_rejected(self):
        package, framework, evidence = self.make_inputs(missing_dimension="scale_bar_or_spatial_calibration")
        errors, _ = validate_visual_claim_comparability(package, framework, evidence)
        self.assertTrue(any("lacks required dimensions" in item for item in errors), errors)

    def test_mismatched_scale_can_only_be_reported_with_restricted_inference(self):
        package, framework, evidence = self.make_inputs(one_mismatch=True)
        errors, warnings = validate_visual_claim_comparability(package, framework, evidence)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_visual_comparison_cannot_be_comparable_with_mismatched_scale(self):
        package, framework, evidence = self.make_inputs(one_mismatch=True)
        package["comparability_assessments"]["CMP001"]["assessment_status"] = "COMPARABLE"
        errors, _ = validate_visual_claim_comparability(package, framework, evidence)
        self.assertTrue(any("cannot be COMPARABLE" in item for item in errors), errors)


class RouteDecisionTests(unittest.TestCase):
    def make_bundle(self):
        return {
            "recommended_route_id": "ROUTE001",
            "recommendation_rationale": "A concise but sufficiently detailed recommendation rationale that explains why this direction is preferred.",
            "routes": {
                "ROUTE001": {"route_id": "ROUTE001"},
                "ROUTE002": {"route_id": "ROUTE002"},
                "ROUTE003": {"route_id": "ROUTE003"},
            },
            "route_decision": {
                "selected_route_id": "ROUTE001",
                "selection_rationale": (
                    "The selected direction best matches the evidence that is presently available, "
                    "addresses the highest-value unresolved question, and has a testable next step."
                ),
                "selection_criteria": [
                    "Evidence adequacy and traceability",
                    "Comparability and uncertainty limits",
                    "Discriminating missing evidence and feasibility",
                ],
                "alternatives_considered": [
                    {"route_id": "ROUTE002", "disposition": "DEFERRED",
                     "rationale": "This route remains plausible but requires inputs not available for the primary decision."},
                    {"route_id": "ROUTE003", "disposition": "REJECTED",
                     "rationale": "This route does not address the central unresolved question as directly as the selected route."},
                ],
            },
        }

    def test_complete_route_decision_passes(self):
        errors, warnings = validate_route_selection(self.make_bundle())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_selected_route_requires_reasoned_alternative_assessment(self):
        bundle = self.make_bundle()
        del bundle["route_decision"]
        errors, _ = validate_route_selection(bundle)
        self.assertTrue(any("structured route_decision" in item for item in errors), errors)

    def test_all_non_selected_routes_must_be_assessed(self):
        bundle = self.make_bundle()
        bundle["route_decision"]["alternatives_considered"].pop()
        errors, _ = validate_route_selection(bundle)
        self.assertTrue(any("every non-selected candidate route" in item for item in errors), errors)

    def test_recommendation_rationale_cannot_be_empty(self):
        bundle = self.make_bundle()
        bundle["recommendation_rationale"] = ""
        errors, _ = validate_route_selection(bundle)
        self.assertTrue(any("requires recommendation_rationale" in item for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
