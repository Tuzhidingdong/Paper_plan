#!/usr/bin/env python3
"""Import a Data_analysis Evidence Package without copying or registering raw data."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Any

from era_core import atomic_write_json, default_evidence_bundle, default_registry, ensure_workspace_dirs, sha256_file, workspace_paths
from external_evidence import CATEGORY_TYPES, registry_path

CONTRACT_ID = "scientific-evidence-export"
CONTRACT_VERSION = "1.0.0"
SOURCE_SYSTEM = "Data_analysis"
CATEGORIES = tuple(collection for collection, _ in CATEGORY_TYPES.values())


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _validate_package(package: dict[str, Any], schema_path: Path) -> list[str]:
    errors: list[str] = []
    if package.get("schema_version") != "1.0.0":
        errors.append("Data_analysis schema_version must be '1.0.0'")
    if package.get("contract_id") != CONTRACT_ID:
        errors.append(f"contract_id must be {CONTRACT_ID!r}")
    if package.get("contract_version") != CONTRACT_VERSION:
        errors.append(f"unsupported contract_version: {package.get('contract_version')!r}")
    if package.get("source_system") != SOURCE_SYSTEM:
        errors.append(f"source_system must be {SOURCE_SYSTEM!r}")
    if not isinstance(package.get("evidence_package_id"), str) or not package["evidence_package_id"].strip():
        errors.append("evidence_package_id is required")
    if not schema_path.is_file():
        errors.append(f"Evidence Package schema is missing: {schema_path}")
        return errors
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        from referencing import Registry, Resource
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        source_schema_path = schema_path.parent / "data_analysis_evidence_package.schema.json"
        if not source_schema_path.is_file():
            errors.append(f"Pinned Data_analysis Schema snapshot is missing: {source_schema_path}")
        else:
            source_schema = json.loads(source_schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(source_schema)
            source_ref = schema.get("allOf", [{}])[0].get("$ref")
            if source_ref != source_schema_path.name:
                errors.append("external Evidence Package Schema must reference the adjacent pinned data_analysis_evidence_package.schema.json using a relative local $ref")
            elif urlparse(source_ref).scheme or urlparse(source_ref).netloc:
                errors.append("Data_analysis Schema $ref must not use a remote URL")
            else:
                local_ref_uri = urljoin(schema["$id"], source_ref)
                resource = Resource.from_contents(source_schema)
                registry = Registry().with_resource(local_ref_uri, resource)
                if source_schema.get("$id"):
                    registry = registry.with_resource(source_schema["$id"], resource)
                validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
                errors.extend(
                    f"schema {'.'.join(str(part) for part in item.absolute_path) or '<root>'}: {item.message}"
                    for item in sorted(validator.iter_errors(package), key=lambda item: list(map(str, item.absolute_path)))
                )
    except ImportError:
        errors.append("jsonschema is required; install requirements.txt")
    except Exception as exc:
        errors.append(f"cannot validate Evidence Package schema: {exc}")
    count_fields = {
        "datasets": "dataset_count", "battery_reports": "battery_report_count",
        "statistics_reports": "statistics_report_count", "xrd_reports": "xrd_report_count",
        "xanes_reports": "xanes_report_count", "eis_reports": "eis_report_count",
        "cross_modal_reports": "cross_modal_report_count",
    }
    category_lengths: list[int] = []
    for collection, count_key in count_fields.items():
        items = package.get(collection, [])
        if isinstance(items, list):
            category_lengths.append(len(items))
            if package.get(count_key) != len(items):
                errors.append(f"{count_key} does not match {collection} length")
    if len(category_lengths) == len(count_fields) and not any(category_lengths):
        errors.append("Evidence Package must contain at least one non-empty evidence category")
    for entity_type, (collection, id_field) in CATEGORY_TYPES.items():
        values = [item.get(id_field) for item in package.get(collection, []) if isinstance(item, dict)]
        if len(values) != len(set(values)):
            errors.append(f"{collection} contains duplicate {id_field} identities")
    return errors

def _identity_and_hash_audit(package: dict[str, Any]) -> tuple[dict[str, list[str]], list[str], list[str]]:
    identities: dict[str, list[str]] = {name: [] for name in CATEGORIES}
    source_hashes: set[str] = set()
    warnings: list[str] = []
    for entity_type, (collection, id_field) in CATEGORY_TYPES.items():
        seen: set[str] = set()
        for item in package.get(collection, []):
            entity_id = item.get(id_field)
            if not isinstance(entity_id, str) or not entity_id.strip():
                warnings.append(f"{collection}: an entity has no usable {id_field}")
                continue
            if entity_id in seen:
                warnings.append(f"{collection}: duplicate {id_field} {entity_id}")
            seen.add(entity_id)
            identities[collection].append(entity_id)
            if item.get("source_sha256"):
                source_hashes.add(item["source_sha256"])
            for digest in item.get("source_hashes", []):
                source_hashes.add(digest)
            for field in ("source_sha256", "summary_sha256", "manifest_sha256"):
                value = item.get(field)
                if value is not None and (not isinstance(value, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", value)):
                    warnings.append(f"{collection}/{entity_id}: {field} is not a valid SHA-256")
        if len(seen) != len(package.get(collection, [])):
            warnings.append(f"{collection}: identity completeness/uniqueness requires review")
    if not any(package.get(collection) for collection in CATEGORIES):
        warnings.append("Evidence Package contains no registered entities")
    return identities, sorted(source_hashes), warnings


def import_package(workspace: Path, package_path: Path, schema_path: Path | None = None) -> dict[str, Any]:
    workspace = workspace.expanduser().resolve()
    package_path = package_path.expanduser().resolve()
    root = Path(__file__).resolve().parents[1]
    schema_path = schema_path or root / "schemas" / "external_evidence_package.schema.json"
    raw = package_path.read_bytes()
    try:
        package = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Evidence Package is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(package, dict):
        raise ValueError("Evidence Package root must be a JSON object")
    errors = _validate_package(package, schema_path)
    if errors:
        raise ValueError("Evidence Package rejected:\n- " + "\n- ".join(errors))
    package_id = package["evidence_package_id"]
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,160}", package_id):
        raise ValueError("evidence_package_id contains unsafe path characters")
    package_hash = _digest(raw)
    paths = ensure_workspace_dirs(workspace)
    registry_file = registry_path(workspace)
    registry = json.loads(registry_file.read_text(encoding="utf-8")) if registry_file.exists() else {
        "schema_version": 1, "source_system": SOURCE_SYSTEM,
        "contract_id": CONTRACT_ID, "contract_version": CONTRACT_VERSION, "packages": {},
    }
    existing = registry.setdefault("packages", {}).get(package_id)
    if existing:
        if existing.get("package_sha256") != package_hash:
            raise ValueError(
                f"package_id {package_id} already exists with a different SHA-256; "
                "the old version is preserved and overwrite is refused"
            )
        stored = workspace / existing.get("package_path", "")
        if stored.is_file() and sha256_file(stored) == package_hash:
            return {"status": "ALREADY_IMPORTED", "evidence_package_id": package_id,
                    "package_sha256": package_hash, "package_path": str(stored)}
        raise ValueError("registry points to a missing or hash-mismatched imported package; manual recovery is required")

    target_rel = Path("sources") / "data_analysis" / "packages" / package_id / package_hash / "evidence_package.json"
    target = workspace / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)

    identities, source_hashes, identity_warnings = _identity_and_hash_audit(package)
    category_ids = {collection: list(identities[collection]) for collection in CATEGORIES}
    limitations = [
        "Raw scientific data files are not copied, moved or re-registered by this importer.",
        "source_sha256 values are syntax-checked and retained; raw source bytes are not imported for byte-level re-hashing.",
        "summary_sha256 values are retained but the individual report/summary bytes are not embedded for independent re-hashing.",
        "Dataset summaries and descriptive statistics are not automatically promoted to scientific Result Units or Claims.",
        "Sample identity, experimental conditions, replicate identity and independence are not inferred from numeric similarity or filenames.",
    ]
    unverifiable = [
        "raw source file bytes and source_sha256 correspondence",
        "individual source summary/report bytes and summary_sha256 correspondence",
        "experimental/sample identity when not explicitly encoded",
        "observation-level identity where the package does not supply observation IDs",
        "independence of measurements unless explicitly declared in source records",
    ]
    record = {
        "source_system": SOURCE_SYSTEM, "contract_id": CONTRACT_ID,
        "contract_version": CONTRACT_VERSION, "evidence_package_id": package_id,
        "payload_schema_version": package.get("schema_version"),
        "package_sha256": package_hash, "package_path": target_rel.as_posix(),
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "status": "IMPORTED_STRUCTURAL_ONLY",
        "categories": category_ids, "source_hashes": source_hashes,
        "warnings": identity_warnings, "limitations": limitations,
        "unverifiable_fields": unverifiable,
    }
    registry["packages"][package_id] = record
    atomic_write_json(registry_file, registry)

    bundle_path = paths["bundle"]
    if not bundle_path.exists():
        atomic_write_json(bundle_path, default_evidence_bundle())
    id_registry_path = paths["registry"]
    if not id_registry_path.exists():
        atomic_write_json(id_registry_path, default_registry())
    manifest_path = paths["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {
        "schema_version": 1, "workspace_revision": "structured/1.0.0",
        "stage": "EVIDENCE_DRAFTED", "source_pdf": None, "pages": [],
        "region_count": 0, "panel_count": 0, "bundles": {"evidence_bundle.json": "HEAD"},
        "tools": {}, "validation": {"status": "NOT_RUN", "errors": [], "warnings": []},
        "capability_profile": None,
    }
    manifest["source_pdf"] = manifest.get("source_pdf")
    manifest.setdefault("external_sources", {})
    manifest["external_sources"].update({
        "registry_path": "state/external_sources/registry.json",
        "package_count": len(registry["packages"]),
        "last_imported_package_id": package_id,
        "last_imported_package_sha256": package_hash,
    })
    manifest.setdefault("bundles", {})["evidence_bundle.json"] = "HEAD"
    atomic_write_json(manifest_path, manifest)
    return {"status": "IMPORTED", "evidence_package_id": package_id,
            "package_sha256": package_hash, "package_path": str(target),
            "entity_counts": {key: len(value) for key, value in category_ids.items()},
            "warnings": identity_warnings, "limitations": limitations}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True, help="Data_analysis evidence_package.json with v1.0.0 contract envelope")
    parser.add_argument("--schema", type=Path, help="Optional compatible Evidence Package schema")
    args = parser.parse_args()
    try:
        result = import_package(args.workspace, args.package, args.schema)
    except Exception as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
