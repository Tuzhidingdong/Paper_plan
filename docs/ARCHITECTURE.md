# ERA V3.3 architecture

## Principles

- One initial PDF source.
- Python owns physical evidence anchors, permanent IDs, persistence, bundle validation and repeatable transformations.
- The Agent owns scientific interpretation, current literature searching, route synthesis and manuscript planning.
- Humans own ambiguous sample identity and final scientific decisions.
- Full state remains on disk; prompt context is task-specific.
- Raw evidence is immutable; derived records are versioned and retain lineage.

## Data flow

    PDF
     -> ingestion and page inventory
     -> embedded raster extraction + vector candidate triage
     -> explicit vector crop and panel registration where needed
     -> image-first visual pass
     -> caption/text comparison
     -> Result Units, Sample Entities and artifact/confounder audit
     -> evidence validation
     -> literature frontier and verified citation claims
     -> three candidate research routes
     -> Claim–Evidence graph and Data Slots
     -> Data Units and dependency-aware execution tasks
     -> Introduction, manuscript framework and research-plan export

## HEAD-only bundles

1. evidence_bundle.json: source references, regions, panels, samples, Result Units, Findings, inspections and audits.
2. literature_bundle.json: search scope, access-tiered literature records, exact snippets, literature claims and bounded gaps.
3. routes_bundle.json: candidate routes, supporting evidence, recommendation and Gate A decision state.
4. framework_bundle.json: claims, Data Slots, Data Units, tasks, sections, figure plan, Introduction and Gate B state.
5. state_manifest.json: source, workspace revision, stage, tool versions, bundle references and capability profile.

Search logs and entity revision history belong in append-only JSONL sidecars rather than full prompt context.

## Stable IDs and lineage

Python creates physical Region anchors from source PDF SHA-256, page, normalized BBox, pixel SHA-256 and extractor version. Similarity hashes are hints only. The registry allocates and reuses IDs; deleted IDs are tombstoned, never recycled. Planning IDs are reserved using a stable semantic anchor key. LLMs may reference IDs but may not mint them.

A Data Unit records all source Result Unit IDs and transformations. Multiple derived views of one source do not become independent experiments.

## Visual and layout triage

Vector candidates are selected from central-page spatial clusters and chart-like drawing primitives. Full-page drawing BBox is diagnostic only. Candidate flags are not semantic chart labels.

Repeated near-identical top/footer image blocks are labelled as layout assets for default Contact Sheet suppression. They remain in the Evidence Bundle and can be included explicitly.

Image-first inspection precedes caption/report-text extraction. If the model context has already seen the narrative, cognitive independence is not guaranteed and must be declared.

## Capability and validation

The active model provider, exact model ID/version, capabilities and evidence basis are recorded per workspace. Unknown capability blocks the associated high-risk task. This is operator-attested, not a model benchmark.

Deterministic validation is layered:
- evidence provenance, source hash, Region/Sample IDs and numeric permissions;
- sample mapping and conditional Micro-Gate;
- Draft 2020-12 JSON Schema validation;
- cross-bundle citation, route, claim, Data Slot, Data Unit lineage and task dependency validation.

None of these checks proves a scientific mechanism or novelty claim.
