#!/usr/bin/env python3
"""Compile a task-specific, token-lean Markdown view without losing scientific caveats."""
from __future__ import annotations

import argparse
import re
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
        parts.append("  - [Image-derived estimate: state reading basis, confidence and figure-resolution limits; native data are required only for exact values or calculations the figure cannot support]")
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
    lines.append("## General cross-result scientific analyses")
    analyses = bundle.get("scientific_analyses", {})
    all_result_ids = set(bundle.get("result_units", {}))
    covered_result_ids = set()
    if analyses:
        for analysis_id, analysis in sorted(analyses.items()):
            coverage = analysis.get("coverage", [])
            covered_result_ids.update(item.get("result_id") for item in coverage if item.get("result_id"))
            lines.append(
                f"- **{analysis_id}** [{analysis.get('analysis_status', 'unknown')} | "
                f"{len(analysis.get('result_ids', []))} Result Units]"
            )
            lines.append(f"  - Scientific summary: {analysis.get('summary', 'not recorded')}")
            for observation in analysis.get("observations", []):
                lines.append(
                    f"  - Observed ({observation.get('confidence', 'unreported')}): "
                    f"{observation.get('description', '')} "
                    f"[{', '.join(observation.get('result_ids', []))}]"
                )
            for comparison in analysis.get("comparisons", []):
                lines.append(
                    f"  - Comparison: {comparison.get('question', '')} "
                    f"[{comparison.get('comparison_status', 'unknown')}]: "
                    f"{comparison.get('conclusion', '')}"
                )
                for dimension in comparison.get("dimension_assessments", []):
                    lines.append(
                        f"    - {dimension.get('dimension', 'dimension')}: "
                        f"{dimension.get('status', 'UNKNOWN')} — {dimension.get('consequence', '')}"
                    )
                for difference in comparison.get("quantitative_differences", []):
                    values = "; ".join(
                        f"{value.get('entity_or_group') or value.get('result_id')}: "
                        f"{value.get('value')} {value.get('unit', '')} "
                        f"[{value.get('source_basis', 'basis not stated')}]"
                        for value in difference.get("values", [])
                    )
                    lines.append(
                        f"    - {difference.get('measurand', 'quantity')}: {values}; "
                        f"pattern: {difference.get('direction_or_pattern', 'not stated')}; "
                        f"limit: {difference.get('interpretation_limit', 'not stated')}"
                    )
                for difference in comparison.get("qualitative_differences", []):
                    lines.append(f"    - Qualitative difference: {difference}")
                if comparison.get("limitations"):
                    lines.append(f"    - Comparison limits: {'; '.join(comparison['limitations'])}")
            for relationship in analysis.get("relationships", []):
                lines.append(
                    f"  - Relationship ({relationship.get('relationship_type', 'OTHER')}, "
                    f"{relationship.get('strength', 'unresolved')}, "
                    f"{relationship.get('causal_status', 'NOT_ESTABLISHED')}): "
                    f"{relationship.get('description', '')} "
                    f"[{', '.join(relationship.get('result_ids', []))}]"
                )
            for interpretation in analysis.get("interpretations", []):
                lines.append(
                    f"  - {interpretation.get('epistemic_status', 'Interpretation')}: "
                    f"{interpretation.get('description', '')}"
                )
                if interpretation.get("alternative_explanations"):
                    lines.append(f"    - Alternatives: {'; '.join(interpretation['alternative_explanations'])}")
            for contradiction in analysis.get("contradictions", []):
                lines.append(
                    f"  - Contradiction ({contradiction.get('resolution_status', 'UNRESOLVED')}): "
                    f"{contradiction.get('description', '')}"
                )
            if analysis.get("candidate_scientific_implications"):
                lines.append(
                    f"  - Candidate scientific implications: "
                    f"{'; '.join(analysis['candidate_scientific_implications'])}"
                )
            if analysis.get("unresolved_questions"):
                lines.append(f"  - Unresolved questions: {'; '.join(analysis['unresolved_questions'])}")
            if analysis.get("limitations"):
                lines.append(f"  - Analysis limitations: {'; '.join(analysis['limitations'])}")
            for item in coverage:
                if item.get("status") != "ANALYZED":
                    lines.append(
                        f"  - Coverage {item.get('result_id')}: {item.get('status')} — "
                        f"{item.get('reason', 'reason not recorded')}"
                    )
        uncovered = sorted(all_result_ids - covered_result_ids)
        if uncovered:
            lines.append(
                "- Result Units not yet covered by a general scientific analysis: "
                + ", ".join(uncovered)
            )
    elif all_result_ids:
        lines.append(
            "- No general cross-result scientific analysis has been recorded. "
            "Do not treat independent single-result descriptions as a completed scientific synthesis. "
            "Prepare the general analysis packs before manuscript reasoning."
        )

    lines.append("")
    lines.append("## Raman / FTIR cross-sample comparisons (legacy compatibility)")
    spectral_result_ids = [
        result_id for result_id, result in bundle.get("result_units", {}).items()
        if re.search(r"\braman\b|\bftir\b|\bft-ir\b|\binfrared\b|\bir spectroscopy\b",
                     " ".join(str(value or "") for value in (
                         result.get("data_type"),
                         result.get("measurement_context", {}).get("technique"),
                     )), re.I)
    ]
    comparisons = bundle.get("spectral_comparisons", {})
    if comparisons:
        for comparison_id, comparison in sorted(comparisons.items()):
            assessment = comparison.get("comparability_assessment", {})
            lines.append(
                f"- **{comparison_id}** [{comparison.get('technique', 'unknown')} | "
                f"{comparison.get('comparison_status', 'unknown')} | "
                f"{assessment.get('status', 'unknown')} | Result Units: "
                f"{', '.join(comparison.get('result_ids', []))}]"
            )
            lines.append(f"  - Comparative conclusion: {comparison.get('summary', 'not recorded')}")
            if assessment.get("conclusion"):
                lines.append(f"  - Comparability: {assessment['conclusion']}")
            for item in comparison.get("direct_observations", []):
                lines.append(f"  - Observed: {item.get('description', '')}")
            for item in comparison.get("band_comparisons", []):
                label = item.get("feature_id") or item.get("change_type") or "band"
                lines.append(
                    f"  - Band {label}: {item.get('observed_change', '')} "
                    f"Position: {item.get('position_comparison', 'not resolved')}; "
                    f"relative signal: {item.get('relative_signal_comparison', 'not assessed')} "
                    f"(basis: {item.get('signal_basis', 'unspecified')})."
                )
                for estimate in item.get("position_estimates", []):
                    if estimate.get("position_cm1_approx") is not None:
                        lines.append(
                            f"    - Approx. {estimate.get('sample_or_series', 'series')} band position: "
                            f"{estimate.get('position_cm1_approx')} ± {estimate.get('uncertainty_cm1_approx', 'unreported')} cm-1 "
                            f"[{estimate.get('reading_basis', 'unspecified')}; confidence {estimate.get('confidence', 'unreported')}]."
                        )
                if item.get("peak_shift_cm1_approx") is not None:
                    lines.append(
                        f"    - Approx. peak shift: {item.get('peak_shift_cm1_approx')} cm-1 "
                        f"({item.get('shift_direction', 'direction unresolved')})."
                    )
                if item.get("relative_signal_trend"):
                    lines.append(f"    - Relative signal trend: {item['relative_signal_trend']}.")
                if item.get("apparent_area_trend"):
                    lines.append(f"    - Apparent band-area trend: {item['apparent_area_trend']}.")
                if item.get("interpretation"):
                    lines.append(f"    - Interpretation: {item['interpretation']}")
                if item.get("alternative_explanations"):
                    lines.append(f"    - Alternatives: {'; '.join(item['alternative_explanations'])}")
            for item in comparison.get("functional_group_interpretations", []):
                lines.append(
                    f"  - {item.get('epistemic_status', 'Interpretation')}: "
                    f"{item.get('assignment', 'unassigned')} — {item.get('rationale', '')}"
                )
            if comparison.get("candidate_scientific_implications"):
                lines.append(f"  - Candidate implications: {'; '.join(comparison['candidate_scientific_implications'])}")
            if comparison.get("limitations"):
                lines.append(f"  - Limitations: {'; '.join(comparison['limitations'])}")
        covered_spectral_result_ids = {
            result_id for comparison in comparisons.values()
            for result_id in comparison.get("result_ids", [])
        }
        uncovered_spectral_result_ids = sorted(set(spectral_result_ids) - covered_spectral_result_ids)
        if uncovered_spectral_result_ids:
            lines.append(
                "- Spectral Result Units not yet included in a recorded comparison: "
                + ", ".join(uncovered_spectral_result_ids)
            )
    elif spectral_result_ids:
        lines.append(
            "- Spectral Result Units were identified, but no joint cross-sample comparison has been recorded. "
            "Do not treat independent single-spectrum inspections as a completed comparison; prepare and record "
            "a joint task with scripts/prepare_spectral_comparison.py."
        )
        lines.append(f"  - Spectral Result Units: {', '.join(sorted(spectral_result_ids))}")
    else:
        lines.append("- No Raman/FTIR Result Units are currently registered.")

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
