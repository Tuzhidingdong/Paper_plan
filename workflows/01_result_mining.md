# 01 — Result Mining & Evidence Quality (P0/P1)

## Objective

Turn one unstructured experimental-report PDF into a traceable inventory of candidate experimental results without inventing values, sample identities, conditions or conclusions.

## 1. Source and workspace

- Preserve the original PDF and record SHA-256, byte size and page count.
- Use one isolated workspace for this PDF. Never overwrite a different source.
- If a previously validated workspace exists for the identical SHA-256, reuse its Evidence Bundle, ID Registry, visual-inspection cards and raw source assets rather than repeating model calls.
- Any reuse must first verify the source hash and the provenance of every referenced asset.

## 2. Page inventory and vector triage

Run ingest_pdf.py on a new workspace, or refresh_vector_candidates.py on an existing workspace. Both use the same spatial vector-cluster heuristic.

The candidate heuristic:
- ignores page-edge furniture when scoring the central body area;
- groups drawing centers into a page grid and finds spatially connected clusters;
- counts line/rectangle/quad primitives within the strongest cluster;
- records drawing-grid occupancy, cluster drawing count and plot primitive types;
- allows raster images and vector drawings on the same page.

drawing_bbox_area_ratio reports the largest central cluster's grid bounding area, not the union of every page drawing. The legacy whole-page union is retained separately as drawing_full_page_union_bbox_area_ratio.

A candidate flag is a source-coverage obligation, not a semantic conclusion. For every page flagged by the ingest detector, retain each spatial vector-figure candidate and its PDF-coordinate BBox. Review the full-page render and candidate crop before deciding whether it is a scientific figure. Do not silently discard a candidate because it is unfamiliar or difficult to interpret.

## 3. Raster extraction and Contact Sheet triage

Run extract_regions.py. In addition to embedded raster image blocks and any explicitly supplied BBoxes, it automatically rasterizes every vector-figure candidate recorded by ingest_pdf.py using the retained PDF-coordinate BBox (default 300 dpi). Each crop becomes a source-anchored Region and a figure_candidates record with image SHA-256, pixel dimensions and PENDING_TRIAGE status. Multiple spatial plot clusters on one page are preserved as separate candidates. Do not provide hand-authored BBoxes for candidates already detected by the ingest stage.

Repeated near-identical top/footer image blocks are labelled REPEATED_LAYOUT_ASSET only for triage. They remain in the Evidence Bundle and their IDs are not merged or deleted. The default Contact Sheet omits these repeated assets; use --include-layout-assets to inspect all.

Contact Sheets are for orientation only. Never read quantitative values, weak peaks, slopes, close line styles or axes from downscaled sheets. Inspect the original-resolution Region/Panel instead.

When previously registered vector BBoxes or other manual regions exist, reuse them only when source hash, page-coordinate provenance and extraction version match. Do not re-create equivalent crops or repeat completed visual inspections without a documented evidence gap.

Every ingest-detected vector candidate must subsequently receive an explicit disposition using `scripts/record_figure_triage.py --workspace WORKSPACE --decisions-json DECISIONS_JSON`. For an actual scientific figure, use `INCLUDE_AS_SCIENTIFIC_FIGURE` and link the Result Unit(s) that cite its Region (or child Panel). Use `EXCLUDE_NOT_SCIENTIFIC_FIGURE` only when it is demonstrably decorative/non-scientific, with a concise source-based reason. A difficult-to-read or unresolved scientific chart is not an exclusion: register it as evidence and mark its Result Unit NOT_ASSESSABLE with the specific blocker. Record candidate decisions after Result Units exist and before evidence validation. Unreviewed or unlinked candidates are validation errors.

## 4. Image-first visual inspection

Before opening page text, captions or narrative:
1. Check scripts/check_capability.py --task visual_inspection.
2. Inspect original-resolution images individually.
3. Create a CAPTION_BLIND task pack and record visibility, axes/units, sample labels actually visible, legibility and confidence.
4. In the same inspection card, record a structured `visual_metadata_assessment` for every linked Region/Panel. Explicitly assess: imaging modality; magnification or pixel size; scale bar/spatial calibration; specimen state/preparation; image processing/contrast; and field selection/sampling.
5. For each dimension, record OBSERVED with its value, unit where applicable, source location, recording method and confidence, or explicitly record NOT_PRESENT, NOT_LEGIBLE, NOT_APPLICABLE or UNKNOWN with a reason. Never fill a missing scale/calibration value from a caption, another panel or a guessed magnification.
6. A scale-bar value read from the original-resolution crop must be marked `SCALE_BAR_READ`, linked to its location in that crop, and retain its unit and confidence. Distinguish this manual visual reading from a value copied from source or instrument metadata.
7. Keep each panel, axis, unit, tick, legend and series association independent.
8. Exact values require legible ticks, axis, units and series identity. Low-resolution plots never yield exact values.
9. One targeted reinspection per Region/Panel is allowed, with a written reason.

If the same Agent has already read the report text in the active context, set cognitive_blindness = NOT_GUARANTEED. The JSON task pack omitting captions does not erase context already seen by the model. Do not describe the inspection as fully independent.

## 5. Text and caption comparison

Only after the first image-only pass, inspect extracted page text and external captions. Compare what the text says with what is directly visible. Record agreement, text-only details not visible in the figure, visual/text discrepancies, text that overstates the image and unresolved crop/caption contamination.

Figure-level status and report-level status stay separate. NOT_SHOWN means not shown in the inspected figure, not absent from the whole report.

## 6. Results, sample identities and context

- Create Sample Entities only from explicit sample names/aliases or documented mappings.
- Keep CONFIRMED, PROBABLE, AMBIGUOUS, UNMAPPED and NOT_APPLICABLE distinct.
- Reserve Result and Finding IDs with assign_entity_ids.py.
- One Result Unit represents one source observation/series with Region/Panel provenance and a Measurement Context.
- Keep Observed, Interpreted and Hypothesized separate.
- Capture Exact_Text/Exact_Table/Vector_Extracted separately from Visual_Estimate and Qualitative_Observation.
- Never infer unreported batches, measurement runs, replicates, treatment conditions or raw data.
- For every quantitative Result Unit that may support a central claim, create a measurement definition recording the measurand, raw signal, method, formula where derived, output unit, normalization basis, calibration/blank corrections, uncertainty and parent Result Unit IDs. Mark incomplete definitions PARTIAL or NOT_ASSESSED; do not promote them to a verified core metric.
- When a fitted/derived relationship is extracted or calculated, create its source-linked calculation audit immediately. Record the input vectors, displayed parameter values/precision and an explicit reproduction_status. Separately assess statistical diagnostics/uncertainty and state whether validation is in-sample, internally resampled, externally independent or prospective. Never infer one status from another.
- Mark each Result Unit's intended claim role as UNDECIDED, SUPPORTING, CORE or NOT_USED. A numeric CORE result must pass the measurement-definition checks before it can support a central quantitative claim.
- Compare experimental conditions explicitly before combining or contrasting Result Units. Record matched, mismatched, unknown and not-applicable dimensions rather than assuming like-for-like comparability.

## 7. General cross-result scientific analysis (mandatory)

After all Result Units, sample associations, individual visual inspections and measurement definitions have been assembled, perform the general scientific evidence analysis before manuscript synthesis. This stage is domain-neutral and is triggered by the existence of Result Units, not by a user naming a particular technique or comparison.

First qualify the active model:

    python scripts/check_capability.py --workspace WORKSPACE --task scientific_analysis

Then prepare a source-linked analysis inventory and joint task packs:

    python scripts/prepare_scientific_analysis.py --workspace WORKSPACE

Inspect the generated analysis_index.json and every request JSON under WORKSPACE/cache/scientific_analysis. The index must account for every Result Unit and expose Regions/Panels that have not been linked to a Result Unit. Each pack includes the relevant Result Units, original-resolution assets, sample/series mappings, measurement conditions, existing observations and candidate metadata relationships.

The candidate relationship graph is only a navigation aid. The Agent must inspect the underlying evidence map and discover relevant relationships that metadata indexing may not capture. It must consider within-result series and between-result relationships, including cross-sample, cross-condition, temporal, quantitative, cross-method, convergent, divergent, unexpected or contradictory patterns where appropriate. The active Agent decides which comparisons are scientifically meaningful; no fixed instrument- or discipline-specific checklist is imposed.

Open all original-resolution assets in each pack and analyze them jointly with the associated structured evidence. Attach those assets to the active model invocation as native image inputs; a file path or the text "asset_exists=true" is not evidence that the model saw the image. Never claim an image was inspected from a path alone.

Treat plotted experimental signals as primary evidence. Identify the coordinate axes, units, plotted series and relevant visible features in the actual source image. Where supported by resolution and measurement context, record feature-level observations for peaks, bands, reflections, shoulders, edges, plateaus or other salient signal structures. Compare features within a plot and across compatible samples/conditions/series, including position, width, intensity, area, shape, appearance/disappearance and non-monotonic changes. Do not force a spectroscopy-specific or diffraction-specific checklist on unrelated data; select feature types from the evidence itself. Do not invent exact values from a low-resolution image; record visual estimates with basis, precision, uncertainty and confidence, or mark the metric unresolved. Feature labels/assignments are interpretations, not direct observations.

Use `signal_analysis_coverage` to explicitly disposition every Result Unit as APPLICABLE, NOT_APPLICABLE or NOT_ASSESSABLE for plotted-signal analysis. APPLICABLE requires source-linked feature records; when no defensible comparison can be made, explain why. NOT_APPLICABLE and NOT_ASSESSABLE require a reason. Use the prepared `signal_features` and `signal_comparisons` fields for source-linked feature records. Every feature and comparison must cite Result Unit and Region/Panel/page. Explicitly separate direct signal change from its interpretation and assess baseline, overlap, normalization, orientation, acquisition settings and other relevant alternatives.

For every model call, persist the actual request and response artifacts in the project workspace and record a `model_invocation` receipt: invocation ID, actual model ID, response status, input mode, each native image attachment's source path and SHA-256, its runtime attachment reference, and request/response artifact paths and SHA-256. The receipt is Agent-reported runtime evidence, not a claim of independent host verification. If native image attachment or the actual request/response cannot be confirmed, mark affected Result Units NOT_ASSESSABLE; do not mark them ANALYZED.

Every Result Unit must receive exactly one disposition: ANALYZED, NO_COMPARISON_APPLICABLE or NOT_ASSESSABLE. Give a reason for the latter two. If there is no valid comparison, record that result rather than inventing a relationship. For large projects, process packs within the configured size limit and preserve cross-pack links for project-level synthesis. After all packs are recorded, inspect analysis_index.json cross_pack_relationships and each record's related_results_outside_pack. Reopen the relevant pack descriptors/assets and perform a project-level review of these links before Stage 2. Confirm only evidence-supported relationships; persist material cross-pack conclusions as Findings using the existing ID registry, with exact Result Unit and Region/Panel references. Do not treat an unreviewed metadata link as a scientific result.

Save each pack's structured response following its required_output shape and register it:

    python scripts/record_scientific_analysis.py --workspace WORKSPACE --request-json REQUEST_JSON --record-json ANALYSIS_RESULT_JSON

After all packs are recorded, regenerate the compact evidence context. The new scientific_analyses records are first-class Evidence Bundle evidence and must inform later claim selection, literature comparison, manuscript storyline and Figure allocation. Do not treat single-result descriptions as completed scientific synthesis.

If the capability check is blocked, do not quietly substitute text-only reasoning for visual analysis. Mark the affected units NOT_ASSESSABLE and preserve the exact capability blocker. Reuse source-hash-matched extraction and previous analysis records; do not repeat costly work without an evidence gap.

## 8. Artifact/confounder audit

Before upgrading observations into interpretations, consider relevant sample identity, preparation differences, instrument calibration, acquisition settings, baseline/background/fitting, normalization and units, replicate variability, controls, alternate mechanisms, image cropping/contrast and selection bias.

For every relevant factor record whether the report shows it, where that evidence came from, plausible alternatives and what would resolve the uncertainty. Missing metadata makes the stronger claim not assessable; it does not prove the experiment is wrong.

## 9. Validation and context compilation

Before evidence validation, create a decisions JSON for every vector figure candidate and record the explicit inclusion/exclusion decisions:

    python scripts/record_figure_triage.py --workspace WORKSPACE --decisions-json FIGURE_TRIAGE_DECISIONS_JSON

Then run:

    python scripts/validate_evidence.py --workspace WORKSPACE
    python scripts/validate_samples.py --workspace WORKSPACE
    python scripts/compile_prompt_context.py --workspace WORKSPACE --output WORKSPACE/cache/prompt_context/evidence_context.md

A PASS is structural only. Surface sample warnings and unresolved mappings. Trigger Micro-Gate 0.5 only when an unresolved association blocks a central cross-result link; independent results can still be analyzed.

## Required outputs

Evidence Bundle, State Manifest, ID Registry, PDF/page inventory, all extracted Regions, Contact Sheets, Result Units, Sample Entities, instrument checklist, general scientific analyses, per-Result-Unit coverage and unassigned Region/Panel report, artifact audit, visual/text discrepancies, validation reports and compact context.

## Stop conditions

Block only the affected interpretation when capability is insufficient, resolution is inadequate, a panel cannot be separated, or sample identity is unresolved. Continue unrelated independent evidence extraction. Never claim all figures were extracted when vector-only BBoxes remain unregistered.
