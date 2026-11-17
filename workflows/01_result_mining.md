# 01 — Result Mining & Evidence Quality (P0/P1)

## Objective

Turn one unstructured PDF report into a traceable inventory of candidate experimental results without inventing values, sample identities, conditions or conclusions.

## 1. Deterministic ingestion

Run ingest_pdf.py and extract_regions.py. Python must compute source SHA-256; record page count, dimensions, rotation and extracted text; extract embedded raster image blocks; retain page-coordinate BBoxes and pixel hashes; register stable Region IDs; and flag pages with vector drawings/text but no embedded image blocks.

Do not claim all figures were extracted. Vector-only plots need separately defined regions.

## 2. Triage

Generate a contact sheet to identify likely figure regions and prioritize inspection. It is only a triage view and must not be used to read exact values, weak peaks, slopes or close line styles.

Inspect individual image regions at their extracted resolution. For vector-only figures, define a page-coordinate BBox and render at a declared DPI.

## 3. Caption-blind visual inspection

The first visual pass receives only the cropped figure/panel. Do not provide the external caption or report narrative. Keep image-internal labels, ticks, units, legends and annotations visible.

Identify each panel before interpreting a multi-panel figure. Never transfer an axis, unit or legend across panels. Record what is visible and what cannot be read.

Do not return exact values unless the image is legible and the extraction policy permits them.

## 4. Instrument checklist

Load only the checklist for the recognized technique. For each field use FOUND, NOT_SHOWN, NOT_LEGIBLE, UNCERTAIN or NOT_APPLICABLE.

Keep figure-level status separate from report-wide status. After visual inspection, search report text for the same field. NOT_SHOWN is not equivalent to “not performed”.

## 5. Caption and narrative comparison

Only after the blind visual pass, retrieve the associated caption and nearby report text. Compare visual observation, caption and narrative. If they disagree, create VISUAL_TEXT_DISCREPANCY with source references. Do not conclude that the student is wrong.

## 6. Result Units and panels

A Result Unit is one independently meaningful result, not necessarily one image. A Figure can contain multiple Results; a Result may use one Panel or several coordinated regions. Preserve every parent/child relationship.

For multi-curve plots, use series-level sample associations. If the curve-to-sample mapping is unclear, leave it unresolved.

## 7. Sample mapping and Micro-Gate 0.5

Create provisional Sample Entities from explicit names and preparation descriptions. Do not infer batches/runs.

Trigger Micro-Gate 0.5 only if unresolved mapping breaks a central cross-result relationship, changes a key interpretation, or is required by a core claim. Show only relevant aliases and candidate mappings. The user may confirm, reject or defer. Deferral does not block independent analysis.

Unconfirmed mappings cannot support cross-result causal, mechanistic or structure–property conclusions.

## 8. Artifact audit and epistemic separation

For each important candidate finding:
- separate Observed, Interpreted and Hypothesized statements;
- record data origin, legibility and quantitative permission;
- check relevant instrument-specific artifact factors;
- record alternative explanations and their evidence status;
- distinguish figure-level NOT_SHOWN from report-wide NOT_REPORTED;
- do not treat missing metadata as proof of error.

Incomplete normalization or critical conditions may still allow descriptive reporting, but not stronger intrinsic-performance or causal claims.

## 9. Validation and context compilation

```bash
python scripts/validate_evidence.py --workspace ERA_Workspace
python scripts/validate_samples.py --workspace ERA_Workspace
python scripts/compile_prompt_context.py --workspace ERA_Workspace --output ERA_Workspace/cache/prompt_context/evidence_context.md
```

Do not mark evidence audited while deterministic errors remain. Surface warnings.

## Required outputs

Evidence Bundle, State Manifest, ID Registry, PDF/page inventory, extracted images, Result Units, Sample Entities, instrument checklist, artifact audit, visual/text discrepancies, validation report and compact context.

## Stop conditions

Stop only the affected interpretation when required visual capability is unavailable, resolution is inadequate, a panel cannot be separated, or sample mapping remains ambiguous. Continue unrelated independent extraction.
