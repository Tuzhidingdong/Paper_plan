# Scientific argument synthesis: analysis → Finding → Claim

## Purpose

This procedure converts the recorded scientific analysis of the user's existing research outputs into a defensible manuscript argument. It is domain-neutral. It does not add new data, repeat source-document research, or replace expert scientific judgement.

The required chain is:

**source Region/Panel or supplied dataset → Result Unit → analysis observation/comparison/relationship/interpretation → Finding → manuscript Claim → route and central contribution → Results/Discussion, Figure/SI and work programme.**

The chain must be explicit enough that a reviewer can move from a central paper statement back to the exact source evidence and understand how the statement was derived.

## 1. Distil decision-relevant Findings

After the general scientific-analysis stage, review all analysis packs together, including their cross-pack links. Do not treat the model's pack summary as the final scientific argument.

Create a Finding only when an observation, comparison, relationship, interpretation or contradiction materially affects a scientific question, a candidate contribution, an inference boundary or a decision-critical task. Do not create one Finding per Result Unit, plot, feature or sentence. Merge redundant descriptions while retaining distinct evidence sources and contradictory results.

Each Finding derived from a scientific-analysis record must contain:

- analysis_derived = true;
- one or more scientific_analysis_refs, each with the exact analysis_id, record_type and stable record_id;
- supporting Result Unit IDs and, where relevant, contradictory Result Unit IDs;
- an accurate epistemic status: Observed, Interpreted or Hypothesized;
- plausible alternative explanations for an interpreted finding;
- limitations, comparability constraints and prohibited inferences.

Supported record types are observation, comparison, relationship, interpretation, contradiction, signal_feature and signal_comparison. An analysis-derived Finding must cite the exact underlying record, not just the analysis-pack ID or its free-text summary. If a historical record lacks a stable ID, do not invent one in the reference; add a stable ID when that record is legitimately revised or create a new source-linked analysis record.

A Finding may connect more than one analysis pack when the same scientific relationship was reviewed across packs. Cite every contributing record and preserve its source Result Units. Do not promote a candidate metadata link into a Finding unless the underlying evidence was actually examined and the relationship supported.

## 2. Preserve evidence roles and independence

Keep supporting, contradictory, audit-target and context-only Result Units distinct. A result being checked for reliability is not automatically evidence supporting the claim under review. A derived value or repeated panel from one underlying measurement is not an independent experiment. Do not inflate convergence by counting dependent outputs as independent evidence.

Where analyses disagree, retain the disagreement and explain whether it arises from different conditions, measurement definitions, sample states, methods, resolution, processing, uncertainty or an unresolved inconsistency. Do not average away inconvenient evidence or exclude it merely because it weakens the preferred story.

## 3. Construct Claims from Findings

For each serious candidate route, formulate atomic scientific claims. Each Claim must distinguish:

- what is directly observed or quantified;
- what relationship is established by comparison;
- what is interpreted and with what confidence;
- what remains a hypothesis;
- which evidence supports it and which evidence contradicts it;
- which alternatives or confounders remain;
- what observation would strengthen, weaken or falsify it.

Use Claim evidence references to link the relevant Finding entities. Direct Result Unit references may supplement a Finding, but they do not replace an analysis-derived Finding when a central comparative, associational, causal or mechanistic Claim synthesizes two or more Result Units covered by the general scientific-analysis stage.

A causal or mechanistic label requires a design and evidence chain appropriate to that inference. A correlation, co-occurrence, sequence or cross-method consistency does not by itself establish causation or mechanism. Record alternative explanations and the discriminating controls or measurements needed.

## 4. Select the mainline using the argument graph

Compare the user's original hypothesis with materially different evidence-led candidates. For each candidate, trace the chain from source evidence through Findings and Claims to the proposed contribution. Identify:

- the strongest supporting Findings and whether their sources are independent;
- the strongest contradictory Findings and unresolved conflicts;
- which links are direct observations, derived comparisons, interpretations or hypotheses;
- the closest prior-art challenge and the precise remaining distinction;
- the key alternative explanation and smallest feasible discriminating test;
- which claims are essential, supporting or unnecessary for the proposed paper.

Do not select a route because it has the greatest number of Findings, figures or methods. Select the line that changes scientific understanding, survives the closest prior-art challenge and is supportable within explicit evidence and feasibility boundaries. If evidence is insufficient, retain a conditional or stop/defer recommendation.

## 5. Propagate the argument into the manuscript

The selected Claim set must control the Introduction gap, Results/Discussion order, Figure take-home messages, SI allocation and work packages. Each main-text section should advance one or more Claims and explain the inferential step. Each Figure should visually test or establish a necessary part of the argument. Diagnostic evidence belongs in SI unless its result itself is central.

For each essential missing link, create a Data Slot and a targeted experiment, reanalysis or computation task. State the competing explanations it distinguishes and how supportive, contradictory, mixed or inconclusive outcomes alter the mainline. Separate the smallest decision-changing test from later publication-strength extensions.

The narrative plan must explain the argument in ordinary scientific prose. Do not expose internal IDs or use a network diagram as a substitute for the scientific explanation.

## 6. Validation boundary

Deterministic code may verify that Finding references resolve, that referenced analysis records exist, that Result Unit links are consistent, and that a central cross-result Claim cites a suitable analysis-derived Finding. It cannot decide whether an interpretation is scientifically correct, whether a comparison is meaningful, whether evidence is independent in practice, whether novelty is real or whether a mechanism is established. Those remain model/researcher reasoning and human scientific review.

If analysis coverage is NOT_ASSESSABLE or NO_COMPARISON_APPLICABLE, preserve that exact state. Do not manufacture a Finding or treat a non-assessable result as analysed support.
