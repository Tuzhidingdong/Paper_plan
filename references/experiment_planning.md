# Evidence-to-experiment planning

Every proposed task must resolve a named Claim/Data Slot, not merely add another characterization technique.

## Task design checklist
- What uncertainty or alternative explanation will this task discriminate?
- Which exact sample or preparation condition is needed, and is its identity confirmed?
- What controls, blanks and comparison samples are needed?
- Which variable is changed, which outputs are measured, and what remains controlled?
- What raw data must be retained (instrument-native files, calibration, metadata, processing settings)?
- What quality criterion makes the result interpretable?
- What result would support, weaken or falsify the target claim?
- What is the replicate/statistical plan? If unknown, explicitly request supervisor/lab confirmation instead of guessing.
- What task is prerequisite to another experiment or calculation?
- What is the task priority (P0/P1/P2) and where will the output be used in the manuscript?

## Priority
P0 resolves a central claim or determines whether the route is viable. P1 strengthens interpretation or controls a major confounder. P2 is an optional extension. Explain the ordering.

## Calculation prerequisites
DFT/MD/kinetic/thermodynamic models require explicit inputs and validation. A calculation is not ready merely because the topic sounds computational. Record structure/composition, charge/protonation, phases/surface/facets, solvent/electrolyte, temperature, boundary conditions, model rationale and validation data as relevant. Missing experimental inputs create BLOCKED_BY_EXPERIMENT status with named prerequisite task IDs.

## No fabricated protocol details
Do not assume laboratory equipment, reagent purity, available sample mass, instrument access or safety procedures. Conditions copied from literature are proposed starting points, not validated local protocols. The student/supervisor must confirm feasibility and safety.

## Decision-ready experiment handoff

For a supervisor-ready experiment, state the measurement principle, independent/controlled/response variables, groups and controls, required inputs and availability, native outputs, QC/acceptance criteria, replicate/statistics and uncertainty plans, responsible role, decision owner, risks and fallback.

Use an explicit readiness state. A research brief with TBD parameters is not an approved protocol. `APPROVED_FOR_EXECUTION` requires human approval, confirmed local feasibility, all required inputs available and documented local safety/feasibility review.

For agreement or equivalence questions, correlation is not an agreement criterion. Predefine the primary estimand, appropriate analysis method, agreement/equivalence method, acceptance boundary and defensible basis, assumptions and support/contradict/inconclusive rules. If no justified boundary exists, keep the decision framework unresolved; do not invent one.

## Dependency classes

Separate execution, interpretation and publication prerequisites. Only execution prerequisites block execution readiness. Preserve the legacy `prerequisites` list as the union for backward compatibility. Publication readiness and scientific interpretation may remain gated after data acquisition without unnecessarily blocking the experiment itself.
