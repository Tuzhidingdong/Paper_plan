# V5.1 Researcher-Facing Delivery Standard

## Purpose

This standard governs the document that Paper_plan delivers to the researcher. It converts the Skill's internal scientific analysis into a professional manuscript-development and research-execution plan that a principal investigator can review, a student can understand, and collaborators can use to prepare and return the required work.

This is a domain-neutral product standard. It defines the quality and function of the report, not a fixed scientific story, discipline, journal, method list, figure count, section count or page count.

## 1. Two distinct output layers

Paper_plan maintains two synchronized but separate layers.

### 1.1 Primary product: the researcher-facing plan

The primary product is a standalone, well-written research report. It explains:

- why the research problem matters;
- what the supplied evidence actually establishes and what remains uncertain;
- what the closest literature has already established;
- what contribution the proposed paper can defensibly make;
- how the complete manuscript should develop its argument;
- what each main figure and supporting item should show;
- what research, analysis and computation remain necessary;
- how each task should be carried out, evaluated and returned to the manuscript;
- how work should be prioritized and assigned.

A reader must be able to understand and use this document without opening JSON bundles, logs, validator output or workflow state.

### 1.2 Supporting layer: internal records

The following belong in separate workspace records or an explicitly requested technical appendix, not in the main researcher-facing narrative:

- workflow-stage names and completion traces;
- Skill, commit, worktree, runtime and validator metadata;
- schema names, bundle names, internal entity IDs and raw Data Slot identifiers;
- implementation/debugging notes and tool errors;
- internal route labels or decision enums such as `HYBRID`, `CONDITIONAL`, `FALLBACK`, `STOP/DEFER`;
- product QA enums such as `PLAN_PRODUCT_STATUS`, `SCIENTIFIC_READINESS` and `BENCHMARK_COMPARISON`;
- validator PASS/FAIL summaries and structural-validation details;
- raw search-query histories and provider diagnostics;
- benchmark-comparison matrices and developer acceptance notes.

Keep these records. They are important for traceability and development. Do not expose them by pasting them into the main plan. Convert only their scientific meaning into clear researcher-facing language.

Scientific uncertainty must never be hidden. Translate an internal state into its practical consequence. For example, instead of writing "BLOCKED_BY_MISSING_INPUT", explain which information or material is missing, why work cannot proceed without it, who can provide it, and what can be done in the meantime. Instead of writing "CONDITIONAL", explain which conclusion is currently supported, which evidence is still needed, and what result would justify proceeding or changing direction. Do not replace uncertainty with confident prose.

## 2. Audience and voice

Write for two connected audiences:

- **Supervisor / principal investigator:** needs a defensible scientific rationale, a coherent paper argument, evidence limitations, resource priorities, risks and decisions requiring approval.
- **Student / research collaborator:** needs a clear objective, scientific reason, inputs, study design, records to keep, analyses to perform, files to return, and criteria for deciding whether the task is complete.

Use the user's preferred language for the plan. The default voice is professional scientific prose: direct, specific, explanatory and measured. Avoid software-development language, agent self-description, generic coaching, marketing language, inflated claims and unexplained abbreviations.

The plan should read like a research group's internal scientific proposal and manuscript-development dossier—not like an audit of an AI tool, a schema export, a meeting transcript or a validator report.

## 3. Recommended document architecture

Adapt the architecture to the project's actual needs. A substantive full-paper project will normally need the following components, but may combine, split, reorder or omit sections with a clear scientific reason.

1. **Project title and executive recommendation.** Give a meaningful working title and a concise narrative recommendation. State the central research question, why the paper is worth pursuing, the main evidence currently available, the most important limitation and the recommended next step.
2. **Scientific background and rationale.** Explain the field context, practical or theoretical problem, limitations of current approaches, and why the unresolved problem matters. Build a logical argument rather than a generic introduction to the discipline.
3. **Current research basis.** Interpret the actual supplied findings as a connected body of evidence. Identify the most informative observations, their sources and reliability, what can be concluded now, what cannot be concluded, and which missing data materially affect the paper.
4. **Literature position and contribution.** Explain the most relevant prior work in prose, compare the closest studies on the dimensions that matter, and state the precise scientific distinction the project can attempt to establish. A comparison table may support the discussion but must not replace it.
5. **Research question, hypotheses and objectives.** State the central question and any testable hypotheses, their basis, competing explanations, objectives and the observations that would support, weaken or reject them.
6. **Manuscript development blueprint.** Set out the working title, abstract argument, Introduction sequence, Results/Discussion story, conclusion logic and relevant methods content. Develop actual paragraph-level messages and transitions. Draft manuscript prose where the evidence and references justify it.
7. **Main figures and graphical summary.** Explain the figure sequence as the visual proof of the paper. Specify every Figure and Panel in enough detail to guide data assembly and figure preparation.
8. **Supporting Information.** Define the actual supplementary text, tables, figures, methods and validation material needed, and explain what each item supports in the main paper.
9. **Research and analysis programme.** Provide task briefs that can be assigned to students or collaborators. Distinguish essential decision-making work from later mechanism, generalization or application studies.
10. **Theory and computational studies, where relevant.** Provide concrete collaborator handoffs only when computation has a defined role in resolving a scientific question.
11. **Execution sequence, risks and decision points.** Explain what must happen first, which tasks can proceed in parallel, what each result unlocks, and when the project should be narrowed or stopped.
12. **Supervisor decisions and team responsibilities.** Present only decisions that genuinely require human approval and define the expected return from each assigned role.
13. **References and supporting records.** Give complete usable references and identify supplementary ledgers or data records by readable name and location.

This architecture is not a mandatory checklist. Select the form that best explains the science and organizes the work. Do not create empty sections merely to match a template.

## 4. Required depth of scientific reasoning

### 4.1 Research diagnosis

Do not list extracted observations without explaining their scientific meaning. For every important observation, explain:

- what was measured or reported;
- which source and conditions it comes from;
- whether it is direct, derived, estimated, qualitative or inferred;
- how reliable and comparable it is;
- what it supports and what it does not support;
- how it affects the proposed paper.

Separate established observations, reprocessed results, interpretations, hypotheses and future work. Explicitly discuss contradictions and data-quality issues only to the extent that they affect scientific conclusions or planned work.

### 4.2 Literature synthesis

Do not turn the literature section into a bibliography or a database-search diary. Write a connected account of how the field has developed, what the closest studies have demonstrated, where their systems or conclusions differ from the current project, and what remains unresolved.

For the most relevant prior studies, explain the actual system, research question, approach, conditions, measured quantities, principal findings and limitations at the level supported by the inspected source. Distinguish primary studies from reviews. A comparison table should clarify the argument, not carry it alone. Detailed queries and citation trails stay in the separate literature ledger.

### 4.3 Manuscript narrative

A manuscript storyline is not a list of characterization methods or proposed experiments. Organize it as a sequence of scientific questions:

- What does the reader need to understand first?
- What evidence establishes the system and its relevant starting state?
- What observation answers the next scientific question?
- Which alternative explanation must be excluded?
- Why does the next result follow logically?
- What is the strongest conclusion supported by the complete evidence?
- What remains outside the paper's defensible scope?

For each Results/Discussion section, supply a proposed heading or message, the paragraph-level argument, evidence/data required, comparisons and controls, intended inference, alternative interpretations and the transition to the next section. Where results do not yet exist, describe the planned evidence and alternative possible outcomes without writing an anticipated result as fact.

### 4.4 Figure and Panel planning

Every main-text Figure must have a reader-facing take-home message and a necessary role in the scientific argument. For each Panel, specify as applicable:

- the scientific question answered;
- the exact data or conceptual content to be assembled;
- source files, samples, conditions, time points or data products;
- grouping and comparison logic;
- plot, image, diagram or model format;
- axes, units, normalization, annotations and statistical presentation;
- required uncertainty, replicate or sampling information;
- the inference the Panel is intended to support;
- conclusions the Panel cannot support;
- related text, task and supplementary material;
- what would make the Panel scientifically interpretable.

Give composition guidance where it helps the figure designer: panel order, shared axes, aligned comparisons, inset/legend use, image pairing, color/label consistency and visual emphasis. Do not prescribe unsupported visual results or force every project into the same figure style.

### 4.5 Supporting Information planning

Do not provide only an item ID and title. For each planned item, say what data, method, derivation, calculation, control, extended analysis or reproducibility detail it contains; where the material will come from; which main-text claim or figure it supports; and what a reader should be able to verify from it.

### 4.6 Student- and collaborator-ready research tasks

A task is assignable only when its recipient can understand the purpose and return a usable result without reverse-engineering the Skill's internal data model.

For each important task, provide a readable task brief containing:

1. **Task title and intended role.**
2. **Scientific question and reason for doing it.** Identify the claim, uncertainty or alternative explanation the work addresses.
3. **Starting materials and information.** List what is already available, what must be requested or generated, and who is expected to provide it.
4. **Study design.** Define the experimental/computational unit, groups, conditions, variables, comparison basis, sampling/pairing and relevant controls. State unresolved design decisions explicitly.
5. **Method and practical considerations.** Explain the proposed approach sufficiently for planning and discussion with the responsible specialist. Do not invent local operating parameters or replace local SOP/safety approval.
6. **Records and data to retain.** Identify raw data, metadata, calibration, processing history, scripts, intermediate files and sample/condition records needed for reproducibility.
7. **Analysis and quality checks.** Explain calculations, normalization, statistics, uncertainty, validity checks and how questionable results will be handled.
8. **Expected return package.** Name the actual files, tables, plots, logs or model outputs to return, including a clear folder/file organization where useful.
9. **Completion criteria and interpretation.** State what constitutes a complete and usable result, and how positive, negative, mixed or inconclusive outcomes affect the scientific question.
10. **Manuscript destination and dependencies.** Explain which Results/Discussion section, Figure/Panel, SI item or decision uses the output, and which preceding inputs or approvals are required.

Unknown values remain explicit and should be assigned to the person or source able to resolve them. Do not invent sample amounts, instrument settings, replicate counts, statistical thresholds or timelines. A good task brief makes the remaining human decisions visible rather than disguising them.

### 4.7 Computational collaboration

A computational brief must go beyond naming a method. Where relevant, define the scientific question, model system, model construction, required structures/compositions, boundary conditions, states, method rationale, computational settings that can be justified, convergence and sensitivity checks, observables, expected raw and processed outputs, validation against experiments, alternative models and limitations. State exactly which manuscript claim and figure the calculation is intended to support. If essential inputs are absent, identify them and explain what can be done before computation begins.

## 5. Writing and editorial process

The Agent must perform a deliberate synthesis and editing process. Do not export the intermediate planning tables as the final report.

### Pass 1 — Scientific synthesis

Build an internal map linking evidence, prior work, the central question, manuscript sections, figures, supplementary items and research tasks. Resolve contradictions and identify missing links before drafting.

### Pass 2 — Narrative drafting

Write the report in complete, connected prose. Each major section should contain an argument, not merely a topic label. Use tables for dense comparisons, figure inventories and assignments, but introduce and interpret them in prose.

### Pass 3 — Execution design

Expand high-priority tasks into complete student/collaborator briefs. Connect every returned dataset or calculation to a specific scientific decision and manuscript location. Keep longer-term optional work separate from the minimum work needed to decide whether the central paper is viable.

### Pass 4 — Editorial integration

Read the plan as a supervisor, then as a student receiving an assignment. Revise for:

- scientific narrative and transitions;
- evidence and citation accuracy;
- consistency among title, contribution, abstract, Results/Discussion, Figures, SI and tasks;
- explanatory depth and specificity;
- plain, unambiguous wording and defined abbreviations;
- removal of repeated content, unexplained IDs, status codes, internal jargon and implementation notes;
- clear distinction between completed evidence and proposed work;
- explicit ownership of every unresolved decision.

Do not pass the plan merely because every section exists. If the report remains mostly short bullets, empty headings, status labels, task IDs or repeated tables, continue writing and integration.

## 6. Translating internal analysis into researcher-facing language

Internal records may contain compact state labels. The primary plan must communicate their practical meaning.

| Internal representation | Researcher-facing treatment |
|---|---|
| A route was labelled `HYBRID` or `CONDITIONAL` | Explain the selected scientific question and why its evidence path is appropriate. Do not expose the route enum. |
| A task is `BLOCKED` | Explain the missing input, why it is required, who can provide it and what work can proceed meanwhile. |
| An evidence item is `NOT_ASSESSABLE` | Explain what the source does not allow the team to determine and what additional evidence would resolve it. |
| A validator returned `PASS` | Omit from the scientific report. Keep the result in the separate technical record. |
| A work package uses `T001` or an internal entity ID | Give it a meaningful task title. Use a short human-readable work-package label only when it helps team coordination. |
| A benchmark comparison is unavailable | Record this in the separate review record. Do not insert software-product QA states into the scientific plan. |
| A citation lead is unresolved | Explain which bibliographic detail or source access is missing and how it affects the literature conclusion. |

This translation must not weaken the science. Keep genuine limitations, uncertainty, alternative explanations and human decisions explicit.

## 7. Product boundaries and adaptation

- The report is a manuscript-development and research-execution plan, not a completed manuscript or a guarantee of publication.
- The plan must be grounded in the user's actual evidence and current literature. Do not invent findings or write speculative expected results as observations.
- The exact document architecture follows the project, discipline, evidence and user requirements. No fixed number of Figures, Panels, experiments, calculations or supplementary items is prescribed.
- Journal requirements are project-specific and must be verified from current official sources. If the target or article type is unknown, state this in normal language and explain which aspects of the plan remain journal-dependent.
- Internal status records and audit ledgers remain available as supplementary files, but the main report must stand alone.
- The plan should be as detailed as the project requires. Do not inflate it with filler, duplicate audit tables or repeated descriptions merely to increase page count.

## 8. Final output boundary

The researcher-facing package normally contains:
- a polished editable Markdown plan;
- a PDF exported from that exact Markdown revision;
- necessary scientific appendices such as a literature ledger, evidence register or detailed collaborator brief when these are useful to the research team.

Internal QA and run metadata belong in a separate internal workspace location. They are not part of the main plan and should not be presented as the scientific deliverable unless the user explicitly requests a technical audit package.
