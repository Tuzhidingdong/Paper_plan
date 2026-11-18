# V5.1 Local Product Acceptance

Passing unit tests or existing validators does not establish that the generated plan is usable.

## Sync and inspect

From the Paper_plan repository root, inspect the working tree first. Preserve uncommitted work and user data. Never reset, clean, force checkout or overwrite the existing test workspace.

    git status --short
    git fetch origin
    git switch --track -c v5.1/scientific-mainline-literature origin/v5.1/scientific-mainline-literature
    git rev-parse HEAD
    git status --short

If the local branch already exists, switch to it and fast-forward only. Do not merge V5 into main for this test.

## Engineering regression

Use Python 3.10 or later:

    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v

Record the commit and test summary. Tests protect the deterministic layer and bundles; they do not test reasoning depth or narrative usability.

## One meaningful end-to-end run

Use the original research input package and the separately held project benchmark. Start a new isolated workspace.

- Do not reuse old V4.3 deliverables as source evidence.
- Reuse extraction only if source hashes and provenance match.
- Do not modify or overwrite the source project's existing directories, original files or prior human decisions.
- Keep project-specific evidence, benchmark content, test-specific target journal and literature conclusions in the isolated workspace/test-run inputs, never generic Skill files. Verify generic sources remain domain- and journal-neutral.
- Verify current official requirements for the target journal/article type.
- Run SKILL.md with workflows/13_v5_manuscript_development.md. Supply the current project's target journal explicitly when selected; never infer it from a benchmark used for another project. Explicitly request the complete V5 integrated plan, not a validator report or direction shortlist.

## Inspect actual deliverables

Read the whole FINAL_MANUSCRIPT_DEVELOPMENT_PLAN.md and its same-revision PDF. For a substantive full-paper project, confirm a multi-page PDF and check for truncation.

Assess: recovery of the user's original scientific intent; comparison against materially different candidate mainlines (including but not defaulting to an audit/validation route); explicit selection rationale; multi-route discovery and citation chasing; verified closest-work comparison; paragraph-level Introduction and draft where possible; connected Results/Discussion storyline; actionable Figure/Panel content, status, comparisons and inference limits; concrete SI items; assignable experiments/analyses with inputs, controls, outputs, QC and alternative outcomes; collaborator-ready or explicitly blocked computations; dependency-aware priorities; and supervisor/team usability without reconstructing reasoning from JSON.

A short validator report, one-page PDF, bundle dump, generic directions or vague tasks fail this product test even if engineering tests pass.

## Report once

Record branch commit, inputs/source hashes, model/provider, Markdown/PDF paths/hashes, regression result, product review against the benchmark and the few material gaps. Do not repeat full runs for more scores/logs. Fix a specific root cause and rerun once only when it materially changes the product.


## Additional V5.1 product-quality review

Before reporting acceptance, apply docs/V5_1_NARRATIVE_PRODUCT_QA.md to the actual Markdown and matching PDF. This review is mandatory and is distinct from the existing validator suite.

In particular, verify:
- the populated literature-frontier audit ledger based on templates/V5_1_LITERATURE_FRONTIER_LEDGER.md is retained in the workspace, and all user-supplied literature leads and citation clues have documented resolution; do not accept "not found" based on one failed endpoint;
- the closest primary studies have been compared at the highest accessible evidence tier and every novelty proposition has passed an adversarial search;
- the main Figure portfolio advances the chosen scientific contribution; data transcription/fit/QC audits are in SI unless central to the contribution;
- decision-critical experiments explicitly discriminate the leading alternatives and address relevant confounders;
- sample handling preserves the state being claimed, or the preservation issue remains a blocker;
- title, abstract map, Figure messages and conclusion are no stronger than the evidence;
- the Markdown and same-revision PDF are coherent, complete and readable.

Report PLAN_PRODUCT_STATUS, SCIENTIFIC_READINESS and BENCHMARK_COMPARISON separately. If the requested benchmark is absent, mark comparison BLOCKED_REFERENCE_UNAVAILABLE; do not replace it with memory or a generic substitute and claim completion. Do not convert missing experimental evidence into a product failure when the plan gives a rigorous bounded recovery/stop decision.
