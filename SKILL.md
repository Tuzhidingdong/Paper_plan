---
name: experiment-report-analyzer
description: Develop a complete V5 evidence-grounded, target-journal-aware manuscript-development dossier from existing research evidence, including a defensible contribution, connected manuscript argument, detailed Figure/Panel and SI architecture, and assignable experimental, analytical and computational work packages.
---

# Paper_plan — V5 Research-to-Manuscript Development

## Product objective

Paper_plan is a general Agent Skill for developing a research project into a coherent, reviewable manuscript-development package. It starts from the user's existing experimental report and associated data. It does not assume a scientific field, material, mechanism, instrument, journal, figure count or paper structure.

The product is not merely a PDF extractor, literature summary, validator report, structured bundle or automatic paper writer. It must connect:

**existing evidence → literature frontier → defensible central contribution → target-journal positioning → paragraph-level Introduction → connected manuscript storyline → TOC/Figure/Panel and SI architecture → assignable experiment/analysis/computation packages → prioritized integrated narrative plan.**

The integrated narrative plan is the researcher-facing product. Structured bundles provide provenance and machine-checkable state; they do not replace the scientific explanation, decisions or execution detail in the plan.

The Skill may identify that the available evidence does not yet support a defensible paper. In that case, it must explain the limitation and provide a bounded evidence-recovery or decision plan rather than manufacture novelty or a complete-looking story.

## Operating model

- Python owns source fingerprints, physical Region/Panel anchors, permanent IDs, persistence, deterministic transformations, schema checks and cross-reference validation.
- The Agent owns qualified scientific interpretation, live literature research, journal-instruction verification, contribution synthesis, story design and the detailed content of the work packages.
- Humans own unresolved sample identity, research-direction selection, journal positioning, framework approval and local laboratory/simulation decisions.
- Full state stays on disk. Compile only the task-specific context needed for each stage.
- Use the active host model unless the user explicitly authorizes another worker/job. Do not start hidden Workers or billable external work.
- A one-pass package may be provisional, but human approval fields remain pending until a human decision is actually recorded.
- Do not claim that schema validation proves scientific truth, novelty, causality or journal acceptance.

## V5 product rules — narrative plan is the product

- The controlling product contract is docs/V5_PRODUCT_CONTRACT.md, the controlling full-run workflow is workflows/13_v5_manuscript_development.md, and the researcher-facing writing rules are in docs/V5_1_RESEARCHER_FACING_DELIVERY_STANDARD.md. Use templates/V5_INTEGRATED_MANUSCRIPT_PLAN.md for the primary report and templates/V5_INTERNAL_PRODUCT_QA_REPORT.md only for the separate internal QA record. Also read docs/V5_1_SCIENTIFIC_MAINLINE_DECISION.md and docs/V5_1_LITERATURE_FRONTIER_PROTOCOL.md before a full project.
- Maintain two synchronized representations: structured bundles for provenance, IDs and cross-reference integrity; and a complete narrative plan for the researcher. The narrative is the delivered product. Structured JSON, validator reports and workflow-stage notes are supporting state only.
- Do not assemble the final plan by concatenating short bundle summaries. Explain scientific reasoning in connected prose, with detailed tables only where they help comparison or assignment.
- The primary deliverable must read like a professional scientific research proposal and manuscript-development dossier for supervisors, students and collaborators. It is not an Agent activity report, validator report, schema export or checklist.
- Keep all workflow stages, Skill/commit/runtime details, schema and bundle terminology, raw entity IDs, route enums, QA status codes, validator results and tool diagnostics in internal workspace records. Never append them to the researcher-facing plan. Translate genuine uncertainty into its scientific consequence, missing input, responsible source and next action.
- Perform explicit synthesis, narrative drafting, task-brief development and editorial-integration passes. Complete prose is required for the scientific rationale, literature position, Introduction, Results/Discussion storyline and task handoffs; tables support these sections but cannot substitute for them.
- A student-facing task must state its scientific purpose, starting inputs, design, controls, records to retain, analysis/QC, required return files, completion criteria, interpretation of alternative outcomes and manuscript use. Do not use internal task IDs as the task description.
- For substantive projects, cover research diagnosis, closest-literature comparison and bounded novelty, one central contribution, paragraph-level Introduction design, complete Results/Discussion storyline, TOC and Figure/Panel architecture, SI architecture, actionable experiment/analysis packages, relevant collaborator-ready theory/computation briefs, priorities, risks and supervisor decisions.
- Default to the user's language for the planning dossier. When the user works in Chinese, write the integrated plan in Chinese unless asked otherwise. Draft manuscript English only when sources support the claims and citations.
- Read the whole Markdown and PDF as a supervisor would and then as a student would; judge scientific reasoning, writing quality, Figure specificity, student handoff readiness and standalone usefulness against the V5 product contract and the researcher-facing delivery standard. Internal QA statuses and validator output must remain outside the primary report.
- Keep every V4.1–V4.3 scientific-integrity gate active. Never weaken evidence requirements, turn planned work into observed results or invent missing literature, values, protocols, conditions or thresholds.
- Evaluate the user's original scientific hypothesis as an explicit candidate alongside evidence-led alternatives. Do not automatically replace a scientifically meaningful line with a measurement/audit paper because evidence is incomplete; test whether a finite, feasible evidence-recovery path exists. A validation route becomes the main contribution only if it independently passes novelty/significance review.
- Never hard-code a project's scientific subject, samples, results, mechanisms, Figure scheme, literature or journal choices into reusable sources.

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
6. Low-resolution plots never yield exact values. Legible original-resolution figures may support bounded visual or semi-quantitative comparisons (for example relative trends, approximate positions or relative signal changes) without requiring native numeric data. Label such readings as image-derived estimates, state their reading basis, confidence and uncertainty, and limit precision to the axis and pixel resolution. Mark raw data as required only when the scientific question needs exact values or calculations that the supplied figure cannot support.
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

## General cross-result scientific analysis

After individual Result Units, sample associations, visual inspections and measurement definitions are recorded, and before literature/mainline synthesis, the Skill MUST complete the domain-neutral scientific-analysis stage defined in workflows/01_result_mining.md and references/scientific_analysis.md.

- Trigger this stage from the presence of Result Units, not from a user naming a technique, figure, sample pair or analysis checklist.
- During PDF extraction, preserve all vector-figure candidates detected in the page manifest. scripts/extract_regions.py must rasterize each candidate from its source PDF-coordinate BBox into an original-resolution, SHA-256-linked Region; each candidate remains pending until explicitly triaged.
- After Result Units are created, every vector-figure candidate must be dispositioned with scripts/record_figure_triage.py. Include actual scientific figures and link their Result Unit(s); exclude only demonstrably non-scientific/decorative candidates with an explicit reason. Unresolved or unlinked candidates are validation errors, not silent omissions.
- Use scripts/prepare_scientific_analysis.py to index every Result Unit, prepare joint analysis packs and expose unassigned Regions/Panels. Use scripts/record_scientific_analysis.py to validate and persist each structured result.
- The Agent must inspect the original-resolution assets and decide which relationships are scientifically meaningful. For plotted data, analyze actual signal features and changes within and across displayed series: positions, widths, intensities, areas, shapes, appearances/disappearances and trends only where the source supports them. The model selects relevant features from the evidence; no fixed technique checklist or expected peak list is imposed. Do not reduce analysis to generic assignments or captions.
- Record source-linked signal_features and signal_comparisons, preserving axes/units, series identity, measurement basis, normalization, resolution, precision and uncertainty. Visual estimates are allowed when legible, but may not claim precision beyond the plot; unresolved values remain unresolved. Interpretations must be separate from direct observations and include alternatives.
- Every image-derived Result Unit marked ANALYZED must have a model-invocation receipt confirming its original image asset was passed as a native image attachment. A path string is not image input. Store actual request/response artifacts and their SHA-256 values in the project workspace. If native attachment or invocation artifacts cannot be confirmed, mark affected Result Units NOT_ASSESSABLE.
- Treat program-generated relationship candidates as navigation hints, never as proof of scientific comparability. Discover scientifically useful links that the deterministic metadata index did not identify.
- For each comparison, assess relevant compatibility dimensions, source precision, normalization, calibration, measurement definitions and uncertainties. Keep direct observations, quantified/derived differences, interpretations and hypotheses separate; cite Result Units and physical Region/Panel sources.
- Every Result Unit must be covered exactly once in its analysis pack as ANALYZED, NO_COMPARISON_APPLICABLE or NOT_ASSESSABLE. The latter two require reasons. Preserve unassigned Regions/Panels as an explicit extraction coverage gap.
- Compile recorded analyses into the evidence context before the literature frontier and manuscript synthesis. The final researcher-facing plan must explain material cross-result findings, convergence, contradictions, alternative explanations and unresolved limits; do not merely list the internal records.
- Check the model's scientific_analysis capability profile before using multimodal analysis. If native high-resolution visual input, scientific reasoning, structured output or long-context consistency is not qualified, do not silently replace visual analysis with text-only summaries; mark affected evidence NOT_ASSESSABLE and explain why.
- Reuse same-source extraction and completed records. Do not start hidden workers, additional model providers or paid jobs. Preserve existing spectral_comparisons only for older-workspace compatibility; the general scientific_analyses workflow is authoritative for new projects.
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

## Entry and commands

For every full project, read workflows/13_v5_manuscript_development.md, docs/V5_PRODUCT_CONTRACT.md, docs/V5_1_RESEARCHER_FACING_DELIVERY_STANDARD.md, templates/V5_INTEGRATED_MANUSCRIPT_PLAN.md, templates/V5_INTERNAL_PRODUCT_QA_REPORT.md and docs/V5_1_NARRATIVE_PRODUCT_QA.md first; also follow docs/V5_1_LITERATURE_FRONTIER_PROTOCOL.md and docs/V5_1_SCIENTIFIC_MAINLINE_DECISION.md before completing their respective stages, using templates/V5_1_LITERATURE_FRONTIER_LEDGER.md for the project-specific search audit. workflows/07_full_run.md is a compatibility entry point to V5. Reuse workflows/01–06 and 08–12 as stage-specific technical procedures when the V5 runbook calls for them; do not treat their intermediate outputs as the final plan. Load only reference files needed for the current stage.

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
    python scripts/validate_manuscript_development.py --workspace "WORKSPACE" --deliverables-dir "WORKSPACE/deliverables" --skill-commit "<CURRENT_SKILL_COMMIT>"

For an existing workspace with the same source hash, refresh only the relevant diagnostics. Do not reset validated evidence or human decisions. Reserve IDs with assign_entity_ids.py / assign_planning_ids.py and persist entities through upsert_planning_entity.py. V4 manuscript entities include journal-source, introduction-paragraph, story-step, figure, si-item and comparability. Run the existing validators and the V4 manuscript-development validator after updating the package.

For visual inspection, prepare image-only task packs and record structured cards. One targeted automated reinspection per Region/Panel is allowed unless the governing project protocol explicitly permits otherwise.

## Required product coverage

Adapt the depth and exact file split to the project. The researcher-facing narrative must independently explain the scientific reasoning; do not satisfy this list by merely populating JSON fields. Use the V5 integrated-plan template and V5.1 researcher-facing delivery standard. The package must cover:

- evidence and source inventory, including uncertainty and calculation lineage;
- literature frontier, closest competitors, counter-evidence and bounded novelty;
- defensible candidate directions and one central contribution, or a reasoned stop decision;
- target-journal/article-type profile with current source references and unresolved requirements;
- Introduction paragraph architecture and evidence-linked English draft when justified;
- complete manuscript storyline with transitions;
- TOC/graphical abstract brief when relevant;
- main Figure and Panel specifications with data provenance and acceptance criteria;
- Supporting Information architecture;
- clear relationships between important scientific claims and their source evidence, expressed in readable language;
- detailed student-/collaborator-ready experiment, analysis and computation briefs;
- dependencies, milestones, scientific decision points, responsibilities and risks;
- a complete researcher-facing Markdown report and matching verified PDF; keep literature ledgers, structured bundles and internal QA/run metadata as separate supporting records.

Do not force exactly three routes, any fixed Figure/Panel count, a three-paragraph Introduction, a standard instrument sequence or a mandatory computation section. Let evidence, scientific logic and verified journal instructions determine the package.

## Completion and validation

Run applicable validators, review warnings and verify that the PDF is generated from the final Markdown revision. Record source hashes, project/Skill versions, literature access, journal-profile status, structural validation, tool limitations and other run details in the separate internal QA/run record. Do not put these technical details into the researcher-facing plan.

The result must be a complete, supervisor-reviewable and team-assignable scientific report. It is not a guarantee of publishability or an automatically approved lab/computational protocol. Product acceptance requires human inspection of the complete Markdown/PDF against the product contract and any available project benchmark; tests and validators alone are insufficient.

46. Create each fitted Result Unit's source-linked calculation audit at the time the fit is extracted or calculated, not as a post hoc repair. Record an explicit `reproduction_status` (`REPRODUCED`, `NOT_REPRODUCED`, `NOT_ASSESSABLE` or `NOT_ASSESSED`) and require the deterministic validator to verify that label against recomputed coefficients and source precision. Keep statistical-quality diagnostics/uncertainty and internal/external/prospective validation in their separate fields; one status never substitutes for another.


47. Treat every user-supplied or project-mentioned literature citation, author/year clue, DOI/title fragment and bibliography entry as a lead requiring documented identity resolution. One failed query or provider error is not enough to declare it unlocated; preserve ambiguous/unresolved leads and their effect on novelty.
48. Stress-test atomic novelty propositions against the closest primary literature using adversarial query variants. Distinguish established principles, incremental extensions, potentially distinct contributions and unassessable claims; a new combination of known factors is not automatically novel.
49. A novelty-critical source inspected only at metadata/abstract level cannot support conclusions about details not present there. If direct competitors or critical leads remain inaccessible/unresolved, constrain the gap and mainline decision accordingly.
50. Main-text Figures must carry the central manuscript argument. Data extraction/transcription audits, fit-reproduction diagnostics and general QC normally belong in SI unless their result is itself a central contribution; the Figure portfolio must agree with the stated route selection.
51. Align title, contribution sentence, abstract map, Figure messages and conclusions with evidence status. Do not assert planned outcomes, phase identity, purity, mechanism, causality, structural incorporation/removal or application performance before the necessary evidence exists.
52. Where source acquisition, preparation, handling, preprocessing, storage, transfer or measurement may alter the property or phenomenon being evaluated, require an appropriate preservation/stability or process-effect assessment, or mark the inference blocked. Do not assume an input-processing step leaves the studied state unchanged.
53. Map every decision-relevant alternative explanation/confounder to a control, measurement or explicit inference limitation. Matching one condition does not automatically isolate other coupled variables.
54. Where relevant, state the operational scale and resolution of a measurement and the scale of the claim. Do not generalize across spatial, temporal, population, aggregation or system levels without an explicit sampling, modelling or inference bridge.
55. Separate the minimum discriminating test from the full publication-strength program. Prioritize the smallest feasible experiment/reanalysis/calculation that can change the mainline decision, then expand only for claims it unlocks.
56. Apply docs/V5_1_NARRATIVE_PRODUCT_QA.md to the actual Markdown and same-revision PDF. Report product quality, scientific readiness and benchmark-comparison status separately; template completion, PDF length, tests and validators do not certify the narrative product.

57. Select HYBRID only when its components form one logically interdependent scientific argument with a stated shared central question. Do not use HYBRID as a compromise between disconnected stories or as a way to retain unrelated results; distribute main-text sections, Figures and tasks in proportion to their role in the central contribution.


58. When a project benchmark is required, extract its complete quality criteria and map each to the new plan; transfer only domain-neutral quality expectations, never its scientific facts or default settings. If the required benchmark is unavailable, do not claim complete comparison or overall product acceptance.
