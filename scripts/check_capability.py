#!/usr/bin/env python3
"""Fail closed when the active model is not qualified for a high-risk ERA stage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from era_core import atomic_write_json, workspace_paths


REQUIREMENTS = {
    "visual_inspection": {"native_multimodal": "yes", "high_resolution_image_input": "yes"},
    "artifact_audit": {"scientific_reasoning": "yes"},
    "literature_screening": {"structured_json_output": "yes", "web_search_access": "yes"},
    "route_synthesis": {"scientific_reasoning": "yes", "long_context_consistency": "yes"},
    "framework_design": {"structured_json_output": "yes", "long_context_consistency": "yes"},
    "academic_writing": {"structured_json_output": "yes", "long_context_consistency": "yes"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--task", choices=sorted(REQUIREMENTS), required=True)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    profile_path = workspace_paths(workspace)["state"] / "capability_profile.json"
    errors = []
    profile = None
    if not profile_path.is_file():
        errors.append("No capability profile has been recorded for the active model.")
    else:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    required = REQUIREMENTS[args.task]
    missing = {}
    if profile is not None:
        capabilities = profile.get("capabilities", {})
        for key, expected in required.items():
            if capabilities.get(key, "unknown") != expected:
                missing[key] = {"required": expected, "recorded": capabilities.get(key, "unknown")}
        if not profile.get("provider") or not profile.get("model_id") or not profile.get("model_version"):
            errors.append("Provider, exact model ID and model version are required.")
        if not profile.get("evidence_basis"):
            errors.append("Capability evidence_basis must be recorded.")
    status = "PASS" if profile is not None and not missing and not errors else "BLOCKED_BY_CAPABILITY"
    report = {
        "status": status,
        "task": args.task,
        "model": None if profile is None else {
            "provider": profile.get("provider"),
            "model_id": profile.get("model_id"),
            "model_version": profile.get("model_version"),
        },
        "missing_or_unqualified": missing,
        "errors": errors,
        "note": "Capability records are operator-attested; this check does not benchmark or independently prove model performance.",
    }
    out = workspace_paths(workspace)["state"] / f"capability_{args.task}.json"
    atomic_write_json(out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
