#!/usr/bin/env python3
"""Reserve permanent IDs for literature, route, claim, Data Slot, Data Unit and task entities."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from era_core import register_anchor


KINDS = {
    "literature": ("LIT", "literature_record"),
    "literature-snippet": ("SN", "literature_snippet"),
    "literature-claim": ("LC", "literature_claim"),
    "gap": ("GAP", "research_gap"),
    "route": ("ROUTE", "research_route"),
    "claim": ("C", "scientific_claim"),
    "data-slot": ("DS", "data_slot"),
    "data-unit": ("DU", "data_unit"),
    "task": ("T", "execution_task"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("kind", choices=sorted(KINDS))
    parser.add_argument("--anchor-key", required=True, help="Stable semantic key, e.g. route:acid-conversion-mechanism")
    parser.add_argument("--parent-id", help="Optional parent entity ID")
    args = parser.parse_args()
    if not args.anchor_key.strip():
        parser.error("--anchor-key cannot be blank")
    prefix, entity_type = KINDS[args.kind]
    metadata = {"anchor_key": args.anchor_key, "parent_id": args.parent_id, "status": "RESERVED"}
    entity_id = register_anchor(args.workspace.expanduser().resolve(), prefix, args.anchor_key, entity_type, metadata)
    print(json.dumps({
        "entity_id": entity_id,
        "entity_type": entity_type,
        "anchor_key": args.anchor_key,
        "status": "RESERVED",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
