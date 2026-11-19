# Paper_plan V5 — Product Contract

## 1. Product definition

Paper_plan converts a user's existing research evidence into a complete, evidence-grounded manuscript-development and research-execution plan. The document must be suitable for a supervisor to evaluate the scientific case and for a research team to understand, plan and carry out the required work.

The primary product is a **professional researcher-facing report**, not an account of how the Skill processed files, chose a route, populated schemas or passed validation. It should read like a well-developed scientific project proposal and manuscript-development dossier.

Paper_plan is not an automatic paper generator, generic literature review, JSON bundle, validator report or autonomous experiment/computation runner. It designs a defensible paper and the research work required to support it.

**Structured project state is the evidence and traceability layer. The integrated narrative plan is the product delivered to the researcher.**

A complete schema, successful validator, list of task IDs or set of workflow files cannot substitute for the integrated plan.

## 2. Two synchronized representations

### Structured and internal state

Retain evidence, literature, candidate-route, framework and manuscript-development records. They preserve source links, identifiers, measurement definitions, evidence roles, uncertainty, claims, data dependencies, comparison states, journal provenance and machine-checkable consistency.

Internal state may also retain workflow progress, run metadata, tool diagnostics, route enums, QA status and implementation details. These records belong in the isolated project workspace or a separate internal review report.

### Researcher-facing narrative plan

Produce a standalone editable Markdown report and a PDF exported from that exact revision. It must explain the scientific reasoning in complete prose and use tables where they improve comparison or assignment. The report must be understandable and actionable without opening JSON bundles, validator reports or development logs.

Internal IDs may support cross-referencing in the workspace but are not a substitute for readable explanations. Never paste a schema dump or stage-by-stage execution summary into the report.

## 3. Required capabilities

The exact document architecture and depth depend on the project. A substantive full-paper plan must develop the following capabilities in a connected narrative:

1. **Scientific background and rationale:** explain the field problem, scientific importance, limitations of current knowledge/approaches and the reason the project matters.
2. **Research diagnosis:** interpret the user's actual evidence, identify robust findings and uncertainties, explain what can and cannot be concluded, and connect data limitations to the paper.
3. **Literature frontier and novelty:** discover and compare the closest prior studies, competing explanations and contradictory evidence; define a precise, defensible contribution boundary. Keep the detailed search audit separately.
4. **Scientific-mainline decision:** evaluate the user's original intended question alongside evidence-led alternatives and stop/defer options; explain the selected scientific question and why it is preferable in ordinary scientific language.
5. **Introduction and manuscript architecture:** provide a paragraph-level Introduction argument with verified literature support; develop the Results/Discussion story as a connected sequence of scientific questions and conclusions; define abstract and conclusion logic.
6. **Main Figures and Panels:** design the visual proof of the paper. Specify each Figure's scientific message and every Panel's actual content, source, status, comparison, layout, analysis, intended inference and limitation.
7. **Supporting Information:** define concrete supplementary texts, tables, figures, methods, derivations and validation records, and explain how each supports the main paper.
8. **Research work programme:** turn evidence gaps and manuscript needs into student-/collaborator-ready experiment, reanalysis and analysis briefs with inputs, designs, controls, records, outputs, QC, interpretation and completion criteria.
9. **Theory/computation when relevant:** provide concrete collaborator handoffs with model construction, inputs, assumptions, methods, outputs, controls, validation and links to the scientific argument. Never force a method with no decision value.
10. **Execution and assignment:** organize tasks by scientific priority, dependencies, responsibilities and manuscript use; distinguish decisive minimum work from later extensions.
11. **Integrated reasoning:** ensure the background, evidence, literature, central question, Introduction, Results/Discussion, Figures, SI, tasks and conclusion all express one coherent scientific argument.

## 4. Required narrative depth

A recommendation is complete only when the plan explains:

- why the scientific problem matters and why the proposed question follows from the current evidence and literature;
- how the user's original research intent was assessed;
- what the closest studies have actually demonstrated and how the current project differs;
- which observations support each central statement and how reliable they are;
- what additional or reprocessed evidence is needed, why it is needed and what alternative explanations it distinguishes;
- how the manuscript will develop its argument from Introduction to conclusion;
- what each Figure and Panel will show and why it belongs in the paper;
- what each SI item contains and what the reader can verify from it;
- what students/collaborators must do, what they must return and how the result will be used;
- what would weaken, falsify or narrow the interpretation;
- which scientific and practical decisions require supervisor input.

For substantive projects, a one-page summary, a short direction list, a sequence of questions or a set of populated headings is not a complete product. Do not impose a fixed word count or page count: the report must contain enough developed scientific reasoning and practical detail for the actual project.

The researcher-facing document must not merely reproduce the internal evidence map, literature ledger, route comparison, task graph or QA checklist. Synthesize those materials into an argument and a plan.

## 5. Evidence and uncertainty rules

Distinguish source-verified observations, extracted but unchecked evidence, reprocessed/derived results, interpretations, hypotheses and future work. Explain uncertainty in scientific language and state its consequence for the proposed paper.

Never describe planned results as observed. Never invent values, thresholds, sample identities, protocols, controls, replicates, parameters, references, journal requirements or outcomes. Preserve contradictory evidence and alternative explanations. If evidence is insufficient, narrow the proposed claim, define a decisive research path or recommend stopping; do not manufacture a complete-looking story.

Metadata is not full-text evidence. A null result from one search provider is not proof of novelty or absence of prior art. Use alternative query formulations, independent discovery routes and citation chasing. Keep the detailed search history and identity-resolution audit separate from the scientific narrative. Verify current journal requirements against official dated sources.

Retain physical source anchors, visual provenance, comparison compatibility, measurement definitions, calculation reproduction, proxy validation, uncertainty separation, task readiness and human approval gates in the internal evidence layer. Explain only the scientific consequences that matter to the reader in the main report.

## 6. Researcher-facing language and report boundaries

The main report must be written for supervisors, students and collaborators, not for the Skill developer.

Do not include the following in the main plan unless the user explicitly requests a technical audit document:

- workflow/stage names, Skill versions, commit SHAs, worktree paths or runtime configuration;
- schema, bundle, validator, prompt, agent, tool, pipeline or implementation terminology;
- internal identifiers in place of readable task/evidence descriptions;
- route enums such as `HYBRID`, `CONDITIONAL`, `FALLBACK` or `STOP/DEFER`;
- product-quality status fields such as `PLAN_PRODUCT_STATUS`, `SCIENTIFIC_READINESS` and `BENCHMARK_COMPARISON`;
- validator PASS/FAIL summaries, test counts or developer acceptance notes;
- raw provider errors, search logs and workflow completion traces.

Translate internal states into their scientific and operational meaning. For example, explain what input is missing, why it matters, who can provide it and what work can proceed; do not expose a bare `BLOCKED` label. Explain why a research direction is being pursued or not pursued; do not expose internal route enums. Keep limitations and uncertainty visible rather than hiding them.

The primary report must use meaningful descriptive headings, complete paragraphs, well-designed tables and clear task briefs. It must not read like a software status report or concatenated checklist.

## 7. Generality and project isolation

All Skills, workflows, schemas, templates, examples and configurations remain domain-neutral. Project-specific scientific content, names, sample labels, values, equations, mechanisms, literature conclusions, conditions and Figure designs belong only in the isolated workspace, test fixture or separately maintained user benchmark. The benchmark teaches depth and reasoning, not a fixed scientific story or output shape.

The target journal is a project-scoped runtime input, never a cross-project default. Use only the journal explicitly supplied or authorized for the current project. A benchmark journal applies only when the current test/run explicitly declares it as the target for that same case. Never inherit target journal, article type, format or publication rules from a different benchmark, prior project, previous run, memory or generic configuration. Verify the current project's selected journal independently.

Do not impose fixed numbers of routes, paragraphs, Figures, Panels, SI items, tasks, controls, techniques or computational methods.

## 8. Required deliverables

At minimum:
- integrated editable Markdown research plan;
- PDF exported from that exact Markdown revision and checked for text, page structure and visual integrity;
- structured project bundles and relevant evidence/search/task records retained separately in the workspace;
- a supervisor decision section and student/team assignment briefs within the main plan;
- an internal QA/run record stored separately from the main plan.

Recommended primary-plan path: `WORKSPACE/deliverables/FINAL_MANUSCRIPT_DEVELOPMENT_PLAN.md`, with a same-basename PDF.

Recommended internal review path: `WORKSPACE/internal/PRODUCT_QA_REPORT.md`. Do not concatenate this internal report into the primary plan.

## 9. Product acceptance

A supervisor should be able to answer from the main narrative: What problem is being addressed and why does it matter? What is the proposed contribution and its boundary? Which closest studies define the novelty? What does the current evidence show? What is the whole argument from Introduction to conclusion? What exactly belongs in every main Figure/Panel and SI item? What work must each student or collaborator carry out and return? What outcomes support, weaken or invalidate the proposed interpretation? What is the execution order and what decisions remain?

A student should be able to understand an assigned task without reverse-engineering JSON or asking what an internal status code means. Local SOPs, safety review and specialist approvals remain required where applicable.

A package that only passes schemas, lists directions, reproduces workflow states or gives generic advice fails. Engineering tests and validators support, but never substitute for, human inspection of the complete Markdown/PDF against the product contract and project benchmark.

## 10. Internal product QA

Apply `docs/V5_1_NARRATIVE_PRODUCT_QA.md` to the actual main report and matching PDF. Keep the QA record separate using `templates/V5_INTERNAL_PRODUCT_QA_REPORT.md`.

Report product quality, scientific readiness, benchmark comparison and structural validation independently in that internal record. Benchmark unavailability affects whether a benchmark comparison can be claimed; it does not automatically determine the intrinsic quality of the plan. Assess the actual report against the product contract even when a benchmark cannot be inspected. Do not put these internal status codes into the researcher-facing report.
