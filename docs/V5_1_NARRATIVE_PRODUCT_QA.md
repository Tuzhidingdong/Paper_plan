# V5.1 Researcher-Facing Product QA Protocol

## Purpose and authority

This protocol reviews the actual researcher-facing manuscript-development plan, not the Skill's workflow log or structured bundle. It complements schemas, deterministic validators, unit tests and PDF-export checks; none of those can replace the review.

Apply the protocol to the complete Markdown and the matching PDF. Record findings in a separate internal QA report using `templates/V5_INTERNAL_PRODUCT_QA_REPORT.md`. **Never append the QA report, status codes or validator summary to the research plan.**

The main plan must be understandable and useful to a supervisor, student and collaborator without opening internal JSON bundles, logs or developer documentation.

## 1. Keep product quality, scientific readiness and benchmark comparison independent

Record these only in the separate internal QA report:

- **PLAN_PRODUCT_STATUS:** PASS, PARTIAL or FAIL. Does the actual plan meet the researcher-facing product contract and provide a reliable, usable scientific explanation and work handoff?
- **SCIENTIFIC_READINESS:** READY, CONDITIONAL, NOT_READY or STOP_DEFER. Does the existing evidence support the paper now, support it only after defined work, or fail to justify proceeding?
- **BENCHMARK_COMPARISON:** COMPLETE, BLOCKED_REFERENCE_UNAVAILABLE or NOT_APPLICABLE. Was the requested project benchmark available and actually compared?

A lack of decisive data does not automatically make the plan a product failure. A strong plan may correctly recommend conditional work or stopping. Benchmark unavailability limits the benchmark comparison, but **does not automatically cap or lower PLAN_PRODUCT_STATUS**. Evaluate the actual plan independently against the V5 product contract and researcher-facing delivery standard. Never claim a comparison that was not performed.

## 2. Reader-facing form and usefulness

Read the report as if it were being handed to a supervisor and then to a student.

- Does it read as a professional scientific research proposal and manuscript-development plan rather than a software, workflow or validator report?
- Does it begin with the scientific problem, proposed contribution and research recommendation?
- Is the scientific reasoning explained in complete prose, with tables used to clarify rather than replace argument?
- Are unexplained abbreviations, raw internal IDs, state enums, schema terms, workflow stages, commit hashes and tool diagnostics absent from the main narrative?
- Are important limitations translated into clear scientific and operational consequences rather than unexplained status labels?
- Can the supervisor understand the scientific rationale and decide what to approve?
- Can a student understand the purpose, inputs, work design, records, analyses and expected return from an assigned task?
- Is the main document readable on its own, without asking the user to open JSON files to understand the paper?

A report that is primarily short bullets, headings, internal status messages, task IDs or copied structured records fails this gate even if it is complete by schema.

## 3. Scientific background, evidence and contribution

A supervisor should be able to identify from the narrative:

- the field-level problem and why it matters;
- the specific unresolved problem motivating the project;
- the evidence supplied by the user and its reliability/limitations;
- the original research intent and how it was assessed;
- materially different candidate contributions and why they were selected, narrowed or rejected;
- one central question and bounded contribution, or a justified recommendation not to proceed;
- the closest prior work that most threatens the contribution and the exact scientific distinction;
- the strongest supporting and contradicting evidence, alternatives and observations that would change the recommendation.

Reject cosmetic route variants, generic topic statements masquerading as contributions and a contribution that changes wording but not scientific understanding. Do not reward a candidate merely because it was the user's original hypothesis; do not discard it solely because current evidence is incomplete.

## 4. Literature-frontier and novelty gate

Inspect the completed project-specific literature audit ledger and the narrative synthesis, not just the bibliography.

- Important citation leads and references identified in project material have documented identity-resolution outcomes.
- Discovery covers relevant system, transformation, mechanism, condition, measurement and adjacent-system facets.
- Independent discovery routes and backward/forward citation trails are documented.
- Novelty-critical primary studies are inspected at the highest accessible tier.
- Metadata-only items do not substantiate technical conclusions; abstract-only sources do not support details absent from the abstract.
- Closest studies are discussed in prose, with a comparison table where useful.
- Contradictory/inconvenient sources are considered.
- Each serious contribution claim has undergone an adversarial novelty test.
- Gap statements are bounded by actual literature coverage and source-access limitations.

An identity-critical citation or likely direct competitor that remains unresolved must narrow the novelty claim and be assigned a specific retrieval task. Do not turn a search log into the literature narrative.

## 5. Manuscript narrative and argument integrity

The proposed paper must form a sequence of scientific questions and answers, not an inventory of instruments or characterization methods.

Check that:
- the Introduction narrows logically from field context to the unresolved question and contribution;
- each paragraph has a clear reader-facing role, evidence/literature support and transition;
- the Results/Discussion order follows the logic of proof and reader comprehension;
- each section has an explained scientific purpose, evidence, comparisons, inference limits and transition;
- abstract and conclusion logic match the proposed evidence and contribution;
- important alternatives and contradictory results are integrated rather than relegated to generic risk statements.

If the plan contains only section headings, brief notes or "add literature/data" placeholders, it is not a complete manuscript-development plan.

## 6. Figure and Supporting Information gate

For every main-text Figure, ask: what scientific message does it communicate, and what would be lost from the central argument if it were removed?

For every Panel, inspect:
- exact scientific question and data/conceptual content;
- source and whether the evidence exists, requires reanalysis or remains planned;
- groups, conditions, controls and comparison basis;
- proposed visual form, axes, units, normalization and statistical/uncertainty display where relevant;
- intended and prohibited inferences;
- required annotations, image handling or layout guidance where relevant;
- linked manuscript section, research task and supplementary item;
- criteria for making the Panel interpretable.

Diagnostic audits, source transcription checks, fit reproduction and general QC normally belong in supplementary material unless they are themselves central to the scientific contribution. Do not hide decisive scientific evidence in SI.

Each supplementary item must have defined contents, source/producing task, purpose, main-paper relationship and required reproducibility checks. An ID/title alone is insufficient.

## 7. Student and collaborator task handoff gate

A task is assignable only when a recipient can understand the decision it serves, what is needed and what to return.

For each important task inspect:
- scientific question and rationale;
- available materials and missing inputs, including who can provide them;
- study unit, groups, variables, conditions and comparisons;
- relevant controls and plausible confounders;
- method and practical planning considerations without invented local parameters;
- required raw/processed data, metadata, scripts, records and outputs;
- analysis, normalization, statistics, uncertainty and QC;
- supportive, negative, mixed and inconclusive outcome interpretations;
- dependencies, approvals, priority and concrete completion criteria;
- manuscript section, Figure/Panel or SI item that uses the output.

Where the target property or phenomenon can change during acquisition or handling, require a relevant state-preservation or process-effect check. Matching one parameter does not automatically isolate other coupled variables. Distinguish the operational scale of a measurement from the scale of the claim.

A list of techniques is not a task brief. Do not force every task to contain irrelevant details; adapt the design to the actual science and local expertise.

## 8. Computational handoff gate

Where computation has a defined scientific role, confirm that the brief specifies model construction, required inputs, assumptions, method rationale, known settings versus unresolved settings, convergence/sensitivity, observables, raw and processed outputs, controls, validation against experiment, limitations and links to the paper's scientific questions and Figures.

A method name alone is not an executable or discussable handoff. Missing essential inputs must be identified with a responsible source or role.

## 9. Figure-to-task and whole-plan consistency

Trace the selected scientific contribution through current evidence, literature, Introduction, Results/Discussion, Figures, SI, research tasks, priorities and conclusion.

Resolve contradictions such as:
- a secondary validation topic occupying most main Figures;
- a hypothesis described as unproven in one section but asserted as fact in the title or conclusion;
- a planned result being presented as existing data;
- an essential manuscript claim with no supporting evidence or acquisition task;
- a task whose result is not used by any scientific decision or manuscript section;
- a Figure with no scientific message or acceptance criterion;
- an essential missing input that has no owner or acquisition route.

Run a skeptical-reviewer pass and identify the strongest challenge to the preferred contribution and the observation that would resolve it.

## 10. Editorial and document checks

The Markdown and matching PDF must:
- read as one coherent professional report, not concatenated summaries;
- use clear scientific prose, logical transitions and consistent terminology;
- avoid repetition and filler;
- include no empty headings or unresolved generic placeholders;
- distinguish established findings, interpretations, hypotheses and planned work;
- include usable references and readable source locations;
- give sufficiently detailed Figures, SI and task briefs for the project;
- be exported from the exact same Markdown revision;
- contain readable text, page structure, tables and figures without truncation or missing sections.

There is no fixed page count or word count. A short report is acceptable only when the scientific scope and product requirements genuinely justify it. Do not use length as a proxy for quality.

## 11. Internal review output

Record gate-level findings, three independent statuses, benchmark limitations, scientific-readiness issues, product defects, technical validation and release recommendation in a separate internal QA report.

Do not put the QA report in the main manuscript-development plan. Do not make the researcher-facing plan end with validator claims, Skill status codes or benchmark availability statements.
