#!/usr/bin/env python3
"""Check sample entities and series-level mapping references."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle, workspace_paths

VALID = {"CONFIRMED", "PROBABLE", "AMBIGUOUS", "UNMAPPED", "NOT_APPLICABLE"}


def validate(bundle: dict[str, Any]) -> tuple[list[str], list[str], bool]:
    errors: list[str] = []
    warnings: list[str] = []
    unresolved_core_link = False
    samples = bundle.get("samples", {})
    for sample_id, sample in samples.items():
        if sample.get("sample_id") != sample_id:
            errors.append(f"Sample key/id mismatch: {sample_id}")
        if not isinstance(sample.get("aliases"), list):
            errors.append(f"{sample_id}: aliases must be a list")
        if sample.get("identity_status") not in VALID:
            errors.append(f"{sample_id}: invalid identity_status")
    for result_id, result in bundle.get("result_units", {}).items():
        context = result.get("measurement_context", {})
        for association in context.get("sample_associations", []):
            sample_id = association.get("sample_id")
            status = association.get("mapping_status")
            if sample_id and sample_id not in samples:
                errors.append(f"{result_id}: unknown sample_id {sample_id}")
            if status not in VALID:
                errors.append(f"{result_id}: invalid mapping_status")
            if status in {"AMBIGUOUS", "UNMAPPED", "PROBABLE"}:
                warnings.append(f"{result_id}: sample mapping is {status}; do not use for cross-result causal/structure-property claims")
                if association.get("core_link", False):
                    unresolved_core_link = True
    micro_gate = bundle.get("micro_gate", {})
    micro_gate["triggered"] = bool(unresolved_core_link)
    micro_gate["reason"] = "Unresolved sample association is marked as a core link" if unresolved_core_link else None
    bundle["micro_gate"] = micro_gate
    return errors, warnings, unresolved_core_link


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    errors, warnings, triggered = validate(bundle)
    report = {
        "status": "ERROR" if errors else ("NEEDS_HUMAN_CONFIRMATION" if triggered else ("WARNING" if warnings else "PASS")),
        "micro_gate_0_5": {"triggered": triggered},
        "errors": errors,
        "warnings": warnings,
    }
    paths = workspace_paths(workspace)
    atomic_write_json(paths["bundle"], bundle)
    atomic_write_json(paths["state"] / "validation_samples.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
