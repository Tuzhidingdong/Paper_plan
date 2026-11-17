#!/usr/bin/env python3
"""Validate the V4 manuscript-development package across all project bundles."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from era_core import atomic_write_json, workspace_paths

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "manuscript_development_bundle.schema.json"
ENTITY_TYPES = {
    "journal_sources": "journal_source",
    "introduction_paragraphs": "introduction_paragraph",
    "storyline": "manuscript_story_step",
    "main_figures": "manuscript_figure",
    "supporting_information": "supporting_information_item",
}


def _unique_map(items: dict[str, Any], id_field: str, label: str,
                errors: list[str]) -> None:
    for key, item in items.items():
        if item.get(id_field) != key:
            errors.append(f"{label} {key}: {id_field} must match its bundle key")


def _check_refs(owner: str, field: str, refs: list[str], valid: set[str],
                errors: list[str]) -> None:
    for ref in refs or []:
        if ref not in valid:
            errors.append(f"{owner}: {field} references unknown ID {ref}")


def _dependency_cycles(tasks: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    graph = {task_id: list(task.get("prerequisites", []))
             for task_id, task in tasks.items()}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            errors.append(f"work-package dependency cycle detected at {task_id}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in graph.get(task_id, []):
            if dependency in graph:
                visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id)
    return errors


def validate_package(package: dict[str, Any],
                     framework: dict[str, Any] | None = None,
                     literature: dict[str, Any] | None = None,
                     evidence: dict[str, Any] | None = None,
                     registry: dict[str, Any] | None = None,
                     deliverables_dir: Path | None = None) -> dict[str, Any]:
    """Return deterministic schema, cross-reference and package-completeness findings."""
    errors: list[str] = []
    warnings: list[str] = []
    framework = framework or {}
    literature = literature or {}
    evidence = evidence or {}
    registry = registry or {}

    if not isinstance(package, dict):
        return {"status": "ERROR", "errors": ["package root must be an object"],
                "warnings": [], "counts": {}}

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        for issue in sorted(validator.iter_errors(package),
                            key=lambda e: list(map(str, e.absolute_path))):
            location = ".".join(str(x) for x in issue.absolute_path) or "<root>"
            errors.append(f"schema:{location}: {issue.message}")
    except (OSError, json.JSONDecodeError, Exception) as exc:
        errors.append(f"cannot validate manuscript-development schema: {exc}")

    claims = framework.get("claims", {})
    slots = framework.get("data_slots", {})
    tasks = framework.get("tasks", {})
    claim_ids = set(claims) or set(package.get("claim_ids", []))
    slot_ids = set(slots) or set(package.get("data_slot_ids", []))
    task_ids = set(tasks)
    literature_claim_ids = set(literature.get("literature_claims", {}))
    result_ids = set(evidence.get("result_units", {}))
    finding_ids = set(evidence.get("findings", {}))

    _check_refs("package", "claim_ids", package.get("claim_ids", []),
                claim_ids, errors)
    _check_refs("package", "data_slot_ids", package.get("data_slot_ids", []),
                slot_ids, errors)

    journal_sources = package.get("journal_sources", {})
    paragraphs = package.get("introduction_paragraphs", {})
    storyline = package.get("storyline", {})
    figures = package.get("main_figures", {})
    si_items = package.get("supporting_information", {})
    _unique_map(journal_sources, "source_id", "journal source", errors)
    _unique_map(paragraphs, "paragraph_id", "Introduction paragraph", errors)
    _unique_map(storyline, "step_id", "story step", errors)
    _unique_map(figures, "figure_id", "Figure", errors)
    _unique_map(si_items, "item_id", "SI item", errors)

    journal_profile = package.get("journal_profile", {})
    journal_source_ids = set(journal_sources)
    _check_refs("journal_profile", "source_ids",
                journal_profile.get("source_ids", []), journal_source_ids, errors)
    if journal_profile.get("status") == "VERIFIED" and not journal_profile.get("source_ids"):
        errors.append("journal_profile is VERIFIED but has no traceable official or publisher sources")
    if journal_profile.get("status") == "PARTIAL" and not journal_profile.get("unresolved_items"):
        warnings.append("journal_profile is PARTIAL but unresolved_items is empty")
    if journal_profile.get("status") == "UNVERIFIED":
        warnings.append("target-journal requirements are not verified; do not claim journal compliance")

    core = package.get("core_argument", {})
    _check_refs("core_argument", "contribution_claim_ids",
                core.get("contribution_claim_ids", []), claim_ids, errors)
    if not core.get("novelty_boundaries"):
        warnings.append("core argument has no explicit novelty boundaries")
    if core.get("novelty_confidence") in {"MEDIUM", "HIGH"} and not core.get("contribution_claim_ids"):
        warnings.append("novelty confidence is elevated without linked contribution claims")

    for paragraph_id, paragraph in paragraphs.items():
        _check_refs(paragraph_id, "claim_ids", paragraph.get("claim_ids", []),
                    claim_ids, errors)
        _check_refs(paragraph_id, "literature_claim_ids",
                    paragraph.get("literature_claim_ids", []),
                    literature_claim_ids, errors)
        if paragraph.get("status") in {"DRAFTED", "REVIEWED"}:
            if not paragraph.get("literature_claim_ids"):
                warnings.append(f"{paragraph_id}: drafted Introduction paragraph has no linked verified literature claims")

    intro = package.get("introduction", {})
    _check_refs("introduction", "paragraph_ids",
                intro.get("paragraph_ids", []), set(paragraphs), errors)
    if intro.get("status") in {"DRAFT", "REVIEWED"} and not intro.get("draft"):
        errors.append("Introduction is marked DRAFT/REVIEWED but draft text is empty")

    panel_index: dict[str, str] = {}
    figure_orders: dict[int, str] = {}
    for figure_id, figure in figures.items():
        _check_refs(figure_id, "claim_ids", figure.get("claim_ids", []),
                    claim_ids, errors)
        _check_refs(figure_id, "data_slot_ids", figure.get("data_slot_ids", []),
                    slot_ids, errors)
        order = figure.get("order")
        if order in figure_orders:
            warnings.append(f"{figure_id}: Figure order duplicates {figure_orders[order]}")
        else:
            figure_orders[order] = figure_id
        if not figure.get("panels"):
            errors.append(f"{figure_id}: each planned main-text Figure needs at least one Panel")
        if not figure.get("claim_ids"):
            errors.append(f"{figure_id}: Figure is not linked to a scientific Claim")
        for panel in figure.get("panels", []):
            label = panel.get("label", "")
            panel_key = f"{figure_id}.{label}"
            if panel_key in panel_index:
                errors.append(f"{figure_id}: duplicate Panel label {label}")
            panel_index[panel_key] = figure_id
            _check_refs(panel_key, "claim_ids", panel.get("claim_ids", []),
                        claim_ids, errors)
            _check_refs(panel_key, "data_slot_ids", panel.get("data_slot_ids", []),
                        slot_ids, errors)
            if not panel.get("claim_ids") and not panel.get("data_slot_ids"):
                warnings.append(f"{panel_key}: Panel has no explicit Claim or Data Slot link")
            for evidence_ref in panel.get("existing_evidence_refs", []):
                kind, ref_id = evidence_ref.get("kind"), evidence_ref.get("id")
                valid = result_ids if kind == "result_unit" else finding_ids if kind == "finding" else None
                if valid is None:
                    errors.append(f"{panel_key}: unsupported existing evidence kind {kind!r}")
                elif ref_id not in valid:
                    errors.append(f"{panel_key}: unknown existing evidence {kind}:{ref_id}")

    for item_id, item in si_items.items():
        _check_refs(item_id, "claim_ids", item.get("claim_ids", []), claim_ids, errors)
        _check_refs(item_id, "figure_ids", item.get("figure_ids", []), set(figures), errors)
        _check_refs(item_id, "data_slot_ids", item.get("data_slot_ids", []), slot_ids, errors)

    story_orders: dict[int, str] = {}
    story_figure_refs: set[str] = set()
    for step_id, step in storyline.items():
        _check_refs(step_id, "claim_ids", step.get("claim_ids", []), claim_ids, errors)
        _check_refs(step_id, "figure_ids", step.get("figure_ids", []), set(figures), errors)
        story_figure_refs.update(step.get("figure_ids", []))
        order = step.get("order")
        if order in story_orders:
            errors.append(f"{step_id}: storyline order duplicates {story_orders[order]}")
        else:
            story_orders[order] = step_id
    for figure_id in figures:
        if figure_id not in story_figure_refs:
            warnings.append(f"{figure_id}: planned Figure is not placed in the manuscript storyline")

    toc = package.get("toc_graphic", {})
    _check_refs("toc_graphic", "claim_ids", toc.get("claim_ids", []), claim_ids, errors)
    _check_refs("toc_graphic", "data_slot_ids", toc.get("data_slot_ids", []), slot_ids, errors)
    if toc.get("journal_requirement_status") == "REQUIRED" and toc.get("status") == "NOT_STARTED":
        warnings.append("journal requires a TOC graphic but no concept has been planned")

    sections = package.get("manuscript_sections", [])
    for index, section in enumerate(sections, start=1):
        owner = f"manuscript_sections[{index}]"
        _check_refs(owner, "claim_ids", section.get("claim_ids", []), claim_ids, errors)
        _check_refs(owner, "figure_ids", section.get("figure_ids", []), set(figures), errors)
        _check_refs(owner, "citation_literature_claim_ids",
                    section.get("citation_literature_claim_ids", []),
                    literature_claim_ids, errors)

    work_package_ids = set(package.get("work_package_task_ids", []))
    _check_refs("package", "work_package_task_ids", list(work_package_ids),
                task_ids, errors)
    slot_to_tasks: dict[str, set[str]] = defaultdict(set)
    for task_id, task in tasks.items():
        for slot_id in task.get("target_data_slot_ids", []):
            slot_to_tasks[slot_id].add(task_id)
        if task_id in work_package_ids:
            if not task.get("objective"):
                warnings.append(f"{task_id}: work-package handoff lacks a specific objective")
            if not task.get("expected_output") or not task.get("completion_criteria"):
                errors.append(f"{task_id}: work-package needs an output and measurable completion criteria")
            if task.get("task_type") == "EXPERIMENT":
                for field in ("controls", "measurements", "required_raw_data", "replicate_plan"):
                    if not task.get(field):
                        warnings.append(f"{task_id}: experiment handoff is missing {field}; request confirmation rather than inventing it")
            if task.get("task_type") in {"THEORY", "COMPUTATION"}:
                design = task.get("design", {})
                required = set(design.get("required_inputs", []))
                available = set(design.get("available_inputs", []))
                unresolved = required - available
                if unresolved and task.get("status") in {"READY", "IN_PROGRESS"}:
                    errors.append(f"{task_id}: calculation is executable while required inputs are missing: {', '.join(sorted(unresolved))}")
                if unresolved and task.get("status") != "BLOCKED_BY_EXPERIMENT":
                    warnings.append(f"{task_id}: calculation with unresolved inputs should be BLOCKED_BY_EXPERIMENT")
                if task.get("status") == "BLOCKED_BY_EXPERIMENT" and not (task.get("blocked_by_experiment_ids") or task.get("blockers")):
                    warnings.append(f"{task_id}: blocked calculation does not identify prerequisite work")
    for slot_id, slot in slots.items():
        if slot.get("priority") == "ESSENTIAL" and slot.get("status") in {"MISSING", "PARTIAL", "BLOCKED"}:
            if not slot_to_tasks.get(slot_id) and not slot.get("no_task_rationale"):
                errors.append(f"{slot_id}: essential unsatisfied Data Slot has no task or explicit no_task_rationale")
        if slot_id in package.get("data_slot_ids", []) and slot.get("status") in {"MISSING", "PARTIAL", "BLOCKED"}:
            if slot.get("priority") == "ESSENTIAL" and not slot_to_tasks.get(slot_id):
                warnings.append(f"{slot_id}: manuscript package does not close an essential evidence gap")
    # An essential slot should be placed in a figure, SI item or explicitly deferred.
    placed_slots: set[str] = set()
    for figure in figures.values():
        placed_slots.update(figure.get("data_slot_ids", []))
        for panel in figure.get("panels", []):
            placed_slots.update(panel.get("data_slot_ids", []))
    for item in si_items.values():
        placed_slots.update(item.get("data_slot_ids", []))
    for slot_id in package.get("data_slot_ids", []):
        slot = slots.get(slot_id, {})
        if slot.get("priority") == "ESSENTIAL" and slot_id not in placed_slots and not slot.get("no_task_rationale"):
            warnings.append(f"{slot_id}: essential Data Slot is not placed in a main Figure or Supporting Information item")

    errors.extend(_dependency_cycles(tasks))
    for task_id, task in tasks.items():
        for dependency in task.get("prerequisites", []):
            if dependency not in tasks:
                errors.append(f"{task_id}: unknown prerequisite task {dependency}")

    # Permanent V4 entities must be issued by the shared Python ID registry.
    registry_entities = registry.get("entities", {})
    for collection_name, expected_type in ENTITY_TYPES.items():
        collection = package.get(collection_name, {})
        for entity_id in collection:
            record = registry_entities.get(entity_id)
            if registry and record is None:
                errors.append(f"{entity_id}: missing from Python ID registry")
            elif record and record.get("entity_type") != expected_type:
                errors.append(f"{entity_id}: registry type must be {expected_type}")

    for deliverable in package.get("deliverables", []):
        path_text = deliverable.get("path", "")
        relative = Path(path_text)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"deliverable path must remain workspace-relative: {path_text}")
        if deliverables_dir is not None and deliverable.get("required") and deliverable.get("status") == "FINAL":
            target = deliverables_dir / relative
            if not target.is_file():
                errors.append(f"required deliverable marked FINAL but file is missing: {path_text}")

    quality = package.get("quality_review", {})
    check_statuses = [item.get("status") for item in quality.get("checks", [])]
    if quality.get("status") == "PASS" and ("FAIL" in check_statuses or quality.get("unresolved_critical_questions")):
        errors.append("quality_review cannot be PASS while failed checks or critical open questions remain")
    if quality.get("status") == "PASS_WITH_WARNINGS" and "FAIL" in check_statuses:
        errors.append("quality_review cannot be PASS_WITH_WARNINGS while a check is FAIL")

    counts = {
        "claims": len(claim_ids), "data_slots": len(slot_ids),
        "introduction_paragraphs": len(paragraphs), "story_steps": len(storyline),
        "main_figures": len(figures), "panels": len(panel_index),
        "supporting_information_items": len(si_items),
        "work_package_tasks": len(work_package_ids),
    }
    return {"status": "ERROR" if errors else ("WARNING" if warnings else "PASS"),
            "errors": errors, "warnings": warnings, "counts": counts,
            "note": "Checks schema, provenance links, manuscript architecture and task closure. It does not certify scientific truth, novelty or journal acceptance."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--deliverables-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    paths = workspace_paths(workspace)
    state = paths["state"]
    errors: list[str] = []

    def read(name: str, required: bool = True) -> dict[str, Any]:
        path = state / name
        if not path.is_file():
            if required:
                errors.append(f"missing required bundle: {name}")
            return {}
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                errors.append(f"{name}: root must be an object")
                return {}
            return value
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read {name}: {exc}")
            return {}

    package = read("manuscript_development_bundle.json")
    framework = read("framework_bundle.json")
    literature = read("literature_bundle.json")
    evidence = read("evidence_bundle.json", required=False)
    registry = read("id_registry.json", required=False)
    report = validate_package(package, framework, literature, evidence,
                              registry, args.deliverables_dir)
    report["errors"] = errors + report["errors"]
    if report["errors"]:
        report["status"] = "ERROR"
    output = args.report or state / "manuscript_development_validation.json"
    atomic_write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "ERROR" else 0


if __name__ == "__main__":
    raise SystemExit(main())
