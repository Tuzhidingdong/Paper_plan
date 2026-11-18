"""Cross-cutting scientific quality gates for evidence and manuscript bundles.

These checks complement JSON Schema: they validate semantic provenance, visual
comparability, quantitative-fit reproducibility and route-selection rationale.
They deliberately avoid domain/sample-specific rules.
"""
from __future__ import annotations

import math
import re
from typing import Any

PAGE_PATTERN = re.compile(r"\b(?:pdf\s*)?p(?:age)?\.?\s*(\d+)\b", re.IGNORECASE)
FIT_METHOD_PATTERN = re.compile(
    r"\b(?:least[\s-]*squares|linear\s+fit|regression|curve\s+fit|fitting\s+model)\b",
    re.IGNORECASE,
)
IMAGE_PATTERN = re.compile(
    r"\b(?:sem|tem|microscop\w*|micrograph\w*|image[- ]based|optical\s+image)\b",
    re.IGNORECASE,
)
VISUAL_ORIGINS = {"Visual_Estimate", "Qualitative_Observation"}
VISUAL_DIMENSIONS = {
    "imaging_modality",
    "magnification_or_pixel_size",
    "scale_bar_or_spatial_calibration",
    "specimen_state_and_preparation",
    "image_processing_and_contrast",
    "field_selection_and_sampling",
}
VISUAL_DIMENSION_ALIASES = {
    "modality": "imaging_modality",
    "imaging_mode": "imaging_modality",
    "magnification": "magnification_or_pixel_size",
    "pixel_size": "magnification_or_pixel_size",
    "spatial_scale": "magnification_or_pixel_size",
    "scale_bar": "scale_bar_or_spatial_calibration",
    "scale_bar_or_calibration": "scale_bar_or_spatial_calibration",
    "sample_state": "specimen_state_and_preparation",
    "specimen_state": "specimen_state_and_preparation",
    "sample_preparation": "specimen_state_and_preparation",
    "image_processing": "image_processing_and_contrast",
    "contrast": "image_processing_and_contrast",
    "field_selection": "field_selection_and_sampling",
    "sampling": "field_selection_and_sampling",
    "number_of_fields": "field_selection_and_sampling",
}


def _page_numbers(source_location: Any) -> set[int]:
    if not isinstance(source_location, str):
        return set()
    return {int(value) for value in PAGE_PATTERN.findall(source_location)}


def _has_caption_blind_inspection(bundle: dict[str, Any], entity_id: str) -> bool:
    history = bundle.get("visual_inspections", {}).get(entity_id, {})
    if not isinstance(history, dict):
        return False
    cards = []
    if isinstance(history.get("initial"), dict):
        cards.append(history["initial"])
    cards.extend(item for item in history.get("reinspections", []) if isinstance(item, dict))
    for card in cards:
        if (
            card.get("inspection_mode") == "CAPTION_BLIND"
            and card.get("caption_text_included") is False
            and card.get("report_narrative_included") is False
            and card.get("visual_legibility") in {"High", "Medium", "Low", "Unassessable"}
        ):
            return True
    return False


def validate_evidence_integrity(bundle: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Reject misleading Region links and unrecorded visual observations."""
    errors: list[str] = []
    warnings: list[str] = []
    regions = bundle.get("regions", {})
    panels = bundle.get("panels", {})

    for result_id, result in bundle.get("result_units", {}).items():
        region_ids = result.get("region_ids", [])
        linked_regions = [(rid, regions.get(rid)) for rid in region_ids if rid in regions]
        for region_id, region in linked_regions:
            if region.get("triage_role") == "REPEATED_LAYOUT_ASSET":
                errors.append(
                    f"{result_id}: Region {region_id} is a repeated header/footer layout asset "
                    "and cannot serve as a scientific evidence anchor"
                )

        cited_pages = _page_numbers(result.get("source_location"))
        if cited_pages:
            page_matches = [
                (region_id, region)
                for region_id, region in linked_regions
                if region.get("page_number") in cited_pages
                and region.get("triage_role") != "REPEATED_LAYOUT_ASSET"
            ]
            if not page_matches:
                linked_pages = sorted({
                    region.get("page_number")
                    for _, region in linked_regions
                    if isinstance(region.get("page_number"), int)
                })
                errors.append(
                    f"{result_id}: source_location cites PDF page(s) "
                    f"{sorted(cited_pages)}, but no usable linked Region is anchored to those pages "
                    f"(linked pages: {linked_pages})"
                )

        if result.get("data_origin") in VISUAL_ORIGINS:
            inspection_entities = set(region_ids)
            for panel_id in result.get("panel_ids", []):
                inspection_entities.add(panel_id)
                panel = panels.get(panel_id, {})
                if panel.get("parent_region_id"):
                    inspection_entities.add(panel["parent_region_id"])
            if not any(
                _has_caption_blind_inspection(bundle, entity_id)
                for entity_id in inspection_entities
            ):
                errors.append(
                    f"{result_id}: image-derived {result.get('data_origin')} evidence "
                    "requires a recorded CAPTION_BLIND visual inspection of a linked Region or Panel"
                )

    return errors, warnings


def _numeric_vector(result: dict[str, Any], observation_index: Any) -> list[float] | None:
    if not isinstance(observation_index, int) or isinstance(observation_index, bool):
        return None
    observations = result.get("observations", [])
    if observation_index < 0 or observation_index >= len(observations):
        return None
    observation = observations[observation_index]
    raw = observation.get("numeric_values")
    if not isinstance(raw, list) or len(raw) < 3:
        return None
    values: list[float] = []
    for value in raw:
        if isinstance(value, bool):
            return None
        try:
            parsed = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if not math.isfinite(parsed):
            return None
        values.append(parsed)
    return values


def _ordinary_least_squares(x_values: list[float], y_values: list[float]) -> tuple[float, float, float] | None:
    if len(x_values) != len(y_values) or len(x_values) < 3:
        return None
    mean_x = sum(x_values) / len(x_values)
    mean_y = sum(y_values) / len(y_values)
    sxx = sum((value - mean_x) ** 2 for value in x_values)
    syy = sum((value - mean_y) ** 2 for value in y_values)
    if sxx <= 0 or syy <= 0:
        return None
    sxy = sum(
        (x_value - mean_x) * (y_value - mean_y)
        for x_value, y_value in zip(x_values, y_values)
    )
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    residual_sum = sum(
        (y_value - (intercept + slope * x_value)) ** 2
        for x_value, y_value in zip(x_values, y_values)
    )
    r_squared = 1.0 - residual_sum / syy
    return slope, intercept, r_squared


def _audit_reported_value(
    observations: list[dict[str, Any]],
    reported_observation_index: Any,
    value_indices: dict[str, Any],
    parameter: str,
) -> float | None:
    if not isinstance(reported_observation_index, int) or isinstance(reported_observation_index, bool):
        return None
    if reported_observation_index < 0 or reported_observation_index >= len(observations):
        return None
    values = observations[reported_observation_index].get("numeric_values")
    index = value_indices.get(parameter)
    if not isinstance(values, list) or not isinstance(index, int) or isinstance(index, bool):
        return None
    if index < 0 or index >= len(values):
        return None
    try:
        value = float(values[index])
    except (TypeError, ValueError, OverflowError):
        return None
    return value if math.isfinite(value) else None


def validate_fit_reproducibility(bundle: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Recompute declared OLS fits from linked, machine-readable source observations."""
    errors: list[str] = []
    warnings: list[str] = []
    results = bundle.get("result_units", {})

    for result_id, result in results.items():
        definition = result.get("measurement_definition") or {}
        method = str(definition.get("method") or "")
        is_statistical_fit = bool(definition.get("is_derived_metric")) and bool(
            FIT_METHOD_PATTERN.search(method)
        )
        if not is_statistical_fit:
            continue

        audits = result.get("calculation_audits", [])
        core = result.get("claim_role") == "CORE"
        if not isinstance(audits, list) or not audits:
            message = (
                f"{result_id}: statistical-fit Result Unit requires calculation_audits "
                "with source-linked x/y vectors and printed-parameter precision"
            )
            (errors if core else warnings).append(message)
            continue

        for audit_index, audit in enumerate(audits, start=1):
            owner = f"{result_id} calculation_audits[{audit_index}]"
            if audit.get("audit_type") != "OLS_LINEAR_FIT":
                errors.append(f"{owner}: unsupported audit_type; expected OLS_LINEAR_FIT")
                continue

            x_ref, y_ref = audit.get("x_source", {}), audit.get("y_source", {})
            x_result_id, y_result_id = x_ref.get("result_id"), y_ref.get("result_id")
            if x_result_id not in results or y_result_id not in results:
                errors.append(f"{owner}: x_source/y_source references an unknown Result Unit")
                continue
            x_values = _numeric_vector(results[x_result_id], x_ref.get("observation_index"))
            y_values = _numeric_vector(results[y_result_id], y_ref.get("observation_index"))
            if x_values is None or y_values is None:
                errors.append(
                    f"{owner}: source references must resolve to numeric_values vectors "
                    "with at least three finite observations"
                )
                continue
            computed = _ordinary_least_squares(x_values, y_values)
            if computed is None:
                errors.append(f"{owner}: OLS cannot be computed (length mismatch or zero variance)")
                continue
            slope, intercept, r_squared = computed

            reported_source = audit.get("reported_source", {})
            if reported_source.get("result_id", result_id) != result_id:
                errors.append(f"{owner}: reported_source must point to the Result Unit being audited")
                continue
            value_indices = reported_source.get("value_indices", {})
            precision = audit.get("displayed_precision", {})
            reported_values = {
                "slope": _audit_reported_value(
                    result.get("observations", []),
                    reported_source.get("observation_index"),
                    value_indices,
                    "slope",
                ),
                "intercept": _audit_reported_value(
                    result.get("observations", []),
                    reported_source.get("observation_index"),
                    value_indices,
                    "intercept",
                ),
                "r_squared": _audit_reported_value(
                    result.get("observations", []),
                    reported_source.get("observation_index"),
                    value_indices,
                    "r_squared",
                ),
            }
            computed_values = {
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_squared,
            }
            mismatches = []
            for parameter, computed_value in computed_values.items():
                digits = precision.get(parameter)
                reported_value = reported_values[parameter]
                if (
                    not isinstance(digits, int)
                    or isinstance(digits, bool)
                    or digits < 0
                    or digits > 12
                    or reported_value is None
                ):
                    mismatches.append(f"{parameter} has no valid reported value/precision")
                    continue
                # A printed decimal rounded to d places has a transparent
                # half-unit-in-the-last-place reproduction tolerance.
                tolerance = 0.5 * (10 ** (-digits)) + 1e-12
                if abs(computed_value - reported_value) > tolerance:
                    mismatches.append(
                        f"{parameter}: recomputed {computed_value:.12g} vs printed "
                        f"{reported_value:.12g} (rounding tolerance {tolerance:.3g})"
                    )
            if mismatches:
                message = f"{owner}: OLS fit is NOT_REPRODUCED; " + "; ".join(mismatches)
                (errors if core else warnings).append(message)

    return errors, warnings


def _visual_dimension_id(label: Any) -> str | None:
    text = re.sub(r"[^a-z0-9]+", "_", str(label or "").strip().casefold()).strip("_")
    if text in VISUAL_DIMENSIONS:
        return text
    return VISUAL_DIMENSION_ALIASES.get(text)


def _claim_result_roles(
    claim: dict[str, Any],
    findings: dict[str, Any],
) -> dict[str, set[str]]:
    result_roles: dict[str, set[str]] = {}
    finding_lists = {
        "supporting_result_ids": "SUPPORTS_CLAIM",
        "contradictory_result_ids": "CONTRADICTS_CLAIM",
        "audit_target_result_ids": "AUDIT_TARGET",
        "context_result_ids": "CONTEXT_ONLY",
    }
    for reference in claim.get("evidence_refs", []):
        kind, ref_id = reference.get("kind"), reference.get("id")
        role = reference.get("evidence_role", "SUPPORTS_CLAIM")
        if kind == "result_unit":
            result_roles.setdefault(ref_id, set()).add(role)
        elif kind == "finding":
            finding = findings.get(ref_id, {})
            if role == "SUPPORTS_CLAIM":
                for field, child_role in finding_lists.items():
                    for result_id in finding.get(field, []):
                        result_roles.setdefault(result_id, set()).add(child_role)
            else:
                for field in finding_lists:
                    for result_id in finding.get(field, []):
                        result_roles.setdefault(result_id, set()).add(role)
    return result_roles


def validate_visual_claim_comparability(
    package: dict[str, Any],
    framework: dict[str, Any],
    evidence: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Require explicit acquisition/scale comparability for multi-image claims."""
    errors: list[str] = []
    warnings: list[str] = []
    result_units = evidence.get("result_units", {})
    findings = evidence.get("findings", {})
    claims = framework.get("claims", {})
    assessments = package.get("comparability_assessments", {})

    for claim_id, claim in claims.items():
        roles = _claim_result_roles(claim, findings)
        image_result_ids = []
        for result_id, result_roles in roles.items():
            if not result_roles.intersection({"SUPPORTS_CLAIM", "CONTRADICTS_CLAIM"}):
                continue
            result = result_units.get(result_id, {})
            descriptor = " ".join([
                str(result.get("data_type") or ""),
                str((result.get("measurement_context") or {}).get("technique") or ""),
            ])
            if result.get("data_origin") in VISUAL_ORIGINS or IMAGE_PATTERN.search(descriptor):
                image_result_ids.append(result_id)
        image_result_ids = sorted(set(image_result_ids))
        if len(image_result_ids) < 2:
            continue

        linked_ids = list(claim.get("comparability_assessment_ids", []))
        linked_ids.extend(
            assessment_id
            for assessment_id, assessment in assessments.items()
            if claim_id in assessment.get("claim_ids", [])
        )
        linked_ids = sorted(set(linked_ids))
        if not linked_ids:
            errors.append(
                f"{claim_id}: claim uses multiple image-derived Result Units "
                f"{', '.join(image_result_ids)} without a linked visual comparability assessment"
            )
            continue

        for assessment_id in linked_ids:
            assessment = assessments.get(assessment_id)
            if not isinstance(assessment, dict):
                continue
            visual_dimensions = {}
            for dimension in assessment.get("dimensions", []):
                dimension_id = _visual_dimension_id(dimension.get("dimension"))
                if dimension_id:
                    visual_dimensions[dimension_id] = dimension
            missing = sorted(VISUAL_DIMENSIONS - set(visual_dimensions))
            if missing:
                errors.append(
                    f"{assessment_id}: visual comparison lacks required dimensions: "
                    + ", ".join(missing)
                )
                continue

            statuses = {
                key: visual_dimensions[key].get("match_status")
                for key in VISUAL_DIMENSIONS
            }
            nonmatched = {
                key: status for key, status in statuses.items()
                if status in {"MISMATCHED", "UNKNOWN"}
            }
            if assessment.get("assessment_status") == "COMPARABLE" and nonmatched:
                errors.append(
                    f"{assessment_id}: visual comparison cannot be COMPARABLE while "
                    "scale/acquisition/specimen dimensions are mismatched or unknown"
                )
            if nonmatched and not assessment.get("prohibited_inference"):
                errors.append(
                    f"{assessment_id}: mismatched/unknown visual dimensions require "
                    "explicit prohibited_inference statements"
                )
            if nonmatched and not assessment.get("limitations"):
                errors.append(
                    f"{assessment_id}: mismatched/unknown visual dimensions require "
                    "explicit limitations"
                )

    return errors, warnings


def validate_route_selection(routes_bundle: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Require a transparent decision record when a preferred route is nominated."""
    errors: list[str] = []
    warnings: list[str] = []
    routes = routes_bundle.get("routes", {})
    selected_id = routes_bundle.get("recommended_route_id")
    if not selected_id:
        return errors, warnings
    if selected_id not in routes:
        errors.append(f"recommended_route_id references unknown route {selected_id}")
        return errors, warnings

    decision = routes_bundle.get("route_decision")
    if not isinstance(decision, dict):
        errors.append(
            "recommended_route_id requires a structured route_decision with "
            "selection criteria and explicit assessment of alternatives"
        )
        return errors, warnings
    if decision.get("selected_route_id") != selected_id:
        errors.append("route_decision.selected_route_id must match recommended_route_id")
    rationale = decision.get("selection_rationale")
    if not isinstance(rationale, str) or len(rationale.strip()) < 40:
        errors.append("route_decision.selection_rationale must explain the evidence-based selection")
    criteria = decision.get("selection_criteria", [])
    if not isinstance(criteria, list) or len(criteria) < 3 or any(
        not isinstance(item, str) or len(item.strip()) < 8 for item in criteria
    ):
        errors.append("route_decision.selection_criteria must contain at least three substantive criteria")

    alternatives = decision.get("alternatives_considered", [])
    alternative_ids = set()
    for alternative in alternatives if isinstance(alternatives, list) else []:
        route_id = alternative.get("route_id")
        if route_id == selected_id:
            errors.append("route_decision alternatives_considered must not repeat the selected route")
            continue
        if route_id not in routes:
            errors.append(f"route_decision references unknown alternative route {route_id}")
            continue
        alternative_ids.add(route_id)
        if alternative.get("disposition") not in {"DEFERRED", "REJECTED", "MERGED", "NOT_SELECTED"}:
            errors.append(f"{route_id}: alternative route disposition is missing or invalid")
        if not isinstance(alternative.get("rationale"), str) or len(alternative["rationale"].strip()) < 30:
            errors.append(f"{route_id}: alternative route requires a substantive disposition rationale")
    required_alternatives = set(routes) - {selected_id}
    missing_alternatives = sorted(required_alternatives - alternative_ids)
    if missing_alternatives:
        errors.append(
            "route_decision must explicitly assess every non-selected candidate route: "
            + ", ".join(missing_alternatives)
        )
    return errors, warnings


def validate_evidence_quality(bundle: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors, warnings = validate_evidence_integrity(bundle)
    fit_errors, fit_warnings = validate_fit_reproducibility(bundle)
    errors.extend(fit_errors)
    warnings.extend(fit_warnings)
    return errors, warnings
