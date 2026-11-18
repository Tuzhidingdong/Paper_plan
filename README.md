# Paper_plan — Research-to-Manuscript Development Skill

Paper_plan develops an evidence-grounded, target-journal-aware manuscript project package from a user's experimental report and associated research data.

Its deliverable is broader than a research-plan summary: it connects the existing evidence and literature frontier to one central contribution, an Introduction, a complete manuscript storyline, Figure/Panel and Supporting Information architecture, and assignable experiment/analysis/computation work packages.

## V4 development line

The V4 development branch preserves the V3.3 deterministic evidence engine and adds a structured Manuscript Development Bundle plus cross-package validation.

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

The Skill must remain domain-neutral. No project-specific material names, sample labels, values, equations, mechanisms, literature findings, journal requirements or Figure designs may be embedded in generic Skill instructions, references, schemas, templates or configuration. Those belong only in an isolated workspace. Figure count, route count and manuscript structure are determined at runtime.

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

## V4.1–V4.2 scientific decision and integrity controls

V4.1 adds typed evidence-use roles, distinct evidence assessments and comparability states, Panel data scopes, execution-readiness gates, agreement/equivalence decision rules, classified task dependencies and validation fingerprints.

V4.2 closes quality gaps exposed by a fresh original-PDF acceptance run:
- Result Unit Region references must be physical, page-consistent evidence crops; repeated headers/footers cannot anchor scientific claims.
- Image-derived evidence requires a linked caption-blind inspection record.
- Claims combining multiple image-derived Result Units require acquisition/scale/specimen comparability dimensions and explicit inference limits.
- Derived statistical fits require source-linked, deterministic coefficient reproduction against printed precision. Measurement-definition status is not treated as proof that a fitted model reproduces or is externally validated.
- A nominated research route requires an auditable selection rationale and dispositions for all non-selected candidates.

These are generic engineering controls. They do not encode the scientific case that exposed the defects, and do not replace expert review or human route approval.
