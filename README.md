# Paper_plan — Experiment Report Analyzer (ERA)

ERA is an evidence-driven Agent Skill that starts from one potentially unstructured experimental-report PDF and develops a traceable research opportunity, a data-centric SCI manuscript framework, and a prioritized experimental/analytical/computational execution plan.

## Current capability

**ERA V3.3 — Evidence Mining + Agent-executable Research Planning**

### Deterministic Python layer
- PDF fingerprint, page inventory and immutable source preservation.
- Embedded raster-image Region extraction with stable Python-owned anchors.
- Vector-figure candidate detection using page-body spatial clusters and primitive types; candidates still require human review.
- Explicit PDF-coordinate BBox rendering for vector-only figures and explicit panel registration.
- Repeated near-identical header/footer asset hints; these assets remain preserved but are excluded from default triage sheets.
- Caption-blind task packs, inspection records and one-reinspection gate.
- Sample entities, evidence provenance and numeric-permission validation.
- Python-issued planning IDs for literature, gaps, routes, claims, Data Slots, Data Units and tasks.
- Planning bundle initialization, cross-bundle provenance/dependency validation and JSON Schema validation.
- Model capability profile recording and fail-closed checks for high-risk stages.
- Markdown-to-PDF export through installed Edge/Chrome, with page/text verification.

### Agent-executed scientific layer
- Three-stage literature frontier review: terminology, primary competitors, counter-evidence.
- Three genuinely distinct research routes and a provisional recommendation.
- Claim–Evidence graph, Data Slots, Data Units and conceptual figure/section architecture.
- Prioritized experiment, analysis and conditional theory/computation plans.
- English Introduction draft and student-facing self-check message.
- Consolidated editable Markdown and verified PDF research plan.

The literature and scientific reasoning are executed by the host Agent using its available search/reasoning tools. Python validates provenance and structure; it does not independently prove novelty, causality or scientific mechanisms. Gate A and Gate B remain PENDING_HUMAN_REVIEW until a human actually decides.

## Quick start

Python 3.10+ is required.

    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v

Run the full workflow from repository root:

    python scripts/ingest_pdf.py path/to/report.pdf --workspace ERA_Workspace
    python scripts/extract_regions.py --workspace ERA_Workspace
    python scripts/build_contact_sheet.py --workspace ERA_Workspace
    python scripts/validate_evidence.py --workspace ERA_Workspace
    python scripts/validate_samples.py --workspace ERA_Workspace
    python scripts/compile_prompt_context.py --workspace ERA_Workspace --output ERA_Workspace/cache/prompt_context/evidence_context.md
    python scripts/init_planning_bundles.py --workspace ERA_Workspace
    python scripts/validate_planning.py --workspace ERA_Workspace
    python scripts/validate_bundle_schemas.py --workspace ERA_Workspace
    python scripts/export_plan_pdf.py ERA_Workspace/deliverables/FINAL_RESEARCH_PLAN.md

Follow workflows/07_full_run.md for the complete Agent sequence, literature verification, route synthesis and final deliverables. Use scripts/assign_entity_ids.py and scripts/assign_planning_ids.py for all permanent IDs, then scripts/upsert_planning_entity.py to persist one entity with a JSONL revision event. For an existing same-hash workspace use scripts/refresh_vector_candidates.py; do not reset its evidence.

## Scientific boundaries

- The original PDF and extracted source regions are immutable evidence.
- A vector candidate flag is only a prompt for visual review, not automatic chart recognition.
- Repeated layout images are never deleted or merged; triage hints only affect default Contact Sheets.
- Low-resolution visual estimates are never represented as exact numeric measurements.
- Missing information in the report does not prove that an experiment was not performed.
- Unconfirmed sample mappings cannot support causal or structure–property claims.
- The model must not invent instrument settings, sample identities, raw data, literature evidence, novelty or calculation inputs.
- Literature access levels are explicit: metadata, abstract or full text actually inspected.
- Derived views of one Result Unit are not independent experiments.
- Computations requiring unavailable experimental structures/models are BLOCKED_BY_EXPERIMENT.
- Student self-check messages must be gentle and non-accusatory.

See docs/IMPLEMENTATION_STATUS.md for the boundary between deterministic code and Agent-executed scientific work.
