#!/usr/bin/env python3
"""Validate and persist a general scientific analysis record against its prepared pack."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle, parse_numeric_scalar, sha256_file, workspace_paths
from plot_reading import apply_plot_reading_audit

VALID_ANALYSIS_STATUS = {"COMPLETE", "PARTIAL", "NOT_ASSESSABLE"}
VALID_COVERAGE = {"ANALYZED", "NO_COMPARISON_APPLICABLE", "NOT_ASSESSABLE"}
VALID_COMPARISON = {"COMPARABLE", "PARTIALLY_COMPARABLE", "NOT_COMPARABLE", "NOT_APPLICABLE"}
VALID_DIMENSION = {"MATCHED", "MISMATCHED", "UNKNOWN", "NOT_APPLICABLE"}

VALID_SIGNAL_FEATURE_TYPES = {"PEAK", "BAND", "REFLECTION", "EDGE", "SHOULDER", "PLATEAU", "OTHER"}
VALID_SIGNAL_CHANGE_TYPES = {
    "POSITION_SHIFT", "WIDTH_CHANGE", "INTENSITY_CHANGE", "AREA_CHANGE",
    "APPEARED", "DISAPPEARED", "SHAPE_CHANGE", "OTHER",
}
VALID_SIGNAL_COVERAGE = {"APPLICABLE", "NOT_APPLICABLE", "NOT_ASSESSABLE"}
VALID_SERIES_MAPPING = {"CONFIRMED", "PROBABLE", "AMBIGUOUS", "UNRESOLVED"}
VALID_SAMPLE_MAPPING = {"CONFIRMED", "PROBABLE", "AMBIGUOUS", "UNMAPPED", "NOT_APPLICABLE"}
VALID_PANEL_MAPPING = {"CONFIRMED", "PROBABLE", "AMBIGUOUS", "UNRESOLVED", "NOT_APPLICABLE"}


def _validate_sample_mapping(
    bundle: dict[str, Any],
    result_id: str | None,
    sample_id: str | None,
    mapping_status: str,
    series_id: str | None,
    label: str,
) -> None:
    if mapping_status not in VALID_SAMPLE_MAPPING:
        raise ValueError(f"{label} has invalid sample_mapping_status")
    samples = bundle.get("samples", {})
    if sample_id and sample_id not in samples:
        raise ValueError(f"{label} references unknown sample_id {sample_id}")
    if mapping_status == "CONFIRMED":
        if not sample_id:
            raise ValueError(f"{label}: CONFIRMED sample mapping requires sample_id")
        if samples.get(sample_id, {}).get("identity_status") != "CONFIRMED":
            raise ValueError(f"{label}: CONFIRMED sample mapping requires a CONFIRMED sample identity")
    if mapping_status in {"UNMAPPED", "NOT_APPLICABLE"} and sample_id:
        raise ValueError(f"{label}: {mapping_status} sample mapping must not carry sample_id")
    result = bundle.get("result_units", {}).get(result_id, {})
    associations = result.get("measurement_context", {}).get("sample_associations", []) or []
    if series_id:
        linked = [item for item in associations if item.get("series_id") == series_id]
        for item in linked:
            linked_sample = item.get("sample_id")
            if linked_sample and sample_id and linked_sample != sample_id:
                raise ValueError(f"{label}: sample_id conflicts with the Result Unit's mapping for series {series_id}")
            if mapping_status == "CONFIRMED" and item.get("mapping_status") != "CONFIRMED":
                raise ValueError(f"{label}: series sample mapping conflicts with a non-confirmed Result Unit association")


def _validate_panel_mapping(
    bundle: dict[str, Any],
    result_id: str,
    panel_id: str | None,
    mapping_status: str,
    label: str,
) -> None:
    if mapping_status not in VALID_PANEL_MAPPING:
        raise ValueError(f"{label} has invalid panel_mapping_status")
    result = bundle.get("result_units", {}).get(result_id, {})
    if panel_id:
        if panel_id not in bundle.get("panels", {}):
            raise ValueError(f"{label} references unknown panel_id {panel_id}")
        if panel_id not in set(result.get("panel_ids", []) or []):
            raise ValueError(f"{label} references a Panel not linked to its Result Unit")
    elif mapping_status == "CONFIRMED":
        raise ValueError(f"{label}: CONFIRMED panel mapping requires panel_id")
    if mapping_status == "NOT_APPLICABLE" and panel_id:
        raise ValueError(f"{label}: NOT_APPLICABLE panel mapping must not carry panel_id")


def _validate_signal_estimate(estimate: Any, label: str) -> None:
    if estimate is None:
        return
    if not isinstance(estimate, dict):
        raise ValueError(f"{label} must be an object or null")
    value = estimate.get("value")
    if value is None:
        return
    if parse_numeric_scalar(value) is None:
        raise ValueError(f"{label}.value must be a finite numeric estimate or null")
    for field in ("unit", "reading_basis", "precision_or_uncertainty"):
        if not str(estimate.get(field) or "").strip():
            raise ValueError(f"{label}.{field} is required for numeric signal estimates")


def _validate_model_invocation(
    request: dict[str, Any],
    record: dict[str, Any],
    workspace: Path | None,
    has_analyzed_units: bool,
) -> None:
    if not request.get("invocation_audit_required"):
        return
    invocation = record.get("model_invocation")
    if not isinstance(invocation, dict):
        raise ValueError("model_invocation receipt is required for this analysis pack")
    if invocation.get("evidence_level") != "AGENT_REPORTED_RUNTIME_RECEIPT":
        raise ValueError("model_invocation.evidence_level must disclose agent-reported runtime evidence")
    if invocation.get("status") not in {"RESPONSE_RECEIVED", "BLOCKED", "UNVERIFIABLE"}:
        raise ValueError("model_invocation.status is invalid")
    if not str(invocation.get("invocation_id") or "").strip():
        raise ValueError("model_invocation.invocation_id is required")
    if has_analyzed_units and invocation.get("status") != "RESPONSE_RECEIVED":
        raise ValueError("ANALYZED coverage requires a completed model invocation receipt")
    analyzed_result_ids = {
        item.get("result_id") for item in record.get("coverage", [])
        if item.get("status") == "ANALYZED"
    }
    def applies_to_analyzed_result(asset: dict[str, Any]) -> bool:
        linked_ids = asset.get("result_ids") or ([asset.get("result_id")] if asset.get("result_id") else [])
        return not linked_ids or bool(set(linked_ids) & analyzed_result_ids)

    applicable_assets = [
        item for item in request.get("assets", []) if applies_to_analyzed_result(item)
    ]
    expected_assets = [
        item for item in applicable_assets
        if item.get("asset_exists") and item.get("asset_sha256")
    ]
    if workspace is not None and has_analyzed_units and any(
        not item.get("asset_exists") or not item.get("asset_sha256") for item in applicable_assets
    ):
        raise ValueError("ANALYZED coverage is blocked because an image asset for an ANALYZED Result Unit is missing or unhashed")
    if expected_assets and has_analyzed_units:
        if invocation.get("input_mode") != "NATIVE_IMAGE_ATTACHMENTS":
            raise ValueError("image-derived ANALYZED coverage requires confirmed native image attachments")
        attached = invocation.get("attached_assets")
        if not isinstance(attached, list):
            raise ValueError("model_invocation.attached_assets must list every native image attachment")
        expected = {(item["image_path"], item["asset_sha256"]) for item in expected_assets}
        received = set()
        for index, item in enumerate(attached):
            pair = (item.get("image_path"), item.get("asset_sha256"))
            if item.get("attachment_type") != "NATIVE_IMAGE":
                raise ValueError(f"model_invocation.attached_assets[{index}] is not declared as NATIVE_IMAGE")
            if not str(item.get("attachment_reference") or "").strip():
                raise ValueError(f"model_invocation.attached_assets[{index}] requires the actual attachment reference")
            received.add(pair)
        if len(received) != len(attached):
            raise ValueError("model_invocation.attached_assets contains duplicate native image receipts")
        if received != expected:
            missing = sorted(expected - received)
            extra = sorted(received - expected)
            raise ValueError(
                f"native image attachment manifest does not exactly match request assets; missing={missing}, extra={extra}"
            )
    elif has_analyzed_units and invocation.get("input_mode") not in {"TEXT_ONLY_PATHS", "NATIVE_IMAGE_ATTACHMENTS"}:
        raise ValueError("model_invocation.input_mode must state how the model received the evidence")
    if has_analyzed_units:
        if not str(invocation.get("model_id") or "").strip():
            raise ValueError("completed model invocation requires model_id")
        for field in ("request_log_path", "request_log_sha256", "response_log_path", "response_log_sha256"):
            if not str(invocation.get(field) or "").strip():
                raise ValueError(f"completed model invocation requires {field}")
        if workspace is not None:
            root = workspace.resolve()
            for path_field, hash_field in (
                ("request_log_path", "request_log_sha256"),
                ("response_log_path", "response_log_sha256"),
            ):
                artifact = Path(invocation[path_field])
                artifact = artifact if artifact.is_absolute() else root / artifact
                try:
                    artifact.resolve().relative_to(root)
                except ValueError as exc:
                    raise ValueError(f"{path_field} must remain inside the workspace") from exc
                if not artifact.is_file():
                    raise ValueError(f"{path_field} does not exist: {artifact}")
                if sha256_file(artifact) != invocation[hash_field]:
                    raise ValueError(f"{hash_field} does not match {path_field}")



def _valid_refs(
    bundle: dict[str, Any],
    result_ids: set[str],
    refs: list[dict[str, Any]],
    label: str,
) -> None:
    if not isinstance(refs, list) or not refs:
        raise ValueError(f"{label} must cite at least one source evidence reference")
    results = bundle.get("result_units", {})
    for ref in refs:
        result_id = ref.get("result_id")
        if result_id not in result_ids:
            raise ValueError(f"{label} cites a Result Unit outside the prepared pack: {result_id}")
        result = results.get(result_id, {})
        region_ids = set(result.get("region_ids", []) or [])
        panel_ids = set(result.get("panel_ids", []) or [])
        region_id = ref.get("region_id")
        panel_id = ref.get("panel_id")
        if region_id and region_id not in region_ids:
            raise ValueError(f"{label} cites an unrelated Region {region_id} for {result_id}")
        if panel_id and panel_id not in panel_ids:
            raise ValueError(f"{label} cites an unrelated Panel {panel_id} for {result_id}")
        if not region_id and not panel_id:
            raise ValueError(f"{label} reference must include region_id or panel_id")
        regions = bundle.get("regions", {})
        if region_id and region_id in regions:
            source_region = regions[region_id]
            if ref.get("page_number") is not None and source_region.get("page_number") is not None:
                if int(ref["page_number"]) != int(source_region["page_number"]):
                    raise ValueError(f"{label} page_number does not match source Region {region_id}")
        if panel_id:
            panel = bundle.get("panels", {}).get(panel_id, {})
            parent_region_id = panel.get("parent_region_id")
            if region_id and parent_region_id and region_id != parent_region_id:
                raise ValueError(f"{label} Panel {panel_id} does not belong to Region {region_id}")
            if ref.get("page_number") is not None and parent_region_id in regions:
                source_page = regions[parent_region_id].get("page_number")
                if source_page is not None and int(ref["page_number"]) != int(source_page):
                    raise ValueError(f"{label} page_number does not match Panel {panel_id}")


def validate_record(
    bundle: dict[str, Any],
    request: dict[str, Any],
    record: dict[str, Any],
    workspace: Path | None = None,
) -> None:
    expected_id = request.get("analysis_id")
    request_sha = request.get("source", {}).get("sha256")
    current_sha = bundle.get("source", {}).get("sha256")
    if not request_sha or not current_sha or request_sha != current_sha:
        raise ValueError("Prepared request source SHA-256 does not match the current Evidence Bundle")
    if record.get("analysis_id") != expected_id:
        raise ValueError("analysis_id does not match the prepared request")
    if record.get("analysis_mode") != "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS":
        raise ValueError("analysis_mode must be GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS")
    expected_ids = set(request.get("result_ids", []))
    supplied_ids = record.get("result_ids", [])
    if set(supplied_ids) != expected_ids or len(supplied_ids) != len(expected_ids):
        raise ValueError("record result_ids must match the prepared pack exactly")
    for result_id in expected_ids:
        if result_id not in bundle.get("result_units", {}):
            raise ValueError(f"Prepared Result Unit no longer exists in Evidence Bundle: {result_id}")
    if record.get("analysis_status") not in VALID_ANALYSIS_STATUS:
        raise ValueError("analysis_status must be COMPLETE, PARTIAL or NOT_ASSESSABLE")
    if not str(record.get("summary") or "").strip():
        raise ValueError("A scientific analysis summary is required")

    coverage = record.get("coverage")
    if not isinstance(coverage, list):
        raise ValueError("coverage must be a list")
    coverage_ids = [item.get("result_id") for item in coverage]
    if set(coverage_ids) != expected_ids or len(coverage_ids) != len(expected_ids):
        raise ValueError("coverage must account for every Result Unit exactly once")
    for item in coverage:
        if item.get("status") not in VALID_COVERAGE:
            raise ValueError(f"Invalid coverage status for {item.get('result_id')}")
        if item.get("status") in {"NO_COMPARISON_APPLICABLE", "NOT_ASSESSABLE"} and not str(item.get("reason") or "").strip():
            raise ValueError(f"{item['result_id']}: a reason is required for {item['status']}")
    if record["analysis_status"] == "COMPLETE" and any(
        item["status"] == "NOT_ASSESSABLE" for item in coverage
    ):
        raise ValueError("COMPLETE analysis cannot contain NOT_ASSESSABLE Result Units")

    observation_ids: set[str] = set()
    observation_result_map: dict[str, set[str]] = {}
    for index, item in enumerate(record.get("observations", [])):
        observation_id = item.get("observation_id")
        if not observation_id or observation_id in observation_ids:
            raise ValueError(f"observations[{index}] requires a unique observation_id")
        observation_ids.add(observation_id)
        if item.get("epistemic_status") != "Observed":
            raise ValueError(f"observations[{index}] must be an Observed statement")
        refs = item.get("result_ids", [])
        if not refs or not set(refs).issubset(expected_ids):
            raise ValueError(f"observations[{index}] must cite Result Units in the prepared pack")
        observation_result_map[observation_id] = set(refs)
        _valid_refs(bundle, expected_ids, item.get("evidence_refs", []), f"observations[{index}]")
        sample_id = item.get("sample_id")
        mapping_status = item.get("mapping_status")
        if sample_id or mapping_status:
            _validate_sample_mapping(
                bundle, refs[0] if len(refs) == 1 else item.get("result_id"),
                sample_id, mapping_status or ("AMBIGUOUS" if sample_id else "UNMAPPED"),
                item.get("series_id"), f"observations[{index}]",
            )
        numeric_present = item.get("numeric_value") is not None or item.get("numeric_values") is not None
        if numeric_present:
            if len(refs) != 1:
                raise ValueError(f"observations[{index}] numeric measurement must identify exactly one Result Unit")
            if not str(item.get("measurand") or "").strip():
                raise ValueError(f"observations[{index}] numeric measurement requires measurand")
            if not str(item.get("unit") or "").strip():
                raise ValueError(f"observations[{index}] numeric measurement requires unit")
            if not str(item.get("data_origin") or "").strip():
                raise ValueError(f"observations[{index}] numeric measurement requires data_origin")
            if item.get("numeric_value") is not None and parse_numeric_scalar(item.get("numeric_value")) is None:
                raise ValueError(f"observations[{index}].numeric_value must be finite numeric")
            numeric_values = item.get("numeric_values")
            if numeric_values is not None:
                if not isinstance(numeric_values, list) or not numeric_values:
                    raise ValueError(f"observations[{index}].numeric_values must be a non-empty list")
                if any(parse_numeric_scalar(value) is None for value in numeric_values):
                    raise ValueError(f"observations[{index}].numeric_values must contain only finite numbers")

    for item in coverage:
        if item.get("status") == "ANALYZED":
            refs = set(item.get("observation_ids", []))
            if not refs or not refs.issubset(observation_ids):
                raise ValueError(f"{item['result_id']}: ANALYZED coverage must cite at least one recorded observation")
            if any(item["result_id"] not in observation_result_map.get(obs_id, set()) for obs_id in refs):
                raise ValueError(f"{item['result_id']}: coverage observation does not cite this Result Unit")

    generic_comparison_map: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(record.get("comparisons", [])):
        generic_id = str(item.get("comparison_id") or "")
        if generic_id:
            if generic_id in generic_comparison_map:
                raise ValueError(f"comparisons[{index}] requires a unique comparison_id")
            generic_comparison_map[generic_id] = item
        ids = item.get("result_ids", [])
        if len(set(ids)) < 2 or not set(ids).issubset(expected_ids):
            raise ValueError(f"comparisons[{index}] must compare at least two Result Units in the prepared pack")
        if item.get("comparison_status") not in VALID_COMPARISON:
            raise ValueError(f"comparisons[{index}] has an invalid comparison_status")
        dimensions = item.get("dimension_assessments")
        if not isinstance(dimensions, list) or not dimensions:
            raise ValueError(f"comparisons[{index}] requires dimension_assessments")
        for dimension in dimensions:
            if dimension.get("status") not in VALID_DIMENSION:
                raise ValueError(f"comparisons[{index}] has an invalid dimension status")
        if not str(item.get("conclusion") or "").strip():
            raise ValueError(f"comparisons[{index}] requires a conclusion")
        observation_refs = set(item.get("observation_ids", []))
        if not observation_refs or not observation_refs.issubset(observation_ids):
            raise ValueError(f"comparisons[{index}] must cite recorded observations")
        _valid_refs(bundle, expected_ids, item.get("evidence_refs", []), f"comparisons[{index}]")
        if any(ref.get("result_id") not in ids for ref in item.get("evidence_refs", [])):
            raise ValueError(f"comparisons[{index}] cites evidence outside its compared Result Units")
        if any(not str(value).strip() for value in item.get("signal_comparison_ids", []) or []):
            raise ValueError(f"comparisons[{index}] contains an empty signal_comparison_id")
        for difference in item.get("quantitative_differences", []):
            for value in difference.get("values", []):
                if value.get("result_id") not in ids:
                    raise ValueError(f"comparisons[{index}] quantitative difference cites an unrelated Result Unit")
                if parse_numeric_scalar(value.get("value")) is None:
                    raise ValueError(f"comparisons[{index}] quantitative values must be finite numeric estimates or measurements")
                if not str(value.get("unit") or "").strip():
                    raise ValueError(f"comparisons[{index}] quantitative values must declare a unit (use 'dimensionless' when appropriate)")
                if not str(value.get("source_basis") or "").strip():
                    raise ValueError(f"comparisons[{index}] quantitative values must declare their source basis")
                if not str(value.get("precision_or_uncertainty") or "").strip():
                    raise ValueError(f"comparisons[{index}] quantitative values must state precision or uncertainty")

    for index, item in enumerate(record.get("relationships", [])):
        ids = item.get("result_ids", [])
        if not ids or not set(ids).issubset(expected_ids):
            raise ValueError(f"relationships[{index}] must cite Result Units in the prepared pack")
        refs = set(item.get("observation_ids", []))
        if not refs.issubset(observation_ids):
            raise ValueError(f"relationships[{index}] cites unknown observations")
        if item.get("causal_status") not in {
            "NOT_ESTABLISHED", "SUPPORTED_WITH_CONTROLS", "ESTABLISHED_BY_DESIGN"
        }:
            raise ValueError(f"relationships[{index}] has invalid causal_status")

    for index, item in enumerate(record.get("interpretations", [])):
        if item.get("epistemic_status") not in {"Interpreted", "Hypothesized"}:
            raise ValueError(f"interpretations[{index}] must be Interpreted or Hypothesized")
        refs = set(item.get("supporting_observation_ids", []))
        if not refs or not refs.issubset(observation_ids):
            raise ValueError(f"interpretations[{index}] must cite recorded observations")
        if not item.get("alternative_explanations"):
            raise ValueError(f"interpretations[{index}] must record alternative explanations")

    for index, item in enumerate(record.get("contradictions", [])):
        ids = item.get("result_ids", [])
        if not ids or not set(ids).issubset(expected_ids):
            raise ValueError(f"contradictions[{index}] must cite Result Units in the prepared pack")
        _valid_refs(bundle, expected_ids, item.get("evidence_refs", []), f"contradictions[{index}]")

    signal_features = record.get("signal_features", [])
    feature_map: dict[str, dict[str, Any]] = {}
    for index, feature in enumerate(signal_features):
        feature_id = str(feature.get("feature_id") or "")
        if not feature_id or feature_id in feature_map:
            raise ValueError(f"signal_features[{index}] requires a unique feature_id")
        if feature.get("result_id") not in expected_ids:
            raise ValueError(f"signal_features[{index}] references a Result Unit outside the prepared pack")
        if feature.get("feature_type") not in VALID_SIGNAL_FEATURE_TYPES:
            raise ValueError(f"signal_features[{index}] has an invalid feature_type")
        if not str(feature.get("description") or "").strip():
            raise ValueError(f"signal_features[{index}] requires a description of the observed feature")
        refs = feature.get("evidence_refs", [])
        _valid_refs(bundle, expected_ids, refs, f"signal_features[{index}]")
        if any(ref.get("result_id") != feature.get("result_id") for ref in refs):
            raise ValueError(f"signal_features[{index}] evidence must belong to its declared Result Unit")
        if not str(feature.get("series_label") or "").strip():
            raise ValueError(f"signal_features[{index}] requires a visible series_label or UNKNOWN")
        if feature.get("series_mapping_status") is not None and feature["series_mapping_status"] not in VALID_SERIES_MAPPING:
            raise ValueError(f"signal_features[{index}] has invalid series_mapping_status")
        mapping_evidence = feature.get("series_mapping_evidence_refs", []) or []
        if mapping_evidence:
            _valid_refs(bundle, expected_ids, mapping_evidence, f"signal_features[{index}].series_mapping_evidence_refs")
            if any(ref.get("result_id") != feature.get("result_id") for ref in mapping_evidence):
                raise ValueError(f"signal_features[{index}] series mapping evidence must belong to its Result Unit")
        if feature.get("sample_mapping_status") is not None:
            _validate_sample_mapping(
                bundle, feature.get("result_id"), feature.get("sample_id"),
                feature["sample_mapping_status"], feature.get("series_id"), f"signal_features[{index}]",
            )
        if feature.get("panel_mapping_status") is not None:
            _validate_panel_mapping(
                bundle, feature.get("result_id"), feature.get("panel_id"),
                feature["panel_mapping_status"], f"signal_features[{index}]",
            )
        axes = feature.get("axis_context")
        if not isinstance(axes, dict):
            raise ValueError(f"signal_features[{index}] requires axis_context")
        for field in ("x_axis_label", "x_axis_unit", "x_axis_scale",
                      "y_axis_label", "y_axis_unit", "y_axis_scale", "normalization_basis"):
            if not str(axes.get(field) or "").strip():
                raise ValueError(f"signal_features[{index}].axis_context requires {field} (use UNKNOWN when unresolved)")
        if axes.get("x_axis_scale") not in {"LINEAR", "LOG", "CATEGORICAL", "UNKNOWN"}:
            raise ValueError(f"signal_features[{index}] has invalid x_axis_scale")
        if axes.get("y_axis_scale") not in {"LINEAR", "LOG", "CATEGORICAL", "UNKNOWN"}:
            raise ValueError(f"signal_features[{index}] has invalid y_axis_scale")
        for estimate_name in ("position", "width", "intensity", "area"):
            estimate = feature.get(estimate_name)
            _validate_signal_estimate(estimate, f"signal_features[{index}].{estimate_name}")
            if estimate_name in {"intensity", "area"} and isinstance(estimate, dict) and estimate.get("value") is not None:
                if not str(estimate.get("normalization_basis") or axes.get("normalization_basis") or "").strip():
                    raise ValueError(f"signal_features[{index}].{estimate_name} requires normalization_basis")
        feature_map[feature_id] = feature

    comparison_ids: set[str] = set()
    comparison_map: dict[str, dict[str, Any]] = {}
    for index, comparison in enumerate(record.get("signal_comparisons", [])):
        comparison_id = str(comparison.get("comparison_id") or "")
        if not comparison_id or comparison_id in comparison_ids:
            raise ValueError(f"signal_comparisons[{index}] requires a unique comparison_id")
        comparison_ids.add(comparison_id)
        comparison_map[comparison_id] = comparison
        feature_ids = comparison.get("feature_ids", [])
        if len(set(feature_ids)) < 2 or not set(feature_ids).issubset(feature_map):
            raise ValueError(f"signal_comparisons[{index}] must reference at least two recorded signal features")
        result_ids = comparison.get("result_ids", [])
        if not result_ids or not set(result_ids).issubset(expected_ids):
            raise ValueError(f"signal_comparisons[{index}] must cite Result Units in the prepared pack")
        feature_result_ids = {feature_map[item]["result_id"] for item in feature_ids}
        if feature_result_ids != set(result_ids):
            raise ValueError(f"signal_comparisons[{index}] feature/result links are inconsistent")
        generic_ids = comparison.get("analysis_comparison_ids", []) or []
        if not set(generic_ids).issubset(generic_comparison_map):
            raise ValueError(f"signal_comparisons[{index}] references an unknown generic comparison_id")
        for generic_id in generic_ids:
            generic = generic_comparison_map[generic_id]
            if comparison_id not in set(generic.get("signal_comparison_ids", []) or []):
                raise ValueError(f"signal_comparisons[{index}] and generic comparison {generic_id} must link reciprocally")
            if not set(result_ids).issubset(set(generic.get("result_ids", []) or [])):
                raise ValueError(f"signal_comparisons[{index}] Result Units fall outside generic comparison {generic_id}")
        evidence_result_ids = {ref.get("result_id") for ref in comparison.get("evidence_refs", [])}
        if not set(result_ids).issubset(evidence_result_ids):
            raise ValueError(f"signal_comparisons[{index}] must cite source evidence for every compared Result Unit")
        if comparison.get("change_type") not in VALID_SIGNAL_CHANGE_TYPES:
            raise ValueError(f"signal_comparisons[{index}] has an invalid change_type")
        if comparison.get("comparability_status") not in VALID_COMPARISON | {"UNKNOWN"}:
            raise ValueError(f"signal_comparisons[{index}] has an invalid comparability_status")
        if not str(comparison.get("description") or "").strip():
            raise ValueError(f"signal_comparisons[{index}] requires an observed comparison description")
        _valid_refs(bundle, expected_ids, comparison.get("evidence_refs", []), f"signal_comparisons[{index}]")
        if any(ref.get("result_id") not in result_ids for ref in comparison.get("evidence_refs", [])):
            raise ValueError(f"signal_comparisons[{index}] cites evidence outside its compared Result Units")
        quantified = comparison.get("quantified_change")
        if quantified and quantified.get("value") is not None:
            if parse_numeric_scalar(quantified.get("value")) is None:
                raise ValueError(f"signal_comparisons[{index}].quantified_change.value must be finite numeric or null")
            for field in ("unit", "source_basis", "precision_or_uncertainty"):
                if not str(quantified.get(field) or "").strip():
                    raise ValueError(f"signal_comparisons[{index}].quantified_change.{field} is required")

    for generic_id, generic in generic_comparison_map.items():
        for signal_id in generic.get("signal_comparison_ids", []) or []:
            linked_signal = next(
                (item for item in record.get("signal_comparisons", [])
                 if item.get("comparison_id") == signal_id),
                None,
            )
            if linked_signal is None:
                raise ValueError(f"generic comparison {generic_id} references an unknown signal_comparison_id")
            if generic_id not in set(linked_signal.get("analysis_comparison_ids", []) or []):
                raise ValueError(f"generic comparison {generic_id} and signal comparison {signal_id} must link reciprocally")
            if not set(linked_signal.get("result_ids", [])).issubset(set(generic.get("result_ids", []) or [])):
                raise ValueError(f"signal comparison {signal_id} Result Units fall outside generic comparison {generic_id}")

    signal_coverage = record.get("signal_analysis_coverage")
    if not isinstance(signal_coverage, list):
        raise ValueError("signal_analysis_coverage must explicitly disposition every Result Unit")
    signal_coverage_ids = [item.get("result_id") for item in signal_coverage]
    if set(signal_coverage_ids) != expected_ids or len(signal_coverage_ids) != len(expected_ids):
        raise ValueError("signal_analysis_coverage must account for every Result Unit exactly once")
    feature_owner: dict[str, str] = {}
    signal_coverage_map: dict[str, dict[str, Any]] = {}
    for item in signal_coverage:
        result_id = item.get("result_id")
        signal_coverage_map[result_id] = item
        if item.get("status") not in VALID_SIGNAL_COVERAGE:
            raise ValueError(f"{result_id}: invalid signal_analysis_coverage status")
        if item.get("status") in {"NOT_APPLICABLE", "NOT_ASSESSABLE"} and not str(item.get("reason") or "").strip():
            raise ValueError(f"{result_id}: signal coverage {item.get('status')} requires a reason")
        feature_ids = item.get("feature_ids", [])
        if item.get("status") == "APPLICABLE" and not feature_ids:
            raise ValueError(f"{result_id}: APPLICABLE signal coverage requires recorded signal_features")
        if any(feature_id not in feature_map or feature_map[feature_id].get("result_id") != result_id for feature_id in feature_ids):
            raise ValueError(f"{result_id}: signal_analysis_coverage contains an unrelated or unknown feature_id")
        for feature_id in feature_ids:
            feature_owner[feature_id] = result_id
        comparison_refs = item.get("comparison_ids", [])
        if not set(comparison_refs).issubset(comparison_ids):
            raise ValueError(f"{result_id}: signal_analysis_coverage contains an unknown comparison_id")
        if any(result_id not in comparison_map[comparison_id].get("result_ids", []) for comparison_id in comparison_refs):
            raise ValueError(f"{result_id}: signal_analysis_coverage references a comparison that does not include this Result Unit")
        if not comparison_refs and item.get("status") == "APPLICABLE" and not str(item.get("reason") or "").strip():
            raise ValueError(f"{result_id}: explain why no signal comparison was possible")
    for feature_id, feature in feature_map.items():
        if feature_owner.get(feature_id) != feature.get("result_id"):
            raise ValueError(f"{feature_id}: signal feature is not linked from its Result Unit coverage")
    for comparison_id, comparison in comparison_map.items():
        for result_id in comparison.get("result_ids", []):
            coverage_item = signal_coverage_map.get(result_id, {})
            if comparison_id not in coverage_item.get("comparison_ids", []):
                raise ValueError(f"{comparison_id}: comparison is not linked from every compared Result Unit's signal coverage")

    calibration_map = {}
    for index, calibration in enumerate(record.get("plot_calibrations", [])):
        calibration_id = calibration.get("calibration_id")
        result_id = calibration.get("result_id")
        if result_id not in expected_ids:
            raise ValueError(f"plot_calibrations[{index}] cites a Result Unit outside the prepared pack")
        refs = calibration.get("evidence_refs", [])
        _valid_refs(bundle, expected_ids, refs, f"plot_calibrations[{index}]")
        if any(ref.get("result_id") != result_id for ref in refs):
            raise ValueError(f"plot_calibrations[{index}] evidence must belong to its declared Result Unit")
        if calibration_id in calibration_map:
            raise ValueError(f"plot_calibrations[{index}] requires a unique calibration_id")
        calibration_map[calibration_id] = calibration
        for series_index, series in enumerate(calibration.get("series", []) or []):
            series_label = f"plot_calibrations[{index}].series[{series_index}]"
            if series.get("mapping_status") not in VALID_SERIES_MAPPING:
                raise ValueError(f"{series_label} has invalid mapping_status")
            mapping_refs = series.get("mapping_evidence_refs", []) or []
            if mapping_refs:
                _valid_refs(bundle, expected_ids, mapping_refs, f"{series_label}.mapping_evidence_refs")
                if any(ref.get("result_id") != result_id for ref in mapping_refs):
                    raise ValueError(f"{series_label}.mapping_evidence_refs must cite its calibration Result Unit")
            if series.get("mapping_status") == "CONFIRMED" and (
                not str(series.get("mapping_basis") or "").strip() or not mapping_refs
            ):
                series["mapping_status"] = "UNRESOLVED"
                series.setdefault("mapping_limitations", []).append(
                    "Confirmed trace mapping lacks its mapping basis or source evidence and has been downgraded."
                )
            series.setdefault("panel_mapping_status", "AMBIGUOUS" if series.get("panel_id") else "UNRESOLVED")
            series.setdefault("sample_mapping_status", "AMBIGUOUS" if series.get("sample_id") else "UNMAPPED")
            _validate_panel_mapping(
                bundle, result_id, series.get("panel_id"),
                series["panel_mapping_status"], series_label,
            )
            _validate_sample_mapping(
                bundle, result_id, series.get("sample_id"),
                series["sample_mapping_status"], series.get("series_id"), series_label,
            )
            if series["panel_mapping_status"] == "CONFIRMED":
                panel_id = series.get("panel_id")
                if not any(ref.get("panel_id") == panel_id for ref in refs):
                    raise ValueError(f"{series_label}: confirmed panel must be present in calibration evidence_refs")

    for index, reading in enumerate(record.get("plot_readings", [])):
        result_id = reading.get("result_id")
        if result_id not in expected_ids:
            raise ValueError(f"plot_readings[{index}] cites a Result Unit outside the prepared pack")
        refs = reading.get("evidence_refs", [])
        _valid_refs(bundle, expected_ids, refs, f"plot_readings[{index}]")
        if any(ref.get("result_id") != result_id for ref in refs):
            raise ValueError(f"plot_readings[{index}] evidence must belong to its declared Result Unit")
        calibration = calibration_map.get(reading.get("calibration_id"))
        if calibration is None or calibration.get("result_id") != result_id:
            raise ValueError(f"plot_readings[{index}] must resolve to a calibration for the same Result Unit")
        calibration_refs = {
            (ref.get("region_id"), ref.get("panel_id"), ref.get("page_number"))
            for ref in calibration.get("evidence_refs", [])
        }
        reading_refs = {
            (ref.get("region_id"), ref.get("panel_id"), ref.get("page_number"))
            for ref in refs
        }
        if not reading_refs.issubset(calibration_refs):
            raise ValueError(f"plot_readings[{index}] source must match its axis calibration source")

    _validate_model_invocation(
        request, record, workspace,
        has_analyzed_units=any(item.get("status") == "ANALYZED" for item in coverage),
    )
    apply_plot_reading_audit(request, record, workspace)

    # A comparison labelled COMPARABLE must not outrun the identity evidence
    # attached to each plotted feature's trace, sample and source panel.
    feature_lookup_after_audit = {
        item.get("feature_id"): item for item in record.get("signal_features", [])
        if item.get("feature_id")
    }
    for index, comparison in enumerate(record.get("signal_comparisons", [])):
        if comparison.get("comparability_status") != "COMPARABLE":
            continue
        for feature_id in comparison.get("feature_ids", []):
            feature = feature_lookup_after_audit.get(feature_id, {})
            if (
                feature.get("series_mapping_status") != "CONFIRMED"
                or not str(feature.get("series_mapping_basis") or "").strip()
                or not feature.get("series_mapping_evidence_refs")
            ):
                raise ValueError(
                    f"signal_comparisons[{index}] cannot be COMPARABLE while feature {feature_id} lacks a source-supported confirmed series identity"
                )
            if feature.get("sample_mapping_status") not in {"CONFIRMED", "NOT_APPLICABLE"}:
                raise ValueError(
                    f"signal_comparisons[{index}] cannot be COMPARABLE while feature {feature_id} has unresolved sample mapping"
                )
            if feature.get("panel_mapping_status") not in {"CONFIRMED", "NOT_APPLICABLE"}:
                raise ValueError(
                    f"signal_comparisons[{index}] cannot be COMPARABLE while feature {feature_id} has unresolved panel mapping"
                )


def register_analysis(
    bundle: dict[str, Any],
    request: dict[str, Any],
    record: dict[str, Any],
    replace_existing: bool = False,
    workspace: Path | None = None,
) -> None:
    validate_record(bundle, request, record, workspace)
    analyses = bundle.setdefault("scientific_analyses", {})
    analysis_id = record["analysis_id"]
    if analysis_id in analyses and not replace_existing:
        raise ValueError(f"Analysis already recorded: {analysis_id}; pass --replace to revise it")
    saved = dict(record)
    saved["recorded_at"] = datetime.now(timezone.utc).isoformat()
    saved["source_sha256"] = bundle.get("source", {}).get("sha256")
    saved["request_pack_number"] = request.get("pack_number")
    saved["request_asset_count"] = request.get("asset_count")
    saved["invocation_audit_required"] = bool(request.get("invocation_audit_required"))
    saved["plot_reading_audit_required"] = bool(request.get("plot_reading_audit_required"))
    saved["request_assets"] = [
        {"image_path": item.get("image_path"), "asset_sha256": item.get("asset_sha256"),
         "region_id": item.get("region_id"), "panel_id": item.get("panel_id"),
         "result_id": item.get("result_id"), "result_ids": item.get("result_ids", []),
         "pixel_width": item.get("pixel_width"), "pixel_height": item.get("pixel_height"),
         "vector_geometry_path": item.get("vector_geometry_path"),
         "vector_geometry_sha256": item.get("vector_geometry_sha256"),
         "asset_exists": item.get("asset_exists")}
        for item in request.get("assets", [])
    ]
    saved["model_invocation_status"] = record.get("model_invocation", {}).get("status")
    saved["model_input_mode"] = record.get("model_invocation", {}).get("input_mode")
    saved["candidate_relationships"] = request.get("candidate_relationships", [])
    saved["related_results_outside_pack"] = request.get("related_results_outside_pack", [])
    analyses[analysis_id] = saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--request-json", type=Path, required=True)
    parser.add_argument("--record-json", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    request = json.loads(args.request_json.read_text(encoding="utf-8"))
    record = json.loads(args.record_json.read_text(encoding="utf-8"))
    bundle = load_evidence_bundle(workspace)
    register_analysis(bundle, request, record, args.replace, workspace)
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    saved = bundle["scientific_analyses"][record["analysis_id"]]
    event = {
        "event_type": "SCIENTIFIC_ANALYSIS_RECORDED",
        "analysis_id": record["analysis_id"],
        "result_ids": record["result_ids"],
        "analysis_status": record["analysis_status"],
        "coverage_complete": len(record["coverage"]) == len(record["result_ids"]),
        "recorded_at": saved["recorded_at"],
    }
    paths["history"].mkdir(parents=True, exist_ok=True)
    with (paths["history"] / "scientific_analyses.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
