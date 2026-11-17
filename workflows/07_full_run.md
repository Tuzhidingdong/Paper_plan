# 07 — Full One-PDF Run: Evidence to Research Plan

This is the controlling runbook for a complete one-PDF deliverable. Exactly one initial PDF is allowed.

## 0. Workspace reuse, source protection and cost baseline

- Record source SHA-256, byte size, page count, Git commit and active host model/provider/version.
- Search the project for an existing workspace with the identical source hash. If one exists and its evidence assets validate, reuse it rather than repeat ingestion and high-resolution model inspection.
- Before refreshing an existing workspace, copy its Evidence Bundle and State Manifest into a timestamped subfolder under state/history. Do not overwrite older research outputs.
- If no identical-source workspace exists, create a new isolated workspace. Never reuse a workspace with a different PDF.
- Record available token counters before work. Do not start hidden Workers. Keep provider counters separate. If a meter is unavailable, state the limitation.
- Do not upload user PDFs/raw experimental data to external services. Web searching should use public scientific metadata and public papers/abstracts; do not upload the user's report.
- Read this runbook and only stage-specific documents needed. Avoid repeatedly loading long scripts and full report text.

## 1. Refresh evidence and triage without resetting prior analysis

For an existing workspace with the same source SHA:
1. Run refresh_vector_candidates.py to update page-level vector diagnostics in place. It must preserve all bundles, visual inspection cards and sample mappings.
2. Run extract_regions.py to add layout-fingerprint and repeated-header/footer triage hints. Stable Region IDs must be reused. Previously registered manual vector BBoxes remain in the Evidence Bundle.
3. Run build_contact_sheet.py. Default Contact Sheets omit repeated near-identical top/footer assets only; all assets remain in evidence. Use --include-layout-assets for a complete audit.
4. Run validate_evidence.py and validate_samples.py.
5. Confirm p10/p11 vector candidates and compare old/new flags. Reuse existing Region images, manually registered vector regions and completed visual-inspection cards. Do not rerun the ten prior visual inspections without a specific unresolved scientific reason.

For a new workspace, run ingest_pdf.py, extract_regions.py, build_contact_sheet.py and the evidence validators in that order.

Vector flags are review prompts, not semantic figure recognition. The detector uses central-page spatial clusters and line/rectangle/quad primitives. drawing_bbox_area_ratio is now the largest central cluster grid-BBox area; drawing_full_page_union_bbox_area_ratio preserves the whole-page union diagnostic. Do not tune thresholds simply to reduce the percentage flagged.

## 2. Image-first and evidence-quality review

- Check capability with check_capability.py --task visual_inspection before new visual interpretation.
- Inspect original-resolution regions, never numerical values from Contact Sheets.
- Prepare CAPTION_BLIND packs and record structured cards.
- If the same Agent has already read the report narrative in this or an earlier active context, record cognitive_blindness = NOT_GUARANTEED. Do not claim a psychologically independent first pass.
- Reuse complete prior visual-inspection records for the exact same source hash. Only inspect a new/unread region if it materially affects a candidate research claim.
- Keep figure-level and report-level missingness distinct.
- Preserve Observed / Interpreted / Hypothesized and Exact_Text / Exact_Table / Vector_Extracted / Visual_Estimate / Qualitative_Observation / Unavailable distinctions.
- Audit artifacts/confounders and sample identity before any causal or mechanistic interpretation.

The gypsum PDF was previously analyzed. Its known preliminary result inventory includes XRD (gypsum and quartz phases reported), TGA mass losses for FGDG/PG/CG, sulfate/pH charts, conversion versus acid-consumption data, BET surface areas and descriptive SEM morphology. Treat these as prior extracted observations only; verify source Result Units and uncertainty notes in the Evidence Bundle before relying on them. Do not copy summary figures into new claims if there is no corresponding Result Unit.

## 3. Capability profile and planning bundle initialization

Record the exact active provider/model/version and attested capabilities using templates/capability_profile.template.json and record_capability_profile.py. The required fields include:
- native_multimodal;
- high_resolution_image_input;
- structured_json_output;
- scientific_reasoning;
- long_context_consistency;
- web_search_access.

Values are yes/no/unknown and require an evidence basis. Unknown capability blocks the corresponding high-risk task. This is an operator-attested profile, not a benchmark.

Run check_capability.py for visual inspection, artifact audit, literature screening, route synthesis, framework design and academic writing when those stages begin. If web_search_access is unavailable, do not claim a complete current literature frontier or defend novelty.

Run init_planning_bundles.py. It creates missing literature, routes and framework HEAD bundles without overwriting existing state.

## 4. Literature frontier review

Use actual web/search tools available to the Agent. Record exact queries, databases/search systems, date bounds, inclusion/exclusion terms and search date in search_scope and literature_search_log.jsonl.

Use the three-stage funnel:
1. Recent reviews to align terminology and define neighboring fields.
2. Primary competitor/frontier studies to compare the actual material/system, preparation route, measured outcomes and mechanism.
3. Counter-evidence, conflicting results, null results and limitations.

Verify title, authors, journal, year, DOI and source links. For every source, set exactly one access level:
- METADATA_ONLY: bibliographic metadata only; cannot support technical claims.
- ABSTRACT_VERIFIED: abstract actually inspected; supports abstract-level facts only.
- FULLTEXT_VERIFIED: relevant full text actually inspected; record concise exact snippets and section/page/figure/table locations.

Allocate a Python-issued LIT ID for every paper and an SN ID for every evidence snippet. Allocate LC IDs for each bounded literature claim and GAP IDs for each gap. Write entities with upsert_planning_entity.py; do not directly replace full JSON bundles.

Compare 3–5 primary studies per proposed route at full text where access permits; this is a target, not a fabricated gate. If fewer are available, report the exact limitation and mark Benchmark_Conditions_Unverified. Never assume conditions from abstracts.

A research gap must identify target system, searched databases/systems, dates, exact query terms, strongest competing studies, counter-evidence and residual uncertainty. Do not say “first” or “unprecedented” unless the bounded primary-source search actually supports it.

## 5. Three distinct research routes

Allocate ROUTE IDs through assign_planning_ids.py and create records through upsert_planning_entity.py.

Generate three scientifically distinct candidate routes where defensible. Each route must connect to:
- existing Result Unit and Finding IDs;
- bounded GAP IDs and literature-claim IDs;
- relevant competitor literature IDs;
- sample dependencies and mapping confidence;
- Observed / Interpreted / Hypothesized status;
- alternative artifact/mechanism explanations;
- decisive Data Slot needs and tasks;
- feasibility and novelty risk.

Compare the routes transparently. Recommend one provisional route and explain why it is stronger than the alternatives. Do not fabricate a third mature route if the evidence only supports one or two. Record route_generation_note and downgrade novelty confidence where appropriate.

Keep approval_A = PENDING_HUMAN_REVIEW. For one-pass delivery, continue framework planning against the provisional recommended route rather than waiting for a human response.

## 6. Data-centric manuscript framework

Allocate IDs in Python and persist each item through guarded Entity Upsert:
- Claim IDs (C);
- Data Slot IDs (DS);
- Data Unit IDs (DU);
- Task IDs (T).

For every Claim, include exact claim text, claim type, epistemic status, Result/Finding/Literature Claim references, limitations, contradictory evidence and alternative explanations.

For every Data Slot, include target Claim, manuscript section, evidence requirement, status (FILLED/PARTIAL/MISSING/BLOCKED), priority (ESSENTIAL/STRENGTHENING/OPTIONAL), available Result/Data Unit links and acceptance criteria.

For every Data Unit, include source Result IDs and the full transformation lineage. Different fits/plots derived from the same observation are not independent experiments.

Plan conceptual Figures/Panels only after Claims and Data Slots are stable. Each figure slot states its message, linked Claims/Slots, sample/condition comparisons, and main-text/SI placement. Map sections across Introduction, Results/Discussion, Methods, Conclusions and Supporting Information.

Keep approval_B = PENDING_HUMAN_REVIEW. Provide Claim–Citation skeletons and a Data Slot table before the full narrative.

## 7. Experiment, analysis and computation plan

Every unsatisfied essential Data Slot must have a task or an explicit no-task rationale.

Each task must include:
- objective and scientific rationale;
- target Claim/Data Slot IDs;
- existing evidence and the exact uncertainty/missing evidence it resolves;
- sample ID/alias and mapping confidence;
- variables, controls, blanks and comparison groups;
- measurement method, instruments and required native/raw file formats;
- replicate/statistical plan, or an explicit TBD for supervisor/lab confirmation;
- processing and quality-control checks;
- expected output and measurable completion criteria;
- prerequisite Task IDs, priority P0/P1/P2, feasibility and risks;
- intended manuscript section and conceptual figure slot.

P0 resolves central-claim validity or determines route viability. P1 strengthens mechanism/comparability or controls a major confounder. P2 is an optional extension. Do not prescribe unreported equipment, reagent quantities, sample mass, temperature, concentration, time or replicate count. Literature values are proposed starting ranges only when their exact source and applicability are stated; local SOP/supervisor confirmation is required.

Theory/computation is not mandatory. Recommend DFT/MD/kinetics only when it discriminates a concrete hypothesis and actual input structure/composition/model is known. If a required experimental structure, composition, surface, solvent or interface is missing, mark the calculation task BLOCKED_BY_EXPERIMENT and list prerequisite experiment Task IDs. Do not make a blocked calculation look executable.

## 8. Introduction and consolidated deliverables

Draft an English Introduction aligned with the provisional recommended route. Each technical premise must cite a verified Literature Claim. Do not insert unreported results or claim the novelty is established.

Create:
- deliverables/01_evidence_report.md
- deliverables/02_literature_frontier.md
- deliverables/03_three_research_routes.md
- deliverables/04_recommended_framework.md
- deliverables/05_experiment_and_computation_plan.md
- deliverables/06_student_self_check.md
- deliverables/FINAL_RESEARCH_PLAN.md
- deliverables/FINAL_RESEARCH_PLAN.pdf

The consolidated plan must contain an executive recommendation, evidence already available versus still needed, literature search scope, comparison with competitors, three routes, provisional selection, Introduction, Claim–Evidence graph, Data Slot table, manuscript section/figure logic, prioritized task plan, computation blockers, uncertainty and references.

Student-facing self-check must be gentle, plain and question-oriented. Say “could you help check whether…” rather than “the report is wrong”.

Export with export_plan_pdf.py. Reopen the PDF and verify page count and extracted text. Record the SHA-256 of both Markdown and PDF and ensure the PDF is generated from the final Markdown revision.

## 9. Final validators and report

Run:
- validate_evidence.py;
- validate_samples.py;
- validate_planning.py;
- validate_bundle_schemas.py.

Resolve all structural errors. Warnings must be visible in the final report, not silently deleted. Then compare all ID references with the Python registry and verify no dangling citations/tasks remain.

Report source SHA, Git commit, workspace, validated Result/Findings, sample ambiguities, literature access tiers, search coverage, routes and recommendation, Data Slots, P0/P1/P2 tasks, blocked calculations, both approval gates, validation result, final PDF path and token deltas.

The final package is a reviewable research proposal, not proof that a novelty claim will survive peer review. Never claim all scientific questions are solved.
