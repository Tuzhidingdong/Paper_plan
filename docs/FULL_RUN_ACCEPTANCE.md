# Full-run acceptance — Paper_plan V4 manuscript-development package

## Technical acceptance

- Source hashes and evidence provenance remain valid; originals are unchanged.
- Existing V3.3 extraction, identity, evidence and planning tests do not regress.
- The Manuscript Development Bundle is initialized without overwriting existing work.
- All V4 permanent IDs are Python-issued and upsert history is recorded.
- Manuscript JSON Schema is valid and representative package records conform.
- Journal source/profile status is coherent.
- Introduction paragraph, literature-claim and Claim references resolve.
- Storyline steps refer to valid Figures and Claims.
- Every central numeric Result Unit marked CORE has a verified measurement definition and parent/source calculation lineage.
- A comparison marked COMPARABLE contains no mismatched or unknown declared dimensions; comparative Panels link to a comparability assessment.
- Every main Figure has Panels, a take-home message and Claim/Data Slot links.
- Every Panel has purpose and acceptance criteria.
- SI items resolve their Claim/Figure/Data Slot references.
- Essential unsatisfied Data Slots have work-package coverage or an explicit no-task rationale.
- Work-package dependencies resolve and are acyclic.
- A calculation with missing required inputs cannot be READY or IN_PROGRESS.
- Deliverable paths remain workspace-relative; files marked FINAL exist.
- Final Markdown exports to PDF, which is reopened and checked for page count and expected text.
- Python 3.10, 3.11 and 3.12 CI matrix passes.

## Scientific/product acceptance

- The plan has one central contribution or an explicit stop/redirect recommendation.
- The contribution is bounded by the strongest competing literature and counter-evidence.
- The target-journal profile uses current official sources or clearly reports unresolved requirements.
- Introduction, storyline, Figures, SI, tasks and final plan express the same central argument.
- Figure count and arrangement follow the science and journal, not a fixed template.
- Every planned Panel identifies existing evidence or a missing Data Slot; no invented results.
- Supporting Information is linked to claims/Figures and does not conceal decisive missing evidence.
- Every proposed experiment/analysis/computation has a defined question, output and completion criteria.
- Computational tasks are handoff-ready and blocked when essential inputs are absent.
- Conditions, sample quantities, instruments, replicates and timelines are not invented.
- The package is usable by a supervisor to approve, reject or revise the direction and by a student/collaborator to understand assigned work.
- The Skill is evaluated using a fresh project without access to any prior project's source data or context.

## Generality / contamination acceptance

- Generic SKILL.md, README, workflows, references, schemas and default templates contain no real project-specific names, measurements, sample codes, equations, mechanisms, paper conclusions, source citations or figure layouts.
- Project-specific outputs stay in isolated workspaces.
- Synthetic tests use neutral data and do not encode any user's real experimental details.
- No fixed field-specific story, Figure count, route count, instrument sequence or journal policy is imposed.

## Verdict

Use PASS only when technical and product-level checks are complete and no critical contradiction remains. Use PASS_WITH_WARNINGS when a bounded package is useful but unresolved limitations remain. Use BLOCKED when the evidence, journal fit or execution prerequisites prevent a responsible plan. CI success alone is not product acceptance.
