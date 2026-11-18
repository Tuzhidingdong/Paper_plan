# Paper_plan V4 product contract

## Product definition

Paper_plan converts a user's existing research evidence into a journal-aware, evidence-traceable manuscript-development package that a supervisor can review and a research team can execute.

The package should make the research contribution, paper argument, visual evidence plan and follow-up work explicit. It is not a one-prompt paper generator, a generic literature review or an autonomous experiment runner.

## Required capabilities

1. Evidence inventory: trace each important observation to a source and preserve uncertainty, measurement definition and calculation lineage. A numeric metric used for the central contribution must define its measurand, signal, method, formula if derived, units, normalization, corrections and uncertainty.
2. Research frontier: identify closest competitors, contradictory evidence, bounded gaps and novelty limitations.
3. Contribution design: select one central question/contribution or explain why the current evidence does not justify a paper.
4. Journal adaptation: verify current official requirements for the selected journal/article type and record dated sources.
5. Introduction: produce a paragraph-level rhetorical plan and citation-grounded English draft when evidence permits.
6. Storyline: connect the manuscript sections as a sequence of scientific questions and answers.
7. Main Figures: define a project-specific number of Figures and Panels, each with a scientific message, claim/data links and acceptance criteria. Cross-sample/condition comparisons must record which conditions are matched, mismatched or unknown.
8. TOC/graphical abstract: provide a journal-aware concept brief when required or useful.
9. Supporting Information: plan reproducibility and supporting evidence with explicit claim/Figure links.
10. Work packages: create assignable experiment, analysis, theory and computation tasks with inputs, controls, outputs, dependencies and completion criteria.
11. Integrated audit: verify that the same central contribution is reflected through the Introduction, storyline, Figures, SI, work packages and consolidated plan.
12. Delivery: provide editable Markdown, verified PDF, structured project state and supervisor/student decision aids.

## Non-negotiable product rules

- The Skill must remain domain-neutral.
- Never embed a real project's names, sample codes, numeric results, equations, mechanisms, figure design or literature findings in generic Skill files.
- No fixed number of routes, figures, panels, Introduction paragraphs, SI items or research tasks.
- No target journal's current policies may be hard-coded as permanent generic facts.
- A specific output must be linked to evidence or visibly marked as planned/hypothesized.
- Every core claim needs a traceable support, explicit limitation or an evidence acquisition task. Numeric Result Units supporting the central contribution must be explicitly marked CORE and pass the verified measurement-definition gate, including when reached through a linked Finding.
- Every essential missing Data Slot must be addressed or explicitly deferred with rationale.
- Experiments and computations must have measurable outputs and acceptance criteria.
- Missing inputs block execution; unknown parameters remain TBD.
- Human decision gates must not be silently approved.

## Product-level acceptance questions

A reviewer should be able to answer from the package alone:
- What is the one-sentence scientific contribution?
- Why is it different from the closest prior studies?
- Which evidence already supports it, and how reliable is that evidence?
- What is the complete story from Introduction to final conclusion?
- What exactly belongs in every main Figure and Panel?
- What belongs in SI, and why?
- What additional experiment or calculation is required, and what does each resolve?
- What inputs and outputs must be handed to each collaborator?
- What results would weaken or falsify the proposed interpretation?
- Which decisions remain with the supervisor?

A package that answers only "what research directions could be explored?" does not meet the product contract.

## V4.1 scientific decision quality

- Claim evidence references distinguish support, contradiction, audit target and context. Quantitative SUPPORTS_CLAIM and CONTRADICTS_CLAIM evidence used to assess a central claim must be CORE/VERIFIED; AUDIT_TARGET and CONTEXT_ONLY are not promoted into decision-bearing results.
- Evidence assessments distinguish supported, partially supported, not established, not assessable, contradicted and inconclusive. Contradiction requires explicit counter-evidence; comparison failure alone is not contradiction.
- Comparability has separate NOT_COMPARABLE, NOT_ASSESSABLE and UNASSESSED states with declared dimensions and inference limits.
- Panels sharing Data Slots specify data scope or explain reuse.
- Work packages carry structured execution-design readiness, required-input availability, local feasibility, owner, outputs and QC.
- Agreement/equivalence tasks require a suitable analysis design and predeclared, justified decision boundaries; correlation alone is insufficient.
- Task dependencies distinguish execution, interpretation and publication gates.
- Validation outputs are fingerprinted to the Skill commit, validator, schema and input bundles.

These capabilities improve scientific decision traceability; they do not automate scientific sign-off or generate missing experimental facts.
