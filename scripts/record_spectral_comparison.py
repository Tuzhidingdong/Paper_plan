#!/usr/bin/env python3
"""Validate and persist structured cross-sample Raman/IR comparison findings."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle, workspace_paths

COMPARISON = {"COMPARABLE", "CONDITIONALLY_COMPARABLE", "NOT_COMPARABLE", "NOT_ASSESSABLE"}
DIMENSION = {"MATCHED", "MISMATCHED", "UNKNOWN", "NOT_APPLICABLE"}
EPISTEMIC = {"Observed", "Interpreted", "Hypothesized"}
SHIFT = {"HIGHER_WAVENUMBER", "LOWER_WAVENUMBER", "NO_CLEAR_SHIFT", "NOT_ASSESSABLE"}
TREND = {"INCREASED", "DECREASED", "SIMILAR", "MIXED", "NOT_ASSESSABLE"}
PRESENCE = {"PRESENT_IN_ALL", "EMERGES", "DISAPPEARS", "PRESENT_IN_SUBSET", "NOT_ASSESSABLE"}


def _range(value: Any, label: str, nonnegative: bool = False) -> None:
    if value is None:
        return
    if (not isinstance(value, list) or len(value) != 2
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)
            or value[0] > value[1] or (nonnegative and value[0] < 0)):
        raise ValueError(f"{label} must be a two-number ascending range" +
                         (" with non-negative values" if nonnegative else "") + " or null")


def validate_comparison(task: dict[str, Any], card: dict[str, Any]) -> None:
    if card.get("task_id") != task.get("task_id"):
        raise ValueError("record task_id does not match the prepared task pack")
    if card.get("comparison_status") not in COMPARISON:
        raise ValueError("comparison_status is missing or invalid")
    allowed = {u["unit_id"] for u in task.get("comparison_units", [])}
    selected = card.get("compared_units")
    if not isinstance(selected, list) or len(set(selected)) < 2 or set(selected) - allowed:
        raise ValueError("compared_units must identify at least two distinct task-pack units")
    dimensions = card.get("comparability_dimensions")
    if not isinstance(dimensions, dict) or not dimensions:
        raise ValueError("comparability_dimensions must be a non-empty object")
    missing = set(task.get("required_comparability_dimensions", [])) - set(dimensions)
    if missing:
        raise ValueError("comparability_dimensions must assess every required dimension: " + ", ".join(sorted(missing)))
    for name, item in dimensions.items():
        if not isinstance(item, dict) or item.get("status") not in DIMENSION:
            raise ValueError(f"comparability dimension {name} needs a valid status")
        if item["status"] == "UNKNOWN" and not item.get("reason"):
            raise ValueError(f"unknown comparability dimension {name} needs a reason")
    if card["comparison_status"] == "COMPARABLE":
        failed = [k for k, v in dimensions.items() if v["status"] not in {"MATCHED", "NOT_APPLICABLE"}]
        if failed:
            raise ValueError("COMPARABLE requires every dimension to be MATCHED or NOT_APPLICABLE: " + ", ".join(failed))

    bands = card.get("band_comparisons")
    if not isinstance(bands, list) or not bands:
        raise ValueError("band_comparisons must contain at least one finding or explicit non-comparison finding")
    for index, band in enumerate(bands, 1):
        if not isinstance(band, dict) or not band.get("band_id") or not band.get("observed_difference"):
            raise ValueError(f"band_comparisons[{index}] needs band_id and observed_difference")
        unit_ids = band.get("unit_ids")
        if not isinstance(unit_ids, list) or len(set(unit_ids)) < 2 or set(unit_ids) - set(selected):
            raise ValueError(f"band_comparisons[{index}] must compare at least two selected unit_ids")
        if band.get("epistemic_status") not in EPISTEMIC or band.get("shift_direction") not in SHIFT:
            raise ValueError(f"band_comparisons[{index}] has invalid epistemic_status or shift_direction")
        _range(band.get("shift_magnitude_cm1_range"), f"band_comparisons[{index}].shift_magnitude_cm1_range", True)
        for estimate in band.get("peak_position_estimates_cm1", []) or []:
            if not isinstance(estimate, dict) or estimate.get("unit_id") not in unit_ids:
                raise ValueError(f"band_comparisons[{index}] has an estimate for an unlinked unit")
            _range(estimate.get("range"), f"band_comparisons[{index}].peak_position_estimates_cm1.range")
            if estimate.get("range") is None:
                raise ValueError("peak position estimates must use ranges, not unsupported exact point values")
        if band.get("relative_intensity_trend") not in TREND:
            raise ValueError(f"band_comparisons[{index}] has invalid relative_intensity_trend")
        if band.get("relative_peak_area_trend") not in TREND:
            raise ValueError(f"band_comparisons[{index}] has invalid relative_peak_area_trend")
        if band.get("band_presence_change") not in PRESENCE:
            raise ValueError(f"band_comparisons[{index}] has invalid band_presence_change")
        for key in ("assignment_candidates", "alternative_explanations"):
            if not isinstance(band.get(key, []), list):
                raise ValueError(f"band_comparisons[{index}].{key} must be a list")
    for key in ("overall_synthesis", "uncertainty_note"):
        if not isinstance(card.get(key), str) or not card[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    if not isinstance(card.get("cross_validation_targets", []), list):
        raise ValueError("cross_validation_targets must be a list")


def register_comparison(bundle: dict[str, Any], task: dict[str, Any], card: dict[str, Any]) -> dict[str, Any]:
    validate_comparison(task, card)
    records = bundle.setdefault("spectral_comparisons", {})
    task_id = task["task_id"]
    if task_id in records:
        raise ValueError(f"Spectral comparison already recorded for {task_id}")
    saved = dict(card)
    saved.update({
        "modality": task.get("modality"),
        "measurement_group": task.get("measurement_group"),
        "source_sha256": task.get("source", {}).get("sha256"),
        "source_entities": [a["entity_id"] for a in task.get("assets", [])],
        "source_result_ids": sorted({u.get("result_id") for u in task.get("comparison_units", []) if u.get("result_id")}),
        "compared_unit_context": [
            {k: u.get(k) for k in ("unit_id", "result_id", "entity_ids", "samples", "series",
                                    "condition_summary", "measurement_group", "technique",
                                    "data_type", "visual_legibility", "quantitative_permission")}
            for u in task.get("comparison_units", []) if u.get("unit_id") in card["compared_units"]
        ],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    })
    records[task_id] = saved
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--task-json", type=Path, required=True)
    parser.add_argument("--record-json", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    task = json.loads(args.task_json.read_text(encoding="utf-8"))
    card = json.loads(args.record_json.read_text(encoding="utf-8"))
    bundle = load_evidence_bundle(workspace)
    saved = register_comparison(bundle, task, card)
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    history = paths["history"]
    history.mkdir(parents=True, exist_ok=True)
    event = {
        "event_type": "SPECTRAL_COMPARISON_RECORDED", "task_id": task["task_id"],
        "modality": saved["modality"], "comparison_status": saved["comparison_status"],
        "compared_unit_count": len(saved["compared_units"]),
        "band_comparison_count": len(saved["band_comparisons"]), "recorded_at": saved["recorded_at"]
    }
    with (history / "spectral_comparisons.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    output = workspace / "cache" / "spectral_comparisons"
    output.mkdir(parents=True, exist_ok=True)
    atomic_write_json(output / f"{task['task_id']}_recorded.json", saved)
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
