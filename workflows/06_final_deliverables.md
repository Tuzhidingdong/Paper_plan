# 06 — Manuscript Development Package and Execution Deliverables

## Required product coverage

Adapt the number and exact file split to the project. The integrated package must cover:

1. Evidence report: source inventory, observations, confidence, missing evidence, sample/condition ambiguity and measurement/calculation lineage.
2. Literature frontier: search scope, access-tiered bibliography, closest competitors, counter-evidence and bounded gaps.
3. Candidate research directions: defensible alternatives, comparison, provisional recommendation or an explicit stop/redirect decision. Do not force a fixed route count.
4. Target-journal profile: article type, current official requirements, cited sources, fit analysis and unresolved instructions.
5. Core argument: central scientific question, one main contribution, claim boundaries and alternative explanations.
6. Introduction: paragraph-level rhetorical plan and evidence-linked English draft when citations and premises are sufficiently verified.
7. Manuscript storyline: ordered scientific argument with section purpose, claim links, Figure references and transitions.
8. TOC/graphical abstract brief when required or useful under the verified target-journal profile.
9. Main Figure/Panel architecture: project-specific number of Figures, one message per Figure, panel content, data provenance, comparisons, missing slots and acceptance criteria.
10. Supporting Information architecture: methods, controls, supporting results and reproducibility items linked to claims/Figures.
11. Experiment and analysis work packages: objective, rationale, controls, conditions, raw data, replicate/statistical plan, QC, outputs and measurable completion criteria.
12. Theory/computation work packages only where scientifically justified, with model, inputs, assumptions, methods, observables, validation, handoff files and blockers.
13. Supervisor decision checklist, student-facing self-check and sequencing/dependency view.
14. Cross-bundle and integrated package validation report.
15. Consolidated editable Markdown and verified PDF export.

## Work-package specification

Every Task ID must include:
- objective and scientific reason;
- target Claim IDs and Data Slot IDs;
- existing evidence and exact missing evidence;
- sample identity and mapping confidence;
- variables, conditions, controls, blanks and comparisons;
- measurement/analysis method and expected native/raw data formats;
- replicate/statistical plan, or explicitly state that it requires supervisor/lab confirmation;
- data processing, quality criteria and acceptance/completion criteria;
- prerequisites, dependencies and priority;
- expected output, uncertainty/risk, feasibility and safety notes;
- intended Figure/Panel or SI destination;
- responsible role and handoff brief where relevant.

Do not invent concentrations, temperatures, equipment availability, sample quantities, replicate counts or timelines. Unknowns stay TBD.

## Theory/computation gate

A calculation task must specify the target hypothesis, system/model, structures/composition, input data, boundary conditions, method rationale, convergence/validation criteria, target observables and expected output. If the actual model inputs are unavailable, set status BLOCKED_BY_EXPERIMENT (or an explicit input blocker), name prerequisites and do not present the task as executable.

## Student-facing message

Use a short, friendly, question-oriented message. Phrase gaps as “could you help check whether…” or “do we have the original…?” Never say an experiment was wrong merely because the report does not show a condition.

## Cross-check before export

- Every central Claim links to evidence, verified literature support or an explicit hypothesis/test plan.
- Every novelty statement is bounded by closest competitors and search limitations.
- Target-journal requirements have current source links or are explicitly unresolved.
- Introduction, storyline, Figures, SI and final conclusion express the same central contribution.
- Every Figure/Panel has a purpose and evidence/Data Slot link.
- Every missing essential Data Slot has a task or explicit no-task rationale.
- Every work package targets a scientific uncertainty and has completion criteria.
- Calculation gates and sample/condition dependencies are correct.
- No literature source is represented as full text unless it was actually inspected.
- Human decision states reflect actual decisions.
- Exported Markdown and PDF have the same revision; reopen the PDF and verify page count/text extraction.
