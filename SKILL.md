---
name: experiment-report-analyzer
description: Analyze one experimental-report PDF, mine traceable evidence, research the current literature frontier, propose distinct SCI research routes, and deliver a data-centric manuscript framework plus prioritized experiment/computation plan.
---

# Experiment Report Analyzer (ERA)

ERA accepts exactly one initial experimental-report PDF. The report may be incomplete, image-heavy, informal or scientifically unsystematic. The goal is to discover what the evidence actually supports, identify high-value scientific questions, and produce a literature-grounded research framework and follow-up plan.

## Operating model

- Python owns PDF fingerprints, physical Region/Panel anchors, permanent IDs, persistence, deterministic transformations and validation.
- The Agent owns qualified scientific interpretation, web/literature searching, route synthesis and manuscript planning.
- Humans own unresolved sample identity, scientific route selection and final approval. Never silently approve Gate A or Gate B.
- Full state stays on disk; use task-specific compact context to control token cost.
- Do not start hidden Workers or model jobs. Use the active host model unless explicitly authorized.
- For a requested one-pass deliverable, provide a provisional recommendation and continue planning. Keep both gates PENDING_HUMAN_REVIEW until an actual human decision is recorded.

## Implementation status

P0/P1 deterministic scripts cover PDF inventory, image extraction, spatial vector triage, repeated-layout triage, stable IDs, visual-inspection protocols, sample/evidence validation and compact context.

The later stages are Agent-executed workflows backed by persistent literature/route/framework bundles and deterministic validators. They are not an autonomous literature crawler or scientific truth engine. The Agent must actually search and verify literature using available web/search tools, and must state any inaccessible sources or unsupported stages.

## Scientific rules

1. Preserve the original PDF read-only and record SHA-256.
2. LLMs may reference only Python-issued IDs. Reserve IDs before writing entities.
3. Inspect images before captions/report narrative. If the active model has already seen the report text, record cognitive_blindness = NOT_GUARANTEED.
4. Keep FOUND, NOT_SHOWN, NOT_LEGIBLE, UNCERTAIN and NOT_APPLICABLE distinct.
5. Distinguish Exact_Text, Exact_Table, Vector_Extracted, Visual_Estimate, Qualitative_Observation and Unavailable.
6. Low-resolution plots never yield exact values. Visual estimates carry [Visual Estimate - Raw Data Required].
7. Keep Observed, Interpreted and Hypothesized separate from claim type (Descriptive, Comparative, Associational, Causal, Mechanistic).
8. Audit artifacts and confounders before promoting observations into interpretations. Missing metadata means not assessable, not proof of error.
9. Unconfirmed sample mappings cannot support causal, mechanistic or structure–property claims requiring sample identity.
10. Never infer unreported batches, runs, conditions, controls, raw data, replicate counts or material properties.
11. Literature access tiers are METADATA_ONLY, ABSTRACT_VERIFIED and FULLTEXT_VERIFIED. Never imply full-text review where only metadata/abstract was inspected.
12. Research gaps are bounded by actual search systems, dates, databases, terms and target systems. No search hit is not proof of novelty.
13. Metadata-only literature cannot substantiate scientific claims. Every literature claim references an exact snippet and source location.
14. Derived Data Units retain source lineage; multiple transformations from one Result Unit are not independent experiments.
15. Computations needing missing experimental structure/composition/model inputs must be BLOCKED_BY_EXPERIMENT.
16. Python validators check references and structure, not scientific truth, novelty or mechanism.
17. Student-facing messages are gentle, concrete and non-accusatory.

## Entry and commands

Read workflows/07_full_run.md first, then use workflows/01–06 at their respective stages. Load only relevant reference files.

    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v
    python scripts/ingest_pdf.py "REPORT.pdf" --workspace "WORKSPACE"
    python scripts/extract_regions.py --workspace "WORKSPACE"
    python scripts/build_contact_sheet.py --workspace "WORKSPACE"
    python scripts/validate_evidence.py --workspace "WORKSPACE"
    python scripts/validate_samples.py --workspace "WORKSPACE"
    python scripts/compile_prompt_context.py --workspace "WORKSPACE" --output "WORKSPACE/cache/prompt_context/evidence_context.md"
    python scripts/init_planning_bundles.py --workspace "WORKSPACE"
    python scripts/validate_planning.py --workspace "WORKSPACE"
    python scripts/validate_bundle_schemas.py --workspace "WORKSPACE"

For an existing workspace with the same PDF hash, use refresh_vector_candidates.py to update only page diagnostics; do not reset the Evidence Bundle or redo visual inspection.

For a capability-gated stage, fill templates/capability_profile.template.json using the exact active provider/model/version and evidence basis. Record it with record_capability_profile.py, then run check_capability.py for the intended task. Unknown values block high-risk tasks. Capability values are operator-attested, not benchmark results.

Reserve planning IDs through assign_planning_ids.py. Write permanent records through upsert_planning_entity.py, which checks the ID registry and appends an entity revision event. Do not manually mint IDs or overwrite full bundles. Run validate_planning.py and validate_bundle_schemas.py after each completed planning stage.

For visual inspection, prepare image-only task packs and record structured cards. One targeted automated reinspection per Region/Panel is allowed.

For vector-only figures, supply explicit page-coordinate BBoxes at a declared DPI. Semantic panel detection is not claimed. The spatial vector detector only prioritizes candidate pages. Repeated header/footer assets may be omitted from default Contact Sheets but are never removed from evidence; use --include-layout-assets to inspect them.

## Final deliverables

Produce:
- evidence report and sample/uncertainty inventory;
- literature frontier with bounded search scope, competitors, counter-evidence and verified citations;
- three distinct research routes where defensible, plus provisional recommendation;
- Claim–Evidence graph, Data Slot table, Data Units and lineage;
- conceptual figure/panel logic and section-by-section manuscript plan;
- English Introduction aligned with cited literature;
- prioritized experiment/analysis/theory/computation plan with controls and completion criteria;
- supportive student self-check message;
- validated editable Markdown and a verified PDF.

A package can be PARTIAL where evidence, access or prerequisites are insufficient. Never hide a blocker to make the output appear complete.
