from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from prepare_visual_inspection import build_payload
from record_visual_inspection import register_inspection


def make_bundle():
    return {
        "regions": {
            "REG001": {
                "region_id": "REG001",
                "page_number": 2,
                "image_path": "extracted/regions/REG001.png",
                "pixel_sha256": "a" * 64,
                "caption_separation_status": "UNVERIFIED"
            }
        },
        "panels": {},
        "visual_inspections": {}
    }


def make_card(legibility="Medium"):
    return {
        "inspection_mode": "CAPTION_BLIND",
        "caption_text_included": False,
        "report_narrative_included": False,
        "visual_legibility": legibility,
        "data_origin": "Visual_Estimate",
        "quantitative_permission": "Trend_Only",
        "observations": [{"description": "possible trend", "source_status": "Observed"}],
        "instrument_checklist": {}
    }


class VisualInspectionTests(unittest.TestCase):
    def test_prepared_payload_contains_no_caption_or_narrative(self):
        payload = build_payload(make_bundle(), "REG001", "initial")
        self.assertIsNone(payload["caption_text"])
        self.assertIsNone(payload["report_narrative"])
        self.assertEqual(payload["inspection_mode"], "CAPTION_BLIND")
        self.assertIsNotNone(payload["crop_review_warning"])

    def test_initial_inspection_can_be_recorded_once(self):
        state = make_bundle()
        register_inspection(state, "REG001", "initial", make_card())
        with self.assertRaisesRegex(ValueError, "already recorded"):
            register_inspection(state, "REG001", "initial", make_card())

    def test_only_one_reinspection_is_allowed(self):
        state = make_bundle()
        register_inspection(state, "REG001", "initial", make_card())
        register_inspection(state, "REG001", "reinspection", make_card("Low"), "Check whether the x axis is legible")
        self.assertTrue(state["visual_inspections"]["REG001"]["locked"])
        with self.assertRaisesRegex(ValueError, "limit"):
            register_inspection(state, "REG001", "reinspection", make_card(), "Try again")

    def test_caption_inclusion_is_rejected(self):
        state = make_bundle()
        bad = make_card()
        bad["caption_text_included"] = True
        with self.assertRaisesRegex(ValueError, "cannot include caption"):
            register_inspection(state, "REG001", "initial", bad)


if __name__ == "__main__":
    unittest.main()
