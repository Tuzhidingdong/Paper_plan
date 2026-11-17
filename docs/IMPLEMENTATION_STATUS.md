# Implementation status — ERA V3.2

## Current milestone: P0/P1 MVP

| Capability | Status | Notes |
|---|---|---|
| PDF SHA-256 and page inventory | Implemented | Requires PyMuPDF |
| Embedded raster extraction | Implemented | Image-block extraction with page/BBox provenance |
| Stable region anchors and persistent IDs | Implemented | Python-owned registry |
| Contact sheets | Implemented | Triage only |
| Vector-only chart extraction | Partial/manual | Page-region specification required |
| Panel registration | Implemented from explicit panel spec | Semantic panel detection is not claimed |
| Caption-blind protocol | Specified | Agent must keep caption/narrative out of first-pass visual prompt |
| Instrument checklist | Schema and reference implemented | Agent records visibility status |
| Sample entity and measurement context | Schema and validator implemented | No inferred batch/run hierarchy |
| Evidence and artifact-audit validation | Implemented | Structural rules only |
| Compact context compiler | Implemented | Retains scientifically relevant uncertainty |
| Literature research, routes, manuscript planning | Not implemented | Future contracts only |

## Known limitations

1. Embedded raster image blocks are extracted automatically. Vector-only charts may not exist as image blocks and need a specified PDF region.
2. Panel semantic segmentation is not automatic. The panel script accepts normalized BBoxes and creates reproducible crops.
3. A field marked NOT_SHOWN is absent from the inspected figure only; report-wide presence requires a separate search.
4. Tool upgrades can change region geometry. Ambiguous region reconciliation is surfaced, not silently remapped.
5. No real student PDF is included. The user must run local end-to-end acceptance with a representative report.

## Test

```bash
python -m unittest discover -s tests -v
```
