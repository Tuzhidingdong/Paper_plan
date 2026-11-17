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

A candidate flag is only a prompt for page-level review, not semantic chart detection. Review candidate pages against the rendered page before creating a Result Unit. Do not manually register decorative rules as scientific figures.

## 3. Raster extraction and Contact Sheet triage

Run extract_regions.py. It extracts embedded raster image blocks and can render explicit PDF-coordinate BBoxes for vector-only figures.

Repeated near-identical top/footer image blocks are labelled REPEATED_LAYOUT_ASSET only for triage. They remain in the Evidence Bundle and their IDs are not merged or deleted. The default Contact Sheet omits these repeated assets; use --include-layout-assets to inspect all.

Contact Sheets are for orientation only. Never read quantitative values, weak peaks, slopes, close line styles or axes from downscaled sheets. Inspect the original-resolution Region/Panel instead.

For the gypsum-report regression, previously registered vector BBoxes on p10/p11 and other manual chart regions should be reused when source hash and page-coordinate provenance match. Do not re-create equivalent crops or re-run their visual inspection merely to consume tokens.

## 4. Image-first visual inspection

Before opening page text, captions or narrative:
1. Check scripts/check_capability.py --task visual_inspection.
2. Inspect original-resolution images individually.
3. Create a CAPTION_BLIND task pack and record visibility, axes/units, sample labels actually visible, legibility and confidence.
4. Keep each panel, axis, unit, tick, legend and series association independent.
5. Exact values require legible ticks, axis, units and series identity. Low-resolution plots never yield exact values.
6. One targeted reinspection per Region/Panel is allowed, with a written reason.

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

## 7. Artifact/confounder audit

Before upgrading observations into interpretations, consider relevant sample identity, preparation differences, instrument calibration, acquisition settings, baseline/background/fitting, normalization and units, replicate variability, controls, alternate mechanisms, image cropping/contrast and selection bias.

For every relevant factor record whether the report shows it, where that evidence came from, plausible alternatives and what would resolve the uncertainty. Missing metadata makes the stronger claim not assessable; it does not prove the experiment is wrong.

## 8. Validation and context compilation

Run:

    python scripts/validate_evidence.py --workspace WORKSPACE
    python scripts/validate_samples.py --workspace WORKSPACE
    python scripts/compile_prompt_context.py --workspace WORKSPACE --output WORKSPACE/cache/prompt_context/evidence_context.md

A PASS is structural only. Surface sample warnings and unresolved mappings. Trigger Micro-Gate 0.5 only when an unresolved association blocks a central cross-result link; independent results can still be analyzed.

## Required outputs

Evidence Bundle, State Manifest, ID Registry, PDF/page inventory, all extracted Regions, Contact Sheets, Result Units, Sample Entities, instrument checklist, artifact audit, visual/text discrepancies, validation reports and compact context.

## Stop conditions

Block only the affected interpretation when capability is insufficient, resolution is inadequate, a panel cannot be separated, or sample identity is unresolved. Continue unrelated independent evidence extraction. Never claim all figures were extracted when vector-only BBoxes remain unregistered.
