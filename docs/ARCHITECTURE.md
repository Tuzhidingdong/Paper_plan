# ERA V3.2 architecture

## Principles

- One initial PDF source.
- Python owns region anchors, permanent IDs, persistence and deterministic validation.
- Agent owns qualified scientific interpretation and literature reasoning.
- Humans own ambiguous identity confirmation and final research decisions.
- Full state remains on disk; prompt context is task-specific.
- Raw evidence is immutable; derived records are versioned.

## Data flow

```text
PDF
 └─ ingest and page inventory
     └─ raster region extraction / vector-region review
         └─ Figure and Panel registration
             └─ caption-blind visual inspection
                 └─ separate caption and narrative extraction
                     └─ Evidence Bundle
                         ├─ sample mapping
                         ├─ instrument checklist
                         ├─ artifact/confounder audit
                         └─ Observed / Interpreted / Hypothesized
```

## HEAD-only bundles

1. evidence_bundle.json: source references, regions, panels, samples, Result Units, findings and audits.
2. literature_bundle.json: later literature records, claims, snippets, gaps and retrieval references.
3. routes_bundle.json: later research routes and Gate A decision.
4. framework_bundle.json: later claims, Data Slots, Data Units, tasks and Gate B state.
5. state_manifest.json: workspace revision, stage, schema versions, hashes and capability status.

History and raw search responses belong in append-only JSONL sidecars, not the HEAD bundles.

## Stable anchors

Python creates a physical region anchor from source PDF SHA-256, page number, normalized BBox, pixel SHA-256 and extractor version. Perceptual hashes are similarity hints only; never merge regions from perceptual similarity alone.

The ID registry is Python-owned. Repeated extraction reuses known anchor mappings. New IDs are allocated atomically. Deleted IDs are tombstoned and never recycled. LLMs may reference existing IDs but may not choose permanent IDs.

## Sample representation

Use a simple Sample Entity with aliases, optional preparation-condition dictionary, optional batch note and identity status. Put Measurement Context inside each Result Unit. Each independently labeled curve/series may have its own sample association. Do not infer separate batches or measurement runs unless explicitly identified.

## Evidence state

Epistemic status: Observed / Interpreted / Hypothesized.
Data origin: Exact_Text / Exact_Table / Vector_Extracted / Visual_Estimate / Qualitative_Observation / Unavailable.
Visual legibility: High / Medium / Low / Unassessable.
Quantitative permission: Exact_Values / Trend_Only / Qualitative_Only / None.

Checklist state: FOUND, NOT_SHOWN, NOT_LEGIBLE, UNCERTAIN, NOT_APPLICABLE. NOT_SHOWN is scoped to the inspected figure, not the whole report.

## Later-stage contracts

Research frontier, route generation, Data-centric framework, human revision and final deliverables are documented but not implemented in this MVP.
