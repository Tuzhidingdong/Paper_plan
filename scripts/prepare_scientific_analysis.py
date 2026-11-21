#!/usr/bin/env python3
"""Prepare domain-neutral, source-linked scientific analysis packs from all Result Units."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle, sha256_file

DEFAULT_MAX_RESULTS_PER_PACK = 10
MAX_CANDIDATE_LINKS = 3000

ANALYSIS_INSTRUCTIONS = [
    "Analyze this evidence set as a connected scientific dataset, not as unrelated figure captions.",
    "Inspect each supplied original-resolution image or panel. Where one result contains multiple plotted series, samples, groups, stages or conditions, inspect and compare those within-result elements as well as links across Result Units.",
    "Discover which relationships are scientifically meaningful from the supplied evidence. Consider cross-sample differences, within-sample changes, condition or dose responses, time/order trends, relationships among measured quantities, cross-method convergence, contradictions, outliers and results that do not follow the dominant pattern. Do not force every possible comparison.",
    "Use the supplied relationship candidates only as navigation hints. They are not proof that two results are comparable. Also identify useful relationships that are not listed when supported by shared source labels, sample mappings, conditions, series or scientific context.",
    "The request omits captions and report narrative, but the active Agent may already have seen source text in prior context. Do not claim a fully caption-blind or cognitively independent review. Separate what is directly observed in the original image from what is learned from text or prior context.",
    "Before combining or contrasting evidence, explicitly assess sample identity, measurement definition, units, acquisition/method conditions, data processing, normalization, calibration, replicate basis and relevant environmental or operational conditions. Mark dimensions MATCHED, MISMATCHED, UNKNOWN or NOT_APPLICABLE with reasons.",
    "Keep direct observations, extracted/transcribed values, derived calculations, interpretations and hypotheses separate. Every material observation or comparison must cite the relevant Result Unit and source Region/Panel/page.",
    "Quantitative differences must preserve units, definitions, normalization basis, source precision and uncertainty. If values are estimated visually from an image, label them as estimates and state the image/axis limitations; do not imply precision beyond the source.",
    "Do not invent raw data, missing values, sample identities, conditions, controls, replicates, units, significance, correlations or causal relationships. Do not infer correlation or causation from co-occurrence alone.",
    "Look for independent evidence that supports or contradicts a proposed interpretation. State whether evidence converges, conflicts, is merely compatible, or is insufficient; do not treat several panels derived from the same measurement as independent confirmation.",
    "For each plausible interpretation, give competing explanations, confounders, scope limits and what additional evidence would discriminate them. Do not turn an attractive pattern into a mechanism without an adequate evidence chain.",
    "Identify candidate scientific implications or questions that were not explicitly supplied by the user, but label them as candidates and state exactly which existing evidence motivates them.",
    "Account for every Result Unit in the request. Use ANALYZED when its evidence has been examined, NO_COMPARISON_APPLICABLE when there is no defensible relationship to compare (with a reason), and NOT_ASSESSABLE when a source/identity/quality blocker prevents analysis.",
    "If a relationship cannot be assessed, say so and preserve the blocker. A clear NOT_ASSESSABLE conclusion is preferable to a manufactured scientific finding.",
    "Treat plotted signals as primary experimental evidence, not as illustrations. For every relevant plot, identify the axes, units, trace/series identities and visible signal features before interpreting the result.",
    "When the source supports it, record individual peak-like features (for example, peaks, reflections or absorption bands) with their position, width, signal magnitude and apparent area. Use the axis and unit of that plot; do not force a feature type or assign a chemical/structural identity without evidence.",
    "Compare features across the curves, samples, conditions and stages that are actually shown. Record shifts, broadening/narrowing, relative-intensity changes, area changes, new or disappearing features, shoulders, splitting, overlap and non-monotonic responses when resolvable.",
    "For every numeric signal estimate, state whether it comes from exact source data, printed values or a calibrated plot reading; preserve axis calibration, resolution, normalization basis, precision and uncertainty. Use null/not-resolvable rather than invented numeric values.",
    "For every numeric signal feature and quantified signal comparison, use a controlled reading_basis/source_basis: EXACT_SOURCE_DATA, EXACT_TEXT, EXACT_TABLE, PRINTED_FIGURE_VALUE, DERIVED_FROM_EXPLICIT_VALUES, CALIBRATED_PLOT_READING or UNRESOLVED. Do not use free-form wording to disguise an uncalibrated visual estimate.",
    "A list of generic feature assignments is not a completed signal analysis. Explain what changed between the actual plotted series, which changes are robust, and what instrument, processing, overlap, orientation, baseline or sample-state alternatives could produce them.",
    "Before marking any image-derived Result Unit ANALYZED, record whether its original-resolution image was actually attached to the model call as native image input. A file path or text description alone is not an image attachment. If native image delivery cannot be confirmed, mark the affected units NOT_ASSESSABLE and disclose the blocker.",
    "For every Result Unit, explicitly assess whether the source contains plotted/scan/curve signal features that require feature-level analysis. Record exactly one signal_analysis_coverage disposition: APPLICABLE with linked feature IDs, NOT_APPLICABLE with a reason, or NOT_ASSESSABLE with a reason. Do not silently omit this decision; do not force feature extraction onto non-signal evidence.",
    "Persist the actual model request and response artifacts and provide an invocation receipt listing every requested image path, its SHA-256 and the matching native image attachment reference. The receipt is agent-reported evidence and must not be described as an independent host-level verification.",
    "Assign a unique stable ID to every material relationship (relationship_id), interpretation (interpretation_id) and contradiction (contradiction_id) in this analysis record. Preserve observation_id, comparison_id, feature_id and signal-comparison comparison_id values. These IDs will be cited by downstream Findings; do not reuse an ID for two records of the same type within one analysis.",
    "For every quantitative plot read, create a plot_calibration with the actual image/PDF coordinate frame, plot-area bounds, visible tick anchors, axis scale and units, plus the visible series-to-identity mapping. Never calibrate an axis from only its title or from an assumed standard range.",
    "Use at least two visible numeric tick anchors per numeric axis. Prefer three or more distributed anchors so the recorder can check linear/log calibration residuals. Record the coordinate uncertainty of each tick anchor and the printed tick value as visible; do not invent hidden ticks.",
    "Create plot_readings for each numeric point/feature used by a quantitative conclusion. For raster images, report the pixel coordinate and coordinate uncertainty. For PDF-native vector geometry, cite the sidecar path_id/item_index/point_index (or curve_t for a cubic trace); the recorder will retrieve the coordinates from the source-anchored sidecar. Do not use cubic control points as observed data vertices.",
    "The recorder independently maps those coordinates through the tick calibration and stores mapped values and graph-reading uncertainty. Graph-reading uncertainty is not experimental standard deviation, replicate variability or instrument uncertainty.",
    "A plotted numeric estimate may support a bounded quantitative statement only when the axis used for that value is calibrated adequately; an x/y data point requires both axes. Quantitative readings require CONFIRMED series-to-trace mapping. PROBABLE, AMBIGUOUS or UNRESOLVED series mapping permits trend-only/qualitative language, not a numeric comparison. Two-tick calibrations have limited status; low-quality calibration permits trend-only language. Unreadable axes or overlapping traces must remain unresolved.",
    "Every numeric signal feature read visually from a plot must cite plot_reading_ids. A numeric signal comparison based on a plot must cite the relevant plot_reading_ids and declare a reproducible calculation operation/axis; the recorder recomputes the difference, ratio or percent change and rejects inconsistent values.",
    "Do not estimate integrated peak/band area from a displayed curve unless a reproducible integration region, baseline method and calibration are explicitly provided. Prefer null/unresolved rather than a visually invented area.",
    "If native vector geometry is available for a figure, inspect the retained vector path/text sidecar together with the raster image. Use vector path coordinates as a higher-resolution geometric source, but do not mistake path coordinates for original instrument data or infer series identity from line colour alone.",
    "Treat coordinate calibration and semantic identity mapping as separate evidence tasks. For each plotted series, state mapping_status, mapping_basis and mapping_evidence_refs. A CONFIRMED series mapping requires a visible legend/trace linkage supported by source evidence; colour similarity alone is insufficient.",
    "When a plotted series is traced through PDF-native vector geometry, record source_path_refs as exact path_id/item_index pairs. Every VECTOR_GEOMETRY reading assigned to that series must refer to one of those exact path/item pairs. If trace-to-path linkage is uncertain, downgrade mapping_status and keep the reading trend-only.",
    "For every series, explicitly record panel_id/panel_mapping_status and sample_id/sample_mapping_status. Use unresolved/unmapped states when identity is not evidenced; use NOT_APPLICABLE only when the source genuinely has no distinct panel or sample association. Never infer missing identities from similar labels across figures.",
    "When tabular or textual evidence reports multiple quantities, analytes, parameters, samples or conditions, create separately source-linked numeric observations at the appropriate measurand-by-sample-by-condition granularity. Every numeric observation requires one measurand, unit, data_origin and the exact source evidence; do not combine different quantities into an unstructured description or one ambiguous numeric field.",
    "When a general Result-Unit comparison is materially supported by signal-level comparison, link the records reciprocally using comparisons[].signal_comparison_ids and signal_comparisons[].analysis_comparison_ids. Keep feature IDs and Result Unit sets consistent; do not imply a signal-level comparison that is absent from the linked feature records."]


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().casefold())


def _sample_map(result: dict[str, Any]) -> dict[str, str]:
    context = result.get("measurement_context", {})
    output: dict[str, str] = {}
    for item in context.get("sample_associations", []) or []:
        sample_id = item.get("sample_id")
        if sample_id:
            output[str(sample_id)] = str(item.get("mapping_status") or "UNKNOWN")
    for observation in result.get("observations", []) or []:
        sample_id = observation.get("sample_id")
        if sample_id and str(sample_id) not in output:
            output[str(sample_id)] = str(observation.get("mapping_status") or "UNKNOWN")
    return output

def _sample_association_records(bundle: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    context = result.get("measurement_context", {})
    associations = list(context.get("sample_associations", []) or [])
    context_sample_ids = {
        str(item.get("sample_id")) for item in associations if item.get("sample_id")
    }
    for observation in result.get("observations", []) or []:
        sample_id = observation.get("sample_id")
        if sample_id:
            # Do not create a second non-series mapping when the measurement context
            # already maps the same sample; preserve genuinely distinct series IDs.
            if str(sample_id) in context_sample_ids and not observation.get("series_id"):
                continue
            associations.append({
                "sample_id": sample_id,
                "mapping_status": observation.get("mapping_status", "UNKNOWN"),
                "series_id": observation.get("series_id"),
            })
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in associations:
        sample_id = str(item.get("sample_id") or "")
        if not sample_id:
            continue
        key = (
            sample_id,
            str(item.get("series_id") or ""),
            str(item.get("mapping_status") or "UNKNOWN"),
        )
        unique[key] = item
    output = []
    for (sample_id, series_id, mapping_status), item in sorted(unique.items()):
        sample = bundle.get("samples", {}).get(sample_id, {})
        output.append({
            "sample_id": sample_id,
            "sample_aliases": [
                alias.get("alias") for alias in sample.get("aliases", []) if alias.get("alias")
            ],
            "identity_status": sample.get("identity_status", "UNKNOWN"),
            "prep_conditions": sample.get("prep_conditions", {}),
            "batch_note": sample.get("batch_note"),
            "mapping_status": mapping_status,
            "series_id": series_id or None,
        })
    return output



def _condition_map(result: dict[str, Any]) -> dict[str, Any]:
    conditions = result.get("measurement_context", {}).get("measurement_conditions", {})
    return conditions if isinstance(conditions, dict) else {}


def _measurement_signatures(result: dict[str, Any]) -> set[str]:
    context = result.get("measurement_context", {})
    signatures = set()
    for value in (result.get("data_type"), context.get("technique")):
        normalized = _norm(value)
        if normalized:
            signatures.add(normalized)
    return signatures


def _add_index_links(index: dict[str, list[str]], key: str, result_id: str) -> None:
    if key:
        index[key].append(result_id)


def discover_relationship_candidates(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Create candidate links from metadata without declaring scientific comparability."""
    results = bundle.get("result_units", {})
    indexes: dict[str, dict[str, list[str]]] = {
        "sample": defaultdict(list),
        "measurement_group": defaultdict(list),
        "measurement_signature": defaultdict(list),
        "region": defaultdict(list),
        "condition_field": defaultdict(list),
        "series": defaultdict(list),
    }
    result_maps: dict[str, dict[str, Any]] = {}
    for result_id, result in sorted(results.items()):
        result_maps[result_id] = result
        for sample_id in _sample_map(result):
            _add_index_links(indexes["sample"], sample_id, result_id)
        context = result.get("measurement_context", {})
        _add_index_links(indexes["measurement_group"], _norm(context.get("measurement_group")), result_id)
        for signature in _measurement_signatures(result):
            _add_index_links(indexes["measurement_signature"], signature, result_id)
        for entity_id in result.get("region_ids", []) or []:
            _add_index_links(indexes["region"], str(entity_id), result_id)
        for key in _condition_map(result):
            _add_index_links(indexes["condition_field"], _norm(key), result_id)
        for association in context.get("sample_associations", []) or []:
            series_id = association.get("series_id")
            if series_id:
                _add_index_links(indexes["series"], _norm(series_id), result_id)
        for observation in result.get("observations", []) or []:
            series_id = observation.get("series_id")
            if series_id:
                _add_index_links(indexes["series"], _norm(series_id), result_id)

    pair_reasons: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_notes: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    def link_group(member_ids: list[str], reason: str) -> None:
        unique = sorted(set(member_ids))
        if len(unique) < 2:
            return
        # A bounded star connects the component without asserting all-pairs comparability.
        anchor_id = unique[0]
        for related_id in unique[1:]:
            pair_reasons[(anchor_id, related_id)].add(reason)

    for ids in indexes["sample"].values():
        link_group(ids, "SHARED_SAMPLE_ASSOCIATION")
    for ids in indexes["measurement_group"].values():
        link_group(ids, "SHARED_MEASUREMENT_GROUP")
    for ids in indexes["measurement_signature"].values():
        link_group(ids, "SHARED_MEASUREMENT_SIGNATURE")
    for ids in indexes["region"].values():
        link_group(ids, "SHARED_SOURCE_REGION")
    for ids in indexes["condition_field"].values():
        link_group(ids, "SHARED_CONDITION_FIELD")
    for ids in indexes["series"].values():
        link_group(ids, "SHARED_SERIES_IDENTIFIER")

    for pair in list(pair_reasons):
        left, right = pair
        left_conditions = _condition_map(result_maps[left])
        right_conditions = _condition_map(result_maps[right])
        common_fields = sorted(
            set(_norm(key) for key in left_conditions)
            & set(_norm(key) for key in right_conditions)
        )
        if common_fields:
            lmap = {_norm(key): value for key, value in left_conditions.items()}
            rmap = {_norm(key): value for key, value in right_conditions.items()}
            pair_notes[pair].append({
                "type": "SHARED_CONDITION_FIELDS",
                "fields": [
                    {"field": field, "left_value": lmap[field], "right_value": rmap[field],
                     "values_equal_as_text": _norm(lmap[field]) == _norm(rmap[field])}
                    for field in common_fields
                ],
                "note": "Matching field names do not establish compatible units or measurement conditions.",
            })
        shared_samples = sorted(set(_sample_map(result_maps[left])) & set(_sample_map(result_maps[right])))
        if shared_samples:
            pair_notes[pair].append({
                "type": "SHARED_SAMPLE_IDS",
                "sample_ids": shared_samples,
                "mapping_statuses": {
                    sample_id: {
                        "left": _sample_map(result_maps[left])[sample_id],
                        "right": _sample_map(result_maps[right])[sample_id],
                    } for sample_id in shared_samples
                },
            })

    candidates = [
        {
            "result_ids": [left, right],
            "candidate_reasons": sorted(reasons),
            "metadata_notes": pair_notes.get((left, right), []),
            "relationship_is_confirmed": False,
        }
        for (left, right), reasons in sorted(pair_reasons.items())
    ]
    return candidates[:MAX_CANDIDATE_LINKS]


def _asset_exists(image_path: str, workspace: Path) -> bool:
    root = workspace.resolve()
    candidate = Path(image_path)
    candidate = candidate if candidate.is_absolute() else root / candidate
    try:
        candidate.resolve().relative_to(root)
    except ValueError:
        return False
    return candidate.is_file()


def _image_dimensions(image_path: Path) -> tuple[int, int] | None:
    """Read actual raster dimensions so model-reported coordinate frames can be checked."""
    try:
        from PIL import Image
        with Image.open(image_path) as image:
            width, height = image.size
        return int(width), int(height)
    except Exception:
        return None


def _asset_records(bundle: dict[str, Any], result: dict[str, Any], workspace: Path) -> list[dict[str, Any]]:
    regions = bundle.get("regions", {})
    panels = bundle.get("panels", {})
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    panel_ids = result.get("panel_ids", []) or []
    if panel_ids:
        for panel_id in panel_ids:
            panel = panels.get(panel_id, {})
            parent_id = panel.get("parent_region_id")
            region = regions.get(parent_id, {})
            # A declared panel path is its source identity even when the file is
            # temporarily absent. Track availability separately; only use the
            # parent Region path when no panel-specific path was recorded.
            image_path = panel.get("image_path") or region.get("image_path")
            if not image_path or str(image_path) in seen:
                continue
            seen.add(str(image_path))
            asset_exists = _asset_exists(str(image_path), workspace)
            resolved_asset = Path(str(image_path))
            resolved_asset = resolved_asset if resolved_asset.is_absolute() else workspace / resolved_asset
            records.append({
                "image_path": str(image_path),
                "asset_exists": asset_exists,
                "asset_sha256": sha256_file(resolved_asset) if asset_exists else None,
                "asset_size_bytes": resolved_asset.stat().st_size if asset_exists else None,
                "page_number": region.get("page_number"),
                "region_id": parent_id,
                "panel_id": panel_id,
                "panel_label": panel.get("label"),
                "pixel_sha256": panel.get("pixel_sha256") or region.get("pixel_sha256"),
                "resolution_scope": "PANEL" if panel.get("image_path") else "PARENT_REGION",
                "pixel_width": panel.get("pixel_width") or (region.get("pixel_width") if not panel.get("image_path") else None),
                "pixel_height": panel.get("pixel_height") or (region.get("pixel_height") if not panel.get("image_path") else None),
            })
            if asset_exists and (
                records[-1].get("pixel_width") is None or records[-1].get("pixel_height") is None
            ):
                dimensions = _image_dimensions(resolved_asset)
                if dimensions:
                    records[-1]["pixel_width"], records[-1]["pixel_height"] = dimensions
            # Parent-region vector coordinates are reusable only when the model
            # sees that same parent-region crop; a separately cropped Panel has
            # its own image coordinate frame and must not inherit parent geometry.
            if not panel.get("image_path"):
                candidate = next((item for item in bundle.get("figure_candidates", {}).values()
                                  if item.get("region_id") == parent_id and item.get("vector_geometry_path")), None)
                if candidate:
                    records[-1]["vector_geometry_path"] = candidate.get("vector_geometry_path")
                    records[-1]["vector_geometry_sha256"] = candidate.get("vector_geometry_sha256")
    if not records:
        for region_id in result.get("region_ids", []) or []:
            region = regions.get(region_id, {})
            image_path = region.get("image_path")
            if not image_path or str(image_path) in seen:
                continue
            seen.add(str(image_path))
            asset_exists = _asset_exists(str(image_path), workspace)
            resolved_asset = Path(str(image_path))
            resolved_asset = resolved_asset if resolved_asset.is_absolute() else workspace / resolved_asset
            records.append({
                "image_path": str(image_path),
                "asset_exists": asset_exists,
                "asset_sha256": sha256_file(resolved_asset) if asset_exists else None,
                "asset_size_bytes": resolved_asset.stat().st_size if asset_exists else None,
                "page_number": region.get("page_number"),
                "region_id": region_id,
                "panel_id": None,
                "panel_label": None,
                "pixel_sha256": region.get("pixel_sha256"),
                "resolution_scope": "REGION",
                "pixel_width": region.get("pixel_width"),
                "pixel_height": region.get("pixel_height"),
            })
            if asset_exists and (
                records[-1].get("pixel_width") is None or records[-1].get("pixel_height") is None
            ):
                dimensions = _image_dimensions(resolved_asset)
                if dimensions:
                    records[-1]["pixel_width"], records[-1]["pixel_height"] = dimensions
            candidate = next((item for item in bundle.get("figure_candidates", {}).values()
                              if item.get("region_id") == region_id and item.get("vector_geometry_path")), None)
            if candidate:
                records[-1]["vector_geometry_path"] = candidate.get("vector_geometry_path")
                records[-1]["vector_geometry_sha256"] = candidate.get("vector_geometry_sha256")
    for asset in records:
        asset["result_id"] = result.get("result_id")
    return records


def _inspection_cards(bundle: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    inspections = bundle.get("visual_inspections", {})
    for entity_id in list(result.get("region_ids", []) or []) + list(result.get("panel_ids", []) or []):
        history = inspections.get(entity_id, {})
        card = history.get("initial") or (history.get("reinspections") or [None])[-1]
        if card:
            output.append({
                "entity_id": entity_id,
                "visual_legibility": card.get("visual_legibility"),
                "data_origin": card.get("data_origin"),
                "quantitative_permission": card.get("quantitative_permission"),
                "observations": card.get("observations", []),
                "instrument_checklist": card.get("instrument_checklist", {}),
                "visual_metadata_assessment": card.get("visual_metadata_assessment", {}),
            })
    return output


def _component_groups(result_ids: list[str], candidates: list[dict[str, Any]]) -> list[list[str]]:
    parent = {result_id: result_id for result_id in result_ids}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for item in candidates:
        left, right = item["result_ids"]
        union(left, right)
    groups: dict[str, list[str]] = defaultdict(list)
    for result_id in result_ids:
        groups[find(result_id)].append(result_id)
    return [sorted(group) for _, group in sorted(groups.items())]


def _analysis_id(source_sha: str, result_ids: list[str]) -> str:
    payload = json.dumps([source_sha, sorted(result_ids)], separators=(",", ":")).encode("utf-8")
    return "SANA-" + hashlib.sha256(payload).hexdigest()[:16]


def build_analysis_pack(
    bundle: dict[str, Any],
    workspace: Path,
    result_ids: list[str],
    candidates: list[dict[str, Any]],
    pack_number: int,
) -> dict[str, Any]:
    results = bundle.get("result_units", {})
    selected = []
    assets = []
    asset_by_path: dict[str, dict[str, Any]] = {}
    for result_id in result_ids:
        result = results[result_id]
        context = result.get("measurement_context", {})
        result_assets = _asset_records(bundle, result, workspace)
        for asset in result_assets:
            image_path = asset["image_path"]
            if image_path in asset_by_path:
                existing = asset_by_path[image_path]
                existing["result_ids"] = sorted(set(existing.get("result_ids", [])) | {result_id})
                continue
            asset["result_ids"] = [result_id]
            asset_by_path[image_path] = asset
            assets.append(asset)
        selected.append({
            "result_id": result_id,
            "data_type": result.get("data_type"),
            "data_origin": result.get("data_origin"),
            "visual_legibility": result.get("visual_legibility"),
            "quantitative_permission": result.get("quantitative_permission"),
            "epistemic_status": result.get("epistemic_status"),
            "claim_role": result.get("claim_role", "UNDECIDED"),
            "measurement_context": context,
            "sample_associations": _sample_association_records(bundle, result),
            "series_associations": [
                {"series_id": item.get("series_id"), "sample_id": item.get("sample_id"),
                 "mapping_status": item.get("mapping_status", "UNKNOWN"),
                 "source_record": source_record,
                 "description": item.get("description", "")}
                for source_record, items in (
                    ("measurement_context", context.get("sample_associations", []) or []),
                    ("observation", result.get("observations", []) or []),
                )
                for item in items
                if item.get("series_id") or item.get("sample_id")
            ],
            "region_ids": result.get("region_ids", []),
            "panel_ids": result.get("panel_ids", []),
            "source_pages": sorted({
                bundle.get("regions", {}).get(region_id, {}).get("page_number")
                for region_id in result.get("region_ids", [])
                if bundle.get("regions", {}).get(region_id, {}).get("page_number") is not None
            }),
            "observations": result.get("observations", []),
            "instrument_checklist": result.get("instrument_checklist", {}),
            "measurement_definition": result.get("measurement_definition"),
            "uncertainty_note": result.get("uncertainty_note"),
            "visual_inspections": _inspection_cards(bundle, result),
            "images": result_assets,
        })
    result_id_set = set(result_ids)
    internal_links = [
        item for item in candidates
        if set(item["result_ids"]).issubset(result_id_set)
    ]
    external_links = [
        item for item in candidates
        if bool(set(item["result_ids"]) & result_id_set)
        and not set(item["result_ids"]).issubset(result_id_set)
    ]
    source = bundle.get("source", {})
    analysis_id = _analysis_id(str(source.get("sha256") or "unknown-source"), result_ids)
    return {
        "analysis_id": analysis_id,
        "analysis_mode": "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS",
        "pack_number": pack_number,
        "source": dict(source),
        "bundle_revision": bundle.get("workspace_revision"),
        "result_ids": result_ids,
        "result_units": selected,
        "assets": assets,
        "asset_count": len(assets),
        "invocation_audit_required": True,
        "plot_reading_audit_required": True,
        "plot_reading_protocol": {
            "required": True,
            "purpose": "Coordinate-calibrated extraction of quantitative values from plots.",
            "geometry_sidecars": [
                {"image_path": item["image_path"], "vector_geometry_path": item.get("vector_geometry_path"),
                 "vector_geometry_sha256": item.get("vector_geometry_sha256"),
                 "pixel_width": item.get("pixel_width"), "pixel_height": item.get("pixel_height")}
                for item in assets if item.get("vector_geometry_path")
            ],
            "boundary": "A calibrated plot estimate is not an exact source value or experimental uncertainty."
        },
        "invocation_audit": {
            "required": True,
            "evidence_level": "AGENT_REPORTED_RUNTIME_RECEIPT",
            "expected_assets": [
                {"image_path": item["image_path"], "asset_sha256": item.get("asset_sha256"),
                 "region_id": item.get("region_id"), "panel_id": item.get("panel_id"),
                 "page_number": item.get("page_number")}
                for item in assets
            ],
            "receipt_rule": "Every expected asset must appear as a native image attachment in the actual model invocation, or the affected Result Units must be NOT_ASSESSABLE."
        },
        "candidate_relationships": internal_links,
        "related_results_outside_pack": external_links,
        "task_status": "READY" if result_ids else "EMPTY",
        "caption_and_narrative_context": "NOT_INCLUDED_IN_REQUEST; MODEL_PRIOR_CONTEXT_MAY_HAVE_SEEN_SOURCE_TEXT",
        "instructions": ANALYSIS_INSTRUCTIONS,
        "required_output": {
            "analysis_id": analysis_id,
            "analysis_mode": "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS",
            "result_ids": result_ids,
            "analysis_status": "COMPLETE | PARTIAL | NOT_ASSESSABLE",
            "summary": "Concise account of what the evidence set establishes, suggests and cannot establish.",
            "coverage": [{
                "result_id": result_id,
                "status": "ANALYZED | NO_COMPARISON_APPLICABLE | NOT_ASSESSABLE",
                "observation_ids": [],
                "reason": "",
            } for result_id in result_ids],
            "observations": [{
                "observation_id": "OBS-1",
                "description": "",
                "epistemic_status": "Observed",
                "result_ids": [],
                "evidence_refs": [{"result_id": "", "region_id": "", "panel_id": None, "page_number": None}],
                "confidence": "High | Medium | Low | Unresolved",
            }],
            "comparisons": [{
                "comparison_id": "CMP-1",
                "question": "",
                "result_ids": [],
                "observation_ids": [],
                "evidence_refs": [{"result_id": "", "region_id": "", "panel_id": None, "page_number": None}],
                "comparison_status": "COMPARABLE | PARTIALLY_COMPARABLE | NOT_COMPARABLE | NOT_APPLICABLE",
                "dimension_assessments": [{
                    "dimension": "",
                    "status": "MATCHED | MISMATCHED | UNKNOWN | NOT_APPLICABLE",
                    "left_or_group_values": [],
                    "consequence": "",
                }],
                "quantitative_differences": [{
                    "measurand": "",
                    "values": [{"result_id": "", "entity_or_group": "", "value": None, "unit": "",
                                "source_basis": "", "precision_or_uncertainty": ""}],
                    "direction_or_pattern": "",
                    "delta_or_effect_size": None,
                    "interpretation_limit": "",
                }],
                "qualitative_differences": [],
                "conclusion": "",
                "limitations": [],
            }],
            "relationships": [{
                "relationship_id": "REL-1",
                "relationship_type": "CONVERGENCE | DIVERGENCE | TREND | CONDITION_RESPONSE | CORRELATION_CANDIDATE | STRUCTURE_PROPERTY | TEMPORAL_OR_SEQUENTIAL | OTHER",
                "description": "",
                "result_ids": [],
                "observation_ids": [],
                "strength": "STRONG | MODERATE | WEAK | UNRESOLVED",
                "causal_status": "NOT_ESTABLISHED | SUPPORTED_WITH_CONTROLS | ESTABLISHED_BY_DESIGN",
                "limitations": [],
            }],
            "interpretations": [{
                "interpretation_id": "INT-1",
                "description": "",
                "epistemic_status": "Interpreted | Hypothesized",
                "supporting_observation_ids": [],
                "alternative_explanations": [],
                "confidence": "High | Medium | Low | Unresolved",
                "limitations": [],
            }],
            "contradictions": [{
                "contradiction_id": "CONTRA-1",
                "description": "",
                "result_ids": [],
                "evidence_refs": [],
                "possible_reasons": [],
                "resolution_status": "UNRESOLVED | EXPLAINED | REQUIRES_REVIEW",
            }],
            "candidate_scientific_implications": [],
            "unresolved_questions": [],
            "limitations": [],
            "signal_analysis_coverage": [{
                "result_id": result_id,
                "status": "APPLICABLE | NOT_APPLICABLE | NOT_ASSESSABLE",
                "feature_ids": [],
                "comparison_ids": [],
                "reason": ""
            } for result_id in result_ids],
            "plot_calibrations": [{
                "calibration_id": "PLOT-1",
                "result_id": "",
                "plot_type": "XY_LINE | SPECTRUM | DIFFRACTOGRAM | SCATTER | BAR | HISTOGRAM | HEATMAP | OTHER",
                "coordinate_system": "IMAGE_PIXEL | PDF_CROP_POINT",
                "coordinate_frame": {"width": 0, "height": 0},
                "plot_area": [0, 0, 0, 0],
                "evidence_refs": [{"result_id": "", "region_id": "", "panel_id": None, "page_number": None}],
                "x_axis": {"label": "", "unit": "", "scale": "LINEAR | LOG10 | CATEGORICAL | UNKNOWN",
                           "tick_anchors": [{"coordinate": 0, "value": 0, "printed_label": "", "coordinate_uncertainty": 0.5, "value_uncertainty": 0}]},
                "y_axis": {"label": "", "unit": "", "scale": "LINEAR | LOG10 | CATEGORICAL | UNKNOWN",
                           "tick_anchors": [{"coordinate": 0, "value": 0, "printed_label": "", "coordinate_uncertainty": 0.5, "value_uncertainty": 0}]},
                "series": [{"series_id": "", "legend_label": "", "mapping_status": "CONFIRMED | PROBABLE | AMBIGUOUS | UNRESOLVED",
                            "source_path_ids": []}],
                "limitations": []
            }],
            "plot_readings": [{
                "reading_id": "READ-1",
                "calibration_id": "PLOT-1",
                "result_id": "",
                "series_id": None,
                "reading_role": "DATA_POINT | FEATURE_POSITION | FEATURE_EDGE | BAR_ENDPOINT | PLATEAU_BOUNDARY | OTHER",
                "coordinate_source": "RASTER_IMAGE | VECTOR_GEOMETRY",
                "coordinate": {"x": 0, "y": 0},
                "coordinate_uncertainty": {"x": 1.0, "y": 1.0},
                "vector_ref": {"path_id": "", "item_index": 0, "point_index": 0},
                "evidence_refs": [{"result_id": "", "region_id": "", "panel_id": None, "page_number": None}]
            }],
            "signal_features": [{
                "feature_id": "SIG-1",
                "result_id": "",
                "series_id": None,
                "series_label": "visible legend label or UNKNOWN",
                "feature_type": "PEAK | BAND | REFLECTION | EDGE | SHOULDER | PLATEAU | OTHER",
                "feature_label": "",
                "description": "",
                "axis_context": {
                    "x_axis_label": "visible axis title or UNKNOWN",
                    "x_axis_unit": "visible unit or UNKNOWN",
                    "x_axis_scale": "LINEAR | LOG | CATEGORICAL | UNKNOWN",
                    "y_axis_label": "visible axis title or UNKNOWN",
                    "y_axis_unit": "visible unit or UNKNOWN",
                    "y_axis_scale": "LINEAR | LOG | CATEGORICAL | UNKNOWN",
                    "normalization_basis": "reported basis or UNKNOWN"
                },
                "position": {"value": None, "unit": "", "reading_basis": "CALIBRATED_PLOT_READING | EXACT_SOURCE_DATA | EXACT_TEXT | EXACT_TABLE | PRINTED_FIGURE_VALUE | DERIVED_FROM_EXPLICIT_VALUES | UNRESOLVED", "precision_or_uncertainty": "", "confidence": "High | Medium | Low | Unresolved", "plot_reading_ids": [], "calculation": {"operation": "DIRECT", "axis": "x"}},
                "width": {"value": None, "unit": "", "reading_basis": "CALIBRATED_PLOT_READING | EXACT_SOURCE_DATA | EXACT_TEXT | EXACT_TABLE | PRINTED_FIGURE_VALUE | DERIVED_FROM_EXPLICIT_VALUES | UNRESOLVED", "precision_or_uncertainty": "", "plot_reading_ids": [], "calculation": {"operation": "DIFFERENCE", "axis": "x"}},
                "intensity": {"value": None, "unit": "", "reading_basis": "CALIBRATED_PLOT_READING | EXACT_SOURCE_DATA | EXACT_TEXT | EXACT_TABLE | PRINTED_FIGURE_VALUE | DERIVED_FROM_EXPLICIT_VALUES | UNRESOLVED", "normalization_basis": "", "precision_or_uncertainty": "", "plot_reading_ids": [], "calculation": {"operation": "DIRECT", "axis": "y"}},
                "area": {"value": None, "unit": "", "reading_basis": "EXACT_SOURCE_DATA | EXACT_TEXT | EXACT_TABLE | PRINTED_FIGURE_VALUE | DERIVED_FROM_EXPLICIT_VALUES | UNRESOLVED", "normalization_basis": "", "precision_or_uncertainty": "", "plot_reading_ids": []},
                "evidence_refs": [{"result_id": "", "region_id": "", "panel_id": None, "page_number": None}]
            }],
            "signal_comparisons": [{
                "comparison_id": "SIGCMP-1",
                "feature_ids": [],
                "result_ids": [],
                "change_type": "POSITION_SHIFT | WIDTH_CHANGE | INTENSITY_CHANGE | AREA_CHANGE | APPEARED | DISAPPEARED | SHAPE_CHANGE | OTHER",
                "description": "",
                "direction_or_pattern": "",
                "comparability_status": "COMPARABLE | PARTIALLY_COMPARABLE | NOT_COMPARABLE | UNKNOWN",
                "normalization_basis": "",
                "quantified_change": {"metric": "", "value": None, "unit": "", "source_basis": "CALIBRATED_PLOT_READING | EXACT_SOURCE_DATA | EXACT_TEXT | EXACT_TABLE | PRINTED_FIGURE_VALUE | DERIVED_FROM_EXPLICIT_VALUES | UNRESOLVED", "precision_or_uncertainty": "",
                                      "plot_reading_ids": [], "calculation": {"operation": "DIFFERENCE | RATIO | PERCENT_CHANGE", "axis": "x | y"}},
                "evidence_refs": [{"result_id": "", "region_id": "", "panel_id": None, "page_number": None}],
                "interpretation_limits": []
            }],
            "model_invocation": {
                "invocation_id": "",
                "status": "RESPONSE_RECEIVED | BLOCKED | UNVERIFIABLE",
                "model_id": "",
                "input_mode": "NATIVE_IMAGE_ATTACHMENTS | TEXT_ONLY_PATHS | UNVERIFIABLE",
                "evidence_level": "AGENT_REPORTED_RUNTIME_RECEIPT",
                "attached_assets": [{"image_path": "", "asset_sha256": "", "attachment_type": "NATIVE_IMAGE", "attachment_reference": ""}],
                "request_log_path": "",
                "request_log_sha256": "",
                "response_log_path": "",
                "response_log_sha256": "",
                "limitations": []
            }
        },
        "invocation_audit_required": True
    }


def prepare_all(
    bundle: dict[str, Any],
    workspace: Path,
    max_results_per_pack: int = DEFAULT_MAX_RESULTS_PER_PACK,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    results = bundle.get("result_units", {})
    if max_results_per_pack < 2:
        raise ValueError("max_results_per_pack must be at least 2")
    result_ids = sorted(results)
    candidates = discover_relationship_candidates(bundle)
    groups = _component_groups(result_ids, candidates)

    multi_result_groups = [group for group in groups if len(group) > 1]
    isolated_ids = sorted(result_id for group in groups if len(group) == 1 for result_id in group)
    chunks: list[list[str]] = []
    for group in multi_result_groups:
        for start in range(0, len(group), max_results_per_pack):
            chunks.append(group[start:start + max_results_per_pack])
    for start in range(0, len(isolated_ids), max_results_per_pack):
        chunks.append(isolated_ids[start:start + max_results_per_pack])
    if not chunks and result_ids:
        chunks = [result_ids[:max_results_per_pack]]

    packs = [
        build_analysis_pack(bundle, workspace, ids, candidates, index + 1)
        for index, ids in enumerate(chunks)
    ]
    assigned_regions = {
        region_id for result in results.values() for region_id in result.get("region_ids", [])
    }
    assigned_panels = {
        panel_id for result in results.values() for panel_id in result.get("panel_ids", [])
    }
    unassigned_regions = sorted(set(bundle.get("regions", {})) - assigned_regions)
    unassigned_panels = sorted(set(bundle.get("panels", {})) - assigned_panels)
    unassigned_region_assets = [{
        "region_id": region_id,
        "page_number": bundle.get("regions", {}).get(region_id, {}).get("page_number"),
        "image_path": bundle.get("regions", {}).get(region_id, {}).get("image_path"),
        "region_type": bundle.get("regions", {}).get(region_id, {}).get("region_type"),
        "triage_role": bundle.get("regions", {}).get(region_id, {}).get("triage_role"),
    } for region_id in unassigned_regions]
    unassigned_panel_assets = [{
        "panel_id": panel_id,
        "parent_region_id": bundle.get("panels", {}).get(panel_id, {}).get("parent_region_id"),
        "image_path": bundle.get("panels", {}).get(panel_id, {}).get("image_path"),
        "label": bundle.get("panels", {}).get(panel_id, {}).get("label"),
    } for panel_id in unassigned_panels]
    coverage = {
        result_id: next(pack["analysis_id"] for pack in packs if result_id in pack["result_ids"])
        for result_id in result_ids
    }
    cross_pack_relationships = [
        item for item in candidates
        if coverage.get(item["result_ids"][0]) != coverage.get(item["result_ids"][1])
    ]
    figure_candidates = bundle.get("figure_candidates", {})
    figure_candidate_coverage = [
        {
            "candidate_id": candidate_id,
            "page_number": candidate.get("page_number"),
            "region_id": candidate.get("region_id"),
            "extraction_status": candidate.get("extraction_status"),
            "triage_status": candidate.get("triage_status"),
            "disposition": candidate.get("disposition"),
            "result_ids": candidate.get("result_ids", []),
            "reason": candidate.get("reason"),
            "asset_sha256": candidate.get("asset_sha256"),
        }
        for candidate_id, candidate in sorted(figure_candidates.items())
    ]
    index = {
        "source_sha256": bundle.get("source", {}).get("sha256"),
        "analysis_mode": "GENERAL_SCIENTIFIC_EVIDENCE_ANALYSIS",
        "result_unit_count": len(result_ids),
        "figure_candidate_count": len(figure_candidate_coverage),
        "pending_figure_candidate_ids": [
            item["candidate_id"] for item in figure_candidate_coverage
            if item.get("triage_status") != "REVIEWED"
        ],
        "figure_candidate_coverage": figure_candidate_coverage,
        "candidate_relationship_count": len(candidates),
        "cross_pack_relationships": cross_pack_relationships,
        "pack_count": len(packs),
        "coverage_map": coverage,
        "unassigned_region_ids": unassigned_regions,
        "unassigned_panel_ids": unassigned_panels,
        "unassigned_region_assets": unassigned_region_assets,
        "unassigned_panel_assets": unassigned_panel_assets,
        "packs": [{
            "analysis_id": pack["analysis_id"],
            "pack_number": pack["pack_number"],
            "result_ids": pack["result_ids"],
            "asset_count": pack["asset_count"],
            "task_status": pack["task_status"],
        } for pack in packs],
        "limitations": [
            "Candidate relationships are navigation hints, not declarations of scientific comparability.",
            "All Result Units are assigned to a pack; the model must still record ANALYZED, NO_COMPARISON_APPLICABLE or NOT_ASSESSABLE for each.",
            "Regions/Panels not linked to any Result Unit remain explicit extraction-coverage gaps.",
            "Every detected vector-figure candidate requires an explicit inclusion/exclusion disposition and, when included, a Result Unit link before evidence validation can pass.",
        ],
    }
    return index, packs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, help="Defaults to WORKSPACE/cache/scientific_analysis")
    parser.add_argument("--max-results-per-pack", type=int, default=DEFAULT_MAX_RESULTS_PER_PACK)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    output_dir = (args.output_dir or (workspace / "cache" / "scientific_analysis")).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    index, packs = prepare_all(bundle, workspace, args.max_results_per_pack)
    for pack in packs:
        atomic_write_json(output_dir / f"{pack['analysis_id']}_request.json", pack)
    atomic_write_json(output_dir / "analysis_index.json", index)
    print(json.dumps(index, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
