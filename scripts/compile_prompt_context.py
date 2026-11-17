#!/usr/bin/env python3
"""Compile a task-specific, token-lean Markdown view without losing scientific caveats."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from era_core import atomic_write_text, load_evidence_bundle, workspace_paths


def compact_record(result_id: str, item: dict[str, Any]) -> str:
    origin = item.get("data_origin", "Unavailable")
    legibility = item.get("visual_legibility", "Unassessable")
    permission = item.get("quantitative_permission", "None")
    pages = []
    for rid in item.get("region_ids", []):
        page = item.get("_region_pages", {}).get(rid)
        pages.append(f"{rid}/p{page}" if page else rid)
    samples = []
    for association in item.get("measurement_context", {}).get("sample_associations", []):
        samples.append(f"{association.get('sample_id') or 'unmapped'}:{association.get('mapping_status', 'UNKNOWN')}")
    observations = "; ".join(
        f"{obs.get('source_status', '?')}: {obs.get('description', '')}"
        for obs in item.get("observations", [])
    )
    uncertainty = item.get("uncertainty_note")
    artifact_notes = item.get("artifact_summary")
    parts = [
        f"- **{result_id}** [{item.get('data_type', 'unknown')} | {', '.join(pages)} | {origin}/{legibility} | {permission}]",
        f"  - Samples: {', '.join(samples) if samples else 'not mapped'}",
        f"  - Observation: {observations or 'not yet recorded'}",
    ]
    if uncertainty:
        parts.append(f"  - Uncertainty: {uncertainty}")
    if artifact_notes:
        parts.append(f"  - Artifact audit: {artifact_notes}")
    if origin == "Visual_Estimate":
        parts.append("  - [Visual Estimate - Raw Data Required]")
    return "\n".join(parts)


def compile_context(bundle: dict[str, Any]) -> str:
    lines = ["# ERA compact evidence context", "", "This is a task view, not the complete evidence record.",
             "Preserve every uncertainty and source limitation when reasoning.", ""]
    source = bundle.get("source", {})
    lines.append(f"Source: {source.get('file_name', 'unknown')} | pages: {source.get('page_count', 'unknown')}")
    lines.append("")
    regions = bundle.get("regions", {})
    lines.append("## Extracted regions")
    for region_id, region in sorted(regions.items(), key=lambda pair: (pair[1].get("page_number", 0), pair[0])):
        lines.append(f"- {region_id} | page {region.get('page_number')} | {region.get('region_type')} | {region.get('image_path')}")
    lines.append("")
    lines.append("## Result Units")
    for result_id, result in sorted(bundle.get("result_units", {}).items()):
        enriched = dict(result)
        enriched["_region_pages"] = {rid: regions.get(rid, {}).get("page_number") for rid in result.get("region_ids", [])}
        lines.append(compact_record(result_id, enriched))
    lines.append("")
    lines.append("## Findings")
    for finding_id, finding in sorted(bundle.get("findings", {}).items()):
        lines.append(f"- {finding_id} [{finding.get('epistemic_status', 'unknown')}]: {finding.get('description', '')}")
        if finding.get("alternative_explanations"):
            lines.append(f"  - Alternative explanations recorded: {len(finding['alternative_explanations'])}")
        if finding.get("limitations"):
            lines.append(f"  - Limitations: {'; '.join(finding['limitations'])}")
    lines.append("")
    lines.append("## Human attention")
    if bundle.get("micro_gate", {}).get("triggered"):
        lines.append("- Micro-Gate 0.5 is triggered for a decision-relevant sample mapping. Unrelated independent results may still be analyzed.")
    for discrepancy in bundle.get("discrepancies", []):
        lines.append(f"- Visual/text discrepancy: {discrepancy.get('description', 'details in evidence bundle')}")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    bundle = load_evidence_bundle(workspace)
    output = args.output or (workspace_paths(workspace)["cache"] / "evidence_context.md")
    output = output.expanduser().resolve()
    atomic_write_text(output, compile_context(bundle))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
