"""Shared deterministic utilities for the ERA P0/P1 MVP.

Only the Python layer allocates permanent entity identifiers and writes HEAD state.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

EXTRACTOR_VERSION = "era-region-extractor/0.1.0"
BUNDLE_NAME = "evidence_bundle.json"
MANIFEST_NAME = "state_manifest.json"
REGISTRY_NAME = "id_registry.json"


# ---------------------------------------------------------------------------
# Quantitative-evidence semantics shared by every validator.
#
# A value is machine-readable only when it is carried by the structured fields
# ``numeric_value`` or ``numeric_values`` and parses to a finite number. Free
# text (descriptions, captions, sample labels, page numbers) is never scanned
# for numbers: prose digits are not a measurement declaration. A Result Unit
# may still be quantitative through its validated ``quantitative_permission``
# declaration, which records that exact values were transcribed even when no
# structured numeric field was populated.
# ---------------------------------------------------------------------------
_NUMERIC_STRING = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


def parse_numeric_scalar(value: Any) -> float | None:
    """Return a finite float for a number or a clean numeric string, else None.

    Rejects booleans, free text, identifiers and any non-finite value so that
    unrelated digits cannot be mistaken for a measurement.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        text = value.strip()
        if not _NUMERIC_STRING.fullmatch(text):
            return None
        try:
            number = float(text)
        except (ValueError, OverflowError):
            return None
        return number if math.isfinite(number) else None
    return None


def observation_numeric_values(observation: dict[str, Any]) -> list[float]:
    """Collect machine-readable measurement values carried by an observation."""
    if not isinstance(observation, dict):
        return []
    values: list[float] = []
    single = parse_numeric_scalar(observation.get("numeric_value"))
    if single is not None:
        values.append(single)
    for item in observation.get("numeric_values", []) or []:
        parsed = parse_numeric_scalar(item)
        if parsed is not None:
            values.append(parsed)
    return values


def observation_is_numeric(observation: dict[str, Any]) -> bool:
    return bool(observation_numeric_values(observation))


def result_has_machine_readable_number(result: dict[str, Any]) -> bool:
    return any(observation_is_numeric(item) for item in result.get("observations", []) or [])


def result_is_quantitative(result: dict[str, Any]) -> bool:
    """True when a Result Unit declares exact numeric evidence.

    Recognises two structured routes: a machine-readable value in an
    observation, or the validated ``quantitative_permission == Exact_Values``
    declaration. Description text is never scanned.
    """
    if result_has_machine_readable_number(result):
        return True
    return (
        result.get("quantitative_permission") == "Exact_Values"
        and bool(result.get("observations"))
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def workspace_paths(workspace: Path) -> dict[str, Path]:
    state = workspace / "state"
    extracted = workspace / "extracted"
    return {
        "workspace": workspace,
        "source": workspace / "source",
        "state": state,
        "history": state / "history",
        "registry": state / REGISTRY_NAME,
        "bundle": state / BUNDLE_NAME,
        "manifest": state / MANIFEST_NAME,
        "regions": extracted / "regions",
        "panels": extracted / "panels",
        "pages": extracted / "pages",
        "contact_sheets": extracted / "contact_sheets",
        "cache": workspace / "cache" / "prompt_context",
        "external_sources": state / "external_sources",
        "external_packages": workspace / "sources" / "data_analysis" / "packages",
    }


def ensure_workspace_dirs(workspace: Path) -> dict[str, Path]:
    paths = workspace_paths(workspace)
    for key in ("source", "state", "history", "regions", "panels", "pages", "contact_sheets", "cache", "external_sources", "external_packages"):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def default_evidence_bundle() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "workspace_revision": "0.1.0",
        "source": None,
        "regions": {},
        "panels": {},
        "samples": {},
        "result_units": {},
        "findings": {},
        "audit_records": [],
        "discrepancies": [],
        "visual_inspections": {},
    }


def default_registry() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "counters": {"REG": 0, "PANEL": 0, "S": 0, "R": 0, "F": 0},
        "anchors": {},
        "entities": {},
        "tombstones": [],
    }


@contextmanager
def registry_lock(registry_path: Path, timeout_seconds: float = 10.0) -> Iterator[None]:
    """Cross-platform best-effort lock using exclusive lock-file creation."""
    lock_path = registry_path.with_suffix(registry_path.suffix + ".lock")
    deadline = time.monotonic() + timeout_seconds
    descriptor = None
    while descriptor is None:
        try:
            descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(descriptor, str(os.getpid()).encode("ascii"))
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for ID registry lock: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def allocate_id(registry: dict[str, Any], prefix: str) -> str:
    if prefix not in registry["counters"]:
        registry["counters"][prefix] = 0
    registry["counters"][prefix] += 1
    width = 3
    return f"{prefix}{registry['counters'][prefix]:0{width}d}"


def register_anchor(
    workspace: Path,
    prefix: str,
    anchor_key: str,
    entity_type: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Register a Python-generated physical anchor idempotently."""
    paths = ensure_workspace_dirs(workspace)
    with registry_lock(paths["registry"]):
        registry = load_json(paths["registry"], default_registry())
        registry.setdefault("anchors", {})
        registry.setdefault("entities", {})
        registry.setdefault("tombstones", [])
        compound_key = f"{prefix}:{anchor_key}"
        existing = registry["anchors"].get(compound_key)
        if existing:
            entity = registry["entities"].get(existing, {})
            entity["last_seen"] = True
            registry["entities"][existing] = entity
            atomic_write_json(paths["registry"], registry)
            return existing
        entity_id = allocate_id(registry, prefix)
        registry["anchors"][compound_key] = entity_id
        registry["entities"][entity_id] = {
            "entity_type": entity_type,
            "anchor_key": anchor_key,
            "metadata": metadata or {},
            "status": "ACTIVE",
        }
        atomic_write_json(paths["registry"], registry)
        return entity_id


def register_named_sample(
    workspace: Path,
    exact_alias: str,
    source_ref: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Create/reuse a provisional Sample Entity from an explicit observed alias.

    The source reference prevents identical labels on unrelated pages from being
    silently merged. Human mapping can later relate aliases to a canonical entity.
    """
    normalized = re.sub(r"\s+", " ", exact_alias.strip().casefold())
    key_payload = f"{source_ref}|{normalized}".encode("utf-8")
    anchor_key = "sample-" + sha256_bytes(key_payload)[:20]
    return register_anchor(workspace, "S", anchor_key, "sample", metadata)


def make_region_anchor(
    source_sha256: str,
    page_number: int,
    bbox_normalized: list[float],
    pixel_sha256: str,
    extractor_version: str = EXTRACTOR_VERSION,
) -> str:
    rounded = [round(float(value), 5) for value in bbox_normalized]
    payload = {
        "source_sha256": source_sha256,
        "page_number": int(page_number),
        "bbox_normalized": rounded,
        "pixel_sha256": pixel_sha256,
        "extractor_version": extractor_version,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "region-" + sha256_bytes(encoded)[:24]


def normalize_bbox(bbox: tuple[float, float, float, float] | list[float], width: float, height: float) -> list[float]:
    x0, y0, x1, y1 = [float(value) for value in bbox]
    if width <= 0 or height <= 0:
        raise ValueError("Page width and height must be positive")
    if x1 <= x0 or y1 <= y0:
        raise ValueError("BBox must have positive width and height")
    values = [x0 / width, y0 / height, x1 / width, y1 / height]
    if values[0] < 0 or values[1] < 0 or values[2] > 1.0001 or values[3] > 1.0001:
        raise ValueError("BBox lies outside the page")
    return [round(value, 6) for value in values]


def load_evidence_bundle(workspace: Path) -> dict[str, Any]:
    paths = ensure_workspace_dirs(workspace)
    return load_json(paths["bundle"], default_evidence_bundle())


def save_evidence_bundle(workspace: Path, bundle: dict[str, Any]) -> None:
    paths = ensure_workspace_dirs(workspace)
    atomic_write_json(paths["bundle"], bundle)


def get_source_pdf(workspace: Path) -> Path:
    candidates = sorted((workspace / "source").glob("*.pdf"))
    if not candidates:
        raise FileNotFoundError("No source PDF found under workspace/source")
    if len(candidates) > 1:
        raise RuntimeError("Workspace must have exactly one initial source PDF")
    return candidates[0]
