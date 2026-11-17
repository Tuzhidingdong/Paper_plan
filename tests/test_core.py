from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from era_core import make_region_anchor, register_anchor, register_named_sample


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_region_anchor_is_deterministic(self):
        args = ("a" * 64, 3, [0.1, 0.2, 0.8, 0.9], "b" * 64)
        self.assertEqual(make_region_anchor(*args), make_region_anchor(*args))
        self.assertNotEqual(make_region_anchor(*args), make_region_anchor(args[0], 3, [0.1, 0.2, 0.7, 0.9], args[3]))

    def test_anchor_registry_reuses_id(self):
        first = register_anchor(self.workspace, "REG", "region-abc", "region", {"page": 1})
        second = register_anchor(self.workspace, "REG", "region-abc", "region", {"page": 1})
        other = register_anchor(self.workspace, "REG", "region-def", "region", {"page": 2})
        self.assertEqual(first, second)
        self.assertEqual(first, "REG001")
        self.assertEqual(other, "REG002")

    def test_named_sample_is_idempotent_for_same_alias_and_source(self):
        first = register_named_sample(self.workspace, "Sample A", "P003")
        second = register_named_sample(self.workspace, " sample   a ", "P003")
        third = register_named_sample(self.workspace, "Sample A", "P008")
        self.assertEqual(first, second)
        self.assertNotEqual(first, third)


if __name__ == "__main__":
    unittest.main()
