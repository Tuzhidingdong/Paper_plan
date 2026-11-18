from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scientific_quality_gates import (
    validate_evidence_integrity,
    validate_fit_reproducibility,
    validate_proxy_measurement_design,
)


def complete_proxy_framework():
    return {
        "tasks": {
            "T001": {
                "task_id": "T001",
                "task_type": "EXPERIMENT",
                "target_data_slot_ids": ["DS001"],
                "expected_output": "Paired candidate and reference measurements.",
                "completion_criteria": "A traceable comparison dataset and analysis report.",
                "status": "PLANNED",
                "execution_design": {
                    "readiness": "READY_FOR_SUPERVISOR_APPROVAL",
                    "decision_framework": {
                        "question_type": "PROXY_VALIDATION",
                        "relationship_type": "AGREEMENT",
                        "primary_estimand": "Predeclared difference between candidate and reference measurements.",
                        "analysis_method": "A method appropriate to the measurement scale and sampling design.",
                        "acceptance_boundary": "A predeclared maximum absolute difference of 0.2 synthetic units.",
                        "acceptance_boundary_basis": "The synthetic margin was set before observing the synthetic comparison outcomes.",
                        "outcome_rules": [
                            {"outcome": "SUPPORTS", "criterion": "Agreement criteria are met.", "claim_implication": "The proxy is supported within the tested scope."},
                            {"outcome": "CONTRADICTS", "criterion": "Agreement criteria are not met beyond the declared boundary.", "claim_implication": "The proxy is not supported for the tested scope."},
                            {"outcome": "INCONCLUSIVE", "criterion": "Uncertainty or coverage prevents a decision.", "claim_implication": "No validity conclusion is established."},
                        ],
                    },
                    "measurement_validation": {
                        "validation_type": "PROXY_TO_REFERENCE",
                        "candidate_measurement": {
                            "name": "Candidate indicator",
                            "measurand": "Indirectly inferred target property",
                            "operational_definition": "Predeclared calculation from the candidate signal.",
                            "method": "Candidate measurement procedure.",
                            "unit": "unit-A",
                            "result_ids": [],
                        },
                        "reference_measurement": {
                            "name": "Reference endpoint",
                            "measurand": "Target property measured directly or by a justified reference",
                            "operational_definition": "Predeclared reference measurement procedure.",
                            "method": "Reference measurement procedure.",
                            "unit": "unit-A",
                            "reference_basis": "ORTHOGONAL_METHOD",
                            "independence_rationale": "The reference method has an independent measurement principle; shared limitations are disclosed.",
                            "limitations": [],
                        },
                        "sampling_design": {
                            "unit_of_analysis": "Independent experimental unit",
                            "pairing_strategy": "WITHIN_UNIT_PAIRED",
                            "condition_alignment": "MATCHED",
                            "time_alignment": "Same predefined observation window.",
                            "limitations": [],
                        },
                        "control_coverage": {
                            "review_status": "ASSESSED",
                            "required_control_classes": ["BLANK", "REFERENCE"],
                            "planned_controls": [
                                {"control_class": "BLANK", "purpose": "Estimate background contribution.", "rationale": "Background may contribute to the candidate signal."},
                                {"control_class": "REFERENCE", "purpose": "Anchor the target measurement.", "rationale": "A justified reference is needed to assess proxy validity."},
                            ],
                        },
                        "accounting_closure": {
                            "applicability": "NOT_REQUIRED",
                            "rationale": "The target measurement is not defined by a conserved input-output quantity in this design.",
                        },
                        "validation_strategy": {
                            "level": "INTERNAL_RESAMPLING",
                            "resampling_method": "Grouped cross-validation.",
                            "split_unit": "Independent experimental unit.",
                            "leakage_controls": ["All preprocessing and model fitting occur within training folds."],
                            "limitations": "Internal validation does not establish transportability to new settings.",
                        },
                        "limitations": ["Conclusions are limited to the declared population and conditions."],
                    },
                },
            }
        }
    }



def visual_evidence_bundle(metadata=None):
    card = {
        "inspection_mode": "CAPTION_BLIND",
        "caption_text_included": False,
        "report_narrative_included": False,
        "visual_legibility": "High",
    }
    if metadata is not None:
        card["visual_metadata_assessment"] = metadata
    return {
        "source": {"page_count": 1},
        "regions": {
            "REG001": {
                "region_id": "REG001",
                "page_number": 1,
                "bbox_normalized": [0.1, 0.2, 0.9, 0.8],
                "region_type": "embedded_image_block",
            }
        },
        "panels": {},
        "visual_inspections": {"REG001": {"initial": card, "reinspections": [], "locked": True}},
        "result_units": {
            "R001": {
                "result_id": "R001",
                "region_ids": ["REG001"],
                "panel_ids": [],
                "source_location": "PDF p.1, embedded image",
                "data_origin": "Qualitative_Observation",
            }
        },
    }


def complete_visual_metadata():
    return {
        "status": "RECORDED",
        "assessment_note": "The original-resolution crop was inspected and each required metadata dimension was recorded.",
        "dimensions": [
            {"dimension": "imaging_modality", "status": "OBSERVED", "value": "Microscopy",
             "source_location": "Image header", "recording_method": "SOURCE_METADATA", "confidence": "HIGH"},
            {"dimension": "magnification_or_pixel_size", "status": "UNKNOWN", "reason": "No magnification or pixel calibration was supplied.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
            {"dimension": "scale_bar_or_spatial_calibration", "status": "NOT_LEGIBLE", "reason": "A scale bar is not legible in the supplied crop.",
             "recording_method": "VISUAL_REVIEW", "confidence": "UNASSESSABLE"},
            {"dimension": "specimen_state_and_preparation", "status": "UNKNOWN", "reason": "Preparation metadata are absent.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
            {"dimension": "image_processing_and_contrast", "status": "UNKNOWN", "reason": "Processing metadata are absent.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
            {"dimension": "field_selection_and_sampling", "status": "UNKNOWN", "reason": "Field selection is not documented.",
             "recording_method": "OTHER", "confidence": "UNASSESSABLE"},
        ],
    }


class VisualMetadataCaptureTests(unittest.TestCase):
    def test_linked_visual_inspection_requires_metadata_capture(self):
        errors, _ = validate_evidence_integrity(visual_evidence_bundle())
        self.assertTrue(any("lacks a visual_metadata_assessment" in item for item in errors), errors)

    def test_explicit_unknown_and_not_legible_states_are_acceptable_records(self):
        errors, warnings = validate_evidence_integrity(
            visual_evidence_bundle(complete_visual_metadata())
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_all_visual_metadata_dimensions_must_be_recorded(self):
        metadata = complete_visual_metadata()
        metadata["dimensions"].pop()
        errors, _ = validate_evidence_integrity(visual_evidence_bundle(metadata))
        self.assertTrue(any("lacks explicit states for" in item for item in errors), errors)

    def test_observed_scale_value_requires_unit_and_source_location(self):
        metadata = complete_visual_metadata()
        scale = next(
            item for item in metadata["dimensions"]
            if item["dimension"] == "scale_bar_or_spatial_calibration"
        )
        scale.update({
            "status": "OBSERVED",
            "value": "50",
            "unit": "",
            "source_location": "",
            "recording_method": "SCALE_BAR_READ",
            "confidence": "HIGH",
        })
        errors, _ = validate_evidence_integrity(visual_evidence_bundle(metadata))
        self.assertTrue(any("requires an explicit unit" in item for item in errors), errors)
        self.assertTrue(any("requires a source_location" in item for item in errors), errors)

    def test_not_present_or_unknown_visual_metadata_requires_a_reason(self):
        metadata = complete_visual_metadata()
        scale = next(
            item for item in metadata["dimensions"]
            if item["dimension"] == "scale_bar_or_spatial_calibration"
        )
        scale["reason"] = ""
        errors, _ = validate_evidence_integrity(visual_evidence_bundle(metadata))
        self.assertTrue(any("requires a reason" in item for item in errors), errors)


class ProxyMeasurementDesignTests(unittest.TestCase):
    def test_complete_proxy_to_reference_design_passes(self):
        errors, warnings = validate_proxy_measurement_design(complete_proxy_framework())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_non_proxy_task_is_not_subject_to_proxy_gate(self):
        framework = {"tasks": {"T001": {"task_id": "T001", "execution_design": {"readiness": "DRAFT"}}}}
        errors, warnings = validate_proxy_measurement_design(framework)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_measurement_validation_is_reported(self):
        framework = complete_proxy_framework()
        del framework["tasks"]["T001"]["execution_design"]["measurement_validation"]
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("measurement_validation record" in item for item in errors), errors)

    def test_incomplete_draft_warns_without_becoming_execution_error(self):
        framework = complete_proxy_framework()
        execution = framework["tasks"]["T001"]["execution_design"]
        execution["readiness"] = "DRAFT"
        execution["measurement_validation"]["reference_measurement"] = {}
        errors, warnings = validate_proxy_measurement_design(framework)
        self.assertEqual(errors, [])
        self.assertTrue(any("reference_measurement is missing" in item for item in warnings), warnings)

    def test_candidate_and_reference_measurands_must_be_separately_defined(self):
        framework = complete_proxy_framework()
        framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["candidate_measurement"] = {}
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("candidate_measurement is missing" in item for item in errors), errors)

    def test_matched_units_require_matching_factors(self):
        framework = complete_proxy_framework()
        sampling = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["sampling_design"]
        sampling["pairing_strategy"] = "MATCHED_UNITS"
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("matching_factors" in item for item in errors), errors)

    def test_agreement_rejects_unpaired_design_without_rationale(self):
        framework = complete_proxy_framework()
        sampling = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["sampling_design"]
        sampling["pairing_strategy"] = "UNPAIRED"
        sampling.pop("unpaired_design_rationale", None)
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("requires a paired or matched sampling design" in item for item in errors), errors)

    def test_mismatched_conditions_block_agreement_ready_design(self):
        framework = complete_proxy_framework()
        sampling = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["sampling_design"]
        sampling["condition_alignment"] = "MISMATCHED"
        sampling["limitations"] = ["The compared units differ on a relevant condition."]
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("cannot be execution-ready" in item for item in errors), errors)

    def test_relationship_type_is_required(self):
        framework = complete_proxy_framework()
        del framework["tasks"]["T001"]["execution_design"]["decision_framework"]["relationship_type"]
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("relationship_type" in item for item in errors), errors)

    def test_placeholder_acceptance_boundary_is_not_decision_ready(self):
        framework = complete_proxy_framework()
        decision = framework["tasks"]["T001"]["execution_design"]["decision_framework"]
        decision["acceptance_boundary"] = "To be justified later."
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("acceptance_boundary" in item for item in errors), errors)

    def test_result_unit_links_must_resolve_when_evidence_is_supplied(self):
        framework = complete_proxy_framework()
        candidate = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["candidate_measurement"]
        candidate["result_ids"] = ["R999"]
        errors, _ = validate_proxy_measurement_design(framework, {"result_units": {"R001": {}}})
        self.assertTrue(any("unknown Result Unit R999" in item for item in errors), errors)

    def test_prospective_validation_requires_a_future_data_collection_plan(self):
        framework = complete_proxy_framework()
        validation = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["validation_strategy"]
        validation.update({
            "level": "PROSPECTIVE",
            "training_data_scope": "Existing development cohort",
            "validation_data_scope": "Future independent cohort",
            "training_dataset_ids": ["TRAIN-001"],
            "planned_validation_source": "A separately recruited cohort under a pre-registered protocol.",
            "independence_unit": "Participant",
            "leakage_controls": ["No participant appears in both development and future validation cohorts."],
            "limitations": "Prospective data have not yet been acquired.",
        })
        errors, warnings = validate_proxy_measurement_design(framework)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_outcome_rules_and_boundary_basis_are_required(self):
        framework = complete_proxy_framework()
        decision = framework["tasks"]["T001"]["execution_design"]["decision_framework"]
        decision["outcome_rules"] = []
        decision["acceptance_boundary_basis"] = ""
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("acceptance_boundary_basis" in item for item in errors), errors)
        self.assertTrue(any("outcome_rule:SUPPORTS" in item for item in errors), errors)
        self.assertTrue(any("outcome_rule:CONTRADICTS" in item for item in errors), errors)

    def test_required_control_class_must_have_a_planned_control(self):
        framework = complete_proxy_framework()
        control = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["control_coverage"]
        control["required_control_classes"].append("RECOVERY")
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("required control classes have no planned control" in item for item in errors), errors)

    def test_empty_control_plan_requires_explicit_rationale(self):
        framework = complete_proxy_framework()
        control = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["control_coverage"]
        control["required_control_classes"] = []
        control["planned_controls"] = []
        control.pop("no_control_rationale", None)
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("empty control plan requires a rationale" in item for item in errors), errors)

    def test_required_accounting_closure_needs_inputs_outputs_and_residual(self):
        framework = complete_proxy_framework()
        accounting = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["accounting_closure"]
        accounting["applicability"] = "REQUIRED"
        accounting.pop("accounted_inputs", None)
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("required accounting closure is missing" in item for item in errors), errors)

    def test_not_required_accounting_closure_needs_rationale(self):
        framework = complete_proxy_framework()
        accounting = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["accounting_closure"]
        accounting.pop("rationale")
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("NOT_REQUIRED accounting closure requires a rationale" in item for item in errors), errors)

    def test_external_validation_requires_independent_scope_and_leakage_controls(self):
        framework = complete_proxy_framework()
        validation = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["validation_strategy"]
        validation["level"] = "EXTERNAL_INDEPENDENT_DATA"
        validation["training_data_scope"] = "dataset-A"
        validation["validation_data_scope"] = "dataset-A"
        validation["validation_dataset_ids"] = []
        validation.pop("independence_unit", None)
        validation.pop("leakage_controls", None)
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("EXTERNAL_INDEPENDENT_DATA requires" in item for item in errors), errors)

    def test_external_validation_with_disjoint_datasets_passes(self):
        framework = complete_proxy_framework()
        validation = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["validation_strategy"]
        validation.update({
            "level": "EXTERNAL_INDEPENDENT_DATA",
            "training_data_scope": "Development cohort",
            "validation_data_scope": "Independent external cohort",
            "training_dataset_ids": ["TRAIN-001"],
            "validation_dataset_ids": ["VALIDATE-001"],
            "independence_unit": "Independent participant",
            "leakage_controls": ["No participant or batch appears in both cohorts."],
            "limitations": ["External performance is limited to the sampled population."],
        })
        errors, warnings = validate_proxy_measurement_design(framework)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_external_validation_rejects_overlapping_dataset_ids(self):
        framework = complete_proxy_framework()
        validation = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["validation_strategy"]
        validation.update({
            "level": "EXTERNAL_INDEPENDENT_DATA",
            "training_data_scope": "Development cohort",
            "validation_data_scope": "Claimed external cohort",
            "training_dataset_ids": ["DATASET-001"],
            "validation_dataset_ids": ["DATASET-001"],
            "independence_unit": "Independent participant",
            "leakage_controls": ["A nominal split was applied."],
            "limitations": ["Potential overlap is acknowledged."],
        })
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("disjoint training/validation dataset IDs" in item for item in errors), errors)

    def test_in_sample_validation_is_explicitly_limited(self):
        framework = complete_proxy_framework()
        validation = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["validation_strategy"]
        validation["level"] = "IN_SAMPLE_ONLY"
        validation["limitations"] = "Evaluation uses only the fitted observations."
        errors, warnings = validate_proxy_measurement_design(framework)
        self.assertEqual(errors, [])
        self.assertTrue(any("IN_SAMPLE_ONLY" in item for item in warnings), warnings)

    def test_not_assessed_validation_cannot_be_execution_ready(self):
        framework = complete_proxy_framework()
        validation = framework["tasks"]["T001"]["execution_design"]["measurement_validation"]["validation_strategy"]
        validation["level"] = "NOT_ASSESSED"
        validation["limitations"] = "Validation planning has not been completed."
        errors, _ = validate_proxy_measurement_design(framework)
        self.assertTrue(any("cannot leave validation strategy unassessed" in item for item in errors), errors)


class FitAssessmentSeparationTests(unittest.TestCase):
    def make_fit_bundle(self):
        audit = {
            "audit_type": "OLS_LINEAR_FIT",
            "reproduction_status": "REPRODUCED",
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
                "uncertainty_status": "QUANTIFIED",
                "uncertainty_note": "Expanded uncertainty was estimated from the synthetic replicate distribution.",
                "assessment_note": "Uncertainty was separately assessed in this synthetic fixture.",
            },
            "validation_assessment": {
                "level": "INTERNAL_RESAMPLING",
                "resampling_method": "Grouped cross-validation.",
                "split_unit": "Independent observation unit.",
                "leakage_controls": ["Preprocessing is fitted within training folds."],
                "limitations": ["This synthetic fixture does not prove external transportability."],
            },
        }
        return {
            "result_units": {
                "R001": {
                    "result_id": "R001",
                    "observations": [
                        {"numeric_values": [0, 1, 2, 3]},
                        {"numeric_values": [1, 3, 5, 7]},
                    ],
                },
                "R002": {
                    "result_id": "R002",
                    "claim_role": "CORE",
                    "measurement_definition": {
                        "is_derived_metric": True,
                        "method": "least-squares linear fit",
                        "status": "VERIFIED",
                    },
                    "observations": [{"numeric_values": [2.0, 1.0, 1.0]}],
                    "calculation_audits": [audit],
                },
            }
        }

    def test_fit_assessment_records_are_distinct_and_complete(self):
        errors, warnings = validate_fit_reproducibility(self.make_fit_bundle())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_reproduction_status_must_match_the_recomputed_fit(self):
        bundle = self.make_fit_bundle()
        audit = bundle["result_units"]["R002"]["calculation_audits"][0]
        audit["reproduction_status"] = "NOT_REPRODUCED"
        errors, _ = validate_fit_reproducibility(bundle)
        self.assertTrue(any("reproduction_status must be REPRODUCED" in item for item in errors), errors)

    def test_core_fit_requires_separate_statistical_quality_assessment(self):
        bundle = self.make_fit_bundle()
        del bundle["result_units"]["R002"]["calculation_audits"][0]["statistical_quality_assessment"]
        errors, _ = validate_fit_reproducibility(bundle)
        self.assertTrue(any("statistical_quality_assessment" in item for item in errors), errors)

    def test_placeholder_diagnostic_does_not_count_as_quality_assessment(self):
        bundle = self.make_fit_bundle()
        quality = bundle["result_units"]["R002"]["calculation_audits"][0]["statistical_quality_assessment"]
        quality["diagnostics"] = [{
            "diagnostic": "TBD",
            "method": "Not assessed",
            "result": "Unknown",
        }]
        errors, _ = validate_fit_reproducibility(bundle)
        self.assertTrue(any("requires a diagnostic with a defined check, method and result" in item for item in errors), errors)

    def test_core_fit_requires_explicit_validation_level(self):
        bundle = self.make_fit_bundle()
        del bundle["result_units"]["R002"]["calculation_audits"][0]["validation_assessment"]
        errors, _ = validate_fit_reproducibility(bundle)
        self.assertTrue(any("validation_assessment" in item for item in errors), errors)

    def test_in_sample_fit_is_not_mislabelled_as_external_validation(self):
        bundle = self.make_fit_bundle()
        audit = bundle["result_units"]["R002"]["calculation_audits"][0]
        audit["validation_assessment"] = {
            "level": "IN_SAMPLE_ONLY",
            "limitations": ["Only fitted observations were used."],
        }
        errors, warnings = validate_fit_reproducibility(bundle)
        self.assertEqual(errors, [])
        self.assertTrue(any("in-sample only" in item for item in warnings), warnings)

    def test_external_validation_with_disjoint_training_and_validation_data_passes(self):
        bundle = self.make_fit_bundle()
        validation = bundle["result_units"]["R002"]["calculation_audits"][0]["validation_assessment"]
        validation.update({
            "level": "EXTERNAL_INDEPENDENT_DATA",
            "training_data_scope": "Development cohort",
            "validation_data_scope": "Independent validation cohort",
            "training_dataset_ids": ["TRAIN-001"],
            "validation_dataset_ids": ["VALIDATE-001"],
            "independence_unit": "Independent participant",
            "leakage_controls": ["No participant is shared between training and validation data."],
            "limitations": ["External validity is limited to the sampled population."],
        })
        errors, warnings = validate_fit_reproducibility(bundle)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_external_validation_requires_distinct_scope_and_leakage_controls(self):
        bundle = self.make_fit_bundle()
        audit = bundle["result_units"]["R002"]["calculation_audits"][0]
        audit["validation_assessment"] = {
            "level": "EXTERNAL_INDEPENDENT_DATA",
            "training_data_scope": "dataset-A",
            "validation_data_scope": "dataset-A",
            "validation_dataset_ids": [],
            "independence_unit": "",
            "leakage_controls": [],
            "limitations": [],
        }
        errors, _ = validate_fit_reproducibility(bundle)
        self.assertTrue(any("EXTERNAL_INDEPENDENT_DATA requires" in item for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
