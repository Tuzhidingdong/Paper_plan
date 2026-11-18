#!/usr/bin/env python3
"""Validate cross-bundle scientific provenance and the research-plan dependency graph."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from era_core import atomic_write_json, workspace_paths
from scientific_quality_gates import validate_route_selection


def _read(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"Missing required planning bundle: {path.name}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot read {path.name}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name} root must be a JSON object")
        return {}
    return value


def validate_bundles(evidence: dict[str, Any], literature: dict[str, Any],
                     routes_bundle: dict[str, Any], framework: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    evidence_results = evidence.get("result_units", {})
    evidence_findings = evidence.get("findings", {})
    evidence_samples = evidence.get("samples", {})
    records = literature.get("literature_records", {})
    lit_claims = literature.get("literature_claims", {})
    gaps = literature.get("research_gaps", {})
    routes = routes_bundle.get("routes", {})
    claims = framework.get("claims", {})
    slots = framework.get("data_slots", {})
    data_units = framework.get("data_units", {})
    tasks = framework.get("tasks", {})

    # Every gap and literature claim must be bounded by a recorded real search.
    search_scope = literature.get("search_scope", {})
    for field in ("search_date", "databases", "date_range", "search_terms", "target_systems", "inclusion_criteria", "exclusion_criteria"):
        if not search_scope.get(field):
            warnings.append(f"Literature search_scope.{field} is missing or empty")

    # Literature evidence is access-tiered. Metadata-only records can guide search,
    # but can never substantiate a scientific statement.
    valid_access = {"METADATA_ONLY", "ABSTRACT_VERIFIED", "FULLTEXT_VERIFIED"}
    snippets_by_lit: dict[str, dict[str, dict[str, Any]]] = {}
    for lit_id, record in records.items():
        if record.get("literature_id", lit_id) != lit_id:
            errors.append(f"{lit_id}: literature_id does not match bundle key")
        if not record.get("title"):
            errors.append(f"{lit_id}: title is required")
        access = record.get("access_level")
        if access not in valid_access:
            errors.append(f"{lit_id}: invalid access_level {access!r}")
        snippets = {}
        for snippet in record.get("evidence_snippets", []):
            snippet_id = snippet.get("snippet_id")
            if not snippet_id or not snippet.get("text") or not snippet.get("source_location"):
                errors.append(f"{lit_id}: every evidence snippet needs snippet_id, exact text and source_location")
                continue
            snippets[snippet_id] = snippet
        snippets_by_lit[lit_id] = snippets
        if access == "FULLTEXT_VERIFIED":
            if not snippets:
                errors.append(f"{lit_id}: FULLTEXT_VERIFIED requires at least one located full-text evidence snippet")
            elif not any(str(item.get("scope", "")).upper() == "FULLTEXT" for item in snippets.values()):
                errors.append(f"{lit_id}: FULLTEXT_VERIFIED snippets must identify FULLTEXT scope")
        if access == "ABSTRACT_VERIFIED" and not record.get("abstract") and not snippets:
            warnings.append(f"{lit_id}: ABSTRACT_VERIFIED record has no retained abstract text or snippet")

    for claim_id, lit_claim in lit_claims.items():
        if lit_claim.get("literature_claim_id", claim_id) != claim_id:
            errors.append(f"{claim_id}: literature_claim_id does not match bundle key")
        citation_refs = lit_claim.get("citation_refs", [])
        if not citation_refs:
            errors.append(f"{claim_id}: literature claim needs citation_refs")
        for ref in citation_refs:
            lit_id = ref.get("literature_id")
            snippet_id = ref.get("snippet_id")
            record = records.get(lit_id)
            if record is None:
                errors.append(f"{claim_id}: unknown literature_id {lit_id}")
                continue
            if record.get("access_level") == "METADATA_ONLY":
                errors.append(f"{claim_id}: metadata-only source {lit_id} cannot support a literature claim")
                continue
            snippet = snippets_by_lit.get(lit_id, {}).get(snippet_id)
            if snippet is None:
                errors.append(f"{claim_id}: unknown or unlocated snippet {lit_id}/{snippet_id}")
                continue
            if record.get("access_level") == "ABSTRACT_VERIFIED":
                scope = str(snippet.get("scope", "")).upper()
                location = str(snippet.get("source_location", "")).lower()
                if scope not in {"ABSTRACT", "METADATA"} and "abstract" not in location:
                    errors.append(f"{claim_id}: abstract-only source {lit_id} is used outside abstract scope")

    for gap_id, gap in gaps.items():
        if gap.get("gap_id", gap_id) != gap_id:
            errors.append(f"{gap_id}: gap_id does not match bundle key")
        bounds = gap.get("search_bounds", {})
        for field in ("databases", "date_range", "search_terms", "target_systems"):
            if not bounds.get(field):
                warnings.append(f"{gap_id}: research-gap search_bounds.{field} is missing")
        if not gap.get("supporting_literature_claim_ids") and not gap.get("counterevidence_literature_ids"):
            warnings.append(f"{gap_id}: gap has no linked supporting or counter-evidence literature")
        for lit_claim_id in gap.get("supporting_literature_claim_ids", []):
            if lit_claim_id not in lit_claims:
                errors.append(f"{gap_id}: unknown supporting literature claim {lit_claim_id}")
        for lit_id in gap.get("counterevidence_literature_ids", []):
            if lit_id not in records:
                errors.append(f"{gap_id}: unknown counter-evidence literature record {lit_id}")

    # Candidate research routes must be traceable to evidence and bounded literature gaps.
    normalized_route_questions = {}
    for route_id, route in routes.items():
        if route.get("route_id", route_id) != route_id:
            errors.append(f"{route_id}: route_id does not match bundle key")
        for field in ("central_question", "novelty_candidate", "bounded_gap", "feasibility", "novelty_risk"):
            if not route.get(field):
                errors.append(f"{route_id}: {field} is required")
        for result_id in route.get("supporting_result_ids", []):
            if result_id not in evidence_results:
                errors.append(f"{route_id}: unknown supporting Result Unit {result_id}")
        for finding_id in route.get("supporting_finding_ids", []):
            if finding_id not in evidence_findings:
                errors.append(f"{route_id}: unknown supporting Finding {finding_id}")
        for gap_id in route.get("gap_ids", []):
            if gap_id not in gaps:
                errors.append(f"{route_id}: unknown Research Gap {gap_id}")
        for lit_claim_id in route.get("supporting_literature_claim_ids", []):
            if lit_claim_id not in lit_claims:
                errors.append(f"{route_id}: unknown literature claim {lit_claim_id}")
        for lit_id in route.get("competing_literature_ids", []):
            if lit_id not in records:
                errors.append(f"{route_id}: unknown competing literature record {lit_id}")
        for sample_id in route.get("sample_dependency_ids", []):
            if sample_id not in evidence_samples:
                errors.append(f"{route_id}: unknown sample dependency {sample_id}")
        normalized_question = " ".join(str(route.get("central_question", "")).casefold().split())
        if normalized_question:
            if normalized_question in normalized_route_questions:
                warnings.append(f"{route_id}: central question duplicates {normalized_route_questions[normalized_question]}; route diversity needs human review")
            else:
                normalized_route_questions[normalized_question] = route_id
        if not route.get("alternative_explanations"):
            warnings.append(f"{route_id}: alternative artifact/mechanism explanations are not recorded")
        if not route.get("data_slot_needs"):
            warnings.append(f"{route_id}: route has no explicit data_slot_needs")

    if len(routes) < 3:
        note = routes_bundle.get("route_generation_note")
        if not note:
            warnings.append("Fewer than three distinct research routes are present and no explanation is recorded; do not fabricate a weak third route.")
    recommended_route = routes_bundle.get("recommended_route_id")
    framework_route = framework.get("recommended_route_id")
    if recommended_route and framework_route and recommended_route != framework_route:
        errors.append("framework recommended_route_id must match routes_bundle recommended_route_id")
    if recommended_route and recommended_route not in routes:
        errors.append(f"recommended_route_id references unknown route {recommended_route}")
    approval_a = routes_bundle.get("approval_A", {})
    if approval_a.get("status") == "APPROVED" and not approval_a.get("decision"):
        errors.append("Gate A cannot be APPROVED without a recorded human decision")
    route_errors, route_warnings = validate_route_selection(routes_bundle)
    errors.extend(route_errors)
    warnings.extend(route_warnings)

    # Manuscript Claims must point to traceable evidence or verified literature claims.
    valid_claim_types = {"Descriptive", "Comparative", "Associational", "Causal", "Mechanistic"}
    valid_epistemic = {"Observed", "Interpreted", "Hypothesized"}
    for claim_id, claim in claims.items():
        if claim.get("claim_id", claim_id) != claim_id:
            errors.append(f"{claim_id}: claim_id does not match bundle key")
        if claim.get("claim_type") not in valid_claim_types:
            errors.append(f"{claim_id}: invalid claim_type")
        if claim.get("epistemic_status") not in valid_epistemic:
            errors.append(f"{claim_id}: invalid epistemic_status")
        evidence_refs = claim.get("evidence_refs", [])
        for ref in evidence_refs:
            kind, ref_id = ref.get("kind"), ref.get("id")
            if kind == "result_unit" and ref_id not in evidence_results:
                errors.append(f"{claim_id}: unknown Result Unit {ref_id}")
            elif kind == "finding" and ref_id not in evidence_findings:
                errors.append(f"{claim_id}: unknown Finding {ref_id}")
            elif kind == "literature_claim" and ref_id not in lit_claims:
                errors.append(f"{claim_id}: unknown literature claim {ref_id}")
            elif kind not in {"result_unit", "finding", "literature_claim"}:
                errors.append(f"{claim_id}: invalid evidence_refs kind {kind}")
        if not evidence_refs:
            errors.append(f"{claim_id}: at least one evidence_refs entry is required")
        if claim.get("claim_type") in {"Causal", "Mechanistic"} and not claim.get("alternative_explanations"):
            warnings.append(f"{claim_id}: causal/mechanistic claim has no alternative_explanations")

    # Data Slots are requirements, not claims that the result already exists.
    valid_slot_status = {"FILLED", "PARTIAL", "MISSING", "BLOCKED"}
    for slot_id, slot in slots.items():
        if slot.get("data_slot_id", slot_id) != slot_id:
            errors.append(f"{slot_id}: data_slot_id does not match bundle key")
        if slot.get("target_claim_id") not in claims:
            errors.append(f"{slot_id}: target_claim_id references unknown claim")
        if not slot.get("required_evidence_description"):
            errors.append(f"{slot_id}: required_evidence_description is required")
        if slot.get("status") not in valid_slot_status:
            errors.append(f"{slot_id}: invalid Data Slot status")
        if slot.get("priority") not in {None, "ESSENTIAL", "STRENGTHENING", "OPTIONAL"}:
            errors.append(f"{slot_id}: invalid Data Slot priority")
        for result_id in slot.get("available_result_ids", []):
            if result_id not in evidence_results:
                errors.append(f"{slot_id}: unknown available Result Unit {result_id}")

    # Derived Data Units retain source lineage and do not count as independent experiments.
    root_usage = defaultdict(list)
    for unit_id, unit in data_units.items():
        if unit.get("data_unit_id", unit_id) != unit_id:
            errors.append(f"{unit_id}: data_unit_id does not match bundle key")
        source_ids = unit.get("source_result_ids", [])
        if not source_ids:
            errors.append(f"{unit_id}: source_result_ids cannot be empty")
        for result_id in source_ids:
            if result_id not in evidence_results:
                errors.append(f"{unit_id}: unknown source Result Unit {result_id}")
            root_usage[result_id].append(unit_id)
        if not unit.get("transformation") and unit.get("derived", False):
            errors.append(f"{unit_id}: derived Data Unit requires a transformation description")
    for result_id, units in root_usage.items():
        if len(units) > 1:
            warnings.append(
                f"{result_id}: reused by Data Units {', '.join(units)}; these are derived views of one source, not independent experiments"
            )

    # Every proposed execution task must close an explicit Data Slot and define a completion test.
    valid_task_types = {"EXPERIMENT", "ANALYSIS", "THEORY", "COMPUTATION", "LITERATURE"}
    valid_task_status = {"READY", "BLOCKED_BY_EXPERIMENT", "PLANNED", "DONE"}
    for task_id, task in tasks.items():
        if task.get("task_id", task_id) != task_id:
            errors.append(f"{task_id}: task_id does not match bundle key")
        if task.get("task_type") not in valid_task_types:
            errors.append(f"{task_id}: invalid task_type")
        if task.get("status") not in valid_task_status:
            errors.append(f"{task_id}: invalid task status")
        if task.get("priority") not in {"P0", "P1", "P2"}:
            warnings.append(f"{task_id}: task priority must be P0, P1 or P2")
        targets = task.get("target_data_slot_ids", [])
        if not targets:
            errors.append(f"{task_id}: at least one target_data_slot_id is required")
        for slot_id in targets:
            if slot_id not in slots:
                errors.append(f"{task_id}: unknown target Data Slot {slot_id}")
        for claim_id in task.get("target_claim_ids", []):
            if claim_id not in claims:
                errors.append(f"{task_id}: unknown target Claim {claim_id}")
        if not task.get("expected_output"):
            errors.append(f"{task_id}: expected_output is required")
        if not task.get("completion_criteria"):
            errors.append(f"{task_id}: completion_criteria is required")
        if task.get("requires_experiment_before_calculation") and task.get("task_type") in {"THEORY", "COMPUTATION"}:
            if task.get("status") != "BLOCKED_BY_EXPERIMENT":
                errors.append(f"{task_id}: calculation requiring experimental input must be BLOCKED_BY_EXPERIMENT")
            if not task.get("blocked_by_experiment_ids"):
                errors.append(f"{task_id}: blocked calculation must identify prerequisite experiment/task IDs")
        if task.get("task_type") == "EXPERIMENT":
            for field in ("objective", "controls", "measurements", "required_raw_data"):
                if not task.get(field):
                    warnings.append(f"{task_id}: experiment plan is missing {field}")
            if not task.get("replicate_plan"):
                warnings.append(f"{task_id}: replicate plan is not specified; do not invent replicate count")
        if task.get("task_type") in {"THEORY", "COMPUTATION"} and task.get("status") != "BLOCKED_BY_EXPERIMENT":
            if not task.get("input_structure_or_model"):
                warnings.append(f"{task_id}: calculation input structure/model is not explicitly identified")

    # Task prerequisite links must resolve and form an acyclic dependency graph.
    task_graph = {task_id: list(task.get("prerequisites", [])) for task_id, task in tasks.items()}
    dependency_groups = ("execution_prerequisite_ids", "interpretation_prerequisite_ids", "publication_prerequisite_ids")
    priority_rank = {"P0": 0, "P1": 1, "P2": 2}
    for task_id, task in tasks.items():
        for prerequisite_id in task_graph[task_id]:
            if prerequisite_id not in tasks:
                errors.append(f"{task_id}: unknown prerequisite task {prerequisite_id}")
        for prerequisite_id in task.get("blocked_by_experiment_ids", []):
            prerequisite = tasks.get(prerequisite_id)
            if prerequisite is None:
                errors.append(f"{task_id}: unknown blocked_by_experiment_id {prerequisite_id}")
            elif prerequisite.get("task_type") != "EXPERIMENT":
                errors.append(f"{task_id}: blocked_by_experiment_id {prerequisite_id} is not an EXPERIMENT task")
        classified = any(field in task for field in dependency_groups)
        if classified:
            categorized = set().union(*(set(task.get(field, [])) for field in dependency_groups))
            if categorized != set(task.get("prerequisites", [])):
                errors.append(f"{task_id}: prerequisites must equal the union of execution, interpretation and publication prerequisite IDs")
        for field in dependency_groups:
            for prerequisite_id in task.get(field, []):
                if prerequisite_id not in tasks:
                    errors.append(f"{task_id}: unknown {field} task {prerequisite_id}")
                prerequisite = tasks.get(prerequisite_id, {})
                if (field == "execution_prerequisite_ids"
                    and task.get("priority") in priority_rank
                    and prerequisite.get("priority") in priority_rank
                    and priority_rank[prerequisite["priority"]] > priority_rank[task["priority"]]):
                    warnings.append(f"{task_id}: execution prerequisite {prerequisite_id} has lower priority ({prerequisite['priority']}) than dependent task ({task['priority']}); review sequencing")
        design = task.get("execution_design", {})
        if design.get("readiness") == "APPROVED_FOR_EXECUTION":
            if task.get("status") != "READY":
                errors.append(f"{task_id}: APPROVED_FOR_EXECUTION requires task status READY")
            execution_dependencies = task.get(
                "execution_prerequisite_ids",
                [] if classified else task_graph[task_id]
            )
            for prerequisite_id in execution_dependencies:
                if tasks.get(prerequisite_id, {}).get("status") != "DONE":
                    errors.append(f"{task_id}: execution prerequisite {prerequisite_id} is not DONE")
        if task.get("status") == "READY":
            blocking = task.get("execution_prerequisite_ids", task_graph[task_id] if not classified else [])
            for prerequisite_id in blocking:
                if tasks.get(prerequisite_id, {}).get("status") != "DONE":
                    warnings.append(f"{task_id}: execution prerequisite {prerequisite_id} is not DONE; verify execution readiness")

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(f"Task dependency cycle detected at {task_id}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in task_graph.get(task_id, []):
            if dependency in task_graph:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)
    for task_id in task_graph:
        visit(task_id)

    tasks_by_slot = defaultdict(list)
    for task_id, task in tasks.items():
        for slot_id in task.get("target_data_slot_ids", []):
            tasks_by_slot[slot_id].append(task_id)
    for slot_id, slot in slots.items():
        if slot.get("priority") == "ESSENTIAL" and slot.get("status") in {"MISSING", "PARTIAL", "BLOCKED"}:
            if not tasks_by_slot.get(slot_id) and not slot.get("no_task_rationale"):
                errors.append(f"{slot_id}: essential unsatisfied Data Slot needs an execution task or explicit no_task_rationale")
        if slot.get("status") == "FILLED" and not (slot.get("available_result_ids") or slot.get("data_unit_ids")):
            errors.append(f"{slot_id}: FILLED Data Slot must link to an existing Result Unit or Data Unit")
        for unit_id in slot.get("data_unit_ids", []):
            if unit_id not in data_units:
                errors.append(f"{slot_id}: unknown Data Unit {unit_id}")

    approval_b = framework.get("approval_B", {})
    if approval_b.get("status") == "APPROVED" and not approval_b.get("decision"):
        errors.append("Gate B cannot be APPROVED without a recorded human decision")
    if framework.get("recommended_route_id") and framework.get("recommended_route_id") not in routes:
        errors.append("Framework recommended_route_id is not present in routes_bundle")

    return {
        "status": "ERROR" if errors else ("WARNING" if warnings else "PASS"),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "literature_records": len(records), "literature_claims": len(lit_claims),
            "research_gaps": len(gaps), "routes": len(routes), "claims": len(claims),
            "data_slots": len(slots), "data_units": len(data_units), "tasks": len(tasks),
        },
        "note": "Structural provenance validation only; it does not prove literature novelty, experimental validity or scientific mechanisms.",
    }


def validate_registry_entities(registry: dict[str, Any], literature: dict[str, Any],
                               routes_bundle: dict[str, Any], framework: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    mapping = [
        (literature.get("literature_records", {}), "literature_record"),
        (literature.get("literature_claims", {}), "literature_claim"),
        (literature.get("research_gaps", {}), "research_gap"),
        (routes_bundle.get("routes", {}), "research_route"),
        (framework.get("claims", {}), "scientific_claim"),
        (framework.get("data_slots", {}), "data_slot"),
        (framework.get("data_units", {}), "data_unit"),
        (framework.get("tasks", {}), "execution_task"),
    ]
    entities = registry.get("entities", {})
    for literature_record in literature.get("literature_records", {}).values():
        for snippet in literature_record.get("evidence_snippets", []):
            snippet_id = snippet.get("snippet_id")
            if snippet_id:
                record = entities.get(snippet_id)
                if record is None:
                    errors.append(f"{snippet_id}: literature snippet ID is absent from Python id_registry.json")
                elif record.get("entity_type") != "literature_snippet":
                    errors.append(f"{snippet_id}: ID registry type is not literature_snippet")
    for collection, expected_type in mapping:
        for entity_id in collection:
            record = entities.get(entity_id)
            if record is None:
                errors.append(f"{entity_id}: permanent ID is absent from Python id_registry.json")
            elif record.get("entity_type") != expected_type:
                errors.append(f"{entity_id}: ID registry type {record.get('entity_type')!r} does not match {expected_type!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    paths = workspace_paths(workspace)
    errors: list[str] = []
    evidence = _read(paths["bundle"], errors)
    literature = _read(paths["state"] / "literature_bundle.json", errors)
    routes = _read(paths["state"] / "routes_bundle.json", errors)
    framework = _read(paths["state"] / "framework_bundle.json", errors)
    report = validate_bundles(evidence, literature, routes, framework)
    registry = {}
    if paths["registry"].is_file():
        try:
            registry = json.loads(paths["registry"].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Cannot read id_registry.json: {exc}")
    errors.extend(validate_registry_entities(registry, literature, routes, framework))
    report["errors"] = errors + report["errors"]
    if report["errors"]:
        report["status"] = "ERROR"
    output = args.report or (paths["state"] / "planning_validation.json")
    atomic_write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
