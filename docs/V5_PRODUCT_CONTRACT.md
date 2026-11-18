# Paper_plan V5 — Product Contract

## Product definition

Paper_plan V5 turns a user's existing research evidence into a complete, evidence-grounded and target-journal-aware manuscript-development dossier. It must be reasoned enough for supervisor review and concrete enough for team assignment.

V5 is not an automatic paper generator, generic literature review, JSON bundle, validator report or autonomous experiment/computation runner. It designs the paper and the work needed to make the paper defensible.

**Structured project state is the evidence and traceability layer. The integrated narrative plan is the product delivered to the researcher.**

A complete schema, successful validator, list of task IDs or set of workflow files cannot substitute for the integrated plan.

## Two synchronized representations

**Structured state:** retain the existing evidence, literature, routes, framework and manuscript-development bundles. They preserve permanent IDs, source links, measurement definitions, evidence-use roles, uncertainty, claims, Data Slots, comparison states, dependencies, journal-source provenance and machine-checkable consistency. Retain the V4.1–V4.3 scientific-integrity controls.

**Narrative plan:** produce a standalone editable Markdown document and a verified PDF. The plan must explain the scientific reasoning in complete prose and use tables where they improve comparison or assignment. It must be understandable without opening JSON bundles. IDs are traceability links, not substitutes for explanation. Never paste a schema dump into the plan.

## Required capabilities

The exact section count and depth depend on the project. Every full-paper plan must cover:

1. **Research diagnosis and evidence readiness:** what is established, uncertain, decision-critical, suitable for a paper now, or requires further work.
2. **Literature frontier and novelty boundary:** multi-route discovery and citation chasing; closest primary studies; comparison of actual systems, transformation pathways, methods, conditions, observables, conclusions and limitations; counter-evidence; bounded gap statements and search-saturation basis.
3. **Scientific-mainline decision:** compare the user's original intended question/hypothesis with evidence-led alternatives, conditional/hybrid options and stop/defer; distinguish a scientific contribution from an audit/validation task; explain why the selected mainline is preferable and what evidence would change the choice.
4. **One central contribution:** research question, proposed contribution and boundary; why it matters; difference from closest work; supporting/missing evidence; alternative explanations.
4. **Introduction architecture:** actual paragraph sequence, each paragraph's role/message/literature support/transition/citation needs; draft prose when claims and references are sufficiently verified.
5. **Complete storyline:** Results/Discussion as a connected sequence of questions, evidence, inference and transitions, not an instrument-by-instrument list.
6. **TOC and main Figures/Panels:** journal-aware concept where relevant; exact content, purpose, evidence status, new/reprocessed data, comparison, intended inference and limitations for every proposed Panel.
7. **Supporting Information:** concrete Text/Table/Figure items, content, source/status, purpose and links to main claims/Figures.
8. **Experiment and analysis work packages:** question, rationale, inputs, variables, controls, design, outputs, QC, alternative outcomes, dependencies and measurable completion criteria.
9. **Theory/computation handoff when relevant:** scientific question, model construction, inputs, assumptions, methods, observables, controls, convergence, validation, expected files and links to experimental claims/Figures. Block on missing inputs. Do not force DFT/MD or any method where it has no decision value.
10. **Prioritized execution plan:** verification/reanalysis, experiments, computation, figure preparation and writing as appropriate; priority, dependencies, value and decision unlocked.
11. **Integrated delivery:** consistent contribution, Introduction, storyline, Figures, SI, tasks and priorities; explicit supervisor decisions and assignable team outputs.

## Required reasoning depth

A recommendation is complete only when the plan explains why this scientific mainline/contribution is defensible; how the user's original scientific intent was evaluated; how closest studies differ; why a validation/audit-only fallback was selected or rejected where relevant; which evidence supports each important statement and how reliable it is; what new/reprocessed evidence is required and why; what each Figure/Panel demonstrates and what alternative outcomes mean; how each task reduces a named uncertainty or tests a claim; where each task output goes; what would weaken/falsify/narrow the interpretation; and what the supervisor must decide.

For a substantive full-paper project, a one-page summary or short list of directions is presumptively insufficient. Do not chase a fixed page count; provide enough reasoning and task detail for review and assignment. A small/evidence-limited project may be shorter only with an explicit reason.

## Evidence and uncertainty rules

Distinguish existing source-verified evidence, extracted but unchecked evidence, reprocessed/derived evidence, evidence requiring audit, planned work, hypotheses/interpretations and blocked/unavailable evidence.

Never describe planned results as observed. Never invent values, thresholds, sample identities, protocols, controls, replicates, parameters, references, journal requirements or outcomes. Preserve contradictory evidence and alternatives. If evidence is insufficient, narrow the claim, propose a decisive test or recommend stopping; do not manufacture a complete-looking story.

Metadata is not full-text evidence. A null result from one search provider is not proof of novelty or absence of prior art. Use alternative query formulations, independent discovery routes and citation chasing; stop on coverage/saturation, not a paper-count target. Verify current journal requirements against official dated sources. Keep physical source anchors, visual provenance, comparison compatibility, measurement definitions, fit reproduction, proxy validation, uncertainty separation, task readiness and human approval gates.

## Generality and isolation

All Skills, workflows, schemas, templates, examples and configurations remain domain-neutral. Project-specific scientific content, names, sample labels, values, equations, mechanisms, literature conclusions, conditions and Figure designs belong only in the isolated workspace, test fixture or separately maintained user benchmark. The benchmark teaches depth and reasoning, not a fixed scientific story or output shape.

The target journal is also a project-scoped runtime input, never a cross-project default. Use only the journal explicitly supplied or authorized for the current project. A benchmark journal applies only when the current test/run explicitly declares it as the target for that same case. Never inherit target journal, article type, format or publication rules from a different benchmark, prior project, previous run, memory or generic configuration. Verify the current project's selected journal independently.

Do not impose fixed numbers of routes, paragraphs, Figures, Panels, SI items, tasks, controls, techniques or computational methods.

## Required deliverables

At minimum:
- integrated editable Markdown plan;
- PDF exported from that exact Markdown revision and checked for text/page count;
- structured project bundles and relevant source/audit records;
- supervisor decision list and student/team execution list;
- final status report separating product completeness, scientific issues, structural validation and human decisions.

Recommended plan path: WORKSPACE/deliverables/FINAL_MANUSCRIPT_DEVELOPMENT_PLAN.md, with a same-basename PDF.

## Product acceptance

The supervisor must be able to answer from the narrative plan: What is the one-sentence contribution and boundary? Which closest studies define novelty? What is the whole argument from Introduction to conclusion? What is every Figure/Panel's exact role/content? What belongs in SI? What must be verified/reprocessed/measured and why? What must collaborators receive and return? Which outcomes support, weaken, contradict or leave the interpretation unresolved? What is the execution order and what decisions remain?

A package that only passes schemas, lists directions or gives generic advice fails. Product acceptance is human inspection of the complete Markdown/PDF against the project benchmark. Engineering tests and validators support, but never substitute for, that review.


## Narrative-product quality gates

Apply the operational review in docs/V5_1_NARRATIVE_PRODUCT_QA.md to the actual final Markdown and its matching PDF. This is a product-quality gate, not another schema validator.

A plan is not complete merely because every template heading, bundle entity or work-package field is present. It must pass these substantive checks:

- **Scientific distinctiveness:** the selected contribution survives an adversarial comparison with the closest primary studies; each novelty dimension has a specific, evidenced distinction or is explicitly provisional.
- **Literature reliability:** supplied literature leads have documented identity-resolution outcomes; novelty-critical sources are inspected at the highest accessible tier; important absences/access limits constrain the claim.
- **Argument integrity:** one contribution connects the Introduction, Results/Discussion, Figures, SI, work packages and conclusion without unrelated side stories.
- **Figure logic:** main-text Figures carry the central argument. Data-extraction audits, calculation-reproduction diagnostics and general QC material normally belong in SI unless their result is itself essential to the central contribution.
- **Experimental discrimination:** work packages distinguish competing explanations and address material confounders; matching one control variable is not assumed to control all others.
- **Sample-state integrity:** where sampling, quenching, washing, drying, storage, transfer or measurement can change the property being studied, the plan includes a preservation/stability check before relying on those measurements.
- **Claim calibration:** title, abstract, Figure labels and conclusion do not assert planned, hypothesized or literature-inferred outcomes as observations.
- **Handoff readiness:** each priority task has concrete inputs, a decision question, design, controls, outputs, QC, alternative outcomes, dependencies and completion/stop criteria; blocked tasks name their unlocking inputs.

Report three separate outcomes: (1) PLAN_PRODUCT_STATUS = PASS / PARTIAL / FAIL; (2) SCIENTIFIC_READINESS = READY / CONDITIONAL / NOT_READY / STOP_DEFER; and (3) BENCHMARK_COMPARISON = COMPLETE / BLOCKED_REFERENCE_UNAVAILABLE / NOT_APPLICABLE. Missing decisive research data can make the science conditional without making a carefully bounded plan a product failure. Conversely, a polished plan cannot be marked product PASS when its requested benchmark is unavailable and no valid comparison can be performed. Never collapse these three outcomes into one green status.
