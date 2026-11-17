# Implementation status — ERA V3.2

## Current milestone: P0/P1 MVP

| Capability | Status | Notes |
|---|---|---|
| PDF SHA-256 and page inventory | Implemented | PyMuPDF |
| Embedded raster extraction | Implemented | Image-block extraction with source/page/BBox provenance and canonical pixel hash |
| Stable region anchors and persistent IDs | Implemented | Python-owned, registry-backed and reused across repeated extraction |
| Result/Finding/Sample ID reservation | Implemented | Agent must request IDs before writing permanent records |
| Contact sheets | Implemented | Triage only; never a quantitative source |
| Vector-only chart extraction | Partial/manual | Explicit page-region BBox required |
| Panel registration | Implemented from explicit panel spec | Semantic panel detection is not claimed |
| Caption-blind task preparation | Implemented | First-pass task pack contains no external caption or report narrative |
| Visual inspection record and retry gate | Implemented | Initial inspection plus at most one automated reinspection per Region/Panel |
| Instrument checklist | Schema and reference implemented | Figure-level and report-level status remain separate |
| Sample Entity + Measurement Context | Schema, ID allocator and validator implemented | No inferred batch/run hierarchy |
| Artifact/confounder audit contract | Reference, template and structural checks implemented | Scientific relevance remains an Agent judgment |
| Evidence and sample validation | Implemented | Source hash, registry IDs, provenance references and numeric permissions |
| Compact context compiler | Implemented | Retains IDs, source pages, data fidelity and caveats |
| Literature research, routes and manuscript planning | Not implemented | Workflow and Bundle contracts only |

## Known limitations

1. Embedded raster image blocks are extracted automatically. Vector-only charts may be PDF drawing primitives rather than images and need an explicitly specified page region.
2. Panel semantic segmentation is not automatic. The panel script accepts normalized BBoxes and creates reproducible crops. Every axis and unit still needs independent review.
3. A field marked NOT_SHOWN is absent from the inspected figure only; report-wide presence requires a separate search.
4. Caption-blind task generation withholds external caption/narrative text. It cannot automatically prove that the crop itself contains no embedded descriptive caption; the crop warning must be reviewed.
5. A Region/Panel receives one initial automated visual inspection and at most one automated reinspection. New source material or explicit human authorization is required for further review.
6. Tool upgrades can change region geometry. Ambiguous region reconciliation is surfaced, not silently remapped.
7. Deterministic tests do not validate the scientific performance of a chosen VLM. A representative student PDF must be tested locally.

## Tests

```bash
python -m unittest discover -s tests -v
```
