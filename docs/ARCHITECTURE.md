# Paper_plan V4 architecture

## Product architecture

Paper_plan has four connected layers:

1. Evidence layer: source reports and supplemental assets, Region/Panel anchors, Sample entities, Result Units, Findings, audits and uncertainty.
2. Research layer: literature search scope, access-tiered sources, literature claims, bounded gaps and candidate research directions.
3. Manuscript-development layer: target-journal profile, central contribution, Introduction paragraphs, storyline, Figure/Panel and TOC architecture, Supporting Information plan, and work packages.
4. Delivery/audit layer: editable reports, verified PDF, cross-bundle validation, human decision records and execution checklists.

## Data flow

    primary report + user-supplied supplemental research data
      -> immutable source inventory and hashes
      -> evidence extraction, visual triage and sample identity
      -> measurement definitions, condition-comparability checks, calculations and data lineage
      -> literature frontier and competing-study analysis
      -> defensible candidate directions and central contribution
      -> dated target-journal profile
      -> Claim–Evidence–Data Slot graph
      -> Introduction and manuscript storyline
      -> TOC + main Figure/Panel + Supporting Information architecture
      -> experiment / analysis / theory / computation work packages
      -> integrated plan, PDF and package audit

## Workspace bundles

- evidence_bundle.json: source references, regions, panels, samples, Result Units, Findings, inspections, audits and discrepancies.
- literature_bundle.json: search scope, access-tiered records, exact snippets, literature claims and bounded gaps.
- routes_bundle.json: candidate directions, supporting evidence, recommendation and human decision state.
- framework_bundle.json: Claims, Data Slots, Data Units, execution tasks and dependency links.
- manuscript_development_bundle.json: project profile, dated journal sources, central argument, Introduction paragraphs, storyline, TOC, main Figures, SI items, condition-comparability assessments, references to Claims/Data Slots/tasks, manuscript sections and deliverables.
- state_manifest.json: source hashes, workspace revision, stage, tool versions, bundle references and capability profile.

Search logs and entity revision history belong in append-only JSONL sidecars rather than prompt context.

## Permanent IDs and persistence

Python issues permanent IDs. V4 adds journal-source (JS), Introduction paragraph (IP), story step (STORY), Figure (FIG), Supporting Information item (SI) and comparability assessment (CMP). Existing Claim (C), Data Slot (DS), Data Unit (DU) and task (T) IDs remain in the framework bundle and are referenced by the manuscript-development bundle. Entity Upsert records revisions in the history log. No model-minted or recycled permanent IDs.

## Generality and isolation

Generic Skill sources contain procedures and schemas only. Every project's source material, names, measurements, sample labels, literature results, calculations, journal profile and planned Figure content remain in that project's workspace. No fixed Figure count, route count, paragraph count, method sequence or journal policy is imposed.

## Validation

The existing validators cover evidence/sample identity, literature provenance, routes, claims, Data Slots, Data Unit lineage and task dependencies. The V4 manuscript validator adds:
- journal-source/profile consistency;
- Introduction paragraph and citation references;
- storyline, Figure, Panel, Claim and Data Slot relationships;
- cross-sample/condition comparability records and Panel references;
- SI support relationships;
- essential missing-slot task closure;
- task dependency cycles and calculation input blockers;
- deliverable path and file checks;
- quality-review state consistency.

Structural validation does not establish scientific truth, research novelty or journal acceptance. Human decisions remain separate.

## V4.1 semantic controls

The framework Claim model distinguishes evidence-use roles and evidence assessments from epistemic status. Finding records can reference audit targets and contextual Result Units separately from supporting and contradictory observations. This prevents a measurement under examination from being mistaken for a verified result supporting the claim.

The manuscript validator reviews comparability semantics, repeated Data Slot use across Panels, structured work-package execution readiness and decision criteria for agreement/equivalence questions. The planning validator distinguishes execution, interpretation and publication prerequisites while retaining the legacy union.

Validation reports record currentness metadata (run time, Skill commit, validator/schema fingerprints and input-bundle hashes). A report is valid only for the exact versions it records.
