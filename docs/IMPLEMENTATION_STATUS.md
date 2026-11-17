# Implementation status — Paper_plan V4 development

## Branch scope

This branch develops the V4 manuscript-development product layer while preserving the V3.3 evidence-mining engine. It is a development candidate until the automated CI and a fresh real-project acceptance run pass.

## Existing capabilities retained

| Capability | Status | Notes |
|---|---|---|
| PDF source fingerprint and page inventory | Implemented | Original source preserved |
| Raster Region extraction | Implemented | Source/page/BBox/pixel provenance |
| Spatial vector candidate detection | Implemented heuristic | Candidate prompt only; not semantic chart recognition |
| Vector-only chart cropping | Partial/manual | Explicit PDF-coordinate BBox required |
| Stable Region/Panel IDs | Implemented | Python-owned registry |
| Visual-inspection and retry protocol | Implemented | Same-context cognitive leakage disclosed |
| Sample identity and evidence validation | Implemented | Human confirmation for ambiguous mappings |
| Literature access-tier and search records | Agent-executed + validated | Search coverage remains tool/access dependent |
| Candidate research directions | Agent-executed + validated | No forced number of directions |
| Claim, Data Slot, Data Unit and task bundles | Implemented | Existing V3.3 framework bundle retained |
| Markdown-to-PDF export | Implemented | Reopen and verify final PDF |

## V4 capabilities added in this branch

| Capability | Implementation | Status |
|---|---|---|
| Manuscript Development Bundle | New JSON Schema and non-destructive initializer | Implemented in branch |
| Journal source / Introduction / story / Figure / SI IDs | Extended Python ID reservation and guarded upsert | Implemented in branch |
| Current journal profile workflow | New stage-specific runbook | Agent-executed; requires current source verification |
| Central contribution and storyline design | New workflow and references | Agent-executed; quality subject to review |
| Introduction paragraph architecture | Structured entities and workflow | Agent-executed + references checked |
| Figure/Panel and SI architecture | Structured Figure/SI entities and workflow | Agent-executed; not automatic visual design |
| Experiment/computation handoff detail | New work-package workflow | Agent-executed; linked to existing tasks |
| Integrated package validator | Schema, reference, placement, task-closure, cycle and blocker checks | Implemented in branch |
| Genericity/project isolation rules | Updated Skill, runbooks and product contract | Documented; requires multi-domain acceptance |

## Known limitations

1. Literature research and journal verification depend on the active Agent's current search access and source access. No autonomous crawler is claimed.
2. A structured Figure plan does not itself render publication-ready scientific plots or validate plot aesthetics.
3. The Agent designs a TOC/graphical-abstract brief; actual artwork still requires a dedicated image/design step and journal-specific dimensions.
4. Schema and cross-reference validation cannot judge whether a proposed mechanism is scientifically true or whether a novelty claim will survive peer review.
5. Figure/Panel plans and computational handoff briefs are model-authored content. Their scientific assumptions require expert review.
6. The V4 package is a planning/coordination product, not an automatic manuscript submission or experimental execution system.
7. Real-world quality across unrelated research domains has not yet been established. A single successful run is insufficient.

## Verification required before release

- GitHub Actions: Python 3.10, 3.11 and 3.12.
- New V4 unit tests: schema validity, graph references, essential Data Slot closure, dependency cycles, missing computational inputs, journal source requirements and flexible Figure counts.
- Existing V3.3 regression suite must remain green.
- Inspect generic Skill/workflow sources to ensure they contain no project-specific scientific content.
- Run on a fresh report from a different research domain, without reusing prior project context or project data.
- Evaluate the final package against the V4 product contract and user-provided quality benchmark. A generated PDF alone does not pass acceptance.
