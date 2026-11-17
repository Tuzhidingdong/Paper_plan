#!/usr/bin/env python3
"""Persist a caption-blind inspection card and enforce one automated reinspection."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle, workspace_paths

MAX_REINSPECTION_PER_REGION = 1
VALID_LEGIBILITY = {"High", "Medium", "Low", "Unassessable"}
VALID_ORIGIN = {"Exact_Text", "Exact_Table", "Vector_Extracted", "Visual_Estimate", "Qualitative_Observation", "Unavailable"}
VALID_PERMISSION = {"Exact_Values", "Trend_Only", "Qualitative_Only", "None"}


def register_inspection(
    bundle: dict[str, Any],
    entity_id: str,
    mode: str,
    card: dict[str, Any],
    reason: str | None = None,
) -> None:
    known = entity_id in bundle.get("regions", {}) or entity_id in bundle.get("panels", {})
    if not known:
        raise KeyError(f"Unknown Python-issued Region/Panel ID: {entity_id}")
    if card.get("inspection_mode") != "CAPTION_BLIND":
        raise ValueError("Inspection card must declare CAPTION_BLIND mode")
    if card.get("caption_text_included") is not False or card.get("report_narrative_included") is not False:
        raise ValueError("Caption-blind inspection cannot include caption or report narrative")
    if card.get("visual_legibility") not in VALID_LEGIBILITY:
        raise ValueError("Invalid or missing visual_legibility")
    if card.get("data_origin") not in VALID_ORIGIN:
        raise ValueError("Invalid or missing data_origin")
    if card.get("quantitative_permission") not in VALID_PERMISSION:
        raise ValueError("Invalid or missing quantitative_permission")
    if not isinstance(card.get("observations"), list):
        raise ValueError("observations must be a list")
    if not isinstance(card.get("instrument_checklist", {}), dict):
        raise ValueError("instrument_checklist must be an object")

    inspections = bundle.setdefault("visual_inspections", {})
    record = inspections.setdefault(entity_id, {"initial": None, "reinspections": [], "locked": False})
    saved_card = dict(card)
    saved_card["recorded_at"] = datetime.now(timezone.utc).isoformat()

    if mode == "initial":
        if record.get("initial") is not None:
            raise ValueError(f"Initial visual inspection already recorded for {entity_id}")
        record["initial"] = saved_card
        record["locked"] = False
        return

    if mode != "reinspection":
        raise ValueError("mode must be initial or reinspection")
    if record.get("initial") is None:
        raise ValueError("Reinspection requires an initial inspection")
    if not reason or not reason.strip():
        raise ValueError("Reinspection requires a specific reason")
    existing = record.setdefault("reinspections", [])
    if record.get("locked") or len(existing) >= MAX_REINSPECTION_PER_REGION:
        record["locked"] = True
        raise ValueError(f"Automated reinspection limit ({MAX_REINSPECTION_PER_REGION}) reached for {entity_id}")
    saved_card["reinspection_reason"] = reason.strip()
    existing.append(saved_card)
    record["locked"] = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--entity-id", required=True)
    parser.add_argument("--mode", choices=["initial", "reinspection"], required=True)
    parser.add_argument("--record-json", type=Path, required=True)
    parser.add_argument("--reason")
    args = parser.parse_args()

    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    card = json.loads(args.record_json.read_text(encoding="utf-8"))
    register_inspection(bundle, args.entity_id, args.mode, card, args.reason)

    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    history_dir = paths["history"]
    history_dir.mkdir(parents=True, exist_ok=True)

    inspection_entry = bundle["visual_inspections"][args.entity_id]
    recorded_card = inspection_entry["initial"] if args.mode == "initial" else inspection_entry["reinspections"][-1]
    event = {
        "event_type": "VISUAL_INSPECTION_RECORDED",
        "entity_id": args.entity_id,
        "mode": args.mode,
        "reinspection_count": len(inspection_entry["reinspections"]),
        "locked": inspection_entry["locked"],
        "recorded_at": recorded_card["recorded_at"]
    }
    with (history_dir / "visual_inspections.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
