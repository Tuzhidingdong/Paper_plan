# 06 — Final Research Plan and Execution Deliverables

## Required package

1. Evidence report: what the PDF shows, confidence, missing/unclear evidence and limitations.
2. Literature frontier: searchable bibliography, access tiers, direct competitors, counter-evidence, bounded gaps and references.
3. Three research routes: comparison matrix, recommended provisional route and novelty/feasibility risk.
4. Data-centric manuscript framework: Claim–Evidence graph, Data Slot table, Data Units and lineage, section logic and conceptual figure/panel plan.
5. English Introduction draft: 4–6 coherent paragraphs where evidence and citations are verified; do not invent data or cite metadata-only records for technical statements.
6. Prioritized experiment and analysis plan; theory/computation plan only where inputs exist.
7. Student-facing self-check message: natural, supportive and question-oriented, with no accusation.
8. Cross-bundle validation report and editable Markdown.
9. Verified PDF export of the consolidated final research plan.

## Experiment task specification

Every task must have a Python-issued Task ID and include:
- objective and scientific reason;
- target Claim IDs and Data Slot IDs;
- existing evidence and exact missing evidence;
- sample IDs/aliases and mapping confidence;
- experimental system, variables and conditions (unknown values explicitly marked TBD);
- controls, blanks and comparison groups;
- measurements, instruments and required raw-data formats;
- replicate/statistical plan, or explicitly state that the count requires supervisor/lab confirmation;
- data processing, quality criteria and acceptance/completion criteria;
- prerequisites, dependencies and priority;
- expected output, uncertainty/risk, safety/feasibility notes;
- intended manuscript section and conceptual figure/panel slot.

Do not invent concentrations, temperatures, equipment availability, sample quantities or replicate counts. Use ranges only when supported by literature and mark them as proposed starting conditions requiring confirmation.

## Theory/computation gate

A calculation task must specify the target hypothesis, model, composition/structure, input data, boundary conditions, method/software rationale, convergence/validation criteria and expected output. If the actual sample structure, stoichiometry, surface, solvent, interface or other required input is unknown and must be experimentally determined, set status BLOCKED_BY_EXPERIMENT, list the prerequisite Task IDs and do not present the calculation as immediately executable.

Never recommend DFT/MD/GNN merely to make the plan look advanced. Explain what experiment or hypothesis the computation discriminates.

## Student-facing message

Use a short, friendly message. Phrase gaps as “could you help check whether…” or “do we have the original…?” Never say an experiment was wrong merely because the report does not show a condition. Ask for original raw files, labels, metadata or sample mapping only where these would resolve a named uncertainty.

## Cross-check before export

- Every main scientific claim links to evidence or a verified literature claim.
- Every route gap links to a bounded search record and counter-evidence.
- Every Data Slot targets an existing Claim.
- Every Data Unit records Result Unit lineage.
- Every missing/blocked essential slot has a task or an explicit reason why no feasible task is proposed.
- Every task targets at least one Data Slot and includes completion criteria.
- Calculation gates and sample-mapping dependencies are correct.
- No literature source is represented as full text unless it was opened and checked.
- Gate A and Gate B states reflect actual human decisions.
- Exported Markdown and PDF have the same revision and content; reopen the PDF and verify page count/text extraction.
