## 2026-11-21 status update — analysis-to-argument bridge

The V54 Validator defect is closed and locally accepted at branch baseline `7613c5746acf7c859b19281fe5cda875c47b1996` (167-test full regression, targeted tests, compile check and read-only V54 integrity verification). No further Validator repair is planned absent new evidence.

The next product-capability phase adds a source-traceable bridge from general scientific analysis to manuscript argument:
- analysis records for relationships, interpretations and contradictions receive stable IDs for later citation;
- analysis-derived Findings cite exact analysis IDs, record types and record IDs while retaining supporting/counter-evidence Result Units;
- Evidence validation checks those references and source Result Unit alignment;
- candidate routes receive a warning when they combine multiple Result Units without a cross-result Finding;
- central comparative/associational/causal/mechanistic Claims spanning multiple Result Units must cite an analysis-derived Finding;
- the Skill workflow explicitly distils the full analysis set into Findings before literature/mainline selection and propagates them into Claims, Figures and Results/Discussion.

**Current state:** implementation is on `feat/spectral-analysis-capability`; code/test integration is in progress. The traceability gate does not judge scientific truth. General multi-domain black-box acceptance and user review of the resulting researcher-facing plan remain outstanding. No merge, publication or release is authorized.

## V5 manuscript-planning core (development candidate)

The V5 branch adds a narrative-first full-run controller, product contract, integrated-plan template and local product-acceptance procedure. It preserves the V4.3 evidence/reliability layer rather than treating those controls as the whole product.

The intended behavior change is that the Agent synthesizes evidence and structured state into a complete, readable, assignable manuscript-development dossier. Bundle completeness and validator status remain supporting checks, not product acceptance.

This branch remains a development candidate until the user completes one fresh local end-to-end run and inspects the actual Markdown/PDF against the separately held project benchmark. Do not mark product acceptance complete from documentation or unit-test results alone.

## General scientific evidence analysis — release candidate prepared; black-box acceptance pending

The baseline V5.1 branch already contains reliable source provenance, sample/result structures, individual visual inspection, measurement definitions, condition comparability, calculation audits and a researcher-facing manuscript plan. A Raman/FTIR-specific comparison prototype was also added, but it is not a general scientific discovery capability.

The release-candidate branch adds a domain-neutral analysis stage that:
- indexes all Result Units and emits candidate evidence relationships without treating metadata links as confirmed comparisons;
- prepares joint analysis packs containing multiple Result Units, original-resolution assets, sample/series context and source anchors;
- requires the model to identify scientifically meaningful within-result and cross-result patterns, cross-method convergence, divergence and contradictions;
- records per-Result-Unit coverage, source-linked observations, comparisons, relationships, interpretations, alternatives and limitations;
- integrates records into Evidence Bundle validation and compact context;
- checks model capability before the multimodal scientific-analysis stage.

**Status:** The parent release-candidate branch is CODE/CI VERIFIED — SCIENTIFIC BLACK-BOX ACCEPTANCE PENDING. Its previous 155-test matrix does not establish spectral analysis quality.

## Follow-on spectral analysis capability — implementation branch

Branch: `feat/spectral-analysis-capability`, based on the unchanged RC commit `aff67d386109760e3a5267f3d574707878de1b53`.

This follow-on implementation addresses the root-cause audit's extraction, coverage, signal-analysis and invocation-audit gaps:
- the PDF ingest heuristic now retains per-cluster vector plot BBoxes instead of emitting only a page-level review flag;
- `extract_regions.py` rasterizes each detected vector candidate at the requested DPI into a provenance-linked Region and records an explicit source-figure candidate;
- `record_figure_triage.py` records inclusion with Result Unit links or reasoned exclusion; unresolved/missing candidates block evidence validation;
- analysis packs include per-asset SHA-256 manifests and explicitly request feature-level signal observations/comparisons;
- the analysis recorder validates signal feature identity, position/width/intensity/area estimates, comparison links, native image attachment receipts and request/response log hashes;
- the evidence validator rechecks persisted signal references, native image receipt correspondence, request/response artifact hashes and source-figure coverage;
- compact context carries signal features/comparisons, figure-candidate dispositions and model-input audit state.

**Status:** IMPLEMENTATION IN PROGRESS — CI AND AGENT ACCEPTANCE PENDING. These changes improve deterministic ingestion, persistence and auditability; they do not themselves prove that the selected model can correctly interpret diffraction/spectroscopy signals. Do not claim scientific acceptance until the existing Agent runs the targeted regression and a fresh ordinary-prompt black-box test against real material, with no manually supplied analysis targets.

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

## V4.2 evidence-integrity gates (merged to main)

| Gate | Implementation | Intended effect |
|---|---|---|
| Physical Region integrity | `scientific_quality_gates.py` wired into `validate_evidence.py` | Rejects repeated header/footer anchors and source-page/Region page mismatches |
| Caption-blind visual provenance | Evidence validator checks linked visual-inspection history for image-derived Result Units | Prevents unsupported visual observations without an inspection record |
| Multi-image visual comparability | Manuscript validator requires six acquisition/scale/specimen dimensions for multi-image claims | Detects magnification/scale-bar, modality, preparation and image-processing mismatches |
| Statistical-fit reproduction | Evidence validator recomputes source-linked OLS linear fits at displayed precision | Separates method definition from actual coefficient reproduction |
| Research-route decision audit | Planning validator requires selection criteria, evidence rationale and disposition of every alternative | Prevents an opaque preferred-route choice |

V4.2 regression tests are in `tests/test_v4_2_scientific_integrity.py`. These gates are generic and contain no test-project/sample facts. GitHub Actions runs compileall and the complete unittest suite on Python 3.10, 3.11 and 3.12 for every PR head. V4.2 was merged to `main`. The V4.2 targeted functional acceptance report identifies the tested Skill commit and confirms that its project inputs and prior outputs were preserved; this focused round did not rerun the full regression suite.


## V4.3 measurement-validity controls (development branch)

| Gate | Implementation | Intended effect |
|---|---|---|
| Inspection-time visual metadata | Extended caption-blind inspection cards plus evidence-integrity validation | Requires source-linked modality, spatial calibration, specimen state, processing and field-sampling states to be recorded at original-resolution inspection |
| Proxy-to-reference design | `validate_proxy_measurement_design()` wired into planning validation | Requires separate candidate/reference measurands, justified reference basis, sampling alignment, relationship and outcome rules |
| Control coverage | Structured, case-specific required control classes and planned controls | Requires confounder-driven control review and explicit rationale for omissions; no universal controls |
| Accounting closure | Explicit REQUIRED / NOT_REQUIRED / NOT_ASSESSED decision | Requires inputs, outputs, residual method and basis only when closure is relevant |
| Fit-quality separation | Statistical-quality diagnostics and uncertainty status on calculation audits | Prevents coefficient reproduction or R-squared from being treated as a complete quality assessment |
| Validation scope | In-sample, internal resampling, independent external and prospective levels | Requires distinct data scope, independence unit and leakage controls where applicable |

V4.3 tests use synthetic generic fixtures. The controls do not encode any specific sample, material system, measurement technique or experimental conclusion. This development remains subject to CI and local regression before merge.


V4.3 fit audits now require a declared `reproduction_status` that the validator cross-checks against recomputed coefficients. The status is separate from statistical-quality diagnostics/uncertainty and from internal, external-independent or prospective validation scope.


## Follow-on scientific data-reading capability — 2026-11-21

A new generic plotted-data reading layer is being added after the V5.1 product review. It preserves PDF-native vector/text geometry alongside existing raster evidence; requires explicit axis calibration, tick anchors, plot coordinates, series identity and reading uncertainty for numeric plot estimates; and deterministically recomputes values and differences before accepting them into scientific-analysis records.

The gate distinguishes coordinate-reading uncertainty from experimental uncertainty and blocks uncalibrated visual numbers or extrapolation outside the readable axis range. It does not recover instrument arrays or establish scientific correctness. The implementation remains subject to CI and a later real-project black-box assessment; neither source changes nor passing software tests alone establish improved scientific performance.
