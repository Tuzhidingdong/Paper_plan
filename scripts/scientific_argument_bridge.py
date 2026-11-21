#!/usr/bin/env python3
"""Trace the bridge from general scientific-analysis records to manuscript Findings and Claims."""
from __future__ import annotations

from typing import Any

RECORD_SPECS = (
    ("observation", "observations", "observation_id"),
    ("comparison", "comparisons", "comparison_id"),
    ("relationship", "relationships", "relationship_id"),
    ("interpretation", "interpretations", "interpretation_id"),
    ("contradiction", "contradictions", "contradiction_id"),
    ("signal_feature", "signal_features", "feature_id"),
    ("signal_comparison", "signal_comparisons", "comparison_id"),
)
VALID_RECORD_TYPES = {item[0] for item in RECORD_SPECS}
CROSS_RESULT_CLAIM_TYPES = {"Comparative", "Associational", "Causal", "Mechanistic"}


def _as_ids(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def build_analysis_record_index(
    evidence: dict[str, Any],
) -> tuple[dict[tuple[str, str, str], set[str]], list[str]]:
    """Index explicitly identified records and the Result Units they concern.

    Historical records without stable IDs remain valid, but cannot be cited by a
    Finding until the record has an explicit ID. No scientific inference is made.
    """
    index: dict[tuple[str, str, str], set[str]] = {}
    errors: list[str] = []
    analyses = evidence.get("scientific_analyses", {})
    if not isinstance(analyses, dict):
        return index, ["scientific_analyses must be an object"]

    for analysis_id, analysis in analyses.items():
        if not isinstance(analysis, dict):
            errors.append(f"{analysis_id}: scientific analysis record must be an object")
            continue

        observation_results: dict[str, set[str]] = {}
        for record_type, collection_name, id_field in RECORD_SPECS:
            collection = analysis.get(collection_name, [])
            if not isinstance(collection, list):
                errors.append(f"{analysis_id}: {collection_name} must be a list")
                continue
            for position, record in enumerate(collection):
                if not isinstance(record, dict):
                    errors.append(f"{analysis_id}: {collection_name}[{position}] must be an object")
                    continue
                record_id = record.get(id_field)
                if not isinstance(record_id, str) or not record_id.strip():
                    # Optional for backward compatibility. New analysis requests
                    # instruct the model to create IDs for citeable outputs.
                    continue
                key = (analysis_id, record_type, record_id)
                if key in index:
                    errors.append(
                        f"{analysis_id}: duplicate {record_type} record ID {record_id}"
                    )
                    continue

                result_ids = _as_ids(record.get("result_ids"))
                if record.get("result_id"):
                    result_ids.add(record["result_id"])

                if record_type == "interpretation":
                    for observation_id in _as_ids(
                        record.get("supporting_observation_ids")
                        or record.get("observation_ids")
                    ):
                        result_ids.update(observation_results.get(observation_id, set()))

                if record_type == "contradiction" and not result_ids:
                    for ref in record.get("evidence_refs", []):
                        if isinstance(ref, dict) and ref.get("result_id"):
                            result_ids.add(ref["result_id"])

                index[key] = result_ids
                if record_type == "observation":
                    observation_results[record_id] = result_ids

    return index, errors


def validate_finding_analysis_refs(evidence: dict[str, Any]) -> list[str]:
    """Validate Finding-to-analysis provenance and Result Unit alignment."""
    index, errors = build_analysis_record_index(evidence)
    findings = evidence.get("findings", {})
    if not isinstance(findings, dict):
        return errors + ["findings must be an object"]

    for finding_id, finding in findings.items():
        if not isinstance(finding, dict):
            errors.append(f"{finding_id}: Finding must be an object")
            continue

        refs = finding.get("scientific_analysis_refs", [])
        if not isinstance(refs, list):
            errors.append(f"{finding_id}: scientific_analysis_refs must be a list")
            continue

        analysis_derived = finding.get("analysis_derived", False)
        if analysis_derived is True and not refs:
            errors.append(
                f"{finding_id}: analysis-derived Finding requires scientific_analysis_refs"
            )
        if refs and analysis_derived is not True:
            errors.append(
                f"{finding_id}: scientific_analysis_refs require analysis_derived=true"
            )

        seen: set[tuple[str, str, str]] = set()
        cited_result_ids: set[str] = set()
        for position, ref in enumerate(refs):
            if not isinstance(ref, dict):
                errors.append(f"{finding_id}: scientific_analysis_refs[{position}] must be an object")
                continue
            analysis_id = ref.get("analysis_id")
            record_type = ref.get("record_type")
            record_id = ref.get("record_id")
            if not all(isinstance(value, str) and value.strip()
                       for value in (analysis_id, record_type, record_id)):
                errors.append(
                    f"{finding_id}: scientific_analysis_refs[{position}] requires analysis_id, record_type and record_id"
                )
                continue
            if record_type not in VALID_RECORD_TYPES:
                errors.append(f"{finding_id}: unsupported scientific analysis record_type {record_type!r}")
                continue
            key = (analysis_id, record_type, record_id)
            if key in seen:
                errors.append(f"{finding_id}: duplicate scientific analysis reference {key}")
                continue
            seen.add(key)
            if key not in index:
                errors.append(f"{finding_id}: unknown scientific analysis record {key}")
                continue
            cited_result_ids.update(index[key])

        if analysis_derived:
            if not cited_result_ids:
                errors.append(
                    f"{finding_id}: cited analysis records do not identify any source Result Units"
                )
            required_result_ids = (
                _as_ids(finding.get("supporting_result_ids"))
                | _as_ids(finding.get("contradictory_result_ids"))
            )
            missing = sorted(required_result_ids - cited_result_ids)
            if missing:
                errors.append(
                    f"{finding_id}: analysis references do not cover Finding Result Units: {', '.join(missing)}"
                )

    return errors


def validate_core_claim_analysis_bridge(
    package: dict[str, Any],
    framework: dict[str, Any],
    evidence: dict[str, Any],
) -> list[str]:
    """Require cross-result central claims to cite an analysis-derived Finding.

    This is a traceability gate only. It does not assess whether the Finding or
    the underlying scientific interpretation is true or sufficiently strong.
    """
    analyses = evidence.get("scientific_analyses", {})
    if not analyses:
        return []

    findings = evidence.get("findings", {})
    claims = framework.get("claims", {})
    core_claim_ids = package.get("core_argument", {}).get("contribution_claim_ids", [])
    errors: list[str] = []

    for claim_id in core_claim_ids:
        claim = claims.get(claim_id)
        if not isinstance(claim, dict):
            continue
        if claim.get("claim_type") not in CROSS_RESULT_CLAIM_TYPES:
            continue

        supporting_result_ids: set[str] = set()
        qualifying_findings: list[dict[str, Any]] = []
        for ref in claim.get("evidence_refs", []):
            if not isinstance(ref, dict):
                continue
            role = ref.get("evidence_role", "SUPPORTS_CLAIM")
            if role != "SUPPORTS_CLAIM":
                continue
            kind, ref_id = ref.get("kind"), ref.get("id")
            if kind == "result_unit":
                supporting_result_ids.add(ref_id)
            elif kind == "finding":
                finding = findings.get(ref_id, {})
                if not isinstance(finding, dict):
                    continue
                supporting_result_ids.update(_as_ids(finding.get("supporting_result_ids")))
                if finding.get("analysis_derived") is True:
                    qualifying_findings.append(finding)

        if len(supporting_result_ids) < 2:
            continue

        has_cross_result_finding = any(
            len(_as_ids(finding.get("supporting_result_ids"))) >= 2
            and _as_ids(finding.get("supporting_result_ids")).issubset(supporting_result_ids)
            for finding in qualifying_findings
        )
        if not has_cross_result_finding:
            errors.append(
                f"{claim_id}: cross-result central Claim must cite an analysis-derived Finding "
                "that links at least two supporting Result Units"
            )

    return errors


def validate_route_analysis_bridge(
    routes_bundle: dict[str, Any],
    evidence: dict[str, Any],
) -> list[str]:
    """Return review warnings for candidate routes lacking a cross-result Finding."""
    if not evidence.get("scientific_analyses"):
        return []
    findings = evidence.get("findings", {})
    warnings: list[str] = []
    for route_id, route in routes_bundle.get("routes", {}).items():
        result_ids = _as_ids(route.get("supporting_result_ids"))
        if len(result_ids) < 2:
            continue
        linked = [
            findings.get(finding_id, {})
            for finding_id in route.get("supporting_finding_ids", [])
        ]
        has_bridge = any(
            isinstance(finding, dict)
            and finding.get("analysis_derived") is True
            and len(_as_ids(finding.get("supporting_result_ids")) & result_ids) >= 2
            for finding in linked
        )
        if not has_bridge:
            warnings.append(
                f"{route_id}: candidate route spans multiple Result Units but has no "
                "analysis-derived supporting Finding; review cross-result synthesis"
            )
    return warnings
