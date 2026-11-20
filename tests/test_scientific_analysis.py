from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compile_prompt_context import compile_context
from prepare_scientific_analysis import (
    build_analysis_pack,
    discover_relationship_candidates,
    prepare_all,
)
from record_scientific_analysis import register_analysis, validate_record


def bundle_fixture():
    return {
        "source": {"file_name": "source.pdf", "sha256": "a" * 64, "page_count": 4},
        "workspace_revision": "test",
        "regions": {
            "REG001": {"region_id": "REG001", "page_number": 1, "image_path": "assets/a.png", "pixel_sha256": "1" * 64},
            "REG002": {"region_id": "REG002", "page_number": 2, "image_path": "assets/b.png", "pixel_sha256": "2" * 64},
            "REG003": {"region_id": "REG003", "page_number": 3, "image_path": "assets/c.png", "pixel_sha256": "3" * 64},
            "REG004": {"region_id": "REG004", "page_number": 4, "image_path": "assets/unassigned.png", "pixel_sha256": "4" * 64},
        },
        "panels": {
            "PANEL001": {"panel_id": "PANEL001", "parent_region_id": "REG001", "label": "a",
                         "image_path": "assets/a1.png", "pixel_sha256": "5" * 64},
            "PANEL002": {"panel_id": "PANEL002", "parent_region_id": "REG001", "label": "b",
                         "image_path": "assets/a2.png", "pixel_sha256": "6" * 64},
        },
        "samples": {
            "S001": {"sample_id": "S001", "aliases": [{"alias": "Specimen A", "source_ref": "page-1"}],
                     "identity_status": "CONFIRMED"},
            "S002": {"sample_id": "S002", "aliases": [{"alias": "Specimen B", "source_ref": "page-2"}],
                     "identity_status": "CONFIRMED"},
        },
        "result_units": {
            "R001": {
                "result_id": "R001", "region_ids": ["REG001"], "panel_ids": ["PANEL001", "PANEL002"],
                "data_type": "readout-alpha", "data_origin": "Visual_Estimate",
                "visual_legibility": "High", "is_visual_estimate": True,
                "quantitative_permission": "Trend_Only", "epistemic_status": "Observed",
                "measurement_context": {"technique": "method-A", "measurement_group": "group-1",
                    "measurement_conditions": {"setting": "low"},
                    "sample_associations": [{"sample_id": "S001", "mapping_status": "CONFIRMED", "series_id": "trace-1"}]},
                "observations": [{"description": "Two series are shown.", "source_status": "Observed",
                                  "sample_id": "S001", "mapping_status": "CONFIRMED"}],
            },
            "R002": {
                "result_id": "R002", "region_ids": ["REG002"], "panel_ids": [],
                "data_type": "readout-alpha", "data_origin": "Exact_Table",
                "visual_legibility": "High", "is_visual_estimate": False,
                "quantitative_permission": "Exact_Values", "epistemic_status": "Observed",
                "measurement_context": {"technique": "method-A", "measurement_group": "group-1",
                    "measurement_conditions": {"setting": "high"},
                    "sample_associations": [{"sample_id": "S002", "mapping_status": "CONFIRMED"}]},
                "observations": [{"description": "A measured value is reported.", "source_status": "Observed",
                                  "numeric_value": 12.5, "unit": "unit-x"}],
            },
            "R003": {
                "result_id": "R003", "region_ids": ["REG003"], "panel_ids": [],
                "data_type": "readout-beta", "data_origin": "Qualitative_Observation",
                "visual_legibility": "Medium", "is_visual_estimate": False,
                "quantitative_permission": "Qualitative_Only", "epistemic_status": "Observed",
                "measurement_context": {"technique": "method-B", "measurement_group": "group-2",
                    "measurement_conditions": {"setting": "ambient"},
                    "sample_associations": [{"sample_id": "S001", "mapping_status": "CONFIRMED"}]},
                "observations": [{"description": "A second type of response is visible.", "source_status": "Observed"}],
            },
        },
        "findings": {}, "audit_records": [], "discrepancies": [],
        "visual_inspections": {}, "spectral_comparisons": {}, "scientific_analyses": {},
    }


def valid_record(request):
    ids = request["result_ids"]
    coverage = []
    observations = []
    for index, result_id in enumerate(ids):
        observation_id = f"OBS-{index+1}"
        region_id = bundle_fixture()["result_units"][result_id]["region_ids"][0]
        panel_ids = bundle_fixture()["result_units"][result_id]["panel_ids"]
        observations.append({
            "observation_id": observation_id,
            "description": f"Observed feature for {result_id}.",
            "epistemic_status": "Observed",
            "result_ids": [result_id],
            "evidence_refs": [{
                "result_id": result_id, "region_id": region_id,
                "panel_id": panel_ids[0] if panel_ids else None, "page_number": index+1
            }],
            "confidence": "Medium",
        })
        coverage.append({
            "result_id": result_id, "status": "ANALYZED",
            "observation_ids": [observation_id], "reason": ""
        })
    comparison = []
    if len(ids) >= 2:
        comparison = [{
            "comparison_id": "CMP-1", "question": "Do the measured responses differ?",
            "result_ids": ids[:2], "comparison_status": "PARTIALLY_COMPARABLE",
            "observation_ids": ["OBS-1", "OBS-2"],
            "evidence_refs": [
                {"result_id": ids[0], "region_id": bundle_fixture()["result_units"][ids[0]]["region_ids"][0],
                 "panel_id": None, "page_number": 1},
                {"result_id": ids[1], "region_id": bundle_fixture()["result_units"][ids[1]]["region_ids"][0],
                 "panel_id": None, "page_number": 2}
            ],
            "dimension_assessments": [{
                "dimension": "measurement settings", "status": "MISMATCHED",
                "left_or_group_values": ["low", "high"],
                "consequence": "Treat the difference as a condition-associated observation, not a direct like-for-like comparison."
            }],
            "quantitative_differences": [{
                "measurand": "reported readout",
                "values": [{"result_id": ids[0], "entity_or_group": "group-1", "value": 12.5,
                            "unit": "unit-x", "source_basis": "transcribed table", "precision_or_uncertainty": "printed precision"}],
                "direction_or_pattern": "one reported value is higher",
                "delta_or_effect_size": None,
                "interpretation_limit": "No replicate or uncertainty estimate supplied."
            }],
            "qualitative_differences": ["The visible response differs."],
            "conclusion": "A difference is visible, but the settings are not matched.",
            "limitations": ["Do not infer a causal effect from this comparison alone."]
        }]
    return {
        "analysis_id": request["analysis_id"],
        "analysis_mode": "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS",
        "analysis_status": "COMPLETE",
        "result_ids": ids,
        "summary": "The evidence set contains source-linked differences and one cross-method link.",
        "coverage": coverage,
        "observations": observations,
        "comparisons": comparison,
        "relationships": [{
            "relationship_type": "CONVERGENCE",
            "description": "Two evidence streams are compatible with the same broad pattern.",
            "result_ids": ids[:2],
            "observation_ids": [f"OBS-{i+1}" for i in range(min(2, len(ids)))],
            "strength": "WEAK", "causal_status": "NOT_ESTABLISHED", "limitations": ["Small evidence base."]
        }] if len(ids) >= 2 else [],
        "interpretations": [{
            "description": "A tentative interpretation.",
            "epistemic_status": "Hypothesized",
            "supporting_observation_ids": ["OBS-1"],
            "alternative_explanations": ["An unmeasured condition may explain the pattern."],
            "confidence": "Low", "limitations": ["Requires independent validation."]
        }],
        "contradictions": [],
        "candidate_scientific_implications": ["A candidate relationship merits targeted review."],
        "unresolved_questions": ["Are the conditions sufficiently matched?"],
        "limitations": ["Synthetic fixture only."]
    }


class TestGeneralScientificAnalysis(unittest.TestCase):
    def test_candidates_cover_shared_sample_measurement_group_signature_and_conditions(self):
        candidates = discover_relationship_candidates(bundle_fixture())
        pair_reasons = {tuple(item["result_ids"]): set(item["candidate_reasons"]) for item in candidates}
        self.assertIn(("R001", "R002"), pair_reasons)
        self.assertIn("SHARED_MEASUREMENT_GROUP", pair_reasons[("R001", "R002")])
        self.assertIn("SHARED_MEASUREMENT_SIGNATURE", pair_reasons[("R001", "R002")])
        self.assertIn(("R001", "R003"), pair_reasons)
        self.assertIn("SHARED_SAMPLE_ASSOCIATION", pair_reasons[("R001", "R003")])

    def test_prepare_all_assigns_every_result_and_preserves_unlinked_regions(self):
        index, packs = prepare_all(bundle_fixture(), Path("/workspace"), max_results_per_pack=2)
        assigned = [rid for pack in packs for rid in pack["result_ids"]]
        self.assertEqual(sorted(assigned), ["R001", "R002", "R003"])
        self.assertEqual(index["result_unit_count"], 3)
        self.assertEqual(index["unassigned_region_ids"], ["REG004"])
        self.assertEqual(index["coverage_map"].keys(), {"R001", "R002", "R003"})

    def test_cross_method_shared_sample_can_be_in_one_related_pack(self):
        index, packs = prepare_all(bundle_fixture(), Path("/workspace"), max_results_per_pack=10)
        pack_for = {rid: pack for pack in packs for rid in pack["result_ids"]}
        self.assertIs(pack_for["R001"], pack_for["R003"])
        cross_link = [
            item for item in pack_for["R001"]["candidate_relationships"]
            if item["result_ids"] == ["R001", "R003"]
        ]
        self.assertTrue(cross_link)
        self.assertFalse(cross_link[0]["relationship_is_confirmed"])

    def test_single_result_multiple_panels_keeps_all_original_assets(self):
        pack = build_analysis_pack(bundle_fixture(), Path("/workspace"), ["R001"], [], 1)
        paths = {asset["image_path"] for asset in pack["assets"]}
        self.assertEqual(paths, {"assets/a1.png", "assets/a2.png"})
        self.assertTrue(any("connected scientific dataset" in line for line in pack["instructions"]))

    def test_result_pack_is_domain_neutral_and_does_not_force_comparisons(self):
        pack = build_analysis_pack(bundle_fixture(), Path("/workspace"), ["R003"], [], 1)
        self.assertIn("NO_COMPARISON_APPLICABLE", str(pack["required_output"]))
        self.assertIn("candidate_relationships", pack)
        joined = " ".join(pack["instructions"]).casefold()
        self.assertNotIn("raman", joined)
        self.assertNotIn("ftir", joined)

    def test_recorder_persists_and_compiler_surfaces_relationships_and_coverage(self):
        bundle = bundle_fixture()
        _, packs = prepare_all(bundle, Path("/workspace"), max_results_per_pack=10)
        request = packs[0]
        record = valid_record(request)
        register_analysis(bundle, request, record)
        self.assertIn(request["analysis_id"], bundle["scientific_analyses"])
        context = compile_context(bundle)
        self.assertIn("General cross-result scientific analyses", context)
        self.assertIn("cross-method link", context)
        self.assertIn("MISMATCHED", context)
        self.assertIn("A tentative interpretation", context)

    def test_recorder_rejects_missing_result_coverage(self):
        bundle = bundle_fixture()
        _, packs = prepare_all(bundle, Path("/workspace"), max_results_per_pack=10)
        request = packs[0]
        record = valid_record(request)
        record["coverage"].pop()
        with self.assertRaisesRegex(ValueError, "coverage must account"):
            validate_record(bundle, request, record)

    def test_recorder_rejects_unrelated_source_panel(self):
        bundle = bundle_fixture()
        _, packs = prepare_all(bundle, Path("/workspace"), max_results_per_pack=10)
        request = packs[0]
        record = valid_record(request)
        record["observations"][0]["evidence_refs"][0]["panel_id"] = "PANEL999"
        with self.assertRaisesRegex(ValueError, "unrelated Panel"):
            validate_record(bundle, request, record)

    def test_recorder_rejects_comparison_outside_pack(self):
        bundle = bundle_fixture()
        _, packs = prepare_all(bundle, Path("/workspace"), max_results_per_pack=2)
        request = next(pack for pack in packs if len(pack["result_ids"]) >= 2)
        record = valid_record(request)
        record["comparisons"][0]["result_ids"] = ["R001", "R999"]
        with self.assertRaisesRegex(ValueError, "at least two Result Units"):
            validate_record(bundle, request, record)


if __name__ == "__main__":
    unittest.main()
