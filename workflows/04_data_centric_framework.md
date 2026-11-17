# 04 — Data-centric Manuscript Framework

## Organizing principle

Organize the paper around claims and evidence requirements, not around preassigned Figure numbers. Figure/panel numbering is assigned only after Data Slots, central contribution and evidence flow are stable. The detailed visual architecture is completed in workflow 10 and persisted in the V4 Manuscript Development Bundle.

## Claim–Evidence graph

Every Python-issued Claim ID records:
- concise claim text;
- epistemic status (Observed, Interpreted, Hypothesized);
- claim type (Descriptive, Comparative, Associational, Causal, Mechanistic);
- linked Result Unit IDs, Finding IDs and Literature Claim IDs;
- contradictory evidence, alternative explanations, scope limits and confidence;
- manuscript section where it belongs.

Causal or Mechanistic claims need discriminating evidence and a careful alternative-explanation audit. A report-level trend is not automatically an intrinsic property or mechanism.

## Data Slots

Each Python-issued Data Slot ID is a requirement attached to a target Claim and manuscript section. It contains:
- required evidence and why it is needed;
- current status: FILLED, PARTIAL, MISSING or BLOCKED;
- existing Result Unit/Data Unit links;
- missing conditions, controls, statistics or raw data;
- acceptance criteria for a sufficient data unit;
- whether the slot is ESSENTIAL, STRENGTHENING or OPTIONAL.

A missing Data Slot is a planned requirement, never an existing result.

## Data Units and lineage

A Data Unit is a curated grouping or transformation of one or more Result Units. Record all source Result IDs, transformation steps, software/settings, exclusions and output. Several plots, fits or normalizations derived from the same raw observation remain one evidence lineage and must not be counted as independent experiments.

Keep source/raw, processed, selected-for-manuscript and unused/rejected data distinct. Never overwrite original data.

## Claim-to-manuscript integration

Before long prose, establish:
- the central contribution and its boundary;
- the claims needed to support it;
- evidence already available and missing Data Slots;
- the manuscript sections that carry each claim;
- the Figures/Panels and SI items that will present the evidence;
- the work packages that close essential gaps.

The V4 Manuscript Development Bundle stores the journal profile, Introduction paragraph entities, storyline steps, Figure/SI entities and references to Claims, Data Slots and tasks. Do not duplicate a Claim or task as an unrelated new entity.

## Gate B skeleton

Provide a compact Claim–Citation skeleton, Data Slot table and provisional manuscript storyline before full narrative. Gate B remains PENDING_HUMAN_REVIEW until a human decision is supplied. Never silently approve the framework.
