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
