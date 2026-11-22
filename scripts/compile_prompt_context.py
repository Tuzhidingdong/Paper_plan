#!/usr/bin/env python3
"""Compile a task-specific, token-lean Markdown view without losing scientific caveats."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from era_core import atomic_write_text, load_evidence_bundle, workspace_paths
from external_evidence import load_registry


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
    evidence_source = item.get("evidence_source", "PDF_REPORT")
    source_label = ", ".join(pages) if pages else "no PDF Region"
    parts = [
        f"- **{result_id}** [{evidence_source} | {item.get('data_type', 'unknown')} | {source_label} | {origin}/{legibility} | {permission}]",
        f"  - Samples: {', '.join(samples) if samples else 'not mapped'}",
        f"  - Observation: {observations or 'not yet recorded'}",
    ]
    for ref in item.get("external_source_refs", []):
        identity = f"{ref.get('source_system')}/{ref.get('entity_type')}:{ref.get('entity_id')}"
        parts.append(
            f"  - External provenance: package={ref.get('evidence_package_id')} | {identity} | "
            f"AnalysisRun={ref.get('analysis_run_id', 'not supplied')} | Dataset={ref.get('dataset_id', 'not supplied')} | "
            f"operation={ref.get('operation_id', 'not supplied')} | source_sha256={ref.get('source_sha256', ref.get('source_hashes', []))} | "
            f"summary_sha256={ref.get('summary_sha256')}"
        )
        if ref.get("warnings"):
            parts.append(f"  - External QC warnings: {'; '.join(ref['warnings'])}")
        if ref.get("limitations"):
            parts.append(f"  - External limitations: {'; '.join(ref['limitations'])}")
    if uncertainty:
        parts.append(f"  - Uncertainty: {uncertainty}")
    if artifact_notes:
        parts.append(f"  - Artifact audit: {artifact_notes}")
    if origin == "Visual_Estimate":
        parts.append("  - [Visual Estimate - Raw Data Required]")
    return "\n".join(parts)


def _external_entity_summary(item: dict[str, Any]) -> str:
    fields = (
        "operation_id", "row_count", "column_count", "omitted_column_count",
        "cycle_count", "complete_cycle_count", "first_complete_discharge_capacity_mAh",
        "last_complete_discharge_capacity_mAh", "capacity_retention_percent_last_vs_first",
        "coulombic_efficiency_summary_percent", "group_count", "groups", "peak_count",
        "selected_peaks", "edge_energy_eV", "edge_energy_method", "edge_step",
        "pre_edge_range_eV", "post_edge_range_eV", "point_count", "frequency_min_hz",
        "frequency_max_hz", "circuit", "fitted_parameters", "rmse_complex_ohm",
        "record_count", "matched_group_count", "unmatched_group_count", "modality_counts",
        "columns", "warnings", "limitations", "notes", "configuration",
        "link_policy", "interpretation_prompt_guidance",
    )
    compact = {}
    for field in fields:
        if field not in item:
            continue
        value = item[field]
        if field in {"groups", "selected_peaks", "columns"} and isinstance(value, list):
            compact[field] = value[:8]
            if len(value) > 8:
                compact[field + "_shown_count"] = 8
                compact[field + "_total_count"] = len(value)
        else:
            compact[field] = value
    return json.dumps(compact, ensure_ascii=False, sort_keys=True)


def compile_context(bundle: dict[str, Any], workspace: Path | None = None) -> str:
    lines = ["# ERA compact evidence context", "", "This is a task view, not the complete evidence record.",
             "Preserve every uncertainty and source limitation when reasoning.", ""]
    source = bundle.get("source")
    if isinstance(source, dict) and source:
        lines.append(f"PDF source: {source.get('file_name', 'unknown')} | pages: {source.get('page_count', 'unknown')} | SHA-256: {source.get('sha256', 'unknown')}")
    else:
        lines.append("PDF source: not supplied (structured-only workspace; no PDF metadata or Region IDs are synthesized)")
    lines.append("")
    if workspace is not None:
        registry = load_registry(workspace)
        if registry.get("packages"):
            lines.append("")
            lines.append("## Imported Data_analysis Evidence Packages")
            for package_id, record in sorted(registry["packages"].items()):
                lines.append(
                    f"### {package_id} | package SHA-256: {record.get('package_sha256')} | {record.get('status')}"
                )
                lines.append(
                    f"- Contract: {record.get('contract_id')} v{record.get('contract_version')} | imported: {record.get('imported_at')}"
                )
                package_path = workspace / record.get("package_path", "")
                if package_path.is_file():
                    try:
                        package = json.loads(package_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError):
                        package = {}
                    if package.get("question"):
                        lines.append(f"- Analysis question: {package['question']}")
                    for collection in (
                        "datasets", "battery_reports", "statistics_reports", "xrd_reports",
                        "xanes_reports", "eis_reports", "cross_modal_reports",
                    ):
                        for entity in package.get(collection, []):
                            entity_id = (
                                entity.get("dataset_id") or entity.get("analysis_run_id")
                                or entity.get("cross_modal_evidence_id", "UNKNOWN")
                            )
                            lines.append(
                                f"- {collection}/{entity_id}: {_external_entity_summary(entity)}"
                            )
                if record.get("warnings"):
                    lines.append("- Import warnings: " + "; ".join(record["warnings"]))
                if record.get("limitations"):
                    lines.append("- Import limitations: " + "; ".join(record["limitations"]))
                if record.get("unverifiable_fields"):
                    lines.append(
                        "- Not independently verifiable from the package alone: "
                        + "; ".join(record["unverifiable_fields"])
                    )
            lines.append("- Registration does not create Result Units or Claims; Agent selection and scientific review are required.")
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
    atomic_write_text(output, compile_context(bundle, workspace))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
