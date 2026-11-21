from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from era_core import sha256_file
from plot_reading import (
    _vector_coordinate,
    apply_plot_reading_audit,
    fit_axis_calibration,
    map_axis_coordinate,
)


def _axis(values, label, unit):
    coordinates = [100.0, 500.0, 900.0]
    return {
        "label": label,
        "unit": unit,
        "scale": "LINEAR",
        "tick_anchors": [
            {"coordinate": coordinate, "value": value, "printed_label": str(value),
             "coordinate_uncertainty": 0.5, "value_uncertainty": 0.0}
            for coordinate, value in zip(coordinates, values)
        ],
    }


def _audit_fixture(workspace: Path, x_anchor_coordinates=None):
    image = workspace / "assets" / "plot.png"
    image.parent.mkdir(parents=True, exist_ok=True)
    image.write_bytes(b"synthetic-image-pixels")
    source_sha = sha256_file(image)
    request = {
        "plot_reading_audit_required": True,
        "result_ids": ["R001"],
        "assets": [{
            "image_path": "assets/plot.png",
            "asset_exists": True,
            "asset_sha256": source_sha,
            "pixel_width": 1000,
            "pixel_height": 1000,
            "result_id": "R001",
            "result_ids": ["R001"],
            "region_id": "REG001",
            "panel_id": None,
        }],
    }
    x_ticks = [
        {"coordinate": c, "value": v, "printed_label": str(v),
         "coordinate_uncertainty": 0.5, "value_uncertainty": 0.0}
        for c, v in zip(
            x_anchor_coordinates or [100.0, 500.0, 900.0],
            [0.0, 10.0, 20.0] if x_anchor_coordinates is None else [0.0, 10.0, 20.0]
        )
    ]
    record = {
        "plot_calibrations": [{
            "calibration_id": "PLOT-1",
            "result_id": "R001",
            "plot_type": "XY_LINE",
            "coordinate_system": "IMAGE_PIXEL",
            "coordinate_frame": {"width": 1000, "height": 1000},
            "plot_area": [100, 100, 900, 900],
            "evidence_refs": [{"result_id": "R001", "region_id": "REG001", "panel_id": None, "page_number": 1}],
            "x_axis": {"label": "Elapsed time", "unit": "s", "scale": "LINEAR", "tick_anchors": x_ticks},
            "y_axis": _axis([1.0, 0.5, 0.0], "Signal", "a.u."),
            "series": [{"series_id": "TRACE-A", "legend_label": "Trace A", "mapping_status": "CONFIRMED"}],
            "limitations": [],
        }],
        "plot_readings": [{
            "reading_id": "READ-1",
            "calibration_id": "PLOT-1",
            "result_id": "R001",
            "series_id": "TRACE-A",
            "feature_id": "SIG-1",
            "reading_role": "FEATURE_POSITION",
            "coordinate_source": "RASTER_IMAGE",
            "coordinate": {"x": 300.0, "y": 500.0},
            "coordinate_uncertainty": {"x": 1.0, "y": 1.0},
            "evidence_refs": [{"result_id": "R001", "region_id": "REG001", "panel_id": None, "page_number": 1}],
        }],
        "signal_features": [{
            "feature_id": "SIG-1",
            "result_id": "R001",
            "series_id": "TRACE-A",
            "feature_type": "OTHER",
            "description": "A plotted value used in a quantitative statement.",
            "series_label": "Trace A",
            "axis_context": {
                "x_axis_label": "Elapsed time", "x_axis_unit": "s", "x_axis_scale": "LINEAR",
                "y_axis_label": "Signal", "y_axis_unit": "a.u.", "y_axis_scale": "LINEAR",
                "normalization_basis": "displayed signal",
            },
            "position": {
                "value": 5.0, "unit": "s", "reading_basis": "CALIBRATED_PLOT_READING",
                "precision_or_uncertainty": "initial estimate",
                "plot_reading_ids": ["READ-1"],
                "calculation": {"operation": "DIRECT", "axis": "x"},
            },
            "evidence_refs": [{"result_id": "R001", "region_id": "REG001", "panel_id": None, "page_number": 1}],
        }],
    }
    return request, record


class TestPlotCalibration(unittest.TestCase):
    def test_linear_axis_maps_coordinates_and_propagates_graph_reading_uncertainty(self):
        fit = fit_axis_calibration(_axis([0.0, 10.0, 20.0], "x", "s"), "x_axis")
        self.assertEqual(fit["grade"], "HIGH")
        result = map_axis_coordinate(fit, 300.0, 1.0)
        self.assertAlmostEqual(result["value"], 5.0, places=8)
        self.assertGreater(result["uncertainty"], 0)
        self.assertEqual(result["permitted_use"], "QUANTITATIVE_PLOT_ESTIMATE")
        self.assertEqual(fit["tick_count"], 3)

    def test_log_axis_calibration_maps_in_log_space(self):
        axis = _axis([1.0, 10.0, 100.0], "x", "concentration")
        axis["scale"] = "LOG10"
        fit = fit_axis_calibration(axis, "x_axis")
        result = map_axis_coordinate(fit, 500.0, 1.0)
        self.assertAlmostEqual(result["value"], 10.0, places=6)

    def test_single_bad_tick_anchor_downgrades_calibration_quality(self):
        axis = _axis([0.0, 10.0, 30.0], "x", "s")
        fit = fit_axis_calibration(axis, "x_axis")
        self.assertEqual(fit["grade"], "LOW")
        self.assertGreater(fit["relative_max_transformed_residual"], 0.08)
        result = map_axis_coordinate(fit, 500.0, 1.0)
        self.assertEqual(result["permitted_use"], "TREND_ONLY")

    def test_nonmonotonic_tick_anchors_are_rejected(self):
        axis = _axis([0.0, 10.0, 5.0], "x", "s")
        with self.assertRaisesRegex(ValueError, "monotonically"):
            fit_axis_calibration(axis, "x_axis")

    def test_extrapolation_outside_tick_anchors_is_not_quantified(self):
        fit = fit_axis_calibration(_axis([0.0, 10.0, 20.0], "x", "s"), "x_axis")
        result = map_axis_coordinate(fit, 950.0, 1.0)
        self.assertIsNone(result["value"])
        self.assertEqual(result["permitted_use"], "NOT_QUANTIFIABLE")

    def test_plot_feature_value_is_recomputed_from_axis_calibration(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            request, record = _audit_fixture(workspace)
            apply_plot_reading_audit(request, record, workspace)
            reading = record["plot_readings"][0]
            self.assertAlmostEqual(reading["mapped_values"]["x"]["value"], 5.0, places=8)
            self.assertEqual(reading["reading_status"], "CALIBRATED_ESTIMATE")
            self.assertAlmostEqual(record["signal_features"][0]["position"]["value"], 5.0, places=8)
            self.assertIn("not experimental uncertainty", record["signal_features"][0]["position"]["precision_or_uncertainty"])

    def test_uncontrolled_free_text_basis_cannot_authorize_numeric_plot_value(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            request, record = _audit_fixture(workspace)
            record["signal_features"][0]["position"]["reading_basis"] = "visual estimate from the plot"
            with self.assertRaisesRegex(ValueError, "explicit evidence reading_basis"):
                apply_plot_reading_audit(request, record, workspace)

    def test_image_coordinate_frame_must_match_actual_source_asset_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            request, record = _audit_fixture(workspace)
            record["plot_calibrations"][0]["coordinate_frame"]["width"] = 999
            with self.assertRaisesRegex(ValueError, "does not match the source image"):
                apply_plot_reading_audit(request, record, workspace)

    def test_plot_feature_numeric_value_that_does_not_reproduce_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            request, record = _audit_fixture(workspace)
            record["signal_features"][0]["position"]["value"] = 8.0
            with self.assertRaisesRegex(ValueError, "does not reproduce"):
                apply_plot_reading_audit(request, record, workspace)

    def test_low_resolution_or_short_axis_cannot_support_numeric_feature(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            request, record = _audit_fixture(workspace, x_anchor_coordinates=[100.0, 110.0, 120.0])
            with self.assertRaisesRegex(ValueError, "trend-only"):
                apply_plot_reading_audit(request, record, workspace)

    def test_ambiguous_series_identity_downgrades_numeric_plot_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            request, record = _audit_fixture(workspace)
            record["plot_calibrations"][0]["series"][0]["mapping_status"] = "AMBIGUOUS"
            record["signal_features"][0]["position"]["value"] = None
            apply_plot_reading_audit(request, record, workspace)
            mapped = record["plot_readings"][0]["mapped_values"]["x"]
            self.assertIsNotNone(mapped["value"])
            self.assertEqual(mapped["permitted_use"], "TREND_ONLY")
            self.assertEqual(record["plot_readings"][0]["series_mapping_status"], "AMBIGUOUS")

    def test_reading_must_reference_a_declared_series(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            request, record = _audit_fixture(workspace)
            record["plot_readings"][0]["series_id"] = "UNKNOWN-TRACE"
            with self.assertRaisesRegex(ValueError, "series_id is not declared"):
                apply_plot_reading_audit(request, record, workspace)

    def test_vector_sidecar_uses_original_item_index_not_list_offset(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            sidecar = workspace / "vector.json"
            sidecar.write_text(json.dumps({
                "coordinate_frame": {"width": 200.0, "height": 100.0},
                "paths": [{
                    "path_id": "VEC-000001",
                    "items": [{"item_index": 7, "command": "l", "points": [[12.5, 15.0], [80.0, 60.0]]}],
                }],
            }), encoding="utf-8")
            asset = {
                "vector_geometry_path": "vector.json",
                "vector_geometry_sha256": sha256_file(sidecar),
            }
            point = _vector_coordinate(
                workspace, asset,
                {"path_id": "VEC-000001", "item_index": 7, "point_index": 0},
            )
            self.assertEqual(point, [12.5, 15.0])


if __name__ == "__main__":
    unittest.main()
