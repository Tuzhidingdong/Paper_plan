#!/usr/bin/env python3
"""Record the exact host model capability profile for this workspace."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from era_core import atomic_write_json, workspace_paths


CAPABILITY_VALUES = {"yes", "no", "unknown"}
REQUIRED = {
    "native_multimodal",
    "high_resolution_image_input",
    "structured_json_output",
    "scientific_reasoning",
    "long_context_consistency",
    "web_search_access",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--profile-json", type=Path, required=True)
    args = parser.parse_args()
    profile = json.loads(args.profile_json.read_text(encoding="utf-8"))
    for key in ("provider", "model_id", "model_version", "capabilities", "evidence_basis"):
        if key not in profile:
            parser.error(f"Profile is missing required field: {key}")
    missing = REQUIRED - set(profile["capabilities"])
    if missing:
        parser.error("Profile is missing capabilities: " + ", ".join(sorted(missing)))
    invalid = {
        key: value for key, value in profile["capabilities"].items()
        if key in REQUIRED and value not in CAPABILITY_VALUES
    }
    if invalid:
        parser.error(f"Capability values must be yes/no/unknown: {invalid}")
    profile["schema_version"] = 1
    profile["profile_source"] = "workspace_operator_attested"
    profile["qualification_status"] = (
        "QUALIFIED" if all(profile["capabilities"].get(k) == "yes" for k in REQUIRED)
        else "PARTIAL_OR_UNKNOWN"
    )
    workspace = args.workspace.expanduser().resolve()
    paths = workspace_paths(workspace)
    target = paths["state"] / "capability_profile.json"
    atomic_write_json(target, profile)
    manifest_path = paths["manifest"]
    if manifest_path.exists():
        import json as json_module
        manifest = json_module.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["capability_profile"] = {
            "path": "state/capability_profile.json",
            "provider": profile["provider"],
            "model_id": profile["model_id"],
            "model_version": profile["model_version"],
            "qualification_status": profile["qualification_status"],
        }
        atomic_write_json(manifest_path, manifest)
    print(json.dumps({"path": str(target), "qualification_status": profile["qualification_status"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
