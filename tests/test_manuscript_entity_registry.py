from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class ManuscriptEntityRegistryTests(unittest.TestCase):
    def run_script(self, name: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)],
                              capture_output=True, text=True)

    def test_v4_entity_ids_are_reserved_and_upserted(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            init = self.run_script("init_planning_bundles.py", "--workspace", str(workspace))
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)

            allocation = self.run_script(
                "assign_planning_ids.py", "--workspace", str(workspace),
                "figure", "--anchor-key", "figure:central-evidence",
            )
            self.assertEqual(allocation.returncode, 0, allocation.stdout + allocation.stderr)
            entity_id = json.loads(allocation.stdout)["entity_id"]
            record = Path(tmp) / "figure.json"
            record.write_text(json.dumps({"figure_id": entity_id}), encoding="utf-8")

            upsert = self.run_script(
                "upsert_planning_entity.py", "--workspace", str(workspace),
                "--kind", "figure", "--entity-json", str(record),
                "--reason", "Persist a manuscript Figure entity",
            )
            self.assertEqual(upsert.returncode, 0, upsert.stdout + upsert.stderr)

            state = workspace / "state"
            bundle = json.loads((state / "manuscript_development_bundle.json").read_text(encoding="utf-8"))
            self.assertIn(entity_id, bundle["main_figures"])
            registry = json.loads((state / "id_registry.json").read_text(encoding="utf-8"))
            self.assertEqual(registry["entities"][entity_id]["entity_type"], "manuscript_figure")
            history = (state / "history" / "planning_entity_history.jsonl").read_text(encoding="utf-8")
            self.assertIn(entity_id, history)


if __name__ == "__main__":
    unittest.main()
