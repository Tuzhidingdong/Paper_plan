# P0/P1 MVP acceptance plan

## Local setup

§§§powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
§§§

The script commands below can be run from the repository root:

§§§powershell
python scripts/ingest_pdf.py "D:\path\to\student_report.pdf" --workspace ERA_Workspace
python scripts/extract_regions.py --workspace ERA_Workspace
python scripts/build_contact_sheet.py --workspace ERA_Workspace
python scripts/validate_evidence.py --workspace ERA_Workspace
python scripts/validate_samples.py --workspace ERA_Workspace
python scripts/compile_prompt_context.py --workspace ERA_Workspace --output ERA_Workspace/cache/prompt_context/evidence_context.md
python scripts/prepare_visual_inspection.py --workspace ERA_Workspace --entity-id REG001 --mode initial
python scripts/record_visual_inspection.py --workspace ERA_Workspace --entity-id REG001 --mode initial --record-json visual_card.json
§§§

For a vector-only figure, create a JSON list of page-coordinate regions and pass it with --regions-json. For a multi-panel image, create an explicit panel layout with normalized coordinates relative to the parent region and run segment_panels.py.

Reserve permanent Result Unit and Finding IDs before writing those entities:

§§§powershell
python scripts/assign_entity_ids.py --workspace ERA_Workspace result-slot --parent-region-id REG001 --slot-index 1
python scripts/assign_entity_ids.py --workspace ERA_Workspace finding-slot --slot-index 1
python scripts/assign_entity_ids.py --workspace ERA_Workspace sample --alias "Sample A" --source-ref REG001
§§§

The Python registry owns all permanent IDs. Models may only reference these IDs.

## Adversarial acceptance tests

| ID | Fixture | Pass criterion |
|---|---|---|
| T01 | Low-resolution spectrum with blurred ticks | No exact values or invented peak positions |
| T02 | Same sample under multiple aliases with an unresolved mapping | Unresolved mapping cannot support cross-result causal/structure–property claims |
| T03 | Apparent performance improvement with missing normalization | Alternative explanations and missing metadata are recorded; no unsupported intrinsic-performance claim |
| T04 | Repeated extraction of the same PDF region | Existing Region IDs are reused |
| T05 | Caption asserts a trend not independently visible | Blind visual record remains independent; discrepancy is surfaced after caption comparison |
| T06 | Multi-panel plot with different axes | Panels remain separate; no axis/legend transfer |
| T07 | Checklist field absent from image but present in report text | Figure status and report status remain distinct |
| T08 | Region remains unreadable after one reinspection | Further automated retries stop; issue enters confirmation list |
| T09 | Workspace reopened in a new Agent session | State and IDs recover from disk, not chat history |

## Acceptance boundary

Automated unit tests verify deterministic boundaries. They do not prove scientific competence of the active VLM. The user must inspect a representative real student report locally, including extracted regions, sample mappings, visual observations and artifact audits. Record model/provider/version and capability qualification for that run.
