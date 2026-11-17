# P0/P1 MVP acceptance and full-plan handoff

This document preserves the original deterministic PDF/evidence acceptance boundary. The full research-plan workflow is specified in workflows/07_full_run.md.

## Local setup

    py -3.11 -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v

## P0/P1 commands

    python scripts/ingest_pdf.py "D:\path\to\student_report.pdf" --workspace ERA_Workspace
    python scripts/extract_regions.py --workspace ERA_Workspace
    python scripts/build_contact_sheet.py --workspace ERA_Workspace
    python scripts/validate_evidence.py --workspace ERA_Workspace
    python scripts/validate_samples.py --workspace ERA_Workspace
    python scripts/compile_prompt_context.py --workspace ERA_Workspace --output ERA_Workspace/cache/prompt_context/evidence_context.md

For an existing workspace with the same PDF SHA-256, use refresh_vector_candidates.py to update the vector diagnostics without resetting evidence. Contact Sheets omit repeated top/footer layout assets by default; use --include-layout-assets to inspect everything.

## Planning handoff

    python scripts/init_planning_bundles.py --workspace ERA_Workspace
    python scripts/check_capability.py --workspace ERA_Workspace --task literature_screening
    python scripts/validate_planning.py --workspace ERA_Workspace
    python scripts/validate_bundle_schemas.py --workspace ERA_Workspace

Allocate all permanent literature, route, claim, Data Slot, Data Unit and task IDs with assign_planning_ids.py. Persist each entity through upsert_planning_entity.py. Read workflows/07_full_run.md for the complete literature, research-route, experiment-plan, Introduction and PDF deliverable workflow.

## Adversarial acceptance

- Dense vector plots mixed with raster banners are flagged for review.
- Sparse decorative lines are not independently enough to trigger vector review.
- Repeated raster header/footer assets are hidden only from default triage sheets, never deleted from evidence.
- Unknown model capabilities block high-risk tasks.
- Metadata-only literature cannot substantiate a literature claim.
- Dangling IDs, evidence citations, Data Slot references and task dependencies are rejected.
- A required experiment blocks a dependent calculation until its prerequisite is completed.
- Duplicate Data Units derived from the same Result Unit are warned as one evidence lineage.

Deterministic tests do not prove scientific competence. The active model's exact provider/version and its actual search/visual capabilities must be recorded for the local run.
