# Structured Evidence Integration Engineering Report

## 1. Baseline and delivery

- Repository: `Tuzhidingdong/Paper_plan`
- Original branch: `main`
- Original HEAD: `146cd26718d789584bd6059c195b9c77d780bb59`
- Development branch: `feat/structured-analysis-evidence-import`
- Final implementation/test commit validated by CI: `5749267caa8c2005b489737915a158946fb6dda4`
- Pull request: [#7](https://github.com/Tuzhidingdong/Paper_plan/pull/7), open against `main`; do not merge into `main`.
- CI run for the implementation/test commit: [ERA tests #44985405203](https://github.com/Tuzhidingdong/Paper_plan/actions/runs/44985405203), all matrix jobs passed.
- The report is finalized in a documentation-only follow-up commit after the successful implementation/test commit; the implementation files and tests are unchanged.

The work is limited to Paper_plan. No Data_analysis or Data_manager files are modified.

## 2. Data_analysis main-branch compatibility audit

Data_analysis `main` was inspected at `5684c6a762ac09caf24661c987b2e7a97eb0e2e7`.

The production schema is `schemas/evidence_package.schema.json`; the producer implementation is `src/data_analysis/evidence.py`. The producer returns `schema_version="1.0.0"`, `evidence_package_id`, category counts and arrays for datasets, battery, descriptive statistics, XRD, XANES, EIS and cross-modal reports. Existing source objects use fields including `dataset_id`, `analysis_run_id`, `cross_modal_evidence_id`, `operation_id`, `source_artifact_ids`, `source_sha256`, `summary_sha256`, `manifest_sha256`, warnings and limitations.

**Important compatibility boundary:** the inspected Data_analysis main branch does not emit `contract_id`, `contract_version` or `source_system`. Paper_plan therefore requires the user-specified v1.0.0 exchange envelope as top-level contract metadata, while validating the remaining payload against a vendored, unchanged snapshot of Data_analysis's current production schema. A separate, synthetic seven-category fixture demonstrates the agreed envelope; it is not represented as a production Data_analysis export. No producer fields were invented or written back to Data_analysis.

The original Data_analysis schema also requires `datasets.minItems=1`, while the builder implementation can be called with no dataset summaries when report files are provided. Paper_plan preserves and validates the schema as published rather than silently relaxing this production constraint. Such report-only packages need a producer-side schema/contract decision before being accepted.

## 3. Files changed and added

### Modified

- `SKILL.md` — adds PDF-only, structured-only and mixed operating modes, import/promotion rules and CLI guidance.
- `schemas/evidence_bundle.schema.json` — allows nullable PDF source, structured origin, NOT_APPLICABLE visual status, external references, explicit `source_lineage_ids` and conditional source-mode rules; legacy PDF mode remains the default.
- `schemas/state_manifest.schema.json` — allows `source_pdf: null` and adds external-source registry metadata.
- `scripts/era_core.py` — adds external-source/package workspace paths and structured-only defaults.
- `scripts/scientific_quality_gates.py` — handles a null PDF source without weakening existing visual checks.
- `scripts/assign_entity_ids.py` — reserves R IDs against either a real PDF Region or a verified external-source reference.
- `scripts/validate_evidence.py` — validates PDF / structured / mixed provenance, external package references, registry/package integrity and nullable PDF source workspaces.
- `scripts/compile_prompt_context.py` — compiles imported package summaries, provenance, methods/operations, warnings, limitations and unverifiable fields; null PDF source is safe.
- `scripts/validate_bundle_schemas.py` — validates the external-source registry and its manifest/package-count/hash cross-links when present or declared, without making it mandatory for PDF-only workspaces.
- `scripts/validate_planning.py` — flags shared raw-source hashes or explicitly shared artifact lineage IDs in a Data Unit so PDF and report views are not treated as independent measurements.
- `scripts/external_evidence.py` — resolves original entity IDs, checks package hash and entity/report identity, and validates imported Registry references and shared-source lineage.
- `scripts/extract_regions.py`, `scripts/segment_panels.py`, `scripts/refresh_vector_candidates.py` — make source metadata lookups null-safe for workspaces that do not carry an ingested PDF.

### Added

- `scripts/import_analysis_evidence.py`
- `scripts/external_evidence.py`
- `scripts/upsert_result_unit.py`
- `schemas/data_analysis_evidence_package.schema.json` — unchanged schema snapshot from Data_analysis main.
- `schemas/external_evidence_package.schema.json` — v1.0.0 exchange-envelope schema composed with the Data_analysis schema.
- `schemas/external_source_registry.schema.json`
- `workflows/13_external_structured_evidence.md`
- `tests/fixtures/structured_evidence/evidence_package.json` — fully synthetic package covering all seven categories.
- `tests/test_structured_evidence_import.py` — synthetic integration tests for import, identity, no-PDF and mixed modes.

## 4. External source registry

Registry path:

`WORKSPACE/state/external_sources/registry.json`

Each imported package is indexed by `evidence_package_id`, with a record containing:

- source system and contract ID/version;
- package ID and Data_analysis payload schema version;
- package-byte `package_sha256`;
- immutable relative path under `WORKSPACE/sources/data_analysis/packages/<package_id>/<package_sha256>/evidence_package.json`;
- import timestamp and structural-only status;
- category-to-original-entity-ID lists for all seven package categories;
- retained source hashes;
- warnings, limitations and fields that cannot be independently verified.

The State Manifest points to this registry and records its package count and most recently imported package ID/hash. The original package JSON bytes are stored unchanged. Only the Evidence Package is copied; raw scientific data files are not copied or registered.

Importing the same package ID and SHA-256 returns `ALREADY_IMPORTED`. A different SHA-256 under an existing package ID is rejected; the previous package is not overwritten.

## 5. Result Unit external-source reference

An external reference records:

- `source_system`, `contract_id`, `contract_version`;
- `evidence_package_id` and `package_sha256`;
- `entity_type`, `entity_id`;
- `analysis_run_id`, `dataset_id`, `artifact_ids`, `observation_ids`, `operation_id` only when the source explicitly supplies them;
- `source_sha256` or `source_hashes`;
- `summary_sha256`;
- copied `warnings` and `limitations`.

The validator resolves every structured reference against the imported registry, verifies the stored package-byte hash, locates the named entity in the original package category, and compares the source/summary digest and AnalysisRun/operation identity. Registry validation also checks that the State Manifest package count and last-imported pointer agree with the Registry, that every immutable package copy still matches its recorded hash, and that each category ID list still matches the stored package. Unknown Observation IDs are rejected rather than generated. Paper_plan IDs are allocated separately by its Python ID Registry.

## 6. PDF source optionality and workspace initialization

For structured-only projects, the importer creates an Evidence Bundle with `source: null`, a State Manifest with `source_pdf: null`, empty page/Region/Panel inventories and an external-source registry pointer. It does not fabricate a PDF path, filename, page count, file hash or Region ID.

PDF ingestion still writes its real `source` and `source_pdf` objects as before. Existing workspaces with populated PDF metadata and Region links keep those records. The schema validator treats the external registry as optional, so PDF-only workspaces do not need to create it. Context compilation and scientific quality checks now safely handle a null source.

## 7. Three modes

- **PDF-only:** legacy source default is `PDF_REPORT`; real Region/Panel and visual rules remain enforced.
- **Structured-only:** `STRUCTURED_ANALYSIS`; empty `region_ids`, at least one real imported external reference, `data_origin=Structured_Analysis`, `visual_legibility=NOT_APPLICABLE`, and no visual-estimate flag.
- **Mixed:** `MIXED`; both real PDF Region IDs and external source refs are required. Neither source is renamed or overwritten.

The importer registers the package only. Human/Agent selection is required before any Result Unit is created. A selected structured Result Unit receives an R ID via `assign_entity_ids.py` and is persisted by `upsert_result_unit.py`, which checks the registry allocation and external source refs.

## 8. Claim, Data Slot and Data Unit lineage

No new parallel claim/result database is introduced. A selected Result Unit enters the existing Paper_plan graph:

`Result Unit → Finding → Claim → Data Slot → Data Unit → Figure / SI → Work Package`

The existing Claim, Data Slot and Data Unit semantics are unchanged. Data Units continue to store `source_result_ids`, transformations and `independence_group_id`. The planning validator detects overlapping raw-source SHA-256 values and explicit source-lineage/artifact identifiers across their source Result Units and warns that these are one source lineage, not independent experiments. Paper Result Units may retain a source-confirmed `source_lineage_ids` list when a PDF Region and an external report demonstrably point to the same original measurement artifact. Numeric similarity does not create a sample, condition or replicate mapping. Discrepant values remain distinct and require review.

## 9. Tests

Targeted module command (for an isolated run):

`python -m unittest discover -s tests -p "test_structured_evidence_import.py" -v`

The module contains 12 synthetic integration test methods. All 12 ran and passed as part of the full-suite command in each successful CI matrix job; Actions did not run this module as a separate step. Coverage includes: all seven import categories, no automatic Result Unit promotion, package-byte hashing, idempotency and changed-content collision rejection, contract/schema/hash/duplicate-identity rejection, AnalysisRun/source/summary digest identity checks, tampered package detection, registry/manifest integrity, Python-issued R ID allocation and reserved-source persistence, structured Result Unit without Region, PDF Region requirement, mixed provenance, structured-only initialization/context compilation and shared artifact/source lineage.

Full regression command:

`python -m unittest discover -s tests -v`

<badge>Final CI: PASS</badge> 149/149 tests passed on each of Python 3.10, 3.11 and 3.12 (447 successful test executions across the matrix). This was GitHub Actions run [44985405203](https://github.com/Tuzhidingdong/Paper_plan/actions/runs/44985405203).

Compilation command:

`python -m compileall -q scripts tests`

Compilation passed on all three Python versions in the same run. Earlier CI attempts exposed two test-fixture setup errors; both were corrected before this final successful run. No local workstation test run is claimed. Schema validation is structural and is not scientific validation.

## 10. Backward compatibility and workspace protection

- Existing Result Units without `evidence_source` retain legacy PDF semantics.
- PDF Region IDs, page anchors, panel links, repeated-layout filtering, image-derived inspections, measurement definitions and calculation audits are not relaxed.
- The original Data_analysis Schema snapshot is stored separately from the exchange schema and is not modified.
- Existing state/bundle files are only initialized when missing; importer adds registry metadata without replacing an existing PDF source.
- Identical package imports are idempotent; differing content cannot silently replace a registered version.

## 11. Limitations and producer coordination

1. Data_analysis main must add the three agreed top-level exchange metadata fields before raw producer output is directly accepted without an envelope adapter.
2. Current Evidence Packages include digest strings but not the original raw data/report bytes; Paper_plan cannot recompute the underlying `source_sha256` or `summary_sha256` from the package alone. It verifies the exact package bytes and digest syntax/identity consistency, then records these limits.
3. The current package schema does not export stable Observation IDs. Paper_plan never fabricates them.
4. The published Data_analysis schema's `datasets.minItems=1` restriction conflicts with the builder's report-only call path and requires a Data_analysis-side schema/contract decision.
5. Sample identity, true experimental independence, sample pairing and condition comparability remain human scientific judgments unless explicit, source-linked information is supplied.
6. The GitHub Actions matrix is development self-check only; the user's synchronized local Skill and real workspace remain the final instance acceptance.
