#!/usr/bin/env python3
"""Verify the pinned Data_analysis Schema snapshot and detect candidate producer drift."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC_RECORD = ROOT / "docs" / "DATA_ANALYSIS_EVIDENCE_CONTRACT_SYNC.json"

def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, help="Optional newer producer Schema file; a different hash means the consumer snapshot is stale.")
    args = parser.parse_args()
    try:
        record = json.loads(SYNC_RECORD.read_text(encoding="utf-8"))
        expected = record["producer_schema_sha256"]
        snapshot = ROOT / record["consumer_snapshot_path"]
        actual = file_sha256(snapshot)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read pinned Schema synchronization record: {exc}", file=sys.stderr)
        return 2
    if actual != expected or record.get("consumer_snapshot_sha256") != expected:
        print(f"ERROR: consumer Schema snapshot hash mismatch: expected {expected}, got {actual}", file=sys.stderr)
        return 1
    print(f"PASS: pinned consumer Schema snapshot SHA-256 {actual}")
    if args.candidate:
        try:
            candidate_hash = file_sha256(args.candidate)
        except OSError as exc:
            print(f"ERROR: cannot read candidate producer Schema: {exc}", file=sys.stderr)
            return 2
        if candidate_hash != expected:
            print(f"STALE: candidate production schema differs from the pinned consumer snapshot (pinned={expected}, candidate={candidate_hash})")
            return 1
        print("PASS: candidate production Schema is byte-identical to the pinned snapshot")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
