# Scientific claim strength

Keep epistemic status separate from claim type.

Epistemic status: Observed, Interpreted, Hypothesized.

Claim types: Descriptive, Comparative, Associational, Causal, Mechanistic.

Evidence strength must match the claim. A clear spectrum may support a descriptive statement; it does not automatically prove a mechanism or causality.

Record supporting evidence, contradictory evidence, alternative explanations and limitations. Never promote a hypothesis to an established fact during downstream planning.


## Quantitative measurement definitions

A displayed label is not a complete definition of a quantitative metric. For a central numeric result, record the measurand, raw signal, measurement method, calculation formula when derived, output unit, normalization basis, blank/calibration corrections, uncertainty approach and source Result Unit lineage. If any essential element is unknown, the definition remains partial and the result must not be promoted as a verified core quantitative metric.

## Comparability

A cross-sample or cross-condition comparison must state the compared entities and the dimensions that were matched, mismatched, unknown or not applicable. A comparison marked comparable cannot contain an unresolved or mismatched dimension among the declared required dimensions. The permitted inference must be restricted to the dimensions and evidence actually assessed.

## Evidence-use roles and assessment

A Claim reference may classify a Result Unit as `SUPPORTS_CLAIM`, `CONTRADICTS_CLAIM`, `AUDIT_TARGET` or `CONTEXT_ONLY`. Legacy unlabelled direct Result Unit references default to support. Finding-linked Result Units retain the semantic type of the Finding list that references them.

Keep evidence assessment distinct from epistemic status. `NOT_ESTABLISHED` and `NOT_ASSESSABLE` are not synonyms for `CONTRADICTED`. The latter requires explicit counter-evidence and a valid basis for contradiction. Comparability failure alone only restricts inference.

Quantitative Result Units used as decision-bearing evidence for or against a central contribution must pass the CORE / VERIFIED measurement-definition gate. CORE means central to evaluating the claim, not necessarily favourable to it. A numeric AUDIT_TARGET can be essential to a methods-validity investigation without being treated as validated support or contradiction; its definition may remain PARTIAL while it is being audited.

## Comparability and evidence strength

Distinguish COMPARABLE, CONDITIONALLY_COMPARABLE, NOT_COMPARABLE, NOT_ASSESSABLE and UNASSESSED. Record the intended comparison and required dimensions. Mismatched or unknown dimensions restrict or prevent the intended comparison; they do not establish the opposite result.


## Proxy, surrogate and indirect measurements

When a Claim relies on a proxy, surrogate or indirect measurement to represent a target measurand, name the target measurand and the candidate indicator separately. State the operational definition and measurement principle of each, and justify why the proposed reference is suitable and sufficiently independent. A shared signal, shared correction or shared preparation dependency can limit the apparent independence of the comparison.

Keep the relationship being tested explicit: agreement, calibration, prediction, classification, ranking, monitoring, association or another defined relationship. Correlation or a shared trend alone does not establish agreement or interchangeability. Define a suitable estimand, analysis method, uncertainty approach, acceptance boundary with an independent rationale, and outcomes that support, contradict or leave the question inconclusive.

Interpret a proxy only within the tested population, conditions, time alignment and unit of analysis. If candidate and reference measurements are not paired or defensibly matched, narrow the claim and explain the sampling limitation. The control design must address the plausible confounders and artefacts of the particular measurement system; no universal control list applies. If recovery or input-output closure is relevant, define what is accounted for and how residuals are judged. If it is not relevant, record why.

Separate in-sample reproduction, statistical diagnostics, internal resampling, external independent validation and prospective validation. None is a substitute for another. A fitted relationship that reproduces its printed coefficients has not thereby established statistical adequacy, external transportability or causal validity.
