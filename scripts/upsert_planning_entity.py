#!/usr/bin/env python3
"""Safely upsert one Python-ID-backed planning entity and append its revision event."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_json, workspace_paths


ENTITY_MAP = {
    "literature": ("literature_bundle.json", "literature_records", "LIT", "literature_record", "literature_id"),
    "literature-claim": ("literature_bundle.json", "literature_claims", "LC", "literature_claim", "literature_claim_id"),
    "gap": ("literature_bundle.json", "research_gaps", "GAP", "research_gap", "gap_id"),
    "route": ("routes_bundle.json", "routes", "ROUTE", "research_route", "route_id"),
    "claim": ("framework_bundle.json", "claims", "C", "scientific_claim", "claim_id"),
    "data-slot": ("framework_bundle.json", "data_slots", "DS", "data_slot", "data_slot_id"),
    "data-unit": ("framework_bundle.json", "data_units", "DU", "data_unit", "data_unit_id"),
    "task": ("framework_bundle.json", "tasks", "T", "execution_task", "task_id"),
}


def upsert(workspace: Path, kind: str, entity: dict[str, Any], reason: str) -> dict[str, Any]:
    bundle_name, collection_name, prefix, expected_type, id_field = ENTITY_MAP[kind]
    entity_id = entity.get(id_field)
    if not isinstance(entity_id, str) or not entity_id.startswith(prefix):
        raise ValueError(f"Entity must contain a Python-issued {id_field} beginning with {prefix}")

    paths = workspace_paths(workspace)
    registry = load_json(paths["registry"], default={})
    registration = registry.get("entities", {}).get(entity_id)
    if not registration:
        raise ValueError(f"{entity_id} is not present in the Python ID registry")
    if registration.get("entity_type") != expected_type:
        raise ValueError(f"{entity_id} registry type is {registration.get('entity_type')!r}, expected {expected_type!r}")
    if kind == "literature":
        for snippet in entity.get("evidence_snippets", []):
            snippet_id = snippet.get("snippet_id")
            snippet_registration = registry.get("entities", {}).get(snippet_id)
            if not snippet_registration or snippet_registration.get("entity_type") != "literature_snippet":
                raise ValueError(f"{snippet_id} is not a Python-issued literature_snippet ID")
    if kind == "literature":
        for snippet in entity.get("evidence_snippets", []):
            snippet_id = snippet.get("snippet_id")
            snippet_registration = registry.get("entities", {}).get(snippet_id)
            if not snippet_registration or snippet_registration.get("entity_type") != "literature_snippet":
                raise ValueError(f"{snippet_id} is not a Python-issued literature_snippet ID")

    bundle_path = paths["state"] / bundle_name
    bundle = load_json(bundle_path)
    collection = bundle.setdefault(collection_name, {})
    old = collection.get(entity_id)
    manifest_path = paths["manifest"]
    manifest = load_json(manifest_path, default={}) if manifest_path.exists() else {}
    previous = max(
        int(bundle.get("workspace_revision_number", 0)),
        int(manifest.get("workspace_revision_number", 0)),
    )
    revision = previous + 1
    collection[entity_id] = entity
    bundle["workspace_revision_number"] = revision
    atomic_write_json(bundle_path, bundle)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bundle": bundle_name,
        "kind": kind,
        "entity_id": entity_id,
        "operation": "UPSERT" if old is not None else "CREATE",
        "base_revision": previous,
        "revision": revision,
        "changed_fields": sorted(set(entity) if old is None else {
            key for key in set(old) | set(entity) if old.get(key) != entity.get(key)
        }),
        "reason": reason,
    }
    history = paths["history"] / "planning_entity_history.jsonl"
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())

    if manifest_path.exists():
        manifest["workspace_revision_number"] = revision
        manifest["last_planning_update"] = event
        atomic_write_json(manifest_path, manifest)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--kind", choices=sorted(ENTITY_MAP), required=True)
    parser.add_argument("--entity-json", type=Path, required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    entity = json.loads(args.entity_json.read_text(encoding="utf-8"))
    result = upsert(args.workspace.expanduser().resolve(), args.kind, entity, args.reason)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
