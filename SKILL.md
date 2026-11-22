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
8. Every central quantitative metric must have a verified measurement definition and calculation lineage: measurand, raw signal, method, formula where derived, units, normalization, blank/calibration, uncertainty and parent/source data. The evidence validator blocks a numeric Result Unit marked CORE when this definition is absent or incomplete.
9. Audit artifacts, confounders, sample identity and comparison-condition compatibility before making causal or mechanistic interpretations. Cross-sample/condition comparisons must have a structured comparability assessment; unknown dimensions remain explicit.
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

## V4.1 scientific decision-quality rules

23. A Claim evidence reference distinguishes `SUPPORTS_CLAIM`, `CONTRADICTS_CLAIM`, `AUDIT_TARGET` and `CONTEXT_ONLY`. Legacy unlabelled direct Result Unit references default to supporting evidence. Finding-linked Result Units retain their typed list semantics.
24. Keep evidence assessment separate from epistemic status. Supported, partially supported, not established, not assessable, contradicted and inconclusive are distinct. A claim is CONTRADICTED only with explicit contradictory evidence; NOT_COMPARABLE, NOT_ASSESSABLE or missing metadata do not establish contradiction.
25. A quantitative Result Unit used as decision-bearing evidence for or against a central contribution must pass the CORE/VERIFIED gate. CORE means central to evaluating the claim, not necessarily favourable to it. AUDIT_TARGET and CONTEXT_ONLY remain distinct; a metric under audit may be essential to the research question without being treated as validated support or contradiction.
26. Distinguish COMPARABLE, CONDITIONALLY_COMPARABLE, NOT_COMPARABLE, NOT_ASSESSABLE and UNASSESSED. Record dimensions and inference limits. A comparison failure is not a counter-result.
27. Every Panel records applicable data scope (specimen/group set, condition, timepoint/stage, analysis population, processing level and source dataset IDs). Reuse of the same Data Slot is permitted when the scope differs or reuse is justified; ambiguous reuse is flagged for review.
28. Work packages distinguish planning readiness from execution approval. A task cannot be APPROVED_FOR_EXECUTION without human approval, confirmed local feasibility, available required inputs and documented local safety/feasibility review.
29. Agreement/equivalence questions require a suitable method, primary estimand, justified predeclared acceptance boundary, basis, assumptions and explicit supportive/contradictory/inconclusive outcome rules. Correlation alone is not agreement; never invent a threshold.
30. Classify task prerequisites as execution, interpretation and publication gates. Only execution prerequisites block task execution readiness; retain the legacy prerequisites list as their union.
31. Fingerprint integrated validator reports with UTC run time, Skill commit, validator/schema SHA-256 and input bundle hashes. A prior PASS is historical after any relevant input or code changes.

## V4.2 evidence-integrity and scientific reproducibility gates

32. A Result Unit's Region links must point to a usable physical evidence crop on the page cited by its source location. A repeated header/footer or decorative layout asset is not a scientific evidence anchor; the validator rejects it even when its Region ID exists.
33. Image-derived Result Units (`Visual_Estimate` and `Qualitative_Observation`) require a recorded caption-blind inspection linked to the actual Region or Panel. Inspection of a contact sheet or another page is not a substitute for a linked source crop.
34. A Claim that combines multiple image-derived Result Units must link a structured visual comparability assessment. Assess modality/acquisition, magnification or pixel size, scale-bar/spatial calibration, specimen state/preparation, image processing/contrast, and field selection/sampling. Record values or explicit unknowns for every compared entity. A mismatched or unknown visual dimension prohibits an unqualified COMPARABLE status and requires explicit limitations and prohibited inferences.
35. A derived Result Unit whose method is a fit/regression/least-squares model must include a source-linked calculation audit. For an OLS linear fit, link the x and y numeric observation vectors and the printed coefficient observation, then reproduce slope, intercept and R-squared. Tolerance is derived from the displayed decimal precision (half of the last printed unit), not chosen to make a result pass. A CORE statistical-fit result cannot pass without a reproducible audit; a failed or unavailable audit must remain non-core and explicitly qualified.
36. Measurement-definition verification and calculation reproducibility are separate checks. A measurand/method/formula can be sufficiently defined while a fitted relationship still fails reproduction or external validation. Do not describe a fit as validated merely because its measurement definition is VERIFIED.
37. When a preferred research route is nominated, record a structured route decision: selection criteria, evidence-based rationale, and a reasoned disposition for every non-selected candidate route. A route recommendation is not human approval; approval gates remain pending until a human decision is recorded.

## V4.3 measurement-validity controls

38. When a proxy, surrogate or indirect measurement is used as decision-bearing evidence for a target property, create an explicit proxy-to-reference validation design. Define candidate and reference measurands separately, including operational definition, method, units, reference basis and independence limitations.
39. Record sampling unit, pairing/matching, condition/time alignment and the scope of inference. Method-agreement or calibration claims require an appropriate paired or matched basis; an unpaired design must be justified and must narrow the claim.
40. For proxy validation, define the relationship type, primary estimand, analysis method, justified acceptance boundary and its basis, uncertainty approach, and explicit supportive, contradictory and inconclusive outcome rules. Never fabricate a decision margin.
41. Assess controls against the specific plausible confounders and artefacts. Declare required control classes and map them to planned controls; explain when no control or a candidate control is not applicable. Do not impose a fixed cross-domain control checklist.
42. Declare whether recovery, balance, conservation or another accounting-closure assessment is applicable. If required, specify inputs, outputs, residual method and justified acceptance basis; if not required, record why.
43. Distinguish in-sample reproduction, statistical-quality assessment, internal resampling, external independent validation and prospective validation. An external-validation label requires a separate validation scope, validation data, independence unit and leakage controls. A future prospective dataset requires a documented collection and separation plan; it is not yet observed validation evidence.
44. A deterministic gate can verify that a measurement-validation design is complete and internally consistent. It cannot prove the reference method is valid, the controls are sufficient, the acceptance boundary is appropriate, or the scientific relationship is true. Expert review and human approval remain required.

45. For every image-derived Result Unit, record during the original-resolution CAPTION_BLIND inspection a structured visual metadata assessment for modality, magnification/pixel size, scale/spatial calibration, specimen state/preparation, image processing/contrast and field selection/sampling. Each dimension must contain an observed value with source location/method/confidence or an explicit NOT_PRESENT, NOT_LEGIBLE, NOT_APPLICABLE or UNKNOWN state with a reason. A scale-bar value read from the crop is a human visual read, not an automatic image-reading claim. Later comparability assessments must reuse this provenance; never infer missing metadata from captions or other panels.

## Evidence source modes

Paper_plan supports three independent entry modes without making Data_analysis a dependency:

- **PDF-only:** retain the existing PDF ingestion, Region/Panel extraction, visual inspection and evidence workflow. Legacy Result Units without an explicit source mode are interpreted as `PDF_REPORT`.
- **Structured-only:** import a Data_analysis `evidence_package.json` using `scripts/import_analysis_evidence.py`. The importer registers the package and its provenance but never auto-creates Result Units, Findings or Claims. A structured-only workspace has `source: null`, `source_pdf: null`, no synthetic page count and no fabricated Region IDs.
- **Mixed:** preserve PDF and Data_analysis as separate source identities. A Result Unit marked `MIXED` must retain real PDF Region IDs and explicit external source references; never relabel structured results as PDF-extracted content.

The exchange envelope is `contract_id=scientific-evidence-export`, `contract_version=1.0.0`, `source_system=Data_analysis`. The imported package is retained byte-for-byte with its own SHA-256. Raw data files are not copied or registered. Package registration is not scientific interpretation: select individual entities only when relevant, allocate a Paper_plan Result Unit ID with `assign_entity_ids.py`, and persist it with `upsert_result_unit.py`. Structured Result Units use `region_ids: []`, `data_origin: Structured_Analysis` and `visual_legibility: NOT_APPLICABLE`, and must cite the exact imported package/entity/hash. Preserve report warnings and limitations. Do not infer sample identity, independent replicates or experimental conditions from numeric similarity.

Run `validate_evidence.py`, `validate_samples.py`, `validate_planning.py` and `validate_bundle_schemas.py` after mapping. Continue to use the existing Claim → Data Slot → Data Unit → Figure/SI → Work Package model; Data Units retain source Result Unit IDs and common source-lineage/independence groups. When documented, retain matching original source SHA-256 or exact shared artifact identifiers in `source_lineage_ids`; numeric similarity alone never establishes common lineage or independence. Schema PASS is structural only.

## Entry and commands

Read workflows/07_full_run.md first. Use workflows/01–06 for evidence and research-frontier stages, then workflows/08–12 for journal positioning, argument, Figure/SI design, work-package handoff and product audit. Load only stage-specific reference files.

    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v
    python scripts/ingest_pdf.py "REPORT.pdf" --workspace "WORKSPACE"
    python scripts/import_analysis_evidence.py --workspace "WORKSPACE" --package "evidence_package.json"
    python scripts/extract_regions.py --workspace "WORKSPACE"
    python scripts/build_contact_sheet.py --workspace "WORKSPACE"
    python scripts/validate_evidence.py --workspace "WORKSPACE"
    python scripts/validate_samples.py --workspace "WORKSPACE"
    python scripts/compile_prompt_context.py --workspace "WORKSPACE" --output "WORKSPACE/cache/prompt_context/evidence_context.md"
    python scripts/init_planning_bundles.py --workspace "WORKSPACE"
    python scripts/validate_planning.py --workspace "WORKSPACE"
    python scripts/validate_bundle_schemas.py --workspace "WORKSPACE"
    python scripts/validate_manuscript_development.py --workspace "WORKSPACE" --deliverables-dir "WORKSPACE/deliverables" --skill-commit "<CURRENT_SKILL_COMMIT>"

For an existing workspace with the same source hash, refresh only the relevant diagnostics. Do not reset validated evidence or human decisions. Reserve IDs with assign_entity_ids.py / assign_planning_ids.py and persist entities through upsert_planning_entity.py. V4 manuscript entities include journal-source, introduction-paragraph, story-step, figure, si-item and comparability. Run the existing validators and the V4 manuscript-development validator after updating the package.

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

46. Create each fitted Result Unit's source-linked calculation audit at the time the fit is extracted or calculated, not as a post hoc repair. Record an explicit `reproduction_status` (`REPRODUCED`, `NOT_REPRODUCED`, `NOT_ASSESSABLE` or `NOT_ASSESSED`) and require the deterministic validator to verify that label against recomputed coefficients and source precision. Keep statistical-quality diagnostics/uncertainty and internal/external/prospective validation in their separate fields; one status never substitutes for another.
