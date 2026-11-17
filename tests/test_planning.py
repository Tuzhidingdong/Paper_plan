from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_planning import validate_bundles


def base_bundles():
    evidence = {
        "result_units": {"R001": {"result_id": "R001"}},
        "findings": {"F001": {"finding_id": "F001"}},
        "samples": {"S001": {"sample_id": "S001"}},
    }
    literature = {
        "search_scope": {"databases": ["Crossref"], "date_range": "2020-2026", "search_terms": ["topic-A"], "target_systems": ["system-A"]},
        "literature_records": {
            "LIT001": {
                "literature_id": "LIT001", "title": "Verified study", "access_level": "FULLTEXT_VERIFIED",
                "source_api": ["publisher"], "evidence_snippets": [
                    {"snippet_id": "SN001", "text": "Exact reported sentence.", "source_location": "Results, section 3", "scope": "FULLTEXT"}
                ],
            }
        },
        "literature_claims": {
            "LC001": {
                "literature_claim_id": "LC001", "claim_text": "A bounded literature statement.",
                "citation_refs": [{"literature_id": "LIT001", "snippet_id": "SN001"}],
            }
        },
        "research_gaps": {
            "GAP001": {
                "gap_id": "GAP001", "gap_statement": "A bounded unresolved comparison.",
                "search_bounds": {"databases": ["Crossref"], "date_range": "2020-2026", "search_terms": ["topic-A"], "target_systems": ["system-A"]},
                "supporting_literature_claim_ids": ["LC001"],
            }
        },
    }
    routes = {
        "routes": {
            f"ROUTE00{i}": {
                "route_id": f"ROUTE00{i}", "central_question": f"Question {i}",
                "novelty_candidate": f"Novelty candidate {i}", "bounded_gap": "A bounded gap",
                "feasibility": "Moderate", "novelty_risk": "Medium",
                "supporting_result_ids": ["R001"], "supporting_finding_ids": ["F001"],
                "gap_ids": ["GAP001"], "supporting_literature_claim_ids": ["LC001"],
                "competing_literature_ids": ["LIT001"], "alternative_explanations": ["Alternative A"],
                "data_slot_needs": ["Need additional control"],
            } for i in range(1, 4)
        },
        "recommended_route_id": "ROUTE001",
        "approval_A": {"status": "PENDING_HUMAN_REVIEW", "decision": None},
    }
    framework = {
        "claims": {
            "C001": {
                "claim_id": "C001", "claim_text": "Descriptive claim",
                "claim_type": "Descriptive", "epistemic_status": "Observed",
                "evidence_refs": [{"kind": "result_unit", "id": "R001"}],
            }
        },
        "data_slots": {
            "DS001": {
                "data_slot_id": "DS001", "target_claim_id": "C001",
                "required_evidence_description": "A repeatable quantitative measurement",
                "status": "MISSING", "available_result_ids": ["R001"],
            }
        },
        "data_units": {
            "DU001": {"data_unit_id": "DU001", "source_result_ids": ["R001"], "derived": False}
        },
        "tasks": {
            "T001": {
                "task_id": "T001", "task_type": "EXPERIMENT", "status": "PLANNED",
                "target_data_slot_ids": ["DS001"], "expected_output": "Validated measurement",
                "completion_criteria": "Quality-controlled result file",
                "objective": "Resolve missing evidence", "controls": ["Blank"],
                "measurements": ["Target measurement"], "required_raw_data": ["Native instrument file"],
                "replicate_plan": "To be confirmed by supervisor",
            }
        },
        "recommended_route_id": "ROUTE001",
        "approval_B": {"status": "PENDING_HUMAN_REVIEW", "decision": None},
    }
    return evidence, literature, routes, framework


class PlanningValidationTests(unittest.TestCase):
    def test_complete_provenance_graph_has_no_errors(self):
        result = validate_bundles(*base_bundles())
        self.assertNotEqual(result["status"], "ERROR", result["errors"])
        self.assertEqual(result["errors"], [])

    def test_metadata_only_source_cannot_support_literature_claim(self):
        evidence, literature, routes, framework = base_bundles()
        literature["literature_records"]["LIT001"]["access_level"] = "METADATA_ONLY"
        result = validate_bundles(evidence, literature, routes, framework)
        self.assertTrue(any("metadata-only" in error for error in result["errors"]))

    def test_dangling_data_slot_claim_reference_is_rejected(self):
        evidence, literature, routes, framework = base_bundles()
        framework["data_slots"]["DS001"]["target_claim_id"] = "C999"
        result = validate_bundles(evidence, literature, routes, framework)
        self.assertTrue(any("unknown claim" in error for error in result["errors"]))

    def test_calculation_waits_for_required_experiment(self):
        evidence, literature, routes, framework = base_bundles()
        framework["tasks"]["T002"] = {
            "task_id": "T002", "task_type": "COMPUTATION", "status": "BLOCKED_BY_EXPERIMENT",
            "target_data_slot_ids": ["DS001"], "expected_output": "Validated model output",
            "completion_criteria": "Compare against the measured structure",
            "requires_experiment_before_calculation": True, "blocked_by_experiment_ids": ["T001"],
        }
        result = validate_bundles(evidence, literature, routes, framework)
        self.assertEqual(result["errors"], [])

    def test_calculation_cannot_be_ready_when_input_experiment_is_missing(self):
        evidence, literature, routes, framework = base_bundles()
        framework["tasks"]["T002"] = {
            "task_id": "T002", "task_type": "COMPUTATION", "status": "READY",
            "target_data_slot_ids": ["DS001"], "expected_output": "Model output",
            "completion_criteria": "Validated model output",
            "requires_experiment_before_calculation": True, "blocked_by_experiment_ids": ["T001"],
        }
        result = validate_bundles(evidence, literature, routes, framework)
        self.assertTrue(any("BLOCKED_BY_EXPERIMENT" in error for error in result["errors"]))

    def test_duplicate_views_of_one_result_are_not_independent(self):
        evidence, literature, routes, framework = base_bundles()
        framework["data_units"]["DU002"] = {
            "data_unit_id": "DU002", "source_result_ids": ["R001"], "derived": True,
            "transformation": "A second plotting normalization",
        }
        result = validate_bundles(evidence, literature, routes, framework)
        self.assertTrue(any("not independent experiments" in warning for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
