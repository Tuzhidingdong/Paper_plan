"""Synthetic V4.1 regression tests for evidence roles, comparability and handoff gates."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_manuscript_development import validate_package
from validate_planning import validate_bundles
try:
    from test_manuscript_development import valid_fixture
    from test_planning import base_bundles
except ImportError:  # package-style unittest discovery
    from tests.test_manuscript_development import valid_fixture
    from tests.test_planning import base_bundles

def add_numeric_ru(evidence):
    evidence["result_units"]["R002"]={"result_id":"R002","claim_role":"UNDECIDED",
        "observations":[{"numeric_value":12.5}],"measurement_definition":{"status":"PARTIAL"}}

def assessment(status="NOT_COMPARABLE"):
    return {"assessment_id":"CMP001","comparison_purpose":"Synthetic comparison",
        "comparison_entities":[{"entity_id":"S001","entity_type":"sample","label":"A"},
                               {"entity_id":"S002","entity_type":"sample","label":"B"}],
        "dimensions":[{"dimension":"condition","match_status":"UNKNOWN"}],
        "assessment_status":status,"limitations":["Missing comparison information"],
        "permitted_inference":"No conclusion beyond the assessed scope.",
        "prohibited_inference":["Do not infer contradiction from incomparability"]}

class EvidenceUseRoleTests(unittest.TestCase):
    def test_audit_target_not_gated_as_core(self):
        p,f,l,e=valid_fixture();add_numeric_ru(e)
        f["claims"]["C001"]["evidence_refs"]=[{"kind":"result_unit","id":"R002","evidence_role":"AUDIT_TARGET"}]
        out=validate_package(p,f,l,e)
        self.assertFalse(any("R002" in x and ("CORE" in x or "VERIFIED" in x) for x in out["errors"]),out["errors"])
    def test_legacy_reference_defaults_to_support(self):
        p,f,l,e=valid_fixture();add_numeric_ru(e)
        f["claims"]["C001"]["evidence_refs"]=[{"kind":"result_unit","id":"R002"}]
        out=validate_package(p,f,l,e)
        self.assertTrue(any("R002" in x and "CORE" in x for x in out["errors"]),out["errors"])
        self.assertTrue(any("R002" in x and "VERIFIED" in x for x in out["errors"]),out["errors"])
    def test_finding_audit_target_not_promoted_to_support(self):
        p,f,l,e=valid_fixture();add_numeric_ru(e)
        e["findings"]["F001"]={"finding_id":"F001","description":"Synthetic audit finding","epistemic_status":"Interpreted",
            "supporting_result_ids":[],"contradictory_result_ids":[],"audit_target_result_ids":["R002"],
            "alternative_explanations":["Alternative"]}
        f["claims"]["C001"]["evidence_refs"]=[{"kind":"finding","id":"F001"}]
        out=validate_package(p,f,l,e)
        self.assertFalse(any("R002" in x and ("CORE" in x or "VERIFIED" in x) for x in out["errors"]),out["errors"])
    def test_contradictory_result_requires_verified_core_measurement(self):
        p,f,l,e=valid_fixture();add_numeric_ru(e)
        e["findings"]["F001"]={"finding_id":"F001","description":"Synthetic counter-evidence","epistemic_status":"Observed",
            "supporting_result_ids":[],"contradictory_result_ids":["R002"],"alternative_explanations":[]}
        f["claims"]["C001"]["evidence_refs"]=[{"kind":"finding","id":"F001"}]
        f["claims"]["C001"]["evidence_assessment"]="CONTRADICTED"
        out=validate_package(p,f,l,e)
        self.assertTrue(any("R002" in x and "claim_role CORE" in x for x in out["errors"]),out["errors"])
        self.assertTrue(any("R002" in x and "VERIFIED measurement definition" in x for x in out["errors"]),out["errors"])
        self.assertFalse(any("explicit CONTRADICTS_CLAIM" in x for x in out["errors"]),out["errors"])
    def test_incomparability_alone_cannot_mark_claim_contradicted(self):
        p,f,l,e=valid_fixture()
        f["claims"]["C001"]["evidence_assessment"]="CONTRADICTED"
        f["claims"]["C001"]["comparability_assessment_ids"]=["CMP001"]
        p["comparability_assessments"]["CMP001"]=assessment("NOT_COMPARABLE")
        out=validate_package(p,f,l,e)
        self.assertTrue(any("CONTRADICTED requires an explicit CONTRADICTS_CLAIM" in x for x in out["errors"]),out["errors"])

    def test_finding_reference_audit_role_overrides_supporting_child_list(self):
        p,f,l,e=valid_fixture();add_numeric_ru(e)
        e["findings"]["F001"]={"finding_id":"F001","description":"Synthetic audit finding","epistemic_status":"Interpreted",
            "supporting_result_ids":["R002"],"contradictory_result_ids":[],"audit_target_result_ids":[],
            "alternative_explanations":["Alternative"]}
        f["claims"]["C001"]["evidence_refs"]=[{"kind":"finding","id":"F001","evidence_role":"AUDIT_TARGET"}]
        out=validate_package(p,f,l,e)
        self.assertFalse(any("R002" in x and ("CORE" in x or "VERIFIED" in x) for x in out["errors"]),out["errors"])

class PanelAndComparabilityTests(unittest.TestCase):
    def test_not_assessable_status_supported(self):
        p,f,l,e=valid_fixture();p["comparability_assessments"]["CMP001"]=assessment("NOT_ASSESSABLE")
        out=validate_package(p,f,l,e);self.assertEqual(out["errors"],[],out["errors"])
    def test_shared_slot_without_dataset_scope_warned(self):
        p,f,l,e=valid_fixture();f2=dict(p["main_figures"]["FIG001"]);f2["figure_id"]="FIG002";f2["order"]=2
        f2["panels"]=[dict(p["main_figures"]["FIG001"]["panels"][0])]
        p["main_figures"]["FIG002"]=f2;p["storyline"]["STORY001"]["figure_ids"].append("FIG002")
        out=validate_package(p,f,l,e)
        self.assertTrue(any("reused across Panels" in x for x in out["warnings"]),out["warnings"])
    def test_shared_slot_with_distinct_scope_allowed(self):
        p,f,l,e=valid_fixture();f2=dict(p["main_figures"]["FIG001"]);f2["figure_id"]="FIG002";f2["order"]=2
        f2["panels"]=[dict(p["main_figures"]["FIG001"]["panels"][0])]
        p["main_figures"]["FIG001"]["panels"][0]["data_scope"]={"specimen_set":"A","condition_set":"baseline","timepoint_or_stage":"initial"}
        f2["panels"][0]["data_scope"]={"specimen_set":"B","condition_set":"treated","timepoint_or_stage":"final"}
        p["main_figures"]["FIG002"]=f2;p["storyline"]["STORY001"]["figure_ids"].append("FIG002")
        out=validate_package(p,f,l,e)
        self.assertFalse(any("reused across Panels" in x for x in out["warnings"]),out["warnings"])

class ExecutionDesignTests(unittest.TestCase):
    def test_agreement_design_requires_method_and_predeclared_boundary(self):
        p,f,l,e=valid_fixture()
        f["tasks"]["T001"]["execution_design"]={"readiness":"READY_FOR_SUPERVISOR_APPROVAL",
          "method_summary":"Paired comparison","required_inputs":[{"input":"Paired measurements","availability":"AVAILABLE"}],
          "raw_outputs":["Native files"],"qc_acceptance_criteria":["Calibration"],"responsible_role":"Analyst",
          "decision_owner":"Supervisor","independent_variables":["Method"],"controlled_variables":["Specimen"],
          "response_variables":["Paired measurement"],"groups_and_controls":["Reference"],
          "replicate_statistics_plan":"Predefined","uncertainty_plan":"Propagated uncertainty",
          "decision_framework":{"question_type":"AGREEMENT","primary_estimand":"Paired difference",
             "analysis_method":"Method comparison","agreement_method":None,"acceptance_boundary":None,
             "acceptance_boundary_basis":None,"outcome_rules":[]}}
        out=validate_package(p,f,l,e)
        self.assertTrue(any("AGREEMENT decision framework lacks" in x for x in out["errors"]),out["errors"])
    def test_execution_approval_requires_local_feasibility_and_available_inputs(self):
        p,f,l,e=valid_fixture();t=f["tasks"]["T001"];t["status"]="READY"
        t["execution_design"]={"readiness":"APPROVED_FOR_EXECUTION","local_feasibility_status":"UNASSESSED",
          "method_summary":"Defined method","required_inputs":[{"input":"Material","availability":"MISSING"}],
          "raw_outputs":["Native file"],"qc_acceptance_criteria":["QC"],"responsible_role":"Researcher",
          "decision_owner":"Supervisor","independent_variables":["Factor"],"controlled_variables":["Condition"],
          "response_variables":["Response"],"groups_and_controls":["Control"],"replicate_statistics_plan":"Defined",
          "uncertainty_plan":"Defined","safety_and_feasibility_notes":""}
        out=validate_package(p,f,l,e);msg=" ".join(out["errors"])
        self.assertIn("local_feasibility_status CONFIRMED",msg);self.assertIn("unavailable inputs",msg)
        self.assertIn("safety/feasibility review",msg)

class DependencyGateTests(unittest.TestCase):
    def test_approved_task_ignores_publication_only_prerequisite(self):
        e,l,r,f=base_bundles()
        f["tasks"]["T001"]["status"]="PLANNED"
        f["tasks"]["T002"]={"task_id":"T002","task_type":"EXPERIMENT","status":"READY","priority":"P0",
          "target_data_slot_ids":["DS001"],"expected_output":"Output","completion_criteria":"QC",
          "prerequisites":["T001"],"publication_prerequisite_ids":["T001"],
          "execution_design":{"readiness":"APPROVED_FOR_EXECUTION"}}
        out=validate_bundles(e,l,r,f)
        self.assertEqual(out["errors"],[],out["errors"])
        self.assertFalse(any("execution prerequisite T001 is not DONE" in x for x in out["warnings"]),out["warnings"])

    def test_approved_task_requires_execution_prerequisite_done(self):
        e,l,r,f=base_bundles()
        f["tasks"]["T001"]["status"]="PLANNED"
        f["tasks"]["T002"]={"task_id":"T002","task_type":"EXPERIMENT","status":"READY","priority":"P0",
          "target_data_slot_ids":["DS001"],"expected_output":"Output","completion_criteria":"QC",
          "prerequisites":["T001"],"execution_prerequisite_ids":["T001"],
          "execution_design":{"readiness":"APPROVED_FOR_EXECUTION"}}
        out=validate_bundles(e,l,r,f)
        self.assertTrue(any("execution prerequisite T001 is not DONE" in x for x in out["errors"]),out["errors"])


    def test_publication_prerequisite_does_not_block_ready_experiment(self):
        e,l,r,f=base_bundles();f["tasks"]["T002"]={"task_id":"T002","task_type":"EXPERIMENT","status":"READY",
          "priority":"P0","target_data_slot_ids":["DS001"],"expected_output":"Output","completion_criteria":"QC",
          "prerequisites":["T001"],"publication_prerequisite_ids":["T001"]}
        out=validate_bundles(e,l,r,f)
        self.assertFalse(any("execution prerequisite T001 is not DONE" in x for x in out["warnings"]),out["warnings"])
    def test_dependency_category_union_must_match(self):
        e,l,r,f=base_bundles();f["tasks"]["T002"]={"task_id":"T002","task_type":"EXPERIMENT","status":"PLANNED",
          "priority":"P0","target_data_slot_ids":["DS001"],"expected_output":"Output","completion_criteria":"QC",
          "prerequisites":["T001"],"execution_prerequisite_ids":[]}
        out=validate_bundles(e,l,r,f)
        self.assertTrue(any("prerequisites must equal the union" in x for x in out["errors"]),out["errors"])
    def test_lower_priority_execution_prerequisite_warned(self):
        e,l,r,f=base_bundles();f["tasks"]["T001"]["priority"]="P1"
        f["tasks"]["T002"]={"task_id":"T002","task_type":"EXPERIMENT","status":"PLANNED","priority":"P0",
          "target_data_slot_ids":["DS001"],"expected_output":"Output","completion_criteria":"QC",
          "prerequisites":["T001"],"execution_prerequisite_ids":["T001"]}
        out=validate_bundles(e,l,r,f)
        self.assertTrue(any("has lower priority" in x for x in out["warnings"]),out["warnings"])

if __name__=="__main__":
    unittest.main()
