# Paper_plan — Experiment Report Analyzer (ERA)

ERA is an evidence-driven Agent Skill for discovering research opportunities from a single, potentially unstructured PDF experimental report and planning a data-centric SCI manuscript.

## Current implementation

**ERA V3.2 — P0/P1 MVP**

The first milestone focuses on trustworthy PDF ingestion and experimental-result mining:

- PDF inventory with source SHA-256 and reproducible extraction metadata.
- Embedded-image region extraction with Python-generated stable anchors.
- Parent Figure / child Panel representation.
- Caption-blind visual inspection protocol.
- Instrument-specific visual checklists.
- Two-layer sample representation and conditional Micro-Gate 0.5.
- Observed / Interpreted / Hypothesized evidence separation.
- Artifact and confounder audit records.
- Deterministic validation and compact prompt-context compilation.
- HEAD-only state bundles and a persistent ID registry.

Research-frontier analysis, route generation, manuscript framework revision, and final report production are specified as later workflow contracts; they are not claimed as implemented in this MVP.

## Quick start

Python 3.10+ is required. Install the optional PDF/image dependencies:

```bash
python -m pip install -r requirements.txt
```

In the repository root:

```bash
python scripts/ingest_pdf.py path/to/report.pdf --workspace ERA_Workspace
python scripts/extract_regions.py --workspace ERA_Workspace
python scripts/build_contact_sheet.py --workspace ERA_Workspace
python scripts/validate_evidence.py --workspace ERA_Workspace
python scripts/compile_prompt_context.py --workspace ERA_Workspace --output ERA_Workspace/cache/prompt_context/evidence_context.md
python scripts/prepare_visual_inspection.py --workspace ERA_Workspace --entity-id REG001 --mode initial
```

The contact sheet is for triage only. It must not be used for quantitative plot reading. Embedded images can be extracted automatically. Vector-only figures require a region specification before they can be inspected at figure resolution.

## Skill entry point

See [SKILL.md](SKILL.md). The detailed P0/P1 procedure is in [workflows/01_result_mining.md](workflows/01_result_mining.md).

## Safety and scientific boundaries

- The original PDF and extracted source regions are treated as immutable evidence.
- A visual estimate is never represented as an exact numeric measurement.
- Missing information in the report does not prove that an experiment was not performed.
- Unconfirmed sample mappings cannot support cross-result causal or structure–property claims.
- The model must not invent instrument settings, sample identities, raw data, literature evidence, or calculations.
- Python validates deterministic structure; scientific interpretation remains explicitly qualified and reviewable.
- Real student-report end-to-end acceptance is intentionally left to the user after local synchronization.

## Development checks

```bash
python -m unittest discover -s tests -v
```

See [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) for scope and known limitations.
