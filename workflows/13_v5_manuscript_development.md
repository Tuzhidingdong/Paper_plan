# 13 — V5 Full Manuscript-Development Workflow

## Authority

This is the controlling V5 workflow for a full Paper_plan project. Workflows 01–06 and 08–12 remain reusable technical procedures. Existing Python tools and V4.1–V4.3 integrity gates remain active.

The goal is one integrated, supervisor-reviewable and team-assignable manuscript-development plan grounded in the user's actual research. The narrative plan is the first-class deliverable; structured bundles are its traceability layer.

Read docs/V5_PRODUCT_CONTRACT.md, docs/V5_1_RESEARCHER_FACING_DELIVERY_STANDARD.md, templates/V5_INTEGRATED_MANUSCRIPT_PLAN.md, docs/V4_PRODUCT_CONTRACT.md, docs/V5_1_LITERATURE_FRONTIER_PROTOCOL.md, docs/V5_1_SCIENTIFIC_MAINLINE_DECISION.md and docs/V5_1_NARRATIVE_PRODUCT_QA.md. Also read templates/V5_INTERNAL_PRODUCT_QA_REPORT.md for the separate internal review record. Load only stage-specific procedures and references.

## Stage 0 — Intake and workspace protection

Confirm project objective, the user's original scientific intent/hypothesis, scope and preferred plan language. Record the target journal/article type only from this current project's explicit user input or an explicit current test-run configuration, and record its provenance. A journal mentioned only in a benchmark, prior project, previous run or memory is not inherited as the current target. If none is specified, use the journal-selection procedure without silently choosing one. Default to the user's language (Chinese where the user works in Chinese); write English manuscript prose only when evidence and citations support it. Inventory all supplied reports, SI, native data, images, methods, calculations and notes. Record hashes and paths where possible; preserve originals read-only. Use an isolated workspace. Do not overwrite old V4/V4.3 runs or human decisions. Reuse extraction only when source hashes and provenance match. Record Skill commit and known model/tool limitations. Do not start hidden Workers or billable jobs. Ask only essential questions; otherwise preserve unknowns explicitly.

## Stage 1 — Scientific evidence base

Follow workflow 01 and applicable visual/data procedures. Reuse exact-source extraction and run relevant existing evidence, sample, measurement and schema checks.

Create a scientific evidence map of actual systems/samples/conditions; principal measured/derived quantities and definitions; strongest observations and source locations; uncertainty, inconsistent labels/values, missing controls, artifacts and comparability limits; hypotheses not yet established; and evidence essential to decide the central question.

Explain what the evidence collectively says, what it does not say and why. Do not turn a list of Result Units into the scientific narrative. Keep all V4.1–V4.3 controls active; an audit target is not silently promoted to validated support.

Before proceeding to the literature frontier or central-contribution decision, complete the mandatory general scientific-analysis stage in workflow 01. It must analyze the full Result Unit set as a connected dataset, including relevant within-result series and between-result relationships. The model, not the user, selects scientifically meaningful comparisons from the evidence. Record source-linked observations, comparability assessments, quantitative/qualitative differences, cross-result convergence or contradiction, interpretations, alternatives and per-Result-Unit coverage. Do not treat independently described figures as completed scientific synthesis. Every Result Unit must be ANALYZED, explicitly NO_COMPARISON_APPLICABLE or NOT_ASSESSABLE. Compile the analysis records into the context used for Stage 2 onward. A missing or capability-blocked analysis must constrain the scientific claims and be reported honestly; do not bypass the Skill with an ad hoc manual analysis.

**Evidence-to-argument distillation is mandatory before Stage 2.** Read `references/scientific_argument_synthesis.md`. Review the analysis packs together, including cross-pack candidate relationships after evidence review. Distil only material patterns, comparisons, interpretations and contradictions into Findings. Each analysis-derived Finding must cite exact `analysis_id`, `record_type` and stable `record_id` values in `scientific_analysis_refs`, and preserve supporting/contradictory Result Units, alternative explanations and inference limits. Do not turn every observation or metadata link into a Finding.

## Stage 2 — Literature frontier

Read and follow `docs/V5_1_LITERATURE_FRONTIER_PROTOCOL.md`, plus relevant stage-specific literature procedures. Build query facets from this project's actual system, mechanism, transformation, methods and vocabulary. Use templates/V5_1_LITERATURE_FRONTIER_LEDGER.md to retain a project-specific search-route, exact-query, citation-lead resolution, citation-trail and closest-prior-art audit. Keep the completed ledger under the isolated workspace and reference its path from the narrative plan. Use independent discovery routes and backward/forward citation trails; a failed or empty search endpoint is not a stopping condition.

Record routes, query families, dates, access tiers, publication status and source locations. Identify the primary studies most capable of defeating candidate novelty claims. Compare actual systems, transformation direction, medium/conditions, mechanisms, impurity/structure roles, observables, demonstrated findings and limitations. Include contradictory and inconvenient sources.

Do not substitute a bibliography, search snippet or metadata-only record for a nearest-prior-art comparison. Each gap statement must link relevant sources and be classified as supported, provisional or not established. When a provider returns no result, retry alternate terminology/formulas, publisher/DOI lookup and citation chasing.

## Stage 3 — Scientific-mainline and central-contribution decision

Read and follow `docs/V5_1_SCIENTIFIC_MAINLINE_DECISION.md`. Recover the user's original scientific problem and hypothesis from the current project's own inputs before selecting a paper story. Preserve it as an explicit candidate even when evidence is incomplete. Compare it with materially different evidence-led alternatives, an independently defensible method/measurement contribution where relevant, and a stop/defer option. Candidate count is project-dependent.

Use the nearest-prior-art evidence from Stage 2. Compare candidates on significance, precise difference from closest work, supporting/counter-evidence, mechanistic/causal adequacy, alternative explanations, falsifiability, decisive evidence-recovery needs, feasibility/dependencies and current-project journal fit. Do not use pseudo-precise scores.

For every serious candidate route, trace its supporting and contradictory Findings back to the exact scientific-analysis records. Multi-Result-Unit routes should cite the analysis-derived Findings that establish the proposed relationship; a list of independently supportive Result Units is not itself a cross-result scientific argument.

Do not pivot automatically from the user's intended scientific contribution to a validation/audit paper merely because the current dataset lacks decisive measurements. Determine whether a finite, feasible evidence-recovery path can test the original line and whether it remains differentiated from prior work. A validation route becomes the central contribution only if it independently passes the significance and prior-art test; otherwise it remains a supporting task.

Recommend RECOMMENDED, CONDITIONAL, HYBRID, FALLBACK or STOP/DEFER. For every serious non-selected candidate, explain why it was deferred/rejected and what could revive it. For the selected line, state the one-sentence contribution, boundary, support, strongest challenge, decisive missing evidence, outcomes that change the decision and human decision pending.

## Stage 4 — Journal/article-type fit

Follow workflow 08. Verify current official journal/publisher requirements and record URL, access date, source type and supported requirement. Assess audience/scope fit, contribution type, evidence maturity, article type, manuscript structure, Figure/TOC/SI restrictions, reference style and relevant data/reporting policies.

Do not infer requirements from old papers or memory. Unknowns remain unresolved. Explain how journal fit affects the architecture. If no target journal is supplied for this current project, do not silently choose one or inherit it from a benchmark; ask, keep unresolved, or produce a conditional analysis as appropriate. A benchmark's journal applies only when this exact run explicitly identifies it as target-journal input for this test case.

## Stage 5 — Introduction

Design the actual paragraph sequence from the selected contribution and literature. Do not impose a fixed paragraph count.

For every paragraph state rhetorical role, reader-facing message, factual premise and verified literature support, limitation/tension motivating the next paragraph, transition, project evidence/citation still needed and readiness. Draft coherent English prose when supported. Do not polish unverified technical claims; use explicit placeholders for inaccessible/unverified citations. Narrow from the real field problem to the closest literature limitation, precise unresolved question and bounded contribution.

## Stage 6 — Complete storyline

Create an ordered Results/Discussion sequence. For each section or major paragraph cluster state the scientific question; evidence/data and status; responsible observation; interpretation/inference strength; plausible alternative/limitation; role in the central thesis; and transition to the next section. For cross-result conclusions, identify the argument-bearing Finding and its underlying analysis records; preserve the distinction between an observed pattern, its interpretation and a proposed mechanism.

Explain why each result is needed and why it appears there. Order by logic of proof and reader comprehension, not instrument or file order. Provide a working title, abstract argument map and conclusion architecture. Draft full text only when the evidence and claim boundaries are ready.

## Stage 7 — TOC, Figures and Panels

Follow workflow 10. Derive Figure number/order from the story; do not impose fixed counts.

For every Figure specify its take-home message, argument role, manuscript destination and Panel sequence. For each Panel specify question; exact content; source files/Regions/Result Units/Data Slots and status; existing/reprocessed/new/blocked state; groups/conditions/controls/comparison basis; analysis/statistics/axes/units/annotations where known; intended and prohibited inferences; linked tasks/SI; and scientific acceptance criterion.

A missing-data Panel may be PLANNED or BLOCKED, but its purpose and required evidence must be concrete. Never present an expected result as observed. Provide a TOC/graphical-abstract concept only when journal/story requires or benefits from it; label concept versus artwork accurately.

## Stage 8 — Supporting Information

For each SI Text/Table/Figure specify identifier/title, exact contents, source or producing task, current status, why it belongs in SI, related main-text claims/Figures/Panels and uncertainty/QC addressed.

Do not fill a conventional count or move decisive evidence to SI to hide a main-text weakness.

## Stage 9 — Work packages and handoffs

Follow workflow 11. Derive tasks from claim risk, Data Slots, Figure needs and scientific decisions, not generic technique lists.

For every experiment/reanalysis/data-audit task state question and rationale; claim/Figure/Panel/SI affected; exact inputs and missing requirements; variables/groups/conditions/comparison unit; design/method/controls and justified replicate/statistical considerations; raw/processed outputs; provenance/QC/uncertainty/completion criteria; interpretations under supportive, negative, mixed and inconclusive outcomes; dependencies/blockers/priority/role.

For relevant theory/computation specify scientific question/inference; model/system construction and source structures/composition; required inputs; relevant states/charges/boundaries/conditions only where known; method/rationale; known settings versus TBD; convergence/sensitivity plan; physical observables/output files; controls/alternative models; experimental validation and limits; Figure/Panel/Claim/SI destinations; and prerequisites/blockers. A method name alone is not a handoff. Do not force DFT/MD or any method where it adds no decision value.

## Stage 10 — Prioritize

Order verification/reanalysis, experiments/controls, theory/computation, Figure/TOC/SI preparation and writing as appropriate. For every action state deliverable, priority reason, prerequisite, decision unlocked and completion/stop condition. Identify parallel tasks. Do not invent dates/durations.

## Stage 11 — Produce the researcher-facing scientific plan

Follow docs/V5_1_RESEARCHER_FACING_DELIVERY_STANDARD.md and use templates/V5_INTEGRATED_MANUSCRIPT_PLAN.md as a writing guide. The template is not the report: remove all instructional text and replace prompts with fully developed project-specific reasoning.

The main deliverable is a professional research proposal and manuscript-development dossier for the principal investigator, students and collaborators. It must not read like an Agent execution log, structured-data summary, quality-control report or software-development document.

### 11.1 Synthesize before drafting

Build an internal synthesis linking the research materials, evidence, literature frontier, central question, complete manuscript argument, Figures, SI and research tasks. Resolve inconsistencies and identify missing logical connections before writing. Use structured bundles and identifiers for traceability; do not paste their contents into the narrative. Explicitly trace the decisive argument from source evidence through analysis records and Findings to Claims, candidate contribution and manuscript sections. Check that supporting and contradictory evidence has not been lost between stages.

### 11.2 Write the scientific rationale and current research basis

Explain the scientific field problem, why it matters, the limitations of existing knowledge and how the user's research addresses the gap. Interpret the actual findings as a coherent body of evidence. Explain their source, conditions, reliability, scientific meaning and limitations. Do not write a bare inventory of extracted values or instruments.

### 11.3 Write the literature argument

Synthesize the research frontier in connected prose. Discuss the closest primary studies and explain what each has established, how their systems and findings compare with the current project, and what precise contribution remains plausible. Use a comparison table only as a supplement to the explanation. Keep exact queries and citation trails in the separate literature ledger.

### 11.4 Develop the manuscript, not just its outline

Provide a meaningful working title and abstract argument. Design the Introduction paragraph by paragraph, including verified support, rhetorical purpose and transitions. Draft coherent manuscript-ready English prose when source evidence permits; do not leave only a paragraph-role table or generic citation placeholders.

Build Results/Discussion as a connected sequence of scientific questions and answers. For every section explain why it appears at that point, the evidence it will use, the comparisons and controls needed, the inference it can support, the main alternative interpretation and how it advances the central argument. Planned results must remain clearly planned.

### 11.5 Design the visual argument

Derive the Figure portfolio from the scientific story. For each Figure state the reader-facing message and argument role. For every Panel give the exact data or conceptual content, source and availability, groups/conditions, comparison, proposed visual form, axes/units/normalization, statistical and uncertainty presentation where appropriate, intended and prohibited inference, layout considerations, and link to the manuscript section and producing task.

Diagnostic audits, extraction/transcription checks and general quality-control material normally belong in SI unless they are central scientific findings. Explain the actual contents and purpose of each SI item.

### 11.6 Design assignable research tasks

Write complete student/collaborator briefs for every decision-critical experiment, reanalysis, data acquisition or characterization task. A brief must explain its scientific purpose, starting inputs, missing prerequisites, design and comparison basis, controls, practical considerations, records to retain, analysis and QC, required return files, completion criteria, alternative outcomes and manuscript use.

Separate the minimum work needed to decide whether the central question is viable from the additional evidence needed for a full publication-strength paper. Do not compress high-priority tasks into a one-line list. Do not invent local operating conditions, sample amounts, replicate counts or thresholds; state who must confirm them.

### 11.7 Provide computation handoffs only when they add scientific value

When relevant, give the computational collaborator the model question, construction strategy, required structures/compositions, assumptions, conditions, method rationale, parameters that are known versus unresolved, convergence/sensitivity checks, observables, raw/processed output files, validation against experiment and the specific paper claim/Figure served. A method name alone is not a handoff.

### 11.8 Edit for the reader

Perform a full editorial pass after all sections are drafted:

- remove repeated content, filler and disconnected topic lists;
- make the scientific argument and section transitions explicit;
- ensure every main Figure, SI item and task contributes to the same central paper;
- translate missing inputs and uncertainty into understandable scientific consequences;
- remove unexplained internal IDs, route enums, QA statuses, validator results, tool names, schema/workflow terminology, Skill versions, commit SHAs and worktree paths;
- distinguish existing results from hypotheses and planned work throughout;
- use descriptive titles and task names instead of software identifiers.

The final Markdown should read as a complete professional scientific plan. If it still consists mainly of short bullets, empty headings, status labels, task IDs or structured tables without interpretation, continue drafting and integration before export.

## Stage 12 — Independent product review and delivery

Read the complete final Markdown as a supervisor and then as a student receiving an assignment. Apply docs/V5_1_NARRATIVE_PRODUCT_QA.md to the actual Markdown and the PDF exported from that same revision.

### 12.1 Review the main product

Check the scientific rationale, evidence interpretation, literature synthesis, central contribution, Introduction prose, Results/Discussion logic, Figure/Panel design, SI contents, task briefs, computational handoffs, execution order, clarity and editorial integration. Confirm that the report stands alone without opening JSON bundles or development logs.

### 12.2 Keep internal QA separate

Create `WORKSPACE/internal/PRODUCT_QA_REPORT.md` using templates/V5_INTERNAL_PRODUCT_QA_REPORT.md. Record product-quality, scientific-readiness and benchmark-comparison outcomes separately, together with gate findings and technical validation.

The internal QA report is not part of the researcher-facing plan. Do not append its statuses, validator summaries, workflow notes or Skill metadata to the Markdown or PDF. Benchmark unavailability blocks a claim of benchmark comparison but does not automatically lower the plan's intrinsic product quality; assess the report against the product contract independently.

### 12.3 Export and verify

Export the PDF from the final Markdown revision using scripts/export_plan_pdf.py. Verify the PDF's text extraction, page structure, tables and visual presentation. Reopen the PDF and confirm that the same content is present without truncation, blank pages, missing sections or layout failures.

### 12.4 Deliver

The researcher-facing deliverables are the integrated Markdown plan and its matching PDF, plus scientific appendices that genuinely help the research team (for example, literature ledger, detailed evidence register or collaborator input files). Keep logs, raw query histories, workflow status and internal QA in separate workspace locations.

The final response should lead with the plan and PDF, and briefly disclose only material scientific limitations and the location of useful appendices. Do not present the internal QA report as the scientific plan.

Engineering tests and validators are supporting evidence only. Do not claim product acceptance solely from regression, schema validation, file presence, page count or successful PDF export.

### Mandatory quality controls within the workflow

**Stage 2 supplement — resolve leads and challenge novelty.** In addition to broad query facets, create a lead-resolution ledger for every user-supplied citation clue, every reference cited as a likely competitor in project materials and every candidate discovered during citation chasing. A lead is not "unlocated" after one failed query. Resolve exact title/author/year/venue/DOI variants across available independent bibliographic, publisher and scholarly routes; preserve ambiguity and version relationships. Before Stage 2 closes, turn every intended novelty phrase into an adversarial query and identify the closest primary studies that could already establish it. If a novelty-critical lead or full-text comparison remains incomplete, constrain the gap and candidate recommendation accordingly.

**Stage 3 supplement — novelty stress test and decision reversal.** For each serious candidate, state the smallest scientifically meaningful distinction from closest prior art and the observable consequence of that distinction. Separate a known principle, an incremental extension, a potentially distinct contribution and an unassessable claim. Record what new literature or experimental result would reverse the selection. Do not treat a finite task list as feasible until its samples, input records, methods/access and owners are checked or explicitly marked unknown.

**Stage 7 supplement — argument-bearing Figure allocation.** Review the main Figure portfolio as a whole. Each main Figure must advance the selected contribution or establish a necessary premise for it. Source-transcription, extraction, regression-reproduction and general QC audits normally belong in SI unless their finding is itself central to the contribution. A plan that demotes a validation route in prose but gives it a dominant main-text Figure allocation is internally inconsistent. Provide a main-text-versus-SI rationale for diagnostic material.

**Stage 9 supplement — discriminating design and sample-state integrity.** For each decision-critical task, identify the plausible alternative explanations and map them to controls or measurements; do not assume matching one variable isolates every other factor. Where source acquisition, preparation or handling may alter the target property or phenomenon, define the required representativeness, timing, processing, transfer, storage and measurement-state checks as applicable. Validate that the measured state is an adequate representation of the intended target state. Distinguish the operational scale and resolution of measurements from the scale of claims; do not infer across levels without an appropriate bridge. Identify a minimum discriminating experiment before a larger campaign where feasible.

**Stage 11/12 supplement — mandatory narrative product QA.** Apply docs/V5_1_NARRATIVE_PRODUCT_QA.md to the actual Markdown and same-revision PDF. Record PLAN_PRODUCT_STATUS, SCIENTIFIC_READINESS and BENCHMARK_COMPARISON separately. Do not call benchmark comparison complete when the requested benchmark was unavailable. Do not mark product PASS solely because the file is long, the PDF is multi-page, tests pass or validators pass.

 
**Stage 3 hybrid guard.** HYBRID is valid only when its components are necessary, logically linked parts of one central inference. It is not a compromise between disconnected stories. Explicitly state the shared central question and why each component is needed; otherwise select one route and defer or separately scope the other. Check that main-text Figure allocation and task priority follow that same logic.


**Benchmark calibration guard.** When a benchmark is supplied, inspect its complete available content and extract its transferable quality criteria for a separate comparison. The benchmark is not evidence for the current project's scientific claims and must not supply domain-specific defaults. If the benchmark is unavailable or only partially accessible, mark BENCHMARK_COMPARISON as BLOCKED_REFERENCE_UNAVAILABLE in the separate internal QA record. Assess PLAN_PRODUCT_STATUS independently against the V5 product contract and researcher-facing delivery standard; benchmark unavailability alone neither passes nor fails the actual plan. Never claim a comparison that was not performed.
