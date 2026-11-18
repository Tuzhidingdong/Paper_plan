# 08 — Target Journal Profile and Manuscript Fit

## Objective

Translate the user's target journal and article type into a current, cited requirement profile that informs the research plan and manuscript package. Journal rules are runtime facts, not hard-coded Skill defaults.

## 1. Establish the target

- Use the exact journal name and article type explicitly supplied for the **current project**. Record its provenance (current user instruction/project brief or explicit current test-run configuration).
- Do not infer the target from a benchmark example, prior project, previous run, saved memory, template default or journal selected for another discipline.
- A benchmark may carry a target journal as part of its case-specific quality context. Use it only when the current run explicitly declares that benchmark's journal as the target for this same test case; it never establishes a default for later projects.
- If no target is supplied for the current project, do not silently choose one. Ask the user or keep it unresolved. Offer a provisional shortlist only when the user requests/authorizes journal recommendation or selection. Article type is a separate input and may remain unresolved.
- Distinguish a target journal from a fallback journal. Do not optimize simultaneously for incompatible formats without explaining the trade-off.

## 2. Verify current requirements

Use live web/search tools where available. Prefer official journal and publisher sources:
1. aims and scope / journal overview;
2. current author instructions for the selected article type;
3. current guidance for figures, graphical abstracts/TOC, Supporting Information and references;
4. relevant policies for data availability, reporting, ethics, disclosures and supplementary files.

For every source, allocate a Python-issued journal-source ID and record title, exact URL, access date, source type and the requirement it supports.

Capture only requirements that affect this manuscript, including where available:
- accepted article types and journal scope;
- title, abstract and keyword constraints;
- main-text structure and section conventions;
- word/page limits;
- main-text figure/table limits and format;
- TOC or graphical abstract requirement, dimensions and content constraints;
- Supporting Information organization and file formats;
- reference and citation format;
- data/materials availability and reporting expectations;
- relevant policy or ethics statements.

Do not guess values that are hidden, ambiguous or not present in the official instructions. Record them as unknown and explain how that uncertainty affects planning.

## 3. Build the journal profile

Store the target journal, its provenance, article type, checked date, source IDs, verified requirements, unresolved requirements and access limitations in the Manuscript Development Bundle. Distinguish USER_SPECIFIED_CURRENT_PROJECT, EXPLICIT_TEST_RUN_CONFIGURATION, USER_AUTHORIZED_SELECTION and UNRESOLVED. Never persist a benchmark-only journal as a project default.

Status:
- VERIFIED: the relevant current official/publisher instructions were inspected and linked.
- PARTIAL: relevant requirements were found but important items remain unresolved.
- UNVERIFIED: no adequate current source was inspected.

A link existing is not proof that its contents were checked. Preserve source access status and exact page/section where practical.

## 4. Evaluate manuscript fit

Assess fit against:
- topic and system scope;
- audience and expected contribution type;
- novelty relative to closest competitors;
- strength and completeness of evidence;
- mechanistic depth or methodological advance expected by the journal;
- environmental, engineering, clinical, physical or other impact dimension only where relevant to that field;
- article type and format constraints.

For each dimension state evidence, concern and confidence. Do not assign pseudo-precise scores without a defined rubric. Avoid claims of guaranteed acceptance or guaranteed reviewer response.

## 5. Translate requirements into the plan

Explicitly state:
- which requirements affect the manuscript structure;
- which Figures, Tables or TOC elements are needed;
- what should be in main text versus SI;
- whether a planned item is required, optional or merely useful;
- what cannot yet be verified.

Recheck the official instructions before final submission if a substantial time has passed. The stored profile is a dated snapshot, not a permanent rulebook.
