from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from compile_prompt_context import compile_context
from test_validation import sample_bundle


class ContextCompilerTests(unittest.TestCase):
    def test_context_keeps_scientific_caveats(self):
        context = compile_context(sample_bundle())
        self.assertIn("Visual_Estimate/Medium", context)
        self.assertIn("Trend_Only", context)
        self.assertIn("Image-derived estimate: state reading basis, confidence and figure-resolution limits", context)
        self.assertIn("p1", context)


if __name__ == "__main__":
    unittest.main()
