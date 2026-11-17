# 05 — Framework Revision and Dependency Control

## Revision rules

Use Entity-Level Upsert. Every update identifies entity ID, base revision, changed fields and rationale. Never replace a complete bundle with a partial model response.

New permanent IDs are reserved by Python. Existing IDs are reused. Deleted entities are tombstoned; never recycle IDs. Apply proposed changes to a temporary copy, run validators, then atomically write the updated HEAD bundle.

## Dependency status

- HARD_STALE: source PDF/evidence lineage or central route hypothesis changed. Recompute all dependent claims, slots and tasks.
- RECHECK_REQUIRED: claim-to-evidence mapping, sample association, Data Slot or Data Unit changed. Revalidate the affected branch.
- SOFT_WARN: wording, order, layout or formatting changed. Check continuity without invalidating scientific evidence.

## Gate B

Present Claim–Citation skeletons, route comparison and Data Slot table before the final narrative. Record the actual human decision if one is made. A one-pass report may include a provisional framework and final-looking PDF for review, but approval_B must remain PENDING_HUMAN_REVIEW.

Do not rewrite unrelated approved sections. Keep a JSONL change history with entity ID, base revision, revision, operation, changed fields and reason.
