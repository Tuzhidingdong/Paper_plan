# 04 — Data-centric Manuscript Framework

## Organizing principle

Organize the paper around claims and evidence requirements, not around preassigned Figure numbers. Figure/panel numbering is assigned only after the Data Slots and evidence flow are stable.

## Claim–Evidence graph

Every Python-issued Claim ID records:
- concise claim text;
- epistemic status (Observed, Interpreted, Hypothesized);
- claim type (Descriptive, Comparative, Associational, Causal, Mechanistic);
- linked Result Unit IDs, Finding IDs and Literature Claim IDs;
- contradictory evidence, alternative explanations, scope limits and confidence;
- manuscript section where it belongs.

Causal or Mechanistic claims need discriminating evidence and a careful alternative-explanation audit. A report-level trend is not automatically an intrinsic material property or mechanism.

## Data Slots

Each Python-issued Data Slot ID is a requirement attached to a target Claim and manuscript section. It contains:
- required evidence and why it is needed;
- current status: FILLED, PARTIAL, MISSING or BLOCKED;
- existing Result Unit/Data Unit links;
- missing conditions, controls, statistics or raw data;
- acceptance criteria for a sufficient data unit;
- whether this is an essential, strengthening or optional slot.

A missing Data Slot is a planned requirement, never an existing result.

## Data Units and lineage

A Data Unit is a curated grouping or transformation of one or more Result Units. Record all source Result IDs, transformation steps, software/settings, exclusions and output. Several plots, fits or normalizations derived from the same raw observation remain one evidence lineage and must not be counted as independent experiments.

Keep source/raw, processed, selected-for-manuscript and unused/rejected data distinct. Never overwrite original data.

## Figure and section architecture

After Data Slots are stable, group them into conceptual Figure/Panel slots. For each planned figure specify the scientific message, target Claim IDs, Data Slot IDs, required comparisons, sample/condition labels and whether it belongs in main text or Supporting Information. Do not invent Figure numbers before ordering is decided.

Map Introduction, Results/Discussion, Methods, Conclusions and Supporting Information to the evidence graph. State which claims are ready, conditional or blocked.

## Gate B skeleton

Before long prose, produce a compact Claim–Citation skeleton and Data Slot table. The final draft may proceed for one-pass delivery, but approval_B remains PENDING_HUMAN_REVIEW until a human decision is supplied. Never silently approve the framework.
