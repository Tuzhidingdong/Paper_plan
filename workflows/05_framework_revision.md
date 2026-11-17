# 05 — Human framework revision (specified; not implemented in MVP)

During Gate B, present compact Claim–Citation Skeletons and Data Slot tables, not full Introduction prose.

Use Entity-Level Upsert with explicit IDs and base revision. New permanent IDs are allocated by Python. Deletions are tombstoned and checked for dependencies. Apply updates to a temporary copy, validate, and atomically commit.

Dependency status:
- HARD_STALE: core evidence source or central hypothesis changed/removed; recompute affected dependency branch.
- RECHECK_REQUIRED: claim-to-data mapping, Data Slot or Data Unit changed; run local validation.
- SOFT_WARN: order, formatting or wording changed; review continuity without invalidating evidence.

Do not rewrite unrelated approved sections.
