# Research Manuscript Development and Execution Plan

> This is the primary researcher-facing deliverable. Write a complete, evidence-grounded scientific plan in the user's preferred language. Replace every instruction with project-specific reasoning. Do not leave a blank form, a bundle summary, a query log or an internal QA report. Adapt the structure and depth to the actual project. Omit irrelevant components with a scientific reason; never invent information.

## Project

**Project title:**  
**Working manuscript title:**  
**Research field / system:**  
**Target journal and article type:**  
**Plan date:**  
**Research materials considered:**  

Do not put Skill commits, worktree paths, validator names, schema versions or internal runtime metadata on this researcher-facing cover page. Keep them in the separate run record.

## Executive summary and recommendation

Write a concise but substantive overview for the supervisor and research team. Explain the scientific problem, the central question the proposed paper will answer, why the question matters, what the current evidence indicates, what is not yet established, and the recommended path forward. State the most important next decision or action and why it has priority.

The summary must be understandable without reading the rest of the plan, but must not overstate what the evidence shows.

### Proposed scientific contribution

State one bounded contribution in complete prose. Explain how it differs from the closest known work and what new understanding the paper would add. If no defensible contribution can yet be stated, explain why and what evidence could change that conclusion.

### Current position

Distinguish what the team has already demonstrated, what has been reprocessed or interpreted, what remains a hypothesis, and what evidence must still be acquired. Explain the practical implications for the paper and the research programme.

## 1. Scientific background and research rationale

Build a logical account of the field and the specific problem. Explain:

- the broader scientific or technological context;
- the unresolved problem or limitation that motivates this project;
- why current knowledge or methods do not adequately answer it;
- why resolving the problem matters scientifically and, where relevant, practically;
- how the project system and available research materials relate to the problem.

Avoid generic textbook introductions. Each paragraph should move the reader toward the specific research question.

## 2. Existing research basis and evidence interpretation

Explain what the supplied materials actually show, in the order most useful for understanding the research—not simply in file order or instrument order.

For each important finding, describe the observation, source, conditions, measurement or derivation, reliability, limitations and scientific meaning. Explain whether different samples or conditions are genuinely comparable. Distinguish direct measurements from derived quantities, estimates and interpretations.

A concise evidence table may be used:

| Finding / observation | Source and conditions | What it supports | Reliability and limitations | Further evidence needed |
|---|---|---|---|---|

After the table, synthesize the findings in prose. Identify which observations provide the strongest basis for the proposed contribution, which are only contextual, which need reanalysis, and which cannot support the desired interpretation. Discuss contradictions and alternative explanations where they change the scientific conclusion.

Do not expose raw internal entity IDs in place of source descriptions. Cite readable file names, page/figure/table locations, dataset identifiers or bibliographic sources that the research team can locate.

## 3. Research frontier and position relative to prior work

Tell the story of how the relevant field has developed. Organize the discussion around the scientific questions, approaches and results that matter to this project.

For the closest primary studies, explain their actual systems, research questions, experimental or theoretical approaches, conditions, measured quantities, main findings and limitations to the extent supported by the inspected source. Identify what has already been established, what differs between those studies and the current project, and what the current project could add.

A comparison table can make the distinctions clear:

| Closest study | System and conditions | What it demonstrated | Relationship to this project | Remaining distinction |
|---|---|---|---|---|

Do not let the table replace the scientific discussion. Include contradictory or competing explanations. Distinguish primary research from reviews and distinguish full-text-supported conclusions from conclusions based only on abstracts or metadata.

### Defensible novelty and its limits

State the narrowest contribution that remains scientifically meaningful after comparison with the closest work. Explain exactly which dimension is new or potentially new and which aspects are already known or incremental. Avoid unsupported priority claims such as "first", "unprecedented" or "no studies have reported".

Explain what literature finding would materially weaken or remove the proposed novelty. Refer to the separate literature search ledger for exact queries and citation trails, but keep the scientific interpretation in this plan.

## 4. Central scientific question, hypotheses and objectives

State the central research question and explain why it follows from the existing evidence and literature.

Where appropriate, define testable hypotheses and predictions. For each, identify:

- its scientific basis;
- the observations or relationships that would support it;
- plausible alternative explanations;
- the result that would weaken or reject it;
- the scope within which the hypothesis is being tested.

List the research objectives in a logical order. Separate the minimum objectives needed to answer the central question from optional extensions that would broaden mechanism, generality or application.

Explain the intended scientific contribution and its limits in ordinary research language. Do not expose internal candidate-route labels or software decision categories.

## 5. Manuscript development blueprint

This section describes the paper the team is planning to write. It must be a connected narrative, not simply a list of headings.

### 5.1 Working title and abstract argument

Provide a working title that reflects the evidence level. Map the abstract from the problem and gap through the approach, principal evidence, defensible finding and significance. Where the decisive findings are not yet available, identify which parts of the abstract must remain unwritten until the results exist.

### 5.2 Introduction: paragraph sequence and draft

For each planned paragraph, explain its reader-facing purpose, main message, literature support, limitation or tension, and transition to the next paragraph. The sequence should narrow from the field-level problem to the closest prior work, the precise unresolved question and the contribution of this study.

Where the evidence and verified literature permit, provide coherent draft prose in manuscript-ready English. Do not leave only notes such as "add literature here" or citation placeholders where a source could reasonably be identified and verified. Where a citation or factual premise genuinely remains unresolved, mark the exact gap and explain what must be checked before submission.

### 5.3 Results and Discussion: complete scientific storyline

Organize the planned sections by the logic of scientific proof and reader comprehension. Do not arrange the paper merely by instrument, characterization method or file order.

For each major section or paragraph cluster, provide:

1. a proposed heading or clear take-home message;
2. the scientific question it answers and why that question comes at this point;
3. the existing or planned evidence, including source and status;
4. the comparison, control or analysis needed to interpret it;
5. the inference the result could support and its limits;
6. the main alternative interpretation and how it will be evaluated;
7. the Figure/Panel and supplementary information that carry the evidence;
8. how the section advances the central contribution and leads to the next section.

Where results are not yet available, describe the planned analysis and the materially different possible outcomes. Do not write expected outcomes as observed facts.

### 5.4 Conclusion and final paper message

Explain how the conclusion should answer the central question, define the boundary of the finding, relate it to prior work and identify implications that are actually supported. Separate demonstrated conclusions from future hypotheses and applications.

### 5.5 Methods and reproducibility content

Identify the experimental, analytical, statistical and computational methods that require sufficient detail for reproducibility. Explain which records, calibration details, processing methods, model settings or uncertainty information must be retained. Keep journal-specific formatting details conditional on verified current instructions.

## 6. Main figures and graphical summary

Explain how the figures collectively tell the scientific story. The sequence should follow the reader's needs: establish the system or premise, present the decisive evidence, discriminate between explanations, and support the final interpretation. Adapt the number and order of figures to the project; do not force a conventional count.

### Overall figure sequence

| Figure | Reader-facing message | Role in the argument | Main evidence | Related manuscript section |
|---|---|---|---|---|

### Detailed Figure and Panel specifications

For each Figure, provide its intended message, why it is needed, its place in the story and the proposed visual composition. Then specify every Panel:

| Panel | Scientific question and content | Data/source and current status | Groups, conditions and comparison | Plot/image/diagram and analysis | Intended inference and limitation | Related task/SI |
|---|---|---|---|---|---|---|

For each Panel, explain as applicable:

- exact data columns, images, observations or model outputs to assemble;
- sample groups, conditions, time points and matching/comparability requirements;
- x/y variables, units, normalization, colour/shape encoding and annotations;
- statistical summaries, uncertainty, replicate display and relevant tests;
- image selection, scale information, pairing and acquisition comparability;
- panel order, shared axes, layout, legends, insets and visual emphasis;
- the conclusion the Panel is meant to support and what it cannot establish.

Do not invent unavailable values or make planned panels look like completed results. Where a dataset, sample identity, comparison or analysis is missing, explain exactly what needs to be obtained before the Panel can be made.

### Graphical abstract / TOC concept

When useful or required for the intended publication, describe the scientific message and visual elements in a way that a designer can use. Distinguish a conceptual brief from completed artwork. If journal requirements are unverified, do not state them as facts.

## 7. Supporting Information plan

List the specific supplementary materials needed to make the paper transparent and reproducible.

| Proposed item | Actual contents | Source or task producing it | Why it belongs in SI | Main-text claim/Figure supported | Required checks |
|---|---|---|---|---|---|

For every item, explain what it contains, how it will be prepared, what the reader should be able to verify, and how it supports the main paper. Include raw-data summaries, extended figures, methods, derivations, controls and reproducibility information when relevant. Do not hide evidence essential to the central argument in SI merely to simplify the main text.

## 8. Research, reanalysis and experimental work programme

Present the research needed to deliver the proposed paper. Organize work by scientific purpose and dependency, not by a generic catalogue of techniques.

Separate:
- the smallest set of tasks that can decide whether the central research question is worth pursuing;
- the additional evidence needed for a publication-strength result;
- optional mechanistic, generalization or application studies.

### Individual task briefs

For every important task, provide a complete brief in a consistent, readable format.

#### [Task title]

**Why this task is needed.** Identify the scientific question, claim or uncertainty it addresses and explain how it affects the manuscript.

**Starting materials and required inputs.** List available samples, datasets, records, structures, methods and references. Identify missing information, who can supply it and whether work can begin without it.

**Study design.** Describe the experimental or analytical unit, groups, variables, conditions, comparison basis, pairing/sampling approach, controls and relevant confounders. Explain why the proposed design can distinguish the competing explanations. Keep unconfirmed values and local operating details open for the responsible specialist.

**Execution and records.** Describe the intended workflow at an appropriate planning level. State what must be recorded during sample preparation, acquisition, processing, storage, calculation or transfer so that the result can be interpreted and reproduced. Do not replace local SOPs, safety review or specialist decisions.

**Analysis and quality assessment.** Specify the calculations, normalizations, statistics, uncertainty estimates, validation checks and failure checks needed. Explain how data quality and comparability will be judged without inventing acceptance thresholds.

**Required return package.** Name the raw files, processed data, tables, plots, scripts, model inputs/outputs, metadata and short interpretation note that the student or collaborator must return. Use clear file types and organization where useful.

**How the result will be used.** Identify the manuscript section, Figure/Panel, SI item or decision that depends on this task.

**Interpretation and next step.** Explain how supportive, negative, mixed or inconclusive findings would affect the central hypothesis, the next experiment and the manuscript scope.

**Dependencies and completion criteria.** Identify prerequisites, approvals and the concrete outputs that make the task complete and usable.

Repeat the task brief for all material work. Do not compress high-priority tasks into one-line entries. If some local design decisions cannot be made from the supplied material, identify the precise question for the supervisor or responsible specialist.

## 9. Theory and computational collaboration

Include this section only when theory or computation can resolve a named scientific question or discriminate between plausible explanations.

For each calculation, give a collaborator-ready brief:

- scientific question and the experimental interpretation it addresses;
- model system and construction strategy;
- required structures, compositions, configurations and source of each input;
- relevant states, boundaries, environment and assumptions;
- method selection and justification;
- parameters that are source-supported versus those requiring specialist decision;
- convergence, sensitivity, sampling and alternative-model checks;
- physical observables and analysis to be returned;
- expected raw outputs, processed files, scripts and reproducibility records;
- comparison with experimental observations and validation limits;
- manuscript section, Figure/Panel and conclusion that the calculation informs;
- explicit prerequisites and the work that remains possible before those inputs are available.

A method name or a request to "perform DFT/MD" is not an adequate handoff. Do not include computation that does not change a scientific decision or materially strengthen the paper.

## 10. Execution sequence, priorities and responsibilities

Organize the project into a dependency-aware sequence. Distinguish work that can proceed in parallel from work that must wait for earlier results.

| Order / priority | Research task | Responsible role | Required input | Expected return | Decision or manuscript element unlocked | Completion condition |
|---|---|---|---|---|---|---|

Explain why the order is efficient and scientifically appropriate. Identify which early result should trigger continuation, redesign or stopping. Do not invent calendar durations or deadlines without project information.

## 11. Risks, alternative outcomes and scope control

Discuss the material risks to the paper: scientific alternatives, literature overlap, measurement validity, sample or dataset limitations, feasibility, computational assumptions and publication fit. For each risk, explain how it could affect the contribution, how it can be detected, and what adjustment would be appropriate.

Describe credible alternative outcomes and how the paper would change under each. Avoid planning the paper around only the preferred result.

## 12. Decisions for the supervisor and team assignment

Present the genuine decisions requiring supervisor or specialist input, with the evidence and trade-offs needed to make each decision.

Then provide a clear assignment summary for the research team:

| Responsible person/role | Assigned work | Materials or decisions needed | Return files/results | Manuscript use |
|---|---|---|---|---|

Use role descriptions where individual names are not known. Do not imply that unapproved work has been authorized.

## References and supporting research records

List complete references actually used in the scientific argument. Include title, authors, venue, year, DOI or stable URL where verified. Make source limitations clear when only an abstract or bibliographic record was available.

Point to the separate literature audit ledger or evidence register by a readable file name and path when those records are retained. Do not copy raw search logs or internal entity tables into the main body.

## Guidance for final writing

The finished document must read as a professional scientific research plan, not as this template. Delete all instructional text and unused headings. Do not include internal route enums, workflow stages, validator statuses, schema terms, runtime details or software-development commentary. Explain real scientific limitations in plain research language.

The plan should give a supervisor enough reasoning to evaluate the paper and give students enough information to understand and plan their assignments. Its depth should follow the complexity and evidence needs of the actual project, not a fixed page count.
