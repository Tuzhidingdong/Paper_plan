#!/usr/bin/env python3
"""Allocate Python-owned IDs for observed sample aliases and reserved evidence slots."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from era_core import atomic_write_json, load_evidence_bundle, register_anchor, register_named_sample, workspace_paths
from external_evidence import validate_external_source_ref


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    sub = parser.add_subparsers(dest="kind", required=True)

    sample = sub.add_parser("sample", help="Register an explicitly observed sample alias")
    sample.add_argument("--alias", required=True)
    sample.add_argument("--source-ref", required=True)
    sample.add_argument("--prep-json", type=Path)
    sample.add_argument("--batch-note")

    result = sub.add_parser("result-slot", help="Reserve a Result Unit ID for a PDF Region or imported structured source")
    source_group = result.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--parent-region-id")
    source_group.add_argument("--external-source-ref-json", type=Path)
    result.add_argument("--slot-index", type=int, required=True)

    finding = sub.add_parser("finding-slot", help="Reserve a Finding ID before writing a finding card")
    finding.add_argument("--slot-index", type=int, required=True)
    args = parser.parse_args()

    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    if args.kind == "sample":
        prep = json.loads(args.prep_json.read_text(encoding="utf-8")) if args.prep_json else {}
        metadata = {"alias": args.alias, "source_ref": args.source_ref, "prep_conditions": prep, "batch_note": args.batch_note}
        sample_id = register_named_sample(workspace, args.alias, args.source_ref, metadata)
        existing = bundle["samples"].get(sample_id, {
            "sample_id": sample_id, "aliases": [], "prep_conditions": {}, "batch_note": None,
            "identity_status": "PROBABLE"
        })
        if not any(item.get("alias") == args.alias and item.get("source_ref") == args.source_ref for item in existing["aliases"]):
            existing["aliases"].append({"alias": args.alias, "source_ref": args.source_ref})
        existing["prep_conditions"].update(prep)
        if args.batch_note:
            existing["batch_note"] = args.batch_note
        bundle["samples"][sample_id] = existing
        atomic_write_json(workspace_paths(workspace)["bundle"], bundle)
        print(json.dumps({"sample_id": sample_id, "status": "PROBABLE"}, ensure_ascii=False))
        return 0

    if args.slot_index < 1:
        parser.error("--slot-index must be >= 1")
    if args.kind == "result-slot":
        prefix, entity_type = "R", "result_slot"
        if args.parent_region_id:
            if args.parent_region_id not in bundle["regions"]:
                parser.error(f"Unknown parent region: {args.parent_region_id}")
            anchor_key = f"result-slot:{args.parent_region_id}:{args.slot_index:03d}"
            metadata = {"parent_region_id": args.parent_region_id, "slot_index": args.slot_index, "status": "RESERVED"}
        else:
            try:
                external_ref = json.loads(args.external_source_ref_json.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                parser.error(f"Cannot read external source reference JSON: {exc}")
            ref_errors = validate_external_source_ref(workspace, external_ref)
            if ref_errors:
                parser.error("; ".join(ref_errors))
            import hashlib
            canonical = json.dumps(external_ref, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            anchor_key = f"structured-result:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:24]}:{args.slot_index:03d}"
            metadata = {"external_source_ref": external_ref, "slot_index": args.slot_index, "status": "RESERVED"}
    else:
        prefix, entity_type = "F", "finding_slot"
        anchor_key = f"finding-slot:{args.slot_index:03d}"
        metadata = {"slot_index": args.slot_index, "status": "RESERVED"}
    entity_id = register_anchor(workspace, prefix, anchor_key, entity_type, metadata)
    print(json.dumps({"entity_id": entity_id, "entity_type": entity_type, "status": "RESERVED"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
