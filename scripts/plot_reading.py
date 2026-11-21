#!/usr/bin/env python3
"""Calibrate and audit values read from plotted figures without inventing precision."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


NUMERIC_SCALES = {"LINEAR", "LOG", "LOG10"}
VALID_COORDINATE_SYSTEMS = {"IMAGE_PIXEL", "PDF_CROP_POINT"}


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite number")
    return result


def _linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float, float, list[float]]:
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((value - mean_x) ** 2 for value in xs)
    if denominator <= 0:
        raise ValueError("Axis tick coordinates must be distinct")
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
    intercept = mean_y - slope * mean_x
    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    rms = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    return slope, intercept, rms, residuals


def fit_axis_calibration(axis: dict[str, Any], axis_name: str) -> dict[str, Any]:
    scale = str(axis.get("scale") or "UNKNOWN").upper()
    if scale not in NUMERIC_SCALES:
        return {
            "axis": axis_name, "scale": scale, "status": "NOT_NUMERIC",
            "grade": "NOT_APPLICABLE", "tick_count": 0, "unit": axis.get("unit") or "UNKNOWN",
            "limitations": ["The axis is categorical or its numeric scale is unresolved."]
        }

    ticks = axis.get("tick_anchors")
    if not isinstance(ticks, list) or len(ticks) < 2:
        return {
            "axis": axis_name, "scale": scale, "status": "UNRESOLVED",
            "grade": "LOW", "tick_count": len(ticks or []), "unit": axis.get("unit") or "UNKNOWN",
            "limitations": ["At least two legible numeric tick anchors are required."]
        }

    coordinates: list[float] = []
    transformed_values: list[float] = []
    coordinate_sigmas: list[float] = []
    value_sigmas: list[float] = []
    raw_values: list[float] = []
    for index, tick in enumerate(ticks):
        coordinate = _number(tick.get("coordinate"), f"{axis_name}.tick_anchors[{index}].coordinate")
        value = _number(tick.get("value"), f"{axis_name}.tick_anchors[{index}].value")
        coordinate_sigma = _number(
            tick.get("coordinate_uncertainty"),
            f"{axis_name}.tick_anchors[{index}].coordinate_uncertainty"
        )
        if coordinate_sigma <= 0:
            raise ValueError(f"{axis_name}.tick_anchors[{index}].coordinate_uncertainty must be > 0")
        value_sigma = _number(tick.get("value_uncertainty", 0), f"{axis_name}.tick_anchors[{index}].value_uncertainty")
        if value_sigma < 0:
            raise ValueError(f"{axis_name}.tick_anchors[{index}].value_uncertainty cannot be negative")
        if scale in {"LOG", "LOG10"}:
            if value <= 0:
                raise ValueError(f"{axis_name} logarithmic tick values must be positive")
            transformed = math.log10(value)
            transformed_sigma = value_sigma / (value * math.log(10)) if value_sigma else 0.0
        else:
            transformed = value
            transformed_sigma = value_sigma
        coordinates.append(coordinate)
        transformed_values.append(transformed)
        coordinate_sigmas.append(coordinate_sigma)
        value_sigmas.append(transformed_sigma)
        raw_values.append(value)

    ordered = sorted(zip(coordinates, transformed_values), key=lambda item: item[0])
    deltas = [ordered[index + 1][1] - ordered[index][1] for index in range(len(ordered) - 1)]
    if any(abs(delta) <= 1e-12 for delta in deltas) or not (
        all(delta > 0 for delta in deltas) or all(delta < 0 for delta in deltas)
    ):
        raise ValueError(f"{axis_name} tick values must change monotonically with pixel/PDF coordinate")

    slope, intercept, residual_rms, residuals = _linear_fit(coordinates, transformed_values)
    span_coordinate = max(coordinates) - min(coordinates)
    span_transformed = max(transformed_values) - min(transformed_values)
    relative_rms = residual_rms / span_transformed if span_transformed > 0 else float("inf")
    max_abs_residual = max(abs(value) for value in residuals)
    relative_max_residual = max_abs_residual / span_transformed if span_transformed > 0 else float("inf")
    tick_coordinate_sigma = math.sqrt(sum(value * value for value in coordinate_sigmas) / len(coordinate_sigmas))
    tick_value_sigma = math.sqrt(sum(value * value for value in value_sigmas) / len(value_sigmas))

    if (
        len(ticks) >= 3 and span_coordinate >= 80
        and relative_rms <= 0.015 and relative_max_residual <= 0.03
    ):
        grade = "HIGH"
        status = "CALIBRATED"
        permitted_use = "QUANTITATIVE_PLOT_ESTIMATE"
    elif (
        len(ticks) >= 2 and span_coordinate >= 40
        and relative_rms <= 0.04 and relative_max_residual <= 0.08
    ):
        grade = "MODERATE"
        status = "CALIBRATED_WITH_LIMITS"
        permitted_use = "BOUNDED_PLOT_ESTIMATE"
    else:
        grade = "LOW"
        status = "LIMITED_CALIBRATION"
        permitted_use = "TREND_ONLY"

    limitations = []
    if len(ticks) == 2:
        limitations.append("Two-point affine calibration has no independent residual check.")
    if relative_rms > 0.015:
        limitations.append("Tick-anchor fit residual is not negligible relative to the axis range.")
    if span_coordinate < 80:
        limitations.append("The calibrated axis spans fewer than 80 coordinate units.")
    return {
        "axis": axis_name,
        "scale": scale,
        "status": status,
        "grade": grade,
        "permitted_use": permitted_use,
        "unit": axis.get("unit") or "UNKNOWN",
        "tick_count": len(ticks),
        "coordinate_span": span_coordinate,
        "coordinate_min": min(coordinates),
        "coordinate_max": max(coordinates),
        "value_span": max(raw_values) - min(raw_values),
        "transformed_rms_residual": residual_rms,
        "relative_rms_residual": relative_rms,
        "max_abs_transformed_residual": max_abs_residual,
        "relative_max_transformed_residual": relative_max_residual,
        "tick_coordinate_uncertainty_rms": tick_coordinate_sigma,
        "tick_value_uncertainty_rms_transformed": tick_value_sigma,
        "slope_transformed_per_coordinate": slope,
        "intercept_transformed": intercept,
        "limitations": limitations,
    }


def map_axis_coordinate(
    calibration: dict[str, Any], coordinate: float, coordinate_uncertainty: float
) -> dict[str, Any]:
    if calibration.get("status") not in {"CALIBRATED", "CALIBRATED_WITH_LIMITS", "LIMITED_CALIBRATION"}:
        return {"value": None, "uncertainty": None, "unit": calibration.get("unit", "UNKNOWN"),
                "permitted_use": "NOT_QUANTIFIABLE", "grade": calibration.get("grade", "LOW")}
    coordinate_min = float(calibration["coordinate_min"])
    coordinate_max = float(calibration["coordinate_max"])
    if not coordinate_min <= coordinate <= coordinate_max:
        return {
            "value": None,
            "uncertainty": None,
            "unit": calibration.get("unit", "UNKNOWN"),
            "permitted_use": "NOT_QUANTIFIABLE",
            "grade": calibration.get("grade", "LOW"),
            "limitations": ["Reading lies outside the calibrated tick-anchor range; extrapolation is prohibited."]
        }
    slope = float(calibration["slope_transformed_per_coordinate"])
    intercept = float(calibration["intercept_transformed"])
    transformed = slope * coordinate + intercept
    transformed_sigma = math.sqrt(
        (abs(slope) * coordinate_uncertainty) ** 2
        + (abs(slope) * float(calibration.get("tick_coordinate_uncertainty_rms", 0))) ** 2
        + float(calibration.get("transformed_rms_residual", 0)) ** 2
        + float(calibration.get("tick_value_uncertainty_rms_transformed", 0)) ** 2
    )
    if calibration["scale"] in {"LOG", "LOG10"}:
        value = 10 ** transformed
        lower = 10 ** (transformed - transformed_sigma)
        upper = 10 ** (transformed + transformed_sigma)
        uncertainty = max(value - lower, upper - value)
    else:
        value = transformed
        uncertainty = transformed_sigma
    return {
        "value": value,
        "uncertainty": uncertainty,
        "unit": calibration.get("unit", "UNKNOWN"),
        "permitted_use": calibration.get("permitted_use", "TREND_ONLY"),
        "grade": calibration.get("grade", "LOW"),
    }


def _bezier_point(points: list[list[float]], t: float) -> list[float]:
    if len(points) != 4:
        raise ValueError("A cubic vector path item must contain exactly four control points")
    one_minus = 1 - t
    weights = [one_minus ** 3, 3 * one_minus ** 2 * t, 3 * one_minus * t ** 2, t ** 3]
    return [
        sum(weights[index] * float(points[index][axis]) for index in range(4))
        for axis in (0, 1)
    ]


def _vector_coordinate(
    workspace: Path, asset: dict[str, Any], vector_ref: dict[str, Any]
) -> list[float]:
    geometry_path = asset.get("vector_geometry_path")
    geometry_hash = asset.get("vector_geometry_sha256")
    if not geometry_path or not geometry_hash:
        raise ValueError("Vector-path reading requires a retained vector geometry sidecar")
    path = Path(geometry_path)
    path = path if path.is_absolute() else workspace / path
    try:
        path.resolve().relative_to(workspace.resolve())
    except ValueError as exc:
        raise ValueError("Vector geometry sidecar must remain inside the workspace") from exc
    if not path.is_file():
        raise ValueError(f"Vector geometry sidecar is missing: {path}")
    from era_core import sha256_file
    if sha256_file(path) != geometry_hash:
        raise ValueError("Vector geometry sidecar SHA-256 mismatch")
    geometry = json.loads(path.read_text(encoding="utf-8"))
    paths = {item["path_id"]: item for item in geometry.get("paths", [])}
    path_id = vector_ref.get("path_id")
    if path_id not in paths:
        raise ValueError(f"Unknown vector path_id: {path_id}")
    items = paths[path_id].get("items", [])
    item_index = vector_ref.get("item_index")
    if not isinstance(item_index, int) or item_index < 0:
        raise ValueError("Vector path item_index must be a non-negative integer")
    item = next((entry for entry in items if entry.get("item_index") == item_index), None)
    if item is None:
        raise ValueError("Vector path item_index is not present in the sidecar")
    points = item.get("points", [])
    command = item.get("command")
    if command == "c":
        if "curve_t" not in vector_ref:
            raise ValueError("Cubic vector paths require curve_t rather than control-point selection")
        t = _number(vector_ref["curve_t"], "vector_ref.curve_t")
        if not 0 <= t <= 1:
            raise ValueError("vector_ref.curve_t must be between 0 and 1")
        return _bezier_point(points, t)
    point_index = vector_ref.get("point_index")
    if not isinstance(point_index, int) or point_index < 0 or point_index >= len(points):
        raise ValueError("Vector path point_index is outside the sidecar")
    return [float(points[point_index][0]), float(points[point_index][1])]


def _asset_for_calibration(request: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    refs = calibration.get("evidence_refs", [])
    result_id = calibration.get("result_id")
    for asset in request.get("assets", []):
        asset_result_ids = set(asset.get("result_ids", [])) | ({asset.get("result_id")} if asset.get("result_id") else set())
        if result_id not in asset_result_ids:
            continue
        for ref in refs:
            if ref.get("result_id") != result_id:
                continue
            if ref.get("region_id") and asset.get("region_id") != ref.get("region_id"):
                continue
            if ref.get("panel_id") and asset.get("panel_id") != ref.get("panel_id"):
                continue
            return asset
    raise ValueError(f"Plot calibration {calibration.get('calibration_id')} does not resolve to a requested source asset")


def _check_plot_area(calibration: dict[str, Any], width: float, height: float) -> tuple[float, float, float, float]:
    area = calibration.get("plot_area")
    if not isinstance(area, list) or len(area) != 4:
        raise ValueError("plot_area must be [x0, y0, x1, y1] in the declared coordinate system")
    x0, y0, x1, y1 = [_number(value, "plot_area") for value in area]
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError("plot_area is outside the declared coordinate frame or has zero area")
    return x0, y0, x1, y1


def apply_plot_reading_audit(
    request: dict[str, Any], record: dict[str, Any], workspace: Path | None
) -> None:
    """Validate source coordinates, fit axes, and write reproducible plot estimates."""
    if not request.get("plot_reading_audit_required"):
        return
    calibrations = record.get("plot_calibrations")
    readings = record.get("plot_readings")
    if not isinstance(calibrations, list) or not isinstance(readings, list):
        raise ValueError("plot_calibrations and plot_readings must both be explicit arrays (empty when not assessable)")
    if workspace is None and any(item.get("coordinate_source") == "VECTOR_GEOMETRY" for item in readings):
        raise ValueError("Workspace is required to verify vector geometry references")

    result_ids = set(request.get("result_ids", []))
    calibration_map: dict[str, dict[str, Any]] = {}
    calibration_assets: dict[str, dict[str, Any]] = {}
    for index, calibration in enumerate(calibrations):
        calibration_id = str(calibration.get("calibration_id") or "")
        if not calibration_id or calibration_id in calibration_map:
            raise ValueError(f"plot_calibrations[{index}] requires a unique calibration_id")
        if calibration.get("result_id") not in result_ids:
            raise ValueError(f"plot_calibrations[{index}] cites a Result Unit outside the prepared pack")
        refs = calibration.get("evidence_refs", [])
        if not refs or any(ref.get("result_id") != calibration.get("result_id") for ref in refs):
            raise ValueError(f"plot_calibrations[{index}] requires source evidence for its own Result Unit")
        asset = _asset_for_calibration(request, calibration)
        coordinate_system = calibration.get("coordinate_system")
        if coordinate_system not in VALID_COORDINATE_SYSTEMS:
            raise ValueError(f"plot_calibrations[{index}] has an invalid coordinate_system")
        frame = calibration.get("coordinate_frame") or {}
        width = _number(frame.get("width"), f"plot_calibrations[{index}].coordinate_frame.width")
        height = _number(frame.get("height"), f"plot_calibrations[{index}].coordinate_frame.height")
        if width <= 0 or height <= 0:
            raise ValueError("coordinate_frame width and height must be positive")
        if coordinate_system == "IMAGE_PIXEL":
            expected_width = asset.get("pixel_width")
            expected_height = asset.get("pixel_height")
            if expected_width is None or expected_height is None:
                raise ValueError("IMAGE_PIXEL calibration is blocked because the actual source-image dimensions are unavailable")
            if int(expected_width) != int(width):
                raise ValueError("IMAGE_PIXEL coordinate_frame.width does not match the source image")
            if int(expected_height) != int(height):
                raise ValueError("IMAGE_PIXEL coordinate_frame.height does not match the source image")
        if coordinate_system == "PDF_CROP_POINT":
            geometry_path = asset.get("vector_geometry_path")
            if not geometry_path:
                raise ValueError("PDF_CROP_POINT calibration requires a vector geometry sidecar")
            path = Path(geometry_path)
            path = path if path.is_absolute() else (workspace or Path.cwd()) / path
            try:
                path.resolve().relative_to((workspace or Path.cwd()).resolve())
            except ValueError as exc:
                raise ValueError("Vector geometry sidecar must remain inside the workspace") from exc
            if not path.is_file() or not asset.get("vector_geometry_sha256"):
                raise ValueError("Vector geometry sidecar is missing or unhashed")
            from era_core import sha256_file
            if sha256_file(path) != asset["vector_geometry_sha256"]:
                raise ValueError("Vector geometry sidecar SHA-256 mismatch")
            geometry = json.loads(path.read_text(encoding="utf-8"))
            geom_frame = geometry.get("coordinate_frame", {})
            if abs(float(geom_frame.get("width", -1)) - width) > 0.01 or abs(float(geom_frame.get("height", -1)) - height) > 0.01:
                raise ValueError("PDF vector coordinate_frame does not match geometry sidecar")
        plot_area = _check_plot_area(calibration, width, height)
        for axis_name in ("x_axis", "y_axis"):
            axis = calibration.get(axis_name)
            if not isinstance(axis, dict):
                raise ValueError(f"plot_calibrations[{index}] requires {axis_name}")
            fit = fit_axis_calibration(axis, axis_name)
            minimum_sigma = 0.5 if coordinate_system == "IMAGE_PIXEL" else 0.01
            for tick_index, tick in enumerate(axis.get("tick_anchors", []) or []):
                coordinate = _number(tick.get("coordinate"), f"{axis_name}.tick_anchors[{tick_index}].coordinate")
                coordinate_sigma = _number(
                    tick.get("coordinate_uncertainty"),
                    f"{axis_name}.tick_anchors[{tick_index}].coordinate_uncertainty"
                )
                if coordinate_sigma < minimum_sigma:
                    raise ValueError(
                        f"{axis_name} tick-anchor coordinate uncertainty is below the minimum resolvable {coordinate_system} increment"
                    )
                low, top, right, bottom = plot_area
                min_coord, max_coord = (low, right) if axis_name == "x_axis" else (top, bottom)
                if not min_coord <= coordinate <= max_coord:
                    raise ValueError(f"{axis_name} tick anchor lies outside plot_area")
            calibration.setdefault("calibration_qc", {})[axis_name] = fit
        grades = [calibration["calibration_qc"][axis]["grade"] for axis in ("x_axis", "y_axis")
                  if calibration["calibration_qc"][axis].get("status") != "NOT_NUMERIC"]
        rank = {"HIGH": 3, "MODERATE": 2, "LOW": 1, "NOT_APPLICABLE": 0}
        overall = min(grades, key=lambda item: rank[item]) if grades else "NOT_APPLICABLE"
        calibration["calibration_qc"]["overall_grade"] = overall
        calibration["calibration_qc"]["coordinate_system"] = coordinate_system
        calibration["calibration_qc"]["limitations"] = list(calibration.get("limitations", []))
        calibration_map[calibration_id] = calibration
        calibration_assets[calibration_id] = asset

    feature_lookup = {
        item.get("feature_id"): item
        for item in record.get("signal_features", [])
        if item.get("feature_id")
    }
    reading_map: dict[str, dict[str, Any]] = {}
    for index, reading in enumerate(readings):
        reading_id = str(reading.get("reading_id") or "")
        if not reading_id or reading_id in reading_map:
            raise ValueError(f"plot_readings[{index}] requires a unique reading_id")
        calibration_id = reading.get("calibration_id")
        calibration = calibration_map.get(calibration_id)
        if calibration is None:
            raise ValueError(f"plot_readings[{index}] references an unknown calibration_id")
        if reading.get("result_id") != calibration.get("result_id"):
            raise ValueError(f"plot_readings[{index}] Result Unit does not match its calibration")
        refs = reading.get("evidence_refs", [])
        if not refs or any(ref.get("result_id") != reading.get("result_id") for ref in refs):
            raise ValueError(f"plot_readings[{index}] requires source refs for its Result Unit")
        series_entries = calibration.get("series", [])
        series_map = {item.get("series_id"): item for item in series_entries if item.get("series_id")}
        if not series_map:
            raise ValueError(f"plot_calibrations[{calibration_id}] must declare the plotted series before point readings are used")
        series_entry = series_map.get(reading.get("series_id"))
        if series_entry is None:
            raise ValueError(f"plot_readings[{index}] series_id is not declared in the calibration")
        series_status = series_entry.get("mapping_status", "UNRESOLVED")
        if series_status not in {"CONFIRMED", "PROBABLE", "AMBIGUOUS", "UNRESOLVED"}:
            raise ValueError(f"plot_readings[{index}] has an invalid series mapping status")
        reading["series_mapping_status"] = series_status
        feature_id = reading.get("feature_id")
        if reading.get("reading_role") in {"FEATURE_POSITION", "FEATURE_EDGE"} and not feature_id:
            raise ValueError(f"plot_readings[{index}] feature positions/edges must identify the signal feature they measure")
        if feature_id:
            linked_feature = feature_lookup.get(feature_id)
            if linked_feature is None or linked_feature.get("result_id") != reading.get("result_id"):
                raise ValueError(f"plot_readings[{index}] feature_id is unknown or belongs to another Result Unit")
            if linked_feature.get("series_id") and linked_feature.get("series_id") != reading.get("series_id"):
                raise ValueError(f"plot_readings[{index}] series_id does not match the cited signal feature")
        coordinate_source = reading.get("coordinate_source")
        coordinate_system = calibration.get("coordinate_system")
        if coordinate_source == "VECTOR_GEOMETRY":
            if coordinate_system != "PDF_CROP_POINT":
                raise ValueError("VECTOR_GEOMETRY reading requires PDF_CROP_POINT calibration")
            if workspace is None:
                raise ValueError("Workspace is required for VECTOR_GEOMETRY readings")
            coordinate = _vector_coordinate(workspace, calibration_assets[calibration_id], reading.get("vector_ref") or {})
            reading["coordinate"] = {"x": coordinate[0], "y": coordinate[1]}
        elif coordinate_source == "RASTER_IMAGE":
            if coordinate_system != "IMAGE_PIXEL":
                raise ValueError("RASTER_IMAGE reading requires IMAGE_PIXEL calibration")
            coordinate = reading.get("coordinate") or {}
            coordinate = [
                _number(coordinate.get("x"), f"plot_readings[{index}].coordinate.x"),
                _number(coordinate.get("y"), f"plot_readings[{index}].coordinate.y"),
            ]
        else:
            raise ValueError(f"plot_readings[{index}] coordinate_source is invalid")
        uncertainty = reading.get("coordinate_uncertainty") or {}
        sigma_x = _number(uncertainty.get("x"), f"plot_readings[{index}].coordinate_uncertainty.x")
        sigma_y = _number(uncertainty.get("y"), f"plot_readings[{index}].coordinate_uncertainty.y")
        minimum_sigma = 0.5 if coordinate_system == "IMAGE_PIXEL" else 0.01
        if sigma_x < minimum_sigma or sigma_y < minimum_sigma:
            raise ValueError(
                f"Coordinate reading uncertainty must be at least {minimum_sigma:g} in {coordinate_system}; "
                "include line thickness/trace ambiguity and avoid sub-pixel certainty"
            )
        x0, y0, x1, y1 = calibration["plot_area"]
        if not (x0 <= coordinate[0] <= x1 and y0 <= coordinate[1] <= y1):
            raise ValueError(f"plot_readings[{index}] lies outside its plot_area")
        x_fit = calibration["calibration_qc"]["x_axis"]
        y_fit = calibration["calibration_qc"]["y_axis"]
        mapped_x = map_axis_coordinate(x_fit, coordinate[0], sigma_x)
        mapped_y = map_axis_coordinate(y_fit, coordinate[1], sigma_y)
        if series_status != "CONFIRMED":
            for mapped in (mapped_x, mapped_y):
                if mapped.get("value") is not None:
                    mapped["permitted_use"] = "TREND_ONLY"
                    mapped.setdefault("limitations", []).append(
                        f"Plotted series identity is {series_status}; numeric comparison is blocked."
                    )
        reading["mapped_values"] = {"x": mapped_x, "y": mapped_y}
        reading["reading_status"] = (
            "CALIBRATED_ESTIMATE"
            if any(item.get("permitted_use") in {"QUANTITATIVE_PLOT_ESTIMATE", "BOUNDED_PLOT_ESTIMATE"}
                   for item in (mapped_x, mapped_y) if item.get("value") is not None)
            else "TREND_ONLY_OR_UNRESOLVED"
        )
        reading_map[reading_id] = reading

    for index, feature in enumerate(record.get("signal_features", [])):
        result_id = feature.get("result_id")
        for label in ("position", "width", "intensity", "area"):
            estimate = feature.get(label) or {}
            if estimate.get("value") is None:
                continue
            basis = str(estimate.get("reading_basis") or "").strip().upper()
            direct_bases = {
                "EXACT_SOURCE_DATA", "EXACT_TEXT", "EXACT_TABLE",
                "PRINTED_FIGURE_VALUE", "DERIVED_FROM_EXPLICIT_VALUES"
            }
            if basis == "CALIBRATED_PLOT_READING":
                ids = estimate.get("plot_reading_ids") or feature.get("plot_reading_ids") or []
                if not ids or any(read_id not in reading_map for read_id in ids):
                    raise ValueError(f"signal_features[{index}].{label} visual numeric estimate must cite plot_reading_ids")
                if any(reading_map[read_id].get("result_id") != result_id for read_id in ids):
                    raise ValueError(f"signal_features[{index}].{label} plot_reading_ids cite another Result Unit")
                if any(reading_map[read_id].get("feature_id") != feature.get("feature_id") for read_id in ids):
                    raise ValueError(f"signal_features[{index}].{label} plot readings must cite this exact feature_id")
                reading_series = {reading_map[read_id].get("series_id") for read_id in ids}
                if len(reading_series) != 1 or None in reading_series:
                    raise ValueError(f"signal_features[{index}].{label} readings must belong to one identified plotted series")
                resolved_series = next(iter(reading_series))
                if feature.get("series_id") and feature.get("series_id") != resolved_series:
                    raise ValueError(f"signal_features[{index}].{label} plotted series does not match the feature's series_id")
                feature["series_id"] = resolved_series
                calculation = estimate.get("calculation") or {}
                operation = calculation.get("operation", "DIRECT")
                axis = calculation.get("axis", "x" if label in {"position", "width"} else "y")
                if axis not in {"x", "y"} or operation not in {"DIRECT", "DIFFERENCE"}:
                    raise ValueError(f"signal_features[{index}].{label} requires DIRECT or DIFFERENCE with axis x/y")
                required_count = 1 if operation == "DIRECT" else 2
                if len(ids) != required_count:
                    raise ValueError(f"signal_features[{index}].{label} {operation} requires {required_count} plot_reading_ids")
                mapped = [reading_map[read_id]["mapped_values"][axis] for read_id in ids]
                if any(item.get("value") is None or item.get("permitted_use") == "TREND_ONLY" for item in mapped):
                    raise ValueError(f"signal_features[{index}].{label} cannot use an unresolved/trend-only axis calibration")
                calculated = mapped[0]["value"] if operation == "DIRECT" else mapped[1]["value"] - mapped[0]["value"]
                uncertainties = [item.get("uncertainty") or 0.0 for item in mapped]
                tolerance = max(math.sqrt(sum(value * value for value in uncertainties)), abs(calculated) * 1e-6, 1e-9)
                reported = _number(estimate.get("value"), f"signal_features[{index}].{label}.value")
                if abs(reported - calculated) > tolerance:
                    raise ValueError(
                        f"signal_features[{index}].{label} does not reproduce from plot_readings "
                        f"(reported={reported}, calculated={calculated}, tolerance={tolerance})"
                    )
                expected_unit = str(mapped[0].get("unit") or "UNKNOWN").strip().casefold().replace("⁻¹", "-1").replace(" ", "")
                declared_unit = str(estimate.get("unit") or "UNKNOWN").strip().casefold().replace("⁻¹", "-1").replace(" ", "")
                if expected_unit not in {"unknown", ""} and declared_unit != expected_unit:
                    raise ValueError(
                        f"signal_features[{index}].{label} unit {estimate.get('unit')} does not match calibrated axis unit {mapped[0].get('unit')}"
                    )
                calculation["recomputed_value"] = calculated
                calculation["recomputed_tolerance"] = tolerance
                estimate["value"] = calculated
                estimate["precision_or_uncertainty"] = (
                    f"coordinate-calibrated graph-reading uncertainty ±{tolerance:g} {mapped[0].get('unit', '')}; "
                    "not experimental uncertainty"
                )
                estimate["calculation"] = calculation
                estimate["plot_reading_ids"] = ids
            elif basis not in direct_bases:
                raise ValueError(
                    f"signal_features[{index}].{label} numeric value requires an explicit evidence reading_basis; "
                    "use CALIBRATED_PLOT_READING with coordinates or an exact source/text/table basis"
                )
        feature["plot_reading_ids"] = list(dict.fromkeys(
            read_id for label in ("position", "width", "intensity", "area")
            for read_id in (feature.get(label) or {}).get("plot_reading_ids", [])
        ))

    for index, comparison in enumerate(record.get("signal_comparisons", [])):
        quantified = comparison.get("quantified_change") or {}
        if quantified.get("value") is None:
            continue
        basis = str(quantified.get("source_basis") or "").strip().upper()
        direct_bases = {
            "EXACT_SOURCE_DATA", "EXACT_TEXT", "EXACT_TABLE",
            "PRINTED_FIGURE_VALUE", "DERIVED_FROM_EXPLICIT_VALUES"
        }
        if basis == "CALIBRATED_PLOT_READING":
            ids = quantified.get("plot_reading_ids") or []
            if len(ids) < 2 or any(read_id not in reading_map for read_id in ids):
                raise ValueError(f"signal_comparisons[{index}] visual quantified_change must cite at least two plot_reading_ids")
            if any(reading_map[read_id].get("result_id") not in comparison.get("result_ids", []) for read_id in ids):
                raise ValueError(f"signal_comparisons[{index}] plot_reading_ids cite a Result Unit outside the comparison")
            features_by_id = {
                item.get("feature_id"): item for item in record.get("signal_features", [])
            }
            comparison_feature_ids = comparison.get("feature_ids", [])
            expected_pairs = {
                (features_by_id[feature_id].get("result_id"), features_by_id[feature_id].get("series_id"))
                for feature_id in comparison_feature_ids
                if feature_id in features_by_id
            }
            reading_pairs = {
                (reading_map[read_id].get("result_id"), reading_map[read_id].get("series_id"))
                for read_id in ids
            }
            reading_feature_ids = {reading_map[read_id].get("feature_id") for read_id in ids}
            if reading_feature_ids != set(comparison_feature_ids):
                raise ValueError(
                    f"signal_comparisons[{index}] plotted readings must map one-to-one to the cited feature IDs"
                )
            if not expected_pairs or not reading_pairs.issubset(expected_pairs) or not expected_pairs.issubset(reading_pairs):
                raise ValueError(
                    f"signal_comparisons[{index}] plot readings must represent every cited feature's Result Unit and series"
                )
            calc = quantified.get("calculation") or {}
            operation = calc.get("operation")
            axis = calc.get("axis")
            if operation not in {"DIFFERENCE", "RATIO", "PERCENT_CHANGE"} or axis not in {"x", "y"}:
                raise ValueError(f"signal_comparisons[{index}] requires a reproducible calculation operation and axis")
            comparability = comparison.get("comparability_status", "UNKNOWN")
            if comparability not in {"COMPARABLE", "PARTIALLY_COMPARABLE"}:
                raise ValueError(
                    f"signal_comparisons[{index}] cannot publish a quantified plot change when comparability is {comparability}"
                )
            expected_axis = {
                "POSITION_SHIFT": "x",
                "WIDTH_CHANGE": "x",
                "INTENSITY_CHANGE": "y",
            }.get(comparison.get("change_type"))
            if expected_axis and axis != expected_axis:
                raise ValueError(
                    f"signal_comparisons[{index}] {comparison.get('change_type')} must be calculated on axis {expected_axis}"
                )
            if comparison.get("change_type") == "AREA_CHANGE":
                raise ValueError("Visual signal area cannot be quantified without a reproducible integration method")
            related_calibrations = [
                calibration_map[reading_map[read_id]["calibration_id"]]
                for read_id in ids
            ]
            axis_units = {
                str(item[axis + "_axis"].get("unit") or "UNKNOWN").strip().casefold().replace("⁻¹", "-1").replace(" ", "")
                for item in related_calibrations
            }
            axis_scales = {str(item[axis + "_axis"].get("scale") or "UNKNOWN").upper() for item in related_calibrations}
            if len(axis_units) != 1 or "unknown" in axis_units or len(axis_scales) != 1:
                raise ValueError(
                    f"signal_comparisons[{index}] plotted values use incompatible or unresolved axis units/scales"
                )
            if axis == "y" and comparison.get("change_type") in {"INTENSITY_CHANGE"}:
                features_by_id = {
                    item.get("feature_id"): item for item in record.get("signal_features", [])
                }
                normalizations = {
                    str((features_by_id.get(feature_id, {}).get("axis_context") or {}).get("normalization_basis") or "UNKNOWN").strip().casefold()
                    for feature_id in comparison.get("feature_ids", [])
                }
                normalization = next(iter(normalizations)) if len(normalizations) == 1 else "unknown"
                if normalization == "unknown" or any(
                    token in normalization
                    for token in ("offset", "independently scaled", "separately normalized", "auto-scaled", "unknown")
                ):
                    raise ValueError(
                        f"signal_comparisons[{index}] intensity values lack a common, absolute normalization basis; "
                        "vertical offsets or independent scaling block absolute intensity comparison"
                    )
            mapped = [reading_map[read_id]["mapped_values"][axis] for read_id in ids]
            if any(item.get("value") is None or item.get("permitted_use") == "TREND_ONLY" for item in mapped):
                raise ValueError(f"signal_comparisons[{index}] calculation axis is unresolved or trend-only")
            values = [item["value"] for item in mapped]
            if operation == "DIFFERENCE":
                calculated = values[-1] - values[0]
            elif operation == "RATIO":
                if values[0] == 0:
                    raise ValueError("Cannot calculate a ratio with a zero baseline")
                calculated = values[-1] / values[0]
            else:
                if values[0] == 0:
                    raise ValueError("Cannot calculate percent change from a zero baseline")
                calculated = (values[-1] - values[0]) / abs(values[0]) * 100.0
            reported = _number(quantified.get("value"), "quantified_change.value")
            uncertainty_start = reading_map[ids[0]]["mapped_values"][axis].get("uncertainty") or 0.0
            uncertainty_end = reading_map[ids[-1]]["mapped_values"][axis].get("uncertainty") or 0.0
            value_start, value_end = values[0], values[-1]
            if operation == "DIFFERENCE":
                propagated_uncertainty = math.sqrt(uncertainty_start ** 2 + uncertainty_end ** 2)
                expected_unit = next(iter(axis_units))
                declared_unit = str(quantified.get("unit") or "").strip().casefold().replace("⁻¹", "-1").replace(" ", "")
                if declared_unit != expected_unit:
                    raise ValueError(
                        f"signal_comparisons[{index}] difference unit does not match the calibrated axis unit"
                    )
            elif operation == "RATIO":
                propagated_uncertainty = math.sqrt(
                    (uncertainty_end / value_start) ** 2
                    + ((value_end * uncertainty_start) / (value_start ** 2)) ** 2
                )
                if str(quantified.get("unit") or "").strip().casefold() not in {"dimensionless", "1"}:
                    raise ValueError(f"signal_comparisons[{index}] ratio must use a dimensionless unit")
            else:
                propagated_uncertainty = 100.0 * math.sqrt(
                    (uncertainty_end / abs(value_start)) ** 2
                    + ((abs(value_end) * uncertainty_start) / (value_start ** 2)) ** 2
                )
                if str(quantified.get("unit") or "").strip().casefold() not in {"%", "percent"}:
                    raise ValueError(f"signal_comparisons[{index}] percent change must use '%' or 'percent'")
            tolerance = max(propagated_uncertainty, abs(calculated) * 1e-6, 1e-9)
            if abs(reported - calculated) > tolerance:
                raise ValueError(
                    f"signal_comparisons[{index}] reported change does not reproduce from plot_readings "
                    f"(reported={reported}, calculated={calculated}, tolerance={tolerance})"
                )
            quantified["calculation"]["recomputed_value"] = calculated
            quantified["calculation"]["recomputed_tolerance"] = tolerance
            quantified["value"] = calculated
            quantified["precision_or_uncertainty"] = (
                f"coordinate-calibrated graph-reading uncertainty ±{tolerance:g} {quantified.get('unit', '')}; "
                "not experimental uncertainty"
            )
        elif basis not in direct_bases:
            raise ValueError(
                f"signal_comparisons[{index}] numeric value requires an explicit source_basis; "
                "use CALIBRATED_PLOT_READING with coordinates or an exact source/text/table basis"
            )

    record["plot_reading_audit"] = {
        "calibration_count": len(calibrations),
        "reading_count": len(readings),
        "calibrations": [
            {"calibration_id": item["calibration_id"], "result_id": item["result_id"],
             "x_grade": item["calibration_qc"]["x_axis"]["grade"],
             "y_grade": item["calibration_qc"]["y_axis"]["grade"],
             "overall_grade": item["calibration_qc"]["overall_grade"]}
            for item in calibrations
        ],
        "numeric_plot_estimates_are_not_experimental_uncertainties": True,
        "limitations": [
            "Axis calibration and coordinate uncertainty quantify graph-reading uncertainty only.",
            "They do not replace replicate variability, instrument uncertainty, calibration uncertainty or experimental error bars.",
            "A calibrated plot estimate is not raw instrument data and must not be described as an exact value."
        ]
    }
