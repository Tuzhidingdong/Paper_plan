"""Generic synthetic tests for structured Evidence Package interoperability."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from era_core import load_json, register_anchor, sha256_file, workspace_paths
from external_evidence import load_registry, validate_external_source_ref
from import_analysis_evidence import import_package
from compile_prompt_context import compile_context
from validate_evidence import validate as validate_evidence
from validate_bundle_schemas import validate_workspace as validate_schemas
from validate_planning import validate_bundles

FIXTURE = ROOT / "tests" / "fixtures" / "structured_evidence" / "evidence_package.json"


class StructuredEvidenceImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.workspace = self.root / "workspace"
        self.package_path = self.root / "evidence_package.json"
        self.package_path.write_bytes(FIXTURE.read_bytes())

    def import_fixture(self):
        return import_package(self.workspace, self.package_path)

    def external_ref(self, package_id="EV-SYNTHETIC-0001"):
        record = load_registry(self.workspace)["packages"][package_id]
        return {
            "source_system": "Data_analysis",
            "contract_id": "scientific-evidence-export",
            "contract_version": "1.0.0",
            "evidence_package_id": package_id,
            "package_sha256": record["package_sha256"],
            "entity_type": "xrd_report",
            "entity_id": "ANALYSIS-SYN-XRD-001",
            "analysis_run_id": "ANALYSIS-SYN-XRD-001",
            "operation_id": "xrd.profile",
            "source_sha256": "a" * 64,
            "summary_sha256": "b" * 64,
            "artifact_ids": [],
            "warnings": ["Synthetic peak-screening warning"],
            "limitations": ["No phase assignment in this fixture"],
        }

    def structured_result(self, result_id):
        return {
            "result_id": result_id,
            "evidence_source": "STRUCTURED_ANALYSIS",
            "region_ids": [],
            "panel_ids": [],
            "external_source_refs": [self.external_ref()],
            "data_type": "xrd_peak_screening",
            "data_origin": "Structured_Analysis",
            "visual_legibility": "NOT_APPLICABLE",
            "is_visual_estimate": False,
            "quantitative_permission": "Exact_Values",
            "epistemic_status": "Observed",
            "measurement_context": {"sample_associations": []},
            "observations": [{
                "description": "Synthetic peak position from imported report",
                "source_status": "Observed",
                "numeric_value": 10.0,
                "unit": "degree",
                "data_origin": "Structured_Analysis",
            }],
            "claim_role": "UNDECIDED",
            "uncertainty_note": "Synthetic fixture; not a scientific conclusion.",
        }

    def test_valid_package_imports_all_seven_categories_without_raw_data(self):
        result = self.import_fixture()
        self.assertEqual(result["status"], "IMPORTED")
        self.assertEqual(set(result["entity_counts"]), {
            "datasets", "battery_reports", "statistics_reports", "xrd_reports",
            "xanes_reports", "eis_reports", "cross_modal_reports",
        })
        self.assertTrue((self.workspace / result["package_path"]).is_file())
        self.assertEqual(load_json(workspace_paths(self.workspace)["bundle"])["result_units"], {})
        self.assertFalse((self.workspace / "raw").exists())
        registry_record = load_registry(self.workspace)["packages"]["EV-SYNTHETIC-0001"]
        self.assertEqual(registry_record["package_sha256"], result["package_sha256"])
        self.assertIn("raw source file bytes", " ".join(registry_record["unverifiable_fields"]))

    def test_reimport_same_package_is_idempotent_and_changed_content_is_rejected(self):
        first = self.import_fixture()
        second = self.import_fixture()
        self.assertEqual(second["status"], "ALREADY_IMPORTED")
        self.assertEqual(first["package_sha256"], second["package_sha256"])
        package = json.loads(self.package_path.read_text(encoding="utf-8"))
        package["question"] = "Changed synthetic contents"
        self.package_path.write_text(json.dumps(package), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "different SHA-256"):
            import_package(self.workspace, self.package_path)

    def test_unknown_contract_version_and_invalid_source_hash_are_rejected(self):
        package = json.loads(FIXTURE.read_text(encoding="utf-8"))
        package["contract_version"] = "9.0.0"
        self.package_path.write_text(json.dumps(package), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsupported contract_version"):
            import_package(self.workspace, self.package_path)
        package["contract_version"] = "1.0.0"
        package["datasets"][0]["source_sha256"] = "not-a-sha"
        self.package_path.write_text(json.dumps(package), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "schema"):
            import_package(self.workspace, self.package_path)

    def test_duplicate_entity_identity_is_rejected(self):
        package = json.loads(FIXTURE.read_text(encoding="utf-8"))
        package["datasets"].append(dict(package["datasets"][0], dataset_id="DATASET-SYN-001"))
        package["dataset_count"] = 2
        self.package_path.write_text(json.dumps(package), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate dataset_id"):
            import_package(self.workspace, self.package_path)

    def test_structured_result_unit_requires_real_external_reference_and_no_region(self):
        self.import_fixture()
        result_id = register_anchor(self.workspace, "R", "synthetic-structured-result", "result_slot", {})
        result = self.structured_result(result_id)
        bundle = load_json(workspace_paths(self.workspace)["bundle"])
        bundle["result_units"][result_id] = result
        errors, warnings = validate_evidence(bundle, self.workspace)
        self.assertFalse(errors, errors)
        self.assertEqual(warnings, [])

        missing_ref = dict(result)
        missing_ref["external_source_refs"] = []
        bundle["result_units"][result_id] = missing_ref
        errors, _ = validate_evidence(bundle, self.workspace)
        self.assertTrue(any("requires external_source_refs" in item for item in errors), errors)

    def test_pdf_region_requirement_remains_mandatory(self):
        result = self.structured_result("R001")
        result["evidence_source"] = "PDF_REPORT"
        result["external_source_refs"] = []
        result["data_origin"] = "Exact_Text"
        result["visual_legibility"] = "High"
        errors, _ = validate_evidence({
            "source": {"file_name": "synthetic.pdf", "sha256": "c" * 64, "page_count": 1},
            "regions": {}, "panels": {}, "samples": {}, "result_units": {"R001": result},
            "findings": {}, "audit_records": [],
        })
        self.assertTrue(any("requires at least one real PDF region_id" in item for item in errors), errors)

    def test_mixed_workspace_keeps_pdf_region_and_structured_source_separate(self):
        self.import_fixture()
        result_id = register_anchor(self.workspace, "R", "synthetic-mixed-result", "result_slot", {})
        region_id = register_anchor(self.workspace, "REG", "synthetic-page-region", "region", {})
        paths = workspace_paths(self.workspace)
        image_path = self.workspace / "extracted" / "regions" / "synthetic.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(b"synthetic-image")
        result = self.structured_result(result_id)
        result.update({
            "evidence_source": "MIXED",
            "region_ids": [region_id],
            "data_origin": "Structured_Analysis",
            "visual_legibility": "NOT_APPLICABLE",
            "source_location": "PDF p. 1; structured report xrd.profile",
        })
        bundle = load_json(paths["bundle"])
        bundle["source"] = {"file_name": "synthetic.pdf", "sha256": "c" * 64, "page_count": 1}
        bundle["regions"][region_id] = {
            "region_id": region_id, "anchor_key": "synthetic-page-region", "page_number": 1,
            "bbox_normalized": [0.1, 0.1, 0.9, 0.9],
            "image_path": "extracted/regions/synthetic.png", "pixel_sha256": "d" * 64,
            "triage_role": "REVIEW_CANDIDATE",
        }
        bundle["result_units"][result_id] = result
        errors, _ = validate_evidence(bundle, self.workspace)
        self.assertFalse(errors, errors)

    def test_structured_only_workspace_initializes_and_compiles_context(self):
        self.import_fixture()
        init = subprocess.run(
            [sys.executable, str(SCRIPTS / "init_planning_bundles.py"), "--workspace", str(self.workspace)],
            capture_output=True, text=True,
        )
        self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
        manifest = load_json(workspace_paths(self.workspace)["manifest"])
        self.assertIsNone(manifest["source_pdf"])
        self.assertEqual(manifest["external_sources"]["package_count"], 1)
        result_id = register_anchor(self.workspace, "R", "structured-schema-result", "result_slot", {})
        bundle = load_json(workspace_paths(self.workspace)["bundle"])
        bundle["result_units"][result_id] = self.structured_result(result_id)
        from era_core import atomic_write_json
        atomic_write_json(workspace_paths(self.workspace)["bundle"], bundle)
        schema_report = validate_schemas(self.workspace)
        self.assertEqual(schema_report["status"], "PASS", schema_report["errors"])
        evidence_errors, _ = validate_evidence(bundle, self.workspace)
        self.assertFalse(evidence_errors, evidence_errors)
        context = compile_context(bundle, self.workspace)
        self.assertIn("PDF source: not supplied", context)
        self.assertIn("ANALYSIS-SYN-XRD-001", context)
        self.assertIn("Synthetic peak-screening warning", context)
        self.assertIn("Imported Data_analysis Evidence Packages", context)
        self.assertIn("does not create Result Units or Claims", context)

    def test_external_reference_detects_tampered_package_and_identity_mismatch(self):
        self.import_fixture()
        ref = self.external_ref()
        self.assertEqual(validate_external_source_ref(self.workspace, ref), [])
        wrong_run = dict(ref, analysis_run_id="ANALYSIS-SYN-OTHER")
        self.assertTrue(any("AnalysisRun identity mismatch" in item
                            for item in validate_external_source_ref(self.workspace, wrong_run)))
        wrong_source_hash = dict(ref, source_sha256="c" * 64)
        self.assertTrue(any("hash not declared" in item
                            for item in validate_external_source_ref(self.workspace, wrong_source_hash)))
        wrong_summary_hash = dict(ref, summary_sha256="c" * 64)
        self.assertTrue(any("summary_sha256 mismatch" in item
                            for item in validate_external_source_ref(self.workspace, wrong_summary_hash)))
        package_file = self.workspace / load_registry(self.workspace)["packages"]["EV-SYNTHETIC-0001"]["package_path"]
        package_file.write_text("tampered", encoding="utf-8")
        self.assertTrue(any("hash does not match" in item for item in validate_external_source_ref(self.workspace, ref)))


    def test_python_id_reservation_and_result_unit_upsert_use_existing_registry(self):
        self.import_fixture()
        ref_path = self.root / "external_ref.json"
        ref_path.write_text(json.dumps(self.external_ref()), encoding="utf-8")
        allocated = subprocess.run(
            [sys.executable, str(SCRIPTS / "assign_entity_ids.py"),
             "--workspace", str(self.workspace), "result-slot",
             "--external-source-ref-json", str(ref_path), "--slot-index", "1"],
            capture_output=True, text=True,
        )
        self.assertEqual(allocated.returncode, 0, allocated.stdout + allocated.stderr)
        result_id = json.loads(allocated.stdout)["entity_id"]
        entity = self.structured_result(result_id)
        entity_path = self.root / "result_unit.json"
        entity_path.write_text(json.dumps(entity), encoding="utf-8")
        saved = subprocess.run(
            [sys.executable, str(SCRIPTS / "upsert_result_unit.py"),
             "--workspace", str(self.workspace), "--entity-json", str(entity_path),
             "--reason", "Synthetic agent-selected result"],
            capture_output=True, text=True,
        )
        self.assertEqual(saved.returncode, 0, saved.stdout + saved.stderr)
        persisted = load_json(workspace_paths(self.workspace)["bundle"])
        self.assertEqual(persisted["result_units"][result_id]["region_ids"], [])
        self.assertEqual(validate_evidence(persisted, self.workspace)[0], [])

    def test_result_unit_cannot_change_its_reserved_external_source(self):
        self.import_fixture()
        ref_path = self.root / "external_ref.json"
        original_ref = self.external_ref()
        ref_path.write_text(json.dumps(original_ref), encoding="utf-8")
        allocated = subprocess.run(
            [sys.executable, str(SCRIPTS / "assign_entity_ids.py"),
             "--workspace", str(self.workspace), "result-slot",
             "--external-source-ref-json", str(ref_path), "--slot-index", "2"],
            capture_output=True, text=True,
        )
        self.assertEqual(allocated.returncode, 0, allocated.stdout + allocated.stderr)
        result_id = json.loads(allocated.stdout)["entity_id"]
        changed_ref = dict(original_ref, entity_id="ANALYSIS-SYN-BAT-001",
                           analysis_run_id="ANALYSIS-SYN-BAT-001",
                           operation_id="battery.cycle_metrics")
        entity = self.structured_result(result_id)
        entity["external_source_refs"] = [changed_ref]
        entity_path = self.root / "wrong_result_unit.json"
        entity_path.write_text(json.dumps(entity), encoding="utf-8")
        saved = subprocess.run(
            [sys.executable, str(SCRIPTS / "upsert_result_unit.py"),
             "--workspace", str(self.workspace), "--entity-json", str(entity_path),
             "--reason", "Must reject mismatched source"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(saved.returncode, 0)
        self.assertIn("reserved for a different external source reference", saved.stderr)

    def test_same_raw_source_hash_is_not_treated_as_independent_in_data_unit(self):
        self.import_fixture()
        ref = self.external_ref()
        dataset_ref = {
            "source_system": "Data_analysis",
            "contract_id": "scientific-evidence-export",
            "contract_version": "1.0.0",
            "evidence_package_id": "EV-SYNTHETIC-0001",
            "entity_type": "dataset",
            "entity_id": "DATASET-SYN-001",
            "dataset_id": "DATASET-SYN-001",
            "source_sha256": "a" * 64,
            "summary_sha256": "b" * 64,
            "package_sha256": load_registry(self.workspace)["packages"]["EV-SYNTHETIC-0001"]["package_sha256"],
            "artifact_ids": ["ARTIFACT-SYN-001"],
        }
        evidence = {
            "source": {"sha256": "c" * 64},
            "result_units": {
                "R001": {
                    "evidence_source": "PDF_REPORT",
                    "source_lineage_ids": ["artifact:ARTIFACT-SYN-001"],
                },
                "R002": {"evidence_source": "STRUCTURED_ANALYSIS", "external_source_refs": [ref, dataset_ref]},
            },
            "findings": {}, "samples": {},
        }
        framework = {
            "claims": {}, "data_slots": {}, "tasks": {},
            "data_units": {
                "DU001": {
                    "data_unit_id": "DU001", "source_result_ids": ["R001", "R002"],
                    "derived": True, "transformation": "Synthetic merge",
                    "independence_group_id": "SRC-SYNTHETIC-SHARED",
                }
            },
        }
        report = validate_bundles(evidence, {}, {}, framework)
        self.assertTrue(any("treat them as one source lineage, not independent experiments" in item
                            for item in report["warnings"]), report["warnings"])


if __name__ == "__main__":
    unittest.main()
