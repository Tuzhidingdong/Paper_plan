# 11 — Experiment, Analysis and Computation Work Packages

## Objective

Turn the visual and argument architecture into actionable work packages that can be assigned to students, laboratory staff or collaborators. A technique list is not an execution plan.

## 1. Trace each work package backwards

Every task must identify:
- the central claim or uncertainty it addresses;
- the Data Slot it fills;
- the Figure/Panel or SI item that will use its output;
- why existing evidence is insufficient;
- the decision that depends on the result.

Do not create tasks that have no manuscript or scientific purpose unless they are justified as risk-reduction or exploratory work.

## 2. Experiment work package

Specify:
- objective and testable question;
- source sample identity and mapping confidence;
- independent variable(s), controlled variable(s) and response variable(s);
- experimental groups, controls, blanks and comparison design;
- method and measurement principle;
- equipment or resources only when actually known;
- required sample amount and conditions as confirmed values or explicit TBD;
- replicate and statistical plan, including what must be decided by the supervisor;
- calibration, blank correction, uncertainty and quality-control requirements;
- original/native data and metadata to retain;
- data processing and output schema;
- expected outcomes under competing explanations;
- measurable completion criteria, risks and fallback action.

The workflow must not silently convert literature conditions into a local protocol. Safety, equipment access, sample availability and operating parameters require local confirmation.

## 3. Analysis work package

Specify input files and their provenance, transformations, software/method, parameters, controls, uncertainty propagation, diagnostic checks, output files and interpretation limits.

Derived plots or fits from the same raw observation are not independent experimental replicates. Keep raw data immutable and version all processed outputs.

## 4. Theory/computation handoff

A computation package must be detailed enough for a collaborator to judge feasibility before starting.

Include:
- scientific question and target claim;
- system identity, phase/composition/structure and provenance;
- model construction and alternatives;
- relevant charge, protonation, spin, solvent, temperature, boundary and surface assumptions where applicable;
- method/model choice and why it is fit for the question;
- convergence and sensitivity tests;
- observables and exact quantities to extract;
- comparison/control calculations;
- validation against available experimental evidence;
- required input files and expected native outputs;
- software/resource assumptions only if confirmed;
- prerequisites, risks and stop criteria.

For computational chemistry or physics, distinguish a calculation that is scientifically interesting from one that can be executed with validated inputs. Missing structures, compositions, surface states, solvent models, boundary conditions or experimental validation may block work. Record exact blockers and prerequisite task IDs.

## 5. Dependency and priority

Use P0 for validity of the central claim or route viability; P1 for major mechanism/comparability/confounder support; P2 for optional extensions. These are priorities, not fixed chronological durations.

Build an acyclic dependency graph. A blocked calculation cannot be marked ready until required inputs are obtained and reviewed. Do not assign artificial deadlines; report sequencing and effort only when supportable.

## 6. Handoff-ready output

Each work package should have a short assignment brief plus its structured record. Include required input manifest, expected deliverable names/formats, completion criteria, decision owner and the person/role expected to perform the work. Use TBD explicitly for unknown details.

## 7. Execution readiness and decision frameworks

A work package must distinguish a scientific task that is worth planning from a protocol that is locally executable. Use the structured `execution_design.readiness` state:
- `NOT_ASSESSED`, `DRAFT`, `BLOCKED`: planning is incomplete or blocked.
- `READY_FOR_SUPERVISOR_APPROVAL`: the design is sufficiently specified for a supervisor/lab feasibility and safety decision; it is not yet approved to run.
- `APPROVED_FOR_EXECUTION`: a human decision has been recorded, local feasibility is confirmed, all required inputs are available and local safety/feasibility review is documented.

A supervisor-ready experiment brief must state the method and measurement principle; independent, controlled and response variables; groups and controls; required inputs and their availability; native outputs; QC/acceptance criteria; replicate/statistical and uncertainty plans; responsible role; decision owner; risks and fallback. Unknown parameters remain TBD and prevent the package from claiming execution approval. Never infer local feasibility or safety from a literature method.

## 8. Agreement and equivalence questions

When the scientific question asks whether two methods or endpoints agree, or whether an effect is equivalent within an acceptable margin, correlation alone is insufficient. Before execution, define the primary estimand and analysis population, an appropriate analysis method, agreement/equivalence method where applicable, an acceptance boundary and its scientific/metrological/user-approved basis, assumptions, uncertainty treatment and rules for supportive, contradictory/weakening and inconclusive results.

Do not invent an acceptance margin or interpret a merely intermediate result as evidence for a specific mechanism or confounder. If the boundary cannot yet be justified, record it as unresolved and keep the task at DRAFT/BLOCKED rather than marking the decision framework ready.

## 9. Dependency classes

Where different stages have different gates, distinguish `execution_prerequisite_ids` (must be complete before work can start), `interpretation_prerequisite_ids` (needed before a result can be interpreted or a claim assessed), and `publication_prerequisite_ids` (needed for journal positioning, manuscript finalization or submission).

The legacy `prerequisites` list remains the union of the three classes. A publication-only prerequisite must not automatically block starting an otherwise approved experiment. An APPROVED_FOR_EXECUTION task must have all execution prerequisites completed. Priority should be consistent with dependency urgency; flag lower-priority execution prerequisites for review.
