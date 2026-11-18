# 09 — Core Scientific Argument and Manuscript Storyline

## Objective

Turn heterogeneous existing results into one coherent, evidence-bounded paper argument. The purpose is not to force every observation into a manuscript.

## 1. Discover candidate contributions

Start from the validated Result Units, Findings, sample relationships, calculation lineage, uncertainty and closest competing literature.

For each candidate contribution state:
- the scientific question;
- what is already established by the user's evidence;
- what is interpretation or hypothesis;
- the closest prior work and counter-evidence;
- what would make the contribution genuinely different;
- the decisive missing evidence;
- the risk if the proposed explanation is wrong.

Candidate directions may be merged, split, deferred or rejected. Do not require three routes or any fixed count.

## 2. Select one central contribution

A strong package should identify one central question and one central contribution. Supporting sub-contributions are allowed only when they strengthen the same argument.

Check whether the proposed contribution is:
- important to the relevant field;
- distinguishable from the closest competitors;
- supported by existing observations or testable with a finite evidence plan;
- specific enough to falsify;
- not dependent on invented data, assumed mechanisms or unsupported "first" claims.

If no defensible contribution can be selected, provide a diagnostic package explaining what is missing rather than manufacturing a paper story.

## 3. Build the argument spine

Represent the manuscript as an ordered sequence of reasoning steps:
1. what established knowledge or practical/scientific problem motivates the study;
2. what limitation or unresolved question remains;
3. what the current study asks or tests;
4. what evidence is introduced first and why;
5. what the next evidence resolves;
6. which interpretation is supported, which alternatives remain;
7. what the full evidence permits the authors to conclude;
8. what the scope and limitations are.

Every transition must be motivated by a scientific dependency, not by a change of instrument.

## 4. Link the argument to the Claim–Evidence model

Use Python-issued Claim IDs, Data Slot IDs, literature-claim IDs and Result/Finding references.

For every central claim:
- record epistemic status separately from claim type;
- link supporting and contradicting evidence;
- list alternative explanations and confounders;
- state conditions under which the claim would be weakened or rejected;
- identify the minimum evidence needed to retain the claim;
- verify that every central quantitative result has a defined measurand, method, signal, calculation/normalization basis and uncertainty;
- record whether the comparison conditions are matched, mismatched or unknown, and restrict inference accordingly.

For every proposed claim not yet established, write it as a hypothesis or planned test, not a result.

## 5. Introduction architecture

The Introduction is a logical funnel customized to the actual field and paper:
- broad context only as far as needed;
- precise state of the art;
- strongest limitations in the closest studies;
- bounded gap and why it matters;
- study question, approach and contribution.

The number of paragraphs is determined by the argument and target-journal style. Each paragraph should have one rhetorical job, a topic message, supporting literature claims and a transition. Avoid a generic three-paragraph formula when the subject needs a different structure.

## 6. Global story checks

Ask:
- Is there one central contribution rather than several unrelated promises?
- Does every major result advance that contribution?
- Does each Figure answer a specific question?
- Are key mechanistic claims supported by evidence beyond correlation or descriptive characterization?
- Are practical application and environmental-impact claims supported by measured or transparently calculated data?
- Are conflicting results visible?
- Can a reviewer state the paper's contribution in one sentence without relying on unsupported assumptions?

Record rejected or deferred directions and why they were not included.

## 7. Evidence-use roles and claim assessment

A Result Unit linked to a Claim is not automatically evidence supporting that Claim. Record the role explicitly when the distinction matters:

- `SUPPORTS_CLAIM`: evidence used in favour of the claim.
- `CONTRADICTS_CLAIM`: evidence that conflicts with the claim under a valid comparison.
- `AUDIT_TARGET`: a measurement, metric or method being examined; its values are not thereby accepted as support.
- `CONTEXT_ONLY`: background or contextual information that does not carry the claim.

For backward compatibility, an unlabelled direct Result Unit reference is interpreted as `SUPPORTS_CLAIM`. Finding links use their typed result lists: supporting, contradictory, audit-target and context Result Units retain those respective roles.

Keep epistemic status (Observed / Interpreted / Hypothesized) separate from evidence assessment: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `NOT_ESTABLISHED`, `NOT_ASSESSABLE`, `CONTRADICTED`, or `INCONCLUSIVE`.

A claim may be NOT_ESTABLISHED because no adequate evidence exists, or NOT_ASSESSABLE because required comparisons or metadata are unavailable. Neither state means the claim is false. A NOT_COMPARABLE or NOT_ASSESSABLE comparison cannot, by itself, be used as contradictory evidence. Mark a claim CONTRADICTED only when an explicit contradictory evidence reference is documented and the comparison is sufficiently valid for that inference.

The CORE quantitative measurement-definition gate applies to numerical Result Units used as `SUPPORTS_CLAIM` for a central contribution. It does not require an audit target, context record or counter-evidence item to be promoted to CORE.
