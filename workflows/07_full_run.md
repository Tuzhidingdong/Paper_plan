# 07 — Full Run: Experimental Evidence to Manuscript Development Package (V4)

This is the controlling runbook. It defines a reusable method, not a fixed scientific story. Project-specific names, measurements, mechanisms, figure counts, journal requirements and conclusions must come only from the current workspace sources and verified research.

## 0. Intake, scope and cost baseline

- Create one isolated workspace for the current research project. The primary experimental-report PDF is the anchor source; user-provided supplemental tables, native data, images, methods, calculations and notes may be inventoried as additional project sources when supplied.
- Record each source's identity, role, immutable hash where available, and workspace-relative location. Never overwrite original files.
- Record repository commit, active provider/model/version and available usage counters. Do not start hidden Workers or external jobs.
- Reuse previous processing only when the exact source hash and extraction provenance match. Refresh diagnostics without resetting validated evidence or human decisions.
- Read this runbook and only the stage-specific workflows required. Keep long source documents out of repeated prompt context; use compact, task-specific evidence packs.
- Treat missing information as unknown. Never infer sample identity, conditions, raw values, replicates, instrument availability, mechanisms or approvals.

## 1. Evidence inventory and quality control

Follow workflow 01. Build the source inventory, page/Region/Panel anchors, Result Units, Sample entities, Findings, visual inspection cards and discrepancy register.

- Preserve original evidence and source locations.
- Keep measured data, calculated quantities, qualitative observations and hypotheses distinct.
- Record each derived measurement's measurand, signal, method, calculation, units, normalization basis, calibration/blank correction, uncertainty and source lineage where available.
- Record ambiguous labels and incompatible measurement conditions explicitly.
- Do not promote an observation to a causal/mechanistic statement without controls or independent evidence.

Run the existing evidence, sample and schema validators. Reuse exact-source results; do not repeat full extraction without a documented reason.

## 2. Literature frontier and competing-work analysis

Follow workflow 02. Use actual search tools and record databases/search systems, queries, date bounds, inclusion/exclusion criteria, access level and search date.

- Separate metadata, abstract and full-text verification.
- Identify the closest primary competitors, not just broad review papers.
- Compare systems, methods, conditions, measurable outcomes, conclusions and limitations.
- Include counter-evidence and contradictory findings.
- Bound every gap statement by the actual search scope.
- Do not claim priority, uniqueness or novelty merely because a search returned no direct match.

## 3. Candidate research directions and one core contribution

Follow workflow 03. Generate as many genuinely distinct directions as the evidence warrants; there is no mandatory number.

For each direction, connect existing evidence, literature claims, unresolved gap, candidate contribution, decisive missing evidence, feasibility, alternatives and risks. Recommend a direction provisionally when possible. If no defensible direction exists, explain why and stop short of manufacturing novelty.

Then select or propose one central contribution for the manuscript package. Supporting results, applications, theory and calculations must be organized around that contribution or explicitly deferred. Do not force unrelated observations into one paper.

## 4. Target-journal profile

Follow workflow 08. If the user specifies a target journal, verify the latest available official author instructions and publisher/journal scope pages. If no journal is specified, propose a small, reasoned shortlist only when useful and label the selection provisional.

Record the exact sources, access date, article type, relevant figure/TOC/SI requirements, format requirements, word limits where verified, data and reporting policies, and unresolved items. Never invent or freeze current journal rules into this Skill.

## 5. Core argument and manuscript storyline

Follow workflow 09. Define:
- the scientific problem and precise literature gap;
- one central research question and provisional thesis;
- one coherent core contribution and its boundaries;
- the evidence-supported claims and claims still requiring proof;
- the logical sequence that takes a reader from problem to evidence, interpretation and implications.

The storyline must explain why each Results/Discussion step is necessary and how it leads to the next. It must not be a list of techniques.

## 6. Introduction design

Build the Introduction from the actual argument and verified literature, not from a generic three-paragraph formula.

For every paragraph, specify its rhetorical role, intended message, supporting literature claims, transition and status. Draft English prose only when the source claims and citations are sufficiently verified. Flag every placeholder, unverified premise and citation gap.

## 7. Main Figures, Panels, TOC Graphic and Supporting Information

Follow workflow 10. Plan the number and order of main Figures from the scientific story; do not impose a fixed count or fixed sequence of characterization, mechanism and application.

For each Figure and each Panel specify the scientific question, take-home message, linked claims, existing evidence, missing Data Slots, sample/condition comparisons, analysis, visual form, acceptance criteria and main-text rationale.

Plan the TOC Graphic only according to the current journal requirement and the actual story. Plan Supporting Information as a structured evidence and reproducibility layer, linked to main claims and Figures. Do not move critical evidence to SI merely to hide a weakness.

## 8. Experiment, analysis and computational work packages

Follow workflow 11. Every unsatisfied essential Data Slot must map to a task or an explicit no-task rationale.

Each work package must state objective, reason, claim/slot/figure links, required inputs, variables, controls, methods, raw deliverables, statistics/replicates, quality checks, possible outcome interpretations, dependencies, blockers, responsible role and measurable completion criteria.

Computational work must be a handoff-ready brief: model/system, structures/composition, state/charge/protonation where relevant, boundary conditions, methods and convergence plan, observables, controls, validation against experiment, expected files, prerequisites and decision value. If essential inputs are unknown, block the work; do not present a generic method name as an executable calculation.

## 9. Integrated deliverables

Prepare an editable project package. The exact file set may vary, but the integrated plan must cover:

- project and source inventory;
- target-journal profile with source links and access status;
- research positioning, closest competitors and bounded novelty;
- core question, thesis and one central contribution;
- Introduction paragraph plan and draft;
- complete manuscript storyline;
- TOC concept and main Figure/Panel plan;
- Supporting Information map;
- Claim–Evidence–Data Slot relationships;
- experiment, analysis and computation work packages;
- dependencies, milestones, decision gates and risks;
- supervisor decision checklist and student execution checklist;
- references and explicit access/verification status.

Create a consolidated Markdown plan and export it to PDF. Supporting files may be split by function, but the consolidated plan must be understandable on its own.

## 10. Integrated product validation

Run all existing validators plus validate_manuscript_development.py.

The V4 validator must check:
- permanent IDs and cross-bundle references;
- journal sources and profile status;
- Introduction paragraph and citation links;
- storyline-to-Figure and Figure-to-Claim/Data Slot links;
- Panel-level evidence and acceptance criteria;
- SI links to claims, Figures and Data Slots;
- essential missing Data Slots covered by tasks or explicit rationale;
- task dependencies are valid and acyclic;
- calculations are not marked executable when required inputs are missing;
- required deliverables marked FINAL actually exist;
- the same core argument is reflected consistently across the Introduction, story, Figures, tasks and final plan.

Review all errors and warnings. A structural PASS is not a scientific truth certificate. A human review remains required for research-direction, journal-positioning and manuscript-framework decisions.

## 11. Final report

Report source hashes, workspace, software/Skill commit, model and usage limitations, evidence status, literature access tiers and search scope, selected direction and novelty confidence, target-journal verification state, main Figures and SI plan, essential Data Slots, work packages, blocked computations, human decisions, validator results and final file hashes.

The package is a decision-ready manuscript development proposal, not an automatically approved experimental protocol or guarantee of publication.
