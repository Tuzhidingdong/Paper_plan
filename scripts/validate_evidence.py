#!/usr/bin/env python3
"""Deterministic structural and numeric-permission validator for the Evidence Bundle."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scientific_quality_gates import validate_evidence_quality
from scientific_argument_bridge import validate_finding_analysis_refs

from era_core import (
    atomic_write_json,
    load_evidence_bundle,
    load_json,
    observation_is_numeric,
    parse_numeric_scalar,
    result_has_machine_readable_number,
    result_is_quantitative,
    sha256_file,
    workspace_paths,
)

VALID_ORIGINS = {"Exact_Text", "Exact_Table", "Vector_Extracted", "Visual_Estimate", "Qualitative_Observation", "Unavailable"}
VALID_LEGIBILITY = {"High", "Medium", "Low", "Unassessable"}
VALID_PERMISSION = {"Exact_Values", "Trend_Only", "Qualitative_Only", "None"}
VALID_EPISTEMIC = {"Observed", "Interpreted", "Hypothesized"}
VALID_VISIBILITY = {"FOUND", "NOT_SHOWN", "NOT_LEGIBLE", "UNCERTAIN", "NOT_APPLICABLE"}
VALID_MAPPING = {"CONFIRMED", "PROBABLE", "AMBIGUOUS", "UNMAPPED", "NOT_APPLICABLE"}
VISUAL_MARKER = "[Visual Estimate - Raw Data Required]"


def validate_figure_candidate_coverage(
    bundle: dict[str, Any],
    workspace: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Require every ingest-detected vector figure candidate to reach an explicit disposition."""
    errors: list[str] = []
    warnings: list[str] = []
    candidates = bundle.get("figure_candidates", {})
    expected: dict[str, dict[str, Any]] = {}
    manifest = None
    if workspace is not None:
        manifest_path = workspace_paths(workspace)["manifest"]
        if manifest_path.is_file():
            manifest = load_json(manifest_path)
    if manifest is not None:
        for page in manifest.get("pages", []):
            if not page.get("vector_or_text_figure_review"):
                continue
            page_number = int(page.get("page_number") or 0)
            page_candidates = page.get("vector_figure_candidates") or []
            if not page_candidates and page.get("vector_candidate_bbox_pdf"):
                page_candidates = [{"candidate_index": 1}]
            if not page_candidates:
                errors.append(
                    f"Page {page_number}: vector-figure review was flagged but no candidate BBox was retained"
                )
            for index, _candidate in enumerate(page_candidates, start=1):
                candidate_id = f"VFIG-P{page_number:04d}-{index:02d}"
                expected[candidate_id] = {"page_number": page_number}
                if candidate_id not in candidates:
                    errors.append(
                        f"{candidate_id}: detected source figure candidate has no extracted Evidence Bundle record"
                    )
    for candidate_id, candidate in candidates.items():
        if candidate.get("extraction_status") != "EXTRACTED":
            errors.append(f"{candidate_id}: vector figure extraction is not complete")
            continue
        region_id = candidate.get("region_id")
        region = bundle.get("regions", {}).get(region_id, {})
        if not region_id or not region:
            errors.append(f"{candidate_id}: extracted candidate has no registered Region")
            continue
        if int(region.get("page_number") or 0) != int(candidate.get("page_number") or 0):
            errors.append(f"{candidate_id}: candidate and Region page numbers disagree")
        if region.get("pixel_sha256") != candidate.get("pixel_sha256"):
            errors.append(f"{candidate_id}: candidate and Region pixel hashes disagree")
        if workspace is not None:
            root = workspace.resolve()
            image_path = Path(str(region.get("image_path") or ""))
            image_path = image_path if image_path.is_absolute() else root / image_path
            try:
                image_path.resolve().relative_to(root)
            except ValueError:
                errors.append(f"{candidate_id}: Region image path escapes the workspace")
                image_path = None
            if image_path is not None and not image_path.is_file():
                errors.append(f"{candidate_id}: extracted Region image file is missing")
            elif image_path is not None and candidate.get("asset_sha256"):
                if sha256_file(image_path) != candidate.get("asset_sha256"):
                    errors.append(f"{candidate_id}: extracted Region file SHA-256 does not match its figure-candidate record")
        if candidate.get("triage_status") != "REVIEWED":
            errors.append(f"{candidate_id}: explicit scientific-figure disposition is missing")
            continue
        disposition = candidate.get("disposition")
        if disposition == "EXCLUDE_NOT_SCIENTIFIC_FIGURE":
            if not str(candidate.get("reason") or "").strip():
                errors.append(f"{candidate_id}: excluded candidate requires a reason")
        elif disposition == "INCLUDE_AS_SCIENTIFIC_FIGURE":
            linked_ids = candidate.get("result_ids", [])
            if not linked_ids:
                errors.append(f"{candidate_id}: included candidate has no linked Result Units")
            for result_id in linked_ids:
                result = bundle.get("result_units", {}).get(result_id)
                if result is None:
                    errors.append(f"{candidate_id}: linked Result Unit {result_id} does not exist")
                    continue
                linked_regions = set(result.get("region_ids", []) or [])
                linked_panel_parents = {
                    bundle.get("panels", {}).get(panel_id, {}).get("parent_region_id")
                    for panel_id in result.get("panel_ids", []) or []
                }
                if region_id not in linked_regions and region_id not in linked_panel_parents:
                    errors.append(
                        f"{candidate_id}: source Region {region_id} is not linked to Result Unit {result_id}"
                    )
        else:
            errors.append(f"{candidate_id}: invalid figure-candidate disposition {disposition!r}")
    unexpected = sorted(set(candidates) - set(expected)) if expected else []
    if unexpected and manifest is not None:
        warnings.append("Figure-candidate records not matched to current ingest manifest: " + ", ".join(unexpected))
    return errors, warnings


def validate(bundle: dict[str, Any], workspace: Path | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for key in ("source", "regions", "panels", "samples", "result_units", "findings", "audit_records"):
        if key not in bundle:
            errors.append(f"Missing top-level field: {key}")
    regions, panels, samples = bundle.get("regions", {}), bundle.get("panels", {}), bundle.get("samples", {})
    results = bundle.get("result_units", {})
    registry = None
    if workspace is not None:
        registry_path = workspace_paths(workspace)["registry"]
        if registry_path.exists():
            registry = load_json(registry_path)
        elif any((regions, panels, samples, results, bundle.get("findings"))):
            errors.append("Persistent ID registry is missing while evidence entities exist")

    def check_registry(entity_id: str, prefix: str, expected_type: str) -> None:
        if registry is None:
            return
        entity = registry.get("entities", {}).get(entity_id)
        if entity is None:
            errors.append(f"{entity_id}: ID is not allocated in the Python registry")
            return
        if not entity_id.startswith(prefix) or entity.get("entity_type") != expected_type:
            errors.append(f"{entity_id}: registry prefix/entity type mismatch (expected {prefix}/{expected_type})")

    for region_id, region in regions.items():
        if region.get("region_id") != region_id:
            errors.append(f"Region key/id mismatch: {region_id}")
        check_registry(region_id, "REG", "region")
        if region.get("page_number", 0) < 1:
            errors.append(f"{region_id}: page_number must be positive")
        bbox = region.get("bbox_normalized", [])
        if len(bbox) != 4 or not (0 <= bbox[0] < bbox[2] <= 1 and 0 <= bbox[1] < bbox[3] <= 1):
            errors.append(f"{region_id}: invalid normalized BBox")
        image_path = region.get("image_path")
        if not image_path:
            errors.append(f"{region_id}: missing image_path")
        elif workspace is not None and not (workspace / image_path).is_file():
            errors.append(f"{region_id}: image file does not exist: {image_path}")

    for panel_id, panel in panels.items():
        if panel.get("panel_id") != panel_id:
            errors.append(f"Panel key/id mismatch: {panel_id}")
        check_registry(panel_id, "PANEL", "panel")
        if panel.get("parent_region_id") not in regions:
            errors.append(f"{panel_id}: unknown parent region")
        bbox = panel.get("bbox_normalized", [])
        if len(bbox) != 4 or not (0 <= bbox[0] < bbox[2] <= 1 and 0 <= bbox[1] < bbox[3] <= 1):
            errors.append(f"{panel_id}: invalid normalized BBox")
        if panel.get("quantitative"):
            axes = panel.get("axes", {})
            for axis_name in ("x", "y"):
                axis = axes.get(axis_name, {})
                if axis.get("review_status") != "CONFIRMED":
                    warnings.append(f"{panel_id}: quantitative panel {axis_name}-axis has not been independently confirmed")
                if axis.get("unit_status") not in VALID_VISIBILITY:
                    warnings.append(f"{panel_id}: quantitative panel {axis_name}-axis unit status is missing")
        image_path = panel.get("image_path")
        if image_path and workspace is not None and not (workspace / image_path).is_file():
            errors.append(f"{panel_id}: image file does not exist: {image_path}")

    for sample_id, sample in samples.items():
        if sample.get("sample_id") != sample_id:
            errors.append(f"Sample key/id mismatch: {sample_id}")
        check_registry(sample_id, "S", "sample")
        if sample.get("identity_status") not in VALID_MAPPING:
            errors.append(f"{sample_id}: invalid identity_status")

    for result_id, result in results.items():
        if result.get("result_id") != result_id:
            errors.append(f"Result key/id mismatch: {result_id}")
        check_registry(result_id, "R", "result_slot")
        region_ids = result.get("region_ids", [])
        if not region_ids:
            errors.append(f"{result_id}: at least one region_id is required")
        for region_id in region_ids:
            if region_id not in regions:
                errors.append(f"{result_id}: unknown region {region_id}")
        for panel_id in result.get("panel_ids", []):
            if panel_id not in panels:
                errors.append(f"{result_id}: unknown panel {panel_id}")

        origin, legibility = result.get("data_origin"), result.get("visual_legibility")
        permission, epistemic = result.get("quantitative_permission"), result.get("epistemic_status")
        if origin not in VALID_ORIGINS:
            errors.append(f"{result_id}: invalid data_origin")
        if legibility not in VALID_LEGIBILITY:
            errors.append(f"{result_id}: invalid visual_legibility")
        if permission not in VALID_PERMISSION:
            errors.append(f"{result_id}: invalid quantitative_permission")
        if epistemic not in VALID_EPISTEMIC:
            errors.append(f"{result_id}: invalid epistemic_status")
        if bool(result.get("is_visual_estimate", False)) != (origin == "Visual_Estimate"):
            errors.append(f"{result_id}: is_visual_estimate disagrees with data_origin")

        # A numeric result used for the central paper claim must have a verified
        # measurement definition, not merely a display label or derived percentage.
        claim_role = result.get("claim_role", "UNDECIDED")
        if claim_role not in {"UNDECIDED", "CORE", "SUPPORTING", "NOT_USED"}:
            errors.append(f"{result_id}: invalid claim_role")
        definition = result.get("measurement_definition")
        if claim_role == "CORE" and result_is_quantitative(result):
            if not isinstance(definition, dict):
                errors.append(f"{result_id}: CORE quantitative result requires a measurement_definition")
            elif isinstance(definition, dict):
                if definition.get("status") != "VERIFIED":
                    errors.append(f"{result_id}: CORE quantitative result requires measurement_definition.status VERIFIED")
                for field in ("measurand", "raw_signal", "method", "output_unit", "normalization_basis"):
                    if not definition.get(field):
                        errors.append(f"{result_id}: CORE measurement definition is missing {field}")
                if definition.get("is_derived_metric") and not definition.get("formula"):
                    errors.append(f"{result_id}: derived CORE metric requires an explicit calculation formula")
                if definition.get("is_derived_metric") and not definition.get("parent_result_ids"):
                    errors.append(f"{result_id}: derived CORE metric requires parent_result_ids")
        if isinstance(definition, dict):
            if definition.get("status") == "VERIFIED":
                for field in ("measurand", "raw_signal", "method", "output_unit", "normalization_basis"):
                    if not definition.get(field):
                        errors.append(f"{result_id}: VERIFIED measurement definition is missing {field}")
                if definition.get("is_derived_metric") and not definition.get("formula"):
                    errors.append(f"{result_id}: VERIFIED derived metric is missing formula")
            for parent_id in definition.get("parent_result_ids", []):
                if parent_id not in results:
                    errors.append(f"{result_id}: measurement definition references unknown parent Result Unit {parent_id}")
        if origin in {"Visual_Estimate", "Qualitative_Observation", "Unavailable"} and legibility in {"Low", "Unassessable"} and permission == "Exact_Values":
            errors.append(f"{result_id}: low/unassessable image cannot grant Exact_Values permission")
        if origin in {"Visual_Estimate", "Qualitative_Observation"} and permission == "Exact_Values":
            errors.append(f"{result_id}: visual/qualitative origin cannot grant Exact_Values permission")
        if legibility in {"Low", "Unassessable"} and permission not in {"None", "Qualitative_Only"}:
            warnings.append(f"{result_id}: low/unassessable image has non-qualitative permission")
        if origin == "Visual_Estimate":
            texts = [str(result.get("uncertainty_note") or "")]
            texts.extend(str(item.get("description", "")) for item in result.get("observations", []))
            if not any(VISUAL_MARKER in value for value in texts):
                errors.append(f"{result_id}: visual estimate must carry the raw-data warning marker")

        context = result.get("measurement_context")
        if not isinstance(context, dict):
            errors.append(f"{result_id}: measurement_context must be an object")
            context = {}
        for association in context.get("sample_associations", []):
            sample_id, status = association.get("sample_id"), association.get("mapping_status")
            if sample_id and sample_id not in samples:
                errors.append(f"{result_id}: association references unknown sample {sample_id}")
            if status not in VALID_MAPPING:
                errors.append(f"{result_id}: invalid sample mapping status")
            if sample_id in samples and samples[sample_id].get("identity_status") in {"AMBIGUOUS", "UNMAPPED"} and status == "CONFIRMED":
                errors.append(f"{result_id}: association cannot be CONFIRMED when Sample Entity is unresolved")
        for observation in result.get("observations", []):
            if "numeric_value" in observation and observation["numeric_value"] is not None:
                if parse_numeric_scalar(observation["numeric_value"]) is None:
                    errors.append(f"{result_id}: numeric_value must be a finite number or numeric string")
            for item in observation.get("numeric_values", []) or []:
                if parse_numeric_scalar(item) is None:
                    errors.append(f"{result_id}: numeric_values entries must be finite numbers or numeric strings")
            if observation_is_numeric(observation) and (
                permission != "Exact_Values"
                or (origin in {"Visual_Estimate", "Qualitative_Observation", "Unavailable"} and legibility in {"Low", "Unassessable"})
            ):
                errors.append(f"{result_id}: numeric_value forbidden by quantitative_permission")
            if observation.get("sample_id") and observation["sample_id"] not in samples:
                errors.append(f"{result_id}: observation references unknown sample {observation['sample_id']}")
        if permission == "Exact_Values" and not result_has_machine_readable_number(result):
            warnings.append(
                f"{result_id}: Exact_Values result has no machine-readable numeric_value/numeric_values; "
                "values transcribed only into description text are not machine-verifiable"
            )
        checklist = result.get("instrument_checklist", {})
        for group in ("figure_status", "report_status"):
            for field, record in checklist.get(group, {}).items():
                if isinstance(record, dict) and record.get("status") not in VALID_VISIBILITY:
                    errors.append(f"{result_id}: invalid checklist status for {group}.{field}")

    for finding_id, finding in bundle.get("findings", {}).items():
        if finding.get("finding_id") != finding_id:
            errors.append(f"Finding key/id mismatch: {finding_id}")
        check_registry(finding_id, "F", "finding_slot")
        for field in ("supporting_result_ids", "contradictory_result_ids", "audit_target_result_ids", "context_result_ids"):
            for rid in finding.get(field, []):
                if rid not in results:
                    errors.append(f"{finding_id}: {field} references unknown Result Unit {rid}")
        if finding.get("epistemic_status") == "Interpreted" and not finding.get("alternative_explanations"):
            warnings.append(f"{finding_id}: interpreted finding has no alternative_explanations")
    analyses = bundle.get("scientific_analyses", {})
    analyzed_result_ids: set[str] = set()
    for analysis_id, analysis in analyses.items():
        if analysis.get("analysis_id") != analysis_id:
            errors.append(f"{analysis_id}: scientific analysis key/id mismatch")
        if analysis.get("analysis_mode") != "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS":
            errors.append(f"{analysis_id}: invalid analysis_mode")
        if analysis.get("analysis_status") not in {"COMPLETE", "PARTIAL", "NOT_ASSESSABLE"}:
            errors.append(f"{analysis_id}: invalid analysis_status")
        result_ids = analysis.get("result_ids", [])
        result_id_set = set(result_ids)
        if not result_ids or len(result_id_set) != len(result_ids):
            errors.append(f"{analysis_id}: result_ids must be non-empty and unique")
        for result_id in result_ids:
            if result_id not in results:
                errors.append(f"{analysis_id}: unknown Result Unit {result_id}")
        coverage = analysis.get("coverage", [])
        coverage_ids = [item.get("result_id") for item in coverage]
        if set(coverage_ids) != result_id_set or len(coverage_ids) != len(result_id_set):
            errors.append(f"{analysis_id}: coverage must account for each Result Unit exactly once")
        for item in coverage:
            result_id = item.get("result_id")
            status = item.get("status")
            if status not in {"ANALYZED", "NO_COMPARISON_APPLICABLE", "NOT_ASSESSABLE"}:
                errors.append(f"{analysis_id}: invalid coverage status for {result_id}")
            if status in {"NO_COMPARISON_APPLICABLE", "NOT_ASSESSABLE"} and not str(item.get("reason") or "").strip():
                errors.append(f"{analysis_id}: {result_id} requires a reason for {status}")
            if result_id:
                analyzed_result_ids.add(result_id)
        if analysis.get("analysis_status") == "COMPLETE" and any(
            item.get("status") == "NOT_ASSESSABLE" for item in coverage
        ):
            errors.append(f"{analysis_id}: COMPLETE analysis contains NOT_ASSESSABLE coverage")

        observations = analysis.get("observations", [])
        observation_ids = set()
        observation_result_map: dict[str, set[str]] = {}
        for index, observation in enumerate(observations):
            observation_id = observation.get("observation_id")
            if not observation_id or observation_id in observation_ids:
                errors.append(f"{analysis_id}: observations[{index}] has missing/duplicate observation_id")
            observation_ids.add(observation_id)
            if observation.get("epistemic_status") != "Observed":
                errors.append(f"{analysis_id}: observations[{index}] must be Observed")
            refs = observation.get("result_ids", [])
            if not refs or not set(refs).issubset(result_id_set):
                errors.append(f"{analysis_id}: observations[{index}] references Result Units outside its pack")
            observation_result_map[observation_id] = set(refs)
            for ref in observation.get("evidence_refs", []):
                rid = ref.get("result_id")
                if rid not in result_id_set:
                    errors.append(f"{analysis_id}: observation evidence reference is outside its pack")
                    continue
                source_result = results.get(rid, {})
                if ref.get("region_id") and ref["region_id"] not in source_result.get("region_ids", []):
                    errors.append(f"{analysis_id}: observation cites unrelated Region {ref['region_id']}")
                if ref.get("panel_id") and ref["panel_id"] not in source_result.get("panel_ids", []):
                    errors.append(f"{analysis_id}: observation cites unrelated Panel {ref['panel_id']}")
                if not ref.get("region_id") and not ref.get("panel_id"):
                    errors.append(f"{analysis_id}: observation evidence reference lacks Region/Panel")
        for item in coverage:
            if item.get("status") == "ANALYZED":
                ids = set(item.get("observation_ids", []))
                if not ids or not ids.issubset(observation_ids):
                    errors.append(f"{analysis_id}: ANALYZED coverage lacks valid observations for {item.get('result_id')}")
                elif any(item.get("result_id") not in observation_result_map.get(obs_id, set()) for obs_id in ids):
                    errors.append(f"{analysis_id}: coverage observation does not cite {item.get('result_id')}")

        if analysis.get("invocation_audit_required"):
            invocation = analysis.get("model_invocation") or {}
            analyzed_units = any(item.get("status") == "ANALYZED" for item in coverage)
            if analyzed_units and invocation.get("status") != "RESPONSE_RECEIVED":
                errors.append(f"{analysis_id}: ANALYZED coverage requires a completed model invocation receipt")
            if analyzed_units and invocation.get("evidence_level") != "AGENT_REPORTED_RUNTIME_RECEIPT":
                errors.append(f"{analysis_id}: model invocation evidence level is missing or misleading")
            analyzed_asset_result_ids = {
                item.get("result_id") for item in coverage
                if item.get("status") == "ANALYZED"
            }
            request_assets = analysis.get("request_assets", [])
            applicable_assets = []
            for asset in request_assets:
                linked_ids = asset.get("result_ids") or ([asset.get("result_id")] if asset.get("result_id") else [])
                if not linked_ids or (set(linked_ids) & analyzed_asset_result_ids):
                    applicable_assets.append(asset)
            expected_assets = set()
            for asset in applicable_assets:
                if not asset.get("asset_exists") or not asset.get("asset_sha256"):
                    if analyzed_units:
                        errors.append(f"{analysis_id}: ANALYZED coverage references a missing/unhashed image asset")
                    continue
                expected_assets.add((asset.get("image_path"), asset.get("asset_sha256")))
                if workspace is not None and analyzed_units:
                    asset_path = Path(str(asset.get("image_path") or ""))
                    asset_path = asset_path if asset_path.is_absolute() else workspace / asset_path
                    try:
                        asset_path.resolve().relative_to(workspace.resolve())
                    except ValueError:
                        errors.append(f"{analysis_id}: requested image asset path escapes the workspace")
                        continue
                    if not asset_path.is_file():
                        errors.append(f"{analysis_id}: requested image asset is missing: {asset.get('image_path')}")
                    elif sha256_file(asset_path) != asset.get("asset_sha256"):
                        errors.append(f"{analysis_id}: requested image asset SHA-256 changed: {asset.get('image_path')}")
            if analyzed_units and not str(invocation.get("model_id") or "").strip():
                errors.append(f"{analysis_id}: completed model invocation is missing model_id")
            if analyzed_units and expected_assets:
                if invocation.get("input_mode") != "NATIVE_IMAGE_ATTACHMENTS":
                    errors.append(f"{analysis_id}: image-derived ANALYZED coverage lacks native image attachments")
                attached_assets = invocation.get("attached_assets", [])
                received_assets = set()
                for attached in attached_assets:
                    if attached.get("attachment_type") != "NATIVE_IMAGE" or not attached.get("attachment_reference"):
                        errors.append(f"{analysis_id}: native image attachment receipt is incomplete")
                    received_assets.add((attached.get("image_path"), attached.get("asset_sha256")))
                if len(received_assets) != len(attached_assets):
                    errors.append(f"{analysis_id}: duplicate native image attachment receipts were recorded")
                if received_assets != expected_assets:
                    errors.append(f"{analysis_id}: native image attachments do not exactly match requested assets")
            if analyzed_units and workspace is not None:
                for path_field, hash_field in (
                    ("request_log_path", "request_log_sha256"),
                    ("response_log_path", "response_log_sha256"),
                ):
                    relative = invocation.get(path_field)
                    expected_hash = invocation.get(hash_field)
                    if not relative or not expected_hash:
                        errors.append(f"{analysis_id}: invocation receipt is missing {path_field}/{hash_field}")
                        continue
                    artifact = Path(relative)
                    artifact = artifact if artifact.is_absolute() else workspace / artifact
                    try:
                        artifact.resolve().relative_to(workspace.resolve())
                    except ValueError:
                        errors.append(f"{analysis_id}: {path_field} escapes the workspace")
                        continue
                    if not artifact.is_file():
                        errors.append(f"{analysis_id}: {path_field} does not exist")
                    elif sha256_file(artifact) != expected_hash:
                        errors.append(f"{analysis_id}: {hash_field} does not match {path_field}")

        for index, comparison in enumerate(analysis.get("comparisons", [])):
            compare_ids = comparison.get("result_ids", [])
            if len(set(compare_ids)) < 2 or not set(compare_ids).issubset(result_id_set):
                errors.append(f"{analysis_id}: comparisons[{index}] must reference at least two Result Units in its pack")
            if comparison.get("comparison_status") not in {"COMPARABLE", "PARTIALLY_COMPARABLE", "NOT_COMPARABLE", "NOT_APPLICABLE"}:
                errors.append(f"{analysis_id}: comparisons[{index}] has invalid comparison_status")
            dimensions = comparison.get("dimension_assessments")
            if not isinstance(dimensions, list) or not dimensions:
                errors.append(f"{analysis_id}: comparisons[{index}] requires dimension_assessments")
            else:
                for dimension in dimensions:
                    if dimension.get("status") not in {"MATCHED", "MISMATCHED", "UNKNOWN", "NOT_APPLICABLE"}:
                        errors.append(f"{analysis_id}: comparisons[{index}] has invalid dimension status")
            if not str(comparison.get("conclusion") or "").strip():
                errors.append(f"{analysis_id}: comparisons[{index}] requires a conclusion")
            observation_refs = set(comparison.get("observation_ids", []))
            if not observation_refs or not observation_refs.issubset(observation_ids):
                errors.append(f"{analysis_id}: comparisons[{index}] lacks valid observation references")
            for evidence_ref in comparison.get("evidence_refs", []):
                rid = evidence_ref.get("result_id")
                if rid not in compare_ids:
                    errors.append(f"{analysis_id}: comparisons[{index}] cites evidence outside its compared Result Units")
                    continue
                source_result = results.get(rid, {})
                if evidence_ref.get("region_id") and evidence_ref["region_id"] not in source_result.get("region_ids", []):
                    errors.append(f"{analysis_id}: comparisons[{index}] cites unrelated Region {evidence_ref['region_id']}")
                if evidence_ref.get("panel_id") and evidence_ref["panel_id"] not in source_result.get("panel_ids", []):
                    errors.append(f"{analysis_id}: comparisons[{index}] cites unrelated Panel {evidence_ref['panel_id']}")
            for difference in comparison.get("quantitative_differences", []):
                for value in difference.get("values", []):
                    if value.get("result_id") not in compare_ids:
                        errors.append(f"{analysis_id}: quantitative difference references an unrelated Result Unit")

        signal_feature_map = {}
        for index, feature in enumerate(analysis.get("signal_features", [])):
            feature_id = feature.get("feature_id")
            result_id = feature.get("result_id")
            if not feature_id or feature_id in signal_feature_map:
                errors.append(f"{analysis_id}: signal_features[{index}] has missing/duplicate feature_id")
            signal_feature_map[feature_id] = feature
            if result_id not in result_id_set:
                errors.append(f"{analysis_id}: signal_features[{index}] cites a Result Unit outside its pack")
                continue
            if feature.get("feature_type") not in {"PEAK", "BAND", "REFLECTION", "EDGE", "SHOULDER", "PLATEAU", "OTHER"}:
                errors.append(f"{analysis_id}: signal_features[{index}] has invalid feature_type")
            if not str(feature.get("description") or "").strip():
                errors.append(f"{analysis_id}: signal_features[{index}] requires an observed description")
            axes = feature.get("axis_context")
            if not isinstance(axes, dict):
                errors.append(f"{analysis_id}: signal_features[{index}] requires axis_context")
            else:
                for field in ("x_axis_label", "x_axis_unit", "x_axis_scale",
                              "y_axis_label", "y_axis_unit", "y_axis_scale", "normalization_basis"):
                    if not str(axes.get(field) or "").strip():
                        errors.append(f"{analysis_id}: signal_features[{index}].axis_context requires {field}")
                if axes.get("x_axis_scale") not in {"LINEAR", "LOG", "CATEGORICAL", "UNKNOWN"}:
                    errors.append(f"{analysis_id}: signal_features[{index}] has invalid x_axis_scale")
                if axes.get("y_axis_scale") not in {"LINEAR", "LOG", "CATEGORICAL", "UNKNOWN"}:
                    errors.append(f"{analysis_id}: signal_features[{index}] has invalid y_axis_scale")
            if not str(feature.get("series_label") or "").strip():
                errors.append(f"{analysis_id}: signal_features[{index}] requires series_label or UNKNOWN")
            for ref in feature.get("evidence_refs", []):
                if ref.get("result_id") != result_id:
                    errors.append(f"{analysis_id}: signal_features[{index}] evidence cites another Result Unit")
                source_result = results.get(result_id, {})
                if ref.get("region_id") and ref["region_id"] not in source_result.get("region_ids", []):
                    errors.append(f"{analysis_id}: signal_features[{index}] cites an unrelated Region")
                if ref.get("panel_id") and ref["panel_id"] not in source_result.get("panel_ids", []):
                    errors.append(f"{analysis_id}: signal_features[{index}] cites an unrelated Panel")
                if not ref.get("region_id") and not ref.get("panel_id"):
                    errors.append(f"{analysis_id}: signal_features[{index}] lacks a Region/Panel evidence anchor")
            for metric in ("position", "width", "intensity", "area"):
                estimate = feature.get(metric) or {}
                value = estimate.get("value")
                if value is not None:
                    if parse_numeric_scalar(value) is None:
                        errors.append(f"{analysis_id}: signal_features[{index}].{metric} must be finite numeric")
                    for field in ("unit", "reading_basis", "precision_or_uncertainty"):
                        if not str(estimate.get(field) or "").strip():
                            errors.append(f"{analysis_id}: signal_features[{index}].{metric} requires {field}")
                    if metric in {"intensity", "area"} and not str(
                        estimate.get("normalization_basis") or (axes or {}).get("normalization_basis") or ""
                    ).strip():
                        errors.append(f"{analysis_id}: signal_features[{index}].{metric} requires normalization_basis")

        seen_signal_comparisons = set()
        signal_comparison_map = {}
        for index, comparison in enumerate(analysis.get("signal_comparisons", [])):
            comparison_id = comparison.get("comparison_id")
            if not comparison_id or comparison_id in seen_signal_comparisons:
                errors.append(f"{analysis_id}: signal_comparisons[{index}] has missing/duplicate comparison_id")
            seen_signal_comparisons.add(comparison_id)
            signal_comparison_map[comparison_id] = comparison
            feature_ids = comparison.get("feature_ids", [])
            if len(set(feature_ids)) < 2 or not set(feature_ids).issubset(signal_feature_map):
                errors.append(f"{analysis_id}: signal_comparisons[{index}] must reference at least two recorded signal features")
            compare_ids = comparison.get("result_ids", [])
            if not compare_ids or not set(compare_ids).issubset(result_id_set):
                errors.append(f"{analysis_id}: signal_comparisons[{index}] references Result Units outside its pack")
            feature_result_ids = {signal_feature_map.get(fid, {}).get("result_id") for fid in feature_ids}
            if feature_result_ids != set(compare_ids):
                errors.append(f"{analysis_id}: signal_comparisons[{index}] feature/result mapping is inconsistent")
            evidence_result_ids = {ref.get("result_id") for ref in comparison.get("evidence_refs", [])}
            if not set(compare_ids).issubset(evidence_result_ids):
                errors.append(f"{analysis_id}: signal_comparisons[{index}] lacks source evidence for every compared Result Unit")
            if comparison.get("change_type") not in {"POSITION_SHIFT", "WIDTH_CHANGE", "INTENSITY_CHANGE", "AREA_CHANGE", "APPEARED", "DISAPPEARED", "SHAPE_CHANGE", "OTHER"}:
                errors.append(f"{analysis_id}: signal_comparisons[{index}] has invalid change_type")
            if comparison.get("comparability_status") not in {"COMPARABLE", "PARTIALLY_COMPARABLE", "NOT_COMPARABLE", "NOT_APPLICABLE", "UNKNOWN"}:
                errors.append(f"{analysis_id}: signal_comparisons[{index}] has invalid comparability_status")
            if not str(comparison.get("description") or "").strip():
                errors.append(f"{analysis_id}: signal_comparisons[{index}] requires an observed description")
            for ref in comparison.get("evidence_refs", []):
                if ref.get("result_id") not in compare_ids:
                    errors.append(f"{analysis_id}: signal_comparisons[{index}] evidence is outside its comparison set")
                    continue
                source_result = results.get(ref.get("result_id"), {})
                if ref.get("region_id") and ref["region_id"] not in source_result.get("region_ids", []):
                    errors.append(f"{analysis_id}: signal_comparisons[{index}] cites an unrelated Region")
                if ref.get("panel_id") and ref["panel_id"] not in source_result.get("panel_ids", []):
                    errors.append(f"{analysis_id}: signal_comparisons[{index}] cites an unrelated Panel")
                if not ref.get("region_id") and not ref.get("panel_id"):
                    errors.append(f"{analysis_id}: signal_comparisons[{index}] lacks a Region/Panel evidence anchor")
            quantified = comparison.get("quantified_change") or {}
            if quantified.get("value") is not None:
                if parse_numeric_scalar(quantified.get("value")) is None:
                    errors.append(f"{analysis_id}: signal_comparisons[{index}] quantified change must be finite numeric")
                for field in ("unit", "source_basis", "precision_or_uncertainty"):
                    if not str(quantified.get(field) or "").strip():
                        errors.append(f"{analysis_id}: signal_comparisons[{index}] quantified change requires {field}")

        if analysis.get("invocation_audit_required"):
            signal_coverage = analysis.get("signal_analysis_coverage", [])
            signal_coverage_ids = [item.get("result_id") for item in signal_coverage]
            if set(signal_coverage_ids) != result_id_set or len(signal_coverage_ids) != len(result_id_set):
                errors.append(f"{analysis_id}: signal_analysis_coverage must disposition each Result Unit exactly once")
            feature_owner = {}
            signal_coverage_map = {}
            for item in signal_coverage:
                result_id = item.get("result_id")
                status = item.get("status")
                if status not in {"APPLICABLE", "NOT_APPLICABLE", "NOT_ASSESSABLE"}:
                    errors.append(f"{analysis_id}: invalid signal-analysis coverage status for {result_id}")
                if status in {"NOT_APPLICABLE", "NOT_ASSESSABLE"} and not str(item.get("reason") or "").strip():
                    errors.append(f"{analysis_id}: {result_id} requires a signal-analysis coverage reason")
                feature_ids = item.get("feature_ids", [])
                if status == "APPLICABLE" and not feature_ids:
                    errors.append(f"{analysis_id}: {result_id} is APPLICABLE but has no signal_features")
                if any(feature_id not in signal_feature_map or signal_feature_map[feature_id].get("result_id") != result_id for feature_id in feature_ids):
                    errors.append(f"{analysis_id}: {result_id} references unrelated/unknown signal feature IDs")
                for feature_id in feature_ids:
                    feature_owner[feature_id] = result_id
                comparison_ids = item.get("comparison_ids", [])
                if not set(comparison_ids).issubset(seen_signal_comparisons):
                    errors.append(f"{analysis_id}: {result_id} references unknown signal comparison IDs")
                if any(result_id not in signal_comparison_map.get(comparison_id, {}).get("result_ids", []) for comparison_id in comparison_ids):
                    errors.append(f"{analysis_id}: {result_id} references a signal comparison that does not include it")
                if status == "APPLICABLE" and not comparison_ids and not str(item.get("reason") or "").strip():
                    errors.append(f"{analysis_id}: {result_id} must explain why no signal comparison was possible")
            for feature_id, feature in signal_feature_map.items():
                if feature_owner.get(feature_id) != feature.get("result_id"):
                    errors.append(f"{analysis_id}: {feature_id} is not linked from its Result Unit signal coverage")
            for comparison_id, comparison in signal_comparison_map.items():
                for result_id in comparison.get("result_ids", []):
                    if comparison_id not in signal_coverage_map.get(result_id, {}).get("comparison_ids", []):
                        errors.append(f"{analysis_id}: {comparison_id} is not linked from every compared Result Unit signal coverage")

        for index, relationship in enumerate(analysis.get("relationships", [])):
            refs = relationship.get("result_ids", [])
            if not refs or not set(refs).issubset(result_id_set):
                errors.append(f"{analysis_id}: relationships[{index}] references Result Units outside its pack")
            if not set(relationship.get("observation_ids", [])).issubset(observation_ids):
                errors.append(f"{analysis_id}: relationships[{index}] references unknown observations")
            if relationship.get("causal_status") not in {"NOT_ESTABLISHED", "SUPPORTED_WITH_CONTROLS", "ESTABLISHED_BY_DESIGN"}:
                errors.append(f"{analysis_id}: relationships[{index}] has invalid causal_status")

        for index, interpretation in enumerate(analysis.get("interpretations", [])):
            if interpretation.get("epistemic_status") not in {"Interpreted", "Hypothesized"}:
                errors.append(f"{analysis_id}: interpretations[{index}] has invalid epistemic_status")
            refs = set(interpretation.get("supporting_observation_ids", []))
            if not refs or not refs.issubset(observation_ids):
                errors.append(f"{analysis_id}: interpretations[{index}] lacks valid supporting observations")
            if not interpretation.get("alternative_explanations"):
                errors.append(f"{analysis_id}: interpretations[{index}] requires alternative_explanations")

        for index, contradiction in enumerate(analysis.get("contradictions", [])):
            refs = contradiction.get("result_ids", [])
            if not refs or not set(refs).issubset(result_id_set):
                errors.append(f"{analysis_id}: contradictions[{index}] references Result Units outside its pack")
            for ref in contradiction.get("evidence_refs", []):
                if ref.get("result_id") not in result_id_set:
                    errors.append(f"{analysis_id}: contradiction evidence reference is outside its pack")

    figure_errors, figure_warnings = validate_figure_candidate_coverage(bundle, workspace)
    errors.extend(figure_errors)
    warnings.extend(figure_warnings)

    uncovered_analysis_results = sorted(set(results) - analyzed_result_ids)
    if results and uncovered_analysis_results:
        warnings.append(
            "Result Units not yet covered by general scientific analysis: "
            + ", ".join(uncovered_analysis_results)
        )

    spectral_pattern = r"\braman\b|\bftir\b|\bft-ir\b|\binfrared\b|\bir spectroscopy\b"
    spectral_result_ids = [
        result_id for result_id, result in results.items()
        if re.search(spectral_pattern,
                     " ".join(str(value or "") for value in (
                         result.get("data_type"),
                         result.get("measurement_context", {}).get("technique"),
                     )), re.I)
    ]
    comparisons = bundle.get("spectral_comparisons", {})
    legacy_spectral_covered = {rid for item in comparisons.values() for rid in item.get("result_ids", [])}
    if spectral_result_ids and (set(spectral_result_ids) - legacy_spectral_covered - analyzed_result_ids):
        warnings.append(
            "Raman/FTIR Result Units exist but no joint spectral_comparisons are recorded; "
            "independent single-image inspections do not satisfy cross-sample comparison."
        )
    for comparison_id, comparison in comparisons.items():
        if comparison.get("comparison_id") != comparison_id:
            errors.append(f"{comparison_id}: spectral comparison key/id mismatch")
        if comparison.get("comparison_mode") != "SPECTRAL_CROSS_SAMPLE":
            errors.append(f"{comparison_id}: invalid comparison_mode")
        if comparison.get("comparison_status") not in {"COMPLETE", "PARTIAL", "NOT_COMPARABLE"}:
            errors.append(f"{comparison_id}: invalid comparison_status")
        compared_ids = comparison.get("result_ids", [])
        if not compared_ids:
            errors.append(f"{comparison_id}: result_ids must not be empty")
        for result_id in compared_ids:
            if result_id not in results:
                errors.append(f"{comparison_id}: unknown Result Unit {result_id}")
            elif not re.search(
                spectral_pattern,
                " ".join(str(value or "") for value in (
                    results[result_id].get("data_type"),
                    results[result_id].get("measurement_context", {}).get("technique"),
                )), re.I
            ):
                errors.append(f"{comparison_id}: {result_id} is not a Raman/FTIR Result Unit")
        assessment = comparison.get("comparability_assessment", {})
        if assessment.get("status") not in {"COMPARABLE", "PARTIALLY_COMPARABLE", "NOT_COMPARABLE", "UNKNOWN"}:
            errors.append(f"{comparison_id}: missing/invalid comparability_assessment.status")
        if not str(comparison.get("summary") or "").strip():
            errors.append(f"{comparison_id}: comparative summary is missing")
        for observation in comparison.get("direct_observations", []):
            if not set(observation.get("result_ids", [])).issubset(set(compared_ids)):
                errors.append(f"{comparison_id}: direct observation references a Result Unit outside its comparison set")
        for band in comparison.get("band_comparisons", []):
            if not set(band.get("result_ids", [])).issubset(set(compared_ids)):
                errors.append(f"{comparison_id}: band comparison references a Result Unit outside its comparison set")
            for evidence_ref in band.get("evidence_refs", []):
                if evidence_ref.get("result_id") not in compared_ids:
                    errors.append(f"{comparison_id}: band evidence reference is outside its comparison set")

    covered_spectral_result_ids = {
        result_id for comparison in comparisons.values()
        for result_id in comparison.get("result_ids", [])
    }
    uncovered_spectral_result_ids = sorted(set(spectral_result_ids) - covered_spectral_result_ids - analyzed_result_ids)
    if uncovered_spectral_result_ids:
        warnings.append(
            "Raman/FTIR Result Units are not covered by a recorded joint comparison: "
            + ", ".join(uncovered_spectral_result_ids)
        )

    errors.extend(validate_finding_analysis_refs(bundle))

    quality_errors, quality_warnings = validate_evidence_quality(bundle)
    errors.extend(quality_errors)
    warnings.extend(quality_warnings)
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    errors, warnings = validate(bundle, workspace)
    paths = workspace_paths(workspace)
    try:
        source_pdf = workspace / "source" / "original_report.pdf"
        if not source_pdf.is_file():
            errors.append("Original source PDF is missing")
        elif sha256_file(source_pdf) != bundle.get("source", {}).get("sha256"):
            errors.append("Original source PDF hash does not match Evidence Bundle")
    except OSError as exc:
        errors.append(f"Could not verify source PDF: {exc}")
    report = {"status": "ERROR" if errors else ("WARNING" if warnings else "PASS"), "errors": errors, "warnings": warnings}
    atomic_write_json(args.report or paths["state"] / "validation_evidence.json", report)
    if paths["manifest"].exists():
        manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
        manifest.setdefault("validation", {})["evidence"] = report
        if not errors:
            manifest["stage"] = "EVIDENCE_AUDITED"
        atomic_write_json(paths["manifest"], manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
