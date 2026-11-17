# 12 — Integrated Manuscript Development Package Audit

## Objective

Verify that the complete package tells one consistent, evidence-bounded story and that every proposed experiment or calculation has a defined role.

## 1. Provenance and scientific claims

- Every factual experimental claim points to a traceable Result Unit, Finding or derived Data Unit.
- Every literature premise points to an appropriately verified literature claim and source location.
- Abstract-only and metadata-only material is not used to support full-text-level technical details.
- Measurement definitions, units, normalization and calculation lineage are explicit for central quantitative indicators.
- Sample identity, condition matching, controls, replicates and uncertainty are sufficiently resolved for the strength of each claim.
- Observed, interpreted and hypothesized statements remain distinct.
- Contradictory evidence and plausible alternatives are visible.

## 2. Argument and journal consistency

- The target journal and article type are explicit.
- Relevant current author requirements have dated source references or are marked unresolved.
- The Introduction leads to the same central question and contribution as the final plan.
- The core contribution is singular and specific; supporting sub-contributions are subordinate.
- The novelty statement is bounded by the strongest competing literature and search limitations.
- Every Results/Discussion step advances the manuscript argument.

## 3. Figure and SI consistency

- Every main Figure has one principal message and a place in the storyline.
- Every Panel has a purpose, traceable evidence or a named missing Data Slot, comparison design and acceptance criteria.
- No proposed result is presented as already measured.
- TOC/graphical abstract requirements match the current journal profile.
- SI items support named claims/Figures or reproducibility; essential evidence is not hidden there.
- Figure labels, claim descriptions, data-slot statuses and text use consistent terminology.

## 4. Work-package closure

- Every essential unsatisfied Data Slot has an experiment/analysis/computation task or an explicit no-task rationale.
- Tasks state objective, rationale, inputs, controls, method, raw outputs, QC, interpretation under alternative outcomes and measurable completion criteria.
- Each task output is assigned to a Figure/Panel, SI item or other explicit scientific decision.
- Computations have validated inputs or are blocked with named prerequisites.
- Dependencies are acyclic and task priorities are justified.
- No project-specific equipment, sample amounts, reagent quantities, conditions, replicates or timelines are invented.

## 5. Cross-document consistency

Compare the consolidated plan with the Evidence, Literature, Routes and Framework bundles. Ensure the same titles, IDs, claim wording, Figure order, task IDs, status and journal requirements are used everywhere. A change to the central contribution must trigger re-review of the Introduction, storyline, Figures, SI and tasks.

## 6. Verdict

Use:
- PASS: no structural errors and no unresolved critical contradictions; scientific sign-off still belongs to humans.
- PASS_WITH_WARNINGS: package is usable for review but limitations remain.
- BLOCKED: a central source, identity, measurement, literature or dependency issue prevents a responsible recommendation.

Never describe the result as scientifically proven because Python validators passed. Preserve all warnings and the human decision status in the final report.
