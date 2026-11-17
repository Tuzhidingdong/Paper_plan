# Paper_plan V4 local acceptance checklist

This checklist is domain-neutral. Use a fresh project workspace and do not copy source data or conclusions into generic Skill files.

## 1. Environment and regression

    python -m pip install -r requirements.txt
    python -m compileall -q scripts tests
    python -m unittest discover -s tests -v

All existing evidence extraction, sample, literature, planning and workspace tests must remain green.

## 2. Fresh workspace initialization

Start with a new workspace and a user-authorized report. Preserve the original source and record its hash.

    python scripts/ingest_pdf.py "PATH_TO_REPORT.pdf" --workspace "WORKSPACE"
    python scripts/extract_regions.py --workspace "WORKSPACE"
    python scripts/build_contact_sheet.py --workspace "WORKSPACE"
    python scripts/init_planning_bundles.py --workspace "WORKSPACE"

Then validate the initialized bundles:

    python scripts/validate_bundle_schemas.py --workspace "WORKSPACE"
    python scripts/validate_manuscript_development.py --workspace "WORKSPACE" --deliverables-dir "WORKSPACE/deliverables"

An initialized but unfinished package should be reported as incomplete/warning, not as a completed research plan.

## 3. Evidence and measurement checks

    python scripts/validate_evidence.py --workspace "WORKSPACE"
    python scripts/validate_samples.py --workspace "WORKSPACE"

When a numeric Result Unit is promoted to the core paper argument, define its measurand, raw signal, method, calculation if derived, units, normalization, corrections, uncertainty and source lineage. Do not mark an incomplete metric as a verified core result.

## 4. Research and manuscript package

    python scripts/validate_planning.py --workspace "WORKSPACE"
    python scripts/validate_manuscript_development.py --workspace "WORKSPACE" --deliverables-dir "WORKSPACE/deliverables"

Before final export, inspect:
- current journal requirements and dated source records;
- closest competing studies and evidence access tiers;
- central contribution and novelty boundaries;
- Introduction-to-storyline consistency;
- every Figure and Panel's evidence/Data Slot links;
- matched/mismatched/unknown comparison dimensions;
- Supporting Information links;
- essential missing Data Slots and their work packages;
- computational input blockers and task dependencies.

## 5. Deliverable verification

Export the consolidated Markdown to PDF using the provided exporter. Reopen the PDF and verify that it is non-empty, readable and consistent with the final Markdown revision. Record both hashes.

A schema/CI pass is technical evidence only. Product acceptance requires review of the scientific argument and the usefulness of the work packages on a fresh, unrelated project.
