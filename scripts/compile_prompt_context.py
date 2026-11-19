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



def compact_spectral_comparison(task_id: str, item: dict[str, Any]) -> str:
    lines = [
        f"### {task_id} [{item.get('modality', 'unknown')} | {item.get('comparison_status', 'UNASSESSED')} | "
        f"measurement group: {item.get('measurement_group') or 'unspecified'}]",
        f"- Source entities: {', '.join(item.get('source_entities', [])) or 'not recorded'}",
        f"- Source Result Units: {', '.join(item.get('source_result_ids', [])) or 'not mapped'}",
    ]
    for unit in item.get("compared_unit_context", []):
        samples = ", ".join(
            f"{sample.get('label', 'unmapped')} ({sample.get('sample_id') or 'no ID'}; {sample.get('identity_status', 'UNKNOWN')})"
            for sample in unit.get("samples", [])
        ) or "unmapped"
        lines.append(
            f"- Compared unit **{unit.get('unit_id')}**: samples={samples}; "
            f"conditions={unit.get('condition_summary') or 'UNKNOWN'}; "
            f"visual permission={unit.get('quantitative_permission', 'None')}"
        )
    lines.append("- Comparability dimensions:")
    for name, dimension in item.get("comparability_dimensions", {}).items():
        lines.append(f"  - {name.replace('_', ' ')}: {dimension.get('status', 'UNKNOWN')} — {dimension.get('reason', '')}")
    lines.append("- Cross-sample band comparisons:")
    for band in item.get("band_comparisons", []):
        assignments = "; ".join(
            f"{candidate.get('assignment', '')} ({candidate.get('confidence', 'unspecified confidence')})"
            for candidate in band.get("assignment_candidates", [])
        ) or "no assignment proposed"
        lines.append(
            f"  - **{band.get('band_id')}** [{', '.join(band.get('unit_ids', []))}]: "
            f"{band.get('observed_difference', '')}; shift={band.get('shift_direction', 'NOT_ASSESSABLE')} "
            f"{band.get('shift_magnitude_cm1_range')}; relative intensity={band.get('relative_intensity_trend', 'NOT_ASSESSABLE')}; "
            f"relative band-area trend={band.get('relative_peak_area_trend', 'NOT_ASSESSABLE')}; "
            f"presence={band.get('band_presence_change', 'NOT_ASSESSABLE')}; assignments={assignments}; "
            f"epistemic={band.get('epistemic_status', 'UNSPECIFIED')}"
        )
        if band.get("alternative_explanations"):
            lines.append(f"    - Alternative explanations: {'; '.join(band['alternative_explanations'])}")
    lines.append(f"- Overall synthesis: {item.get('overall_synthesis', '')}")
    if item.get("cross_validation_targets"):
        lines.append(f"- Cross-validation targets: {'; '.join(item['cross_validation_targets'])}")
    lines.append(f"- Uncertainty: {item.get('uncertainty_note', 'not recorded')}")
    lines.append("- Interpretation boundary: visual/semi-quantitative comparison only; no curve digitization or absolute peak-area claim.")
    return "\n".join(lines)

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
    lines.append("## Cross-sample Raman / IR comparisons")
    spectral = bundle.get("spectral_comparisons", {})
    if spectral:
        for task_id, comparison in sorted(spectral.items()):
            lines.append(compact_spectral_comparison(task_id, comparison))
            lines.append("")
    else:
        lines.append("- No structured spectral comparison has been recorded. Do not treat this as evidence that no spectra exist.")
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
