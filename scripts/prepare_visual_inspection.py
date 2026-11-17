#!/usr/bin/env python3
"""Prepare an image-only, caption-blind inspection request for a known Region or Panel."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, load_evidence_bundle


def build_payload(bundle: dict[str, Any], entity_id: str, mode: str, reason: str | None = None) -> dict[str, Any]:
    if entity_id in bundle.get("regions", {}):
        entity = bundle["regions"][entity_id]
        entity_type = "region"
        parent_region_id = entity_id
    elif entity_id in bundle.get("panels", {}):
        entity = bundle["panels"][entity_id]
        entity_type = "panel"
        parent_region_id = entity["parent_region_id"]
    else:
        raise KeyError(f"Unknown Python-issued Region/Panel ID: {entity_id}")

    history = bundle.get("visual_inspections", {}).get(entity_id, {})
    if mode == "initial" and history.get("initial") is not None:
        raise ValueError(f"Initial visual inspection already exists for {entity_id}")
    if mode == "reinspection":
        if history.get("initial") is None:
            raise ValueError("Reinspection requires a recorded initial inspection")
        if history.get("locked") or len(history.get("reinspections", [])) >= 1:
            raise ValueError(f"Automated reinspection limit reached for {entity_id}")
        if not reason or not reason.strip():
            raise ValueError("A targeted reinspection reason is required")

    parent_region = bundle["regions"][parent_region_id]
    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "parent_region_id": parent_region_id,
        "page_number": entity.get("page_number", parent_region["page_number"]),
        "image_path": entity["image_path"],
        "pixel_sha256": entity.get("pixel_sha256") or parent_region.get("pixel_sha256"),
        "inspection_mode": "CAPTION_BLIND",
        "inspection_attempt": mode,
        "reinspection_reason": reason,
        "caption_text": None,
        "report_narrative": None,
        "instructions": [
            "Inspect only the supplied image file. No external caption or report narrative is included.",
            "Do not use surrounding PDF text to interpret the first-pass image.",
            "Keep each panel, axis, unit, tick, legend and series association independent.",
            "Record visibility using FOUND, NOT_SHOWN, NOT_LEGIBLE, UNCERTAIN or NOT_APPLICABLE.",
            "Separate direct visual observations from interpretations and hypotheses.",
            "Do not report exact numeric values unless the image itself is legible and the evidence policy permits them.",
            "If a descriptive caption appears embedded inside the supplied crop, do not treat it as visual evidence; request a tighter crop or mark separation unresolved."
        ],
        "crop_review_warning": (
            "Caption separation has not been independently confirmed. Check whether descriptive caption text is embedded inside the image crop."
            if entity.get("caption_separation_status", "UNVERIFIED") != "CONFIRMED"
            else None
        )
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--entity-id", required=True, help="Python-issued Region or Panel ID")
    parser.add_argument("--mode", choices=["initial", "reinspection"], default="initial")
    parser.add_argument("--reason", help="Required reason for the one allowed reinspection")
    args = parser.parse_args()

    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    payload = build_payload(bundle, args.entity_id, args.mode, args.reason)
    output_dir = workspace / "cache" / "visual_evidence"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{args.entity_id}_{args.mode}.json"
    atomic_write_json(output, payload)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
