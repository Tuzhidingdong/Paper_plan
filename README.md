# Paper_plan — Research-to-Manuscript Development Skill

Paper_plan develops an evidence-grounded, target-journal-aware manuscript project package from a user's experimental report and associated research data.

Its deliverable is broader than a research-plan summary: it connects the existing evidence and literature frontier to one central contribution, an Introduction, a complete manuscript storyline, Figure/Panel and Supporting Information architecture, and assignable experiment/analysis/computation work packages.

## V5.1 scientific-mainline and literature frontier

V5.1 also includes a mandatory narrative-product quality review (docs/V5_1_NARRATIVE_PRODUCT_QA.md), a reusable literature-frontier audit ledger template (templates/V5_1_LITERATURE_FRONTIER_LEDGER.md), and stricter citation-lead resolution, adversarial prior-art testing, Figure/SI allocation, sample-state integrity and decision-critical task design. Product quality, scientific readiness and benchmark comparison are reported as separate outcomes.

V5.1 retains the V5 narrative-first product and V4.1–V4.3 scientific-integrity controls. It strengthens scientific-mainline selection (including explicit evaluation of the user's original hypothesis) and literature-frontier discovery/synthesis.

The structured bundles remain the provenance/state layer. The final deliverable must be a standalone, reasoned narrative that a supervisor can review and a team can execute: research diagnosis, closest-literature comparison, bounded novelty, one central contribution, paragraph-level Introduction, connected Results/Discussion storyline, TOC and Figure/Panel design, SI map, actionable experiment/analysis/computation handoffs and a prioritized execution plan.

The controlling workflow is workflows/13_v5_manuscript_development.md. Read docs/V5_PRODUCT_CONTRACT.md, templates/V5_INTEGRATED_MANUSCRIPT_PLAN.md, docs/V5_1_SCIENTIFIC_MAINLINE_DECISION.md and docs/V5_1_LITERATURE_FRONTIER_PROTOCOL.md. Product acceptance requires inspection of the actual Markdown and PDF against the project benchmark; regression tests and structural validators are not substitutes.

## General scientific evidence analysis

The release-candidate branch adds a mandatory, domain-neutral analysis stage between evidence extraction and manuscript synthesis. It prepares source-linked joint analysis packs across all Result Units, preserves original-resolution image assets and sample/series context, and requires the Agent to discover meaningful within-result and cross-result relationships without the user supplying an instrument-specific analysis checklist. Results are recorded with source references, compatibility assessments, alternative explanations and explicit coverage for every Result Unit. See docs/SCIENTIFIC_ANALYSIS_CAPABILITY_PLAN.md and references/scientific_analysis.md.

Image-based semi-quantitative comparisons are supported when the original-resolution figure is sufficiently legible; native numeric data are not a universal prerequisite. Estimates must state their basis, confidence, precision and limitations. This software capability remains subject to fresh, user-run scientific black-box acceptance; passing CI alone does not establish scientific correctness.

## Scientific argument synthesis

The analysis layer now has an explicit, domain-neutral bridge into the manuscript argument. Material analysis observations, comparisons, relationships, interpretations and contradictions are distilled into source-linked Findings; each such Finding cites the exact analysis record and preserves supporting and contradictory Result Units. Candidate routes use these Findings as argument evidence, and a cross-result central Claim must cite an analysis-derived Finding. Deterministic validation checks the provenance chain, not the truth of the scientific interpretation. See references/scientific_argument_synthesis.md.
## V4 baseline retained under V5

The V4 line preserves the V3.3 deterministic evidence engine and adds a structured Manuscript Development Bundle plus cross-package validation. V5 reuses these capabilities and adds narrative-first synthesis.

### Existing deterministic layer
- PDF fingerprint, page inventory and immutable source preservation.
- Embedded raster-image Region extraction with stable anchors.
- Vector-figure candidate detection and explicit vector BBox workflow.
- Repeated-layout triage without deleting evidence.
- Caption-blind task preparation, visual-inspection records and retry gate.
- Python-issued IDs, evidence provenance, sample identity and quantitative-permission validation.
- Literature, route, framework and Data Unit/task dependency bundles.
- Markdown-to-PDF export and PDF page/text verification.

### V4 manuscript-development layer
- Current target-journal and article-type profile with dated source references.
- One central contribution, bounded novelty and complete manuscript storyline.
- Introduction paragraph architecture linked to Claim and literature-claim IDs.
- TOC/graphical abstract concept adapted to verified journal requirements.
- Main Figure and Panel plans with scientific purpose, evidence, Data Slots and acceptance criteria.
- Supporting Information items linked to main claims and Figures.
- Work-package links to existing experiment/analysis/computation tasks.
- Verified measurement-definition checks for central quantitative Result Units and condition-comparability assessments for cross-sample/condition Figure comparisons.
- Cross-package validation of journal sources, manuscript references, Figure/SI placement, task coverage, dependency cycles and calculation blockers.

The V4 package schema is in schemas/manuscript_development_bundle.schema.json. The workspace bundle is initialized by scripts/init_planning_bundles.py and validated by scripts/validate_manuscript_development.py.

## Generality contract

The Skill must remain domain-neutral. No project-specific material names, sample labels, values, equations, mechanisms, literature findings, journal requirements or Figure designs may be embedded in generic Skill instructions, references, schemas, templates or configuration. Target journal is a current-project runtime input and must never be inherited from a benchmark, prior project or previous run. Case-specific details belong only in an isolated workspace/test-run input. Figure count, route count and manuscript structure are determined at runtime.

## Run

Python 3.10+ is required.

    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v

For a new project, follow workflows/07_full_run.md. Its stages use workflows/01–06 for evidence mining and literature/routes/framework preparation, then workflows/08–12 for journal profile, argument/storyline, Figure/SI design, handoff work packages and final audit.

Run the V4 validator after creating the V4 bundle:

    python scripts/validate_manuscript_development.py --workspace WORKSPACE --deliverables-dir WORKSPACE/deliverables --skill-commit <CURRENT_SKILL_COMMIT>

Run the existing validators as well:

    python scripts/validate_evidence.py --workspace WORKSPACE
    python scripts/validate_samples.py --workspace WORKSPACE
    python scripts/validate_planning.py --workspace WORKSPACE
    python scripts/validate_bundle_schemas.py --workspace WORKSPACE

## Scientific boundaries

- Validators check structure, provenance, references and execution dependencies. They do not prove novelty, mechanisms, experimental validity or publication outcome.
- Journal rules must be retrieved from current official sources and stored with dates.
- Unresolved sample mappings or method details remain unresolved.
- Computations with missing required inputs are blocked.
- Human decisions remain explicit and are never silently approved.

See docs/V4_PRODUCT_CONTRACT.md, docs/ARCHITECTURE.md and docs/IMPLEMENTATION_STATUS.md for the product boundary and development status.


## V5.1 researcher-facing product

The primary deliverable is a professional scientific research and manuscript-development plan for supervisors, students and collaborators. It must explain the research rationale, current evidence, literature position, contribution, full manuscript storyline, concrete Figure/Panel and Supporting Information plans, and assignable research/computation briefs in connected prose.

Workflow stages, schema/bundle state, internal route labels, Skill/runtime metadata, validator results and product-QA statuses remain in separate internal records. They are not part of the researcher-facing plan.

See:
- `docs/V5_1_RESEARCHER_FACING_DELIVERY_STANDARD.md`
- `docs/V5_PRODUCT_CONTRACT.md`
- `templates/V5_INTEGRATED_MANUSCRIPT_PLAN.md`
- `templates/V5_INTERNAL_PRODUCT_QA_REPORT.md`

## V4.1–V4.2 scientific decision and integrity controls

V4.1 adds typed evidence-use roles, distinct evidence assessments and comparability states, Panel data scopes, execution-readiness gates, agreement/equivalence decision rules, classified task dependencies and validation fingerprints.

V4.2 closes quality gaps exposed by a fresh original-PDF acceptance run:
- Result Unit Region references must be physical, page-consistent evidence crops; repeated headers/footers cannot anchor scientific claims.
- Image-derived evidence requires a linked caption-blind inspection record.
- Claims combining multiple image-derived Result Units require acquisition/scale/specimen comparability dimensions and explicit inference limits.
- Derived statistical fits require source-linked, deterministic coefficient reproduction against printed precision. Measurement-definition status is not treated as proof that a fitted model reproduces or is externally validated.
- A nominated research route requires an auditable selection rationale and dispositions for all non-selected candidates.

These are generic engineering controls. They do not encode the scientific case that exposed the defects, and do not replace expert review or human route approval.


V4.3 also extends the original image-inspection record: each image-derived observation must capture acquisition and spatial metadata during the original-resolution blind-inspection pass. Unknown or illegible metadata is recorded explicitly; it is never guessed from captions. Cross-image comparisons reuse those source-linked records.


V4.3 calculation audits now carry a declared reproduction status that is checked against the recomputed result. Statistical-quality/uncertainty assessment and validation scope are stored separately; a matching coefficient calculation does not imply adequate diagnostics or external validation.


## Reproducible plotted-data reading

A follow-on scientific-analysis capability preserves source-linked PDF-native vector paths/text geometry and adds coordinate-calibrated readings from plots. Numeric plot estimates must retain axis units/scales, tick anchors, plot coordinates, series identity and coordinate uncertainty; a deterministic recorder recomputes values and changes and blocks unsupported precision or extrapolation. Graph-reading uncertainty is kept separate from experimental uncertainty. This capability bounds and audits visual estimates; it does not reconstruct original instrument arrays or substitute for real scientific black-box acceptance.
