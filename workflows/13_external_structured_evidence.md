# 13 — External Structured Scientific Evidence

## Objective and boundaries

Receive a Data_analysis Evidence Package as an additional, optional evidence source. This workflow does not replace the Paper_plan PDF extraction pipeline and does not make Data_analysis a runtime dependency. It registers source evidence; it does not decide which records are scientifically relevant or convert every summary into a manuscript result.

The supported exchange envelope is:

- `contract_id`: `scientific-evidence-export`
- `contract_version`: `1.0.0`
- `source_system`: `Data_analysis`

The payload follows the Data_analysis `schemas/evidence_package.schema.json` snapshot shipped with this Skill. The importer also checks package `schema_version=1.0.0`. Do not invent or add production fields to Data_analysis entities. The three envelope fields are exchange-contract metadata, not replacements for Data_analysis's existing package fields.

## 1. Choose the entry mode

### A. PDF-only

Continue workflows 01–12 exactly as before. Run `ingest_pdf.py`, extract physical Regions and Panels, record caption-blind inspections where required, and validate the Evidence Bundle. Historical Result Units that do not specify `evidence_source` remain PDF_REPORT and retain mandatory Region checks.

### B. Structured-only

1. Receive the single exported `evidence_package.json` from the user.
2. Import it:

   ```bash
   python scripts/import_analysis_evidence.py --workspace WORKSPACE --package evidence_package.json
   ```

3. The importer validates the envelope, Data_analysis payload schema, category counts, entity identities and declared digest formats. It computes SHA-256 over the exact package bytes and stores an immutable package copy at `WORKSPACE/sources/data_analysis/packages/<package_id>/<package_sha256>/evidence_package.json`.
4. It writes `WORKSPACE/state/external_sources/registry.json` and a State Manifest pointer. It initializes an Evidence Bundle with `source: null` only when no bundle exists. It does not create PDF metadata, page records, Regions, Result Units, Findings or Claims.
5. Initialize the ordinary planning bundles and run applicable checks:

   ```bash
   python scripts/init_planning_bundles.py --workspace WORKSPACE
   python scripts/validate_evidence.py --workspace WORKSPACE
   python scripts/validate_bundle_schemas.py --workspace WORKSPACE
   python scripts/compile_prompt_context.py --workspace WORKSPACE --output WORKSPACE/cache/prompt_context/evidence_context.md
   ```

6. Review the complete package registry and compiled context. Preserve import warnings, QC warnings, limitations and unverifiable fields. A dataset summary or descriptive statistic is not automatically a scientific discovery.

### C. PDF + structured sources

Run the regular PDF ingestion and extraction, then import the Evidence Package into the same workspace. Keep `Evidence Bundle.source` and State Manifest `source_pdf` bound to the real PDF, and retain the Data_analysis package under the external-source directory. The compiler shows both sources separately. Do not overwrite one source with the other.

## 2. Select evidence before creating a Result Unit

Inspect the package categories independently:

- `datasets`
- `battery_reports`
- `statistics_reports`
- `xrd_reports`
- `xanes_reports`
- `eis_reports`
- `cross_modal_reports`

Select only an entity that is relevant to the current paper question and whose evidence scope can be described accurately. Record whether it is a source dataset summary, analysis report or cross-modal report. Preserve the Data_analysis package ID, entity ID, AnalysisRun ID when supplied, Dataset ID when supplied, Artifact IDs when supplied, operation ID, source digest(s), summary digest and package digest. Do not fabricate Observation IDs: the current Evidence Package schema does not export them.

Prepare an external-source-reference JSON object with the exact values taken from the imported package and registry, including:

```json
{
  "source_system": "Data_analysis",
  "contract_id": "scientific-evidence-export",
  "contract_version": "1.0.0",
  "evidence_package_id": "<registered package ID>",
  "package_sha256": "<registered package digest>",
  "entity_type": "<dataset or report category>",
  "entity_id": "<source Dataset ID or report AnalysisRun/cross-modal ID>",
  "analysis_run_id": "<only when the source report supplies one>",
  "dataset_id": "<only when explicitly supplied>",
  "artifact_ids": [],
  "source_sha256": "<only when supplied>",
  "summary_sha256": "<source entity summary digest>",
  "operation_id": "<only when supplied>",
  "warnings": [],
  "limitations": []
}
```

This is a shape guide, not a source of default IDs or scientific facts. Omit fields that the source does not provide. For an entity with multiple source hashes, use `source_hashes` instead of inventing one `source_sha256`. Copy warning and limitation text without softening it.

## 3. Allocate and persist a selected Result Unit

For a structured-only result, reserve an R ID through the Python registry using the reference file:

```bash
python scripts/assign_entity_ids.py --workspace WORKSPACE result-slot --external-source-ref-json external_ref.json --slot-index 1
```

For PDF or mixed results continue using `--parent-region-id` with a real registered Region. Build the Result Unit JSON with the returned Python-issued ID, then persist it through:

```bash
python scripts/upsert_result_unit.py --workspace WORKSPACE --entity-json result_unit.json --reason "Human/Agent-selected source evidence for this manuscript question"
```

Structured-only Result Units set:

- `evidence_source: STRUCTURED_ANALYSIS`
- `region_ids: []` (no synthetic Region IDs)
- `data_origin: Structured_Analysis`
- `visual_legibility: NOT_APPLICABLE`
- `is_visual_estimate: false`
- one or more verified `external_source_refs`

They still require epistemic status, measurement context, observation records, quantitative permission and the applicable measurement definition / calculation lineage. A descriptive parser summary must not be promoted to a CORE scientific metric without a verified measurement definition and domain-appropriate QC. Do not infer sample IDs or repeat identity.

A combined Result Unit uses `evidence_source: MIXED` and must contain both real PDF Region IDs and verified external source refs. Keep the origin of each measurement explicit; a Data_analysis report is never described as if it had been extracted from a PDF Region.

## 4. Rejoin the existing scientific argument system

After a selected Result Unit passes the evidence validator, use the existing graph:

`Result Unit → Finding → Claim → Data Slot → Data Unit → Figure / SI → Work Package`

Claims and Data Slots keep their existing semantics. Data Units retain their source Result Unit IDs, transformation, exclusions and `independence_group_id`. If a PDF Result Unit and a Data_analysis report cite the same original source SHA-256 or the same explicitly documented source artifact ID, preserve that common lineage and do not count the pair as independent experiments. Store a source-backed common identifier in the Result Unit's `source_lineage_ids` (for example, the exact artifact ID supplied by the source); the importer derives artifact lineage only from source-declared `artifact_ids`. Never manufacture a shared ID or infer identity from numeric similarity.

If two source paths disagree, keep both identities and values, record a discrepancy/audit target and request scientific review. Do not silently choose a winner or overwrite a source record.

## 5. Idempotency, integrity and limitations

- Re-importing the same package ID and exact byte hash is idempotent.
- Reusing a package ID with a different byte hash is rejected; the previous version remains untouched.
- Source IDs remain Data_analysis IDs. Paper_plan R/F/C/DS/DU identifiers remain Python-issued Paper_plan IDs.
- Only the Evidence Package JSON is copied. Raw source data are not copied, moved or re-registered.
- The importer can verify package-byte SHA-256 and the internal consistency of supplied IDs/digest fields. It cannot recompute a raw source-file hash or each summary/report hash unless those source bytes are supplied separately.
- Schema and provenance PASS does not establish scientific validity, measurement fitness, causal interpretation or independence.

## 6. Validation

Run the applicable Evidence, sample, planning and schema validators. PDF Regions, page consistency, repeated-layout checks and image-derived visual-inspection requirements remain mandatory whenever a Result Unit uses PDF evidence. Structured-only Result Units bypass only those visual checks that are not applicable; quantitative measurement, calculation lineage, QC, source-reference and scientific-quality gates remain active.
