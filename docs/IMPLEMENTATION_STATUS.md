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
| Integrated package validator | Schema, reference, placement, task-closure, cycle, comparison-condition and blocker checks | Implemented in branch |
| Measurement definition and calculation lineage | Structured fields plus a gate for numeric CORE Result Units | Implemented in branch |
| Comparability assessment | Structured comparison entities/dimensions linked to Figure Panels | Implemented in branch |
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
- New V4 unit tests: schema validity, graph references, essential Data Slot closure, dependency cycles, missing computational inputs, journal source requirements, flexible Figure counts, numeric core-metric definitions and comparison-condition compatibility.
- Existing V3.3 regression suite must remain green.
- Inspect generic Skill/workflow sources to ensure they contain no project-specific scientific content.
- Run on a fresh report from a different research domain, without reusing prior project context or project data.
- Evaluate the final package against the V4 product contract and user-provided quality benchmark. A generated PDF alone does not pass acceptance.

## V4.1 development status

The V4.1 branch adds domain-neutral scientific decision controls: typed Claim evidence roles, a distinct NOT_ASSESSABLE state, Panel data-scope/reuse review, structured execution-design readiness, agreement/equivalence decision rules, classified task dependencies and validation fingerprints.

These changes are development-candidate features until GitHub CI and local regression are complete. Existing project runs are not silently rewritten; older validation outputs remain historical and must be regenerated against the current Skill and bundle revisions before being described as current. No project-specific findings are included in generic Skill sources.

## V4.2 evidence-integrity gates (development branch)

| Gate | Implementation | Intended effect |
|---|---|---|
| Physical Region integrity | `scientific_quality_gates.py` wired into `validate_evidence.py` | Rejects repeated header/footer anchors and source-page/Region page mismatches |
| Caption-blind visual provenance | Evidence validator checks linked visual-inspection history for image-derived Result Units | Prevents unsupported visual observations without an inspection record |
| Multi-image visual comparability | Manuscript validator requires six acquisition/scale/specimen dimensions for multi-image claims | Detects magnification/scale-bar, modality, preparation and image-processing mismatches |
| Statistical-fit reproduction | Evidence validator recomputes source-linked OLS linear fits at displayed precision | Separates method definition from actual coefficient reproduction |
| Research-route decision audit | Planning validator requires selection criteria, evidence rationale and disposition of every alternative | Prevents an opaque preferred-route choice |

V4.2 regression tests are in `tests/test_v4_2_scientific_integrity.py`. These gates are generic and contain no test-project/sample facts. GitHub Actions runs compileall and the complete unittest suite on Python 3.10, 3.11 and 3.12 for every PR head. Fresh local synchronization and regression remain to be completed after merge.
