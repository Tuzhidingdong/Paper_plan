#!/usr/bin/env python3
"""Validate and persist a model-produced joint spectral comparison record."""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from era_core import atomic_write_json, load_evidence_bundle, workspace_paths

VALID_COMPARISON_STATUS = {"COMPLETE", "PARTIAL", "NOT_COMPARABLE"}
VALID_COMPARABILITY = {"COMPARABLE", "PARTIALLY_COMPARABLE", "NOT_COMPARABLE", "UNKNOWN"}
VALID_EPISTEMIC = {"Observed", "Interpreted", "Hypothesized"}

def validate_record(bundle: dict[str, Any], request: dict[str, Any], record: dict[str, Any]) -> None:
    expected_id = request.get("comparison_id")
    if record.get("comparison_id") != expected_id:
        raise ValueError("record comparison_id does not match the prepared request")
    if record.get("comparison_mode") != "SPECTRAL_CROSS_SAMPLE":
        raise ValueError("comparison_mode must be SPECTRAL_CROSS_SAMPLE")
    expected_ids = set(request.get("result_ids", []))
    supplied_ids = set(record.get("result_ids", []))
    if supplied_ids != expected_ids or len(record.get("result_ids", [])) != len(expected_ids):
        raise ValueError("record result_ids must match the prepared comparison set exactly")
    if record.get("technique") != request.get("technique"):
        raise ValueError("record technique does not match the prepared request")
    if record.get("comparison_status") not in VALID_COMPARISON_STATUS:
        raise ValueError("comparison_status must be COMPLETE, PARTIAL or NOT_COMPARABLE")
    if not str(record.get("summary") or "").strip():
        raise ValueError("A comparative summary is required")
    comparability = record.get("comparability_assessment")
    if not isinstance(comparability, dict) or comparability.get("status") not in VALID_COMPARABILITY:
        raise ValueError("comparability_assessment.status is missing or invalid")
    if not str(comparability.get("conclusion") or "").strip():
        raise ValueError("comparability_assessment.conclusion is required")
    if not isinstance(comparability.get("assessed_dimensions"), list):
        raise ValueError("comparability_assessment.assessed_dimensions must be a list")
    if record["comparison_status"] in {"COMPLETE", "PARTIAL"}:
        direct = record.get("direct_observations")
        if not isinstance(direct, list) or not direct:
            raise ValueError("A completed/partial comparison requires direct_observations")
    elif comparability.get("status") not in {"NOT_COMPARABLE", "UNKNOWN"}:
        raise ValueError("NOT_COMPARABLE record must explain the non-comparable/unknown status")

    valid_change_types = {
        "SHIFT", "RELATIVE_INTENSITY", "AREA_TREND", "NEW_BAND", "DISAPPEARING_BAND",
        "SPLITTING", "MERGING", "BROADENING", "NARROWING", "SIMILARITY", "OTHER"
    }
    for index, item in enumerate(record.get("direct_observations", [])):
        if not str(item.get("description") or "").strip():
            raise ValueError(f"direct_observations[{index}] is missing description")
        if item.get("source_status", "Observed") not in VALID_EPISTEMIC:
            raise ValueError(f"direct_observations[{index}] has invalid source_status")
        refs = item.get("result_ids", [])
        if not refs or not set(refs).issubset(expected_ids):
            raise ValueError(f"direct_observations[{index}] must cite compared Result Units")
    for index, item in enumerate(record.get("band_comparisons", [])):
        if item.get("change_type") not in valid_change_types:
            raise ValueError(f"band_comparisons[{index}] has invalid change_type")
        if not str(item.get("observed_change") or "").strip():
            raise ValueError(f"band_comparisons[{index}] is missing observed_change")
        refs = item.get("result_ids", [])
        if not refs or not set(refs).issubset(expected_ids):
            raise ValueError(f"band_comparisons[{index}] must cite compared Result Units")
        for ref in item.get("evidence_refs", []):
            if ref.get("result_id") not in expected_ids:
                raise ValueError(f"band_comparisons[{index}] evidence_ref is outside the compared set")
    for index, item in enumerate(record.get("functional_group_interpretations", [])):
        if item.get("epistemic_status") not in {"Interpreted", "Hypothesized"}:
            raise ValueError(f"functional_group_interpretations[{index}] must be Interpreted or Hypothesized")
        if not str(item.get("assignment") or "").strip() or not str(item.get("rationale") or "").strip():
            raise ValueError(f"functional_group_interpretations[{index}] requires assignment and rationale")
    for sample_group in record.get("sample_groups", []):
        for sample_id in sample_group.get("sample_ids", []):
            if sample_id not in bundle.get("samples", {}):
                raise ValueError(f"sample_groups references unknown Sample Entity {sample_id}")

def register_comparison(
    bundle: dict[str, Any], request: dict[str, Any], record: dict[str, Any],
    replace_existing: bool = False,
) -> None:
    validate_record(bundle, request, record)
    comparisons = bundle.setdefault("spectral_comparisons", {})
    comparison_id = record["comparison_id"]
    if comparison_id in comparisons and not replace_existing:
        raise ValueError(f"Spectral comparison already recorded: {comparison_id}; pass --replace to revise it")
    saved = dict(record)
    saved["recorded_at"] = datetime.now(timezone.utc).isoformat()
    saved["source_sha256"] = bundle.get("source", {}).get("sha256")
    saved["request_grouping_status"] = request.get("grouping_status")
    comparisons[comparison_id] = saved

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
    register_comparison(bundle, request, record, args.replace)
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    event = {
        "event_type": "SPECTRAL_COMPARISON_RECORDED",
        "comparison_id": record["comparison_id"], "result_ids": record["result_ids"],
        "comparison_status": record["comparison_status"],
        "comparability_status": record["comparability_assessment"]["status"],
        "recorded_at": bundle["spectral_comparisons"][record["comparison_id"]]["recorded_at"],
    }
    paths["history"].mkdir(parents=True, exist_ok=True)
    with (paths["history"] / "spectral_comparisons.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
