#!/usr/bin/env python3
"""Validate all persisted Paper_plan HEAD bundles against Draft 2020-12 JSON Schemas."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from era_core import atomic_write_json, workspace_paths


BUNDLES = {
    "evidence_bundle.json": "evidence_bundle.schema.json",
    "literature_bundle.json": "literature_bundle.schema.json",
    "routes_bundle.json": "routes_bundle.schema.json",
    "framework_bundle.json": "framework_bundle.schema.json",
    "manuscript_development_bundle.json": "manuscript_development_bundle.schema.json",
    "state_manifest.json": "state_manifest.schema.json",
}
OPTIONAL_BUNDLES = {
    "external_sources/registry.json": "external_source_registry.schema.json",
}


def validate_workspace(workspace: Path) -> dict:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return {
            "status": "ERROR",
            "errors": ["jsonschema is required; install dependencies from requirements.txt"],
            "validated": [],
        }
    root = Path(__file__).resolve().parents[1]
    state = workspace_paths(workspace)["state"]
    errors, validated = [], []
    for bundle_name, schema_name in {**BUNDLES, **OPTIONAL_BUNDLES}.items():
        bundle_path = state / bundle_name
        if bundle_name in OPTIONAL_BUNDLES and not bundle_path.is_file():
            continue
        schema_path = root / "schemas" / schema_name
        if not bundle_path.is_file():
            errors.append(f"Missing bundle: {bundle_path}")
            continue
        if not schema_path.is_file():
            errors.append(f"Missing schema: {schema_path}")
            continue
        try:
            payload = json.loads(bundle_path.read_text(encoding="utf-8"))
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
            bundle_errors = sorted(validator.iter_errors(payload), key=lambda e: list(map(str, e.absolute_path)))
            for error in bundle_errors:
                location = ".".join(str(part) for part in error.absolute_path) or "<root>"
                errors.append(f"{bundle_name}:{location}: {error.message}")
            validated.append(bundle_name)
        except (OSError, json.JSONDecodeError, Exception) as exc:
            errors.append(f"{bundle_name}: {exc}")
    return {"status": "ERROR" if errors else "PASS", "errors": errors, "validated": validated}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    result = validate_workspace(workspace)
    output = args.report or (workspace_paths(workspace)["state"] / "validation_schemas.json")
    atomic_write_json(output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
