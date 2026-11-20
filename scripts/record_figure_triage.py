#!/usr/bin/env python3
"""Record an explicit scientific/non-scientific disposition for every vector figure candidate."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle, workspace_paths

VALID_DISPOSITIONS = {"INCLUDE_AS_SCIENTIFIC_FIGURE", "EXCLUDE_NOT_SCIENTIFIC_FIGURE"}


def record_figure_triage(bundle: dict[str, Any], decisions: list[dict[str, Any]]) -> None:
    candidates = bundle.setdefault("figure_candidates", {})
    results = bundle.get("result_units", {})
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("decisions must be a non-empty JSON list")
    seen: set[str] = set()
    for index, decision in enumerate(decisions):
        candidate_id = str(decision.get("candidate_id") or "")
        if not candidate_id or candidate_id in seen:
            raise ValueError(f"decisions[{index}] requires a unique candidate_id")
        seen.add(candidate_id)
        candidate = candidates.get(candidate_id)
        if candidate is None:
            raise ValueError(f"Unknown source figure candidate: {candidate_id}")
        if candidate.get("extraction_status") != "EXTRACTED":
            raise ValueError(f"{candidate_id}: candidate asset is not successfully extracted")
        disposition = decision.get("disposition")
        if disposition not in VALID_DISPOSITIONS:
            raise ValueError(f"{candidate_id}: invalid disposition {disposition!r}")
        reason = str(decision.get("reason") or "").strip()
        if disposition == "EXCLUDE_NOT_SCIENTIFIC_FIGURE":
            if not reason:
                raise ValueError(f"{candidate_id}: an exclusion reason is required")
            result_ids: list[str] = []
        else:
            raw_ids = decision.get("result_ids")
            if not isinstance(raw_ids, list) or not raw_ids:
                raise ValueError(f"{candidate_id}: inclusion requires one or more linked Result Unit IDs")
            result_ids = [str(item) for item in raw_ids]
            if len(set(result_ids)) != len(result_ids):
                raise ValueError(f"{candidate_id}: result_ids must be unique")
            region_id = candidate.get("region_id")
            for result_id in result_ids:
                result = results.get(result_id)
                if result is None:
                    raise ValueError(f"{candidate_id}: unknown Result Unit {result_id}")
                linked_regions = set(result.get("region_ids", []) or [])
                linked_panels = set(result.get("panel_ids", []) or [])
                panel_parent_regions = {
                    bundle.get("panels", {}).get(panel_id, {}).get("parent_region_id")
                    for panel_id in linked_panels
                }
                if region_id not in linked_regions and region_id not in panel_parent_regions:
                    raise ValueError(
                        f"{candidate_id}: Region {region_id} is not linked to Result Unit {result_id}"
                    )
        candidate.update({
            "triage_status": "REVIEWED",
            "disposition": disposition,
            "result_ids": result_ids,
            "reason": reason or None,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        })


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--decisions-json", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    decisions = json.loads(args.decisions_json.read_text(encoding="utf-8"))
    bundle = load_evidence_bundle(workspace)
    record_figure_triage(bundle, decisions)
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    print(json.dumps({
        "status": "RECORDED",
        "decisions_recorded": len(decisions),
        "pending_candidates": sum(
            1 for item in bundle.get("figure_candidates", {}).values()
            if item.get("triage_status") != "REVIEWED"
        ),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
