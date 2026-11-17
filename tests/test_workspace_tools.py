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

from era_core import atomic_write_json, load_json, workspace_paths


class WorkspaceToolTests(unittest.TestCase):
    def run_script(self, name: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *map(str, args)],
            capture_output=True, text=True,
        )

    def test_planning_id_and_entity_upsert_use_registry_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            init = self.run_script("init_planning_bundles.py", "--workspace", str(workspace))
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)

            allocate = self.run_script(
                "assign_planning_ids.py", "--workspace", str(workspace),
                "literature", "--anchor-key", "doi:10.1234/example",
            )
            self.assertEqual(allocate.returncode, 0, allocate.stdout + allocate.stderr)
            entity_id = json.loads(allocate.stdout)["entity_id"]

            snippet_allocate = self.run_script(
                "assign_planning_ids.py", "--workspace", str(workspace),
                "literature-snippet", "--anchor-key", "abstract:doi:10.1234/example:sentence-1",
            )
            self.assertEqual(snippet_allocate.returncode, 0, snippet_allocate.stdout + snippet_allocate.stderr)
            snippet_id = json.loads(snippet_allocate.stdout)["entity_id"]

            record_path = Path(tmp) / "literature.json"
            record_path.write_text(json.dumps({
                "literature_id": entity_id,
                "title": "Example paper",
                "access_level": "ABSTRACT_VERIFIED",
                "abstract": "An inspected abstract.",
                "source_api": ["Crossref"],
                "evidence_snippets": [{
                    "snippet_id": snippet_id, "text": "An abstract sentence.",
                    "source_location": "Abstract", "scope": "ABSTRACT",
                }],
            }), encoding="utf-8")
            upsert = self.run_script(
                "upsert_planning_entity.py",
                "--workspace", str(workspace),
                "--kind", "literature",
                "--entity-json", str(record_path),
                "--reason", "Register verified bibliographic metadata",
            )
            self.assertEqual(upsert.returncode, 0, upsert.stdout + upsert.stderr)
            bundle = load_json(workspace_paths(workspace)["state"] / "literature_bundle.json")
            self.assertIn(entity_id, bundle["literature_records"])
            history = workspace_paths(workspace)["history"] / "planning_entity_history.jsonl"
            self.assertTrue(history.is_file())
            event = json.loads(history.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(event["entity_id"], entity_id)
            self.assertEqual(event["operation"], "CREATE")

    def test_upsert_rejects_non_registry_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.run_script("init_planning_bundles.py", "--workspace", str(workspace))
            item = Path(tmp) / "fake.json"
            item.write_text(json.dumps({
                "literature_id": "LIT999", "title": "Fake",
                "access_level": "METADATA_ONLY", "source_api": [], "evidence_snippets": [],
            }), encoding="utf-8")
            run = self.run_script(
                "upsert_planning_entity.py", "--workspace", str(workspace),
                "--kind", "literature", "--entity-json", str(item), "--reason", "test",
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("not present in the Python ID registry", run.stderr)

    def test_capability_gate_blocks_unknown_and_passes_attested_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            blocked = self.run_script(
                "check_capability.py", "--workspace", str(workspace), "--task", "visual_inspection"
            )
            self.assertEqual(blocked.returncode, 3)
            self.assertIn("BLOCKED_BY_CAPABILITY", blocked.stdout)

            profile_path = Path(tmp) / "profile.json"
            profile_path.write_text(json.dumps({
                "provider": "test-provider",
                "model_id": "test-multimodal",
                "model_version": "test-2026-01",
                "capabilities": {
                    "native_multimodal": "yes",
                    "high_resolution_image_input": "yes",
                    "structured_json_output": "yes",
                    "scientific_reasoning": "yes",
                    "long_context_consistency": "yes",
                    "web_search_access": "yes",
                },
                "evidence_basis": ["CI fixture only"],
            }), encoding="utf-8")
            recorded = self.run_script(
                "record_capability_profile.py", "--workspace", str(workspace),
                "--profile-json", str(profile_path),
            )
            self.assertEqual(recorded.returncode, 0, recorded.stdout + recorded.stderr)
            passed = self.run_script(
                "check_capability.py", "--workspace", str(workspace), "--task", "visual_inspection"
            )
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            self.assertIn('"status": "PASS"', passed.stdout)

    def test_initialized_workspace_passes_all_bundle_schemas(self):
        try:
            import fitz
        except ImportError:
            self.skipTest("PyMuPDF is required")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf = root / "sample.pdf"
            doc = fitz.open()
            doc.new_page(width=300, height=400)
            doc.save(pdf)
            doc.close()
            workspace = root / "workspace"
            ingest = self.run_script("ingest_pdf.py", str(pdf), "--workspace", str(workspace))
            self.assertEqual(ingest.returncode, 0, ingest.stdout + ingest.stderr)
            init = self.run_script("init_planning_bundles.py", "--workspace", str(workspace))
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            validate = self.run_script("validate_bundle_schemas.py", "--workspace", str(workspace))
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

    def test_refresh_vector_candidates_updates_manifest_without_resetting_evidence(self):
        try:
            import fitz
        except ImportError:
            self.skipTest("PyMuPDF is required")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf = root / "sample.pdf"
            doc = fitz.open()
            page = doc.new_page(width=600, height=800)
            for index in range(60):
                y = 220 + index * 5
                page.draw_line((70, y), (530, y), color=(0, 0, 0))
                page.draw_line((70 + index * 5, 220), (70 + index * 5, 520), color=(0, 0, 0))
            doc.save(pdf)
            doc.close()

            workspace = root / "workspace"
            ingested = self.run_script(
                "ingest_pdf.py", str(pdf), "--workspace", str(workspace)
            )
            self.assertEqual(ingested.returncode, 0, ingested.stdout + ingested.stderr)

            paths = workspace_paths(workspace)
            bundle = load_json(paths["bundle"])
            bundle["findings"]["F999"] = {
                "finding_id": "F999", "description": "Do not delete existing evidence"
            }
            atomic_write_json(paths["bundle"], bundle)

            refreshed = self.run_script(
                "refresh_vector_candidates.py", "--workspace", str(workspace)
            )
            self.assertEqual(refreshed.returncode, 0, refreshed.stdout + refreshed.stderr)
            manifest = load_json(paths["manifest"])
            self.assertEqual(manifest["vector_detector_version"], "spatial-vector-cluster/0.2.0")
            self.assertTrue(manifest["pages"][0]["vector_or_text_figure_review"])
            bundle_after = load_json(paths["bundle"])
            self.assertIn("F999", bundle_after["findings"])


if __name__ == "__main__":
    unittest.main()
