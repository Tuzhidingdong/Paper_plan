#!/usr/bin/env python3
"""Persist one selected Result Unit after Python ID and external-source verification."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_json, workspace_paths
from external_evidence import validate_external_source_ref


def upsert_result_unit(workspace: Path, entity: dict[str, Any], reason: str) -> dict[str, Any]:
    workspace = workspace.expanduser().resolve()
    result_id = entity.get("result_id")
    if not isinstance(result_id, str) or not result_id.startswith("R"):
        raise ValueError("Result Unit must contain a Python-issued result_id beginning with R")
    paths = workspace_paths(workspace)
    registry = load_json(paths["registry"], default={})
    allocation = registry.get("entities", {}).get(result_id)
    if not allocation or allocation.get("entity_type") != "result_slot":
        raise ValueError(f"{result_id} is not a Python-issued result_slot in id_registry.json")
    reserved = allocation.get("metadata", {})
    for field in ("region_ids", "data_type", "data_origin", "visual_legibility",
                  "quantitative_permission", "epistemic_status", "measurement_context", "observations"):
        if field not in entity:
            raise ValueError(f"Result Unit is missing required field {field}")
    evidence_source = entity.get("evidence_source", "PDF_REPORT")
    if evidence_source not in {"PDF_REPORT", "STRUCTURED_ANALYSIS", "MIXED"}:
        raise ValueError("evidence_source must be PDF_REPORT, STRUCTURED_ANALYSIS or MIXED")
    bundle = load_json(paths["bundle"])
    region_ids = entity.get("region_ids", [])
    if evidence_source in {"PDF_REPORT", "MIXED"}:
        reserved_region = reserved.get("parent_region_id")
        if reserved_region and reserved_region not in region_ids:
            raise ValueError(f"{result_id} was reserved for PDF Region {reserved_region}; the Result Unit must retain that anchor")
        if not region_ids:
            raise ValueError(f"{evidence_source} Result Units require a real PDF Region")
        for region_id in region_ids:
            if region_id not in bundle.get("regions", {}):
                raise ValueError(f"Unknown PDF Region {region_id}")
    elif region_ids:
        raise ValueError("STRUCTURED_ANALYSIS Result Units must not contain fabricated Region IDs")
    refs = entity.get("external_source_refs", [])
    if evidence_source in {"STRUCTURED_ANALYSIS", "MIXED"} and not refs:
        raise ValueError(f"{evidence_source} Result Units require external_source_refs")
    reserved_ref = reserved.get("external_source_ref")
    if reserved_ref and reserved_ref not in refs:
        raise ValueError(f"{result_id} was reserved for a different external source reference")
    for ref in refs:
        errors = validate_external_source_ref(workspace, ref)
        if errors:
            raise ValueError("; ".join(errors))
    if evidence_source == "STRUCTURED_ANALYSIS":
        if entity.get("data_origin") != "Structured_Analysis":
            raise ValueError("STRUCTURED_ANALYSIS requires data_origin Structured_Analysis")
        if entity.get("visual_legibility") != "NOT_APPLICABLE":
            raise ValueError("Structured-only evidence must set visual_legibility NOT_APPLICABLE")
        if entity.get("is_visual_estimate", False):
            raise ValueError("Structured-only evidence cannot be marked as a visual estimate")
    collection = bundle.setdefault("result_units", {})
    old = collection.get(result_id)
    if old is not None and old != entity:
        raise ValueError(f"{result_id} already exists with different content; refusing silent replacement")
    collection[result_id] = entity
    previous = int(bundle.get("workspace_revision_number", 0))
    manifest = load_json(paths["manifest"], default={}) if paths["manifest"].exists() else {}
    previous = max(previous, int(manifest.get("workspace_revision_number", 0)))
    revision = previous if old == entity else previous + 1
    bundle["workspace_revision_number"] = revision
    atomic_write_json(paths["bundle"], bundle)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bundle": "evidence_bundle.json", "kind": "result-unit", "entity_id": result_id,
        "operation": "UPSERT" if old is not None else "CREATE",
        "base_revision": previous, "revision": revision,
        "changed_fields": sorted(entity if old is None else {
            key for key in set(old) | set(entity) if old.get(key) != entity.get(key)
        }),
        "reason": reason,
    }
    history = paths["history"] / "evidence_entity_history.jsonl"
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    if paths["manifest"].exists():
        manifest["workspace_revision_number"] = revision
        manifest["last_evidence_update"] = event
        atomic_write_json(paths["manifest"], manifest)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--entity-json", type=Path, required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    entity = json.loads(args.entity_json.read_text(encoding="utf-8"))
    event = upsert_result_unit(args.workspace, entity, args.reason)
    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
