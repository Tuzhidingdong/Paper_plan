"""Cross-cutting scientific quality gates for evidence and manuscript bundles.

These checks complement JSON Schema: they validate semantic provenance, visual
comparability, quantitative-fit reproducibility and route-selection rationale.
They deliberately avoid domain/sample-specific rules.
"""
from __future__ import annotations

import math
import re
from typing import Any

PAGE_PATTERN = re.compile(r"\b(?:pdf\s*)?pp?\.?\s*(\d+)\b", re.IGNORECASE)
FIT_METHOD_PATTERN = re.compile(
    r"\b(?:ols|ordinary\s+least\s+squares|least[\s-]*squares|linear\s+(?:fit|fitting|fitted)|regression|curve\s+(?:fit|fitting)|fitting\s+model)\b",
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
    cards = _inspection_cards(bundle, entity_id)
    for card in cards:
        if (
            card.get("inspection_mode") == "CAPTION_BLIND"
            and card.get("caption_text_included") is False
            and card.get("report_narrative_included") is False
            and card.get("visual_legibility") in {"High", "Medium", "Low", "Unassessable"}
        ):
            return True
    return False


def _inspection_cards(bundle: dict[str, Any], entity_id: str) -> list[dict[str, Any]]:
    history = bundle.get("visual_inspections", {}).get(entity_id, {})
    if not isinstance(history, dict):
        return []
    cards = []
    if isinstance(history.get("initial"), dict):
        cards.append(history["initial"])
    cards.extend(item for item in history.get("reinspections", []) if isinstance(item, dict))
    return cards


def _visual_metadata_errors(bundle: dict[str, Any], entity_id: str) -> list[str]:
    """Require contemporaneous, explicit visual-acquisition metadata for a linked crop."""
    errors: list[str] = []
    cards = _inspection_cards(bundle, entity_id)
    valid_cards = [
        card for card in cards
        if card.get("inspection_mode") == "CAPTION_BLIND"
        and card.get("caption_text_included") is False
        and card.get("report_narrative_included") is False
    ]
    if not valid_cards:
        return [f"{entity_id}: visual metadata must be recorded in a linked CAPTION_BLIND inspection card"]

    required = set(VISUAL_DIMENSIONS)
    assessed = False
    recorded_status = False
    for card in valid_cards:
        metadata = card.get("visual_metadata_assessment")
        if not isinstance(metadata, dict):
            continue
        assessed = True
        if metadata.get("status") != "RECORDED":
            continue
        recorded_status = True
        dimensions = metadata.get("dimensions", [])
        by_dimension: dict[str, dict[str, Any]] = {}
        for item in dimensions if isinstance(dimensions, list) else []:
            if not isinstance(item, dict):
                continue
            dimension_id = _visual_dimension_id(item.get("dimension"))
            if not dimension_id:
                continue
            if dimension_id in by_dimension:
                errors.append(f"{entity_id}: visual metadata dimension {dimension_id} is recorded more than once")
            by_dimension[dimension_id] = item
        missing = sorted(required - set(by_dimension))
        if missing:
            errors.append(f"{entity_id}: visual metadata record lacks explicit states for: " + ", ".join(missing))
            continue
        for dimension_id in required:
            item = by_dimension[dimension_id]
            status = item.get("status")
            if status not in {"OBSERVED", "NOT_PRESENT", "NOT_LEGIBLE", "NOT_APPLICABLE", "UNKNOWN"}:
                errors.append(f"{entity_id}: visual metadata {dimension_id} has a missing/invalid status")
                continue
            if item.get("recording_method") not in {
                "SOURCE_METADATA", "INSTRUMENT_METADATA", "SCALE_BAR_READ",
                "VISUAL_REVIEW", "USER_CONFIRMED", "OTHER"
            }:
                errors.append(f"{entity_id}: visual metadata {dimension_id} needs a recording_method")
            if item.get("confidence") not in {"HIGH", "MEDIUM", "LOW", "UNASSESSABLE"}:
                errors.append(f"{entity_id}: visual metadata {dimension_id} needs a confidence level")
            if status == "OBSERVED":
                if item.get("value") is None or not _has_substantive_text(str(item.get("value"))):
                    errors.append(f"{entity_id}: observed visual metadata {dimension_id} requires a value")
                if not _has_substantive_text(item.get("source_location")):
                    errors.append(f"{entity_id}: observed visual metadata {dimension_id} requires a source_location")
                if dimension_id == "scale_bar_or_spatial_calibration" and not _has_substantive_text(item.get("unit")):
                    errors.append(f"{entity_id}: observed spatial calibration requires an explicit unit")
            elif not _has_substantive_text(item.get("reason")):
                errors.append(f"{entity_id}: {status} visual metadata {dimension_id} requires a reason")
        if not _has_substantive_text(metadata.get("assessment_note")):
            errors.append(f"{entity_id}: visual_metadata_assessment requires an assessment_note")
        return errors
    if not assessed:
        return [f"{entity_id}: linked CAPTION_BLIND inspection lacks a visual_metadata_assessment"]
    if not recorded_status:
        return [f"{entity_id}: visual_metadata_assessment must have status RECORDED"]
    return errors


def validate_evidence_integrity(bundle: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Reject misleading Region links and unrecorded visual observations."""
    errors: list[str] = []
    warnings: list[str] = []
    regions = bundle.get("regions", {})
    panels = bundle.get("panels", {})

    # Do not rely only on an Agent-authored triage label. Detect repeated
    # header/footer crops from their physical layout and pixel fingerprints.
    layout_occurrences: dict[tuple[Any, ...], list[str]] = {}
    for region_id, region in regions.items():
        bbox = region.get("bbox_normalized") or []
        if len(bbox) != 4:
            continue
        # Prefer an exact decoded-pixel fingerprint. Fall back to the
        # perceptual hash only when the exact pixel digest is unavailable.
        fingerprint_type = "pixels" if region.get("pixel_sha256") else "perceptual"
        fingerprint = region.get("pixel_sha256") or region.get("layout_fingerprint")
        if not fingerprint:
            continue
        zone = "header" if bbox[3] <= 0.24 else ("footer" if bbox[1] >= 0.76 else "body")
        if zone in {"header", "footer"}:
            geometry = tuple(round(float(value), 2) for value in bbox)
            layout_occurrences.setdefault(
                (fingerprint_type, str(fingerprint), zone, geometry), []
            ).append(region_id)
    minimum_repeated_pages = max(
        3, int(math.ceil((bundle.get("source", {}).get("page_count") or 0) * 0.15))
    )
    inferred_repeated_regions = set()
    for region_ids_for_layout in layout_occurrences.values():
        pages = {
            regions[region_id].get("page_number")
            for region_id in region_ids_for_layout
        }
        if len(pages) >= minimum_repeated_pages:
            inferred_repeated_regions.update(region_ids_for_layout)

    for result_id, result in bundle.get("result_units", {}).items():
        region_ids = result.get("region_ids", [])
        linked_regions = [(rid, regions.get(rid)) for rid in region_ids if rid in regions]
        for region_id, region in linked_regions:
            if (
                region.get("triage_role") == "REPEATED_LAYOUT_ASSET"
                or region_id in inferred_repeated_regions
            ):
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
            for entity_id in sorted(inspection_entities):
                errors.extend(_visual_metadata_errors(bundle, entity_id))

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
                if audit.get("reproduction_status") != "NOT_ASSESSABLE":
                    (errors if core else warnings).append(f"{owner}: unsupported audit requires reproduction_status NOT_ASSESSABLE")
                continue

            x_ref, y_ref = audit.get("x_source", {}), audit.get("y_source", {})
            x_result_id, y_result_id = x_ref.get("result_id"), y_ref.get("result_id")
            if x_result_id not in results or y_result_id not in results:
                errors.append(f"{owner}: x_source/y_source references an unknown Result Unit")
                if audit.get("reproduction_status") != "NOT_ASSESSABLE":
                    (errors if core else warnings).append(f"{owner}: unresolved source reference requires reproduction_status NOT_ASSESSABLE")
                continue
            x_values = _numeric_vector(results[x_result_id], x_ref.get("observation_index"))
            y_values = _numeric_vector(results[y_result_id], y_ref.get("observation_index"))
            if x_values is None or y_values is None:
                errors.append(
                    f"{owner}: source references must resolve to numeric_values vectors "
                    "with at least three finite observations"
                )
                if audit.get("reproduction_status") != "NOT_ASSESSABLE":
                    (errors if core else warnings).append(f"{owner}: unavailable numeric vectors require reproduction_status NOT_ASSESSABLE")
                continue
            computed = _ordinary_least_squares(x_values, y_values)
            if computed is None:
                errors.append(f"{owner}: OLS cannot be computed (length mismatch or zero variance)")
                if audit.get("reproduction_status") != "NOT_ASSESSABLE":
                    (errors if core else warnings).append(f"{owner}: uncomputable OLS requires reproduction_status NOT_ASSESSABLE")
                continue
            slope, intercept, r_squared = computed

            reported_source = audit.get("reported_source", {})
            if reported_source.get("result_id", result_id) != result_id:
                errors.append(f"{owner}: reported_source must point to the Result Unit being audited")
                if audit.get("reproduction_status") != "NOT_ASSESSABLE":
                    (errors if core else warnings).append(f"{owner}: unresolved reported parameter source requires reproduction_status NOT_ASSESSABLE")
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
            incomplete_printed_parameters = any(
                reported_values[parameter] is None
                or not isinstance(precision.get(parameter), int)
                or isinstance(precision.get(parameter), bool)
                or precision.get(parameter) < 0
                or precision.get(parameter) > 12
                for parameter in ("slope", "intercept", "r_squared")
            )
            if incomplete_printed_parameters:
                computed_reproduction_status = "NOT_ASSESSABLE"
            elif mismatches:
                computed_reproduction_status = "NOT_REPRODUCED"
            else:
                computed_reproduction_status = "REPRODUCED"

            if audit.get("reproduction_status") != computed_reproduction_status:
                message = (
                    f"{owner}: reproduction_status must be {computed_reproduction_status}; "
                    f"recorded {audit.get('reproduction_status')!r}"
                )
                (errors if core else warnings).append(message)
            if mismatches:
                prefix = (
                    "OLS fit reproduction is NOT_ASSESSABLE; "
                    if computed_reproduction_status == "NOT_ASSESSABLE"
                    else "OLS fit is NOT_REPRODUCED; "
                )
                message = f"{owner}: " + prefix + "; ".join(mismatches)
                (errors if core else warnings).append(message)

            # Reproduction is not a statistical-quality assessment. Record the
            # latter explicitly rather than inferring quality from R-squared.
            quality = audit.get("statistical_quality_assessment")
            if not isinstance(quality, dict):
                message = f"{owner}: statistical_quality_assessment must separately record model diagnostics and uncertainty"
                (errors if core else warnings).append(message)
            else:
                quality_status = quality.get("status")
                diagnostics = quality.get("diagnostics", [])
                uncertainty_status = quality.get("uncertainty_status")
                if quality_status not in {"ASSESSED", "PARTIALLY_ASSESSED", "NOT_ASSESSED", "NOT_APPLICABLE"}:
                    message = f"{owner}: statistical_quality_assessment.status is missing or invalid"
                    (errors if core else warnings).append(message)
                elif core and quality_status != "ASSESSED":
                    errors.append(f"{owner}: CORE fit requires a completed statistical-quality assessment; found {quality_status}")
                elif quality_status == "PARTIALLY_ASSESSED":
                    warnings.append(f"{owner}: statistical-quality assessment is partial")
                if quality_status == "ASSESSED" and not diagnostics:
                    message = f"{owner}: an ASSESSED fit requires at least one recorded diagnostic"
                    (errors if core else warnings).append(message)
                elif quality_status == "ASSESSED":
                    meaningful_diagnostics = [
                        item for item in diagnostics if isinstance(item, dict)
                        and all(_has_substantive_text(item.get(field)) for field in ("diagnostic", "method", "result"))
                    ]
                    if not meaningful_diagnostics:
                        message = f"{owner}: an ASSESSED fit requires a diagnostic with a defined check, method and result"
                        (errors if core else warnings).append(message)
                if not _has_substantive_text(quality.get("assessment_note")):
                    message = f"{owner}: statistical-quality assessment requires a substantive assessment_note"
                    (errors if core else warnings).append(message)
                if uncertainty_status not in {
                    "QUANTIFIED", "QUALITATIVELY_ADDRESSED", "NOT_REPORTED",
                    "NOT_ASSESSED", "NOT_APPLICABLE"
                }:
                    message = f"{owner}: uncertainty_status must be explicitly recorded"
                    (errors if core else warnings).append(message)
                if uncertainty_status in {"NOT_REPORTED", "NOT_ASSESSED"} and not _has_substantive_text(quality.get("uncertainty_note")):
                    message = f"{owner}: unavailable/unreported uncertainty requires an explanatory uncertainty_note"
                    (errors if core else warnings).append(message)
                if uncertainty_status == "QUANTIFIED" and not _has_substantive_text(quality.get("uncertainty_note")):
                    message = f"{owner}: quantified uncertainty requires the method or interval to be recorded in uncertainty_note"
                    (errors if core else warnings).append(message)
                if uncertainty_status == "QUALITATIVELY_ADDRESSED" and not _has_substantive_text(quality.get("uncertainty_note")):
                    message = f"{owner}: qualitatively addressed uncertainty requires the approach and its limitations in uncertainty_note"
                    (errors if core else warnings).append(message)
                if uncertainty_status == "NOT_APPLICABLE" and not _has_substantive_text(quality.get("uncertainty_note")):
                    message = f"{owner}: NOT_APPLICABLE uncertainty requires a rationale in uncertainty_note"
                    (errors if core else warnings).append(message)

            # Validation scope is distinct from in-sample coefficient
            # reproduction. An external-validation label needs an explicit
            # independent data scope and leakage controls.
            validation = audit.get("validation_assessment")
            if not isinstance(validation, dict):
                message = f"{owner}: validation_assessment must distinguish in-sample, internal and external validation"
                (errors if core else warnings).append(message)
            else:
                level = validation.get("level")
                valid_levels = {
                    "IN_SAMPLE_ONLY", "INTERNAL_RESAMPLING",
                    "EXTERNAL_INDEPENDENT_DATA", "PROSPECTIVE",
                    "NOT_ASSESSED", "NOT_APPLICABLE"
                }
                if level not in valid_levels:
                    message = f"{owner}: validation_assessment.level is missing or invalid"
                    (errors if core else warnings).append(message)
                elif core and level == "NOT_ASSESSED":
                    errors.append(f"{owner}: CORE fit must explicitly state a validation level; NOT_ASSESSED is not decision-ready")
                elif level == "IN_SAMPLE_ONLY":
                    warnings.append(f"{owner}: fit reproduction is in-sample only; do not describe it as externally validated")
                elif level in {"EXTERNAL_INDEPENDENT_DATA", "PROSPECTIVE"}:
                    training_scope = str(validation.get("training_data_scope") or "").strip()
                    validation_scope = str(validation.get("validation_data_scope") or "").strip()
                    required = {
                        "training_dataset_ids": validation.get("training_dataset_ids"),
                        "independence_unit": validation.get("independence_unit"),
                        "leakage_controls": validation.get("leakage_controls"),
                    }
                    if level == "EXTERNAL_INDEPENDENT_DATA":
                        required["validation_dataset_ids"] = validation.get("validation_dataset_ids")
                    else:
                        required["planned_validation_source"] = validation.get("planned_validation_source")
                    missing = [
                        name for name, value in required.items()
                        if not (_has_substantive_items(value) if isinstance(value, list) else _has_substantive_text(value))
                    ]
                    if not _has_substantive_text(training_scope) or not _has_substantive_text(validation_scope) or training_scope == validation_scope:
                        missing.append("distinct training_data_scope and validation_data_scope")
                    overlap = set(validation.get("training_dataset_ids") or []) & set(validation.get("validation_dataset_ids") or [])
                    if level == "EXTERNAL_INDEPENDENT_DATA" and overlap:
                        missing.append("disjoint training/validation dataset IDs (overlap: " + ", ".join(sorted(overlap)) + ")")
                    if missing:
                        message = f"{owner}: {level} requires " + ", ".join(missing)
                        (errors if core else warnings).append(message)
                elif level == "INTERNAL_RESAMPLING":
                    missing = [
                        name for name, value in {
                            "resampling_method": validation.get("resampling_method"),
                            "split_unit": validation.get("split_unit"),
                            "leakage_controls": validation.get("leakage_controls"),
                        }.items() if not value
                    ]
                    if missing:
                        message = f"{owner}: INTERNAL_RESAMPLING requires " + ", ".join(missing)
                        (errors if core else warnings).append(message)
                if not isinstance(validation.get("limitations"), list) or not _has_substantive_items(validation.get("limitations")):
                    message = f"{owner}: validation_assessment must record substantive limitations as a non-empty list"
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

        # A Claim may also carry non-visual comparability checks (e.g.
        # chemical conditions). Only assessments containing visual-acquisition
        # dimensions are candidates for the image-comparability gate.
        visual_assessments = []
        for assessment_id in linked_ids:
            assessment = assessments.get(assessment_id)
            if not isinstance(assessment, dict):
                continue
            dimensions = {
                _visual_dimension_id(dimension.get("dimension"))
                for dimension in assessment.get("dimensions", [])
            }
            if dimensions.intersection(VISUAL_DIMENSIONS):
                visual_assessments.append((assessment_id, assessment))

        if not visual_assessments:
            errors.append(
                f"{claim_id}: claim uses multiple image-derived Result Units "
                f"{', '.join(image_result_ids)} without a linked visual comparability assessment"
            )
            continue

        for assessment_id, assessment in visual_assessments:
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

            entity_ids = {
                entity.get("entity_id")
                for entity in assessment.get("comparison_entities", [])
                if entity.get("entity_id")
            }
            for dimension_id in VISUAL_DIMENSIONS:
                dimension = visual_dimensions[dimension_id]
                values_by_entity = dimension.get("values_by_entity", {})
                if not isinstance(values_by_entity, dict) or not entity_ids.issubset(set(values_by_entity)):
                    errors.append(
                        f"{assessment_id}: visual dimension {dimension_id} must record a value/status "
                        "for every compared entity"
                    )
                if not isinstance(dimension.get("assessment_note"), str) or not dimension["assessment_note"].strip():
                    errors.append(
                        f"{assessment_id}: visual dimension {dimension_id} requires an assessment_note"
                    )

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
    recommendation_rationale = routes_bundle.get("recommendation_rationale")
    if not isinstance(recommendation_rationale, str) or len(recommendation_rationale.strip()) < 30:
        errors.append("recommended_route_id requires recommendation_rationale explaining the preferred direction")
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


def _has_substantive_text(value: Any) -> bool:
    """Reject empty and unresolved placeholders from decision-ready fields."""
    if not isinstance(value, str):
        return False
    normalized = re.sub(r"\s+", " ", value.strip().casefold())
    if not normalized:
        return False
    unresolved_prefix = re.match(
        r"^(?:tbd|todo|unknown|not assessed|not specified|to be determined|to be confirmed|to be justified|pending|n/?a|not applicable)(?:\b|$)",
        normalized,
    )
    return unresolved_prefix is None


def _has_substantive_items(values: Any) -> bool:
    return isinstance(values, list) and bool(values) and all(
        _has_substantive_text(value) for value in values
    )


def _validation_issue(
    task_id: str,
    readiness: str,
    message: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    """Keep incomplete designs visible while reserving hard errors for execution-ready tasks."""
    target = errors if readiness in {"READY_FOR_SUPERVISOR_APPROVAL", "APPROVED_FOR_EXECUTION"} else warnings
    target.append(f"{task_id}: {message}")


def validate_proxy_measurement_design(
    framework: dict[str, Any],
    evidence: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate a declared proxy-to-reference measurement study without prescribing domain protocols.

    The gate checks that the relationship, sampling alignment, controls, accounting
    closure decision, validation level and outcome rules are explicit. It does not
    decide which controls or acceptance margins are scientifically appropriate.
    """
    errors: list[str] = []
    warnings: list[str] = []
    valid_result_ids = set((evidence or {}).get("result_units", {}))
    for task_id, task in framework.get("tasks", {}).items():
        execution = task.get("execution_design") or {}
        decision = execution.get("decision_framework") or {}
        measurement = execution.get("measurement_validation")
        question_type = decision.get("question_type")
        readiness = execution.get("readiness", "NOT_ASSESSED")
        is_proxy_question = question_type == "PROXY_VALIDATION"
        is_proxy_design = isinstance(measurement, dict) and measurement.get("validation_type") == "PROXY_TO_REFERENCE"
        if not is_proxy_question and not is_proxy_design:
            continue

        if not isinstance(measurement, dict):
            _validation_issue(
                task_id, readiness,
                "PROXY_VALIDATION requires a structured execution_design.measurement_validation record",
                errors, warnings,
            )
            continue

        if question_type == "PROXY_VALIDATION" and measurement.get("validation_type") != "PROXY_TO_REFERENCE":
            _validation_issue(task_id, readiness, "question_type PROXY_VALIDATION requires validation_type PROXY_TO_REFERENCE", errors, warnings)

        candidate = measurement.get("candidate_measurement")
        reference = measurement.get("reference_measurement")
        for label, record in (("candidate_measurement", candidate), ("reference_measurement", reference)):
            if not isinstance(record, dict):
                _validation_issue(task_id, readiness, f"measurement_validation.{label} must define a separate measurement", errors, warnings)
                continue
            missing = [
                field for field in ("name", "measurand", "operational_definition", "method")
                if not _has_substantive_text(record.get(field))
            ]
            if missing:
                _validation_issue(task_id, readiness, f"{label} is missing " + ", ".join(missing), errors, warnings)

        if isinstance(reference, dict):
            if reference.get("reference_basis") not in {
                "DIRECT_MEASUREMENT", "REFERENCE_STANDARD", "ORTHOGONAL_METHOD",
                "COMPOSITE_REFERENCE", "OTHER"
            }:
                _validation_issue(task_id, readiness, "reference_measurement.reference_basis must state the basis of the reference", errors, warnings)
            if not _has_substantive_text(reference.get("independence_rationale")):
                _validation_issue(task_id, readiness, "reference_measurement requires an independence_rationale and must disclose shared-method limitations", errors, warnings)

        # Optional prior/pilot Result Unit links must resolve. Future planned
        # measurements need not have Result Unit IDs before they are acquired.
        for label, record in (("candidate_measurement", candidate), ("reference_measurement", reference)):
            if not isinstance(record, dict):
                continue
            for result_id in record.get("result_ids", []):
                if evidence is not None and result_id not in valid_result_ids:
                    _validation_issue(task_id, readiness, f"{label}.result_ids references unknown Result Unit {result_id}", errors, warnings)
            for source_ref in record.get("source_refs", []):
                if not isinstance(source_ref, dict):
                    _validation_issue(task_id, readiness, f"{label}.source_refs entries must be structured references", errors, warnings)
                elif source_ref.get("kind") == "result_unit" and evidence is not None and source_ref.get("id") not in valid_result_ids:
                    _validation_issue(task_id, readiness, f"{label}.source_refs references unknown Result Unit {source_ref.get('id')}", errors, warnings)

        sampling = measurement.get("sampling_design") or {}
        pairing = sampling.get("pairing_strategy")
        valid_pairing = {"WITHIN_UNIT_PAIRED", "MATCHED_UNITS", "GROUP_LEVEL", "UNPAIRED", "UNKNOWN"}
        if not _has_substantive_text(sampling.get("unit_of_analysis")):
            _validation_issue(task_id, readiness, "sampling_design.unit_of_analysis must be explicit", errors, warnings)
        if pairing not in valid_pairing:
            _validation_issue(task_id, readiness, "sampling_design.pairing_strategy must be explicit", errors, warnings)
        if pairing == "MATCHED_UNITS" and not _has_substantive_items(sampling.get("matching_factors")):
            _validation_issue(task_id, readiness, "MATCHED_UNITS requires explicit matching_factors", errors, warnings)
        if pairing == "UNPAIRED" and not _has_substantive_text(sampling.get("unpaired_design_rationale")):
            _validation_issue(task_id, readiness, "UNPAIRED design requires an unpaired_design_rationale", errors, warnings)
        if pairing == "UNKNOWN":
            _validation_issue(task_id, readiness, "pairing strategy is UNKNOWN; state the limitation and keep the design from execution approval", errors, warnings)
        alignment = sampling.get("condition_alignment")
        if alignment not in {"MATCHED", "CONDITIONALLY_MATCHED", "MISMATCHED", "UNKNOWN"}:
            _validation_issue(task_id, readiness, "sampling_design.condition_alignment must explicitly classify condition alignment", errors, warnings)
        if alignment in {"MISMATCHED", "UNKNOWN"} and not _has_substantive_items(sampling.get("limitations")):
            _validation_issue(task_id, readiness, "mismatched/unknown condition alignment requires explicit limitations", errors, warnings)
        if alignment == "CONDITIONALLY_MATCHED" and not _has_substantive_items(sampling.get("limitations")):
            _validation_issue(task_id, readiness, "CONDITIONALLY_MATCHED conditions require explicit residual mismatch/limitation notes", errors, warnings)
        relationship = decision.get("relationship_type")
        valid_relationships = {
            "AGREEMENT", "CALIBRATION", "PREDICTION", "CLASSIFICATION",
            "RANKING", "MONITORING", "ASSOCIATION", "OTHER"
        }
        if relationship not in valid_relationships:
            _validation_issue(task_id, readiness, "decision_framework.relationship_type must state what relationship is being validated", errors, warnings)
        if relationship == "OTHER" and not _has_substantive_text(decision.get("relationship_other_description")):
            _validation_issue(task_id, readiness, "relationship_type OTHER requires relationship_other_description", errors, warnings)
        if relationship in {"AGREEMENT", "CALIBRATION"} and pairing in {"UNPAIRED", "GROUP_LEVEL", "UNKNOWN"}:
            _validation_issue(task_id, readiness, f"{relationship} between candidate and reference measurements requires a paired or matched sampling design", errors, warnings)
        if relationship in {"AGREEMENT", "CALIBRATION"} and alignment in {"MISMATCHED", "UNKNOWN"}:
            _validation_issue(task_id, readiness, f"{relationship} cannot be execution-ready with MISMATCHED/UNKNOWN condition alignment", errors, warnings)

        missing_decision = [
            field for field in ("primary_estimand", "analysis_method", "acceptance_boundary", "acceptance_boundary_basis")
            if not _has_substantive_text(decision.get(field))
        ]
        outcome_rules = decision.get("outcome_rules", [])
        outcomes = {
            item.get("outcome") for item in outcome_rules if isinstance(item, dict)
            and _has_substantive_text(item.get("criterion"))
            and _has_substantive_text(item.get("claim_implication"))
        }
        for outcome in ("SUPPORTS", "CONTRADICTS", "INCONCLUSIVE"):
            if outcome not in outcomes:
                missing_decision.append(f"outcome_rule:{outcome}")
        if missing_decision:
            _validation_issue(task_id, readiness, "proxy-validation decision_framework lacks " + ", ".join(missing_decision), errors, warnings)

        control = measurement.get("control_coverage") or {}
        control_status = control.get("review_status")
        planned_controls = control.get("planned_controls", [])
        planned_classes = {
            item.get("control_class") for item in planned_controls if isinstance(item, dict)
        }
        required_classes = set(control.get("required_control_classes", []))
        uncovered = sorted(required_classes - planned_classes)
        if control_status not in {"ASSESSED", "PARTIALLY_ASSESSED", "NOT_ASSESSED", "NOT_APPLICABLE"}:
            _validation_issue(task_id, readiness, "control_coverage.review_status must be explicit", errors, warnings)
        if uncovered:
            _validation_issue(task_id, readiness, "required control classes have no planned control: " + ", ".join(uncovered), errors, warnings)
        for control_index, planned in enumerate(planned_controls, start=1):
            if not isinstance(planned, dict) or not _has_substantive_text(planned.get("purpose")) or not _has_substantive_text(planned.get("rationale")):
                _validation_issue(task_id, readiness, f"planned control {control_index} requires a substantive purpose and rationale", errors, warnings)
        if control_status == "NOT_APPLICABLE" and not _has_substantive_text(control.get("no_control_rationale")):
            _validation_issue(task_id, readiness, "NOT_APPLICABLE controls require no_control_rationale", errors, warnings)
        if not planned_controls and not required_classes and not _has_substantive_text(control.get("no_control_rationale")):
            _validation_issue(task_id, readiness, "an empty control plan requires a rationale explaining why no control is needed", errors, warnings)
        if control_status == "NOT_ASSESSED":
            _validation_issue(task_id, readiness, "control coverage remains NOT_ASSESSED", errors, warnings)
        if control_status == "PARTIALLY_ASSESSED":
            warnings.append(f"{task_id}: control coverage is only partially assessed")

        accounting = measurement.get("accounting_closure") or {}
        accounting_status = accounting.get("applicability")
        if accounting_status not in {"REQUIRED", "NOT_REQUIRED", "NOT_ASSESSED"}:
            _validation_issue(task_id, readiness, "accounting_closure.applicability must explicitly state whether closure/recovery accounting is required", errors, warnings)
        elif accounting_status == "REQUIRED":
            missing = [
                field for field in ("accounted_inputs", "accounted_outputs")
                if not _has_substantive_items(accounting.get(field))
            ]
            missing.extend(
                field for field in ("residual_method", "acceptance_basis")
                if not _has_substantive_text(accounting.get(field))
            )
            if missing:
                _validation_issue(task_id, readiness, "required accounting closure is missing " + ", ".join(missing), errors, warnings)
        elif accounting_status == "NOT_REQUIRED" and not _has_substantive_text(accounting.get("rationale")):
            _validation_issue(task_id, readiness, "NOT_REQUIRED accounting closure requires a rationale", errors, warnings)
        elif accounting_status == "NOT_ASSESSED":
            _validation_issue(task_id, readiness, "accounting/recovery closure remains NOT_ASSESSED", errors, warnings)

        validation = measurement.get("validation_strategy") or {}
        validation_level = validation.get("level")
        valid_validation_levels = {
            "IN_SAMPLE_ONLY", "INTERNAL_RESAMPLING",
            "EXTERNAL_INDEPENDENT_DATA", "PROSPECTIVE", "NOT_ASSESSED"
        }
        if validation_level not in valid_validation_levels:
            _validation_issue(task_id, readiness, "validation_strategy.level must distinguish in-sample, internal and independent validation", errors, warnings)
        elif validation_level in {"EXTERNAL_INDEPENDENT_DATA", "PROSPECTIVE"}:
            training_scope = str(validation.get("training_data_scope") or "").strip()
            validation_scope = str(validation.get("validation_data_scope") or "").strip()
            required = {
                "training_dataset_ids": validation.get("training_dataset_ids"),
                "independence_unit": validation.get("independence_unit"),
                "leakage_controls": validation.get("leakage_controls"),
            }
            if validation_level == "EXTERNAL_INDEPENDENT_DATA":
                required["validation_dataset_ids"] = validation.get("validation_dataset_ids")
            else:
                required["planned_validation_source"] = validation.get("planned_validation_source")
            missing = [
                field for field, value in required.items()
                if not (_has_substantive_items(value) if isinstance(value, list) else _has_substantive_text(value))
            ]
            if not _has_substantive_text(training_scope) or not _has_substantive_text(validation_scope) or training_scope == validation_scope:
                missing.append("distinct training_data_scope and validation_data_scope")
            overlap = set(validation.get("training_dataset_ids") or []) & set(validation.get("validation_dataset_ids") or [])
            if validation_level == "EXTERNAL_INDEPENDENT_DATA" and overlap:
                missing.append("disjoint training/validation dataset IDs (overlap: " + ", ".join(sorted(overlap)) + ")")
            if missing:
                _validation_issue(task_id, readiness, f"{validation_level} requires " + ", ".join(missing), errors, warnings)
        elif validation_level == "INTERNAL_RESAMPLING":
            missing = [
                field for field in ("resampling_method", "split_unit", "leakage_controls")
                if not validation.get(field)
            ]
            if missing:
                _validation_issue(task_id, readiness, "INTERNAL_RESAMPLING requires " + ", ".join(missing), errors, warnings)
        elif validation_level in {"IN_SAMPLE_ONLY", "NOT_ASSESSED"}:
            if not _has_substantive_text(validation.get("limitations")):
                _validation_issue(task_id, readiness, f"{validation_level} validation status requires an explicit limitation", errors, warnings)
            if validation_level == "IN_SAMPLE_ONLY":
                warnings.append(f"{task_id}: IN_SAMPLE_ONLY proxy validation is in-sample only; do not describe it as independently validated")

        if readiness in {"READY_FOR_SUPERVISOR_APPROVAL", "APPROVED_FOR_EXECUTION"}:
            if control_status not in {"ASSESSED", "NOT_APPLICABLE"}:
                errors.append(f"{task_id}: execution-ready proxy validation requires assessed control coverage")
            if accounting_status == "NOT_ASSESSED":
                errors.append(f"{task_id}: execution-ready proxy validation cannot leave accounting-closure applicability unassessed")
            if validation_level == "NOT_ASSESSED":
                errors.append(f"{task_id}: execution-ready proxy validation cannot leave validation strategy unassessed")

    return errors, warnings
