#!/usr/bin/env python3
"""Deterministic structural and numeric-permission validator for the Evidence Bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scientific_quality_gates import validate_evidence_quality

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
