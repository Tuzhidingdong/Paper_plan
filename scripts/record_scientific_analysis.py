#!/usr/bin/env python3
"""Validate and persist a general scientific analysis record against its prepared pack."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle, parse_numeric_scalar, workspace_paths

VALID_ANALYSIS_STATUS = {"COMPLETE", "PARTIAL", "NOT_ASSESSABLE"}
VALID_COVERAGE = {"ANALYZED", "NO_COMPARISON_APPLICABLE", "NOT_ASSESSABLE"}
VALID_COMPARISON = {"COMPARABLE", "PARTIALLY_COMPARABLE", "NOT_COMPARABLE", "NOT_APPLICABLE"}
VALID_DIMENSION = {"MATCHED", "MISMATCHED", "UNKNOWN", "NOT_APPLICABLE"}


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


def validate_record(
    bundle: dict[str, Any],
    request: dict[str, Any],
    record: dict[str, Any],
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

    for item in coverage:
        if item.get("status") == "ANALYZED":
            refs = set(item.get("observation_ids", []))
            if not refs or not refs.issubset(observation_ids):
                raise ValueError(f"{item['result_id']}: ANALYZED coverage must cite at least one recorded observation")
            if any(item["result_id"] not in observation_result_map.get(obs_id, set()) for obs_id in refs):
                raise ValueError(f"{item['result_id']}: coverage observation does not cite this Result Unit")

    for index, item in enumerate(record.get("comparisons", [])):
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


def register_analysis(
    bundle: dict[str, Any],
    request: dict[str, Any],
    record: dict[str, Any],
    replace_existing: bool = False,
) -> None:
    validate_record(bundle, request, record)
    analyses = bundle.setdefault("scientific_analyses", {})
    analysis_id = record["analysis_id"]
    if analysis_id in analyses and not replace_existing:
        raise ValueError(f"Analysis already recorded: {analysis_id}; pass --replace to revise it")
    saved = dict(record)
    saved["recorded_at"] = datetime.now(timezone.utc).isoformat()
    saved["source_sha256"] = bundle.get("source", {}).get("sha256")
    saved["request_pack_number"] = request.get("pack_number")
    saved["request_asset_count"] = request.get("asset_count")
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
    register_analysis(bundle, request, record, args.replace)
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
