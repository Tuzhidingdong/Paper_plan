"""Shared registry and identity checks for imported Data_analysis Evidence Packages."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from era_core import load_json, sha256_file, workspace_paths

HEX64 = re.compile(r"^[a-fA-F0-9]{64}$")
CATEGORY_TYPES = {
    "dataset": ("datasets", "dataset_id"),
    "battery_report": ("battery_reports", "analysis_run_id"),
    "statistics_report": ("statistics_reports", "analysis_run_id"),
    "xrd_report": ("xrd_reports", "analysis_run_id"),
    "xanes_report": ("xanes_reports", "analysis_run_id"),
    "eis_report": ("eis_reports", "analysis_run_id"),
    "cross_modal_report": ("cross_modal_reports", "cross_modal_evidence_id"),
}


def registry_path(workspace: Path) -> Path:
    return workspace_paths(workspace)["external_sources"] / "registry.json"


def load_registry(workspace: Path) -> dict[str, Any]:
    return load_json(registry_path(workspace), default={
        "schema_version": 1, "source_system": "Data_analysis",
        "contract_id": "scientific-evidence-export", "contract_version": "1.0.0",
        "packages": {},
    })


def package_entity(package: dict[str, Any], entity_type: str, entity_id: str) -> dict[str, Any] | None:
    if entity_type not in CATEGORY_TYPES:
        return None
    collection, id_field = CATEGORY_TYPES[entity_type]
    for item in package.get(collection, []):
        if item.get(id_field) == entity_id:
            return item
    return None


def validate_external_source_ref(workspace: Path, ref: dict[str, Any]) -> list[str]:
    """Validate a Result Unit's reference against the immutable imported package copy."""
    errors: list[str] = []
    required = ("source_system", "contract_id", "contract_version",
                "evidence_package_id", "entity_type", "entity_id", "summary_sha256", "package_sha256")
    for field in required:
        if not ref.get(field):
            errors.append(f"external source reference is missing {field}")
    if errors:
        return errors
    if ref["source_system"] != "Data_analysis":
        errors.append("external source reference source_system must be Data_analysis")
    if ref["contract_id"] != "scientific-evidence-export" or ref["contract_version"] != "1.0.0":
        errors.append("external source reference uses an unsupported exchange contract")
    entity_type = ref["entity_type"]
    if entity_type not in CATEGORY_TYPES:
        errors.append(f"unsupported external entity_type {entity_type!r}")
        return errors
    try:
        record = load_registry(workspace).get("packages", {}).get(ref["evidence_package_id"])
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"external source registry cannot be read: {exc}"]
    if not isinstance(record, dict):
        return errors + [f"external evidence package {ref['evidence_package_id']} is not imported"]
    package_hash = record.get("package_sha256")
    if ref.get("package_sha256") != package_hash:
        errors.append("external source reference package_sha256 does not match registry")
    package_file = workspace / record.get("package_path", "")
    if not package_file.is_file():
        return errors + [f"imported package file is missing: {package_file}"]
    actual_hash = sha256_file(package_file)
    if actual_hash != package_hash:
        errors.append("imported package file hash does not match external source registry")
        return errors
    try:
        package = json.loads(package_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"cannot read imported package: {exc}"]
    item = package_entity(package, entity_type, ref["entity_id"])
    if item is None:
        errors.append(f"external entity {entity_type}/{ref['entity_id']} is not present in imported package")
        return errors
    if ref.get("analysis_run_id") and item.get("analysis_run_id") != ref["analysis_run_id"]:
        errors.append("external source reference AnalysisRun identity mismatch")
    if ref.get("dataset_id"):
        known = {entry.get("dataset_id") for entry in package.get("datasets", [])}
        if ref["dataset_id"] not in known:
            errors.append("external source reference dataset_id is not present in imported package")
    if ref.get("summary_sha256") != item.get("summary_sha256"):
        errors.append("external source reference summary_sha256 mismatch")
    known_source_hashes = set()
    if item.get("source_sha256"):
        known_source_hashes.add(item["source_sha256"])
    known_source_hashes.update(item.get("source_hashes", []))
    for field in ("source_sha256", "source_hashes"):
        if field in ref:
            values = [ref[field]] if field == "source_sha256" else ref[field]
            if not isinstance(values, list) and field == "source_hashes":
                errors.append("source_hashes must be an array")
                continue
            for digest in values:
                if not isinstance(digest, str) or not HEX64.fullmatch(digest):
                    errors.append(f"{field} contains an invalid SHA-256")
                elif digest not in known_source_hashes:
                    errors.append(f"{field} contains a hash not declared for the referenced entity")
    if ref.get("artifact_ids") is not None:
        supplied = set(ref["artifact_ids"])
        available = set(item.get("source_artifact_ids") or [])
        if not supplied.issubset(available):
            errors.append("external source reference contains unknown source artifact IDs")
    if ref.get("observation_ids"):
        available = set(item.get("observation_ids", []))
        if not set(ref["observation_ids"]).issubset(available):
            errors.append("external source reference contains observation IDs not supplied by the package")
    if ref.get("operation_id") and item.get("operation_id") != ref["operation_id"]:
        errors.append("external source reference operation_id mismatch")
    return errors


def validate_external_registry(workspace: Path) -> list[str]:
    """Verify the manifest pointer, registered package identities and immutable package hashes."""
    errors: list[str] = []
    paths = workspace_paths(workspace)
    registry_file = registry_path(workspace)
    manifest = load_json(paths["manifest"], default={}) if paths["manifest"].is_file() else {}
    manifest_source = manifest.get("external_sources") or {}
    if not registry_file.is_file():
        if manifest_source or any(
            item.get("evidence_source") in {"STRUCTURED_ANALYSIS", "MIXED"}
            for item in load_json(paths["bundle"], default={}).get("result_units", {}).values()
        ):
            errors.append("External source manifest exists but state/external_sources/registry.json is missing")
        return errors
    try:
        registry = load_registry(workspace)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"External source registry cannot be read: {exc}"]
    packages = registry.get("packages", {}) if isinstance(registry, dict) else None
    if not isinstance(packages, dict):
        return ["External source registry packages must be an object"]
    if manifest_source:
        if manifest_source.get("registry_path") != "state/external_sources/registry.json":
            errors.append("State Manifest external_sources.registry_path does not match the workspace registry")
        if manifest_source.get("package_count") != len(packages):
            errors.append("State Manifest external_sources.package_count differs from the external registry")
        last_id = manifest_source.get("last_imported_package_id")
        if last_id and last_id not in packages:
            errors.append("State Manifest last_imported_package_id is absent from the external registry")
        elif last_id and manifest_source.get("last_imported_package_sha256") != packages[last_id].get("package_sha256"):
            errors.append("State Manifest last imported package hash differs from the external registry")
    workspace_root = workspace.resolve()
    for package_id, record in packages.items():
        if not isinstance(record, dict):
            errors.append(f"{package_id}: external registry package record must be an object")
            continue
        if record.get("evidence_package_id") != package_id:
            errors.append(f"{package_id}: registry package key/id mismatch")
        relative = Path(record.get("package_path", ""))
        package_file = (workspace / relative).resolve()
        if relative.is_absolute() or workspace_root not in package_file.parents:
            errors.append(f"{package_id}: imported package_path escapes the workspace")
            continue
        if not package_file.is_file():
            errors.append(f"{package_id}: imported package file is missing")
            continue
        digest = sha256_file(package_file)
        if digest != record.get("package_sha256"):
            errors.append(f"{package_id}: imported package file hash does not match external registry")
            continue
        try:
            package = json.loads(package_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{package_id}: cannot read imported package: {exc}")
            continue
        if not isinstance(package, dict):
            errors.append(f"{package_id}: imported package root must be an object")
            continue
        if package.get("evidence_package_id") != package_id:
            errors.append(f"{package_id}: imported package evidence_package_id mismatch")
        if (
            package.get("contract_id") != "scientific-evidence-export"
            or package.get("contract_version") != "1.0.0"
            or package.get("source_system") != "Data_analysis"
        ):
            errors.append(f"{package_id}: imported package exchange contract identity mismatch")
        categories = record.get("categories", {})
        if not isinstance(categories, dict):
            errors.append(f"{package_id}: registry categories must be an object")
            continue
        for entity_type, (collection, id_field) in CATEGORY_TYPES.items():
            registered_ids = categories.get(collection, [])
            package_ids = [item.get(id_field) for item in package.get(collection, [])]
            if registered_ids != package_ids:
                errors.append(f"{package_id}: registry {collection} identities differ from the stored package")
    return errors


def result_source_hashes(result: dict[str, Any], bundle: dict[str, Any]) -> set[str]:
    hashes: set[str] = set()
    source = bundle.get("source")
    if isinstance(source, dict) and HEX64.fullmatch(str(source.get("sha256", ""))):
        if result.get("evidence_source", "PDF_REPORT") in {"PDF_REPORT", "MIXED"}:
            hashes.add(source["sha256"])
    hashes.update(result.get("source_lineage_ids", []))
    for ref in result.get("external_source_refs", []):
        hashes.update(f"artifact:{item}" for item in ref.get("artifact_ids", []))
        value = ref.get("source_sha256")
        if isinstance(value, str) and HEX64.fullmatch(value):
            hashes.add(value)
        hashes.update(
            item for item in ref.get("source_hashes", [])
            if isinstance(item, str) and HEX64.fullmatch(item)
        )
    return hashes
