from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_manuscript_development import validate_package


def valid_fixture():
    framework = {
        "claims": {
            "C001": {
                "claim_id": "C001", "claim_text": "A measured relationship is observed",
                "claim_type": "Associational", "epistemic_status": "Observed",
                "evidence_refs": [{"kind": "result_unit", "id": "R001"}],
            }
        },
        "data_slots": {
            "DS001": {
                "data_slot_id": "DS001", "target_claim_id": "C001",
                "required_evidence_description": "Independent repeat measurement",
                "status": "MISSING", "priority": "ESSENTIAL",
                "acceptance_criteria": ["Predefined quality criterion"],
            }
        },
        "tasks": {
            "T001": {
                "task_id": "T001", "task_type": "EXPERIMENT", "status": "PLANNED",
                "priority": "P0", "target_data_slot_ids": ["DS001"],
                "target_claim_ids": ["C001"], "expected_output": "A validated data table",
                "completion_criteria": "Quality-control report and native data",
                "objective": "Resolve the missing evidence",
                "controls": ["Appropriate blank"], "measurements": ["Target response"],
                "required_raw_data": ["Native instrument file"],
                "replicate_plan": "Confirm with the responsible laboratory",
                "prerequisites": [],
            }
        },
    }
    literature = {"literature_claims": {"LC001": {"literature_claim_id": "LC001"}}}
    package = {
        "schema_version": 1,
        "project_profile": {
            "project_label": "Example project", "scientific_domain": "Example domain",
            "source_manifest": [{"source_id": "SRC001", "source_type": "report", "description": "Primary source"}],
            "user_constraints": [],
        },
        "journal_profile": {
            "target_journal": "Example Journal", "article_type": "Research Article",
            "status": "VERIFIED", "checked_at": "2026-01-01",
            "source_ids": ["JS001"], "requirements": {"figure_policy": "Checked"},
            "unresolved_items": [],
        },
        "journal_sources": {
            "JS001": {"source_id": "JS001", "title": "Official author guide",
                      "url": "https://example.org/guide", "accessed_at": "2026-01-01",
                      "scope": "Article types and figure requirements", "source_type": "OFFICIAL_JOURNAL"}
        },
        "core_argument": {
            "scientific_problem": "A defined scientific problem",
            "literature_gap": "A bounded literature gap",
            "central_question": "A testable central question",
            "central_thesis": "A provisional central thesis",
            "core_contribution": "One coherent contribution",
            "novelty_confidence": "LOW",
            "novelty_boundaries": ["Do not overstate the scope"],
            "competing_explanations": ["An alternative explanation"],
            "contribution_claim_ids": ["C001"],
        },
        "claim_ids": ["C001"], "data_slot_ids": ["DS001"],
        "introduction": {"status": "DRAFT", "paragraph_ids": ["IP001"],
                        "draft": "A short, evidence-linked draft."},
        "introduction_paragraphs": {
            "IP001": {"paragraph_id": "IP001", "role": "Problem framing",
                      "purpose": "Define the problem and its importance",
                      "topic_sentence": "The problem is important.",
                      "argument_notes": ["Move from field context to the gap"],
                      "claim_ids": ["C001"], "literature_claim_ids": ["LC001"],
                      "status": "DRAFTED"}
        },
        "storyline": {
            "STORY001": {"step_id": "STORY001", "order": 1, "section": "Results",
                         "narrative_question": "What is observed?",
                         "take_home_message": "The measured relationship is present.",
                         "claim_ids": ["C001"], "figure_ids": ["FIG001"],
                         "transition_logic": "The next step tests the explanation."}
        },
        "toc_graphic": {
            "status": "PLANNED", "journal_requirement_status": "REQUIRED",
            "concept_brief": "Summarize the central scientific contribution.",
            "elements": [{"role": "input", "description": "Starting system"}],
            "claim_ids": ["C001"], "data_slot_ids": ["DS001"],
            "generation_brief": "Use only evidence-supported elements.",
            "constraints": ["Do not show hypothetical outcomes as measured facts"],
        },
        "main_figures": {
            "FIG001": {"figure_id": "FIG001", "order": 1,
                       "working_title": "Evidence for the central claim",
                       "scientific_question": "What does the observation establish?",
                       "take_home_message": "A bounded conclusion is supported.",
                       "claim_ids": ["C001"], "data_slot_ids": ["DS001"],
                       "panels": [{"label": "a", "purpose": "Show the primary observation",
                                   "content_description": "An evidence-linked plot",
                                   "claim_ids": ["C001"], "data_slot_ids": ["DS001"],
                                   "existing_evidence_refs": [{"kind": "result_unit", "id": "R001"}],
                                   "comparison_design": ["Matched conditions"],
                                   "display_type": "Plot",
                                   "acceptance_criteria": ["Axes and units are traceable"],
                                   "status": "PARTIAL"}],
                       "main_text_rationale": "This is the first evidential step.",
                       "supporting_information_ids": ["SI001"], "layout_notes": [],
                       "status": "PARTIAL"}
        },
        "supporting_information": {
            "SI001": {"item_id": "SI001", "item_type": "method",
                      "title": "Supporting method details",
                      "content_description": "Reproducibility details and raw-data context",
                      "claim_ids": ["C001"], "figure_ids": ["FIG001"],
                      "data_slot_ids": ["DS001"], "methods_or_metadata": ["Calibration"],
                      "status": "TO_BE_PREPARED"}
        },
        "comparability_assessments": {},
        "work_package_task_ids": ["T001"],
        "manuscript_sections": [{"section": "Results and Discussion",
                                 "purpose": "Build the central evidence chain",
                                 "content_points": ["Present and interpret the observation"],
                                 "claim_ids": ["C001"], "figure_ids": ["FIG001"],
                                 "citation_literature_claim_ids": ["LC001"]}],
        "deliverables": [{"path": "FINAL_PLAN.md", "kind": "editable_plan",
                          "required": True, "status": "DRAFT"}],
        "quality_review": {"status": "IN_PROGRESS", "checks": [],
                           "unresolved_critical_questions": []},
        "human_decisions": {"research_direction": "PENDING_HUMAN_REVIEW",
                            "journal_positioning": "PENDING_HUMAN_REVIEW",
                            "manuscript_framework": "PENDING_HUMAN_REVIEW",
                            "decision_notes": []},
    }
    evidence = {"result_units": {"R001": {"result_id": "R001"}}, "findings": {},
                "samples": {"S001": {"sample_id": "S001"}, "S002": {"sample_id": "S002"}}}
    return package, framework, literature, evidence


class ManuscriptDevelopmentValidationTests(unittest.TestCase):
    def test_complete_generic_package_passes(self):
        package, framework, literature, evidence = valid_fixture()
        result = validate_package(package, framework, literature, evidence)
        self.assertEqual(result["errors"], [], result["errors"])

    def test_variable_figure_count_is_allowed(self):
        package, framework, literature, evidence = valid_fixture()
        package["main_figures"]["FIG002"] = {
            **package["main_figures"]["FIG001"],
            "figure_id": "FIG002", "order": 2,
        }
        package["main_figures"]["FIG002"]["supporting_information_ids"] = []
        package["storyline"]["STORY001"]["figure_ids"].append("FIG002")
        result = validate_package(package, framework, literature, evidence)
        self.assertEqual(result["errors"], [], result["errors"])

    def test_dangling_claim_reference_is_rejected(self):
        package, framework, literature, evidence = valid_fixture()
        package["main_figures"]["FIG001"]["claim_ids"] = ["C999"]
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("unknown ID C999" in item for item in result["errors"]))

    def test_essential_slot_without_task_is_rejected(self):
        package, framework, literature, evidence = valid_fixture()
        package["work_package_task_ids"] = []
        framework["tasks"] = {}
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("no task or explicit no_task_rationale" in item for item in result["errors"]))

    def test_dependency_cycle_is_rejected(self):
        package, framework, literature, evidence = valid_fixture()
        framework["tasks"]["T002"] = {
            **framework["tasks"]["T001"], "task_id": "T002",
            "prerequisites": ["T001"],
        }
        framework["tasks"]["T001"]["prerequisites"] = ["T002"]
        package["work_package_task_ids"].append("T002")
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("dependency cycle" in item for item in result["errors"]))

    def test_computation_cannot_be_ready_with_missing_inputs(self):
        package, framework, literature, evidence = valid_fixture()
        framework["tasks"]["T002"] = {
            "task_id": "T002", "task_type": "COMPUTATION", "status": "READY",
            "priority": "P1", "target_data_slot_ids": ["DS001"],
            "expected_output": "Validated model output",
            "completion_criteria": "Comparison against independent evidence",
            "design": {"required_inputs": ["validated_structure"],
                       "available_inputs": []},
            "prerequisites": [],
        }
        package["work_package_task_ids"].append("T002")
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("required inputs are missing" in item for item in result["errors"]))

    def test_verified_journal_profile_requires_sources(self):
        package, framework, literature, evidence = valid_fixture()
        package["journal_profile"]["source_ids"] = []
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("no cited official journal/publisher instruction source" in item for item in result["errors"]))

    def test_windows_absolute_deliverable_path_is_rejected(self):
        package, framework, literature, evidence = valid_fixture()
        package["deliverables"][0]["path"] = r"C:\\outside\\FINAL_PLAN.md"
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("deliverable path must remain workspace-relative" in item
                            for item in result["errors"]))

    def test_final_required_deliverable_must_exist(self):
        import tempfile
        package, framework, literature, evidence = valid_fixture()
        package["deliverables"][0]["status"] = "FINAL"
        with tempfile.TemporaryDirectory() as tmp:
            result = validate_package(package, framework, literature, evidence,
                                      deliverables_dir=Path(tmp))
        self.assertTrue(any("required deliverable marked FINAL but file is missing" in item
                            for item in result["errors"]))

    def test_verified_profile_cannot_rely_only_on_secondary_source(self):
        package, framework, literature, evidence = valid_fixture()
        package["journal_sources"]["JS001"]["source_type"] = "SECONDARY"
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("no cited official journal/publisher instruction source" in item
                            for item in result["errors"]))

    def test_comparable_assessment_rejects_unknown_or_mismatched_conditions(self):
        package, framework, literature, evidence = valid_fixture()
        package["comparability_assessments"]["CMP001"] = {
            "assessment_id": "CMP001",
            "comparison_purpose": "Assess whether two groups can be directly compared",
            "comparison_entities": [
                {"entity_id": "S001", "entity_type": "sample", "label": "Group A"},
                {"entity_id": "S002", "entity_type": "sample", "label": "Group B"},
            ],
            "dimensions": [
                {"dimension": "preparation_condition", "match_status": "MISMATCHED",
                 "values_by_entity": {"S001": "condition-A", "S002": "condition-B"}},
            ],
            "assessment_status": "COMPARABLE",
            "limitations": [],
            "permitted_inference": "No direct like-for-like inference is permitted.",
        }
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("COMPARABLE cannot contain mismatched or unknown dimensions" in item
                            for item in result["errors"]))

    def test_panel_can_link_valid_comparability_assessment(self):
        package, framework, literature, evidence = valid_fixture()
        package["comparability_assessments"]["CMP001"] = {
            "assessment_id": "CMP001",
            "comparison_purpose": "Assess matched comparison conditions",
            "comparison_entities": [
                {"entity_id": "S001", "entity_type": "sample", "label": "Group A"},
                {"entity_id": "S002", "entity_type": "sample", "label": "Group B"},
            ],
            "dimensions": [
                {"dimension": "measurement_temperature", "unit": "unit-T",
                 "match_status": "MATCHED", "values_by_entity": {"S001": 1, "S002": 1}},
            ],
            "assessment_status": "COMPARABLE", "limitations": [],
            "permitted_inference": "A controlled comparison is permitted for the listed dimension.",
        }
        package["main_figures"]["FIG001"]["panels"][0]["comparability_assessment_ids"] = ["CMP001"]
        result = validate_package(package, framework, literature, evidence)
        self.assertEqual(result["errors"], [], result["errors"])

    def test_central_contribution_cannot_bypass_core_metric_definition(self):
        package, framework, literature, evidence = valid_fixture()
        evidence["result_units"]["R002"] = {
            "result_id": "R002", "claim_role": "UNDECIDED",
            "observations": [{"numeric_value": 4.2}],
            "measurement_definition": {"status": "PARTIAL"},
        }
        framework["claims"]["C001"]["evidence_refs"] = [
            {"kind": "result_unit", "id": "R002"}
        ]
        result = validate_package(package, framework, literature, evidence)
        self.assertTrue(any("must be marked claim_role CORE" in item for item in result["errors"]))
        self.assertTrue(any("lacks a VERIFIED measurement definition" in item for item in result["errors"]))

    def test_verified_core_metric_can_support_central_contribution(self):
        package, framework, literature, evidence = valid_fixture()
        evidence["result_units"]["R002"] = {
            "result_id": "R002", "claim_role": "CORE",
            "observations": [{"numeric_value": 4.2}],
            "measurement_definition": {
                "status": "VERIFIED", "measurand": "Target measurand",
                "raw_signal": "Instrument signal", "method": "Defined method",
                "output_unit": "unit-A", "normalization_basis": "Per defined basis",
                "is_derived_metric": False,
            },
        }
        framework["claims"]["C001"]["evidence_refs"] = [
            {"kind": "result_unit", "id": "R002"}
        ]
        result = validate_package(package, framework, literature, evidence)
        self.assertEqual(result["errors"], [], result["errors"])


if __name__ == "__main__":
    unittest.main()
