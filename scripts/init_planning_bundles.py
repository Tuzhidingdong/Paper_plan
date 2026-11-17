#!/usr/bin/env python3
"""Create missing planning HEAD bundles without overwriting existing work."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from era_core import atomic_write_json, workspace_paths


DEFAULTS = {
    "literature_bundle.json": {
        "schema_version": 1,
        "search_scope": {},
        "literature_records": {},
        "literature_claims": {},
        "research_gaps": {},
        "search_log_refs": [],
    },
    "routes_bundle.json": {
        "schema_version": 1,
        "routes": {},
        "recommended_route_id": None,
        "recommendation_rationale": None,
        "approval_A": {"status": "PENDING_HUMAN_REVIEW", "decision": None},
    },
    "framework_bundle.json": {
        "schema_version": 1,
        "claims": {},
        "data_slots": {},
        "data_units": {},
        "tasks": {},
        "sections": {},
        "figure_plan": {},
        "recommended_route_id": None,
        "introduction_outline": [],
        "introduction_draft": None,
        "approval_B": {"status": "PENDING_HUMAN_REVIEW", "decision": None},
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    paths = workspace_paths(workspace)
    paths["state"].mkdir(parents=True, exist_ok=True)
    created, preserved = [], []
    for name, payload in DEFAULTS.items():
        target = paths["state"] / name
        if target.exists():
            preserved.append(name)
            continue
        atomic_write_json(target, payload)
        created.append(name)

    logs = paths["state"] / "history" / "literature_search_log.jsonl"
    logs.parent.mkdir(parents=True, exist_ok=True)
    if not logs.exists():
        logs.write_text("", encoding="utf-8")
    deliverables = workspace / "deliverables"
    deliverables.mkdir(parents=True, exist_ok=True)

    manifest_path = paths["manifest"]
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.setdefault("bundles", {}).update({
            "literature_bundle.json": "HEAD",
            "routes_bundle.json": "HEAD",
            "framework_bundle.json": "HEAD",
        })
        manifest["planning_initialized"] = True
        atomic_write_json(manifest_path, manifest)
    print(json.dumps({
        "created": created,
        "preserved_existing": preserved,
        "literature_search_log": str(logs),
        "deliverables_dir": str(deliverables),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
