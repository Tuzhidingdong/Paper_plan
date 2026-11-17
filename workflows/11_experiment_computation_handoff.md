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
