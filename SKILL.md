---
name: experiment-report-analyzer
description: Develop an evidence-grounded, target-journal-aware SCI manuscript project package from an experimental-report PDF and associated research data, including the core contribution, Introduction, manuscript storyline, Figure/Panel and SI architecture, and assignable experiment/computation work packages.
---

# Paper_plan — Research-to-Manuscript Development

## Product objective

Paper_plan is a general Agent Skill for developing a research project into a coherent, reviewable manuscript-development package. It starts from the user's existing experimental report and associated data. It does not assume a scientific field, material, mechanism, instrument, journal, figure count or paper structure.

The product is not merely a PDF extractor, a literature summary, a generic research plan or an automatic paper writer. It must connect:

**existing evidence → research frontier → central contribution → target-journal positioning → Introduction → manuscript storyline → Figure/Panel and SI plan → experiment/analysis/computation work packages → integrated, validated project package.**

The Skill may identify that the available evidence does not yet support a defensible paper. In that case, it must explain the limitation and provide a bounded evidence-recovery or decision plan rather than manufacture novelty or a complete-looking story.

## Operating model

- Python owns source fingerprints, physical Region/Panel anchors, permanent IDs, persistence, deterministic transformations, schema checks and cross-reference validation.
- The Agent owns qualified scientific interpretation, live literature research, journal-instruction verification, contribution synthesis, story design and the detailed content of the work packages.
- Humans own unresolved sample identity, research-direction selection, journal positioning, framework approval and local laboratory/simulation decisions.
- Full state stays on disk. Compile only the task-specific context needed for each stage.
- Use the active host model unless the user explicitly authorizes another worker/job. Do not start hidden Workers or billable external work.
- A one-pass package may be provisional, but human approval fields remain pending until a human decision is actually recorded.
- Do not claim that schema validation proves scientific truth, novelty, causality or journal acceptance.

## Generality and project isolation

- This Skill must remain domain-neutral. Project-specific entities, values, sample names, equations, mechanisms, journal choices, figure layouts and conclusions belong only in that project's workspace.
- Never copy a prior project's observations, terminology, numeric values, literature list, mechanisms, Figure plan or journal requirements into SKILL.md, generic workflows, references, schemas, reusable templates or default configuration.
- Generic examples must use neutral synthetic labels and must not resemble a real user's project.
- A project run is a test instance, not a source of new generic facts. Promote a lesson into the Skill only after abstracting it into a domain-independent rule and testing it against multiple unrelated or synthetic scenarios.
- Keep one isolated workspace per research project and preserve all source data immutably. A primary report may be supplemented by user-provided native data, tables, images, methods and calculation outputs; inventory each source and its role.
- Never assume that every project needs the same number of routes, Figures, Panels, paragraphs, experiments, calculations or SI items.

## Scientific rules

1. Preserve original sources read-only and record hashes where possible.
2. LLMs may reference only Python-issued permanent IDs. Reserve IDs before writing entities.
3. Inspect visual evidence before relying on captions/narrative where practical. If the active model has already seen report text, disclose that cognitive blindness is not guaranteed.
4. Keep FOUND, NOT_SHOWN, NOT_LEGIBLE, UNCERTAIN and NOT_APPLICABLE distinct.
5. Distinguish exact text/table extraction, vector extraction, visual estimate, qualitative observation and unavailable data.
6. Low-resolution plots never yield exact values. Visual estimates carry an explicit raw-data-required warning.
7. Keep Observed, Interpreted and Hypothesized separate from claim type (Descriptive, Comparative, Associational, Causal, Mechanistic).
8. Every central quantitative metric should have a measurement definition and calculation lineage: measurand, signal, method, formula, units, normalization, blank/calibration, uncertainty and source data where known.
9. Audit artifacts, confounders, sample identity and comparison-condition compatibility before making causal or mechanistic interpretations.
10. Missing metadata means not assessable, not proof that an experiment was not performed.
11. Never infer unreported batches, runs, conditions, controls, raw data, replicate counts, equipment or material properties.
12. Literature access tiers are METADATA_ONLY, ABSTRACT_VERIFIED and FULLTEXT_VERIFIED. Do not imply full-text review where only metadata/abstract was inspected.
13. Research gaps are bounded by actual search systems, dates, databases, terms and target systems. No search hit is not proof of novelty.
14. Metadata-only literature cannot substantiate technical claims. Literature claims must reference verified snippets and source locations.
15. Derived Data Units retain source lineage. Multiple transformations from one Result Unit are not independent experiments.
16. Computations needing missing structure/composition/model inputs must be BLOCKED_BY_EXPERIMENT or an equivalent explicit blocker.
17. Target-journal requirements are volatile external facts. Verify current official instructions, record dated source links and mark unresolved items.
18. One central contribution should organize the manuscript. Supporting sub-contributions must strengthen that contribution; unrelated findings may be deferred.
19. Every Figure/Panel must have a scientific purpose, Claim/Data Slot links, evidence status, comparison logic and acceptance criteria.
20. Every essential unsatisfied Data Slot must map to a work package or an explicit reason not to pursue it.
21. Never prescribe local protocols, equipment, parameters, sample amounts, replicate counts or timelines without source evidence and local confirmation.
22. Student-facing messages must be supportive, concrete and non-accusatory.

## Entry and commands

Read workflows/07_full_run.md first. Use workflows/01–06 for evidence and research-frontier stages, then workflows/08–12 for journal positioning, argument, Figure/SI design, work-package handoff and product audit. Load only stage-specific reference files.

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
    python scripts/validate_manuscript_development.py --workspace "WORKSPACE" --deliverables-dir "WORKSPACE/deliverables"

For an existing workspace with the same source hash, refresh only the relevant diagnostics. Do not reset validated evidence or human decisions. Reserve IDs with assign_entity_ids.py / assign_planning_ids.py and persist entities through upsert_planning_entity.py. V4 manuscript entities include journal-source, introduction-paragraph, story-step, figure and si-item. Run the existing validators and the V4 manuscript-development validator after updating the package.

For visual inspection, prepare image-only task packs and record structured cards. One targeted automated reinspection per Region/Panel is allowed unless the governing project protocol explicitly permits otherwise.

## Required product coverage

Adapt the depth and exact file split to the project, but the integrated package must cover:

- evidence and source inventory, including uncertainty and calculation lineage;
- literature frontier, closest competitors, counter-evidence and bounded novelty;
- defensible candidate directions and one central contribution, or a reasoned stop decision;
- target-journal/article-type profile with current source references and unresolved requirements;
- Introduction paragraph architecture and evidence-linked English draft when justified;
- complete manuscript storyline with transitions;
- TOC/graphical abstract brief when relevant;
- main Figure and Panel specifications with data provenance and acceptance criteria;
- Supporting Information architecture;
- Claim–Evidence–Data Slot relationships;
- detailed experiment, analysis and computation work packages;
- dependencies, milestones, decision gates, student/supervisor checklists and risks;
- consolidated editable Markdown and verified PDF.

Do not force exactly three routes, any fixed Figure/Panel count, a three-paragraph Introduction, a standard instrument sequence or a mandatory computation section. Let evidence, scientific logic and verified journal instructions determine the package.

## Completion and validation

Run all applicable validators, review every warning and verify the final PDF is generated from the final Markdown revision. The final report must state source hashes, project/Skill versions, literature access levels, journal profile status, central contribution confidence, Figure/SI coverage, work-package closure, blocked calculations, human decisions, validation outcome and available usage deltas.

The result is a decision-ready manuscript-development package, not a guarantee of publishability or an automatically approved lab/computational protocol.
