import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scientific_argument_bridge import (
    validate_core_claim_analysis_bridge,
    validate_finding_analysis_refs,
    validate_route_analysis_bridge,
)


def _base_evidence():
    return {
        "scientific_analyses": {
            "SANA-001": {
                "analysis_id": "SANA-001",
                "observations": [
                    {"observation_id": "OBS-001", "result_ids": ["R001"]},
                    {"observation_id": "OBS-002", "result_ids": ["R002"]},
                ],
                "relationships": [
                    {
                        "relationship_id": "REL-001",
                        "result_ids": ["R001", "R002"],
                        "observation_ids": ["OBS-001", "OBS-002"],
                    }
                ],
                "interpretations": [
                    {
                        "interpretation_id": "INT-001",
                        "supporting_observation_ids": ["OBS-001", "OBS-002"],
                    }
                ],
            }
        },
        "findings": {
            "F001": {
                "finding_id": "F001",
                "description": "A source-linked cross-result relationship.",
                "epistemic_status": "Interpreted",
                "analysis_derived": True,
                "scientific_analysis_refs": [
                    {
                        "analysis_id": "SANA-001",
                        "record_type": "relationship",
                        "record_id": "REL-001",
                    }
                ],
                "supporting_result_ids": ["R001", "R002"],
                "contradictory_result_ids": [],
                "alternative_explanations": ["A non-causal shared-condition explanation."],
                "limitations": ["The relationship is not evidence of causation."],
            }
        },
    }


def _central_package():
    return {"core_argument": {"contribution_claim_ids": ["C001"]}}


def _central_framework(with_finding=True):
    refs = []
    if with_finding:
        refs.append({"kind": "finding", "id": "F001", "evidence_role": "SUPPORTS_CLAIM"})
    else:
        refs.extend([
            {"kind": "result_unit", "id": "R001", "evidence_role": "SUPPORTS_CLAIM"},
            {"kind": "result_unit", "id": "R002", "evidence_role": "SUPPORTS_CLAIM"},
        ])
    return {
        "claims": {
            "C001": {
                "claim_id": "C001",
                "claim_type": "Comparative",
                "evidence_refs": refs,
            }
        }
    }


class ScientificArgumentBridgeTests(unittest.TestCase):
    def test_analysis_derived_finding_reference_resolves(self):
        errors = validate_finding_analysis_refs(_base_evidence())
        self.assertEqual(errors, [])

    def test_analysis_derived_finding_requires_exact_record_reference(self):
        evidence = _base_evidence()
        evidence["findings"]["F001"]["scientific_analysis_refs"][0]["record_id"] = "REL-999"
        errors = validate_finding_analysis_refs(evidence)
        self.assertTrue(any("unknown scientific analysis record" in item for item in errors))

    def test_interpretation_reference_resolves_supporting_observations(self):
        evidence = _base_evidence()
        evidence["findings"]["F001"]["scientific_analysis_refs"] = [{
            "analysis_id": "SANA-001",
            "record_type": "interpretation",
            "record_id": "INT-001",
        }]
        self.assertEqual(validate_finding_analysis_refs(evidence), [])

    def test_legacy_finding_without_analysis_refs_remains_valid(self):
        evidence = _base_evidence()
        finding = evidence["findings"]["F001"]
        finding.pop("analysis_derived")
        finding.pop("scientific_analysis_refs")
        self.assertEqual(validate_finding_analysis_refs(evidence), [])

    def test_duplicate_relationship_ids_are_rejected(self):
        evidence = _base_evidence()
        evidence["scientific_analyses"]["SANA-001"]["relationships"].append({
            "relationship_id": "REL-001",
            "result_ids": ["R001", "R002"],
        })
        errors = validate_finding_analysis_refs(evidence)
        self.assertTrue(any("duplicate relationship record ID" in item for item in errors))

    def test_finding_result_units_must_be_covered_by_cited_records(self):
        evidence = _base_evidence()
        evidence["findings"]["F001"]["supporting_result_ids"].append("R003")
        errors = validate_finding_analysis_refs(evidence)
        self.assertTrue(any("do not cover Finding Result Units" in item for item in errors))

    def test_cross_result_core_claim_requires_analysis_derived_finding(self):
        errors = validate_core_claim_analysis_bridge(
            _central_package(), _central_framework(with_finding=False), _base_evidence()
        )
        self.assertTrue(any("analysis-derived Finding" in item for item in errors))

    def test_cross_result_core_claim_passes_with_linked_finding(self):
        errors = validate_core_claim_analysis_bridge(
            _central_package(), _central_framework(with_finding=True), _base_evidence()
        )
        self.assertEqual(errors, [])

    def test_candidate_route_reports_missing_argument_bridge(self):
        warnings = validate_route_analysis_bridge(
            {"routes": {"ROUTE001": {
                "supporting_result_ids": ["R001", "R002"],
                "supporting_finding_ids": [],
            }}},
            _base_evidence(),
        )
        self.assertEqual(len(warnings), 1)

    def test_single_result_core_claim_does_not_require_cross_result_bridge(self):
        framework = {
            "claims": {"C001": {
                "claim_type": "Comparative",
                "evidence_refs": [{"kind": "result_unit", "id": "R001"}],
            }}
        }
        errors = validate_core_claim_analysis_bridge(
            _central_package(), framework, _base_evidence()
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
