# 10 — Main Figures, Panels, TOC Graphic and Supporting Information

## Objective

Design the visual argument of the manuscript. Figure count, panel count, visual form and SI size must emerge from the science and current journal instructions.

## 1. Figure architecture

Plan the main Figures in narrative order. Do not use a fixed figure count or universal sequence.

For every Figure record:
- permanent Figure ID and working title;
- the exact scientific question it answers;
- one-sentence take-home message;
- claim IDs supported;
- why the Figure belongs in the main text;
- linked Data Slot IDs;
- its role in the storyline and how it leads to the next Figure;
- layout and comparison logic;
- unresolved evidence or interpretation risks.

A Figure should have one principal message. If it contains several unrelated messages, split or redesign it.

## 2. Panel-level specification

For each Panel specify:
- panel label and purpose;
- the data or visual content to be shown;
- source Result/Finding/Data Unit IDs for existing data;
- missing Data Slot IDs for new work;
- exact sample/condition/control comparisons;
- link a Comparability Assessment ID for cross-sample or cross-condition comparisons, including the dimensions matched, mismatched or unknown;
- variables and units to display;
- plot/image/table/conceptual-diagram type;
- statistical or image-processing treatment where relevant;
- acceptance criteria and the conclusion the panel can and cannot support.

Do not invent the presence of a dataset. Mark panels as existing, partial, new-data-required, conceptual or blocked. A proposed mechanism schematic must visually distinguish evidence-supported elements from hypotheses.

## 3. TOC / graphical abstract

First verify whether the current article type and journal require, permit or constrain a TOC/graphical abstract.

The concept should communicate the central contribution in one visual sequence. Specify:
- input/system and the relevant intervention or comparison;
- the mechanism or relationship only to the level actually supported;
- the decisive outcome;
- the broader implication, only if evidenced;
- visual hierarchy, required labels and prohibited unsupported claims.

Produce a concise handoff brief for a designer or image-generation stage. Do not embed project-specific details in the Skill template.

## 4. Supporting Information architecture

Plan SI as an organized support layer, not a dumping ground.

Typical categories may include methods, calibration/validation, raw and extended spectra/images, supplementary controls, additional conditions, detailed calculations, model convergence and extended statistics. Use only categories relevant to the study and journal.

For each SI item record:
- stable SI ID, type and title;
- claim(s) and Figure(s) it supports;
- linked Data Slot IDs;
- content and source data required;
- method/metadata needed for reproducibility;
- status and completion criteria.

Critical evidence for the central claim must remain visible in the main paper. SI cannot be used to hide contradictory evidence or a missing decisive control.

## 5. Cross-check

Every main Figure must appear in the storyline. Every Panel must link to a claim or a Data Slot. Every comparative Panel must link to a comparability assessment or explicitly state that comparability is unresolved. Every essential missing Data Slot must be placed in a Figure or SI item and linked to a task, or have an explicit reason for exclusion. Every SI item must support a claim, Figure or reproducibility requirement.

## 6. Data scope and reuse across Panels

When a Data Slot or source dataset is reused in more than one Panel, describe the scope for each Panel so that the reader can tell whether the Panels show distinct slices or duplicate the same material. Record applicable dimensions such as specimen/group set, condition set, timepoint or process stage, analysis population, processing level and source dataset IDs. If the same data are intentionally shown more than once for different analytical purposes, state the reuse rationale.

A reused Data Slot is not automatically a defect: a baseline and a derived analysis may legitimately use the same source measurements. However, identical or unspecified scope without a rationale must be flagged for human review.

## 7. Comparability states and inference boundaries

Use the states precisely:
- `COMPARABLE`: all dimensions required for the stated comparison have been assessed and are matched or not applicable.
- `CONDITIONALLY_COMPARABLE`: the comparison is limited by one or more known mismatches or unresolved dimensions; state the restricted inference.
- `NOT_COMPARABLE`: one or more required dimensions are mismatched or unknown such that the intended direct comparison is invalid.
- `NOT_ASSESSABLE`: available information is insufficient to judge the comparison itself; identify the missing information.
- `UNASSESSED`: no comparison assessment has yet been performed.

Do not turn NOT_COMPARABLE or NOT_ASSESSABLE into a claim of contradiction. State only what cannot be inferred. A contradiction requires independent, explicitly linked counter-evidence.
