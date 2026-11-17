"""Generic tests for the quantitative Result Unit gate.

All identifiers, values and descriptions here are synthetic. No real project,
sample, measurement or conclusion is represented in this module.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_evidence import validate as validate_evidence  # noqa: E402
from validate_manuscript_development import validate_package  # noqa: E402


def numeric_result(result_id="R001", *, numeric_value="ABSENT", numeric_values=None,
                   description="Group A reading 12.5 units; group B reading 7.25 units",
                   origin="Exact_Text", permission="Exact_Values", role="UNDECIDED",
                   definition_status="PARTIAL"):
    """Build a synthetic quantitative Result Unit with a configurable value carrier."""
    observation = {"description": description, "source_status": "Observed"}
    if numeric_value != "ABSENT":
        observation["numeric_value"] = numeric_value
    if numeric_values is not None:
        observation["numeric_values"] = numeric_values
    result = {
        "result_id": result_id,
        "region_ids": ["REG001"],
        "data_type": "instrument_response",
        "data_origin": origin,
        "visual_legibility": "High",
        "is_visual_estimate": False,
        "quantitative_permission": permission,
        "epistemic_status": "Observed",
        "measurement_context": {"sample_associations": []},
        "observations": [observation],
        "instrument_checklist": {"figure_status": {}, "report_status": {}},
        "claim_role": role,
        "measurement_definition": {"status": definition_status},
    }
    return result


def evidence_bundle(result):
    return {
        "schema_version": 1,
        "workspace_revision": "0.1.0",
        "source": {"file_name": "synthetic.pdf", "sha256": "a" * 64, "page_count": 1},
        "regions": {
            "REG001": {
                "region_id": "REG001", "anchor_key": "region-synthetic", "page_number": 1,
                "bbox_normalized": [0.1, 0.1, 0.9, 0.9],
                "image_path": "extracted/regions/REG001.png", "pixel_sha256": "b" * 64,
            }
        },
        "panels": {},
        "result_units": {result["result_id"]: result},
        "findings": {},
        "samples": {},
        "audit_records": [],
        "discrepancies": [],
        "visual_inspections": {},
    }


def manuscript_fixture(result, *, via_finding=False, via_contradictory=False):
    """Return (package, framework, literature, evidence) with a central claim."""
    rid = result["result_id"]
    evidence = evidence_bundle(result)
    if via_finding or via_contradictory:
        key = "contradictory_result_ids" if via_contradictory else "supporting_result_ids"
        evidence["findings"]["F001"] = {
            "finding_id": "F001", "description": "Synthetic interpretation",
            "epistemic_status": "Observed", "supporting_result_ids": [],
            "contradictory_result_ids": [], "alternative_explanations": [],
        }
        evidence["findings"]["F001"][key] = [rid]
        refs = [{"kind": "finding", "id": "F001"}]
    else:
        refs = [{"kind": "result_unit", "id": rid}]
    framework = {
        "claims": {
            "C001": {
                "claim_id": "C001", "claim_text": "A synthetic central statement",
                "claim_type": "Associational", "epistemic_status": "Observed",
                "evidence_refs": refs,
            }
        },
        "data_slots": {}, "tasks": {},
    }
    literature = {"literature_claims": {}}
    package = {
        "schema_version": 1,
        "project_profile": {
            "project_label": "Synthetic gate project", "scientific_domain": "Synthetic domain",
            "source_manifest": [{"source_id": "SRC001", "source_type": "report", "description": "Synthetic source"}],
            "user_constraints": [],
        },
        "journal_profile": {
            "target_journal": "Synthetic Journal", "article_type": "Research Article",
            "status": "UNVERIFIED", "checked_at": "2026-01-01", "source_ids": [],
            "requirements": {}, "unresolved_items": ["Synthetic item"],
        },
        "journal_sources": {},
        "core_argument": {
            "scientific_problem": "Synthetic problem", "literature_gap": "Synthetic gap",
            "central_question": "Synthetic question", "central_thesis": "Synthetic thesis",
            "core_contribution": "Synthetic contribution", "novelty_confidence": "LOW",
            "novelty_boundaries": ["Synthetic boundary"], "competing_explanations": [],
            "contribution_claim_ids": ["C001"],
        },
        "claim_ids": ["C001"], "data_slot_ids": [],
        "introduction": {"status": "NOT_STARTED", "paragraph_ids": [], "draft": None},
        "introduction_paragraphs": {}, "storyline": {}, "comparability_assessments": {},
        "toc_graphic": {
            "status": "NOT_STARTED", "journal_requirement_status": "UNKNOWN",
            "concept_brief": "Synthetic", "elements": [], "claim_ids": [], "data_slot_ids": [],
        },
        "main_figures": {}, "supporting_information": {}, "work_package_task_ids": [],
        "manuscript_sections": [], "deliverables": [],
        "quality_review": {"status": "PASS", "checks": [], "unresolved_critical_questions": []},
        "human_decisions": {"research_direction": "PENDING_HUMAN_REVIEW",
                            "journal_positioning": "PENDING_HUMAN_REVIEW",
                            "manuscript_framework": "PENDING_HUMAN_REVIEW"},
    }
    return package, framework, literature, evidence


def gate_errors(result, **kwargs):
    package, framework, literature, evidence = manuscript_fixture(result, **kwargs)
    return validate_package(package, framework, literature, evidence)["errors"]


class NumericValueCarrierTests(unittest.TestCase):
    """What counts as a quantitative observation must be explicit and consistent."""

    def test_numeric_json_number_is_recognised(self):
        errors = gate_errors(numeric_result(numeric_value=12.5))
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)

    def test_parseable_numeric_string_is_recognised(self):
        errors = gate_errors(numeric_result(numeric_value="12.5"))
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)

    def test_unparseable_numeric_string_is_not_a_measurement(self):
        # A qualitative result whose carrier field holds free text must not be
        # promoted to quantitative by that stray, unparseable string.
        result = numeric_result(
            numeric_value="not-a-number",
            description="Pattern shown in Figure 3 on page 7 appears different",
            origin="Qualitative_Observation", permission="Qualitative_Only",
        )
        errors = gate_errors(result)
        self.assertFalse(any("claim_role CORE" in e for e in errors), errors)

    def test_missing_numeric_value_with_structured_values_is_recognised(self):
        errors = gate_errors(numeric_result(numeric_values=["12.5", "7.25"]))
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)

    def test_transcribed_values_with_exact_permission_are_recognised(self):
        # Numeric values exist only in transcription text; the structured
        # declaration is quantitative_permission == Exact_Values.
        errors = gate_errors(numeric_result())
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)

    def test_qualitative_description_is_not_treated_as_quantitative(self):
        result = numeric_result(
            numeric_value="ABSENT",
            description="Pattern shown in Figure 3 on page 7 appears different",
            origin="Qualitative_Observation", permission="Qualitative_Only",
        )
        errors = gate_errors(result)
        self.assertFalse(any("claim_role CORE" in e for e in errors), errors)


class EvidenceChainTests(unittest.TestCase):
    def test_direct_result_unit_reference_is_gated(self):
        errors = gate_errors(numeric_result())
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)

    def test_finding_supporting_reference_is_gated(self):
        errors = gate_errors(numeric_result(), via_finding=True)
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)

    def test_finding_contradictory_reference_is_gated(self):
        errors = gate_errors(numeric_result(), via_contradictory=True)
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)

    def test_core_role_and_verified_definition_cannot_be_omitted(self):
        errors = gate_errors(numeric_result())
        self.assertTrue(any("claim_role CORE" in e for e in errors), errors)
        self.assertTrue(any("VERIFIED measurement definition" in e for e in errors), errors)

    def test_derived_metric_requires_formula_and_parent_lineage(self):
        result = numeric_result(role="CORE", definition_status="VERIFIED")
        result["measurement_definition"].update({
            "is_derived_metric": True, "formula": None, "parent_result_ids": [],
        })
        package, framework, literature, evidence = manuscript_fixture(result)
        errors = validate_package(package, framework, literature, evidence)["errors"]
        self.assertTrue(any("lacks formula or parent-result lineage" in e for e in errors), errors)


class EvidenceValidatorTests(unittest.TestCase):
    def test_exact_values_without_machine_readable_number_gets_warning(self):
        errors, warnings = validate_evidence(evidence_bundle(numeric_result()))
        self.assertFalse(errors, errors)
        self.assertTrue(any("machine-readable" in w for w in warnings), warnings)

    def test_structured_values_satisfy_the_interface(self):
        errors, warnings = validate_evidence(
            evidence_bundle(numeric_result(numeric_values=["12.5", "7.25"]))
        )
        self.assertFalse(errors, errors)
        self.assertFalse(any("machine-readable" in w for w in warnings), warnings)

    def test_unparseable_numeric_string_is_rejected(self):
        errors, _ = validate_evidence(
            evidence_bundle(numeric_result(numeric_value="not-a-number"))
        )
        self.assertTrue(any("numeric_value" in e and "number" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
