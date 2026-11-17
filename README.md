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

    python scripts/validate_manuscript_development.py --workspace WORKSPACE --deliverables-dir WORKSPACE/deliverables

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
