# V5.1 Narrative Product Quality and Acceptance Protocol

## Purpose and authority

This protocol defines how to review the actual researcher-facing manuscript-development plan. It complements, but is not replaced by, schemas, deterministic validators, unit tests, workflow completion or PDF export checks. It is domain-neutral: use the gates as reasoning checks, not as a fixed scientific story, method list, section count or Figure count.

Apply it after drafting the complete Markdown and again to the same-revision PDF. The plan must be understandable and useful without opening the structured bundles.

## 1. Keep three decisions separate

Report these independently:

- PLAN_PRODUCT_STATUS: PASS, PARTIAL or FAIL. Does the plan meet the product contract and provide a reliable, usable explanation and handoff?
- SCIENTIFIC_READINESS: READY, CONDITIONAL, NOT_READY or STOP_DEFER. Does the existing evidence support the paper now, support it only after defined work, or fail to justify proceeding?
- BENCHMARK_COMPARISON: COMPLETE, BLOCKED_REFERENCE_UNAVAILABLE or NOT_APPLICABLE. Was the requested project benchmark actually available and compared?

A lack of decisive data does not automatically make the plan a product failure: an excellent plan may identify a conditional path or recommend stopping. Conversely, engineering PASS, a polished PDF or complete template headings do not make a plan PASS when the scientific reasoning or handoffs are inadequate.

When a benchmark is explicitly required but unavailable, do not substitute a remembered summary, unrelated benchmark, generic journal style or the Agent's own checklist and claim a benchmark pass. State exactly which comparisons could not be made. The plan may still be reviewed against the general product contract, but BENCHMARK_COMPARISON remains BLOCKED_REFERENCE_UNAVAILABLE.

## 2. Research question and contribution gate

A supervisor should be able to identify, from the narrative alone:
- the user's original research intent and how it was assessed;
- materially different candidate contributions and why they were selected, combined, deferred or rejected;
- one central question and one bounded contribution, or a justified stop/defer decision;
- the closest prior work that most threatens the contribution and the exact scientific distinction;
- the strongest supporting and contradicting evidence, the alternative explanations and what would change the recommendation.

Reject cosmetic route variants, topic statements masquerading as contributions, and a contribution that changes wording but not scientific understanding. Do not reward a candidate merely because it was the user's original hypothesis; do not discard it solely because current evidence is incomplete.

## 3. Literature-frontier gate

Inspect the search ledger and nearest-work comparison, not just the bibliography.

- Every paper/author/year/DOI/title clue explicitly supplied by the user or found in project source materials has a resolution record and disposition.
- Exact-system, transformation-direction, mechanism, condition, measurement and adjacent-system query facets are represented where relevant.
- Independent discovery routes and backward/forward citation trails are documented.
- Novelty-critical primary studies are inspected at the highest accessible tier. Metadata-only items cannot substantiate scientific conclusions; abstract-only items cannot support details absent from the abstract.
- Each serious candidate has undergone an adversarial novelty test. Known principles, incremental extensions and potentially distinct contributions are not conflated.
- Contradictory/inconvenient sources are included. A single failed endpoint or empty query has not been treated as evidence of absence.
- Gap statements are bounded by inspected literature and access limits. Unsupported "first", "unprecedented" and "no studies" claims are removed.

If an identity-critical citation or likely direct competitor remains unresolved, the novelty boundary cannot be rated fully supported. Identify the exact missing source or retrieval task.

## 4. Evidence-to-argument gate

The mainline is built from the actual project's evidence, not from the order of files or instrument types. Each major claim has an explicit epistemic status, source provenance, measurement definition where applicable, comparability assessment and alternative explanation.

The narrative separates observations, derived results, interpretations, hypotheses and planned work. The story does not turn a measured proxy into the target property, an audit discrepancy into a scientific finding, or an absent record into proof that an experiment never occurred. It explains how each Results/Discussion step changes the argument and why the next step follows.

## 5. Figure and SI allocation gate

For every main-text Figure, ask: **What central claim or decision would be lost if this Figure were removed?** If the answer is only "it proves that data extraction, transcription or a calculation was checked", the material normally belongs in SI or a data-quality note unless method validity is itself the central contribution.

The main Figure portfolio should carry the paper's scientific argument in the order a reader needs it. Diagnostic source audits, raw-data transcription checks, coefficient reproduction and general QC should not crowd out central scientific results. Do not move decisive evidence to SI to hide a weak argument.

Every Panel must state its question, exact planned content, data/source and status, comparison groups, analysis, intended inference, prohibited inference, linked claim/task/SI and acceptance criterion. Planned or blocked Panels must be visually and textually distinguishable from observed results. SI items must have exact contents and a reason for being outside the main text.

## 6. Experiment and analysis handoff gate

A task is assignable only when a colleague can understand what decision it serves, what is needed and what files/results to return. For each material task inspect:

- a precise scientific or analytical question and the uncertainty/claim it addresses;
- known inputs and missing prerequisites, without invented values or local procedures;
- sampling/experimental unit, pairing, conditions, comparison basis and variables;
- plausible confounders and a control/measurement strategy for each decision-relevant alternative;
- outputs, analysis, normalization, uncertainty and QC;
- outcomes that support, weaken, contradict or leave the question unresolved;
- dependency, priority, owner/role, linked Figure/Panel/SI and completion/stop condition.

Where the target property can change during sampling or handling, explicitly consider aliquot representativeness, timing, quenching, separation, washing, drying, transfer, storage and measurement state. Do not assume a handling step preserves the state; require a suitable preservation/stability check or mark the inference blocked. Apply this where relevant rather than forcing it into unrelated project types.

Matching one parameter (for example, concentration, ionic strength, temperature or nominal dose) does not automatically isolate all chemical, physical or procedural alternatives. State which dimensions are matched, which vary, which remain confounded and what additional controls or narrowed inference are needed.

For spatial or compositional claims, distinguish the scale and operational meaning of the measurement where relevant (for example, bulk composition, surface composition, pore/phase association or lattice-level incorporation). A method that measures one scale cannot alone establish a claim at another scale.

Require a minimum discriminating test where feasible before a larger resource-intensive program. A list of techniques is not a work package. An experiment is not ready merely because a named technique is available.

## 7. Title, abstract and claim-language gate

Compare the title, contribution sentence, abstract map, Figure messages and conclusion against the current evidence status. No part may imply that planned work has already succeeded. Do not assert a phase, purity, mechanism, causal relationship, structural incorporation/removal or application benefit more strongly than the available evidence permits. Use neutral or question-oriented working language while a result remains hypothetical. A strong hypothesis may be the subject of the plan without being presented as a fact.

## 8. Journal-fit gate

Verify requirements for the current project's target journal and article type using current official sources. Record exact URLs, checked dates, source locations and access limitations. A link or a statement that the journal is prestigious is not verification. Keep journal fit conditional if the journal/article type is unresolved or official instructions are inaccessible. Never inherit journal settings from another project or benchmark.

## 9. Whole-plan consistency gate

Trace the selected contribution through: project evidence → literature gap → Introduction → Results/Discussion → main Figures → SI → tasks → priorities → conclusion. Find and resolve contradictions such as:
- a validation/audit route described as secondary but occupying most main Figures;
- a mechanism described as hypothetical in the evidence section but stated as fact in the title or conclusion;
- a planned result appearing as observed in a Figure caption;
- an essential claim with no linked evidence or work package;
- a task whose output is not used by any claim/Figure/decision;
- a Figure/Panel with no acceptance criterion or no place in the story;
- a prerequisite that is unavailable but not marked as a blocker.

Run one skeptical-reviewer pass: identify the strongest reason the preferred contribution could already be known, could be explained by an alternative, could fail measurement, or could be infeasible. State the decisive observation that would resolve each concern.

## 10. Deliverable and review checks

Confirm that the Markdown is complete, readable and not a bundle dump; that the PDF is generated from exactly that Markdown revision; and that the PDF has usable text, page structure, readable tables/figures and no truncation or missing sections. There is no fixed page-count or word-count target: depth is determined by project complexity and the benchmark/product requirements. Report hashes/revisions.

Record the findings by gate with PASS, PARTIAL or FAIL and a concise reason. Do not use pseudo-precise quality scores or allow a numeric aggregate to conceal a critical failure.

A final review must state the three independent statuses from Section 1, material strengths, blocking/conditional issues, exact follow-up tasks and human decisions. Product QA is a human reasoning review; an automated checklist can prepare it but cannot certify scientific correctness.
