#!/usr/bin/env python3
"""Prepare joint, original-resolution Raman/FTIR comparison tasks from Result Units."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from era_core import atomic_write_json, load_evidence_bundle

SPECTRAL_TERMS = (
    (re.compile(r"\braman\b", re.I), "Raman"),
    (re.compile(r"\bftir\b|\bft-ir\b|\binfrared\b|\bir spectroscopy\b", re.I), "FTIR"),
)
COMPARISON_INSTRUCTIONS = [
    "Inspect every supplied original-resolution image in this task as ONE joint comparison set. Do not write isolated single-spectrum captions as the final answer.",
    "First identify each plotted spectrum/curve, legend entry, sample label and the Result Unit / panel it belongs to. A single Result Unit may contain several sample traces; compare those traces when labels permit.",
    "Before comparing, assess whether spectra are comparable: technique/mode (including ATR vs transmission where relevant), x/y axes and units, spectral range, resolution/calibration, acquisition settings, sample state/preparation, baseline treatment, normalization, smoothing, vertical offsets and replicate basis. Mark unknown dimensions explicitly.",
    "Do not force a comparison across incompatible modes, units, spectral ranges, sample states or processing. Separate compatible subsets and explain why excluded items cannot be compared.",
    "For each defensible band comparison, report approximate peak/band positions only to the precision supported by the original axis ticks and image resolution; state the uncertainty/range. Describe shift direction and approximate magnitude when supported. Never invent exact peak positions.",
    "Compare relative intensity trends and apparent band-area trends when the plotted basis and baseline/normalization make that meaningful. State whether the comparison is qualitative, semi-quantitative or quantitatively supported. Do not claim integrated peak area from a simple curve unless an area/integration basis is actually available.",
    "Explicitly identify bands that appear, disappear, split, merge, broaden, narrow or remain approximately unchanged between samples. Do not equate a band becoming invisible with chemical absence when overlap, noise or plotting scale could explain it.",
    "Connect the observed spectral changes to plausible functional groups, bonds, coordination environments or chemical interactions. Separate direct observations, interpretations and hypotheses. Give confidence and competing assignments/alternative explanations.",
    "Audit confounders including baseline drift, water/CO2 contributions, sample loading/thickness, particle size/contact (especially ATR), orientation, fluorescence, fluorescence subtraction, normalization, smoothing, peak overlap, different acquisition settings and matrix effects.",
    "Use only supplied evidence and linked Result Units. Cross-check against other characterization results only when those results are explicitly supplied in this bundle. Do not invent cross-validation or literature support.",
    "Extract candidate scientific implications that could distinguish the samples or support a mechanism, but label them as candidate interpretations/hypotheses rather than established novelty.",
    "If the evidence cannot support a valid comparison, return NOT_COMPARABLE or PARTIAL with the precise blocker. This is a valid result; do not manufacture a difference."
]

def classify_spectral_technique(result: dict[str, Any]) -> str | None:
    context = result.get("measurement_context", {})
    text = " ".join(str(value or "") for value in (
        result.get("data_type"), context.get("technique"), context.get("measurement_group")
    ))
    for pattern, technique in SPECTRAL_TERMS:
        if pattern.search(text):
            return technique
    return None

def _sample_details(bundle: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    associations = list(result.get("measurement_context", {}).get("sample_associations", []))
    for observation in result.get("observations", []):
        sample_id = observation.get("sample_id")
        if sample_id and not any(item.get("sample_id") == sample_id for item in associations):
            associations.append({
                "sample_id": sample_id,
                "mapping_status": observation.get("mapping_status", "UNKNOWN"),
                "series_id": observation.get("series_id"),
            })
    output = []
    for item in associations:
        sample_id = item.get("sample_id")
        sample = bundle.get("samples", {}).get(sample_id, {}) if sample_id else {}
        aliases = [alias.get("alias") for alias in sample.get("aliases", []) if alias.get("alias")]
        output.append({
            "sample_id": sample_id, "sample_aliases": aliases,
            "mapping_status": item.get("mapping_status", "UNMAPPED"),
            "series_id": item.get("series_id"),
        })
    return output

def _visual_notes(bundle: dict[str, Any], entity_ids: list[str]) -> list[dict[str, Any]]:
    output = []
    inspections = bundle.get("visual_inspections", {})
    for entity_id in entity_ids:
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
            })
    return output

def _assets_for_result(bundle: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    regions, panels = bundle.get("regions", {}), bundle.get("panels", {})
    result_assets, seen = [], set()
    panel_ids = result.get("panel_ids", [])
    if panel_ids:
        for panel_id in panel_ids:
            panel = panels.get(panel_id, {})
            parent_id = panel.get("parent_region_id")
            region = regions.get(parent_id, {})
            image_path = panel.get("image_path") or region.get("image_path")
            if image_path and image_path not in seen:
                seen.add(image_path)
                result_assets.append({
                    "image_path": image_path, "page_number": region.get("page_number"),
                    "region_id": parent_id, "panel_id": panel_id,
                    "crop_scope": "PANEL" if panel.get("image_path") else "PARENT_REGION",
                    "panel_label": panel.get("label"),
                    "pixel_sha256": panel.get("pixel_sha256") or region.get("pixel_sha256"),
                })
    if not result_assets:
        for region_id in result.get("region_ids", []):
            region = regions.get(region_id, {})
            image_path = region.get("image_path")
            if image_path and image_path not in seen:
                seen.add(image_path)
                result_assets.append({
                    "image_path": image_path, "page_number": region.get("page_number"),
                    "region_id": region_id, "panel_id": None, "crop_scope": "REGION",
                    "panel_label": None, "pixel_sha256": region.get("pixel_sha256"),
                })
    return result_assets

def _comparison_id(source_sha: str, technique: str, group_key: str, result_ids: list[str]) -> str:
    payload = json.dumps([source_sha, technique, group_key, sorted(result_ids)],
                         ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "SCMP-" + hashlib.sha256(payload).hexdigest()[:16]

def build_payload(
    bundle: dict[str, Any], workspace: Path, result_ids: list[str],
    technique: str | None = None, group_key: str | None = None,
    grouping_status: str = "EXPLICIT_SELECTION",
) -> dict[str, Any]:
    if not result_ids:
        raise ValueError("At least one Result Unit ID is required")
    if len(result_ids) != len(set(result_ids)):
        raise ValueError("Duplicate Result Unit IDs are not allowed")
    results = bundle.get("result_units", {})
    missing = [rid for rid in result_ids if rid not in results]
    if missing:
        raise KeyError(f"Unknown Result Unit IDs: {', '.join(missing)}")
    selected = [(rid, results[rid]) for rid in result_ids]
    techniques = {classify_spectral_technique(result) for _, result in selected}
    techniques.discard(None)
    if len(techniques) != 1 or any(classify_spectral_technique(result) is None for _, result in selected):
        raise ValueError("A comparison pack must contain only one spectral technique (Raman or FTIR)")
    detected_technique = next(iter(techniques))
    if technique and technique != detected_technique:
        raise ValueError(f"Requested technique {technique} does not match {detected_technique}")
    if group_key is None:
        explicit_groups = {
            str(result.get("measurement_context", {}).get("measurement_group") or "").strip()
            for _, result in selected
        }
        explicit_groups.discard("")
        group_key = next(iter(explicit_groups)) if len(explicit_groups) == 1 else "UNSPECIFIED_OR_MIXED"
        if len(explicit_groups) > 1:
            grouping_status = "MIXED_MEASUREMENT_GROUPS_REQUIRES_REVIEW"

    comparison_id = _comparison_id(
        str(bundle.get("source", {}).get("sha256") or "unknown-source"),
        detected_technique, group_key, result_ids
    )
    assets, result_entries = [], []
    for rid, result in selected:
        context = result.get("measurement_context", {})
        for asset in _assets_for_result(bundle, result):
            asset["result_ids"] = [rid]
            existing = next((item for item in assets if item["image_path"] == asset["image_path"]), None)
            if existing:
                if rid not in existing["result_ids"]:
                    existing["result_ids"].append(rid)
            else:
                assets.append(asset)
        entity_ids = list(result.get("panel_ids", [])) + list(result.get("region_ids", []))
        result_entries.append({
            "result_id": rid, "data_type": result.get("data_type"),
            "technique": context.get("technique"),
            "measurement_group": context.get("measurement_group"),
            "measurement_conditions": context.get("measurement_conditions", {}),
            "sample_associations": _sample_details(bundle, result),
            "region_ids": result.get("region_ids", []), "panel_ids": result.get("panel_ids", []),
            "page_numbers": sorted({
                bundle.get("regions", {}).get(region_id, {}).get("page_number")
                for region_id in result.get("region_ids", [])
                if bundle.get("regions", {}).get(region_id, {}).get("page_number") is not None
            }),
            "visual_legibility": result.get("visual_legibility"),
            "quantitative_permission": result.get("quantitative_permission"),
            "data_origin": result.get("data_origin"),
            "uncertainty_note": result.get("uncertainty_note"),
            "previous_visual_observations": _visual_notes(bundle, entity_ids),
        })

    return {
        "comparison_id": comparison_id, "comparison_mode": "SPECTRAL_CROSS_SAMPLE",
        "technique": detected_technique, "group_key": group_key,
        "grouping_status": grouping_status, "source": bundle.get("source", {}),
        "result_ids": result_ids, "results": result_entries, "images": assets,
        "image_asset_count": len(assets),
        "task_status": "READY_FOR_JOINT_VISUAL_REVIEW" if assets else "BLOCKED_NO_IMAGE_ASSETS",
        "caption_text_included": False, "report_narrative_included": False,
        "instructions": COMPARISON_INSTRUCTIONS,
        "required_output": {
            "comparison_id": comparison_id, "comparison_mode": "SPECTRAL_CROSS_SAMPLE",
            "result_ids": result_ids, "technique": detected_technique,
            "comparison_status": "COMPLETE | PARTIAL | NOT_COMPARABLE",
            "summary": "A concise comparative scientific conclusion; explicitly state what changed and what did not.",
            "comparability_assessment": {
                "status": "COMPARABLE | PARTIALLY_COMPARABLE | NOT_COMPARABLE | UNKNOWN",
                "assessed_dimensions": [
                    {"dimension": "technique_and_mode", "status": "MATCHED | MISMATCHED | UNKNOWN | NOT_APPLICABLE", "note": ""},
                    {"dimension": "axes_units_range_and_resolution", "status": "MATCHED | MISMATCHED | UNKNOWN | NOT_APPLICABLE", "note": ""},
                    {"dimension": "acquisition_and_calibration", "status": "MATCHED | MISMATCHED | UNKNOWN | NOT_APPLICABLE", "note": ""},
                    {"dimension": "sample_state_and_preparation", "status": "MATCHED | MISMATCHED | UNKNOWN | NOT_APPLICABLE", "note": ""},
                    {"dimension": "baseline_normalization_and_processing", "status": "MATCHED | MISMATCHED | UNKNOWN | NOT_APPLICABLE", "note": ""},
                    {"dimension": "signal_basis_and_scaling", "status": "MATCHED | MISMATCHED | UNKNOWN | NOT_APPLICABLE", "note": ""},
                ],
                "conclusion": "",
            },
            "sample_groups": [],
            "direct_observations": [
                {"description": "", "result_ids": [], "source_status": "Observed", "confidence": "High | Medium | Low"}
            ],
            "band_comparisons": [{
                "feature_id": "",
                "change_type": "SHIFT | RELATIVE_INTENSITY | AREA_TREND | NEW_BAND | DISAPPEARING_BAND | SPLITTING | MERGING | BROADENING | NARROWING | SIMILARITY | OTHER",
                "samples_or_series": [],
                "position_comparison": "Approximate positions/ranges and shift direction; unresolved when unsupported.",
                "relative_signal_comparison": "Qualitative/semi-quantitative trend only when supported.",
                "signal_basis": "Intensity / absorbance / transmittance / integrated area / unavailable",
                "observed_change": "", "result_ids": [],
                "evidence_refs": [{"result_id": "", "region_id": "", "panel_id": "", "page_number": 0}],
                "interpretation": "", "interpretation_confidence": "High | Medium | Low | Unresolved",
                "alternative_explanations": [],
            }],
            "functional_group_interpretations": [{
                "assignment": "", "supporting_feature_ids": [],
                "epistemic_status": "Interpreted | Hypothesized", "rationale": "",
                "confidence": "High | Medium | Low | Unresolved", "alternatives": [],
            }],
            "candidate_scientific_implications": [], "cross_validation": [], "limitations": [],
        },
    }

def discover_groups(bundle: dict[str, Any]) -> list[tuple[str, str, list[str], str]]:
    """Group by technique and explicit measurement_group; unknown groups remain provisional."""
    groups: dict[tuple[str, str], list[str]] = {}
    for result_id, result in sorted(bundle.get("result_units", {}).items()):
        technique = classify_spectral_technique(result)
        if not technique:
            continue
        group = str(result.get("measurement_context", {}).get("measurement_group") or "").strip()
        group_key = group or "UNSPECIFIED_MEASUREMENT_GROUP"
        groups.setdefault((technique, group_key), []).append(result_id)
    return [
        (technique, group_key, ids,
         "EXPLICIT_MEASUREMENT_GROUP" if group_key != "UNSPECIFIED_MEASUREMENT_GROUP"
         else "GROUPING_REQUIRES_MODEL_REVIEW")
        for (technique, group_key), ids in sorted(groups.items())
    ]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--auto", action="store_true",
                          help="Create one pack per technique/measurement_group candidate")
    selector.add_argument("--result-ids", help="Comma-separated Result Unit IDs for one explicit comparison set")
    parser.add_argument("--output-dir", type=Path, help="Defaults to WORKSPACE/cache/spectral_comparisons")
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    output_dir = (args.output_dir or (workspace / "cache" / "spectral_comparisons")).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.auto:
        groups = discover_groups(bundle)
    else:
        ids = [item.strip() for item in args.result_ids.split(",") if item.strip()]
        payload = build_payload(bundle, workspace, ids)
        groups = [(payload["technique"], payload["group_key"], ids, payload["grouping_status"])]
    index = {
        "source_sha256": bundle.get("source", {}).get("sha256"), "packs": [],
        "spectral_result_units_found": len({rid for _, _, ids, _ in discover_groups(bundle) for rid in ids}),
    }
    for technique, group_key, result_ids, grouping_status in groups:
        payload = build_payload(bundle, workspace, result_ids, technique, group_key, grouping_status)
        output = output_dir / f"{payload['comparison_id']}_request.json"
        atomic_write_json(output, payload)
        index["packs"].append({
            "comparison_id": payload["comparison_id"], "technique": technique,
            "group_key": group_key, "grouping_status": grouping_status,
            "result_ids": result_ids, "image_asset_count": payload["image_asset_count"],
            "task_status": payload["task_status"], "request_path": str(output),
        })
    atomic_write_json(output_dir / "comparison_index.json", index)
    print(json.dumps(index, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
