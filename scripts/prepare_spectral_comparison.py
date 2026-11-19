#!/usr/bin/env python3
"""Prepare joint, caption-excluded Raman/IR comparison tasks from the Evidence Bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle

SPECTRAL_TERMS = re.compile(
    r"\b(raman|ftir|drifts|infrared|infra-red|vibrational spectroscopy|"
    r"vibrational spectrum|vibrational spectra|wavenumber)\b|cm\s*[-−^]?\s*1",
    re.IGNORECASE,
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{key} {_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return " ".join(_text(item) for item in value)
    return str(value)


def classify_spectral_modality(*values: Any) -> str | None:
    """Identify the most specific vibrational modality supported by source fields."""
    text = " ".join(_text(value) for value in values)
    if not SPECTRAL_TERMS.search(text):
        return None
    low = text.lower()
    if re.search(r"\braman\b", low):
        return "RAMAN"
    if re.search(r"\bdrifts\b|diffuse reflectance infrared", low):
        return "DRIFTS"
    if re.search(r"\bftir\b|fourier transform infrared", low):
        return "FTIR"
    if re.search(r"\binfra[- ]?red\b|\bir spectrum\b|\bir spectra\b", low):
        return "IR"
    return "VIBRATIONAL_SPECTRUM_UNSPECIFIED"


def _card(bundle: dict[str, Any], entity_id: str) -> dict[str, Any]:
    return bundle.get("visual_inspections", {}).get(entity_id, {}).get("initial") or {}


def _snapshot(card: dict[str, Any]) -> dict[str, Any]:
    allowed = ("plot_type", "axes", "legend_series", "instrument_fields", "instrument_checklist",
               "observations", "visual_legibility", "data_origin", "quantitative_permission", "uncertainty_note")
    result = {key: card[key] for key in allowed if key in card}
    result.update({"caption_text": None, "report_narrative": None,
                   "caption_text_included": False, "report_narrative_included": False})
    return result


def _entity_ids(bundle: dict[str, Any], result: dict[str, Any]) -> list[str]:
    panels = bundle.get("panels", {})
    selected = [pid for pid in result.get("panel_ids", []) if pid in panels]
    if not selected:
        selected = [rid for rid in result.get("region_ids", []) if rid in bundle.get("regions", {})]
    return list(dict.fromkeys(selected))


def _asset(bundle: dict[str, Any], entity_id: str, result_ids: list[str]) -> dict[str, Any] | None:
    panels, regions = bundle.get("panels", {}), bundle.get("regions", {})
    entity = panels.get(entity_id) or regions.get(entity_id)
    if not entity:
        return None
    parent_id = entity.get("parent_region_id") if entity_id in panels else None
    parent = regions.get(parent_id or "", {})
    image_path = entity.get("image_path") or parent.get("image_path")
    if not image_path:
        return None
    card = _card(bundle, entity_id) or _card(bundle, parent_id or "")
    return {
        "entity_id": entity_id,
        "entity_type": "panel" if entity_id in panels else "region",
        "parent_region_id": parent_id,
        "page_number": entity.get("page_number") or parent.get("page_number"),
        "image_path": image_path,
        "pixel_sha256": entity.get("pixel_sha256") or parent.get("pixel_sha256"),
        "visual_inspection": _snapshot(card),
        "linked_result_ids": list(result_ids),
    }


def _sample(bundle: dict[str, Any], sample_id: str | None) -> dict[str, Any]:
    item = bundle.get("samples", {}).get(sample_id or "")
    if not item:
        return {"sample_id": sample_id, "label": "unmapped", "identity_status": "UNMAPPED"}
    alias = next((a.get("alias") for a in item.get("aliases", []) if a.get("alias")), sample_id)
    return {"sample_id": sample_id, "label": alias, "identity_status": item.get("identity_status", "UNMAPPED")}


def _unit(bundle: dict[str, Any], result_id: str, result: dict[str, Any], entities: list[str],
          associations: list[dict[str, Any]], series: dict[str, Any] | None, suffix: str) -> dict[str, Any]:
    context = result.get("measurement_context", {})
    eid = entities[0]
    visual = _card(bundle, eid)
    if eid in bundle.get("panels", {}):
        visual = visual or _card(bundle, bundle["panels"][eid].get("parent_region_id", ""))
    return {
        "unit_id": result_id + suffix, "result_id": result_id, "entity_ids": entities,
        "sample_associations": associations,
        "samples": [_sample(bundle, item.get("sample_id")) for item in associations],
        "series": series, "condition_summary": context.get("measurement_conditions", {}),
        "measurement_group": context.get("measurement_group"), "technique": context.get("technique"),
        "data_type": result.get("data_type"), "data_origin": result.get("data_origin"),
        "visual_legibility": result.get("visual_legibility"),
        "quantitative_permission": result.get("quantitative_permission"),
        "first_pass_visual_observations": _snapshot(visual),
    }


def _result_candidate(bundle: dict[str, Any], result_id: str, result: dict[str, Any]):
    entities = _entity_ids(bundle, result)
    context = result.get("measurement_context", {})
    cards = [_card(bundle, eid) for eid in entities]
    modality = classify_spectral_modality(context.get("technique"), result.get("data_type"))
    if modality is None:
        signatures = []
        for card in cards:
            axes = card.get("axes", {})
            signatures.extend([card.get("plot_type"), axes.get("x", {}).get("label"),
                               axes.get("x", {}).get("unit"), card.get("instrument_checklist", {})])
        modality = classify_spectral_modality(signatures)
    if modality is None or not entities:
        return None, []
    legend = max((c.get("legend_series", []) for c in cards), key=len, default=[])
    associations = context.get("sample_associations", [])
    if len(legend) >= 2:
        units = []
        for idx, entry in enumerate(legend, 1):
            series = entry if isinstance(entry, dict) else {"label": str(entry)}
            units.append(_unit(bundle, result_id, result, entities, associations, series, f"::series-{idx}"))
    elif len(associations) >= 2:
        units = [_unit(bundle, result_id, result, entities, [a], None, f"::sample-{idx}")
                 for idx, a in enumerate(associations, 1)]
    else:
        units = [_unit(bundle, result_id, result, entities, associations, None, "")]
    return modality, units


def _fallback_units(bundle: dict[str, Any], linked: set[str]):
    for eid, history in bundle.get("visual_inspections", {}).items():
        if eid in linked:
            continue
        card = history.get("initial") or {}
        axes = card.get("axes", {})
        modality = classify_spectral_modality(card.get("plot_type"), axes.get("x", {}).get("label"),
                                               axes.get("x", {}).get("unit"), card.get("instrument_checklist", {}))
        entity = bundle.get("panels", {}).get(eid) or bundle.get("regions", {}).get(eid)
        if not modality or not entity:
            continue
        legend = card.get("legend_series", [])
        series_items = legend if len(legend) >= 2 else [None]
        for idx, series in enumerate(series_items, 1):
            unit_id = f"{eid}::visual-series-{idx}" if series else eid
            yield modality, eid, {
                "unit_id": unit_id, "result_id": None, "entity_ids": [eid],
                "sample_associations": [], "samples": [], "series": series,
                "condition_summary": {}, "measurement_group": None, "technique": modality,
                "data_type": "visual-inspection-only", "data_origin": "Unavailable",
                "visual_legibility": card.get("visual_legibility", "Unassessable"),
                "quantitative_permission": "None", "first_pass_visual_observations": _snapshot(card)
            }


def build_comparison_tasks(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Group all candidates by modality across a source document, without merging techniques."""
    groups: dict[str, dict[str, Any]] = defaultdict(lambda: {"units": {}, "assets": {}})
    linked: set[str] = set()
    for rid, result in sorted(bundle.get("result_units", {}).items()):
        modality, units = _result_candidate(bundle, rid, result)
        if not modality:
            continue
        entities = _entity_ids(bundle, result)
        for eid in entities:
            linked.add(eid)
            asset = _asset(bundle, eid, [rid])
            if asset:
                if eid in groups[modality]["assets"]:
                    existing = groups[modality]["assets"][eid]
                    existing["linked_result_ids"] = sorted(set(existing["linked_result_ids"] + [rid]))
                else:
                    groups[modality]["assets"][eid] = asset
        for unit in units:
            groups[modality]["units"][unit["unit_id"]] = unit

    for modality, eid, unit in _fallback_units(bundle, linked):
        asset = _asset(bundle, eid, [])
        if asset:
            groups[modality]["assets"].setdefault(eid, asset)
            groups[modality]["units"].setdefault(unit["unit_id"], unit)

    source = bundle.get("source", {})
    tasks = []
    for modality, grouped in sorted(groups.items()):
        units, assets = list(grouped["units"].values()), list(grouped["assets"].values())
        if len(units) < 2 or not assets:
            continue
        digest_input = json.dumps({"source": source.get("sha256"), "modality": modality,
                                   "units": sorted(u["unit_id"] for u in units)},
                                  ensure_ascii=False, sort_keys=True).encode("utf-8")
        task_id = "SPC" + hashlib.sha256(digest_input).hexdigest()[:10].upper()
        dimensions = ["spectral_modality_and_acquisition_mode", "spectral_range_and_x_axis_unit",
                      "intensity_or_transmittance_basis", "baseline_and_normalization",
                      "instrument_and_acquisition_conditions", "sample_state_and_preparation",
                      "timepoint_or_treatment_condition", "plot_scaling_offsets_and_stacking"]
        tasks.append({
            "task_id": task_id, "task_type": "CROSS_SAMPLE_SPECTRAL_COMPARISON",
            "comparison_mode": "CAPTION_EXCLUDED_COMPARATIVE_VISUAL_REVIEW",
            "modality": modality, "measurement_group": "DOCUMENT_SCOPE",
            "source": {"file_name": source.get("file_name"), "sha256": source.get("sha256")},
            "assets": assets, "comparison_units": units,
            "required_comparability_dimensions": dimensions,
            "instructions": [
                "Open every listed original-resolution image together; do not use contact sheets for peak or intensity judgments.",
                "Compare the spectra jointly and produce a sample/series-by-band table; do not merely restate each spectrum independently.",
                "Assess every comparability dimension before interpreting differences. Keep unknown or mismatched dimensions explicit.",
                "Report peak positions as approximate wavenumber ranges when ticks permit, with shift direction and bounded magnitude; never invent point precision.",
                "Compare relative intensity only when axis basis, baseline, normalization, scaling, offsets and acquisition conditions permit.",
                "Report relative band-area trends qualitatively/semi-quantitatively only; do not digitize curves, integrate pixels or claim absolute areas.",
                "Identify emerging, disappearing, broadened, narrowed, split, merged and stable bands, mapped to their samples/series.",
                "Give plausible functional-group/bond assignments, confidence and alternative assignments; label these as interpretations.",
                "Separate Observed, Interpreted and Hypothesized; a single band does not prove a unique species or mechanism.",
                "Consider baseline/background, normalization, resolution, signal-to-noise, sample loading, particle size, matrix overlap, water content, fluorescence and acquisition changes where relevant.",
                "Name independent evidence that could corroborate or contradict an assignment without assuming those measurements exist.",
                "Do not infer sample names, treatment conditions or missing metadata. This payload excludes captions and report narrative.",
                "This is visual qualitative/semi-quantitative analysis, not raw-curve digitization."
            ],
            "output_contract": {
                "comparison_status": "COMPARABLE | CONDITIONALLY_COMPARABLE | NOT_COMPARABLE | NOT_ASSESSABLE",
                "minimum_output": ["compared_units", "comparability_dimensions", "band_comparisons",
                                  "overall_synthesis", "cross_validation_targets", "uncertainty_note"],
                "band_comparison_fields": ["band_id", "unit_ids", "observed_difference",
                    "peak_position_estimates_cm1", "shift_direction", "shift_magnitude_cm1_range",
                    "relative_intensity_trend", "relative_peak_area_trend", "band_presence_change",
                    "assignment_candidates", "epistemic_status", "alternative_explanations"]
            }
        })
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    output = (args.output_dir or workspace / "cache" / "spectral_comparisons").expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    tasks = build_comparison_tasks(bundle)
    for old in output.glob("SPC*_task.json"):
        old.unlink()
    for task in tasks:
        atomic_write_json(output / f"{task['task_id']}_task.json", task)
    index = {
        "status": "TASKS_READY" if tasks else "NO_COMPARABLE_SPECTRAL_GROUPS_DETECTED",
        "task_count": len(tasks),
        "tasks": [{"task_id": t["task_id"], "modality": t["modality"],
                   "comparison_unit_count": len(t["comparison_units"]), "asset_count": len(t["assets"]),
                   "task_file": f"{t['task_id']}_task.json"} for t in tasks],
        "reason": None if tasks else (
            "No same-modality group with at least two independent spectra/series was identified. "
            "Review modality detection, Region/Panel links, first-pass cards and sample/series mapping; "
            "do not infer that the source contains no spectra."
        )
    }
    atomic_write_json(output / "index.json", index)
    print(json.dumps(index, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
