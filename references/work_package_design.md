# Research work-package design reference

A work package is assignable and testable only when its purpose and completion condition are explicit.

## Minimum handoff record
- Objective and scientific rationale.
- Target Claim and Data Slot.
- Figure/Panel or SI destination.
- Required inputs and their availability.
- Variables, controls, comparisons and methods.
- Raw/native files and metadata to preserve.
- Replicates, statistics, calibration, uncertainty and QC.
- Possible outcomes and how each changes the interpretation.
- Dependencies, blockers, risks and fallback.
- Responsible role and measurable completion criteria.

## Computation-specific handoff
State the exact model/system, input structures or compositions, assumptions, methods, convergence checks, target observables, controls, validation plan, expected outputs and prerequisites. A named method or software package alone is not a computational task.

Unknown laboratory or computational parameters remain TBD. Do not fabricate local capabilities, protocols or execution timelines.

## Execution readiness and analysis decisions

A work package should include a readiness state, method, variables, groups/controls, required inputs and availability, native outputs, QC criteria, replication/statistics, uncertainty, responsible role, decision owner and risks/fallbacks. It is not approved for execution until local feasibility and safety are confirmed by the responsible human.

For agreement/equivalence studies, state the estimand, method, justified acceptance margin/boundary, basis for that boundary, assumptions and explicit rules for supportive, contradictory and inconclusive outcomes. Do not substitute correlation for agreement or infer a mechanism from an intermediate outcome.

Classify prerequisites as execution, interpretation or publication gates. The legacy prerequisite list is their union; publication work must not block otherwise approved data acquisition.


## Proxy and indirect-measurement validation

When a proxy, surrogate or indirect measurement is used to represent a target measurand, specify both measurement definitions separately and justify the reference basis and independence. Record the unit of analysis, pairing/matching, condition and time alignment, and the intended relationship (for example agreement, calibration or prediction). A relationship claim must have a primary estimand, suitable analysis, a defensible acceptance boundary and basis, uncertainty treatment and SUPPORTS / CONTRADICTS / INCONCLUSIVE outcomes.

Assess controls against plausible confounders and artefacts in the actual design. Declare required control classes and their planned implementation, or explain why no control is applicable; do not prescribe a universal control set. Likewise, state whether recovery/accounting closure is relevant and justify either choice. Distinguish reproduction of a fit from statistical diagnostics, internal validation, independent external validation and prospective validation. Independent validation must use a defensibly separate scope and protect against leakage.

Incomplete designs remain draft. A schema or validator can check that these decisions are recorded, but cannot certify that the chosen reference, controls, model or margin are scientifically correct.
